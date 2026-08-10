from datetime import datetime, timezone

from datahub_integration.knowledge_codec import decode_knowledge, encode_custom_properties
from models.schemas import ConfidenceLevel, EvidenceSource, KnowledgeUnit


def _sample_knowledge() -> KnowledgeUnit:
    return KnowledgeUnit(
        asset_urn="urn:li:dataset:(urn:li:dataPlatform:snowflake,db.schema.table,PROD)",
        asset_name="db.schema.table",
        why_it_exists="It stores order data.",
        known_quirks="Nulls on weekends.",
        business_context="Feeds the finance dashboard.",
        confidence=0.85,
        confidence_level=ConfidenceLevel.HIGH,
        evidence=[
            EvidenceSource(
                type="commit_message", url="https://x", author="alice",
                raw_excerpt="fix bug", relevance_score=0.7,
            ),
        ],
        knowledge_authors=["alice", "bob"],
        synthesized_at=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )


def test_round_trip_preserves_all_fields():
    knowledge = _sample_knowledge()
    props = encode_custom_properties(knowledge, review_status="approved")
    rebuilt = decode_knowledge(knowledge.asset_urn, props)

    assert rebuilt.asset_name == knowledge.asset_name
    assert rebuilt.why_it_exists == knowledge.why_it_exists
    assert rebuilt.known_quirks == knowledge.known_quirks
    assert rebuilt.business_context == knowledge.business_context
    assert rebuilt.confidence == knowledge.confidence
    assert rebuilt.confidence_level == knowledge.confidence_level
    assert set(rebuilt.knowledge_authors) == set(knowledge.knowledge_authors)
    assert len(rebuilt.evidence) == 1
    assert rebuilt.evidence[0].url == "https://x"
    assert rebuilt.written_to_datahub is True


def test_pending_status_not_treated_as_written():
    knowledge = _sample_knowledge()
    props = encode_custom_properties(knowledge, review_status="pending")
    rebuilt = decode_knowledge(knowledge.asset_urn, props)
    assert rebuilt.written_to_datahub is False


def test_missing_review_status_defaults_to_approved():
    # Regression: records written before the pending-review feature existed
    # have no lore_review_status key at all — they must not be
    # misclassified as newly pending.
    knowledge = _sample_knowledge()
    props = encode_custom_properties(knowledge, review_status="approved")
    del props["lore_review_status"]
    rebuilt = decode_knowledge(knowledge.asset_urn, props)
    assert rebuilt.written_to_datahub is True


def test_decode_returns_none_when_no_lore_data():
    assert decode_knowledge("urn:li:dataset:(urn:li:dataPlatform:x,y,PROD)", {}) is None
