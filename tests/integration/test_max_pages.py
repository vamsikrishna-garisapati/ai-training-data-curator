"""Integration tests for maxPages configuration."""

from src.config import ActorConfig
from src.crawler import build_crawler


def test_build_crawler_sets_max_requests_per_crawl():
    config = ActorConfig.from_input({"maxPages": 3})
    crawler = build_crawler(config, deduplicator=None)
    assert crawler._max_requests_per_crawl == 3  # noqa: SLF001


def test_max_pages_default_from_input():
    config = ActorConfig.from_input({})
    crawler = build_crawler(config, None)
    assert crawler._max_requests_per_crawl == 10  # noqa: SLF001
