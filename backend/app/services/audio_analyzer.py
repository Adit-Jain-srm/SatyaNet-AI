"""Audio analysis for deepfake voice detection and speaker verification.

Uses spectrogram-based heuristic analysis. For production, replace with
Wav2Vec2 or speaker embedding models.
"""
import base64
import io
import logging
import struct
import wave

import numpy as np

logger = logging.getLogger(__name__)


def analyze_audio_content(audio_data: str) -> dict:
    """Analyze audio for voice cloning and manipulation signals.

    Args:
        audio_data: Base64-encoded audio file (WAV preferred).
    """
    try:
        audio_bytes = base64.b64decode(audio_data)
        samples, sample_rate = _decode_audio(audio_bytes)

        if samples is None:
            return _default_result()

        spectral_score = _spectral_flatness(samples)
        consistency_score = _temporal_consistency(samples, sample_rate)
        silence_ratio = _silence_ratio(samples)

        clone_probability = (
            spectral_score * 0.4
            + (1 - consistency_score) * 0.35
            + (1 - silence_ratio) * 0.25
        )
        clone_probability = max(0.0, min(1.0, clone_probability))

        return {
            "is_voice_clone": clone_probability > 0.6,
            "clone_probability": round(clone_probability, 3),
            "spectral_anomaly_score": round(spectral_score, 3),
            "temporal_consistency": round(consistency_score, 3),
            "duration_seconds": round(len(samples) / max(sample_rate, 1), 1),
        }
    except Exception as e:
        logger.error("Audio analysis failed: %s", e)
        return _default_result()


def _decode_audio(audio_bytes: bytes) -> tuple:
    """Attempt to decode audio bytes as WAV."""
    try:
        buf = io.BytesIO(audio_bytes)
        with wave.open(buf, "rb") as wf:
            n_channels = wf.getnchannels()
            sampwidth = wf.getsampwidth()
            framerate = wf.getframerate()
            n_frames = wf.getnframes()
            raw = wf.readframes(n_frames)

        if sampwidth == 2:
            fmt = f"<{n_frames * n_channels}h"
            samples = np.array(struct.unpack(fmt, raw), dtype=np.float32)
        elif sampwidth == 1:
            samples = np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128
        else:
            return None, 0

        if n_channels > 1:
            samples = samples[::n_channels]

        return samples, framerate
    except Exception:
        return None, 0


def _spectral_flatness(samples: np.ndarray) -> float:
    """High spectral flatness in speech segments can indicate synthesis."""
    if len(samples) < 512:
        return 0.5

    windowed = samples[:len(samples) - len(samples) % 512].reshape(-1, 512)
    spectra = np.abs(np.fft.rfft(windowed, axis=1))
    spectra = np.maximum(spectra, 1e-10)

    geo_mean = np.exp(np.mean(np.log(spectra), axis=1))
    arith_mean = np.mean(spectra, axis=1)
    flatness = geo_mean / np.maximum(arith_mean, 1e-10)

    avg_flatness = float(np.mean(flatness))
    return min(1.0, avg_flatness * 2)


def _temporal_consistency(samples: np.ndarray, sample_rate: int) -> float:
    """Natural speech has varied energy across segments; synthetic is more uniform."""
    if len(samples) < sample_rate:
        return 0.5

    segment_len = sample_rate // 4
    n_segments = len(samples) // segment_len
    if n_segments < 2:
        return 0.5

    energies = []
    for i in range(n_segments):
        segment = samples[i * segment_len : (i + 1) * segment_len]
        energies.append(float(np.sqrt(np.mean(segment ** 2))))

    if not energies or max(energies) == 0:
        return 0.5

    energies = np.array(energies)
    normalized = energies / np.max(energies)
    variation = float(np.std(normalized))

    return min(1.0, variation * 3)


def _silence_ratio(samples: np.ndarray) -> float:
    """Natural audio has silence gaps; synthetic often doesn't."""
    if len(samples) == 0:
        return 0.5
    threshold = np.max(np.abs(samples)) * 0.02
    silent_count = np.sum(np.abs(samples) < threshold)
    return float(silent_count / len(samples))


def _default_result() -> dict:
    return {
        "is_voice_clone": False,
        "clone_probability": 0.0,
        "spectral_anomaly_score": 0.0,
        "temporal_consistency": 0.5,
        "duration_seconds": 0.0,
    }
