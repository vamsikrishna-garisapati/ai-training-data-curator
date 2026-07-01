"""URL helpers for crawl scope and link enqueue filtering."""

from __future__ import annotations

from urllib.parse import urlparse

from crawlee._utils.globs import Glob

from src.config import ActorConfig


def derive_allowed_hosts(urls: list[str]) -> set[str]:
    """Extract lowercase hostnames from seed URLs."""
    hosts: set[str] = set()
    for url in urls:
        hostname = urlparse(url).hostname
        if hostname:
            hosts.add(hostname.lower())
    return hosts


def parse_url_globs(glob_strings: list[str]) -> list[Glob]:
    """Convert user-provided glob strings to Crawlee Glob objects."""
    return [Glob(pattern) for pattern in glob_strings if pattern]


def host_include_globs(hosts: set[str]) -> list[Glob]:
    """Build include globs scoped to allowed seed hosts."""
    globs: list[Glob] = []
    for host in sorted(hosts):
        globs.append(Glob(f"https://{host}/**"))
        globs.append(Glob(f"http://{host}/**"))
    return globs


def build_enqueue_link_kwargs(
    config: ActorConfig,
    allowed_hosts: set[str],
) -> dict:
    """Build keyword arguments for context.enqueue_links when recursing."""
    include_globs = parse_url_globs(config.include_url_globs)
    exclude_globs = parse_url_globs(config.exclude_url_globs)

    kwargs: dict = {"strategy": "all"}

    if config.stay_within_domain and allowed_hosts:
        include_globs = host_include_globs(allowed_hosts) + include_globs

    if include_globs:
        kwargs["include"] = include_globs
    if exclude_globs:
        kwargs["exclude"] = exclude_globs

    return kwargs


def cap_seed_urls(urls: list[str], limit: int) -> list[str]:
    """Return at most ``limit`` seed URLs preserving order."""
    if limit < 1:
        return []
    return urls[:limit]
