"""Azure Translator service with availability caching and robust fallback."""

import logging
import time

import httpx

from app.config import settings
from app.services.retry_utils import retry_call

logger = logging.getLogger(__name__)

API_VERSION = "3.0"

_available: bool | None = None
_available_checked_at: float = 0.0
_CACHE_TTL = 300.0


def _base_url() -> str:
    return settings.azure_translator_endpoint.rstrip("/")


def _headers() -> dict[str, str]:
    return {
        "Ocp-Apim-Subscription-Key": settings.azure_translator_key,
        "Ocp-Apim-Subscription-Region": settings.azure_translator_region,
        "Content-Type": "application/json",
    }


def is_translator_available() -> bool:
    """Check if Azure Translator is reachable, cached for 5 minutes."""
    global _available, _available_checked_at

    if not settings.azure_translator_key:
        return False

    now = time.monotonic()
    if _available is not None and (now - _available_checked_at) < _CACHE_TTL:
        return _available

    try:
        resp = httpx.post(
            f"{_base_url()}/detect",
            params={"api-version": API_VERSION},
            headers=_headers(),
            json=[{"text": "hello"}],
            timeout=settings.external_http_timeout_seconds,
        )
        _available = resp.status_code == 200
    except Exception:
        _available = False

    _available_checked_at = now
    return _available


def detect_language_azure(text: str) -> tuple[str | None, str]:
    """Detect language using Azure Translator REST API.

    Returns (language_code, method) where method is 'azure' or failure mode.
    language_code is None only if detection fails.
    """
    if not is_translator_available():
        return None, "azure_unavailable"

    try:
        resp = retry_call(
            lambda: httpx.post(
                f"{_base_url()}/detect",
                params={"api-version": API_VERSION},
                headers=_headers(),
                json=[{"text": text[:500]}],
                timeout=settings.external_http_timeout_seconds,
            ),
            attempts=settings.external_http_retries,
        )
        resp.raise_for_status()
        data = resp.json()
        if data and data[0].get("language"):
            lang = data[0]["language"]
            return lang, "azure"
        return None, "azure_empty"
    except Exception as e:
        logger.warning("Azure language detection failed: %s", e)
        return None, "azure_error"


def translate_text(text: str, from_lang: str, to_lang: str) -> str:
    """Translate text using Azure Translator. Returns original text on failure."""
    if from_lang == to_lang:
        return text

    if not is_translator_available():
        return text

    try:
        resp = retry_call(
            lambda: httpx.post(
                f"{_base_url()}/translate",
                params={
                    "api-version": API_VERSION,
                    "from": from_lang,
                    "to": to_lang,
                },
                headers=_headers(),
                json=[{"text": text[:5000]}],
                timeout=settings.external_http_timeout_seconds,
            ),
            attempts=settings.external_http_retries,
        )
        resp.raise_for_status()
        data = resp.json()
        if data and data[0].get("translations"):
            return data[0]["translations"][0]["text"]
        return text
    except Exception as e:
        logger.warning("Azure translation failed: %s", e)
        return text
