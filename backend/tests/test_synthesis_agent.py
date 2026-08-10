from unittest.mock import AsyncMock

from agents.synthesis_agent import SynthesisAgent, _extract_json
from models.schemas import ConfidenceLevel, EvidenceSource


def test_extract_json_plain():
    assert _extract_json('{"a": 1}') == '{"a": 1}'


def test_extract_json_markdown_fenced():
    # Regression: Groq sometimes wraps its response in a code fence despite
    # the prompt saying not to — this used to crash json.loads outright.
    text = '```json\n{"a": 1}\n```'
    assert _extract_json(text) == '{"a": 1}'


def test_extract_json_with_stray_text():
    text = 'Here is the result:\n{"a": 1}\nHope that helps!'
    assert _extract_json(text) == '{"a": 1}'


async def test_synthesize_no_evidence_returns_low_confidence():
    agent = SynthesisAgent.__new__(SynthesisAgent)  # skip __init__, no real LLMClient needed
    result = await agent.synthesize(
        "urn:li:dataset:(urn:li:dataPlatform:test,x,PROD)", "x", "test", []
    )
    assert result.confidence == 0.0
    assert result.confidence_level == ConfidenceLevel.LOW


async def test_synthesize_parses_fenced_llm_response():
    agent = SynthesisAgent.__new__(SynthesisAgent)
    agent.llm = AsyncMock()
    agent.llm.complete.return_value = (
        "```json\n"
        '{"why_it_exists": "test reason", "known_quirks": null, '
        '"business_context": null, "confidence_score": 0.9}\n'
        "```"
    )
    evidence = [
        EvidenceSource(type="commit_message", raw_excerpt="test", relevance_score=0.7, author="alice")
    ]
    result = await agent.synthesize(
        "urn:li:dataset:(urn:li:dataPlatform:test,x,PROD)", "x", "test", evidence
    )
    assert result.why_it_exists == "test reason"
    assert result.confidence == 0.9
    assert result.knowledge_authors == ["alice"]
