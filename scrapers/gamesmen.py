from bs4 import BeautifulSoup
from .utils import fetch_text, choose_proxy
import aiohttp

async def check_gamesmen(query: str, proxies=None):
    url = f"https://www.gamesmen.com.au/search?query={query}"
    headers = { "User-Agent": "Mozilla/5.0" }
    proxy = choose_proxy(proxies)
    async with aiohttp.ClientSession() as session:
        text = await fetch_text(session, url, headers=headers, proxy=proxy)
        soup = BeautifulSoup(text, 'html.parser')
        items = []
        for product in soup.select('.product-tile'):
            title = product.select_one('.product-title')
            stock = product.select_one('.availability')
            link = product.find('a')
            items.append({
                "store": "The Gamesmen",
                "product": title.get_text(strip=True) if title else "Unknown",
                "inStock": bool(stock and 'Out of Stock' not in stock.get_text(strip=True)),
                "url": "https://www.gamesmen.com.au" + link['href'] if link and link.get('href') else url
            })
        return items
