# Technical Design Document (TDD)

## Architecture
User -> Input Schema -> Request Queue -> Crawler -> HTML -> Trafilatura -> Filters -> Deduplication -> Dataset -> Export

## Tech Stack
- Python 3.11
- Apify SDK
- Crawlee
- Trafilatura
- readability-lxml
- langdetect
- SimHash

## Processing Flow
1. Read input
2. Queue URLs
3. Crawl pages
4. Extract text
5. Clean text
6. Detect language
7. Remove duplicates
8. Push dataset
9. Export

## Input Schema
- startUrls
- maxPages
- minTextLength
- language
- deduplicate
- outputFormat

## Output Schema
- title
- text
- url
- author
- publishedDate
- language
- wordCount

## Performance
- >20 pages/minute
- <4 GB RAM
- >95% successful extraction

## Security
- Respect robots.txt
- Public websites only
- No sensitive data collection

## Testing
- Unit tests
- Integration tests
- Edge-case validation
