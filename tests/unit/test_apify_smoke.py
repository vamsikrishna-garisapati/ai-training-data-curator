"""Tests for Apify automated daily-check input (prefill values)."""

from src.config import ActorConfig
from src.constants import APIFY_SMOKE_START_URL


def test_apify_prefill_input_is_valid_smoke_config():
    """Mirrors .actor/input_schema.json prefill + defaults used by Apify daily tests."""
    config = ActorConfig.from_input(
        {
            "startUrls": [{"url": APIFY_SMOKE_START_URL}],
            "maxPages": 1,
            "minTextLength": 50,
            "crawlStrategy": "seeds-only",
        }
    )
    assert config.start_urls == [APIFY_SMOKE_START_URL]
    assert config.max_pages == 1
    assert config.min_text_length == 50
    assert config.crawl_strategy == "seeds-only"
    assert config.max_pages <= 10
