import asyncio
import uuid
from datetime import datetime

from fastapi import APIRouter

from agents.datahub_miner import DataHubMiner
from agents.orchestrator import OrchestratorAgent
from api.evidence_store import evidence_cache, prefetch_all_evidence, search_term_for
from api.job_store import job_queues, jobs
from datahub.metadata.schema_classes import DatasetPropertiesClass
from datahub.metadata.urns import DatasetUrn, Urn
from datahub_integration.client import DataHubClient
from datahub_integration.knowledge_codec import decode_knowledge
from datahub_integration.mcp_search import search_via_mcp
from datahub_integration.writer import DataHubWriter
from models.schemas import (
    AssetDetailResponse,
    DependencyGraphResponse,
    ExcavationJob,
    GraphEdge,
    KnowledgeUnit,
    LineageNode,
    RiskAsset,
)

router = APIRouter()


@router.get("/api/risk-dashboard")
async def get_risk_dashboard() -> list[RiskAsset]:
    """Returns all assets scored by knowledge loss risk, sorted CRITICAL
    first, then AT_RISK, then SAFE (compute_risk_scores already sorts
    descending by risk_score).
    """
    miner = DataHubMiner()
    return await miner.compute_risk_scores()


@router.get("/api/search")
async def search_assets(q: str = "") -> list[dict]:
    """Natural-language asset search via DataHub's MCP Server — the
    integration point this hackathon track calls out specifically. Kept
    fully isolated from the SDK-based core pipeline (see mcp_bridge/).
    """
    return await search_via_mcp(q)


def _to_lineage_node(urn: str) -> LineageNode:
    """Lineage edges aren't always dataset-to-dataset — a table can also
    connect to a pipeline task, dashboard, chart, etc. Only DatasetUrn
    knows how to pull out a platform-qualified name, so anything else
    falls back to a generic (still readable) representation instead of
    crashing.
    """
    if Urn.from_string(urn).entity_type != "dataset":
        parsed = Urn.from_string(urn)
        return LineageNode(urn=urn, name=parsed.entity_ids[-1], platform=parsed.entity_type)

    parsed = DatasetUrn.from_string(urn)
    return LineageNode(
        urn=urn, name=parsed.name, platform=parsed.get_data_platform_urn().platform_name
    )


@router.get("/api/dependency-graph")
async def get_dependency_graph() -> DependencyGraphResponse:
    """Returns every asset as a node plus every lineage edge, for the
    whole-instance dependency graph. Also (once) prefetches GitHub evidence
    for every asset concurrently before returning, so that clicking any
    node afterward via /api/asset-detail is instant instead of triggering
    a live search.
    """
    client = DataHubClient()
    urns = client.get_all_datasets()

    nodes = [_to_lineage_node(urn) for urn in urns]

    edges = []
    seen = set()
    for urn in urns:
        lineage = client.get_asset_lineage(urn)
        for downstream_urn in lineage["downstreamEntities"]:
            edge_key = (urn, downstream_urn)
            if edge_key not in seen:
                seen.add(edge_key)
                edges.append(GraphEdge(source=urn, target=downstream_urn))

    await prefetch_all_evidence()

    return DependencyGraphResponse(nodes=nodes, edges=edges)


@router.get("/api/asset-detail/{asset_urn}")
async def get_asset_detail(asset_urn: str) -> AssetDetailResponse:
    """Everything about one asset in a single call: its risk assessment,
    its dependencies, and any GitHub evidence already found for it (from
    the cache /api/dependency-graph populates) — no live search triggered.
    """
    miner = DataHubMiner()
    risk = miner.compute_risk_for_urn(asset_urn)
    lineage = miner.client.get_asset_lineage(asset_urn)

    search_term = search_term_for(risk.asset_name)

    return AssetDetailResponse(
        asset_urn=asset_urn,
        asset_name=risk.asset_name,
        platform=risk.platform,
        risk=risk,
        upstream=[_to_lineage_node(u) for u in lineage["upstreamEntities"]],
        downstream=[_to_lineage_node(u) for u in lineage["downstreamEntities"]],
        evidence=evidence_cache.get(search_term, []),
    )


@router.post("/api/excavate")
async def start_excavation(body: dict) -> dict:
    """Triggers excavation for a single asset.

    Body: { "asset_urn": "...", "asset_name": "..." }
    Returns immediately with a job_id; the excavation itself runs as a
    background asyncio task and streams progress over the paired
    WebSocket at /ws/excavation/{job_id}.
    """
    asset_urn = body["asset_urn"]
    asset_name = body["asset_name"]

    job_id = str(uuid.uuid4())
    jobs[job_id] = ExcavationJob(
        job_id=job_id,
        asset_urn=asset_urn,
        status="PENDING",
        progress_messages=[],
        started_at=datetime.utcnow(),
    )
    job_queues[job_id] = asyncio.Queue()

    asyncio.create_task(_run_excavation(job_id, asset_urn, asset_name))

    return {"job_id": job_id}


async def _run_excavation(job_id: str, asset_urn: str, asset_name: str):
    job = jobs[job_id]
    queue = job_queues[job_id]
    orchestrator = OrchestratorAgent()

    async def progress_callback(message: str):
        job.progress_messages.append(message)
        await queue.put(message)

    try:
        job.status = "MINING"
        knowledge = await orchestrator.excavate(asset_urn, asset_name, progress_callback)
        job.result = knowledge
        job.status = "DONE"
        job.completed_at = datetime.utcnow()
    except Exception as e:
        job.status = "FAILED"
        await progress_callback(f"Excavation failed: {e}")
    finally:
        await queue.put(None)  # sentinel: tells the websocket the job is done


def _all_lore_knowledge() -> list[KnowledgeUnit]:
    """Every asset carrying Lore's custom properties, decoded straight from
    DataHub — DataHub is the durable source of truth, not backend memory.
    """
    client = DataHubClient()
    results = []
    for urn in client.get_all_datasets():
        properties = client.graph.get_aspect(entity_urn=urn, aspect_type=DatasetPropertiesClass)
        if properties is None:
            continue
        knowledge = decode_knowledge(urn, properties.customProperties or {})
        if knowledge:
            results.append(knowledge)
    return results


@router.get("/api/knowledge")
async def get_all_knowledge() -> list[KnowledgeUnit]:
    """Returns every knowledge unit Lore has approved and written back —
    excludes anything still sitting in the pending-review queue.
    """
    return [k for k in _all_lore_knowledge() if k.written_to_datahub]


@router.get("/api/pending-review")
async def get_pending_review() -> list[KnowledgeUnit]:
    """Returns MEDIUM-confidence results awaiting human approval."""
    return [k for k in _all_lore_knowledge() if not k.written_to_datahub]


@router.post("/api/pending-review/{asset_urn}/approve")
async def approve_pending_review(asset_urn: str) -> dict:
    """Promotes a pending review into real DataHub documentation."""
    success = DataHubWriter().approve_pending(asset_urn)
    return {"success": success}


@router.post("/api/pending-review/{asset_urn}/reject")
async def reject_pending_review(asset_urn: str) -> dict:
    """Discards a pending review without ever touching documentation."""
    success = DataHubWriter().reject_pending(asset_urn)
    return {"success": success}


@router.get("/api/excavate/{job_id}")
async def get_excavation_job(job_id: str) -> ExcavationJob:
    """Poll a job's current state (status + progress log + result once done)."""
    return jobs[job_id]
