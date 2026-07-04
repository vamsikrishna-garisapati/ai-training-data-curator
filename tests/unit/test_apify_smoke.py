"""Tests for Apify automated daily-check input (prefill values)."""

from src.config import ActorConfig
from tests.prefill import load_prefill_input


def test_apify_prefill_input_is_valid_smoke_config():
    """Mirrors .actor/input_schema.json prefill used by Apify daily health checks."""
    prefill = load_prefill_input()
    config = ActorConfig.from_input(prefill)

    assert config.start_urls == [prefill["startUrls"][0]["url"]]
    assert config.max_pages == prefill["maxPages"]
    assert config.min_text_length == prefill["minTextLength"]
    assert config.crawl_strategy == prefill["crawlStrategy"]
    assert config.max_pages <= 10
