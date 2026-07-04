# AI Training Data Curator — Agent Guide

Use this document when an AI agent (Cursor, ChatGPT, Apify MCP, or automation) needs to **find, run, or integrate** the **AI Training Data Curator** Apify Actor.

## What it does

Transforms **public websites** into **clean, structured datasets** for:

- LLM **fine-tuning**
- **RAG** (retrieval-augmented generation)
- ML / data science pipelines

Pipeline: **crawl → extract text (Trafilatura) → filter → deduplicate (SimHash) → Apify dataset export (JSONL/CSV)**.

## When to use this Actor

| Use case | Use this Actor? |
|----------|-----------------|
| Build a training corpus from blog/docs sites | Yes |
| Scrape product listings into ML features | Yes (with URL globs) |
| One-off HTML snapshot without cleaning | No — use a raw scraper |
| Sites requiring login / paywall | No — public pages only |
| Semantic chunking for vector DB | Partial — chunking is post-MVP |

## Apify identifiers

| Field | Value |
|-------|--------|
| **Actor name** | `ai-training-data-curator` |
| **GitHub** | `vamsikrishna-garisapati/ai-training-data-curator` |
| **Runtime** | Python 3.11, Apify SDK + Crawlee |

## Minimal input (copy-paste)

```json
{
  "startUrls": [{ "url": "https://httpbin.org/html" }],
  "maxPages": 10,
  "crawlStrategy": "seeds-only",
  "minTextLength": 100,
  "deduplicate": true
}
```

## Output record schema (default dataset)

Each item:

```json
{
  "url": "string",
  "title": "string",
  "text": "string",
  "author": "string",
  "publishedDate": "string",
  "language": "string",
  "wordCount": 0
}
```

Run summary is stored in key-value store key `SUMMARY`.

## Key input fields

| Field | Purpose |
|-------|---------|
| `startUrls` | Seed URLs (required unless `sitemapUrl`) |
| `sitemapUrl` | Optional sitemap.xml |
| `maxPages` | Fetch limit (1–100000); counts HTTP requests, not saved rows after filtering |
| `crawlStrategy` | `recurse` or `seeds-only` |
| `stayWithinDomain` | Limit link following to seed hosts |
| `language` | ISO 639-1 filter (e.g. `en`) |
| `minTextLength` | Min character length |
| `deduplicate` | SimHash near-dedup |
| `maxDepth` | Max link hops from seeds |
| `exportRejectedPages` | Write filtered URLs to `rejected` dataset |
| `proxyConfiguration` | Apify Proxy for blocked sites |

## How to run

**Apify API:** `POST /v2/acts/{actorId}/runs` with `body` = input JSON (see minimal input above).

## Reliability notes

- Invalid input is **coerced to safe defaults** (run does not fail on bad types).
- Missing or invalid `startUrls` and `sitemapUrl` causes the run to **fail** with a clear message (no silent demo URL fallback).
- Per-page handler errors are logged; the run **continues** and exits **Succeeded**.
- Apify **daily automated tests** use input **prefill** values (`https://httpbin.org/html`, `maxPages: 1`, `seeds-only`).

## Compliance

Users must respect robots.txt, site terms of service, and copyright. Actor enables `respect_robots_txt_file`.

## Related files

- User README: [`README.md`](../README.md)
- Input schema: [`.actor/input_schema.json`](../.actor/input_schema.json)
- Source entrypoint: [`src/main.py`](../src/main.py)
