import os
import asyncio
from pyppeteer import launch
from urllib.parse import urljoin, urlparse
from collections import deque

async def is_within_path(base_url, url, depth):
    # 解析URL，檢查是否在指定的深度和路徑內
    base_parts = urlparse(base_url).path.strip('/').split('/')
    url_parts = urlparse(url).path.strip('/').split('/')
    if urlparse(base_url).netloc != urlparse(url).netloc:
        return False
    if url_parts[:len(base_parts)] != base_parts:
        return False
    return len(url_parts) <= len(base_parts) + depth

async def crawl(start_url, depth, max_pages):
    # 啟動瀏覽器和頁面
    browser = await launch(headless=True, args=['--disable-gpu', '--no-sandbox'])
    page = await browser.newPage()

    visited = set()
    queue = deque([(start_url, 0)])
    urls_collected = []

    try:
        while queue and len(urls_collected) < max_pages:
            current_url, current_depth = queue.popleft()
            if current_url in visited or current_depth > depth:
                print(f"Skipping {current_url} at depth {current_depth} (either visited or too deep)")
                continue

            print(f"Processing {current_url} at depth {current_depth}")
            visited.add(current_url)
            await page.goto(current_url)
            await page.waitForSelector('a')

            hrefs = await page.evaluate('''() => Array.from(document.querySelectorAll('a'), a => a.href)''')
            for href in hrefs:
                if href and await is_within_path(start_url, href, depth - current_depth):
                    url = urljoin(current_url, href)
                    if url not in visited:
                        if current_depth < depth:
                            queue.append((url, current_depth + 1))
                        if url not in urls_collected:
                            urls_collected.append(url)
                            print(f"Added {url}")
                            if len(urls_collected) >= max_pages:
                                print("Reached maximum page limit")
                                break

    finally:
        await browser.close()
        print("Driver closed.")

    return urls_collected

if __name__ == "__main__":
    start_url = os.environ.get('CHATGPT_CRAWL_VAR_START_URL', 'https://www.google.com')
    depth = int(os.environ.get('CHATGPT_CRAWL_VAR_DEPTH', 1))
    max_pages = int(os.environ.get('CHATGPT_CRAWL_VAR_MAX_PAGES', 50))

    print(f"Starting crawl at {start_url} with depth {depth} and max pages {max_pages}")
    urls = asyncio.run(crawl(start_url, depth, max_pages))
    for url in urls:
        print(url)
    print(f"Crawl completed. Collected {len(urls)} URLs.")
