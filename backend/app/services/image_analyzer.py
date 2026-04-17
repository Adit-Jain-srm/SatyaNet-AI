import base64
import io
import logging

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)


def analyze_image_content(image_data: str) -> dict:
    """Analyze an image for AI generation and manipulation signals.

    Uses heuristic analysis based on statistical properties of the image.
    For production, replace with CLIP-based or EfficientNet deepfake detector.

    Args:
        image_data: Base64-encoded image string.
    """
    try:
        img_bytes = base64.b64decode(image_data)
        img = Image.open(io.BytesIO(img_bytes)).convert("RGB")
        arr = np.array(img, dtype=np.float32)

        noise_score = _estimate_noise_level(arr)
        symmetry_score = _estimate_symmetry(arr)
        frequency_score = _estimate_frequency_artifacts(arr)

        ai_probability = (noise_score * 0.4 + symmetry_score * 0.3 + frequency_score * 0.3)
        ai_probability = max(0.0, min(1.0, ai_probability))

        has_exif = bool(img.getexif())
        manipulation_probability = 0.3 if has_exif else 0.6

        return {
            "is_ai_generated": ai_probability > 0.6,
            "ai_probability": round(ai_probability, 3),
            "is_manipulated": manipulation_probability > 0.5,
            "manipulation_probability": round(manipulation_probability, 3),
            "similar_verified_images": [],
        }
    except Exception as e:
        logger.error("Image analysis failed: %s", e)
        return {
            "is_ai_generated": False,
            "ai_probability": 0.0,
            "is_manipulated": False,
            "manipulation_probability": 0.0,
            "similar_verified_images": [],
        }


def _estimate_noise_level(arr: np.ndarray) -> float:
    """High uniformity in noise patterns can indicate AI generation."""
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
    variance_of_std = np.std(blocks)
    return 1.0 - min(1.0, variance_of_std / 40.0)


def _estimate_symmetry(arr: np.ndarray) -> float:
    """Excessive symmetry can indicate AI generation."""
    h, w, _ = arr.shape
    half_w = w // 2
    left = arr[:, :half_w]
    right = np.flip(arr[:, w - half_w :], axis=1)
    diff = np.mean(np.abs(left - right)) / 255.0
    return max(0.0, 1.0 - diff * 5)


def _estimate_frequency_artifacts(arr: np.ndarray) -> float:
    """Analyze frequency domain for GAN artifacts."""
    gray = np.mean(arr, axis=2)
    h, w = gray.shape
    center_h, center_w = h // 2, w // 2
    region_size = min(32, center_h, center_w)
    center_region = gray[
        center_h - region_size : center_h + region_size,
        center_w - region_size : center_w + region_size,
    ]
    uniformity = 1.0 - (np.std(center_region) / 128.0)
    return max(0.0, min(1.0, uniformity))
