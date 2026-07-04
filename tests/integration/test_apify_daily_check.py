"""Guarantee Apify automated daily-check prefill produces a non-empty dataset."""

from src.config import ActorConfig
from src.crawler import process_page
from tests.prefill import load_prefill_input
from tests.smoke_html import APIFY_DAILY_CHECK_HTML

PREFILL_INPUT = load_prefill_input()
PREFILL_URL = PREFILL_INPUT["startUrls"][0]["url"]


def test_prefill_input_matches_input_schema_prefill():
    config = ActorConfig.from_input(PREFILL_INPUT)
    assert config.start_urls == [PREFILL_URL]
    assert config.max_pages == PREFILL_INPUT["maxPages"]
    assert config.min_text_length == PREFILL_INPUT["minTextLength"]
    assert config.crawl_strategy == PREFILL_INPUT["crawlStrategy"]


def test_prefill_seed_page_produces_dataset_record():
    """Apify daily check requires Succeeded + non-empty default dataset."""
    config = ActorConfig.from_input(PREFILL_INPUT)

    record, reject_reason = process_page(
        APIFY_DAILY_CHECK_HTML,
        PREFILL_URL,
        config,
        None,
        None,
    )

    assert reject_reason is None, f"Prefill page was filtered: {reject_reason}"
    assert record is not None
    assert record["url"] == PREFILL_URL
    assert len(record.get("text", "")) >= config.min_text_length
    assert record.get("wordCount", 0) > 0
