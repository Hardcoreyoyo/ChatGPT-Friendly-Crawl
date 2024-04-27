import os
import asyncio
import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
from typing import List, Tuple, Set, Optional

async def fetch(session: aiohttp.ClientSession, url: str, headers: Optional[dict] = None, retries: int = 3) -> Optional[str]:
    try:
        async with session.get(url, timeout=5, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            return None
    except asyncio.TimeoutError:
        if retries > 0:
            print(f"Timeout retrieving {url}. Retrying {retries} more times.")
            return await fetch(session, url, headers, retries - 1)
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

    while to_visit:
        current_url, depth = to_visit.pop(0)
        if depth > max_depth or len(urls) >= max_urls:
            break
        if current_url not in visited:
            visited.add(current_url)
            html = await fetch(session, current_url)
            if html:
                soup = BeautifulSoup(html, 'html.parser')
                for link in soup.find_all('a', href=True):
                    link_url = urljoin(current_url, link['href'])
                    link_domain = urlparse(link_url).netloc
                    if link_domain == domain and link_url not in visited:
                        urls.append(link_url)
                        if len(urls) < max_urls:
                            to_visit.append((link_url, depth + 1))
    print("Crawl completed. Collected URLs:")
    for url in urls:
        print(url)
    return urls

async def process_urls(session: aiohttp.ClientSession, urls: List[str]) -> None:
    print("Starting processing URLs...")
    headers = {'x-respond-with': 'markdown'}
    with open('retrieve.md', 'w') as file:
        for index, url in enumerate(urls):
            print(f"Processing {index + 1}/{len(urls)}: {url}")
            api_url = f"https://r.jina.ai/{url}"
            response = await fetch(session, api_url, headers)
            if response:
                file.write(response + '\n' + '-' * 65 + '\n')
            else:
                file.write('No content found\n' + '-' * 65 + '\n')
    print("Processing complete.")

async def main() -> None:
    start_url: str = os.getenv('CHATGPT_CRAWL_VAR_START_URL', 'https://www.google.com')
    depth: int = int(os.getenv('CHATGPT_CRAWL_VAR_DEPTH', 1))
    max_urls: int = int(os.getenv('CHATGPT_CRAWL_VAR_MAX_URLS', 50))

    async with aiohttp.ClientSession() as session:
        urls: List[str] = await crawl_urls(session, start_url, urlparse(start_url).netloc, depth, max_urls)
        await process_urls(session, urls)

if __name__ == '__main__':
    asyncio.run(main())
