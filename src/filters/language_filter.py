"""Language filtering via shared language detector."""

from __future__ import annotations

from src.extractors.language_detector import detect_language


def passes_language(
    text: str,
    lang: str | None,
    html: str = "",
    *,
    detected_language: str | None = None,
) -> bool:
    """Return True if text matches the required ISO 639-1 language code."""
    if not lang:
        return True
    if not text or not text.strip():
        return False

    detected = (
        detected_language
        if detected_language is not None
        else detect_language(text, html)
    )
    if not detected:
        return False
    return detected.lower() == lang.lower()
