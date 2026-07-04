"""Sitemap URL parser with sitemap index support."""

from __future__ import annotations

import xml.etree.ElementTree as ET
from collections.abc import Callable

import httpx

from src.constants import MAX_SITEMAP_RESPONSE_BYTES, MAX_SITEMAP_URLS

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
DEFAULT_MAX_DEPTH = 2
WarnFn = Callable[..., None]


def _local_tag(element: ET.Element) -> str:
    tag = element.tag
    if "}" in tag:
        return tag.split("}", 1)[1]
    return tag


def _iter_locs(root: ET.Element, child_tag: str) -> list[str]:
    urls: list[str] = []
    for element in root:
        if _local_tag(element) != child_tag:
            continue
        for loc in element.iter(f"{{{SITEMAP_NS}}}loc"):
            if loc.text:
                urls.append(loc.text.strip())
        if not urls:
            for loc in element.iter("loc"):
                if loc.text:
                    urls.append(loc.text.strip())
    return urls


def _parse_sitemap_xml(xml_text: str, *, warn: WarnFn) -> ET.Element | None:
    try:
        return ET.fromstring(xml_text)
    except ET.ParseError:
        warn("Invalid sitemap XML; skipping.")
        return None


def _cap_url_list(urls: list[str], max_urls: int, *, warn: WarnFn) -> list[str]:
    if len(urls) <= max_urls:
        return urls
    warn(
        "Sitemap produced %d URLs; truncating to %d.",
        len(urls),
        max_urls,
    )
    return urls[:max_urls]


async def fetch_sitemap_urls(
    url: str,
    client: httpx.AsyncClient,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
    max_urls: int = MAX_SITEMAP_URLS,
    max_response_bytes: int = MAX_SITEMAP_RESPONSE_BYTES,
    warn: WarnFn | None = None,
    _depth: int = 0,
) -> list[str]:
    """Fetch a sitemap (or sitemap index) and return page URLs."""
    log_warn = warn if warn is not None else lambda *_args, **_kwargs: None

    if _depth > max_depth:
        return []

    response = await client.get(url)
    response.raise_for_status()

    if len(response.content) > max_response_bytes:
        log_warn(
            "Sitemap response from %s exceeds %d bytes; skipping.",
            url,
            max_response_bytes,
        )
        return []

    root = _parse_sitemap_xml(response.text, warn=log_warn)
    if root is None:
        return []

    root_tag = _local_tag(root)
    if root_tag == "sitemapindex":
        urls: list[str] = []
        for child_url in _iter_locs(root, "sitemap"):
            if len(urls) >= max_urls:
                break
            try:
                child_urls = await fetch_sitemap_urls(
                    child_url,
                    client,
                    max_depth=max_depth,
                    max_urls=max_urls - len(urls),
                    max_response_bytes=max_response_bytes,
                    warn=warn,
                    _depth=_depth + 1,
                )
                urls.extend(child_urls)
            except httpx.HTTPError as exc:
                log_warn("Failed to fetch child sitemap %s: %s", child_url, exc)
        return _cap_url_list(urls, max_urls, warn=log_warn)

    if root_tag == "urlset":
        return _cap_url_list(_iter_locs(root, "url"), max_urls, warn=log_warn)

    locs: list[str] = []
    for loc in root.iter(f"{{{SITEMAP_NS}}}loc"):
        if loc.text:
            locs.append(loc.text.strip())
    if not locs:
        for loc in root.iter("loc"):
            if loc.text:
                locs.append(loc.text.strip())
    return _cap_url_list(locs, max_urls, warn=log_warn)
