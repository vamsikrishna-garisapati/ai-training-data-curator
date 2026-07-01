"""Tests for URL helper utilities."""

from src.config import ActorConfig
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
        "http://example.com:8080/path",
        "not-a-url",
    ]
    assert derive_allowed_hosts(urls) == {"books.toscrape.com", "example.com"}


def test_cap_seed_urls():
    urls = [f"https://example.com/{index}" for index in range(10)]
    assert len(cap_seed_urls(urls, 3)) == 3
    assert cap_seed_urls(urls, 3)[0] == "https://example.com/0"


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
