import logging
import re

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

FACTCHECK_URL = "https://factchecktools.googleapis.com/v1alpha1/claims:search"
MAX_RESULTS = 5

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


def search_claims(query: str, language: str = "en") -> list[dict]:
    """Search Google Fact Check Tools API for existing fact-checks on a claim.

    Returns a list of fact-check review dicts with publisher, rating, url, and claim text.
    Gracefully returns empty list on any failure.
    """
    if not settings.google_factcheck_api_key:
        return []

    cleaned = query.strip()[:500]
    if not cleaned:
        return []

    lang_map = {"en": "en", "hi": "hi", "ta": "ta"}
    lang_code = lang_map.get(language, "en")

    try:
        resp = httpx.get(
            FACTCHECK_URL,
            params={
                "query": cleaned,
                "key": settings.google_factcheck_api_key,
                "languageCode": lang_code,
                "pageSize": MAX_RESULTS,
            },
            timeout=8.0,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning("Google Fact Check API failed: %s", e)
        return []

    results: list[dict] = []
    for claim_obj in data.get("claims", []):
        claim_text = claim_obj.get("text", "")
        claimant = claim_obj.get("claimant", "")

        for review in claim_obj.get("claimReview", []):
            publisher = review.get("publisher", {})
            results.append({
                "claim_text": claim_text,
                "claimant": claimant,
                "publisher_name": publisher.get("name", "Unknown"),
                "publisher_site": publisher.get("site", ""),
                "rating": review.get("textualRating", ""),
                "url": review.get("url", ""),
                "title": review.get("title", ""),
                "review_date": review.get("reviewDate", ""),
                "language": review.get("languageCode", lang_code),
            })

    return results[:MAX_RESULTS]


def get_factcheck_verdict(reviews: list[dict]) -> str | None:
    """Derive a consensus verdict from multiple fact-check reviews.

    Uses word-boundary regex to avoid substring false-matches
    (e.g. 'untrue' won't match 'true', 'unknown' won't match 'no').
    Returns 'false', 'misleading', 'true', or None if no reviews.
    """
    if not reviews:
        return None

    false_count = 0
    true_count = 0

    for r in reviews:
        rating = r.get("rating", "").strip()
        if _FALSE_PATTERNS.search(rating):
            false_count += 1
        elif _TRUE_PATTERNS.search(rating):
            true_count += 1

    if false_count > true_count:
        return "false"
    if true_count > false_count:
        return "true"
    if false_count > 0:
        return "misleading"
    return None
