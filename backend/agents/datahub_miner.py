from datahub.metadata.urns import DatasetUrn

from datahub_integration.client import DataHubClient
from models.schemas import EvidenceSource, RiskAsset

DOWNSTREAM_RISK_THRESHOLD = 5
STALE_OWNER_DAYS_THRESHOLD = 90


class DataHubMiner:
    def __init__(self):
        self.client = DataHubClient()

    async def mine(self, asset_urn: str) -> list[EvidenceSource]:
        """Detect knowledge signals from DataHub's own graph.

        These are patterns that INDICATE undocumented decisions, not
        direct evidence of intent — they get a lower relevance score
        than a PR comment that states intent explicitly.
        """
        evidence = []

        lineage = self.client.get_asset_lineage(asset_urn)
        downstream_count = len(lineage.get("downstreamEntities", []))
        doc = self.client.get_asset_documentation(asset_urn)

        if downstream_count > DOWNSTREAM_RISK_THRESHOLD and not doc:
            evidence.append(EvidenceSource(
                type="lineage_pattern",
                url=None,
                author=None,
                timestamp=None,
                raw_excerpt=(
                    f"Asset has {downstream_count} downstream consumers but zero "
                    f"documentation. High-usage undocumented asset — likely "
                    f"contains critical business logic."
                ),
                relevance_score=0.6,
            ))

        ownership = self.client.get_asset_ownership(asset_urn)
        if len(ownership) == 1:
            evidence.append(EvidenceSource(
                type="lineage_pattern",
                url=None,
                author=ownership[0],
                timestamp=None,
                raw_excerpt=(
                    f"Single owner: {ownership[0]}. No backup ownership "
                    f"registered. Knowledge concentration risk."
                ),
                relevance_score=0.5,
            ))

        return evidence

    def compute_risk_for_urn(self, urn: str) -> RiskAsset:
        """Compute the risk score for a single asset.

        Score is a weighted blend of: downstream fan-out (impact if wrong),
        inverse documentation coverage (how blind we are), owner staleness
        (how likely the knowledge is already gone), and sole ownership
        (single point of failure).
        """
        lineage = self.client.get_asset_lineage(urn)
        downstream_count = len(lineage.get("downstreamEntities", []))

        doc = self.client.get_asset_documentation(urn)
        doc_coverage = 1.0 if doc else 0.0

        ownership = self.client.get_asset_ownership(urn)
        sole_owner = len(ownership) == 1

        # DataHub doesn't expose "last commit by owner" directly; this
        # is populated by cross-referencing git_miner activity where
        # available, and defaults to unknown (0) otherwise.
        last_owner_activity_days = 0

        impact = min(downstream_count / 10, 1.0)
        blindness = 1.0 - doc_coverage
        staleness = min(last_owner_activity_days / STALE_OWNER_DAYS_THRESHOLD, 1.0)
        concentration = 1.0 if sole_owner else 0.3

        risk_score = (
            0.35 * impact
            + 0.30 * blindness
            + 0.20 * staleness
            + 0.15 * concentration
        )

        if risk_score >= 0.8:
            risk_level = "CRITICAL"
        elif risk_score >= 0.5:
            risk_level = "AT_RISK"
        else:
            risk_level = "SAFE"

        risk_reasons = []
        if downstream_count > DOWNSTREAM_RISK_THRESHOLD:
            risk_reasons.append(f"{downstream_count} downstream consumers depend on this asset")
        if doc_coverage == 0:
            risk_reasons.append("No documentation on file")
        if sole_owner:
            risk_reasons.append(f"Single owner ({ownership[0]}) — no backup registered")
        if not ownership:
            risk_reasons.append("No registered owner")

        parsed_urn = DatasetUrn.from_string(urn)

        return RiskAsset(
            asset_urn=urn,
            asset_name=parsed_urn.name,
            asset_type="TABLE",
            platform=parsed_urn.get_data_platform_urn().platform_name,
            risk_level=risk_level,
            risk_score=round(risk_score, 2),
            downstream_consumer_count=downstream_count,
            documentation_coverage=doc_coverage,
            last_owner_activity_days=last_owner_activity_days,
            sole_owner=sole_owner,
            risk_reasons=risk_reasons,
        )

    async def compute_risk_scores(self) -> list[RiskAsset]:
        """Compute risk scores for ALL assets in DataHub — used to populate
        the Knowledge at Risk dashboard.
        """
        risk_assets = [
            self.compute_risk_for_urn(urn) for urn in self.client.get_all_datasets()
        ]
        return sorted(risk_assets, key=lambda a: a.risk_score, reverse=True)
