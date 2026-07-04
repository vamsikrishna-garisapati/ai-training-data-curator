"""Shared Actor constants."""

# Stable public HTML page for demos and Apify automated daily checks.
DEFAULT_START_URL = "https://httpbin.org/html"
APIFY_SMOKE_START_URL = DEFAULT_START_URL

# Key-value store record for run statistics (no leading '#' — breaks KV PUT URLs).
SUMMARY_KEY = "SUMMARY"

# Sitemap fetch safety limits.
MAX_SITEMAP_RESPONSE_BYTES = 10 * 1024 * 1024
MAX_SITEMAP_URLS = 100_000
