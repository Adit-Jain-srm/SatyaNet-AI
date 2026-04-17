import logging

from qdrant_client import QdrantClient
from qdrant_client.models import FieldCondition, Filter, MatchValue

from app.services.embedder import get_embedding

logger = logging.getLogger(__name__)


def retrieve_evidence(
    client: QdrantClient,
    claim: str,
    language: str,
    top_k: int = 5,
) -> list[dict]:
    try:
        vector = get_embedding(claim)
        results = client.query_points(
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
        ).points
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
        })
    return evidence


def find_matching_misinfo(
    client: QdrantClient,
    claim: str,
    language: str,
    threshold: float = 0.75,
    top_k: int = 3,
) -> list[dict]:
    try:
        vector = get_embedding(claim)
        results = client.query_points(
            collection_name="misinfo_patterns",
            query=vector,
            with_payload=True,
            limit=top_k,
        ).points
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
            })
    return matches


def get_source_credibility(
    client: QdrantClient,
    source_text: str,
    top_k: int = 3,
) -> float:
    try:
        vector = get_embedding(source_text)
        results = client.query_points(
            collection_name="source_credibility",
            query=vector,
            with_payload=True,
            limit=top_k,
        ).points
    except Exception as e:
        logger.error("Source credibility lookup failed: %s", e)
        return 0.5

    if not results:
        return 0.5

    total_score = 0.0
    total_weight = 0.0
    for point in results:
        payload = point.payload or {}
        trust = payload.get("trust_score", 0.5)
        weight = point.score
        total_score += trust * weight
        total_weight += weight

    return total_score / total_weight if total_weight > 0 else 0.5
