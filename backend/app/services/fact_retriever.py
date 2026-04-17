"""Qdrant-powered fact retrieval with payload filtering across all 3 collections."""

import logging

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.config import settings
from app.services.embedder import get_embedding
from app.services.retry_utils import retry_call

logger = logging.getLogger(__name__)


def retrieve_evidence(
    client: QdrantClient,
    claim: str,
    language: str,
    top_k: int = 5,
    score_threshold: float = 0.25,
) -> list[dict]:
    """Search verified_facts with language filter and score threshold."""
    try:
        vector = get_embedding(claim)
        results = retry_call(
            lambda: client.query_points(
                collection_name="verified_facts",
                query=vector,
                query_filter=Filter(
                    should=[
                        FieldCondition(key="language", match=MatchValue(value=language)),
                        FieldCondition(key="language", match=MatchValue(value="en")),
                    ]
                ),
                with_payload=True,
                limit=top_k,
                score_threshold=score_threshold,
            ).points,
            attempts=settings.qdrant_retries,
        )
    except Exception as e:
        logger.error("Evidence retrieval failed: %s", e)
        return []

    evidence = []
    for point in results:
        payload = point.payload or {}
        evidence.append({
            "text": payload.get("text", ""),
            "source": payload.get("source", ""),
            "url": payload.get("url", ""),
            "credibility_score": payload.get("credibility_score", 0.5),
            "relevance_score": point.score,
            "collection": "verified_facts",
            "category": payload.get("category", ""),
        })
    return evidence


def find_matching_misinfo(
    client: QdrantClient,
    claim: str,
    language: str,
    threshold: float = 0.75,
    top_k: int = 3,
) -> list[dict]:
    """Search misinfo_patterns with language filter."""
    try:
        vector = get_embedding(claim)
        results = retry_call(
            lambda: client.query_points(
                collection_name="misinfo_patterns",
                query=vector,
                query_filter=Filter(
                    should=[
                        FieldCondition(key="language", match=MatchValue(value=language)),
                        FieldCondition(key="language", match=MatchValue(value="en")),
                    ]
                ),
                with_payload=True,
                limit=top_k,
            ).points,
            attempts=settings.qdrant_retries,
        )
    except Exception as e:
        logger.error("Misinfo pattern search failed: %s", e)
        return []

    matches = []
    for point in results:
        if point.score >= threshold:
            payload = point.payload or {}
            matches.append({
                "original_claim": payload.get("original_claim", ""),
                "debunk_summary": payload.get("debunk_summary", ""),
                "verdict": payload.get("verdict", "unverified"),
                "similarity": point.score,
                "spread_count": payload.get("spread_count", 0),
                "collection": "misinfo_patterns",
            })
    return matches


def get_source_credibility(
    client: QdrantClient,
    source_text: str,
    top_k: int = 3,
) -> tuple[float, list[dict]]:
    """Search source_credibility and return (weighted_score, matched_sources)."""
    try:
        vector = get_embedding(source_text)
        results = retry_call(
            lambda: client.query_points(
                collection_name="source_credibility",
                query=vector,
                with_payload=True,
                limit=top_k,
                score_threshold=0.3,
            ).points,
            attempts=settings.qdrant_retries,
        )
    except Exception as e:
        logger.error("Source credibility lookup failed: %s", e)
        return 0.5, []

    if not results:
        return 0.5, []

    total_score = 0.0
    total_weight = 0.0
    matched_sources = []
    for point in results:
        payload = point.payload or {}
        trust = payload.get("trust_score", 0.5)
        weight = point.score
        total_score += trust * weight
        total_weight += weight
        matched_sources.append({
            "domain": payload.get("domain", ""),
            "trust_score": trust,
            "similarity": point.score,
            "category": payload.get("category", ""),
            "collection": "source_credibility",
        })

    score = total_score / total_weight if total_weight > 0 else 0.5
    return score, matched_sources
