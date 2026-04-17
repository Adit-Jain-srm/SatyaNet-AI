import re

from app.models.schemas import CredibilityBreakdown


WEIGHTS = {
    "ai_generation": 0.10,
    "fact_evidence": 0.25,
    "source_credibility": 0.15,
    "misinfo_pattern": 0.15,
    "emotional_language": 0.10,
    "google_factcheck": 0.25,
}

_FALSE_PATTERNS = re.compile(
    r"\b(?:"
    r"false|fake|incorrect|wrong|pants on fire|misleading|mostly false"
    r"|not true|fabricated|unproven|debunked|untrue|baseless|unfounded"
    r"|half true|mixture"
    r")\b",
    re.IGNORECASE,
)

_TRUE_PATTERNS = re.compile(
    r"\b(?:"
    r"true|correct|accurate|mostly true|verified"
    r")\b",
    re.IGNORECASE,
)


def compute_credibility(
    ai_generation_score: float,
    fact_evidence_score: float,
    source_credibility_score: float,
    misinfo_pattern_score: float,
    emotional_language_score: float,
    google_factcheck_score: float = 0.5,
) -> tuple[float, CredibilityBreakdown]:
    breakdown = CredibilityBreakdown(
        ai_generation_score=_clamp(ai_generation_score),
        fact_evidence_score=_clamp(fact_evidence_score),
        source_credibility_score=_clamp(source_credibility_score),
        misinfo_pattern_score=_clamp(misinfo_pattern_score),
        emotional_language_score=_clamp(emotional_language_score),
        google_factcheck_score=_clamp(google_factcheck_score),
    )

    credibility = (
        (1 - breakdown.ai_generation_score) * WEIGHTS["ai_generation"]
        + breakdown.fact_evidence_score * WEIGHTS["fact_evidence"]
        + breakdown.source_credibility_score * WEIGHTS["source_credibility"]
        + (1 - breakdown.misinfo_pattern_score) * WEIGHTS["misinfo_pattern"]
        + (1 - breakdown.emotional_language_score) * WEIGHTS["emotional_language"]
        + breakdown.google_factcheck_score * WEIGHTS["google_factcheck"]
    )

    credibility = _clamp(credibility)
    return credibility, breakdown


def score_to_verdict(score: float) -> str:
    if score >= 0.75:
        return "true"
    if score >= 0.5:
        return "unverified"
    if score >= 0.25:
        return "misleading"
    return "false"


def google_reviews_to_score(reviews: list[dict]) -> float:
    """Convert Google Fact Check reviews into a 0-1 credibility score.

    0.0 = all reviews say false, 1.0 = all reviews say true, 0.5 = no data.
    Uses word-boundary regex to avoid substring false-matches.
    """
    if not reviews:
        return 0.5

    scores: list[float] = []
    for r in reviews:
        rating = r.get("rating", "").strip()
        if _FALSE_PATTERNS.search(rating):
            scores.append(0.0)
        elif _TRUE_PATTERNS.search(rating):
            scores.append(1.0)
        else:
            scores.append(0.4)

    return sum(scores) / len(scores) if scores else 0.5


def _clamp(v: float) -> float:
    return max(0.0, min(1.0, v))
