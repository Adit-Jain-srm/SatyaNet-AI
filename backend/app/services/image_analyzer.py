"""Image analysis using GPT-4o Vision for AI detection, OCR, and content assessment.

Falls back to heuristic analysis if the Vision API is unavailable.
"""

import base64
import io
import json
import logging

import numpy as np
from openai import AzureOpenAI
from PIL import Image

from app.config import settings

logger = logging.getLogger(__name__)

_client: AzureOpenAI | None = None

VISION_PROMPT = """Analyze this image thoroughly as a fact-checking and misinformation detection expert.

Provide your analysis in the following JSON format:
{
  "description": "<brief description of what the image shows>",
  "is_ai_generated": <true/false — is this image likely AI-generated?>,
  "ai_confidence": <float 0-1 — how confident are you about the AI generation assessment>,
  "ai_generation_reasoning": "<why you think it is/isn't AI-generated>",
  "is_manipulated": <true/false — has the image been edited/doctored/photoshopped?>,
  "manipulation_confidence": <float 0-1>,
  "manipulation_reasoning": "<what manipulation signs you see, if any>",
  "extracted_text": "<any text visible in the image, transcribed verbatim>",
  "text_claims": ["<list of factual claims found in any text in the image>"],
  "content_concerns": ["<list of misinformation concerns about the image content>"],
  "is_real_photo": <true/false — does this appear to be a genuine photograph of a real scene/person?>,
  "context_flags": ["<any red flags: out-of-context use, misattribution, etc.>"]
}

Be precise. For a normal photograph of a real person, is_ai_generated should be false with high confidence. For AI art, deepfakes, or synthetic images, flag them. Read all visible text carefully."""


def _get_client() -> AzureOpenAI:
    global _client
    if _client is None:
        _client = AzureOpenAI(
            azure_endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_api_key,
            api_version=settings.azure_openai_api_version,
        )
    return _client


def analyze_image_content(image_data: str) -> dict:
    """Analyze image using GPT-4o Vision with heuristic fallback."""
    vision_result = _analyze_with_vision(image_data)
    if vision_result:
        heuristic = _heuristic_analysis(image_data)
        vision_result["heuristic_ai_score"] = heuristic.get("ai_probability", 0.0)
        vision_result["has_exif"] = heuristic.get("has_exif", False)
        return vision_result

    logger.info("Vision API unavailable, using heuristic fallback")
    return _heuristic_analysis(image_data)


def _analyze_with_vision(image_data: str) -> dict | None:
    """Use GPT-4o Vision to analyze the image."""
    if not settings.azure_openai_api_key:
        return None

    b64_prefix = image_data[:20]
    if b64_prefix.startswith("/9j/"):
        mime = "image/jpeg"
    elif b64_prefix.startswith("iVBOR"):
        mime = "image/png"
    else:
        mime = "image/jpeg"

    data_url = f"data:{mime};base64,{image_data}"

    try:
        client = _get_client()
        response = client.chat.completions.create(
            model=settings.azure_openai_deployment,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert image forensics analyst. Always respond with valid JSON.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": VISION_PROMPT},
                        {"type": "image_url", "image_url": {"url": data_url, "detail": "high"}},
                    ],
                },
            ],
            temperature=0.1,
            max_tokens=1500,
            response_format={"type": "json_object"},
        )

        raw = response.choices[0].message.content or "{}"
        parsed = json.loads(raw)

        ai_gen = parsed.get("is_ai_generated", False)
        ai_conf = float(parsed.get("ai_confidence", 0.5))
        manip = parsed.get("is_manipulated", False)
        manip_conf = float(parsed.get("manipulation_confidence", 0.3))

        return {
            "is_ai_generated": ai_gen,
            "ai_probability": round(ai_conf if ai_gen else 1.0 - ai_conf, 3),
            "is_manipulated": manip,
            "manipulation_probability": round(manip_conf if manip else 1.0 - manip_conf, 3),
            "similar_verified_images": [],
            "description": parsed.get("description", ""),
            "ai_reasoning": parsed.get("ai_generation_reasoning", ""),
            "manipulation_reasoning": parsed.get("manipulation_reasoning", ""),
            "extracted_text": parsed.get("extracted_text", ""),
            "text_claims": parsed.get("text_claims", []),
            "content_concerns": parsed.get("content_concerns", []),
            "is_real_photo": parsed.get("is_real_photo", True),
            "context_flags": parsed.get("context_flags", []),
            "analysis_method": "gpt4o_vision",
        }
    except Exception as e:
        logger.warning("GPT-4o Vision analysis failed: %s", e)
        return None


def _heuristic_analysis(image_data: str) -> dict:
    """Fallback heuristic analysis using pixel statistics."""
    try:
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        arr = np.array(img, dtype=np.float32)

        noise_score = _estimate_noise_level(arr)
        symmetry_score = _estimate_symmetry(arr)
        frequency_score = _estimate_frequency_artifacts(arr)

        ai_probability = noise_score * 0.4 + symmetry_score * 0.3 + frequency_score * 0.3
        ai_probability = max(0.0, min(1.0, ai_probability))

        has_exif = bool(img.getexif())
        manipulation_probability = 0.2 if has_exif else 0.5

        return {
            "is_ai_generated": ai_probability > 0.7,
            "ai_probability": round(ai_probability, 3),
            "is_manipulated": manipulation_probability > 0.4,
            "manipulation_probability": round(manipulation_probability, 3),
            "similar_verified_images": [],
            "description": "",
            "ai_reasoning": "Heuristic pixel-level analysis (Vision API unavailable)",
            "manipulation_reasoning": "EXIF present" if has_exif else "No EXIF metadata found",
            "extracted_text": "",
            "text_claims": [],
            "content_concerns": [],
            "is_real_photo": has_exif,
            "context_flags": [],
            "analysis_method": "heuristic",
            "has_exif": has_exif,
            "heuristic_ai_score": round(ai_probability, 3),
        }
    except Exception as e:
        logger.error("Heuristic image analysis failed: %s", e)
        return {
            "is_ai_generated": False,
            "ai_probability": 0.0,
            "is_manipulated": False,
            "manipulation_probability": 0.0,
            "similar_verified_images": [],
            "description": "",
            "ai_reasoning": "Analysis failed",
            "manipulation_reasoning": "",
            "extracted_text": "",
            "text_claims": [],
            "content_concerns": [],
            "is_real_photo": True,
            "context_flags": [],
            "analysis_method": "failed",
        }


def _estimate_noise_level(arr: np.ndarray) -> float:
    h, w, _ = arr.shape
    if h < 4 or w < 4:
        return 0.5
    block_size = min(64, h // 2, w // 2)
    blocks = []
    for i in range(0, h - block_size, block_size):
        for j in range(0, w - block_size, block_size):
            block = arr[i : i + block_size, j : j + block_size]
            blocks.append(np.std(block))
    if not blocks:
        return 0.5
    return 1.0 - min(1.0, float(np.std(blocks)) / 40.0)


def _estimate_symmetry(arr: np.ndarray) -> float:
    h, w, _ = arr.shape
    half_w = w // 2
    left = arr[:, :half_w]
    right = np.flip(arr[:, w - half_w :], axis=1)
    diff = np.mean(np.abs(left - right)) / 255.0
    return max(0.0, 1.0 - diff * 5)


def _estimate_frequency_artifacts(arr: np.ndarray) -> float:
    gray = np.mean(arr, axis=2)
    h, w = gray.shape
    center_h, center_w = h // 2, w // 2
    region_size = min(32, center_h, center_w)
    center_region = gray[
        center_h - region_size : center_h + region_size,
        center_w - region_size : center_w + region_size,
    ]
    return max(0.0, min(1.0, 1.0 - float(np.std(center_region)) / 128.0))
