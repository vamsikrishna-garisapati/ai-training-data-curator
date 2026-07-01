"""Tests for Actor main entrypoint."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from src.crawl_depth import get_request_depth
from src.main import _dedupe_urls, main


def _seed_urls_from_run_call(mock_crawler) -> list[str]:
  requests = mock_crawler.run.call_args[0][0]
  return [request.url for request in requests]


def _patch_actor(mock_input: dict | None):
    mock_actor = MagicMock()
    mock_actor.get_input = AsyncMock(return_value=mock_input)
    mock_actor.log = MagicMock()
    mock_actor.create_proxy_configuration = AsyncMock(return_value=None)
    mock_actor.set_value = AsyncMock()
    mock_actor.fail = AsyncMock()
    mock_actor.__aenter__ = AsyncMock(return_value=mock_actor)
    mock_actor.__aexit__ = AsyncMock(return_value=None)
    return patch("src.main.Actor", mock_actor), mock_actor


@pytest.mark.asyncio
async def test_main_runs_crawler_with_start_urls():
    mock_crawler = AsyncMock()
    with _patch_actor({"startUrls": [{"url": "https://books.toscrape.com"}], "maxPages": 5})[0], patch(
        "src.main.build_crawler", return_value=mock_crawler
    ) as mock_build:
        await main()

    mock_build.assert_called_once()
    passed = mock_crawler.run.call_args[0][0]
    assert len(passed) == 1
    assert passed[0].url == "https://books.toscrape.com"
    assert get_request_depth(passed[0].user_data) == 0


@pytest.mark.asyncio
async def test_main_merges_sitemap_urls():
    mock_crawler = AsyncMock()
    with _patch_actor(
        {
            "startUrls": [{"url": "https://books.toscrape.com"}],
            "sitemapUrl": "https://books.toscrape.com/sitemap.xml",
        }
    )[0], patch("src.main.build_crawler", return_value=mock_crawler), patch(
        "src.main.fetch_sitemap_urls",
        AsyncMock(return_value=["https://books.toscrape.com/page1"]),
    ):
        await main()

    assert _seed_urls_from_run_call(mock_crawler) == [
        "https://books.toscrape.com",
        "https://books.toscrape.com/page1",
    ]


@pytest.mark.asyncio
async def test_main_uses_default_url_when_no_seeds():
    mock_crawler = AsyncMock()
    with _patch_actor({})[0], patch("src.main.build_crawler", return_value=mock_crawler) as mock_build:
        await main()

    mock_build.assert_called_once()
    assert _seed_urls_from_run_call(mock_crawler) == [
        "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html"
    ]


@pytest.mark.asyncio
async def test_main_coerces_invalid_input_and_runs():
    mock_crawler = AsyncMock()
    actor_patch, mock_actor = _patch_actor({"maxPages": "invalid", "startUrls": [{"url": "https://books.toscrape.com"}]})
    with actor_patch, patch("src.main.build_crawler", return_value=mock_crawler) as mock_build:
        await main()

    mock_build.assert_called_once()
    config = mock_build.call_args[0][0]
    assert config.max_pages == 10
    mock_actor.fail.assert_not_called()


@pytest.mark.asyncio
async def test_main_skips_deduplicator_when_disabled():
    mock_crawler = AsyncMock()
    with _patch_actor(
        {"startUrls": [{"url": "https://books.toscrape.com"}], "deduplicate": False}
    )[0], patch("src.main.build_crawler", return_value=mock_crawler) as mock_build:
        await main()

    _config, deduplicator, _proxy, _stats, _hosts = mock_build.call_args[0]
    assert deduplicator is None


@pytest.mark.asyncio
async def test_main_always_writes_summary_even_on_error():
    actor_patch, mock_actor = _patch_actor({"startUrls": [{"url": "https://books.toscrape.com"}]})
    with actor_patch, patch(
        "src.main.build_crawler",
        side_effect=RuntimeError("boom"),
    ):
        await main()

    mock_actor.set_value.assert_awaited_once()
    assert mock_actor.set_value.call_args[0][0] == "#SUMMARY"


@pytest.mark.asyncio
async def test_main_continues_when_sitemap_fetch_fails():
    mock_crawler = AsyncMock()
    with _patch_actor(
        {
            "startUrls": [{"url": "https://books.toscrape.com"}],
            "sitemapUrl": "https://books.toscrape.com/sitemap.xml",
        }
    )[0], patch("src.main.build_crawler", return_value=mock_crawler), patch(
        "src.main.fetch_sitemap_urls",
        AsyncMock(side_effect=httpx.HTTPStatusError(
            "Not Found",
            request=MagicMock(),
            response=MagicMock(status_code=404),
        )),
    ):
        await main()

    assert _seed_urls_from_run_call(mock_crawler) == ["https://books.toscrape.com"]


@pytest.mark.asyncio
async def test_main_deduplicates_seed_urls():
    mock_crawler = AsyncMock()
    with _patch_actor(
        {
            "startUrls": [
                {"url": "https://books.toscrape.com/"},
                {"url": "https://books.toscrape.com"},
            ],
        }
    )[0], patch("src.main.build_crawler", return_value=mock_crawler):
        await main()

    assert _seed_urls_from_run_call(mock_crawler) == ["https://books.toscrape.com/"]


@pytest.mark.asyncio
async def test_main_exports_summary():
    mock_crawler = AsyncMock()
    actor_patch, mock_actor = _patch_actor({"startUrls": [{"url": "https://books.toscrape.com"}]})
    with actor_patch, patch("src.main.build_crawler", return_value=mock_crawler):
        await main()

    mock_actor.set_value.assert_awaited_once()
    key, summary = mock_actor.set_value.call_args[0]
    assert key == "#SUMMARY"
    assert "crawled" in summary
    assert "saved" in summary
    assert "filtered" in summary


def test_dedupe_urls():
    urls = [
        "https://books.toscrape.com",
        "https://books.toscrape.com/",
        "https://books.toscrape.com/page",
    ]
    assert _dedupe_urls(urls) == [
        "https://books.toscrape.com",
        "https://books.toscrape.com/page",
    ]


@pytest.mark.asyncio
async def test_main_caps_merged_seed_urls():
    mock_crawler = AsyncMock()
    sitemap_urls = [f"https://books.toscrape.com/page{index}" for index in range(20)]
    with _patch_actor(
        {
            "startUrls": [{"url": "https://books.toscrape.com"}],
            "sitemapUrl": "https://books.toscrape.com/sitemap.xml",
            "maxPages": 5,
        }
    )[0], patch("src.main.build_crawler", return_value=mock_crawler), patch(
        "src.main.fetch_sitemap_urls",
        AsyncMock(return_value=sitemap_urls),
    ):
        await main()

    passed_urls = _seed_urls_from_run_call(mock_crawler)
    assert len(passed_urls) == 5
    assert passed_urls[0] == "https://books.toscrape.com"


@pytest.mark.asyncio
async def test_main_passes_allowed_hosts_to_crawler():
    mock_crawler = AsyncMock()
    with _patch_actor({"startUrls": [{"url": "https://books.toscrape.com"}]})[0], patch(
        "src.main.build_crawler", return_value=mock_crawler
    ) as mock_build:
        await main()

    assert mock_build.call_args[0][4] == {"books.toscrape.com"}


@pytest.mark.asyncio
async def test_main_uses_max_fingerprints_for_deduplicator():
    mock_crawler = AsyncMock()
    with _patch_actor(
        {"startUrls": [{"url": "https://books.toscrape.com"}], "maxFingerprints": 123}
    )[0], patch("src.main.build_crawler", return_value=mock_crawler) as mock_build:
        await main()

    deduplicator = mock_build.call_args[0][1]
    assert deduplicator.max_fingerprints == 123
