from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.middleware.wsgi import WSGIMiddleware
import yfinance as yf
import requests
import os
from dotenv import load_dotenv
from dashboard import dash_app

load_dotenv()

app = FastAPI()

# Mount the Dash dashboard at /dashboard
app.mount("/dashboard", WSGIMiddleware(dash_app.server))

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


@app.get("/", response_class=HTMLResponse)
def read_root():
    """Display basic usage instructions."""
    return """
    <html>
        <head><title>Konan API</title></head>
        <body>
            <h1>Konan Stock Dashboard API</h1>
            <p>This service provides stock prices and news data for the Dash dashboard.</p>
            <h2>Getting started</h2>
            <ol>
                <li>Install dependencies with <code>pip install -r requirements.txt</code></li>
                <li>Copy <code>.env.example</code> to <code>.env</code> and add your NewsData.io API key.</li>
                <li>Run the server with <code>uvicorn stock_data:app --reload</code></li>
                <li>Open <a href='http://localhost:8000/dashboard'>http://localhost:8000/dashboard</a> to view the dashboard.</li>
            </ol>
        </body>
    </html>
    """

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
