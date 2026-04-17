import logging

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

SUPPORTED_LANGS = {"en", "hi", "ta"}

DETECT_URL = "https://api.cognitive.microsofttranslator.com/detect"
TRANSLATE_URL = "https://api.cognitive.microsofttranslator.com/translate"
API_VERSION = "3.0"


def _headers() -> dict[str, str]:
    return {
        "Ocp-Apim-Subscription-Key": settings.azure_translator_key,
        "Ocp-Apim-Subscription-Region": settings.azure_translator_region,
        "Content-Type": "application/json",
    }


def detect_language_azure(text: str) -> str | None:
    """Detect language using Azure Translator REST API. Returns ISO code or None."""
    if not settings.azure_translator_key:
        return None
    try:
        resp = httpx.post(
            DETECT_URL,
            params={"api-version": API_VERSION},
            headers=_headers(),
            json=[{"text": text[:500]}],
            timeout=5.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if data and data[0].get("language"):
            lang = data[0]["language"]
            return lang if lang in SUPPORTED_LANGS else None
        return None
    except Exception as e:
        logger.warning("Azure language detection failed: %s", e)
        return None


def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """Translate text between supported languages using Azure Translator REST API."""
    if from_lang == to_lang or not settings.azure_translator_key:
        return text
    try:
        resp = httpx.post(
            TRANSLATE_URL,
            params={
                "api-version": API_VERSION,
                "from": from_lang,
                "to": to_lang,
            },
            headers=_headers(),
            json=[{"text": text}],
            timeout=10.0,
        )
        resp.raise_for_status()
        data = resp.json()
        if data and data[0].get("translations"):
            return data[0]["translations"][0]["text"]
        return text
    except Exception as e:
        logger.warning("Azure translation failed: %s", e)
        return text
