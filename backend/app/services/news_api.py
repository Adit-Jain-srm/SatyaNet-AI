"""Fetch relevant news articles from News API to corroborate or contradict claims."""
import logging

import httpx

from app.config import settings
from app.services.retry_utils import retry_call

logger = logging.getLogger(__name__)

NEWS_API_URL = "https://newsapi.org/v2/everything"


def search_news(query: str, language: str = "en", max_results: int = 5) -> list[dict]:
    """Search News API for articles relevant to a claim.

    Returns list of dicts with: title, source, url, description, published_at
    Gracefully returns empty list on any failure.
    """
    if not settings.news_api_key:
        return []

    cleaned = query.strip()[:200]
    if not cleaned:
        return []

    lang_map = {"en": "en", "hi": "hi", "ta": "ta"}

    try:
        resp = retry_call(
            lambda: httpx.get(
                NEWS_API_URL,
                params={
                    "q": cleaned,
                    "apiKey": settings.news_api_key,
                    "pageSize": max_results,
                    "sortBy": "relevancy",
                    "language": lang_map.get(language, "en"),
                },
                timeout=settings.external_http_timeout_seconds,
            ),
            attempts=settings.external_http_retries,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        logger.warning("News API failed: %s", e)
        return []

    if data.get("status") != "ok":
        return []

    results = []
    for article in data.get("articles", [])[:max_results]:
        results.append({
            "title": article.get("title", ""),
            "source": article.get("source", {}).get("name", "Unknown"),
            "url": article.get("url", ""),
            "description": article.get("description", "") or "",
            "published_at": article.get("publishedAt", ""),
        })

    return results
