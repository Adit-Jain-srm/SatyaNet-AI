from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PayloadSchemaType,
    VectorParams,
)

from app.config import settings

COLLECTIONS = {
    "verified_facts": {
        "description": "Verified news articles, government data, trusted sources",
        "payload_indexes": {
            "language": PayloadSchemaType.KEYWORD,
            "category": PayloadSchemaType.KEYWORD,
            "source": PayloadSchemaType.KEYWORD,
        },
    },
    "misinfo_patterns": {
        "description": "Known debunked misinformation patterns",
        "payload_indexes": {
            "language": PayloadSchemaType.KEYWORD,
            "verdict": PayloadSchemaType.KEYWORD,
        },
    },
    "source_credibility": {
        "description": "Domain/source trust scores",
        "payload_indexes": {
            "category": PayloadSchemaType.KEYWORD,
        },
    },
}


def ensure_collections(client: QdrantClient) -> None:
    existing = {c.name for c in client.get_collections().collections}

    for name, meta in COLLECTIONS.items():
        if name not in existing:
            client.create_collection(
                collection_name=name,
                vectors_config=VectorParams(
                    size=settings.embedding_dim,
                    distance=Distance.COSINE,
                ),
            )

        for field_name, field_type in meta["payload_indexes"].items():
            try:
                client.create_payload_index(
                    collection_name=name,
                    field_name=field_name,
                    field_schema=field_type,
                )
            except Exception:
                pass
