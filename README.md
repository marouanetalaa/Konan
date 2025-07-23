# Konan

Example FastAPI and Dash application that displays stock prices from Yahoo Finance
and retrieves related news via NewsData.io. Select a date range on the chart and
click **Search News** to fetch headlines within that window (offset by one day).

## Quick start

Install dependencies:

```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill in your NewsData.io API key:

```bash
cp .env.example .env
# edit .env and set NEWS_API_KEY
```

Run the FastAPI backend and Dash frontend:

```bash
uvicorn stock_data:app --reload &
python dashboard.py
```

Open [http://localhost:8050](http://localhost:8050) to view the dashboard.
