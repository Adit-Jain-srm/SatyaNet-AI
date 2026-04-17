from qdrant_client import QdrantClient

from app.config import settings

_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        kwargs: dict = {
            "url": settings.qdrant_url,
            "timeout": settings.qdrant_timeout_seconds,
        }
        if settings.qdrant_api_key:
            kwargs["api_key"] = settings.qdrant_api_key
        _client = QdrantClient(**kwargs)
    return _client
