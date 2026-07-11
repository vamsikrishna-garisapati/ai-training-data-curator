"""Shared Actor constants."""

# Repo-hosted HTML for demos and Apify automated daily checks (stable, not a third-party demo host).
DEFAULT_START_URL = (
    "https://raw.githubusercontent.com/vamsikrishna-garisapati/"
    "ai-training-data-curator/main/fixtures/daily_check.html"
)
APIFY_SMOKE_START_URL = DEFAULT_START_URL

# Key-value store record for run statistics (no leading '#' — breaks KV PUT URLs).
SUMMARY_KEY = "SUMMARY"

# Sitemap fetch safety limits.
MAX_SITEMAP_RESPONSE_BYTES = 10 * 1024 * 1024
MAX_SITEMAP_URLS = 100_000
