"""URL validation and normalization helpers."""

from __future__ import annotations

from urllib.parse import urlparse


def is_valid_http_url(url: str) -> bool:
    """Return True when ``url`` has an http(s) scheme and a non-empty host."""
    try:
        parsed = urlparse(url.strip())
    except ValueError:
        return False
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def normalize_url_for_dedup(url: str) -> str:
    """Normalize a URL for seed deduplication (scheme, host, path; no query/fragment)."""
    parsed = urlparse(url.strip())
    scheme = (parsed.scheme or "http").lower()
    host = (parsed.hostname or "").lower()
    port = parsed.port
    if port and (
        (scheme == "http" and port == 80)
        or (scheme == "https" and port == 443)
    ):
        port = None
    netloc = host if port is None else f"{host}:{port}"
    path = parsed.path.rstrip("/") or ""
    return f"{scheme}://{netloc}{path}"
