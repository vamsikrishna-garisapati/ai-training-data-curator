"""Actor input configuration parsing and validation."""

from __future__ import annotations

import logging
from collections.abc import Callable
from dataclasses import dataclass

from src.url_validation import is_valid_http_url

logger = logging.getLogger(__name__)

CRAWL_STRATEGIES = ("recurse", "seeds-only")
WarnFn = Callable[..., None]


def _resolve_warn(warn: WarnFn | None) -> WarnFn:
    return warn if warn is not None else logger.warning


def _parse_string_list(
    raw: object,
    field_name: str,
    *,
    warn: WarnFn,
) -> list[str]:
    if raw is None:
        return []
    if not isinstance(raw, list):
        warn("%s must be an array of strings; using [].", field_name)
        return []
    result: list[str] = []
    for item in raw:
        if not isinstance(item, str):
            warn("%s must be an array of strings; skipping invalid entry.", field_name)
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
    warn: WarnFn,
) -> int:
    if isinstance(value, bool):
        warn(
            "%s must be an integer between %s and %s; using %s (got %r).",
            field_name,
            minimum,
            maximum,
            default,
            value,
        )
        return default
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if not isinstance(value, int):
        warn(
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
        warn(
            "%s out of range; clamped %r to %s.",
            field_name,
            value,
            clamped,
        )
        return clamped
    return value


def _coerce_optional_positive_int(
    value: object,
    *,
    minimum: int,
    maximum: int,
    field_name: str,
    warn: WarnFn,
) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        warn("%s must be a positive integer; ignoring.", field_name)
        return None
    if isinstance(value, float) and value.is_integer():
        value = int(value)
    if not isinstance(value, int) or value < minimum or value > maximum:
        warn(
            "%s must be a positive integer between %s and %s; ignoring.",
            field_name,
            minimum,
            maximum,
        )
        return None
    return value


def _coerce_bool(value: object, *, default: bool, field_name: str, warn: WarnFn) -> bool:
    if not isinstance(value, bool):
        warn("%s must be a boolean; using %s (got %r).", field_name, default, value)
        return default
    return value


def _coerce_float_nonneg(value: object, *, default: float, field_name: str, warn: WarnFn) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool) or value < 0:
        warn(
            "%s must be a non-negative number; using %s (got %r).",
            field_name,
            default,
            value,
        )
        return default
    return float(value)


def _parse_http_url(value: object, field_name: str, *, warn: WarnFn) -> str | None:
    if value is None or value == "":
        return None
    if not isinstance(value, str):
        warn("%s must be a string; ignoring.", field_name)
        return None
    if not is_valid_http_url(value):
        warn("%s must be an http(s) URL with a host; ignoring %r.", field_name, value)
        return None
    return value.strip()


def _parse_start_urls(raw: object, *, warn: WarnFn) -> list[str]:
    start_urls: list[str] = []
    if not isinstance(raw, list):
        warn("startUrls must be an array; using [].")
        return start_urls
    for item in raw:
        candidate: str | None = None
        if isinstance(item, dict):
            url = item.get("url", "")
            if url:
                candidate = str(url)
        elif item:
            candidate = str(item)
        if candidate is None:
            continue
        if is_valid_http_url(candidate):
            start_urls.append(candidate.strip())
        else:
            warn("startUrls entry must be an http(s) URL with a host; skipping %r.", candidate)
    return start_urls


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
    def from_input(cls, raw: dict | None, *, warn: WarnFn | None = None) -> ActorConfig:
        """Parse Apify Actor input; invalid fields are coerced with warnings (never raises)."""
        raw = raw or {}
        log_warn = _resolve_warn(warn)

        start_urls = _parse_start_urls(raw.get("startUrls", []), warn=log_warn)

        sitemap_url = _parse_http_url(raw.get("sitemapUrl"), "sitemapUrl", warn=log_warn)

        max_pages = _coerce_int(
            raw.get("maxPages", 10),
            default=10,
            minimum=1,
            maximum=100_000,
            field_name="maxPages",
            warn=log_warn,
        )

        min_text_length = _coerce_int(
            raw.get("minTextLength", 100),
            default=100,
            minimum=0,
            maximum=1_000_000,
            field_name="minTextLength",
            warn=log_warn,
        )

        language = raw.get("language") or None
        if language == "":
            language = None
        elif language is not None and not isinstance(language, str):
            log_warn("language must be a string; ignoring.")
            language = None

        deduplicate = _coerce_bool(
            raw.get("deduplicate", True),
            default=True,
            field_name="deduplicate",
            warn=log_warn,
        )

        proxy_configuration = raw.get("proxyConfiguration")
        if proxy_configuration is not None and not isinstance(proxy_configuration, dict):
            log_warn("proxyConfiguration must be an object; ignoring.")
            proxy_configuration = None

        max_concurrency = _coerce_int(
            raw.get("maxConcurrency", 10),
            default=10,
            minimum=1,
            maximum=200,
            field_name="maxConcurrency",
            warn=log_warn,
        )

        crawl_strategy = raw.get("crawlStrategy", "seeds-only")
        if crawl_strategy not in CRAWL_STRATEGIES:
            log_warn(
                "crawlStrategy must be one of %s; using 'seeds-only' (got %r).",
                CRAWL_STRATEGIES,
                crawl_strategy,
            )
            crawl_strategy = "seeds-only"

        stay_within_domain = _coerce_bool(
            raw.get("stayWithinDomain", True),
            default=True,
            field_name="stayWithinDomain",
            warn=log_warn,
        )

        include_url_globs = _parse_string_list(
            raw.get("includeUrlGlobs"),
            "includeUrlGlobs",
            warn=log_warn,
        )
        exclude_url_globs = _parse_string_list(
            raw.get("excludeUrlGlobs"),
            "excludeUrlGlobs",
            warn=log_warn,
        )

        max_sitemap_urls = _coerce_optional_positive_int(
            raw.get("maxSitemapUrls"),
            minimum=1,
            maximum=100_000,
            field_name="maxSitemapUrls",
            warn=log_warn,
        )

        min_request_delay_secs = _coerce_float_nonneg(
            raw.get("minRequestDelaySecs", 0),
            default=0.0,
            field_name="minRequestDelaySecs",
            warn=log_warn,
        )

        max_fingerprints = _coerce_int(
            raw.get("maxFingerprints", 50_000),
            default=50_000,
            minimum=1,
            maximum=10_000_000,
            field_name="maxFingerprints",
            warn=log_warn,
        )

        max_depth_raw = raw.get("maxDepth")
        max_depth = None
        if max_depth_raw is not None:
            if isinstance(max_depth_raw, bool):
                log_warn("maxDepth must be a non-negative integer; ignoring.")
            else:
                if isinstance(max_depth_raw, float) and max_depth_raw.is_integer():
                    max_depth_raw = int(max_depth_raw)
                if isinstance(max_depth_raw, int) and max_depth_raw >= 0:
                    max_depth = max_depth_raw
                else:
                    log_warn("maxDepth must be a non-negative integer; ignoring.")

        export_rejected_pages = _coerce_bool(
            raw.get("exportRejectedPages", False),
            default=False,
            field_name="exportRejectedPages",
            warn=log_warn,
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
