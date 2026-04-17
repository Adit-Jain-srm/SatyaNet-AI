import json
import os

from fastapi import APIRouter

from app.config import settings
from app.models.schemas import BulkIngestRequest, IngestFactRequest, IngestMisinfoRequest, IngestSourceRequest
from app.qdrant.client import get_qdrant
from app.qdrant.ingest import ingest_facts, ingest_misinfo, ingest_sources

router = APIRouter(tags=["ingest"])


@router.post("/ingest")
async def bulk_ingest(request: BulkIngestRequest):
    client = get_qdrant()
    facts_count = ingest_facts(client, request.facts)
    misinfo_count = ingest_misinfo(client, request.misinfo_patterns)
    sources_count = ingest_sources(client, request.sources)
    return {
        "ingested": {
            "facts": facts_count,
            "misinfo_patterns": misinfo_count,
            "sources": sources_count,
        }
    }


@router.post("/ingest/seed")
async def seed_from_files():
    client = get_qdrant()
    base = settings.seed_data_path
    counts = {"facts": 0, "misinfo_patterns": 0, "sources": 0}

    facts_path = os.path.join(base, "seed_facts.json")
    if os.path.exists(facts_path):
        with open(facts_path, encoding="utf-8") as f:
            raw = json.load(f)
        facts = [IngestFactRequest(**item) for item in raw]
        counts["facts"] = ingest_facts(client, facts)

    misinfo_path = os.path.join(base, "misinfo_patterns.json")
    if os.path.exists(misinfo_path):
        with open(misinfo_path, encoding="utf-8") as f:
            raw = json.load(f)
        patterns = [IngestMisinfoRequest(**item) for item in raw]
        counts["misinfo_patterns"] = ingest_misinfo(client, patterns)

    sources_path = os.path.join(base, "source_credibility.json")
    if os.path.exists(sources_path):
        with open(sources_path, encoding="utf-8") as f:
            raw = json.load(f)
        sources = [IngestSourceRequest(**item) for item in raw]
        counts["sources"] = ingest_sources(client, sources)

    return {"seeded": counts}
