"""Language detection with HTML lang fallback and confidence threshold."""

from __future__ import annotations

import re

from langdetect import LangDetectException, detect_langs

MIN_LANG_DETECT_LENGTH = 50
LONG_TEXT_LENGTH = 100
LANG_CONFIDENCE_THRESHOLD = 0.8
LANG_CONFIDENCE_THRESHOLD_SHORT = 0.6


def extract_html_lang(html: str) -> str | None:
    """Extract ISO 639-1 language code from the HTML lang attribute."""
    match = re.search(r'<html[^>]*\blang=["\']([^"\']+)["\']', html, re.I)
    if not match:
        return None
    lang = match.group(1).strip().split("-")[0].lower()
    if re.fullmatch(r"[a-z]{2}", lang):
        return lang
    return None


def _normalize_lang_code(lang: str | None) -> str | None:
    if not lang:
        return None
    code = lang.strip().split("-")[0].lower()
    if re.fullmatch(r"[a-z]{2}", code):
        return code
    return None


def detect_language(
    text: str,
    html: str = "",
    trafilatura_lang: str | None = None,
) -> str | None:
    """Detect page language using metadata hints and langdetect."""
    html_lang = extract_html_lang(html) if html else None
    meta_lang = _normalize_lang_code(trafilatura_lang)

    if not text or not text.strip():
        return html_lang or meta_lang

    stripped = text.strip()
    if len(stripped) < MIN_LANG_DETECT_LENGTH:
        return html_lang or meta_lang

    threshold = (
        LANG_CONFIDENCE_THRESHOLD
        if len(stripped) >= LONG_TEXT_LENGTH
        else LANG_CONFIDENCE_THRESHOLD_SHORT
    )

    try:
        langs = detect_langs(text)
        if langs and langs[0].prob >= threshold:
            return langs[0].lang
    except LangDetectException:
        pass

    return html_lang or meta_lang
