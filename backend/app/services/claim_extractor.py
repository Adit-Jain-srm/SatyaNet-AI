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


CLAIM_EXTRACTION_PROMPT = """You are a fact-checking analyst. Extract all verifiable factual claims from the following content.

Rules:
- Each claim should be a single, self-contained factual statement
- Ignore opinions, questions, and subjective statements
- Keep claims in the ORIGINAL language of the content
- If no verifiable claims exist, return an empty claims array

Content:
{content}

Return a JSON object: {{"claims": ["claim 1", "claim 2", ...]}}"""


PROPAGANDA_ANALYSIS_PROMPT = """Analyze the following content for propaganda techniques, emotional manipulation, and misleading language patterns.

Content (Language: {language}):
{content}

Return a JSON object with:
{{
  "emotional_score": <float 0-1, how emotionally charged>,
  "propaganda_techniques": [<list of detected techniques>],
  "misleading_patterns": [<specific misleading phrases or patterns found>],
  "sensationalism_score": <float 0-1>
}}"""


def extract_claims(content: str) -> list[str]:
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": "You extract factual claims from content. Always respond with valid JSON."},
                {"role": "user", "content": CLAIM_EXTRACTION_PROMPT.format(content=content)},
            ],
            temperature=0.1,
            max_tokens=1000,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or "[]"
        parsed = json.loads(raw)
        if isinstance(parsed, list):
            return parsed
        if isinstance(parsed, dict) and "claims" in parsed:
            return parsed["claims"]
        return []
    except Exception as e:
        logger.error("Claim extraction failed: %s", e)
        return [content]


def analyze_propaganda(content: str, language: str) -> dict:
    client = _get_client()
    lang_name = get_language_name(language)
    try:
        response = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {"role": "system", "content": "You are a media literacy expert. Always respond with valid JSON."},
                {"role": "user", "content": PROPAGANDA_ANALYSIS_PROMPT.format(content=content, language=lang_name)},
            ],
            temperature=0.2,
            max_tokens=800,
            response_format={"type": "json_object"},
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
        }
