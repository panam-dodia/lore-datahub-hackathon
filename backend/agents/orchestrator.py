import asyncio

from agents.confidence_scorer import ConfidenceScorer
from agents.datahub_miner import DataHubMiner
from agents.git_miner import GitMiner
from agents.synthesis_agent import SynthesisAgent
from datahub.metadata.urns import DatasetUrn
from datahub_integration.writer import DataHubWriter
from models.schemas import KnowledgeUnit


class OrchestratorAgent:
    def __init__(self):
        self.git_miner = GitMiner()
        self.datahub_miner = DataHubMiner()
        self.synthesis_agent = SynthesisAgent()
        self.confidence_scorer = ConfidenceScorer()
        self.writer = DataHubWriter()

    async def excavate(self, asset_urn: str, asset_name: str, progress_callback) -> KnowledgeUnit:
        """Full excavation pipeline for a single asset.

        progress_callback(message: str) streams updates to the frontend via
        WebSocket.
        """
        await progress_callback(f"Starting excavation for {asset_name}...")

        # DataHub's fully-qualified asset_name (e.g. "b2fd91.schema.TABLE_NAME")
        # includes an instance-specific prefix that no commit message would
        # ever literally contain. Git mining is a literal substring search, so
        # it needs the bare table name instead.
        search_term = asset_name.rsplit(".", 1)[-1]
        platform = DatasetUrn.from_string(asset_urn).get_data_platform_urn().platform_name

        await progress_callback(
            f'Mining GitHub history and DataHub lineage for "{search_term}"...'
        )
        git_evidence, datahub_evidence = await asyncio.gather(
            self.git_miner.mine(search_term),
            self.datahub_miner.mine(asset_urn),
        )
        await progress_callback(
            f"Found {len(git_evidence)} git artifacts, {len(datahub_evidence)} lineage signals"
        )

        await progress_callback("Synthesizing knowledge across all sources...")
        all_evidence = git_evidence + datahub_evidence
        knowledge = await self.synthesis_agent.synthesize(asset_urn, asset_name, platform, all_evidence)

        knowledge = self.confidence_scorer.score(knowledge)
        await progress_callback(
            f"Confidence level: {knowledge.confidence_level.value} ({knowledge.confidence:.0%})"
        )

        if knowledge.confidence_level == "HIGH":
            await progress_callback("High confidence — writing knowledge to DataHub...")
            success = self.writer.write_knowledge_back(knowledge)
            knowledge.written_to_datahub = success
            if success:
                await progress_callback("Knowledge written to DataHub successfully")
            else:
                await progress_callback("Failed to write knowledge to DataHub — see server logs")
        elif knowledge.confidence_level == "MEDIUM":
            saved = self.writer.write_pending_review(knowledge)
            if saved:
                await progress_callback(
                    "Medium confidence — saved to the Pending Review queue for a human to approve"
                )
            else:
                await progress_callback("Medium confidence — failed to save for review, see server logs")
        else:
            await progress_callback("Low confidence — surfaced for manual inspection only")

        return knowledge
