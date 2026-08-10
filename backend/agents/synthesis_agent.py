import json
from datetime import datetime

from models.schemas import ConfidenceLevel, EvidenceSource, KnowledgeUnit
from utils.llm import LLMClient
from utils.prompts import SYNTHESIS_PROMPT


def _extract_json(text: str) -> str:
    """LLMs sometimes wrap JSON in a markdown code fence or add stray text
    around it despite being told not to — this strips that so json.loads
    gets a clean object instead of failing on the first character.
    """
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```")[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    start, end = text.find("{"), text.rfind("}")
    if start != -1 and end != -1:
        text = text[start : end + 1]
    return text


class SynthesisAgent:
    def __init__(self):
        self.llm = LLMClient()

    async def synthesize(
        self, asset_urn: str, asset_name: str, platform: str, evidence: list[EvidenceSource]
    ) -> KnowledgeUnit:
        """Cross-reference all evidence sources and synthesize structured
        institutional knowledge via LLM.
        """
        if not evidence:
            return KnowledgeUnit(
                asset_urn=asset_urn,
                asset_name=asset_name,
                why_it_exists="No evidence found across git history or DataHub lineage.",
                confidence=0.0,
                confidence_level=ConfidenceLevel.LOW,
                evidence=[],
                knowledge_authors=[],
                synthesized_at=datetime.utcnow(),
            )

        evidence_text = "\n\n---\n\n".join([
            f"SOURCE TYPE: {e.type}\n"
            f"AUTHOR: {e.author or 'unknown'}\n"
            f"RELEVANCE: {e.relevance_score}\n"
            f"CONTENT:\n{e.raw_excerpt}"
            for e in evidence
        ])

        prompt = SYNTHESIS_PROMPT.format(
            asset_name=asset_name, platform=platform, evidence_text=evidence_text
        )
        response = await self.llm.complete(prompt)
        parsed = json.loads(_extract_json(response))

        authors = list({e.author for e in evidence if e.author})

        return KnowledgeUnit(
            asset_urn=asset_urn,
            asset_name=asset_name,
            why_it_exists=parsed.get("why_it_exists", ""),
            known_quirks=parsed.get("known_quirks"),
            business_context=parsed.get("business_context"),
            confidence=parsed.get("confidence_score", 0.5),
            confidence_level=ConfidenceLevel.LOW,  # set by ConfidenceScorer
            evidence=evidence,
            knowledge_authors=authors,
            synthesized_at=datetime.utcnow(),
        )
