"""Language detection with Azure Translator primary and langdetect fallback."""

from langdetect import detect, DetectorFactory

from app.services.translator import detect_language_azure

DetectorFactory.seed = 0

SUPPORTED_LANGUAGES = {"en", "hi", "ta"}

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
}


def detect_language_with_method(text: str) -> tuple[str, str]:
    """Detect language and return (code, method).

    Method is one of: 'azure', 'langdetect', 'default'.
    """
    azure_result, azure_status = detect_language_azure(text)
    if azure_result:
        return azure_result, "azure"

    try:
        lang = detect(text)
        if lang in SUPPORTED_LANGUAGES:
            return lang, "langdetect"
        return "en", "langdetect_fallback"
    except Exception:
        return "en", "default"


def detect_language(text: str) -> str:
    code, _ = detect_language_with_method(text)
    return code


def get_language_name(code: str) -> str:
    return LANGUAGE_NAMES.get(code, "English")
