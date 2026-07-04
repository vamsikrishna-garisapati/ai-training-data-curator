"""Text extraction using Trafilatura with readability-lxml fallback."""

from __future__ import annotations

import re

from readability import Document
from trafilatura import bare_extraction

from src.extractors.language_detector import detect_language

DEFAULT_MIN_TEXT_LENGTH = 50


def _word_count(text: str) -> int:
    return len(text.split())


def _strip_html(html: str) -> str:
    text = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", text).strip()


def extract_page(
    html: str,
    url: str,
    min_text_length: int = DEFAULT_MIN_TEXT_LENGTH,
) -> dict | None:
    """Extract title, text, author, date, language, and word count from HTML."""
    document = bare_extraction(html, url=url, with_metadata=True)

    title: str | None = None
    text: str | None = None
    author: str | None = None
    published_date: str | None = None
    trafilatura_lang: str | None = None

    if document is not None:
        data = document.as_dict()
        title = data.get("title") or None
        text = data.get("text") or data.get("raw_text") or None
        author = data.get("author") or None
        published_date = data.get("date") or None
        trafilatura_lang = data.get("language") or None

    if not text or len(text) < min_text_length:
        doc = Document(html)
        fallback_title = doc.title()
        fallback_html = doc.summary()
        fallback_text = _strip_html(fallback_html)
        if fallback_text:
            text = fallback_text
            if not title and fallback_title:
                title = fallback_title

    if not text:
        return None

    language = detect_language(text, html, trafilatura_lang=trafilatura_lang)

    return {
        "url": url,
        "title": title or "",
        "text": text,
        "author": author or "",
        "publishedDate": published_date or "",
        "language": language or "",
        "wordCount": _word_count(text),
    }
