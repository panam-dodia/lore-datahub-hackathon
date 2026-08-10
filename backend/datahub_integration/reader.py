"""Higher-level read helpers built on top of DataHubClient.

Where client.py wraps individual SDK/graph calls, this module composes them
into the shapes the agents actually want (e.g. "everything needed to score
risk for one asset" in a single call).
"""

from datahub_integration.client import DataHubClient


class DataHubReader:
    def __init__(self, client: DataHubClient = None):
        self.client = client or DataHubClient()

    def get_asset_snapshot(self, urn: str) -> dict:
        """Bundle lineage, ownership, and documentation for a single asset."""
        return {
            "urn": urn,
            "lineage": self.client.get_asset_lineage(urn),
            "owners": self.client.get_asset_ownership(urn),
            "documentation": self.client.get_asset_documentation(urn),
        }

    def get_all_asset_snapshots(self) -> list:
        """Bundle snapshots for every dataset known to DataHub."""
        return [self.get_asset_snapshot(urn) for urn in self.client.get_all_datasets()]
