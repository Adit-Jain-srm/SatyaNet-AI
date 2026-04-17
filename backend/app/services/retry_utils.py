"""Shared retry helpers for transient network operations."""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import TypeVar

import httpx

T = TypeVar("T")


def is_transient_error(exc: Exception) -> bool:
    """Return True for retryable timeout/network errors."""
    transient_types = (
        TimeoutError,
        httpx.TimeoutException,
        httpx.ConnectError,
        httpx.ReadError,
        httpx.RemoteProtocolError,
        httpx.NetworkError,
    )
    message = str(exc).lower()
    return isinstance(exc, transient_types) or "timed out" in message or "timeout" in message


def retry_call(
    fn: Callable[[], T],
    *,
    attempts: int,
    initial_backoff_seconds: float = 0.4,
) -> T:
    """Execute a callable with bounded retries for transient failures."""
    last_error: Exception | None = None
    backoff = max(0.0, initial_backoff_seconds)

    for attempt in range(1, max(1, attempts) + 1):
        try:
            return fn()
        except Exception as exc:  # noqa: BLE001
            last_error = exc
            if attempt >= attempts or not is_transient_error(exc):
                raise
            if backoff > 0:
                time.sleep(backoff)
                backoff *= 2

    assert last_error is not None
    raise last_error
