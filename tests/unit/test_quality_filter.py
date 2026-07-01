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


def test_accepts_long_doc_with_repeated_terms():
    """Long technical docs repeat domain terms; threshold scales down with length."""
    from src.filters.quality_filter import LONG_DOC_WORDS, _min_unique_ratio

    vocabulary = [f"term{i}" for i in range(200)]
    words: list[str] = []
    for i in range(600):
        words.append(vocabulary[i % 200])
        if i % 3 == 0:
            words.append("code")
        if i % 5 == 0:
            words.append("should")
    text = " ".join(
        f"Section {n}: {' '.join(words[n * 12 : (n + 1) * 12])}."
        for n in range(len(words) // 12)
    )
    tokens = text.split()
    assert len(tokens) >= LONG_DOC_WORDS
    unique_ratio = len({w.lower() for w in tokens}) / len(tokens)
    assert unique_ratio < 0.35
    assert unique_ratio >= _min_unique_ratio(len(tokens))
    assert passes_quality(text) is True
