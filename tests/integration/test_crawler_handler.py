"""Integration tests for the crawler page processing pipeline."""

from src.config import ActorConfig
from src.crawler import build_crawler, process_page
from src.dedup.simhash_dedup import Deduplicator
from src.stats import CrawlStats


def test_process_page_full_pipeline(article_html):
    config = ActorConfig.from_input(
        {
            "startUrls": [{"url": "https://books.toscrape.com/article"}],
            "language": "en",
            "minTextLength": 100,
            "deduplicate": True,
        }
    )
    dedup = Deduplicator()

    record, reject_reason = process_page(
        article_html,
        "https://books.toscrape.com/article",
        config,
        dedup,
    )

    assert record is not None
    assert reject_reason is None
    assert record["url"] == "https://books.toscrape.com/article"
    assert record["wordCount"] > 0
    assert "machine learning" in record["text"].lower()


def test_process_page_rejects_wrong_language(article_html):
    config = ActorConfig.from_input({"language": "de", "minTextLength": 50})
    record, reject_reason = process_page(article_html, "https://books.toscrape.com/article", config, None)
    assert record is None
    assert reject_reason == "language"


def test_process_page_rejects_short_text():
    config = ActorConfig.from_input({"minTextLength": 10_000})
    html = "<html><body><p>Too short.</p></body></html>"
    record, reject_reason = process_page(html, "https://books.toscrape.com/short", config, None)
    assert record is None
    assert reject_reason == "length"


def test_process_page_rejects_low_quality():
    config = ActorConfig.from_input({"minTextLength": 10})
    nav_text = "\n".join(["Home", "Books", "Travel", "Mystery"] * 10)
    html = f"<html><body><p>{nav_text}</p></body></html>"
    record, reject_reason = process_page(html, "https://books.toscrape.com/nav", config, None)
    assert record is None
    assert reject_reason == "quality"


def test_process_page_deduplication(article_html):
    config = ActorConfig.from_input({"minTextLength": 50})
    dedup = Deduplicator()

    first, _ = process_page(article_html, "https://books.toscrape.com/a", config, dedup)
    second, reject_reason = process_page(article_html, "https://books.toscrape.com/b", config, dedup)

    assert first is not None
    assert second is None
    assert reject_reason == "dedup"


def test_process_page_returns_none_for_unextractable_html():
    config = ActorConfig.from_input({})
    record, reject_reason = process_page("<html></html>", "https://books.toscrape.com/empty", config, None)
    assert record is None
    assert reject_reason == "extraction"


def test_process_page_tracks_stats(article_html):
    config = ActorConfig.from_input({"minTextLength": 50})
    stats = CrawlStats()
    record, _ = process_page(article_html, "https://books.toscrape.com/a", config, None, stats)
    assert record is not None
    assert stats.filtered_extraction == 0


def test_build_crawler_returns_configured_crawler():
    config = ActorConfig.from_input({"maxPages": 25, "maxConcurrency": 5})
    crawler = build_crawler(config, Deduplicator(), allowed_hosts={"books.toscrape.com"})
    assert crawler is not None
    assert crawler._max_requests_per_crawl == 25  # noqa: SLF001
