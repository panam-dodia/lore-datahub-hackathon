"""Encodes/decodes a KnowledgeUnit to and from DataHub's customProperties,
so DataHub itself is the durable store for what Lore has found — used by
both the writer (to encode) and the API routes (to decode for display).
Shared here so neither has to duplicate the field mapping.
"""

import json

from datahub.metadata.urns import DatasetUrn

from models.schemas import EvidenceSource, KnowledgeUnit


def encode_custom_properties(knowledge: KnowledgeUnit, review_status: str) -> dict:
    """review_status is 'approved' (auto-written, HIGH confidence) or
    'pending' (awaiting human review, MEDIUM confidence).
    """
    return {
        "lore_why_it_exists": knowledge.why_it_exists,
        "lore_known_quirks": knowledge.known_quirks or "",
        "lore_business_context": knowledge.business_context or "",
        "lore_confidence": str(knowledge.confidence),
        "lore_confidence_level": knowledge.confidence_level.value,
        "lore_knowledge_authors": ", ".join(knowledge.knowledge_authors),
        "lore_evidence_count": str(len(knowledge.evidence)),
        "lore_evidence_json": json.dumps([e.model_dump(mode="json") for e in knowledge.evidence]),
        "lore_synthesized_at": knowledge.synthesized_at.isoformat(),
        "lore_review_status": review_status,
    }


def decode_knowledge(urn: str, custom_properties: dict) -> KnowledgeUnit | None:
    if "lore_confidence" not in custom_properties:
        return None

    parsed_urn = DatasetUrn.from_string(urn)
    evidence_data = json.loads(custom_properties.get("lore_evidence_json", "[]"))
    authors = [
        a.strip() for a in custom_properties.get("lore_knowledge_authors", "").split(",") if a.strip()
    ]

    return KnowledgeUnit(
        asset_urn=urn,
        asset_name=parsed_urn.name,
        why_it_exists=custom_properties.get("lore_why_it_exists", ""),
        known_quirks=custom_properties.get("lore_known_quirks") or None,
        business_context=custom_properties.get("lore_business_context") or None,
        confidence=float(custom_properties.get("lore_confidence", 0)),
        confidence_level=custom_properties.get("lore_confidence_level", "LOW"),
        evidence=[EvidenceSource(**e) for e in evidence_data],
        knowledge_authors=authors,
        synthesized_at=custom_properties.get("lore_synthesized_at"),
        # Records written before this pending-review feature existed have no
        # lore_review_status at all — they were always written via the
        # unconditional auto-write path, so treat "missing" as "approved"
        # rather than misclassifying old knowledge as newly pending.
        written_to_datahub=custom_properties.get("lore_review_status", "approved") == "approved",
    )
