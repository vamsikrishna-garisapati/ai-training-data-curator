"""Tests for sitemap parser without XML namespace."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.sitemap import fetch_sitemap_urls


@pytest.mark.asyncio
async def test_fetch_sitemap_urls_without_namespace():
    xml = """<?xml version="1.0"?>
    <urlset>
        <url><loc>https://books.toscrape.com/no-ns</loc></url>
    </urlset>"""

    mock_response = MagicMock()
    mock_response.text = xml
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    urls = await fetch_sitemap_urls("https://books.toscrape.com/sitemap.xml", mock_client)
    assert urls == ["https://books.toscrape.com/no-ns"]
