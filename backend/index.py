"""Vercel entry — ASGI app with optional service path stripping for Vercel Services."""

from collections.abc import Awaitable, Callable

from app.main import app as core_app

# Public routePrefix from vercel.json and Vercel's internal service path (see X-Matched-Path).
# Longest prefix first so paths are unambiguous.
_SERVICE_PREFIXES: tuple[str, ...] = ("/_svc/backend", "/_/backend")


class _StripServicePrefixMiddleware:
    """Strip Vercel Services path prefix so FastAPI routes stay at /health, /analyze, etc."""

    def __init__(
        self,
        app: Callable[..., Awaitable[None]],
        prefixes: tuple[str, ...],
    ) -> None:
        self.app = app
        self.prefixes = tuple(sorted(prefixes, key=len, reverse=True))

    async def __call__(
        self,
        scope: dict,
        receive: Callable[[], Awaitable[dict]],
        send: Callable[[dict], Awaitable[None]],
    ) -> None:
        if scope["type"] == "http":
            path = scope.get("path") or ""
            for prefix in self.prefixes:
                if path == prefix or path.startswith(prefix + "/"):
                    new_path = path[len(prefix) :] or "/"
                    scope = {**scope, "path": new_path}
                    break
        await self.app(scope, receive, send)


app = _StripServicePrefixMiddleware(core_app, _SERVICE_PREFIXES)

__all__ = ["app"]
