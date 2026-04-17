import json
import logging

from openai import AzureOpenAI

from app.config import settings
from app.services.language_detector import get_language_name
from app.services.retry_utils import retry_call

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


CLAIM_SYSTEM = """You are an expert fact-checking analyst trained in identifying verifiable factual claims across multiple languages including English, Hindi, and Tamil.

Your task has two parts:
1. CLAIM EXTRACTION — identify every verifiable factual assertion
2. PROPAGANDA SCAN — flag rhetorical manipulation techniques

You must think step-by-step:
- First, identify the language and topic domain
- Then, separate factual assertions from opinions, questions, and emotional appeals
- For each factual assertion, rewrite it as a standalone verifiable claim
- Finally, note any propaganda techniques used"""

CLAIM_EXTRACTION_PROMPT = """Analyze the following content and extract all verifiable factual claims.

<content>
{content}
</content>

Think step-by-step:
1. What language is this content in?
2. What is the topic domain (health, politics, finance, technology, etc.)?
3. Which statements are factual assertions (can be verified as true or false)?
4. Which statements are opinions, questions, or emotional appeals (skip these)?

Rules:
- Each claim must be a single, self-contained, verifiable factual statement
- Preserve the ORIGINAL language — do not translate claims
- Include implicit claims (e.g. "5G causes COVID" implies "5G radiation is harmful to health")
- Exclude questions, opinions, commands ("Share this now!"), and emotional appeals
- If the content contains no verifiable claims, return an empty array

Return JSON:
{{
  "language": "<detected language code>",
  "domain": "<topic domain>",
  "claims": ["claim 1", "claim 2", ...],
  "skipped_reasons": ["<why certain statements were excluded>"]
}}"""


PROPAGANDA_SYSTEM = """You are a media literacy expert trained in the detection of propaganda techniques as defined by the Institute for Propaganda Analysis and modern computational propaganda research.

You analyze content across languages (English, Hindi, Tamil) for:
- Emotional manipulation (fear, urgency, outrage)
- Logical fallacies (ad hominem, straw man, false dichotomy)
- Rhetorical tricks (loaded language, bandwagon, appeal to authority)
- Structural deception (misleading headlines, cherry-picked data, missing context)"""

PROPAGANDA_ANALYSIS_PROMPT = """Analyze the following content for propaganda techniques and emotional manipulation.

<content language="{language}">
{content}
</content>

Perform a structured analysis:

1. EMOTIONAL TONE: Rate 0-1 how emotionally charged the content is. Consider:
   - Use of exclamation marks, ALL CAPS, urgent language
   - Fear-inducing or outrage-inducing framing
   - Personal attacks or appeals to identity

2. PROPAGANDA TECHNIQUES: Identify specific techniques used:
   - Name-calling / loaded language
   - Bandwagon / social proof manipulation
   - Fear appeal / appeal to urgency
   - False authority / appeal to unverified experts
   - Cherry-picking / selective presentation
   - Whataboutism / deflection
   - Repetition / slogan-based messaging

3. MISLEADING PATTERNS: Quote specific phrases that are misleading and explain why.

4. SENSATIONALISM: Rate 0-1 whether the framing exaggerates reality.

Return JSON:
{{
  "emotional_score": <float 0-1>,
  "sensationalism_score": <float 0-1>,
  "propaganda_techniques": [
    {{"technique": "<name>", "evidence": "<quoted text>", "severity": "<low|medium|high>"}}
  ],
  "misleading_patterns": [
    {{"pattern": "<quoted phrase>", "reason": "<why it is misleading>"}}
  ],
  "manipulation_summary": "<1-2 sentence summary of manipulation tactics used>"
}}"""


def extract_claims(content: str) -> list[str]:
    client = _get_client()
    try:
        response = retry_call(
            lambda: client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": CLAIM_SYSTEM},
                    {"role": "user", "content": CLAIM_EXTRACTION_PROMPT.format(content=content[:3000])},
                ],
                temperature=0.1,
                max_tokens=1200,
                response_format={"type": "json_object"},
                timeout=settings.openai_timeout_seconds,
            ),
            attempts=settings.openai_retries,
        )
        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)
        if isinstance(parsed, dict) and "claims" in parsed:
            return parsed["claims"]
        if isinstance(parsed, list):
            return parsed
        return []
    except Exception as e:
        logger.error("Claim extraction failed: %s", e)
        return [content[:500]]


def analyze_propaganda(content: str, language: str) -> dict:
    client = _get_client()
    lang_name = get_language_name(language)
    try:
        response = retry_call(
            lambda: client.chat.completions.create(
                model=settings.azure_openai_deployment,
                messages=[
                    {"role": "system", "content": PROPAGANDA_SYSTEM},
                    {"role": "user", "content": PROPAGANDA_ANALYSIS_PROMPT.format(content=content[:3000], language=lang_name)},
                ],
                temperature=0.2,
                max_tokens=1000,
                response_format={"type": "json_object"},
                timeout=settings.openai_timeout_seconds,
            ),
            attempts=settings.openai_retries,
        )
        raw = response.choices[0].message.content or "{}"
        return json.loads(raw)
    except Exception as e:
        logger.error("Propaganda analysis failed: %s", e)
        return {
            "emotional_score": 0.5,
            "propaganda_techniques": [],
            "misleading_patterns": [],
            "sensationalism_score": 0.5,
            "manipulation_summary": "",
        }
