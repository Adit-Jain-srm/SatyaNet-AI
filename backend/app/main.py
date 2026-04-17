from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.qdrant.client import get_qdrant
from app.qdrant.collections import ensure_collections
from app.routers import analyze, health, ingest


@asynccontextmanager
async def lifespan(app: FastAPI):
    client = get_qdrant()
    ensure_collections(client)
    yield


app = FastAPI(
    title="SatyaNet-AI",
    description="AI-powered misinformation detection and counter-response system",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router)
app.include_router(analyze.router)
app.include_router(ingest.router)
