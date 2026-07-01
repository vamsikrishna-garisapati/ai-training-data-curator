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


def test_rejects_many_unique_prices_listing_style():
    text = (
        "Books catalog with many products. "
        + " ".join(f"Item {i} costs £{10 + i}.99 and ships fast." for i in range(8))
        + " Browse our categories and add items to your basket today."
    )
    assert passes_quality(text) is False


def test_accepts_product_detail_with_few_prices():
    text = (
        "A Light in the Attic product page with a detailed description for readers. "
        "£51.77\n"
        "In stock (22 available)\n"
        "Product Description\n"
        "It's hard to imagine a world without A Light in the Attic. "
        "This now-classic collection of poetry and drawings from Shel Silverstein "
        "celebrates its 20th anniversary with this special edition. "
        "Silverstein's humorous and creative verse can amuse readers of all ages. "
        "The book includes memorable poems about childhood, imagination, and play. "
        "Readers return to these poems again and again for comfort and laughter. "
        "Teachers and parents often recommend this title for classroom reading lists. "
        "Each poem invites children to think creatively about everyday situations."
    )
    assert passes_quality(text) is True


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
