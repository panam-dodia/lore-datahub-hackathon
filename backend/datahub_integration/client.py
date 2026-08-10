import os
from typing import Optional

from datahub.emitter.rest_emitter import DatahubRestEmitter
from datahub.ingestion.graph.client import DataHubGraph, DataHubGraphConfig
from datahub.ingestion.graph.openapi import LineageDirection
from datahub.metadata.schema_classes import DatasetPropertiesClass, OwnershipClass


class DataHubClient:
    """Thin wrapper around the DataHub Python SDK's graph client + REST emitter."""

    def __init__(self):
        self.gms_url = os.getenv("DATAHUB_GMS_URL", "http://localhost:8080")
        self.token = os.getenv("DATAHUB_TOKEN") or None

        config = DataHubGraphConfig(server=self.gms_url, token=self.token)
        self.graph = DataHubGraph(config)
        self.emitter = DatahubRestEmitter(gms_server=self.gms_url, token=self.token)

    def get_all_datasets(self) -> list:
        """Fetch all dataset URNs from DataHub."""
        return list(self.graph.get_urns_by_filter(entity_types=["dataset"]))

    def get_asset_lineage(self, urn: str) -> dict:
        """Get upstream + downstream lineage for an asset."""
        upstream = self.graph.scroll_lineage(urns=[urn], direction=LineageDirection.UPSTREAM)
        downstream = self.graph.scroll_lineage(urns=[urn], direction=LineageDirection.DOWNSTREAM)
        return {
            "upstreamEntities": [r.upstream_urn for r in upstream.relationships],
            "downstreamEntities": [r.downstream_urn for r in downstream.relationships],
        }

    def get_asset_ownership(self, urn: str) -> list:
        """Get owners of an asset."""
        ownership = self.graph.get_aspect(entity_urn=urn, aspect_type=OwnershipClass)
        if not ownership or not ownership.owners:
            return []
        return [owner.owner for owner in ownership.owners]

    def get_asset_documentation(self, urn: str) -> Optional[str]:
        """Get existing documentation if any."""
        properties = self.graph.get_aspect(entity_urn=urn, aspect_type=DatasetPropertiesClass)
        if properties and properties.description:
            return properties.description
        return None

    def write_knowledge_back(self, knowledge) -> bool:
        """Write synthesized knowledge as DataHub documentation + custom properties.

        Delegates to datahub_integration.writer.DataHubWriter, kept here as a
        pass-through so callers can go through a single client entrypoint.
        """
        from datahub_integration.writer import DataHubWriter

        return DataHubWriter(client=self).write_knowledge_back(knowledge)
