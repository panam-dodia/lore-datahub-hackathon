from models.schemas import ConfidenceLevel, KnowledgeUnit

HIGH_THRESHOLD = 0.80
MEDIUM_THRESHOLD = 0.50


class ConfidenceScorer:
    """Assigns the routing tier (HIGH/MEDIUM/LOW) that determines whether a
    KnowledgeUnit is auto-written to DataHub, flagged for review, or only
    surfaced for manual inspection.
    """

    def score(self, knowledge: KnowledgeUnit) -> KnowledgeUnit:
        if knowledge.confidence >= HIGH_THRESHOLD:
            knowledge.confidence_level = ConfidenceLevel.HIGH
        elif knowledge.confidence >= MEDIUM_THRESHOLD:
            knowledge.confidence_level = ConfidenceLevel.MEDIUM
        else:
            knowledge.confidence_level = ConfidenceLevel.LOW
        return knowledge
