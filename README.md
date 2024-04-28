# ChatGPT Friendly Crawl


### prerequisite

> Ensure Python 11+ is installed. Dependencies can be installed via:  

```bash
pip install aiohttp pyppeteer
```

### Usage

Before running the crawler, set these environment variables:
- `CHATGPT_CRAWL_VAR_START_URL`: Starting URL for the crawl.
- `CHATGPT_CRAWL_VAR_DEPTH`: Maximum crawl depth.
- `CHATGPT_CRAWL_VAR_MAX_PAGES`: Maximum number of pages to fetch.

```bash

export CHATGPT_CRAWL_VAR_START_URL=$target_url && \
export CHATGPT_CRAWL_VAR_DEPTH=$depth_number && \
export CHATGPT_CRAWL_VAR_MAX_PAGES=$max_pages_number && \
python ./chatgpt_crawl.py

```

```bash

export CHATGPT_CRAWL_VAR_START_URL=https://www.google.com && \
export CHATGPT_CRAWL_VAR_DEPTH=2 && \
export CHATGPT_CRAWL_VAR_MAX_PAGES=100 && \
python ./chatgpt_crawl.py

```

## Benefits of Using `https://r.jina.ai` API

Using the `https://r.jina.ai` API optimizes the retrieval process, enhancing scalability and reliability without the overhead of managing infrastructure.

## Wrap-up

This crawler combines modern async patterns with a robust API to streamline data collection, making it an efficient tool for scalable web scraping.
```

This trimmed version keeps it professional with less fluff and more industry-specific terminology, emphasizing efficiency and scalability.
