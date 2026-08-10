from pydantic import BaseModel
from typing import Optional, List, Literal
from datetime import datetime
from enum import Enum


class ConfidenceLevel(str, Enum):
    HIGH = "HIGH"      # >= 0.80 — auto-write to DataHub
    MEDIUM = "MEDIUM"  # 0.50-0.79 — flag for human review
    LOW = "LOW"        # < 0.50 — surface only, do not write


class EvidenceSource(BaseModel):
    type: Literal[
        "pr_comment", "commit_message",
        "code_comment", "lineage_pattern", "git_blame",
    ]
    url: Optional[str] = None
    author: Optional[str] = None
    timestamp: Optional[datetime] = None
    raw_excerpt: str                # The actual text found
    relevance_score: float          # 0.0-1.0


class KnowledgeUnit(BaseModel):
    asset_urn: str                  # DataHub URN e.g. urn:li:dataset:(...)
    asset_name: str
    column_name: Optional[str] = None      # None if asset-level knowledge
    why_it_exists: str              # The synthesized explanation
    known_quirks: Optional[str] = None     # Edge cases, gotchas, anomalies
    business_context: Optional[str] = None  # The "why does the business care" layer
    confidence: float               # 0.0-1.0
    confidence_level: ConfidenceLevel
    evidence: List[EvidenceSource] = []
    knowledge_authors: List[str] = []    # People whose artifacts contributed
    synthesized_at: datetime
    written_to_datahub: bool = False


class RiskAsset(BaseModel):
    asset_urn: str
    asset_name: str
    asset_type: str                 # TABLE, PIPELINE, DASHBOARD, etc.
    platform: str                   # snowflake, dbt, looker, etc.
    risk_level: Literal["CRITICAL", "AT_RISK", "SAFE"]
    risk_score: float                # 0.0-1.0
    downstream_consumer_count: int
    documentation_coverage: float   # 0.0-1.0, how much is documented
    last_owner_activity_days: int   # Days since owner last committed
    sole_owner: bool                 # True = single point of failure
    risk_reasons: List[str] = []     # Human-readable reasons for risk level


class LineageNode(BaseModel):
    urn: str
    name: str
    platform: str


class GraphEdge(BaseModel):
    source: str  # upstream asset urn
    target: str  # downstream asset urn


class DependencyGraphResponse(BaseModel):
    nodes: List[LineageNode] = []
    edges: List[GraphEdge] = []


class AssetDetailResponse(BaseModel):
    asset_urn: str
    asset_name: str
    platform: str
    risk: RiskAsset
    upstream: List[LineageNode] = []
    downstream: List[LineageNode] = []
    evidence: List[EvidenceSource] = []


class ExcavationJob(BaseModel):
    job_id: str
    asset_urn: str
    status: Literal["PENDING", "MINING", "SYNTHESIZING", "WRITING", "DONE", "FAILED"]
    progress_messages: List[str] = []
    result: Optional[KnowledgeUnit] = None
    started_at: datetime
    completed_at: Optional[datetime] = None
