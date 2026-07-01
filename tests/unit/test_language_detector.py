"""Tests for language detection."""

from src.extractors.language_detector import detect_language, extract_html_lang


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


def test_extract_html_lang_parses_iso_code():
    html = '<html lang="en-US"><body>Hello</body></html>'
    assert extract_html_lang(html) == "en"


def test_detect_language_uses_html_lang_for_short_text():
    html = '<html lang="en"><body>Short</body></html>'
    assert detect_language("Too short for langdetect", html) == "en"


def test_detect_language_identifies_english():
    assert detect_language(ENGLISH_TEXT) == "en"


def test_detect_language_identifies_german():
    assert detect_language(GERMAN_TEXT) == "de"


def test_detect_language_falls_back_to_html_lang(monkeypatch):
    from src.extractors import language_detector

    def raise_langs(_text):
        from langdetect import LangDetectException

        raise LangDetectException("error", "No features in text")

    monkeypatch.setattr(language_detector, "detect_langs", raise_langs)
    html = '<html lang="fr"><body>content</body></html>'
    assert detect_language(ENGLISH_TEXT, html) == "fr"


def test_detect_language_prefers_html_lang_over_trafilatura_for_short_text():
    html = '<html lang="en"><body>Short</body></html>'
    assert detect_language("Too short", html, trafilatura_lang="de") == "en"


def test_detect_language_uses_trafilatura_lang_when_html_missing():
    assert detect_language("Short", trafilatura_lang="de") == "de"


def test_detect_language_uses_lower_threshold_for_medium_text():
    medium = (
        "Machine learning is a subset of artificial intelligence that enables "
        "systems to learn from experience without explicit programming."
    )
    assert detect_language(medium) == "en"
