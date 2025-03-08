from fastapi import FastAPI, Query
import requests
from fastapi.middleware.cors import CORSMiddleware
import asyncio

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

API_URL = "https://datasets-server.huggingface.co/rows"
DATASET_NAME = "Abirate/english_quotes"

cached_quotes = []
fetch_lock = asyncio.Lock()

async def fetch_quotes():
    global cached_quotes
    async with fetch_lock:
        if cached_quotes:
            return cached_quotes

        response = requests.get(f"{API_URL}?dataset={DATASET_NAME}&config=default&split=train&length=100")
        data = response.json()
        cached_quotes = [
            {
                "quote": row["row"].get("quote", ""),
                "author": row["row"].get("author", ""),
                "tags": row["row"].get("tags", [])
            } for row in data.get("rows", [])
        ]
        return cached_quotes

@app.get("/quotes")
async def get_quotes():
    return await fetch_quotes()

@app.get("/quotes/by_tag")
async def get_quotes_by_tag(tag: str = Query(...)):
    all_quotes = await fetch_quotes()
    return [q for q in all_quotes if tag.lower() in [t.lower() for t in q.get("tags", [])]]

@app.get("/tags")
async def get_tags():
    all_quotes = await fetch_quotes()
    tags = {tag for quote in all_quotes for tag in quote.get("tags", [])}
    return sorted(tags)
