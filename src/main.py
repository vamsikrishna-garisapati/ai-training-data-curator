"""Apify Actor entrypoint."""

from __future__ import annotations

import asyncio

import httpx
from apify import Actor

from src.config import ActorConfig
from src.constants import DEFAULT_START_URL, SUMMARY_KEY
from src.crawler import build_crawler
from src.dedup.simhash_dedup import Deduplicator
from src.crawl_depth import build_seed_requests
from src.sitemap import fetch_sitemap_urls
from src.stats import CrawlStats
from src.urls import cap_seed_urls, derive_allowed_hosts


def _dedupe_urls(urls: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for url in urls:
        normalized = url.rstrip("/")
        if normalized not in seen:
            seen.add(normalized)
            result.append(url)
    return result


async def _write_summary(
    stats: CrawlStats,
    max_pages: int,
    final_stats=None,
) -> None:
    try:
        await Actor.set_value(
            SUMMARY_KEY,
            stats.to_summary(max_pages, final_stats),
            content_type="application/json",
        )
    except Exception as exc:
        Actor.log.warning(
            "Could not write run summary to key-value store (%s). "
            "This is expected under limited-permission runs.",
            exc,
        )


async def main() -> None:
    stats = CrawlStats()
    max_pages = 10
    final_stats = None

    async with Actor:
        try:
            raw = await Actor.get_input() or {}
            config = ActorConfig.from_input(raw)
            max_pages = config.max_pages

            deduplicator = (
                Deduplicator(max_fingerprints=config.max_fingerprints)
                if config.deduplicate
                else None
            )

            seed_urls = list(config.start_urls)
            if config.sitemap_url:
                try:
                    async with httpx.AsyncClient(timeout=30.0) as client:
                        seed_urls.extend(
                            await fetch_sitemap_urls(config.sitemap_url, client)
                        )
                except httpx.HTTPError as exc:
                    Actor.log.warning(
                        "Failed to fetch sitemap %s: %s. Continuing with startUrls only.",
                        config.sitemap_url,
                        exc,
                    )
                except Exception as exc:
                    Actor.log.warning(
                        "Unexpected sitemap error for %s: %s. Continuing with startUrls only.",
                        config.sitemap_url,
                        exc,
                    )

            seed_urls = _dedupe_urls(seed_urls)
            seed_urls = cap_seed_urls(seed_urls, config.effective_max_sitemap_urls)

            if not seed_urls:
                Actor.log.warning(
                    "No seed URLs provided; using default start URL %s.",
                    DEFAULT_START_URL,
                )
                seed_urls = [DEFAULT_START_URL]

            allowed_hosts = derive_allowed_hosts(seed_urls)

            proxy_configuration = None
            if config.proxy_configuration is not None:
                try:
                    proxy_configuration = await Actor.create_proxy_configuration(
                        actor_proxy_input=config.proxy_configuration,
                    )
                except Exception as exc:
                    Actor.log.warning(
                        "Proxy configuration failed (%s); continuing without proxy.",
                        exc,
                    )

            crawler = build_crawler(
                config,
                deduplicator,
                proxy_configuration,
                stats,
                allowed_hosts,
            )
            final_stats = await crawler.run(build_seed_requests(seed_urls))

            if stats.saved == 0:
                Actor.log.warning(
                    "Run finished with zero saved records (crawled=%d failed=%d). "
                    "Check filters, seed URLs, or site availability.",
                    stats.crawled,
                    stats.failed,
                )

            Actor.log.info(
                "Crawl complete. Crawled=%d saved=%d failed=%d maxPages=%d",
                stats.crawled,
                stats.saved,
                stats.failed,
                config.max_pages,
            )
        except Exception as exc:
            Actor.log.exception("Unhandled error during crawl: %s", exc)
            stats.failed += 1
        finally:
            await _write_summary(stats, max_pages, final_stats)


if __name__ == "__main__":
    asyncio.run(main())
