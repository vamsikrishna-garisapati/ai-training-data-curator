"""Apify Actor entrypoint."""

from __future__ import annotations

import asyncio

import httpx
from apify import Actor

from src.config import ActorConfig
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


async def main() -> None:
    async with Actor:
        raw = await Actor.get_input() or {}
        try:
            config = ActorConfig.from_input(raw)
        except ValueError as exc:
            await Actor.fail(status_message=f"Invalid input: {exc}")
            return

        deduplicator = (
            Deduplicator(max_fingerprints=config.max_fingerprints)
            if config.deduplicate
            else None
        )
        stats = CrawlStats()

        seed_urls = list(config.start_urls)
        if config.sitemap_url:
            try:
                async with httpx.AsyncClient() as client:
                    seed_urls.extend(
                        await fetch_sitemap_urls(config.sitemap_url, client)
                    )
            except httpx.HTTPError as exc:
                Actor.log.warning(
                    "Failed to fetch sitemap %s: %s. Continuing with startUrls only.",
                    config.sitemap_url,
                    exc,
                )

        seed_urls = _dedupe_urls(seed_urls)
        seed_urls = cap_seed_urls(seed_urls, config.effective_max_sitemap_urls)

        if not seed_urls:
            Actor.log.warning("No seed URLs provided; nothing to crawl.")
            return

        allowed_hosts = derive_allowed_hosts(seed_urls)

        proxy_configuration = await Actor.create_proxy_configuration(
            actor_proxy_input=config.proxy_configuration,
        )
        crawler = build_crawler(
            config,
            deduplicator,
            proxy_configuration,
            stats,
            allowed_hosts,
        )
        final_stats = await crawler.run(build_seed_requests(seed_urls))

        await Actor.set_value("#SUMMARY", stats.to_summary(config.max_pages, final_stats))
        Actor.log.info(
            "Crawl complete. Crawled=%d saved=%d failed=%d maxPages=%d",
            stats.crawled,
            stats.saved,
            stats.failed,
            config.max_pages,
        )


if __name__ == "__main__":
    asyncio.run(main())
