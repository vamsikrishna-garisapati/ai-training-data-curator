"""Sitemap URL parser with sitemap index support."""

from __future__ import annotations

import logging
import xml.etree.ElementTree as ET

import httpx

SITEMAP_NS = "http://www.sitemaps.org/schemas/sitemap/0.9"
DEFAULT_MAX_DEPTH = 2

logger = logging.getLogger(__name__)


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


def _parse_sitemap_xml(xml_text: str) -> ET.Element | None:
    try:
        return ET.fromstring(xml_text)
    except ET.ParseError:
        logger.warning("Invalid sitemap XML; skipping.")
        return None


async def fetch_sitemap_urls(
    url: str,
    client: httpx.AsyncClient,
    *,
    max_depth: int = DEFAULT_MAX_DEPTH,
    _depth: int = 0,
) -> list[str]:
    """Fetch a sitemap (or sitemap index) and return page URLs."""
    if _depth > max_depth:
        return []

    response = await client.get(url)
    response.raise_for_status()

    root = _parse_sitemap_xml(response.text)
    if root is None:
        return []

    root_tag = _local_tag(root)
    if root_tag == "sitemapindex":
        urls: list[str] = []
        for child_url in _iter_locs(root, "sitemap"):
            try:
                urls.extend(
                    await fetch_sitemap_urls(
                        child_url,
                        client,
                        max_depth=max_depth,
                        _depth=_depth + 1,
                    )
                )
            except httpx.HTTPError as exc:
                logger.warning("Failed to fetch child sitemap %s: %s", child_url, exc)
        return urls

    if root_tag == "urlset":
        return _iter_locs(root, "url")

    locs: list[str] = []
    for loc in root.iter(f"{{{SITEMAP_NS}}}loc"):
        if loc.text:
            locs.append(loc.text.strip())
    if not locs:
        for loc in root.iter("loc"):
            if loc.text:
                locs.append(loc.text.strip())
    return locs
