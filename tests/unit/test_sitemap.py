"""Tests for sitemap URL parser."""

from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from src.sitemap import fetch_sitemap_urls


@pytest.mark.asyncio
async def test_fetch_sitemap_urls(sitemap_xml):
    mock_response = MagicMock()
    mock_response.text = sitemap_xml
    mock_response.content = sitemap_xml.encode()
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    urls = await fetch_sitemap_urls("https://books.toscrape.com/sitemap.xml", mock_client)

    assert urls == [
        "https://books.toscrape.com/page1",
        "https://books.toscrape.com/page2",
        "https://books.toscrape.com/blog/post-1",
    ]
    mock_client.get.assert_called_once_with("https://books.toscrape.com/sitemap.xml")


@pytest.mark.asyncio
async def test_fetch_sitemap_urls_raises_on_http_error():
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = httpx.HTTPStatusError(
        "Not Found",
        request=MagicMock(),
        response=MagicMock(status_code=404),
    )

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    with pytest.raises(httpx.HTTPStatusError):
        await fetch_sitemap_urls("https://books.toscrape.com/sitemap.xml", mock_client)


@pytest.mark.asyncio
async def test_fetch_sitemap_urls_returns_empty_on_invalid_xml():
    mock_response = MagicMock()
    mock_response.text = "not valid xml <<>>"
    mock_response.content = b"not valid xml <<>>"
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    urls = await fetch_sitemap_urls("https://books.toscrape.com/sitemap.xml", mock_client)
    assert urls == []


@pytest.mark.asyncio
async def test_fetch_sitemap_urls_skips_oversized_response():
    mock_response = MagicMock()
    mock_response.text = "<urlset></urlset>"
    mock_response.content = b"x" * (10 * 1024 * 1024 + 1)
    mock_response.raise_for_status = MagicMock()

    mock_client = AsyncMock(spec=httpx.AsyncClient)
    mock_client.get.return_value = mock_response

    warn = MagicMock()
    urls = await fetch_sitemap_urls(
        "https://books.toscrape.com/sitemap.xml",
        mock_client,
        warn=warn,
    )
    assert urls == []
    warn.assert_called()
