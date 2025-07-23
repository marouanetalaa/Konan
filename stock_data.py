from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import yfinance as yf
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")

@app.get("/stock/{ticker}")
def get_stock(ticker: str, period: str = "1y", interval: str = "1d"):
    data = yf.download(ticker, period=period, interval=interval)
    data.reset_index(inplace=True)
    return JSONResponse(data.to_dict(orient="records"))

@app.get("/news/{company}")
def get_news(company: str, start: str = Query(...), end: str = Query(...)):
    if not NEWS_API_KEY:
        raise HTTPException(status_code=500, detail="NEWS_API_KEY not configured")

    url = "https://newsdata.io/api/1/news"
    params = {
        "apikey": NEWS_API_KEY,
        "q": company,
        "language": "en",
        "category": "business",
        "from_date": start,
        "to_date": end,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()
