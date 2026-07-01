# AI Training Data Curator — Turn websites into LLM training data

**Build clean datasets from any public website** for LLM fine-tuning, RAG (retrieval-augmented generation), and AI model training — without writing scrapers or cleaning HTML by hand.

Paste your URLs, run the Actor, and download structured records with page title, body text, language, and word count — ready for JSON, JSONL, or CSV export.

---

## What this Actor does

1. **Crawls** pages from your start URLs (and optional sitemap)
2. **Extracts** clean article-style text — navigation menus and boilerplate are filtered out
3. **Filters** by language and minimum text length
4. **Removes** near-duplicate pages automatically
5. **Exports** one row per page to your Apify dataset

You get training-ready text, not raw HTML.

---

## Who is it for?

- **AI & ML teams** preparing fine-tuning or pre-training corpora
- **RAG builders** indexing documentation, blogs, or knowledge bases
- **Researchers** collecting web text datasets at scale
- **Product teams** turning help centers or marketing sites into searchable AI content

---

## Quick start (3 steps)

1. **Start URLs** — Add one or more website URLs to crawl (or paste a sitemap URL).
2. **Max pages** — Choose how many pages to collect (default: 10).
3. **Run** — Open the **Dataset** tab when finished and download as JSON, JSONL, CSV, or Excel.

**Tip:** For a single site section, use **Crawl strategy → seeds-only**. To follow internal links, use **recurse** and keep **Stay within seed domains** enabled.

---

## What you get (output)

Each saved page becomes one dataset record:

| Field | What it contains |
|-------|------------------|
| `url` | Page address |
| `title` | Page title |
| `text` | Clean extracted body text |
| `language` | Detected language (e.g. `en`) |
| `wordCount` | Number of words |
| `author` | Author name, when detected |
| `publishedDate` | Publish date, when detected |

**Example record:**

```json
{
  "url": "https://example.com/blog/getting-started",
  "title": "Getting Started with RAG",
  "text": "Retrieval-augmented generation combines search with large language models...",
  "language": "en",
  "wordCount": 842,
  "author": "Jane Doe",
  "publishedDate": "2025-03-15"
}
```

---

## Common settings

| Setting | What it does |
|---------|----------------|
| **Start URLs** | Where crawling begins |
| **Sitemap URL** | Optional — load many URLs from `sitemap.xml` |
| **Max pages** | Stop after this many pages (1–100,000) |
| **Language filter** | Keep only pages in one language (e.g. `en`) |
| **Minimum text length** | Skip very short pages (menus, stubs) |
| **Remove duplicates** | Drop near-duplicate content (recommended: on) |
| **Crawl strategy** | `recurse` = follow links; `seeds-only` = only listed URLs |
| **Stay within seed domains** | Do not leave the original website |
| **Export rejected pages** | Optional second dataset showing filtered-out URLs |
| **Proxy configuration** | Use if the site blocks automated access |

---

## Example input

```json
{
  "startUrls": [{ "url": "https://docs.example.com" }],
  "maxPages": 100,
  "language": "en",
  "minTextLength": 200,
  "deduplicate": true,
  "crawlStrategy": "recurse",
  "stayWithinDomain": true
}
```

---

## Download your dataset

After a run completes:

1. Go to the run in [Apify Console](https://console.apify.com)
2. Open the **Dataset** tab
3. Click **Export** → choose JSON, JSONL, CSV, or Excel

Use the dataset directly in Hugging Face, OpenAI fine-tuning pipelines, vector databases, or your own ML workflow.

---

## FAQ

**Can I use this for RAG?**  
Yes. The output is clean text per URL — ideal for chunking and embedding into Pinecone, Weaviate, Chroma, or similar vector stores.

**Does it work on documentation sites and blogs?**  
Yes. It is designed for article-style pages: docs, blogs, news, help centers, and marketing content.

**Does it remove duplicate pages?**  
Yes, by default. Near-duplicate pages are detected and only one copy is kept.

**What formats can I export?**  
JSON, JSONL, CSV, and Excel from the Apify dataset. JSONL is common for LLM training pipelines.

**Do I need to code?**  
No. Configure inputs in the Apify UI and download results. API access is available if you want to automate runs.

**Is crawling always allowed?**  
No. You must have permission to access and use the content you crawl. See **Legal notice** below.

---

## Legal notice

You are responsible for complying with each website's terms of service and applicable copyright law. Only crawl sites you are allowed to access, respect `robots.txt`, and use extracted data in line with applicable regulations.
