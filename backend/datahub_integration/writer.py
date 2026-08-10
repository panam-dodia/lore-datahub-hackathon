from datahub.emitter.mcp import MetadataChangeProposalWrapper
from datahub.metadata.schema_classes import DatasetPropertiesClass

from datahub_integration.client import DataHubClient
from datahub_integration.knowledge_codec import decode_knowledge, encode_custom_properties
from models.schemas import KnowledgeUnit


class DataHubWriter:
    """Writes synthesized KnowledgeUnits back to DataHub as documentation
    plus structured custom properties, so both humans and downstream tools
    can consume what Lore found.
    """

    LORE_MARKER = "*Synthesized by Lore"

    def __init__(self, client: DataHubClient = None):
        self.client = client or DataHubClient()

    def _build_doc_text(self, knowledge: KnowledgeUnit) -> str:
        doc_text = f"## Why This Exists\n{knowledge.why_it_exists}\n\n"
        if knowledge.known_quirks:
            doc_text += f"## Known Quirks\n{knowledge.known_quirks}\n\n"
        if knowledge.business_context:
            doc_text += f"## Business Context\n{knowledge.business_context}\n\n"

        doc_text += f"---\n*Synthesized by Lore with {knowledge.confidence:.0%} confidence.*\n"
        evidence_urls = [e.url for e in knowledge.evidence if e.url]
        if evidence_urls:
            doc_text += f"*Evidence: {', '.join(evidence_urls)}*"
        return doc_text

    def _get_properties(self, urn: str) -> DatasetPropertiesClass:
        properties = self.client.graph.get_aspect(entity_urn=urn, aspect_type=DatasetPropertiesClass)
        return properties if properties is not None else DatasetPropertiesClass()

    def _emit_properties(self, urn: str, properties: DatasetPropertiesClass):
        mcp = MetadataChangeProposalWrapper(entityUrn=urn, aspect=properties)
        self.client.emitter.emit(mcp)

    def write_knowledge_back(self, knowledge: KnowledgeUnit) -> bool:
        """Auto-write path for HIGH-confidence results: writes both the
        human-readable documentation and the structured custom properties,
        marking this asset's review status as 'approved'.
        """
        try:
            dataset_urn = knowledge.asset_urn
            doc_text = self._build_doc_text(knowledge)
            custom_props = encode_custom_properties(knowledge, review_status="approved")

            properties = self._get_properties(dataset_urn)
            existing_description = properties.description or ""

            # A dataset's documentation lives in the "description" field of
            # its DatasetProperties aspect (the same aspect get_asset_documentation
            # reads) — there is no separate "documentation" aspect for whole
            # datasets, only for individual schema fields.
            if existing_description and self.LORE_MARKER not in existing_description:
                # Preserve pre-existing documentation instead of overwriting it.
                # Different platforms can expose assets with the same leaf
                # table name (e.g. a Snowflake table and a PowerBI report both
                # called "order_details") — literal-string evidence mining
                # can't always tell them apart, so a write here might be
                # about a different real-world thing than whatever originally
                # documented this asset. Appending, not replacing, means a
                # mismatched excavation can't destroy real prior knowledge.
                properties.description = existing_description.rstrip() + "\n\n---\n\n" + doc_text
            else:
                properties.description = doc_text

            properties.customProperties = {**(properties.customProperties or {}), **custom_props}
            self._emit_properties(dataset_urn, properties)
            return True

        except Exception as e:
            print(f"Failed to write to DataHub: {e}")
            return False

    def write_pending_review(self, knowledge: KnowledgeUnit) -> bool:
        """MEDIUM-confidence path: stashes the full result in custom
        properties, marked 'pending', WITHOUT touching the visible
        description — nothing shows up in DataHub's documentation until a
        human approves it via approve_pending().
        """
        try:
            dataset_urn = knowledge.asset_urn
            custom_props = encode_custom_properties(knowledge, review_status="pending")

            properties = self._get_properties(dataset_urn)
            properties.customProperties = {**(properties.customProperties or {}), **custom_props}
            self._emit_properties(dataset_urn, properties)
            return True

        except Exception as e:
            print(f"Failed to save pending review to DataHub: {e}")
            return False

    def approve_pending(self, asset_urn: str) -> bool:
        """Promotes a pending review into the same auto-write path HIGH
        confidence results use — writes the documentation and flips the
        review status to 'approved'.
        """
        properties = self._get_properties(asset_urn)
        knowledge = decode_knowledge(asset_urn, properties.customProperties or {})
        if knowledge is None:
            return False
        return self.write_knowledge_back(knowledge)

    def reject_pending(self, asset_urn: str) -> bool:
        """Discards a pending review — clears Lore's custom properties
        without ever having touched the description, so there's nothing
        else to undo.
        """
        try:
            properties = self._get_properties(asset_urn)
            properties.customProperties = {
                k: v for k, v in (properties.customProperties or {}).items()
                if not k.startswith("lore_")
            }
            self._emit_properties(asset_urn, properties)
            return True
        except Exception as e:
            print(f"Failed to reject pending review: {e}")
            return False
