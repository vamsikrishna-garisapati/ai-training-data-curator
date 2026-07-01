"""Actor input configuration parsing and validation."""

from __future__ import annotations

from dataclasses import dataclass

CRAWL_STRATEGIES = ("recurse", "seeds-only")


def _parse_string_list(raw: object, field_name: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        raise ValueError(f"{field_name} must be an array of strings")
    result: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            raise ValueError(f"{field_name} must be an array of strings")
        if item:
            result.append(item)
    return result


@dataclass
class ActorConfig:
    start_urls: list[str]
    sitemap_url: str | None
    max_pages: int
    min_text_length: int
    language: str | None
    deduplicate: bool
    proxy_configuration: dict | None
    max_concurrency: int
    crawl_strategy: str
    stay_within_domain: bool
    include_url_globs: list[str]
    exclude_url_globs: list[str]
    max_sitemap_urls: int | None
    min_request_delay_secs: float
    max_fingerprints: int
    max_depth: int | None
    export_rejected_pages: bool

    @classmethod
    def from_input(cls, raw: dict | None) -> ActorConfig:
        """Parse Apify Actor input dict into a validated ActorConfig."""
        raw = raw or {}

        start_urls_raw = raw.get("startUrls", [])
        start_urls: list[str] = []
        for item in start_urls_raw:
            if isinstance(item, dict):
                url = item.get("url", "")
                if url:
                    start_urls.append(str(url))
            elif item:
                start_urls.append(str(item))

        sitemap_url = raw.get("sitemapUrl") or None
        if sitemap_url == "":
            sitemap_url = None

        max_pages = raw.get("maxPages", 100)
        if not isinstance(max_pages, int) or max_pages < 1 or max_pages > 100_000:
            raise ValueError(
                f"maxPages must be an integer between 1 and 100000, got {max_pages!r}"
            )

        min_text_length = raw.get("minTextLength", 100)
        if not isinstance(min_text_length, int) or min_text_length < 0:
            raise ValueError(
                f"minTextLength must be a non-negative integer, got {min_text_length!r}"
            )

        language = raw.get("language") or None
        if language == "":
            language = None

        deduplicate = raw.get("deduplicate", True)
        if not isinstance(deduplicate, bool):
            raise ValueError(f"deduplicate must be a boolean, got {deduplicate!r}")

        proxy_configuration = raw.get("proxyConfiguration")
        if proxy_configuration is not None and not isinstance(proxy_configuration, dict):
            raise ValueError(
                f"proxyConfiguration must be an object, got {type(proxy_configuration).__name__!r}"
            )

        max_concurrency = raw.get("maxConcurrency", 10)
        if not isinstance(max_concurrency, int) or max_concurrency < 1 or max_concurrency > 200:
            raise ValueError(
                f"maxConcurrency must be an integer between 1 and 200, got {max_concurrency!r}"
            )

        crawl_strategy = raw.get("crawlStrategy", "recurse")
        if crawl_strategy not in CRAWL_STRATEGIES:
            raise ValueError(
                f"crawlStrategy must be one of {CRAWL_STRATEGIES}, got {crawl_strategy!r}"
            )

        stay_within_domain = raw.get("stayWithinDomain", True)
        if not isinstance(stay_within_domain, bool):
            raise ValueError(
                f"stayWithinDomain must be a boolean, got {stay_within_domain!r}"
            )

        include_url_globs = _parse_string_list(raw.get("includeUrlGlobs"), "includeUrlGlobs")
        exclude_url_globs = _parse_string_list(raw.get("excludeUrlGlobs"), "excludeUrlGlobs")

        max_sitemap_urls = raw.get("maxSitemapUrls")
        if max_sitemap_urls is None:
            pass
        elif not isinstance(max_sitemap_urls, int) or max_sitemap_urls < 1:
            raise ValueError(
                f"maxSitemapUrls must be a positive integer, got {max_sitemap_urls!r}"
            )

        min_request_delay_secs = raw.get("minRequestDelaySecs", 0)
        if not isinstance(min_request_delay_secs, (int, float)) or min_request_delay_secs < 0:
            raise ValueError(
                f"minRequestDelaySecs must be a non-negative number, got {min_request_delay_secs!r}"
            )

        max_fingerprints = raw.get("maxFingerprints", 50_000)
        if not isinstance(max_fingerprints, int) or max_fingerprints < 1:
            raise ValueError(
                f"maxFingerprints must be a positive integer, got {max_fingerprints!r}"
            )

        max_depth = raw.get("maxDepth")
        if max_depth is None:
            pass
        elif not isinstance(max_depth, int) or max_depth < 0:
            raise ValueError(
                f"maxDepth must be a non-negative integer, got {max_depth!r}"
            )

        export_rejected_pages = raw.get("exportRejectedPages", False)
        if not isinstance(export_rejected_pages, bool):
            raise ValueError(
                f"exportRejectedPages must be a boolean, got {export_rejected_pages!r}"
            )

        return cls(
            start_urls=start_urls,
            sitemap_url=sitemap_url,
            max_pages=max_pages,
            min_text_length=min_text_length,
            language=language,
            deduplicate=deduplicate,
            proxy_configuration=proxy_configuration,
            max_concurrency=max_concurrency,
            crawl_strategy=crawl_strategy,
            stay_within_domain=stay_within_domain,
            include_url_globs=include_url_globs,
            exclude_url_globs=exclude_url_globs,
            max_sitemap_urls=max_sitemap_urls,
            min_request_delay_secs=float(min_request_delay_secs),
            max_fingerprints=max_fingerprints,
            max_depth=max_depth,
            export_rejected_pages=export_rejected_pages,
        )

    @property
    def effective_max_sitemap_urls(self) -> int:
        """Resolved sitemap/seed URL cap (defaults to max_pages)."""
        return self.max_sitemap_urls if self.max_sitemap_urls is not None else self.max_pages
