SYNTHESIS_PROMPT = """
You are an expert data archaeologist. Your job is to analyze artifacts from
git history and data lineage patterns — and synthesize the institutional
knowledge buried within them.

ASSET NAME: {asset_name}
ASSET PLATFORM: {platform}

EVIDENCE COLLECTED:
{evidence_text}

Evidence was collected by searching for this asset's bare table name, which
can also match a same-named asset on a completely different platform (e.g. a
Snowflake table and a PowerBI report both called "order_details"). Before
using a piece of evidence, judge whether it's actually consistent with this
asset living on {platform} — e.g. evidence that explicitly discusses a
different platform, tool, or system than {platform} is likely about a
different asset entirely and should be weighted down or excluded.

Your task:
1. Synthesize WHY this data asset exists — what business problem does it solve?
2. Identify any QUIRKS, edge cases, or gotchas mentioned (e.g. "always null on weekends")
3. Extract BUSINESS CONTEXT — what downstream decisions depend on this data?
4. Assign a CONFIDENCE SCORE (0.0-1.0) based on:
   - How many independent sources agree
   - Recency of the evidence
   - Specificity of the information
   - Whether the evidence is actually consistent with the {platform} platform

Return ONLY a valid JSON object. No preamble. No explanation. Just JSON:

{{
  "why_it_exists": "Clear explanation of why this asset was created and what it does",
  "known_quirks": "Any edge cases, gotchas, or anomalies found (null if none)",
  "business_context": "Business decisions or downstream impacts that depend on this (null if none)",
  "confidence_score": 0.85,
  "confidence_reasoning": "Brief explanation of why you assigned this confidence score"
}}
"""

RISK_ANALYSIS_PROMPT = """
You are analyzing a data asset for knowledge loss risk.

Asset: {asset_name}
Downstream consumers: {downstream_count}
Documentation coverage: {doc_coverage}%
Days since owner last active: {days_inactive}
Number of owners: {owner_count}

Based on these signals, provide a 1-2 sentence human-readable explanation of
why this asset is at risk of knowledge loss. Be specific, not generic.

Return ONLY the explanation text, no JSON, no preamble.
"""
