import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import pandas as pd
import requests

dash_app = dash.Dash(__name__)
server = dash_app.server

dash_app.layout = html.Div([
    html.H2("Stock Dashboard"),
    dcc.Dropdown(
        id="ticker",
        options=[{"label": x, "value": x} for x in ["AAPL", "MSFT", "GOOGL"]],
        value="AAPL"
    ),
    dcc.RadioItems(
        id="range",
        options=[
            {"label": "1M", "value": "1mo"},
            {"label": "6M", "value": "6mo"},
            {"label": "1Y", "value": "1y"},
            {"label": "5Y", "value": "5y"}
        ],
        value="1y",
        inline=True
    ),
    dcc.Graph(id="price-chart"),
    html.Button("Search News", id="search-news-btn"),
    html.Div(id="news-output", style={"marginTop": "20px"})
])


@dash_app.callback(
    Output("price-chart", "figure"),
    Input("ticker", "value"),
    Input("range", "value")
)
def update_chart(ticker, period):
    url = f"http://localhost:8000/stock/{ticker}?period={period}"
    df = pd.DataFrame(requests.get(url).json())

    fig = {
        "data": [{
            "x": df["Date"],
            "y": df["Close"],
            "type": "scatter",
            "mode": "lines",
            "name": ticker
        }],
        "layout": {
            "title": f"{ticker} Price History",
            "xaxis": {
                "rangeslider": {"visible": True},
                "rangeselector": {
                    "buttons": [
                        {"count": 1, "label": "1M", "step": "month", "stepmode": "backward"},
                        {"count": 6, "label": "6M", "step": "month", "stepmode": "backward"},
                        {"count": 1, "label": "1Y", "step": "year", "stepmode": "backward"},
                        {"count": 5, "label": "5Y", "step": "year", "stepmode": "backward"},
                        {"step": "all"}
                    ]
                }
            }
        }
    }
    return fig


@dash_app.callback(
    Output("news-output", "children"),
    Input("search-news-btn", "n_clicks"),
    State("price-chart", "relayoutData"),
    State("ticker", "value")
)
def search_news(n_clicks, relayout_data, ticker):
    if n_clicks is None or not relayout_data or "xaxis.range[0]" not in relayout_data:
        return "Select a date range and click 'Search News'."

    start_date = pd.to_datetime(relayout_data["xaxis.range[0]"]).date()
    end_date = pd.to_datetime(relayout_data["xaxis.range[1]"]).date()

    start_date -= pd.Timedelta(days=1)

    news_url = f"http://localhost:8000/news/{ticker}?start={start_date}&end={end_date}"
    news = requests.get(news_url).json()

    if not news.get("results"):
        return "No news found for that period."

    items = []
    for article in news["results"]:
        items.append(html.Div([
            html.A(article["title"], href=article["link"], target="_blank"),
            html.Small(f" {article['pubDate']}")
        ]))
    return items


if __name__ == "__main__":
    dash_app.run_server(debug=True)
