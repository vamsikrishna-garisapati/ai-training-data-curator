"""Tests for ActorConfig input parsing."""

import pytest

from src.config import ActorConfig


def test_from_input_defaults():
    config = ActorConfig.from_input({})
    assert config.start_urls == []
    assert config.sitemap_url is None
    assert config.max_pages == 100
    assert config.min_text_length == 100
    assert config.language is None
    assert config.deduplicate is True
    assert config.proxy_configuration is None
    assert config.max_concurrency == 10
    assert config.crawl_strategy == "recurse"
    assert config.stay_within_domain is True
    assert config.include_url_globs == []
    assert config.exclude_url_globs == []
    assert config.max_sitemap_urls is None
    assert config.effective_max_sitemap_urls == 100
    assert config.min_request_delay_secs == 0
    assert config.max_fingerprints == 50_000
    assert config.max_depth is None
    assert config.export_rejected_pages is False


def test_from_input_parses_start_urls():
    raw = {
        "startUrls": [{"url": "https://books.toscrape.com"}, {"url": "https://test.com"}],
        "maxPages": 50,
        "minTextLength": 200,
        "language": "en",
        "deduplicate": False,
        "sitemapUrl": "https://books.toscrape.com/sitemap.xml",
        "maxConcurrency": 5,
        "crawlStrategy": "seeds-only",
        "proxyConfiguration": {"useApifyProxy": True},
    }
    config = ActorConfig.from_input(raw)
    assert config.start_urls == ["https://books.toscrape.com", "https://test.com"]
    assert config.sitemap_url == "https://books.toscrape.com/sitemap.xml"
    assert config.max_pages == 50
    assert config.min_text_length == 200
    assert config.language == "en"
    assert config.deduplicate is False
    assert config.max_concurrency == 5
    assert config.crawl_strategy == "seeds-only"
    assert config.proxy_configuration == {"useApifyProxy": True}


def test_from_input_accepts_string_urls():
    config = ActorConfig.from_input({"startUrls": ["https://books.toscrape.com"]})
    assert config.start_urls == ["https://books.toscrape.com"]


def test_from_input_empty_language_becomes_none():
    config = ActorConfig.from_input({"language": ""})
    assert config.language is None


def test_from_input_none_input():
    config = ActorConfig.from_input(None)
    assert config.max_pages == 100


@pytest.mark.parametrize("max_pages", [0, -1, 100_001, "50"])
def test_from_input_invalid_max_pages(max_pages):
    with pytest.raises(ValueError, match="maxPages"):
        ActorConfig.from_input({"maxPages": max_pages})


@pytest.mark.parametrize("min_len", [-1, "100"])
def test_from_input_invalid_min_text_length(min_len):
    with pytest.raises(ValueError, match="minTextLength"):
        ActorConfig.from_input({"minTextLength": min_len})


def test_from_input_invalid_deduplicate():
    with pytest.raises(ValueError, match="deduplicate"):
        ActorConfig.from_input({"deduplicate": "yes"})


def test_from_input_invalid_max_concurrency():
    with pytest.raises(ValueError, match="maxConcurrency"):
        ActorConfig.from_input({"maxConcurrency": 0})


def test_from_input_invalid_crawl_strategy():
    with pytest.raises(ValueError, match="crawlStrategy"):
        ActorConfig.from_input({"crawlStrategy": "breadth-first"})


def test_from_input_empty_sitemap_becomes_none():
    config = ActorConfig.from_input({"sitemapUrl": ""})
    assert config.sitemap_url is None


def test_from_input_skips_empty_url_dicts():
    config = ActorConfig.from_input({"startUrls": [{"url": ""}, {"url": "https://ok.com"}]})
    assert config.start_urls == ["https://ok.com"]


def test_from_input_parses_new_fields():
    config = ActorConfig.from_input(
        {
            "stayWithinDomain": False,
            "includeUrlGlobs": ["https://example.com/**"],
            "excludeUrlGlobs": ["**/*.pdf"],
            "maxSitemapUrls": 25,
            "minRequestDelaySecs": 1.5,
            "maxFingerprints": 1000,
            "maxDepth": 2,
            "exportRejectedPages": True,
        }
    )
    assert config.stay_within_domain is False
    assert config.include_url_globs == ["https://example.com/**"]
    assert config.exclude_url_globs == ["**/*.pdf"]
    assert config.max_sitemap_urls == 25
    assert config.effective_max_sitemap_urls == 25
    assert config.min_request_delay_secs == 1.5
    assert config.max_fingerprints == 1000
    assert config.max_depth == 2
    assert config.export_rejected_pages is True


@pytest.mark.parametrize(
    "field,value",
    [
        ("stayWithinDomain", "yes"),
        ("includeUrlGlobs", "bad"),
        ("excludeUrlGlobs", {}),
        ("maxSitemapUrls", 0),
        ("minRequestDelaySecs", -1),
        ("maxFingerprints", 0),
        ("maxDepth", -1),
        ("exportRejectedPages", "yes"),
    ],
)
def test_from_input_invalid_new_fields(field, value):
    with pytest.raises(ValueError):
        ActorConfig.from_input({field: value})
