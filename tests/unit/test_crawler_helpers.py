"""Tests for crawler helper functions."""

from unittest.mock import AsyncMock, MagicMock

import pytest

from src.config import ActorConfig
from src.crawler import _get_html, build_crawler, is_html_content_type
from src.stats import CrawlStats


@pytest.mark.asyncio
async def test_get_html_prefers_http_response_over_soup():
    context = MagicMock()
    context.soup = "<html>from soup</html>"
    context.http_response = MagicMock()
    context.http_response.read = AsyncMock(return_value=b"<html>from body</html>")

    assert await _get_html(context) == "<html>from body</html>"


@pytest.mark.asyncio
async def test_get_html_from_http_response_bytes():
    context = MagicMock()
    context.soup = None
    context.http_response = MagicMock()
    context.http_response.read = AsyncMock(return_value=b"<html>hello</html>")

    assert await _get_html(context) == "<html>hello</html>"


@pytest.mark.asyncio
async def test_get_html_from_http_response_str():
    context = MagicMock()
    context.soup = None
    context.http_response = MagicMock()
    context.http_response.read = AsyncMock(return_value="<html>hello</html>")

    assert await _get_html(context) == "<html>hello</html>"


@pytest.mark.asyncio
async def test_get_html_falls_back_to_soup_when_no_http_response():
    context = MagicMock()
    context.soup = "<html>from soup</html>"
    context.http_response = None

    assert await _get_html(context) == "<html>from soup</html>"


@pytest.mark.asyncio
async def test_get_html_falls_back_to_empty_when_no_source():
    context = MagicMock()
    context.soup = None
    context.http_response = None

    assert await _get_html(context) == ""


@pytest.mark.parametrize(
    "content_type,expected",
    [
        ("text/html; charset=utf-8", True),
        ("application/xhtml+xml", True),
        ("text/plain", True),
        ("", True),
        ("application/pdf", False),
        ("text/css", False),
        ("text/javascript", False),
        ("image/png", False),
        ("video/mp4", False),
    ],
)
def test_is_html_content_type(content_type, expected):
    assert is_html_content_type(content_type) is expected


def test_build_crawler_configures_request_rate_limit():
    config = ActorConfig.from_input({"minRequestDelaySecs": 2, "maxConcurrency": 5})
    crawler = build_crawler(config, None, allowed_hosts={"books.toscrape.com"})
    assert crawler._autoscaled_pool._max_tasks_per_minute == 30  # noqa: SLF001


@pytest.mark.asyncio
async def test_request_handler_skips_non_html_and_does_not_enqueue(monkeypatch):
    config = ActorConfig.from_input({"crawlStrategy": "recurse"})
    stats = MagicMock()
    enqueue = AsyncMock()
    push_data = AsyncMock()

    context = MagicMock()
    context.request.url = "https://books.toscrape.com/file.pdf"
    context.http_response = MagicMock()
    context.http_response.headers = {"content-type": "application/pdf"}
    context.enqueue_links = enqueue
    context.push_data = push_data

    crawler = build_crawler(config, None, stats=stats, allowed_hosts={"books.toscrape.com"})
    handler = crawler.router._default_handler
    assert handler is not None

    get_html = AsyncMock(return_value="<html>ignored</html>")
    process_page = MagicMock(return_value=({"url": "ignored"}, None))
    monkeypatch.setattr("src.crawler._get_html", get_html)
    monkeypatch.setattr("src.crawler.process_page", process_page)

    await handler(context)

    get_html.assert_not_called()
    process_page.assert_not_called()
    push_data.assert_not_called()
    enqueue.assert_not_awaited()


def test_build_crawler_uses_full_max_concurrency():
    config = ActorConfig.from_input({"maxConcurrency": 25})
    crawler = build_crawler(config, None, allowed_hosts={"books.toscrape.com"})
    assert crawler._autoscaled_pool._desired_concurrency == 25  # noqa: SLF001


@pytest.mark.asyncio
async def test_request_handler_exports_rejected_pages(monkeypatch):
    config = ActorConfig.from_input({"exportRejectedPages": True})
    push_data = AsyncMock()

    context = MagicMock()
    context.request.url = "https://books.toscrape.com/short"
    context.request.user_data = {"depth": 0}
    context.http_response = MagicMock()
    context.http_response.headers = {"content-type": "text/html"}
    context.enqueue_links = AsyncMock()
    context.push_data = push_data

    crawler = build_crawler(config, None, allowed_hosts={"books.toscrape.com"})
    handler = crawler.router._default_handler
    assert handler is not None

    monkeypatch.setattr("src.crawler._get_html", AsyncMock(return_value="<html></html>"))
    monkeypatch.setattr("src.crawler.process_page", MagicMock(return_value=(None, "length")))

    await handler(context)

    push_data.assert_awaited_once_with(
        {"url": "https://books.toscrape.com/short", "filterReason": "length"},
        dataset_name="rejected",
    )


@pytest.mark.asyncio
async def test_request_handler_skips_enqueue_at_max_depth(monkeypatch):
    config = ActorConfig.from_input({"crawlStrategy": "recurse", "maxDepth": 1})
    enqueue = AsyncMock()

    context = MagicMock()
    context.request.url = "https://books.toscrape.com/"
    context.request.user_data = {"depth": 1}
    context.http_response = MagicMock()
    context.http_response.headers = {"content-type": "text/html"}
    context.enqueue_links = enqueue
    context.push_data = AsyncMock()

    crawler = build_crawler(config, None, allowed_hosts={"books.toscrape.com"})
    handler = crawler.router._default_handler
    assert handler is not None

    monkeypatch.setattr("src.crawler._get_html", AsyncMock(return_value="<html><body>ok</body></html>"))
    monkeypatch.setattr(
        "src.crawler.process_page",
        MagicMock(return_value=({"url": "https://books.toscrape.com/"}, None)),
    )

    await handler(context)

    enqueue.assert_not_awaited()


@pytest.mark.asyncio
async def test_request_handler_survives_push_data_failure(monkeypatch):
    config = ActorConfig.from_input({"startUrls": [{"url": "https://books.toscrape.com"}]})
    stats = CrawlStats()

    context = MagicMock()
    context.request.url = "https://books.toscrape.com/page"
    context.request.user_data = {"depth": 0}
    context.http_response = MagicMock()
    context.http_response.headers = {"content-type": "text/html"}
    context.enqueue_links = AsyncMock()
    context.push_data = AsyncMock(side_effect=RuntimeError("dataset write failed"))
    context.log = MagicMock()

    crawler = build_crawler(config, None, stats=stats, allowed_hosts={"books.toscrape.com"})
    handler = crawler.router._default_handler
    assert handler is not None

    monkeypatch.setattr(
        "src.crawler._get_html",
        AsyncMock(return_value="<html><body>content</body></html>"),
    )
    monkeypatch.setattr(
        "src.crawler.process_page",
        MagicMock(return_value=({"url": "https://books.toscrape.com/page"}, None)),
    )

    await handler(context)

    assert stats.saved == 0
    assert stats.failed == 1
    context.log.warning.assert_called_once()


@pytest.mark.asyncio
async def test_request_handler_survives_handler_exception(monkeypatch):
    config = ActorConfig.from_input({"startUrls": [{"url": "https://books.toscrape.com"}]})
    stats = CrawlStats()

    context = MagicMock()
    context.request.url = "https://books.toscrape.com/error"
    context.request.user_data = {"depth": 0}
    context.http_response = MagicMock()
    context.http_response.headers = {"content-type": "text/html"}
    context.enqueue_links = AsyncMock()
    context.push_data = AsyncMock()

    crawler = build_crawler(config, None, stats=stats, allowed_hosts={"books.toscrape.com"})
    handler = crawler.router._default_handler
    assert handler is not None

    monkeypatch.setattr("src.crawler._get_html", AsyncMock(side_effect=RuntimeError("boom")))

    await handler(context)

    assert stats.failed == 1
