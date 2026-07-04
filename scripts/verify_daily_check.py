#!/usr/bin/env python3
"""Verify Apify daily-check prefill path (synthetic + live httpbin fetch)."""

from __future__ import annotations

import sys
from pathlib import Path

import httpx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ActorConfig  # noqa: E402
from src.crawler import process_page  # noqa: E402
from tests.prefill import load_prefill_input  # noqa: E402
from tests.smoke_html import APIFY_DAILY_CHECK_HTML  # noqa: E402


def _verify_pipeline(html: str, url: str, config: ActorConfig, label: str) -> int:
    record, reason = process_page(html, url, config, None, None)
    if record is None:
        print(
            f"DAILY CHECK WOULD FAIL ({label}): prefill page filtered ({reason})",
            file=sys.stderr,
        )
        return 1

    print(
        f"{label} OK: url={url} words={record.get('wordCount')} "
        f"text_len={len(record.get('text', ''))}"
    )
    return 0


def main() -> int:
    prefill = load_prefill_input()
    config = ActorConfig.from_input(prefill)
    url = prefill["startUrls"][0]["url"]

    exit_code = _verify_pipeline(APIFY_DAILY_CHECK_HTML, url, config, "Synthetic")

    try:
        response = httpx.get(url, timeout=30.0, follow_redirects=True)
        response.raise_for_status()
    except httpx.HTTPError as exc:
        print(
            f"WARNING: Could not fetch live seed URL {url}: {exc}. "
            "Synthetic check passed; live check skipped.",
            file=sys.stderr,
        )
        return exit_code

    live_code = _verify_pipeline(response.text, url, config, "Live")
    return exit_code or live_code


if __name__ == "__main__":
    raise SystemExit(main())
