import httpx
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser


def is_allowed(base_url: str, user_agent: str, path: str) -> bool:
    robots_url = urljoin(base_url, "/robots.txt")
    rp = urllib.robotparser.RobotFileParser()
    try:
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch(user_agent, path)
    except Exception:
        return False


async def scrape_search_results(search_url: str, result_selector: str, user_agent: str = "my-movie-scraper/1.0"):
    parsed = urlparse(search_url)
    base = f"{parsed.scheme}://{parsed.netloc}"
    if not is_allowed(base, user_agent, parsed.path or "/"):
        raise RuntimeError("Robots.txt disallows scraping this path or robots.txt not accessible.")
    headers = {"User-Agent": user_agent}
    async with httpx.AsyncClient(timeout=15.0, headers=headers) as client:
        r = await client.get(search_url)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "html.parser")
        results = []
        for el in soup.select(result_selector):
            text = el.get_text(strip=True)
            results.append(text)
        return results
