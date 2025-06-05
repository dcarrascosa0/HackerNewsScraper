# app/main.py

from fastapi import FastAPI, HTTPException
import asyncio

from app.scraper import fetch_page

app = FastAPI()


@app.get("/", response_model=list[dict])
@app.get("/{number}", response_model=list[dict])
async def read_pages(number: int = 1):
    # Validate that `number` is a positive integer
    if number < 1:
        raise HTTPException(status_code=400, detail="Parameter must be ≥ 1")

    # Prepare one coroutine per page (1..number)
    coros = [fetch_page(i) for i in range(1, number + 1)]
    try:
        # Run them concurrently
        results = await asyncio.gather(*coros)
    except ValueError:
        # If fetch_page raises ValueError for invalid input
        raise HTTPException(status_code=400, detail="Invalid page number")
    except Exception:
        # Catch all other errors (network, parsing, etc.)
        raise HTTPException(status_code=500, detail="Failed to fetch data from HN")

    # Flatten the list of page‐results into a single list of items
    all_items: list[dict] = []
    for page_items in results:
        all_items.extend(page_items)

    return all_items
