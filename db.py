import os, json, asyncio
from datetime import datetime, timedelta

MONGO_URI = os.environ.get('MONGODB_URI')
CACHE_FILE = os.environ.get('CACHE_FILE', 'cache.json')
TTL_SECONDS = int(os.environ.get('CACHE_TTL', '300'))

if MONGO_URI:
    from motor.motor_asyncio import AsyncIOMotorClient
    client = AsyncIOMotorClient(MONGO_URI)
    db = client.get_default_database()
    async def save_results(query, results):
        doc = {
            "query": query,
            "results": results,
            "ts": datetime.utcnow()
        }
        await db.stock.update_one({"query": query}, {"$set": doc}, upsert=True)

    async def get_recent(query):
        doc = await db.stock.find_one({"query": query})
        if not doc:
            return None
        ts = doc.get('ts')
        if (datetime.utcnow() - ts).total_seconds() > TTL_SECONDS:
            return None
        return doc.get('results', [])

    async def list_cached_queries():
        docs = db.stock.find().limit(100)
        out = []
        async for d in docs:
            out.append(d.get('query'))
        return out
else:
    async def save_results(query, results):
        try:
            data = {}
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
            data[query] = {"results": results, "ts": datetime.utcnow().isoformat()}
            with open(CACHE_FILE, 'w') as f:
                json.dump(data, f)
        except Exception:
            pass

    async def get_recent(query):
        if not os.path.exists(CACHE_FILE):
            return None
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
            v = data.get(query)
            if not v:
                return None
            ts = datetime.fromisoformat(v.get('ts'))
            if (datetime.utcnow() - ts).total_seconds() > TTL_SECONDS:
                return None
            return v.get('results', [])
        except Exception:
            return None

    async def list_cached_queries():
        if not os.path.exists(CACHE_FILE):
            return []
        try:
            with open(CACHE_FILE, 'r') as f:
                data = json.load(f)
            return list(data.keys())
        except:
            return []
