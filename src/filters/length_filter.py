"""Minimum text length filtering."""

from __future__ import annotations


def passes_length(text: str, min_len: int) -> bool:
    """Return True if text meets the minimum character length."""
    return len(text) >= min_len
