from fastapi import APIRouter

from app.models.schemas import HealthResponse
from app.qdrant.client import get_qdrant

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    client = get_qdrant()
    try:
        collections_response = client.get_collections()
        collection_names = [c.name for c in collections_response.collections]
        return HealthResponse(
            status="healthy",
            qdrant_connected=True,
            collections=collection_names,
        )
    except Exception:
        return HealthResponse(
            status="degraded",
            qdrant_connected=False,
            collections=[],
        )
