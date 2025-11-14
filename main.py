import os
import asyncio
from fastapi import FastAPI, Query, HTTPException, Request, Form
from pydantic import BaseModel
from typing import List
from scrapers.manager import aggregate_checks
from db import save_results, get_recent, list_cached_queries
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from admin import send_push_for_results

app = FastAPI(title="Pokemon Stock Finder API (Advanced)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

templates = Jinja2Templates(directory="templates")

class StockItem(BaseModel):
    store: str
    product: str
    inStock: bool
    url: str
    metadata: dict = {}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    queries = await list_cached_queries()
    return templates.TemplateResponse("index.html", {"request": request, "queries": queries})

@app.get("/api/stock", response_model=List[StockItem])
async def api_stock(item: str = Query(..., min_length=1), fresh: bool = False):
    item = item.strip()
    if not item:
        raise HTTPException(status_code=400, detail="Missing item query")

    # If not fresh, try to return recent cached results
    recent = await get_recent(item)
    if recent and not fresh:
        # kick off background refresh
        asyncio.create_task(aggregate_checks(item, save_to_db=True))
        return recent

    results = await aggregate_checks(item, save_to_db=True)
    return results

@app.post("/api/notify")
async def notify(item: str = Form(...)):
    # Force a fresh scrape and send notifications for inStock results
    results = await aggregate_checks(item, save_to_db=True)
    await send_push_for_results(item, results)
    return RedirectResponse(url="/", status_code=303)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))
