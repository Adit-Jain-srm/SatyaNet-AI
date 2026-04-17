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


EXPLANATION_PROMPT = """You are a trusted fact-checker explaining your analysis to a general audience.

Language: Respond ENTIRELY in {language}.

Content analyzed: {content}
Claims found: {claims}
Credibility score: {credibility_score}/1.0
Evidence from verified database: {evidence}
Matching misinformation patterns: {misinfo_matches}
Source credibility: {source_credibility}
External fact-checks (Google Fact Check Tools): {external_reviews}

Generate a clear, structured explanation of why this content is rated {verdict}. Include:
1. A brief summary of what was checked
2. Key reasons for the verdict (numbered)
3. Specific evidence references (including any external fact-checks found)
4. What users should know

Keep it concise (150-250 words). Be factual, not alarmist. If external fact-checks exist, cite them prominently.

Return JSON:
{{
  "explanation": "<the explanation text>",
  "counter_content": "<verified alternative information with citations>",
  "shareable_summary": "<2-3 sentence summary suitable for sharing on WhatsApp>"
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
        f"- {e.get('text', '')[:200]} (source: {e.get('source', 'unknown')}, relevance: {e.get('relevance_score', 0):.2f})"
        for e in evidence[:5]
    ) or "No matching evidence found in verified database."

    misinfo_text = "\n".join(
        f"- Known claim: \"{m.get('original_claim', '')[:150]}\" — Debunked: {m.get('debunk_summary', '')[:150]} (similarity: {m.get('similarity', 0):.2f})"
        for m in misinfo_matches[:3]
    ) or "No matching misinformation patterns found."

    external_text = "None found."
    if external_reviews:
        lines = []
        for r in external_reviews[:3]:
            pub = r.get("publisher_name", "Unknown")
            rating = r.get("rating", "N/A")
            url = r.get("url", "")
            lines.append(f"- {pub}: \"{rating}\" ({url})")
        external_text = "\n".join(lines)

    try:
        response = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {
                    "role": "system",
                    "content": f"You are SatyaNet, a multilingual fact-checking AI assistant. Always respond in {lang_name}. Always respond with valid JSON.",
                },
                {
                    "role": "user",
                    "content": EXPLANATION_PROMPT.format(
                        language=lang_name,
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
            max_tokens=1500,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        result = json.loads(raw)
        return {
            "explanation": result.get("explanation", "Analysis complete."),
            "counter_content": result.get("counter_content", ""),
            "shareable_summary": result.get("shareable_summary", ""),
        }
    except Exception as e:
        logger.error("Explanation generation failed: %s", e)
        return {
            "explanation": f"This content has a credibility score of {credibility_score:.0%}. Verdict: {verdict}.",
            "counter_content": "Unable to generate counter-content at this time.",
            "shareable_summary": f"SatyaNet Analysis: Credibility {credibility_score:.0%} — {verdict}",
        }
