"""Tests for language and length filters."""

from src.filters.language_filter import passes_language
from src.filters.length_filter import passes_length

ENGLISH_TEXT = (
    "Machine learning is a subset of artificial intelligence that enables "
    "systems to learn and improve from experience without being explicitly "
    "programmed. It focuses on developing computer programs."
)

GERMAN_TEXT = (
    "Maschinelles Lernen ist ein Teilgebiet der künstlichen Intelligenz, "
    "das Systeme in die Lage versetzt, aus Erfahrungen zu lernen und sich "
    "zu verbessern, ohne explizit programmiert zu werden."
)


def test_english_passes_en_filter():
    assert passes_language(ENGLISH_TEXT, "en") is True


def test_german_rejected_by_en_filter():
    assert passes_language(GERMAN_TEXT, "en") is False


def test_no_language_filter_accepts_all():
    assert passes_language(GERMAN_TEXT, None) is True
    assert passes_language(ENGLISH_TEXT, None) is True


def test_empty_text_fails_language_filter():
    assert passes_language("", "en") is False
    assert passes_language("   ", "en") is False


def test_undetectable_language_fails_filter(monkeypatch):
    from src.extractors import language_detector

    def raise_detect(_text, _html=""):
        return None

    monkeypatch.setattr(language_detector, "detect_language", raise_detect)
    assert passes_language("some text here", "en") is False


def test_passes_length_above_minimum():
    assert passes_length("hello world", 5) is True


def test_passes_length_below_minimum():
    assert passes_length("hi", 10) is False


def test_passes_length_exact_minimum():
    assert passes_length("12345", 5) is True


def test_passes_length_zero_minimum():
    assert passes_length("", 0) is True
