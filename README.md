# AI Training Data Curator

Transform public websites into clean, structured datasets for LLM fine-tuning, RAG, and ML workflows. This [Apify Actor](https://apify.com/actors) crawls seed URLs, extracts text and metadata, filters by language, length, and quality, deduplicates near-duplicate content, and exports records to the default Apify dataset.

## Features

- **Flexible seeding** — Start URLs and optional sitemap.xml (including sitemap indexes)
- **Clean extraction** — Trafilatura with readability-lxml fallback
- **Quality filtering** — Rejects navigation and listing boilerplate pages
- **Language filtering** — ISO 639-1 code gate with HTML `lang` fallback
- **Deduplication** — SimHash near-duplicate detection with LSH bucketing
- **Robots.txt compliance** — Respects website crawling policies
- **Apify Proxy** — Optional proxy configuration for blocked sites
- **Run summary** — Crawl statistics exported to key-value store (`#SUMMARY`)
- **Export** — JSONL or CSV via Apify dataset download

## Legal Notice

You are responsible for complying with each website's terms of service and applicable copyright law when crawling content. Only scrape sites you have permission to access and use the extracted data in accordance with applicable regulations.

## Input

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `startUrls` | array | `[{url: "https://books.toscrape.com"}]` | Seed URLs |
| `sitemapUrl` | string | — | Optional sitemap.xml URL (supports sitemap indexes) |
| `maxPages` | integer | 100 | Max pages to crawl (1–100,000) |
| `maxSitemapUrls` | integer | `maxPages` | Cap merged seed/sitemap URLs before crawling |
| `minTextLength` | integer | 100 | Minimum text length (characters) |
| `language` | string | — | ISO 639-1 filter; empty = all |
| `deduplicate` | boolean | true | Enable SimHash deduplication |
| `maxFingerprints` | integer | 50000 | Max SimHash fingerprints in memory (FIFO eviction) |
| `crawlStrategy` | string | `recurse` | `recurse` follows links; `seeds-only` crawls seeds only |
| `stayWithinDomain` | boolean | true | When recursing, only follow links on seed hostnames |
| `includeUrlGlobs` | string[] | `[]` | Optional URL globs; enqueued URLs must match at least one |
| `excludeUrlGlobs` | string[] | `[]` | Optional URL globs; matching URLs are never enqueued |
| `maxConcurrency` | integer | 10 | Max parallel page fetches (1–200) |
| `minRequestDelaySecs` | number | 0 | Minimum delay between requests (0 = no limit) |
| `maxDepth` | integer | — | Max link hops from seeds (`0` = seeds only; empty = unlimited) |
| `exportRejectedPages` | boolean | false | Write filtered URLs to a separate `rejected` dataset |
| `proxyConfiguration` | object | — | Apify proxy settings |

### Example Input

```json
{
  "startUrls": [{ "url": "https://books.toscrape.com" }],
  "maxPages": 50,
  "maxSitemapUrls": 50,
  "minTextLength": 200,
  "language": "en",
  "deduplicate": true,
  "maxFingerprints": 50000,
  "crawlStrategy": "recurse",
  "stayWithinDomain": true,
  "includeUrlGlobs": ["https://books.toscrape.com/**"],
  "excludeUrlGlobs": ["**/*.jpg"],
  "maxConcurrency": 10,
  "minRequestDelaySecs": 0,
  "maxDepth": 2,
  "exportRejectedPages": false,
  "proxyConfiguration": { "useApifyProxy": true }
}
```

### Rejected pages dataset

When `exportRejectedPages` is `true`, filtered URLs are written to a named dataset `rejected`:

```json
{
  "url": "https://books.toscrape.com/nav",
  "filterReason": "quality"
}
```

`filterReason` is one of: `extraction`, `language`, `length`, `quality`, `dedup`, `non_html`.

## Output

Each crawled page produces one dataset record:

```json
{
  "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
  "title": "A Light in the Attic",
  "text": "It's hard to imagine a world without A Light in the Attic. This now-classic collection of poetry and drawings from Shel Silverstein celebrates its 20th anniversary...",
  "author": "",
  "publishedDate": "",
  "language": "en",
  "wordCount": 142
}
```

### Run Summary

After each run, statistics are saved to the default key-value store under `#SUMMARY`:

```json
{
  "crawled": 50,
  "saved": 32,
  "filtered": {
    "extraction": 5,
    "language": 3,
    "length": 4,
    "quality": 2,
    "dedup": 4
  },
  "failed": 0,
  "maxPages": 50
}
```

## Exporting Data

Records are pushed to the default Apify dataset during the run. To export:

1. **Apify Console** — Open the run → Dataset tab → Download as JSON, JSONL, CSV, or Excel
2. **Apify API** — Use the [Dataset API](https://docs.apify.com/api/v2#/reference/datasets) with `format=json`, `format=jsonl`, or `format=csv`

## Local Development

### Prerequisites

- Python 3.11+
- [Apify CLI](https://docs.apify.com/cli) (optional, for `apify run`)

### Setup

```bash
python3.11 -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
```

### Run Tests

```bash
pytest --cov=src --cov-report=term-missing
```

### Run Locally

Use `--purge` to clear persisted request queues between runs:

```bash
apify run --purge --input='{"startUrls":[{"url":"https://books.toscrape.com"}],"maxPages":5}'
```

Or directly:

```bash
python -m src.main
```

Set input via Apify local storage or environment when running outside the Apify platform.

## Architecture

```
Input → Seed URLs (+ Sitemap) → BeautifulSoupCrawler
  → Trafilatura Extract → Language Filter → Length Filter → Quality Filter → SimHash Dedup
  → Dataset Push → Export (JSONL/CSV)
  → #SUMMARY to Key-Value Store
```

## Reliability

- **Apify daily checks** — Prefill input crawls a single product page (`maxPages: 5`, `seeds-only`) to finish within 5 minutes with a non-empty dataset ([Apify testing docs](https://docs.apify.com/platform/actors/publishing/testing))
- **Graceful input** — Invalid fields are coerced to safe defaults; runs do not fail on bad types
- **Default seed URL** — Empty `startUrls` falls back to a known public demo page
- **Retries** — Crawlee automatically retries failed requests (default: 3 retries)
- **Resume** — Interrupted runs can be resumed via Apify platform features
- **Robots.txt** — Enabled by default (`respect_robots_txt_file=True`)
- **Same-domain crawling** — `stayWithinDomain` restricts link following to seed hostnames
- **URL glob filters** — Optional `includeUrlGlobs` / `excludeUrlGlobs` for fine-grained crawl scope
- **Sitemap cap** — Merged seed URLs are capped via `maxSitemapUrls` (defaults to `maxPages`)
- **Non-HTML skip** — PDF, image, and other non-HTML responses skip extraction but can still enqueue links
- **Bounded dedup memory** — SimHash fingerprint store evicts oldest entries when `maxFingerprints` is exceeded
- **Crawl politeness** — Optional `minRequestDelaySecs` rate-limits requests via Crawlee concurrency settings
- **Failed requests** — Logged with URL and error; counted in run summary
- **Graceful degradation** — Invalid input fails cleanly; sitemap errors fall back to start URLs

## Documentation

- [Product Requirements (PRD)](01_PRD_Product_Requirements_Document.md)
- [Technical Design (TDD)](02_TDD_Technical_Design_Document.md)
- [API Integration Spec](04_API_Integration_Specification.md)
- [Non-Functional Requirements](06_Non_Functional_Requirements.md)
- [AGENTS.md](AGENTS.md) — machine-readable guide for AI agents and automation

## License

See repository license for terms of use.
