"""Fetch and extract readable text content from URLs."""

import logging
import re
from html.parser import HTMLParser

import httpx

logger = logging.getLogger(__name__)

MAX_FETCH_LENGTH = 500_000
TIMEOUT = 10.0


class _TextExtractor(HTMLParser):
    """Minimal HTML-to-text extractor that skips scripts, styles, and nav."""

    _SKIP_TAGS = frozenset({"script", "style", "nav", "footer", "header", "noscript", "svg", "iframe"})

    def __init__(self) -> None:
        super().__init__()
        self._pieces: list[str] = []
        self._skip_depth = 0

    def handle_starttag(self, tag: str, attrs: list) -> None:
        if tag in self._SKIP_TAGS:
            self._skip_depth += 1

    def handle_endtag(self, tag: str) -> None:
        if tag in self._SKIP_TAGS and self._skip_depth > 0:
            self._skip_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._skip_depth == 0:
            text = data.strip()
            if text:
                self._pieces.append(text)

    def get_text(self) -> str:
        return " ".join(self._pieces)


def fetch_url_content(url: str, max_length: int = 10_000) -> str:
    """Fetch a URL and extract its readable text content.

    Returns extracted text on success, or the original URL on failure.
    """
    if not url or not url.startswith(("http://", "https://")):
        return url

    try:
        resp = httpx.get(
            url,
            timeout=TIMEOUT,
            follow_redirects=True,
            headers={"User-Agent": "SatyaNet-AI/1.0 (Fact-Checking Bot)"},
        )
        resp.raise_for_status()
    except Exception as e:
        logger.warning("URL fetch failed for %s: %s", url[:100], e)
        return url

    content_type = resp.headers.get("content-type", "")
    raw = resp.text[:MAX_FETCH_LENGTH]

    if "html" in content_type:
        text = _extract_html_text(raw)
    else:
        text = raw

    text = _clean_whitespace(text)

    if len(text) < 20:
        return url

    return text[:max_length]


def _extract_html_text(html: str) -> str:
    parser = _TextExtractor()
    try:
        parser.feed(html)
        return parser.get_text()
    except Exception:
        return re.sub(r"<[^>]+>", " ", html)


def _clean_whitespace(text: str) -> str:
    text = re.sub(r"\s+", " ", text)
    return text.strip()
