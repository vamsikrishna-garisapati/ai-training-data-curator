"""Actor input configuration parsing and validation."""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

CRAWL_STRATEGIES = ("recurse", "seeds-only")


def _parse_string_list(raw: object, field_name: str) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        logger.warning("%s must be an array of strings; using [].", field_name)
        return []
    result: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            logger.warning("%s must be an array of strings; skipping invalid entry.", field_name)
            continue
        if item:
            result.append(item)
    return result


def _coerce_int(
    value: object,
    *,
    default: int,
    minimum: int,
    maximum: int,
    field_name: str,
) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        logger.warning(
            "%s must be an integer between %s and %s; using %s (got %r).",
            field_name,
            minimum,
            maximum,
            default,
            value,
        )
        return default
    if value < minimum or value > maximum:
        clamped = max(minimum, min(maximum, value))
        logger.warning(
            "%s out of range; clamped %r to %s.",
            field_name,
            value,
            clamped,
        )
        return clamped
    return value


def _coerce_bool(value: object, *, default: bool, field_name: str) -> bool:
    if not isinstance(value, bool):
        logger.warning("%s must be a boolean; using %s (got %r).", field_name, default, value)
        return default
    return value


def _coerce_float_nonneg(value: object, *, default: float, field_name: str) -> float:
    if not isinstance(value, (int, float)) or value < 0:
        logger.warning(
            "%s must be a non-negative number; using %s (got %r).",
            field_name,
            default,
            value,
        )
        return default
    return float(value)


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
        """Parse Apify Actor input; invalid fields are coerced with warnings (never raises)."""
        raw = raw or {}

        start_urls_raw = raw.get("startUrls", [])
        start_urls: list[str] = []
        if not isinstance(start_urls_raw, list):
            logger.warning("startUrls must be an array; using [].")
            start_urls_raw = []
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
        elif sitemap_url is not None and not isinstance(sitemap_url, str):
            logger.warning("sitemapUrl must be a string; ignoring.")
            sitemap_url = None

        max_pages = _coerce_int(
            raw.get("maxPages", 10),
            default=10,
            minimum=1,
            maximum=100_000,
            field_name="maxPages",
        )

        min_text_length = _coerce_int(
            raw.get("minTextLength", 100),
            default=100,
            minimum=0,
            maximum=1_000_000,
            field_name="minTextLength",
        )

        language = raw.get("language") or None
        if language == "":
            language = None
        elif language is not None and not isinstance(language, str):
            logger.warning("language must be a string; ignoring.")
            language = None

        deduplicate = _coerce_bool(raw.get("deduplicate", True), default=True, field_name="deduplicate")

        proxy_configuration = raw.get("proxyConfiguration")
        if proxy_configuration is not None and not isinstance(proxy_configuration, dict):
            logger.warning("proxyConfiguration must be an object; ignoring.")
            proxy_configuration = None

        max_concurrency = _coerce_int(
            raw.get("maxConcurrency", 10),
            default=10,
            minimum=1,
            maximum=200,
            field_name="maxConcurrency",
        )

        crawl_strategy = raw.get("crawlStrategy", "seeds-only")
        if crawl_strategy not in CRAWL_STRATEGIES:
            logger.warning(
                "crawlStrategy must be one of %s; using 'seeds-only' (got %r).",
                CRAWL_STRATEGIES,
                crawl_strategy,
            )
            crawl_strategy = "seeds-only"

        stay_within_domain = _coerce_bool(
            raw.get("stayWithinDomain", True),
            default=True,
            field_name="stayWithinDomain",
        )

        include_url_globs = _parse_string_list(raw.get("includeUrlGlobs"), "includeUrlGlobs")
        exclude_url_globs = _parse_string_list(raw.get("excludeUrlGlobs"), "excludeUrlGlobs")

        max_sitemap_urls = raw.get("maxSitemapUrls")
        if max_sitemap_urls is None:
            pass
        elif not isinstance(max_sitemap_urls, int) or max_sitemap_urls < 1:
            logger.warning("maxSitemapUrls must be a positive integer; ignoring.")
            max_sitemap_urls = None

        min_request_delay_secs = _coerce_float_nonneg(
            raw.get("minRequestDelaySecs", 0),
            default=0.0,
            field_name="minRequestDelaySecs",
        )

        max_fingerprints = _coerce_int(
            raw.get("maxFingerprints", 50_000),
            default=50_000,
            minimum=1,
            maximum=10_000_000,
            field_name="maxFingerprints",
        )

        max_depth = raw.get("maxDepth")
        if max_depth is None:
            pass
        elif not isinstance(max_depth, int) or max_depth < 0:
            logger.warning("maxDepth must be a non-negative integer; ignoring.")
            max_depth = None

        export_rejected_pages = _coerce_bool(
            raw.get("exportRejectedPages", False),
            default=False,
            field_name="exportRejectedPages",
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
            min_request_delay_secs=min_request_delay_secs,
            max_fingerprints=max_fingerprints,
            max_depth=max_depth,
            export_rejected_pages=export_rejected_pages,
        )

    @property
    def effective_max_sitemap_urls(self) -> int:
        """Resolved sitemap/seed URL cap (defaults to max_pages)."""
        return self.max_sitemap_urls if self.max_sitemap_urls is not None else self.max_pages
