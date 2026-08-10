from datetime import datetime

from agents.confidence_scorer import ConfidenceScorer
from models.schemas import ConfidenceLevel, KnowledgeUnit


def _knowledge(confidence: float) -> KnowledgeUnit:
    return KnowledgeUnit(
        asset_urn="urn:li:dataset:(urn:li:dataPlatform:test,x,PROD)",
        asset_name="x",
        why_it_exists="because",
        confidence=confidence,
        confidence_level=ConfidenceLevel.LOW,
        synthesized_at=datetime.utcnow(),
    )


def test_high_confidence_boundary():
    assert ConfidenceScorer().score(_knowledge(0.80)).confidence_level == ConfidenceLevel.HIGH
    assert ConfidenceScorer().score(_knowledge(0.79)).confidence_level == ConfidenceLevel.MEDIUM


def test_medium_confidence_boundary():
    assert ConfidenceScorer().score(_knowledge(0.50)).confidence_level == ConfidenceLevel.MEDIUM
    assert ConfidenceScorer().score(_knowledge(0.49)).confidence_level == ConfidenceLevel.LOW


def test_low_confidence():
    assert ConfidenceScorer().score(_knowledge(0.0)).confidence_level == ConfidenceLevel.LOW
