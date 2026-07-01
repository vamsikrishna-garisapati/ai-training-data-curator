"""Tests for quality filter."""

from src.filters.quality_filter import passes_quality


def test_passes_quality_accepts_article_text():
    text = (
        "Machine learning is a subset of artificial intelligence that enables systems "
        "to learn and improve from experience without being explicitly programmed. "
        "It focuses on developing computer programs that can access data and use it "
        "to learn for themselves through pattern recognition and statistical modeling."
    )
    assert passes_quality(text) is True


def test_rejects_nav_boilerplate():
    text = "\n".join([
        "Books to Scrape",
        "We love being scraped!",
        "Home",
        "Books",
        "Travel",
        "Mystery",
        "Historical Fiction",
        "Sequential Art",
        "In stock",
        "Add to basket",
    ] * 3)
    assert passes_quality(text) is False


def test_rejects_too_few_words():
    assert passes_quality("Short nav page with few words here.") is False
