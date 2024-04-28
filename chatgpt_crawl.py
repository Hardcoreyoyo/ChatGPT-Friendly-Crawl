import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple, Set, Optional

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

async def crawl_urls(session: aiohttp.ClientSession, start_url: str, domain: str, max_depth: int, max_urls: int) -> List[str]:
    print("Starting URL crawl...")
    to_visit: List[Tuple[str, int]] = [(start_url, 0)]
    visited: Set[str] = set()
    urls: List[str] = []

    while to_visit and len(urls) < max_urls:
        current_url, depth = to_visit.pop(0)
        current_url_parsed = urlparse(current_url)

        if current_url not in visited and current_url_parsed.netloc == domain:
            visited.add(current_url)
            if depth <= max_depth:
                html = await fetch(session, current_url)
                if html:
                    soup = BeautifulSoup(html, 'html.parser')
                    for link in soup.find_all('a', href=True):
                        if len(urls) >= max_urls:
                            break  # Stop processing if we've reached the maximum number of URLs
                        link_url = urljoin(current_url, link['href'])
                        link_url_parsed = urlparse(link_url)
                        # Check if the URL is directly under the start URL and is a new path
                        if (link_url_parsed.netloc == domain and
                            link_url_parsed.path.startswith(current_url_parsed.path) and
                            link_url_parsed.path.strip("/").count("/") == current_url_parsed.path.strip("/").count("/") + 1 and
                            link_url not in visited):
                            urls.append(link_url)
                            to_visit.append((link_url, depth + 1))
                            if len(urls) >= max_urls:
                                break  # Stop adding new URLs if we've reached the maximum number

    print("Crawl completed. Collected URLs:")
    for url in urls:
        print(url)
    print(f"Crawl completed. Collected {len(urls)} URLs.")

    return urls

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
    max_urls: int = int(os.getenv('CHATGPT_CRAWL_VAR_MAX_URLS', 50))

    print(f"start_url: {start_url}, depth: {depth}, max_urls: {max_urls}")

    async with aiohttp.ClientSession() as session:
        urls: List[str] = await crawl_urls(session, start_url, urlparse(start_url).netloc, depth, max_urls)
        await process_urls(session, urls)

if __name__ == '__main__':
    asyncio.run(main())
