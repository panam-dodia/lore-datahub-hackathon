from datetime import datetime
from unittest.mock import MagicMock

from datahub.metadata.schema_classes import DatasetPropertiesClass

from datahub_integration.knowledge_codec import encode_custom_properties
from datahub_integration.writer import DataHubWriter
from models.schemas import ConfidenceLevel, KnowledgeUnit

SAMPLE_URN = "urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)"


def _knowledge() -> KnowledgeUnit:
    return KnowledgeUnit(
        asset_urn=SAMPLE_URN,
        asset_name="db.schema.table",
        why_it_exists="It stores order data.",
        confidence=0.85,
        confidence_level=ConfidenceLevel.HIGH,
        synthesized_at=datetime.utcnow(),
    )


def _writer_with_mock_client(existing_properties):
    client = MagicMock()
    client.graph.get_aspect.return_value = existing_properties
    return DataHubWriter(client=client), client


def _emitted_aspect(client):
    return client.emitter.emit.call_args[0][0].aspect


def test_write_knowledge_back_creates_new_properties_when_none_exist():
    writer, client = _writer_with_mock_client(None)
    assert writer.write_knowledge_back(_knowledge()) is True

    aspect = _emitted_aspect(client)
    assert "Why This Exists" in aspect.description
    assert aspect.customProperties["lore_review_status"] == "approved"


def test_write_knowledge_back_preserves_unrelated_existing_docs():
    # Regression: a mismatched excavation (same leaf name, different
    # platform) must not destroy real pre-existing documentation.
    existing = DatasetPropertiesClass(description="Original real documentation.", customProperties={})
    writer, client = _writer_with_mock_client(existing)
    writer.write_knowledge_back(_knowledge())

    aspect = _emitted_aspect(client)
    assert "Original real documentation." in aspect.description
    assert "Why This Exists" in aspect.description


def test_write_knowledge_back_replaces_its_own_prior_write():
    existing = DatasetPropertiesClass(
        description=(
            "## Why This Exists\nOld explanation.\n\n---\n"
            "*Synthesized by Lore with 70% confidence.*"
        ),
        customProperties={},
    )
    writer, client = _writer_with_mock_client(existing)
    writer.write_knowledge_back(_knowledge())

    aspect = _emitted_aspect(client)
    assert "Old explanation" not in aspect.description
    assert aspect.description.count("Synthesized by Lore") == 1


def test_write_pending_review_does_not_touch_description():
    existing = DatasetPropertiesClass(description="Original docs.", customProperties={})
    writer, client = _writer_with_mock_client(existing)
    writer.write_pending_review(_knowledge())

    aspect = _emitted_aspect(client)
    assert aspect.description == "Original docs."
    assert aspect.customProperties["lore_review_status"] == "pending"


def test_reject_pending_clears_only_lore_keys():
    existing = DatasetPropertiesClass(
        description="Docs.",
        customProperties={"lore_confidence": "0.6", "unrelated_key": "keep me"},
    )
    writer, client = _writer_with_mock_client(existing)
    writer.reject_pending(SAMPLE_URN)

    aspect = _emitted_aspect(client)
    assert "lore_confidence" not in aspect.customProperties
    assert aspect.customProperties["unrelated_key"] == "keep me"


def test_approve_pending_promotes_to_written():
    knowledge = _knowledge()
    pending_props = DatasetPropertiesClass(
        description="",
        customProperties=encode_custom_properties(knowledge, review_status="pending"),
    )
    writer, client = _writer_with_mock_client(pending_props)
    assert writer.approve_pending(SAMPLE_URN) is True

    aspect = _emitted_aspect(client)
    assert aspect.customProperties["lore_review_status"] == "approved"
    assert "Why This Exists" in aspect.description
