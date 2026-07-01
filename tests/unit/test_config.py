"""Tests for ActorConfig input parsing."""

import pytest

from src.config import ActorConfig


def test_from_input_defaults():
    config = ActorConfig.from_input({})
    assert config.start_urls == []
    assert config.sitemap_url is None
    assert config.max_pages == 10
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
    assert config.effective_max_sitemap_urls == 10
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
    assert config.max_pages == 10


@pytest.mark.parametrize(
    "max_pages,expected",
    [(0, 1), (-1, 1), (100_001, 100_000), ("50", 10)],
)
def test_from_input_coerces_invalid_max_pages(max_pages, expected):
    config = ActorConfig.from_input({"maxPages": max_pages})
    assert config.max_pages == expected


@pytest.mark.parametrize(
    "min_len,expected",
    [(-1, 0), ("100", 100)],
)
def test_from_input_coerces_invalid_min_text_length(min_len, expected):
    config = ActorConfig.from_input({"minTextLength": min_len})
    assert config.min_text_length == expected


def test_from_input_coerces_invalid_deduplicate():
    config = ActorConfig.from_input({"deduplicate": "yes"})
    assert config.deduplicate is True


def test_from_input_coerces_invalid_max_concurrency():
    config = ActorConfig.from_input({"maxConcurrency": 0})
    assert config.max_concurrency == 1


def test_from_input_coerces_invalid_crawl_strategy():
    config = ActorConfig.from_input({"crawlStrategy": "breadth-first"})
    assert config.crawl_strategy == "recurse"


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
            "includeUrlGlobs": ["https://books.toscrape.com/**"],
            "excludeUrlGlobs": ["**/*.pdf"],
            "maxSitemapUrls": 25,
            "minRequestDelaySecs": 1.5,
            "maxFingerprints": 1000,
            "maxDepth": 2,
            "exportRejectedPages": True,
        }
    )
    assert config.stay_within_domain is False
    assert config.include_url_globs == ["https://books.toscrape.com/**"]
    assert config.exclude_url_globs == ["**/*.pdf"]
    assert config.max_sitemap_urls == 25
    assert config.effective_max_sitemap_urls == 25
    assert config.min_request_delay_secs == 1.5
    assert config.max_fingerprints == 1000
    assert config.max_depth == 2
    assert config.export_rejected_pages is True


@pytest.mark.parametrize(
    "field,value,attr,expected",
    [
        ("stayWithinDomain", "yes", "stay_within_domain", True),
        ("includeUrlGlobs", "bad", "include_url_globs", []),
        ("excludeUrlGlobs", {}, "exclude_url_globs", []),
        ("maxSitemapUrls", 0, "max_sitemap_urls", None),
        ("minRequestDelaySecs", -1, "min_request_delay_secs", 0.0),
        ("maxFingerprints", 0, "max_fingerprints", 1),
        ("maxDepth", -1, "max_depth", None),
        ("exportRejectedPages", "yes", "export_rejected_pages", False),
    ],
)
def test_from_input_coerces_invalid_new_fields(field, value, attr, expected):
    config = ActorConfig.from_input({field: value})
    assert getattr(config, attr) == expected
