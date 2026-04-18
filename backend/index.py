"""Vercel entry — exposes the FastAPI ASGI app (optionally mounted under a route prefix)."""

import os

from fastapi import FastAPI

from app.main import app as core_app


def _build_app() -> FastAPI:
    """When using Vercel Services, set BACKEND_ROUTE_PREFIX to match backend.routePrefix (e.g. /_/backend)."""
    prefix = (os.environ.get("BACKEND_ROUTE_PREFIX") or "").strip().rstrip("/")
    if not prefix:
        return core_app
    outer = FastAPI()
    outer.mount(prefix, core_app)
    return outer


app = _build_app()

__all__ = ["app"]
