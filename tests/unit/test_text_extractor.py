"""Tests for text extraction."""

from src.extractors.language_detector import detect_language, extract_html_lang
from src.extractors.text_extractor import extract_page


def test_extract_html_lang_from_attribute():
    html = '<html lang="en-US"><body></body></html>'
    assert extract_html_lang(html) == "en"


def test_extract_html_lang_returns_none_when_missing():
    assert extract_html_lang("<html><body></body></html>") is None


def test_detect_language_uses_html_lang_fallback():
    html = '<html lang="de"><body></body></html>'
    assert detect_language("short", html) == "de"


def test_detect_language_skips_langdetect_for_short_text():
    assert detect_language("Too short for detection.") is None


def test_detect_language_with_confidence():
    text = (
        "Machine learning is a subset of artificial intelligence that enables systems "
        "to learn and improve from experience without being explicitly programmed. "
        "It focuses on developing computer programs that can access data and use it "
        "to learn for themselves through pattern recognition and statistical modeling."
    )
    assert detect_language(text) == "en"


def test_extract_page_from_fixture(article_html):
    result = extract_page(article_html, "https://books.toscrape.com/article")

    assert result is not None
    assert result["url"] == "https://books.toscrape.com/article"
    assert "Machine Learning" in result["title"] or "machine learning" in result["title"].lower()
    assert "machine learning" in result["text"].lower()
    assert result["wordCount"] > 50
    assert isinstance(result["language"], str)


def test_extract_page_returns_none_for_empty_html():
    result = extract_page("<html><body></body></html>", "https://books.toscrape.com/empty")
    assert result is None


def test_extract_page_includes_metadata_fields(article_html):
    result = extract_page(article_html, "https://books.toscrape.com/article")
    assert result is not None
    assert "title" in result
    assert "text" in result
    assert "author" in result
    assert "publishedDate" in result
    assert "language" in result
    assert "wordCount" in result


def test_extract_page_uses_html_lang(article_html):
    result = extract_page(article_html, "https://books.toscrape.com/article")
    assert result is not None
    assert result["language"] == "en"
