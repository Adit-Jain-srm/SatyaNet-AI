import uuid

from qdrant_client import QdrantClient
from qdrant_client.models import PointStruct

from app.models.schemas import IngestFactRequest, IngestMisinfoRequest, IngestSourceRequest
from app.services.embedder import get_embeddings


def ingest_facts(client: QdrantClient, facts: list[IngestFactRequest]) -> int:
    if not facts:
        return 0

    texts = [f.text for f in facts]
    vectors = get_embeddings(texts)

    points = []
    for fact, vector in zip(facts, vectors):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "text": fact.text,
                    "source": fact.source,
                    "url": fact.url,
                    "language": fact.language,
                    "category": fact.category,
                    "credibility_score": fact.credibility_score,
                },
            )
        )

    client.upsert(collection_name="verified_facts", points=points, wait=True)
    return len(points)


def ingest_misinfo(client: QdrantClient, patterns: list[IngestMisinfoRequest]) -> int:
    if not patterns:
        return 0

    texts = [p.original_claim for p in patterns]
    vectors = get_embeddings(texts)

    points = []
    for pattern, vector in zip(patterns, vectors):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "original_claim": pattern.original_claim,
                    "debunk_summary": pattern.debunk_summary,
                    "verdict": pattern.verdict.value,
                    "language": pattern.language,
                    "spread_count": pattern.spread_count,
                },
            )
        )

    client.upsert(collection_name="misinfo_patterns", points=points, wait=True)
    return len(points)


def ingest_sources(client: QdrantClient, sources: list[IngestSourceRequest]) -> int:
    if not sources:
        return 0

    texts = [s.domain for s in sources]
    vectors = get_embeddings(texts)

    points = []
    for source, vector in zip(sources, vectors):
        points.append(
            PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={
                    "domain": source.domain,
                    "trust_score": source.trust_score,
                    "category": source.category,
                },
            )
        )

    client.upsert(collection_name="source_credibility", points=points, wait=True)
    return len(points)
