"""Heuristic filter for navigation and listing boilerplate pages."""

from __future__ import annotations

import re

MIN_WORDS = 20
MIN_UNIQUE_RATIO = 0.35
MAX_SHORT_LINE_RATIO = 0.6
SHORT_LINE_CHARS = 25

NAV_KEYWORDS = frozenset(
    {
        "home",
        "menu",
        "login",
        "sign in",
        "sign up",
        "register",
        "cart",
        "basket",
        "checkout",
        "search",
        "categories",
        "category",
        "navigation",
        "breadcrumb",
        "add to basket",
        "add to cart",
        "in stock",
        "out of stock",
    }
)

PRICE_PATTERN = re.compile(
    r"(?:[$£€]\s?\d+|\d+\.\d{2}\s?(?:USD|EUR|GBP)?|price\s*:\s*\d+)",
    re.IGNORECASE,
)


def passes_quality(text: str) -> bool:
    """Return True if text looks like article content rather than nav/listing chrome."""
    stripped = text.strip()
    if len(stripped) < 50:
        return False

    words = stripped.split()
    if len(words) < MIN_WORDS:
        return False

    unique_ratio = len({word.lower() for word in words}) / len(words)
    if unique_ratio < MIN_UNIQUE_RATIO:
        return False

    lines = [line.strip() for line in stripped.splitlines() if line.strip()]
    if len(lines) > 3:
        short_lines = sum(1 for line in lines if len(line) < SHORT_LINE_CHARS)
        if short_lines / len(lines) > MAX_SHORT_LINE_RATIO:
            return False
        if len(set(lines)) / len(lines) < 0.5:
            return False

    lower = stripped.lower()
    nav_hits = sum(1 for keyword in NAV_KEYWORDS if keyword in lower)
    if nav_hits >= 4:
        return False

    if len(PRICE_PATTERN.findall(stripped)) >= 3:
        return False

    return True
