"""Shared pytest fixtures."""

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def article_html() -> str:
    return (FIXTURES_DIR / "article.html").read_text(encoding="utf-8")


@pytest.fixture
def sitemap_xml() -> str:
    return (FIXTURES_DIR / "sitemap.xml").read_text(encoding="utf-8")
