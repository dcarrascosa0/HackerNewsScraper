# app/main.py

from fastapi import FastAPI, HTTPException

from app.scraper import fetch_page

app = FastAPI()


@app.get("/")
@app.get("/{number}")
async def read_pages(number: int = 1):
    # Stub implementation: not yet implemented, so raise
    raise NotImplementedError("read_pages has not been implemented yet")
