import asyncio
from typing import List
from scrapers import ebgames, jbhifi, bigw, target, kmart, amazonau, gamesmen, mightyape
from db import save_results

SEM = asyncio.Semaphore(int(__import__('os').environ.get('MAX_CONCURRENT_SCRAPES', '4')))

async def run_scraper(func, query, proxies):
    async with SEM:
        try:
            return await func(query, proxies=proxies)
        except Exception as e:
            return []

async def aggregate_checks(query: str, save_to_db: bool = True) -> List[dict]:
    proxies = None
    proxy_env = __import__('os').environ.get('PROXIES_JSON')
    if proxy_env:
        try:
            proxies = __import__('json').loads(proxy_env)
        except:
            proxies = None

    tasks = [
        run_scraper(ebgames.check_ebgames, query, proxies),
        run_scraper(jbhifi.check_jbhifi, query, proxies),
        run_scraper(bigw.check_bigw, query, proxies),
        run_scraper(target.check_target, query, proxies),
        run_scraper(kmart.check_kmart, query, proxies),
        run_scraper(amazonau.check_amazonau, query, proxies),
        run_scraper(gamesmen.check_gamesmen, query, proxies),
        run_scraper(mightyape.check_mightyape, query, proxies),
    ]
    results_nested = await asyncio.gather(*tasks)
    results = []
    for r in results_nested:
        if isinstance(r, list):
            results.extend(r)
    if save_to_db:
        await save_results(query, results)
    return results
