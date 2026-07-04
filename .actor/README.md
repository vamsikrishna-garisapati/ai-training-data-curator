**Build LLM training data from any public website** — crawl pages, extract clean text, remove duplicates, and download a ready-to-use dataset for **fine-tuning**, **RAG**, and **machine learning**. No coding required.

This **web-to-dataset** tool saves one row per page with **URL**, **title**, **body text**, **language**, and **word count**. Export as **JSON**, **JSONL**, **CSV**, or **Excel** — ideal for OpenAI fine-tuning, Hugging Face, Pinecone, Weaviate, and other AI pipelines.

> Only crawl websites you are allowed to access. Public pages only; respects robots.txt. Does not bypass logins or paywalls.

---

## What does AI Training Data Curator do?

AI Training Data Curator is a **website crawler for LLM training data**. It turns public web pages into structured datasets — without writing scrapers or cleaning HTML yourself.

You provide URLs or a **sitemap**. The Actor:

1. **Crawls** your target website or documentation site  
2. **Extracts** clean article-style text (not raw HTML)  
3. **Filters** short pages, wrong languages, and navigation boilerplate  
4. **Removes** near-duplicate pages  
5. **Exports** one dataset row per saved page  

Use it to **scrape websites for AI training**, **build RAG knowledge bases**, or **collect text corpora** from docs, blogs, and help centers.

---

## Why scrape websites for LLM training data?

| Goal | What you get |
|------|----------------|
| **LLM fine-tuning** | Clean text + metadata per page, ready for JSONL export |
| **RAG / chatbot knowledge base** | One document per URL to chunk and embed in a vector DB |
| **Documentation dataset** | Crawl a docs site or sitemap at scale |
| **Deduplicated corpus** | Near-duplicate pages removed automatically |
| **English-only data** | Optional language filter (e.g. `en`) |

Best for **documentation**, **blogs**, **help centers**, **news**, and **marketing content**.

Run on a schedule, scale to **100,000 pages**, and integrate via the **Apify API** — no local server needed.

---

## What data does this web scraper extract?

Each saved page includes:

| Field | Description |
|-------|-------------|
| **URL** | Page link |
| **Title** | Page title |
| **Text** | Clean extracted body — **main field for training** |
| **Language** | Detected language (e.g. English) |
| **Word count** | Words in the extracted text |
| **Author** | When available on the page |
| **Published date** | When available on the page |

**Example:**

| URL | Title | Text (shortened) | Words |
|-----|-------|------------------|-------|
| docs.example.com/guide | Getting Started | This guide walks you through setup… | 842 |

Exports include the **full text** — not shortened like the table preview.

---

## How to build an LLM training dataset from a website

1. Click **Start** on this Actor page.  
2. Add **Start URLs** — paste links to pages you want, or a **Sitemap URL** for bulk crawling.  
3. Set **Max pages** (default: **10**; up to **100,000** for large corpora).  
4. Choose **Crawl strategy**:  
   - **Seeds only** — only your listed URLs (fast, predictable)  
   - **Recurse** — follow internal links (keep **Stay within seed domains** on)  
5. Optional: **Language filter** (`en`), **Minimum text length**, **Remove duplicates** (recommended).  
6. Click **Run** → open **Dataset** → **Export** (JSON, JSONL, CSV, or Excel).

**First run?** Use the default prefill and click **Run** to see a sample output in under a minute.

---

## Input settings (see Input tab for all options)

| Setting | Recommendation |
|---------|------------------|
| **Start URLs** | Required unless you use a sitemap |
| **Max pages** | Default 10; raise for larger datasets |
| **Crawl strategy** | Seeds only for listed URLs · Recurse to follow site links |
| **Stay within seed domains** | Keep **on** for single-site crawls |
| **Language filter** | `en` for English-only LLM training data |
| **Remove duplicates** | Keep **on** |
| **Proxy** | Enable if the site blocks datacenter IPs |

**Docs site tip:** Recurse + stay within domain + language `en` + max pages 100–500.

---

## Output — download your web dataset

Export formats: **JSON**, **JSONL**, **CSV**, **Excel**.

Use outputs with **OpenAI fine-tuning**, **Hugging Face**, **LangChain**, **LlamaIndex**, **Pinecone**, **Weaviate**, **Chroma**, or any ML pipeline.

Run statistics are saved under **`SUMMARY`** in the key-value store when available.

---

## Frequently asked questions

### How do I create an LLM training dataset from a website?

Add your URLs (or sitemap), set max pages, click Run, then export the dataset from the **Dataset** tab. No code required.

### Can I use this for RAG and vector databases?

Yes. Each row is clean text per URL — chunk it and embed into Pinecone, Weaviate, Chroma, or similar tools.

### Does this work for documentation and blog scraping?

Yes. It is built for article-style HTML: docs, blogs, help centers, and news sites.

### Do I need to code?

No. Configure everything in Apify Console. Use the **API** tab when you want automation.

### Why are saved pages fewer than max pages?

Pages can be filtered for length, language, quality, or duplicates. That is expected.

### What is the best export format for fine-tuning?

**JSONL** is common for LLM pipelines; **CSV** works for spreadsheets and quick review.

### Where is my data stored?

In your Apify **Dataset** for each run. Download anytime from the Console or via API.

---

## Disclaimer and support

Only crawl sites you are permitted to access. Follow **terms of service**, **copyright**, and **robots.txt**.

> Our Actors collect only publicly visible content on pages you choose. Do not scrape personal data without a lawful reason. Consult your legal advisor if unsure.

**Help:** **Issues** tab on this Store page · **API** tab for programmatic runs · [Apify documentation](https://docs.apify.com)
