"""Tests for crawl depth helpers."""

from src.crawl_depth import (
    DEPTH_USER_DATA_KEY,
    build_seed_requests,
    depth_transform_request,
    get_request_depth,
    should_follow_links,
)


def test_get_request_depth_defaults_to_zero():
    assert get_request_depth(None) == 0
    assert get_request_depth({}) == 0


def test_get_request_depth_reads_user_data():
    assert get_request_depth({DEPTH_USER_DATA_KEY: 2}) == 2


def test_should_follow_links_unlimited():
    assert should_follow_links(5, None) is True


def test_should_follow_links_respects_max():
    assert should_follow_links(0, 2) is True
    assert should_follow_links(2, 2) is False
    assert should_follow_links(3, 2) is False


def test_build_seed_requests_set_depth_zero():
    requests = build_seed_requests(["https://example.com/a", "https://example.com/b"])
    assert len(requests) == 2
    assert all(get_request_depth(r.user_data) == 0 for r in requests)


def test_depth_transform_increments_child_depth():
    transform = depth_transform_request(1)
    result = transform({"url": "https://example.com/child"})
    assert result["user_data"][DEPTH_USER_DATA_KEY] == 2
