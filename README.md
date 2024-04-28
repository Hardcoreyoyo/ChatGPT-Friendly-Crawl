# ChatGPT Friendly Crawl


### prerequisite

> Be sure you have python >= 11 installed.

### execute

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


