import aiohttp
from typing import List, Optional
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
                if href and not '#' in href:
                    url = urljoin(current_url, href)
                    if url not in visited and await is_within_path(start_url, href, depth - current_depth):
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

async def fetch(session: aiohttp.ClientSession, url: str, headers: Optional[dict] = None, retries: int = 3, timeout: int = 10) -> Optional[str]:
    try:
        async with session.get(url, timeout=timeout, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            return None
    except asyncio.TimeoutError:
        if retries > 0:
            print(f"Timeout retrieving {url}. Retrying {retries} more times.")
            return await fetch(session, url, headers, retries - 1, timeout)
        else:
            print(f"Failed to retrieve {url} after multiple retries.")
            return None
    except Exception as e:
        print(f"Error retrieving {url}: {e}")
        return None

async def process_urls(session: aiohttp.ClientSession, urls: List[str], batch_size: int = 10) -> None:
    print("Starting processing URLs...")
    headers = {'x-respond-with': 'markdown'}
    semaphore = asyncio.Semaphore(batch_size)  # Limit the number of concurrent requests
    lock = asyncio.Lock()
    progress_counter = 0

    async def fetch_and_write(url, total):
        nonlocal progress_counter
        async with semaphore:
            response = await fetch(session, f"https://r.jina.ai/{url}", headers)
            async with lock:
                progress_counter += 1
                print(f"Processing {progress_counter}/{total} ({(progress_counter / total) * 100:.2f}%) URLs completed.")
            with open('retrieve.md', 'a') as file:
                if response:
                    file.write(response + '\n' + '-' * 65 + '\n')
                else:
                    file.write('No content found\n' + '-' * 65 + '\n')

    tasks = [fetch_and_write(url, len(urls)) for url in urls]
    await asyncio.gather(*tasks)

    print("Processing complete.")

async def main() -> None:
    start_url: str = os.getenv('CHATGPT_CRAWL_VAR_START_URL', 'https://www.google.com')
    depth: int = int(os.getenv('CHATGPT_CRAWL_VAR_DEPTH', 1))
    max_pages = int(os.environ.get('CHATGPT_CRAWL_VAR_MAX_PAGES', 50))

    async with aiohttp.ClientSession() as session:
        urls: List[str] = await crawl(start_url, depth, max_pages)

        for url in urls:
            print(url)
        print(f"Crawl completed. Collected {len(urls)} URLs.")

        await process_urls(session, urls)

if __name__ == '__main__':
    asyncio.run(main())
