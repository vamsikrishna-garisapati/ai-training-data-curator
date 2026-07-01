# AI Training Data Curator

**Turn public websites into clean LLM training datasets** — crawl, extract, filter, deduplicate, and export in minutes.

Built as an [Apify Actor](https://apify.com/actors) for teams building fine-tuning data, RAG knowledge bases, and AI-ready text corpora without custom scrapers.

---

## Why use it?

| Challenge | How this Actor helps |
|-----------|----------------------|
| Raw HTML is messy | Extracts clean article-style text automatically |
| Duplicate pages waste tokens | Removes near-duplicates before export |
| Wrong language pollutes data | Optional language filter (e.g. English only) |
| Manual export is slow | Download JSON, JSONL, CSV, or Excel from Apify |

---

## Quick start

1. Add **Start URLs** (or a **Sitemap URL**).
2. Set **Max pages** (default: 10).
3. Run and download your dataset from the Apify Console.

For the full user guide (settings, FAQ, examples), see [`.actor/README.md`](.actor/README.md) — this is what appears on the Apify Store listing.

---

## Output

Each page becomes one record with `url`, `title`, `text`, `language`, `wordCount`, and optional `author` / `publishedDate` — ready for LLM fine-tuning, RAG chunking, or research.

---

## Legal notice

Only crawl websites you are permitted to access. You are responsible for terms of service, copyright, and data-use compliance.
