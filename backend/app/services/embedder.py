from functools import lru_cache

from fastembed import TextEmbedding

from app.config import settings

_model: TextEmbedding | None = None


def _get_model() -> TextEmbedding:
    global _model
    if _model is None:
        _model = TextEmbedding(model_name=settings.embedding_model)
    return _model


def get_embeddings(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    embeddings = list(model.embed(texts))
    return [e.tolist() for e in embeddings]


def get_embedding(text: str) -> list[float]:
    return get_embeddings([text])[0]
