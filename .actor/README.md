# AI Training Data Curator

**Turn public websites into clean LLM training datasets** — crawl, extract, filter, deduplicate, export.

## Quick start

1. Set **Start URLs** (or Sitemap URL).
2. Set **Max pages** and optional **Language** filter.
3. Run — download dataset as **JSONL** or **CSV**.

## Example input

```json
{
  "startUrls": [{ "url": "https://books.toscrape.com" }],
  "maxPages": 50,
  "language": "en",
  "deduplicate": true,
  "crawlStrategy": "recurse",
  "stayWithinDomain": true
}
```

## Output

| Field | Description |
|-------|-------------|
| `url` | Page URL |
| `title` | Page title |
| `text` | Clean extracted body text |
| `language` | Detected ISO 639-1 code |
| `wordCount` | Word count |
| `author` | Author if detected |
| `publishedDate` | Date if detected |

## Best for

- LLM fine-tuning corpora
- RAG knowledge bases
- Research datasets from public docs/blogs

## AI agents

See [`AGENTS.md`](../AGENTS.md) for machine-readable integration guidance.

## Legal

Only crawl sites you are allowed to access. You are responsible for ToS and copyright compliance.
