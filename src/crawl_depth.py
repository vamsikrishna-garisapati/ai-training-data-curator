"""Crawl depth tracking via Crawlee request user_data."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from crawlee import Request, RequestOptions

DEPTH_USER_DATA_KEY = "depth"
REJECTED_DATASET_NAME = "rejected"


def get_request_depth(user_data: Mapping[str, Any] | None) -> int:
    """Return the link depth stored on a request (seeds default to 0)."""
    if not user_data:
        return 0
    depth = user_data.get(DEPTH_USER_DATA_KEY, 0)
    if isinstance(depth, bool):
        return 0
    try:
        return max(0, int(depth))
    except (TypeError, ValueError):
        return 0


def should_follow_links(current_depth: int, max_depth: int | None) -> bool:
    """Return True when child links may be enqueued from the current depth."""
    if max_depth is None:
        return True
    return current_depth < max_depth


def build_seed_requests(urls: list[str]) -> list[Request]:
    """Wrap seed URLs as Crawlee requests at depth 0."""
    return [
        Request.from_url(url, user_data={DEPTH_USER_DATA_KEY: 0})
        for url in urls
    ]


def depth_transform_request(current_depth: int):
    """Return a transform that sets child link depth to current_depth + 1."""

    def transform(request_options: RequestOptions) -> RequestOptions:
        user_data = dict(request_options.get("user_data") or {})
        user_data[DEPTH_USER_DATA_KEY] = current_depth + 1
        request_options["user_data"] = user_data
        return request_options

    return transform
