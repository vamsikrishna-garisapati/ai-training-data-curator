"""Tests for URL helper utilities."""

from src.config import ActorConfig
from src.url_validation import is_valid_http_url, normalize_url_for_dedup
from src.urls import (
    build_enqueue_link_kwargs,
    cap_seed_urls,
    derive_allowed_hosts,
    host_include_globs,
    parse_url_globs,
)


def test_derive_allowed_hosts():
    urls = [
        "https://Books.Toscrape.com/page",
        "http://quotes.toscrape.com:8080/path",
        "not-a-url",
    ]
    assert derive_allowed_hosts(urls) == {"books.toscrape.com", "quotes.toscrape.com"}


def test_is_valid_http_url():
    assert is_valid_http_url("https://books.toscrape.com") is True
    assert is_valid_http_url("http://localhost:8080/path") is True
    assert is_valid_http_url("javascript:alert(1)") is False
    assert is_valid_http_url("file:///etc/passwd") is False
    assert is_valid_http_url("not-a-url") is False


def test_normalize_url_for_dedup():
    assert normalize_url_for_dedup("https://Books.Toscrape.com/page/") == (
        "https://books.toscrape.com/page"
    )
    assert normalize_url_for_dedup("https://books.toscrape.com/page?q=1#section") == (
        "https://books.toscrape.com/page"
    )


def test_cap_seed_urls():
    urls = [f"https://books.toscrape.com/page{index}" for index in range(10)]
    assert len(cap_seed_urls(urls, 3)) == 3
    assert cap_seed_urls(urls, 3)[0] == "https://books.toscrape.com/page0"


def test_parse_url_globs_skips_empty():
    globs = parse_url_globs(["https://a.com/**", ""])
    assert [glob.glob for glob in globs] == ["https://a.com/**"]


def test_host_include_globs_covers_http_and_https():
    globs = host_include_globs({"books.toscrape.com"})
    patterns = {glob.glob for glob in globs}
    assert patterns == {
        "https://books.toscrape.com/**",
        "http://books.toscrape.com/**",
    }


def test_build_enqueue_link_kwargs_stay_within_domain():
    config = ActorConfig.from_input(
        {
            "stayWithinDomain": True,
            "includeUrlGlobs": ["https://books.toscrape.com/catalogue/**"],
            "excludeUrlGlobs": ["**/*.jpg"],
        }
    )
    kwargs = build_enqueue_link_kwargs(config, {"books.toscrape.com"})
    assert kwargs["strategy"] == "all"
    assert len(kwargs["include"]) >= 2
    assert len(kwargs["exclude"]) == 1


def test_build_enqueue_link_kwargs_without_domain_restriction():
    config = ActorConfig.from_input({"stayWithinDomain": False})
    kwargs = build_enqueue_link_kwargs(config, {"books.toscrape.com"})
    assert kwargs == {"strategy": "all"}
