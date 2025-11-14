import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
import random

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=1, max=8),
       retry=retry_if_exception_type(Exception))
async def fetch_text(session: aiohttp.ClientSession, url: str, headers=None, proxy=None, timeout=15):
    async with session.get(url, headers=headers, proxy=proxy, timeout=timeout) as resp:
        resp.raise_for_status()
        return await resp.text()

def choose_proxy(proxies):
    if not proxies:
        return None
    import random
    return random.choice(proxies)
