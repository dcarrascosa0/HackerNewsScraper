# app/main.py

from fastapi import FastAPI, HTTPException
import asyncio

from app.scraper import fetch_page
from app.cache import get_missing_pages, get_page, store_page

app = FastAPI()


@app.get("/", response_model=list[dict])
@app.get("/{number}", response_model=list[dict])
async def read_pages(number: int = 1):
    # Validate that `number` is a positive integer
    if number < 1:
        raise HTTPException(status_code=400, detail="Parameter must be ≥ 1")

    # Determine which pages (1..number) need fetching
    pages = list(range(1, number + 1))
    missing = get_missing_pages(pages)

    try:
        # Fetch all missing pages concurrently
        tasks = [fetch_page(p) for p in missing]
        results = await asyncio.gather(*tasks)
        # Store each fetched page in cache
        for page_num, items in zip(missing, results):
            store_page(page_num, items)
    except ValueError:
        # Handle invalid page_number passed to fetch_page
        raise HTTPException(status_code=400, detail="Invalid page number")
    except Exception:
        # Any other error (network, parsing, etc.)
        raise HTTPException(status_code=500, detail="Failed to fetch data from HN")

    # Assemble results from cache in order
    all_items: list[dict] = []
    for p in pages:
        page_items = get_page(p)
        if page_items:
            all_items.extend(page_items)

    return all_items
