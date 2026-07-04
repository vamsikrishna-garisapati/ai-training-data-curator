"""Load Apify input_schema.json prefill values for daily-check tests."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def load_prefill_input() -> dict:
    """Return the input dict Apify uses for automated daily health checks."""
    input_schema = json.loads((ROOT / ".actor/input_schema.json").read_text())
    props = input_schema["properties"]
    prefill: dict = {
        "startUrls": props["startUrls"]["prefill"],
        "maxPages": props["maxPages"]["prefill"],
        "minTextLength": props["minTextLength"]["prefill"],
        "crawlStrategy": props["crawlStrategy"]["prefill"],
    }
    for key in ("deduplicate", "maxConcurrency"):
        if key in props and "prefill" in props[key]:
            prefill[key] = props[key]["prefill"]
    return prefill
