#!/usr/bin/env python3
"""Verify Apify daily-check prefill path without network or scraped HTML fixtures."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import ActorConfig  # noqa: E402
from src.crawler import process_page  # noqa: E402
from tests.smoke_html import APIFY_DAILY_CHECK_HTML  # noqa: E402


def main() -> int:
    input_schema = json.loads((ROOT / ".actor/input_schema.json").read_text())
    props = input_schema["properties"]

    prefill_urls = props["startUrls"]["prefill"]
    prefill = {
        "startUrls": prefill_urls,
        "maxPages": props["maxPages"]["prefill"],
        "minTextLength": props["minTextLength"]["prefill"],
        "crawlStrategy": props["crawlStrategy"]["prefill"],
    }
    if "deduplicate" in props and "prefill" in props["deduplicate"]:
        prefill["deduplicate"] = props["deduplicate"]["prefill"]

    config = ActorConfig.from_input(prefill)
    url = prefill_urls[0]["url"]
    record, reason = process_page(APIFY_DAILY_CHECK_HTML, url, config, None, None)

    if record is None:
        print(f"DAILY CHECK WOULD FAIL: prefill page filtered ({reason})", file=sys.stderr)
        return 1

    print(
        f"Daily check OK: url={url} words={record.get('wordCount')} "
        f"text_len={len(record.get('text', ''))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
