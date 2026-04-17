"""Language detection with Azure Translator primary and langdetect fallback."""

from langdetect import detect, DetectorFactory

from app.services.translator import detect_language_azure

DetectorFactory.seed = 0

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "ta": "Tamil",
    "te": "Telugu",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "ur": "Urdu",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "it": "Italian",
    "pt": "Portuguese",
    "ru": "Russian",
    "uk": "Ukrainian",
    "tr": "Turkish",
    "ar": "Arabic",
    "fa": "Persian",
    "he": "Hebrew",
    "zh": "Chinese",
    "ja": "Japanese",
    "ko": "Korean",
    "th": "Thai",
    "vi": "Vietnamese",
    "id": "Indonesian",
    "ms": "Malay",
    "sw": "Swahili",
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
        if not lang:
            return "en", "langdetect_empty"
        return lang, "langdetect"
    except Exception:
        return "en", "default"


def detect_language(text: str) -> str:
    code, _ = detect_language_with_method(text)
    return code


def get_language_name(code: str) -> str:
    if code in LANGUAGE_NAMES:
        return LANGUAGE_NAMES[code]
    # Best effort for unknown language codes so prompts stay in detected language.
    return f"language '{code}'"
