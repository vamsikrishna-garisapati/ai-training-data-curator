"""Tests for sitemap index parsing."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.sitemap import fetch_sitemap_urls


SITEMAP_INDEX_XML = """<?xml version="1.0" encoding="UTF-8"?>
<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <sitemap>
        <loc>https://books.toscrape.com/sitemap-pages.xml</loc>
    </sitemap>
</sitemapindex>"""

CHILD_SITEMAP_XML = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url><loc>https://books.toscrape.com/page-from-index</loc></url>
</urlset>"""


@pytest.mark.asyncio
async def test_fetch_sitemap_urls_follows_sitemap_index():
    responses = {
        "https://books.toscrape.com/sitemap_index.xml": SITEMAP_INDEX_XML,
        "https://books.toscrape.com/sitemap-pages.xml": CHILD_SITEMAP_XML,
    }

    async def mock_get(url, *args, **kwargs):
        mock_response = MagicMock()
        mock_response.text = responses[str(url)]
        mock_response.raise_for_status = MagicMock()
        return mock_response

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.side_effect = mock_get

    urls = await fetch_sitemap_urls("https://books.toscrape.com/sitemap_index.xml", mock_client)
    assert urls == ["https://books.toscrape.com/page-from-index"]


@pytest.mark.asyncio
async def test_fetch_sitemap_urls_returns_empty_on_invalid_xml():
    mock_response = MagicMock()
    mock_response.text = "not valid xml"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    urls = await fetch_sitemap_urls("https://books.toscrape.com/sitemap.xml", mock_client)
    assert urls == []
