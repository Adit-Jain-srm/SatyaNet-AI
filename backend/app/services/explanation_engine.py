import json
import logging

from openai import AzureOpenAI

from app.config import settings
from app.services.language_detector import get_language_name

logger = logging.getLogger(__name__)

_client: AzureOpenAI | None = None


def _get_client() -> AzureOpenAI:
    global _client
    if _client is None:
        _client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
    return _client


EXPLANATION_SYSTEM = """You are SatyaNet, a multilingual fact-checking AI assistant built to combat misinformation in India.

Your role is to EXPLAIN verdicts and PROVIDE verified alternatives — not just label content as true or false. You are the "Response Layer" of a three-layer misinformation pipeline:
- Layer A (Detection) has already identified signals
- Layer B (Understanding) has already retrieved evidence and matched patterns
- Layer C (Response — YOU) must now explain, educate, and provide actionable counter-information

You must respond ENTIRELY in {language}. Your tone should be:
- Authoritative but not alarmist
- Educational, not condescending
- Specific with evidence, not vague
- Actionable — tell users what to do with this information"""

EXPLANATION_PROMPT = """Based on the following multi-source analysis, generate a comprehensive fact-check response.

<analysis_context>
Content analyzed: {content}
Claims extracted: {claims}

CREDIBILITY SIGNALS:
- Overall credibility score: {credibility_score}/1.00
- Verdict: {verdict}

EVIDENCE FROM QDRANT VECTOR DATABASE:
{evidence}

KNOWN MISINFORMATION PATTERN MATCHES:
{misinfo_matches}

SOURCE CREDIBILITY RATING: {source_credibility}/1.00

EXTERNAL FACT-CHECKS (Google Fact Check Tools API):
{external_reviews}
</analysis_context>

Now, think step-by-step:

1. ASSESS: What is the core claim? Is it completely false, partially true, or taken out of context?
2. EVIDENCE: What specific evidence supports or contradicts the claim?
3. PATTERN: Does this match known misinformation patterns? If so, which ones?
4. CONTEXT: What is the missing context that makes this misleading?
5. VERDICT REASONING: In 1-2 sentences, explain exactly WHY this verdict was reached. Be specific — reference the signals that drove the decision. For example: "Rated misleading because the claim about UPI being banned matches a known debunked hoax pattern (92% similarity) and contradicts verified RBI data, despite the source appearing credible."

Generate three outputs:

A) EXPLANATION (150-250 words): Structured analysis with numbered reasons, evidence citations, and what the user should know.

B) COUNTER-CONTENT: The verified truth with citations. What should people know instead? Include specific sources (PIB Fact Check, WHO, RBI, etc.).

C) SHAREABLE SUMMARY: A 2-3 sentence WhatsApp-ready message that debunks/confirms the claim with a source citation.

D) VERDICT REASON: One precise sentence explaining why this specific verdict was assigned. This must reference concrete evidence (similarity scores, matched patterns, source ratings).

Return JSON:
{{
  "explanation": "<the explanation text>",
  "counter_content": "<verified alternative information with citations>",
  "shareable_summary": "<2-3 sentence WhatsApp-ready summary>",
  "verdict_reason": "<1 sentence explaining why this verdict>"
}}"""


def generate_explanation(
    content: str,
    claims: list[str],
    credibility_score: float,
    verdict: str,
    evidence: list[dict],
    misinfo_matches: list[dict],
    source_credibility: float,
    language: str,
    external_reviews: list[dict] | None = None,
) -> dict:
    client = _get_client()
    lang_name = get_language_name(language)

    evidence_text = "\n".join(
        f"- [{e.get('collection', 'verified_facts')}] {e.get('text', '')[:200]} "
        f"(source: {e.get('source', 'unknown')}, similarity: {e.get('relevance_score', 0):.0%})"
        for e in evidence[:5]
    ) or "No matching evidence found in verified database."

    misinfo_text = "\n".join(
        f"- MATCH ({m.get('similarity', 0):.0%} similar): \"{m.get('original_claim', '')[:150]}\"\n"
        f"  Debunked: {m.get('debunk_summary', '')[:200]}"
        for m in misinfo_matches[:3]
    ) or "No matching misinformation patterns found."

    external_text = "None found."
    if external_reviews:
        lines = []
        for r in external_reviews[:3]:
            pub = r.get("publisher_name", "Unknown")
            rating = r.get("rating", "N/A")
            url = r.get("url", "")
            lines.append(f"- {pub} rated this: \"{rating}\" — {url}")
        external_text = "\n".join(lines)

    try:
        response = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {
                    "role": "system",
                    "content": EXPLANATION_SYSTEM.format(language=lang_name),
                },
                {
                    "role": "user",
                    "content": EXPLANATION_PROMPT.format(
                        content=content[:500],
                        claims=json.dumps(claims, ensure_ascii=False),
                        credibility_score=f"{credibility_score:.2f}",
                        evidence=evidence_text,
                        misinfo_matches=misinfo_text,
                        source_credibility=f"{source_credibility:.2f}",
                        verdict=verdict,
                        external_reviews=external_text,
                    ),
                },
            ],
            temperature=0.3,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        result = json.loads(raw)
        return {
            "explanation": result.get("explanation", "Analysis complete."),
            "counter_content": result.get("counter_content", ""),
            "shareable_summary": result.get("shareable_summary", ""),
            "verdict_reason": result.get("verdict_reason", ""),
        }
    except Exception as e:
        logger.error("Explanation generation failed: %s", e)
        return {
            "explanation": f"This content has a credibility score of {credibility_score:.0%}. Verdict: {verdict}.",
            "counter_content": "Unable to generate counter-content at this time.",
            "shareable_summary": f"SatyaNet Analysis: Credibility {credibility_score:.0%} — {verdict}",
            "verdict_reason": f"Credibility score of {credibility_score:.0%} falls in the {verdict} range.",
        }
