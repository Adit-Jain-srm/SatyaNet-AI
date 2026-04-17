import logging

from langdetect import detect, DetectorFactory

from app.services.translator import detect_language_azure

logger = logging.getLogger(__name__)

DetectorFactory.seed = 0

SUPPORTED_LANGUAGES = {"en", "hi", "ta"}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
}


def detect_language(text: str) -> str:
    """Detect language using Azure Translator (primary) with langdetect fallback."""
    azure_result = detect_language_azure(text)
    if azure_result:
        return azure_result

    try:
        lang = detect(text)
        if lang in SUPPORTED_LANGUAGES:
            return lang
        return "en"
    except Exception:
        return "en"


def get_language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, "English")
