"""Crawlee BeautifulSoupCrawler setup and page processing pipeline."""

from __future__ import annotations

from typing import TYPE_CHECKING

from crawlee import ConcurrencySettings
from crawlee.crawlers import BeautifulSoupCrawler, BeautifulSoupCrawlingContext

from src.config import ActorConfig
from src.crawl_depth import (
    REJECTED_DATASET_NAME,
    get_request_depth,
    should_follow_links,
    depth_transform_request,
)
from src.dedup.simhash_dedup import Deduplicator
from src.extractors.text_extractor import extract_page
from src.filters.language_filter import passes_language
from src.filters.length_filter import passes_length
from src.filters.quality_filter import passes_quality
from src.stats import CrawlStats
from src.urls import build_enqueue_link_kwargs

if TYPE_CHECKING:
    from crawlee.proxy_configuration import ProxyConfiguration

FILTER_REASON_EXTRACTION = "extraction"
FILTER_REASON_LANGUAGE = "language"
FILTER_REASON_LENGTH = "length"
FILTER_REASON_QUALITY = "quality"
FILTER_REASON_DEDUP = "dedup"
FILTER_REASON_NON_HTML = "non_html"


_HTML_CONTENT_TYPES = frozenset(
    {"text/html", "application/xhtml+xml", "text/plain"},
)


def is_html_content_type(content_type: str) -> bool:
    """Return True when the response should be treated as HTML for extraction."""
    normalized = content_type.lower().split(";", maxsplit=1)[0].strip()
    if not normalized:
        return True
    if normalized in _HTML_CONTENT_TYPES:
        return True
    return "html" in normalized


def process_page(
    html: str,
    url: str,
    config: ActorConfig,
    deduplicator: Deduplicator | None,
    stats: CrawlStats | None = None,
) -> tuple[dict | None, str | None]:
    """Run extract → filter → dedup pipeline; return (record, reject_reason)."""
    record = extract_page(html, url, min_text_length=config.min_text_length)
    if record is None:
        if stats is not None:
            stats.filtered_extraction += 1
        return None, FILTER_REASON_EXTRACTION

    text = record.get("text", "")
    if config.language and not passes_language(
        text,
        config.language,
        html,
        detected_language=record.get("language") or None,
    ):
        if stats is not None:
            stats.filtered_language += 1
        return None, FILTER_REASON_LANGUAGE
    if not passes_length(text, config.min_text_length):
        if stats is not None:
            stats.filtered_length += 1
        return None, FILTER_REASON_LENGTH
    if not passes_quality(text):
        if stats is not None:
            stats.filtered_quality += 1
        return None, FILTER_REASON_QUALITY
    if deduplicator is not None and deduplicator.is_duplicate(text):
        if stats is not None:
            stats.filtered_dedup += 1
        return None, FILTER_REASON_DEDUP

    return record, None


async def _push_rejected(
    context: BeautifulSoupCrawlingContext,
    url: str,
    filter_reason: str,
) -> None:
    try:
        await context.push_data(
            {"url": url, "filterReason": filter_reason},
            dataset_name=REJECTED_DATASET_NAME,
        )
    except Exception as exc:
        context.log.warning(
            "Failed to push rejected record for %s: %s",
            url,
            exc,
        )


def build_crawler(
    config: ActorConfig,
    deduplicator: Deduplicator | None,
    proxy_configuration: ProxyConfiguration | None = None,
    stats: CrawlStats | None = None,
    allowed_hosts: set[str] | None = None,
) -> BeautifulSoupCrawler:
    """Create a configured BeautifulSoupCrawler with the full pipeline handler."""
    max_tasks_per_minute = (
        float("inf")
        if config.min_request_delay_secs <= 0
        else 60.0 / config.min_request_delay_secs
    )
    enqueue_kwargs = build_enqueue_link_kwargs(config, allowed_hosts or set())

    crawler = BeautifulSoupCrawler(
        max_requests_per_crawl=config.max_pages,
        respect_robots_txt_file=True,
        proxy_configuration=proxy_configuration,
        concurrency_settings=ConcurrencySettings(
            max_concurrency=config.max_concurrency,
            desired_concurrency=config.max_concurrency,
            max_tasks_per_minute=max_tasks_per_minute,
        ),
    )

    @crawler.router.default_handler
    async def request_handler(context: BeautifulSoupCrawlingContext) -> None:
        try:
            if stats is not None:
                stats.crawled += 1

            url = context.request.url
            current_depth = get_request_depth(context.request.user_data)

            content_type = ""
            if context.http_response is not None:
                content_type = context.http_response.headers.get("content-type", "")

            should_extract = is_html_content_type(content_type)
            if should_extract:
                html = await _get_html(context)
                record, reject_reason = process_page(
                    html, url, config, deduplicator, stats
                )
                if record:
                    try:
                        await context.push_data(record)
                        if stats is not None:
                            stats.saved += 1
                    except Exception as exc:
                        if stats is not None:
                            stats.failed += 1
                        context.log.warning(
                            "Failed to save dataset record for %s: %s",
                            url,
                            exc,
                        )
                elif config.export_rejected_pages and reject_reason:
                    await _push_rejected(context, url, reject_reason)
            elif config.export_rejected_pages:
                await _push_rejected(context, url, FILTER_REASON_NON_HTML)

            if (
                should_extract
                and config.crawl_strategy == "recurse"
                and should_follow_links(current_depth, config.max_depth)
            ):
                await context.enqueue_links(
                    **enqueue_kwargs,
                    transform_request_function=depth_transform_request(current_depth),
                )
        except Exception as exc:
            if stats is not None:
                stats.failed += 1
            crawler.log.exception(
                "Handler error for url=%s: %s",
                context.request.url,
                exc,
            )

    @crawler.failed_request_handler
    async def failed_request_handler(
        context: BeautifulSoupCrawlingContext,
        error: Exception,
    ) -> None:
        if stats is not None:
            stats.failed += 1
        crawler.log.warning(
            "Request failed: url=%s error=%s",
            context.request.url,
            error,
        )

    return crawler


async def _get_html(context: BeautifulSoupCrawlingContext) -> str:
    """Extract raw HTML from the crawling context."""
    if context.http_response is not None:
        body = await context.http_response.read()
        if isinstance(body, bytes):
            return body.decode("utf-8", errors="replace")
        return str(body)
    if context.soup is not None:
        return str(context.soup)
    return ""
