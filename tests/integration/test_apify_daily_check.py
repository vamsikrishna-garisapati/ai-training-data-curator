"""Guarantee Apify automated daily-check prefill produces a non-empty dataset."""

from src.config import ActorConfig
from src.constants import APIFY_SMOKE_START_URL
from src.crawler import process_page
from tests.smoke_html import APIFY_DAILY_CHECK_HTML

PREFILL_INPUT = {
    "startUrls": [{"url": APIFY_SMOKE_START_URL}],
    "maxPages": 5,
    "minTextLength": 50,
    "crawlStrategy": "seeds-only",
}


def test_prefill_input_matches_input_schema_prefill():
    config = ActorConfig.from_input(PREFILL_INPUT)
    assert config.start_urls == [APIFY_SMOKE_START_URL]
    assert config.max_pages == 5
    assert config.min_text_length == 50
    assert config.crawl_strategy == "seeds-only"


def test_prefill_seed_page_produces_dataset_record():
    """Apify daily check requires Succeeded + non-empty default dataset."""
    config = ActorConfig.from_input(PREFILL_INPUT)

    record, reject_reason = process_page(
        APIFY_DAILY_CHECK_HTML,
        APIFY_SMOKE_START_URL,
        config,
        None,
        None,
    )

    assert reject_reason is None, f"Prefill page was filtered: {reject_reason}"
    assert record is not None
    assert record["url"] == APIFY_SMOKE_START_URL
    assert len(record.get("text", "")) >= config.min_text_length
    assert record.get("wordCount", 0) > 0
