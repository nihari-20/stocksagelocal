# market_router.py
# STEP 2 – Market Selection Routing
from fastapi import APIRouter
from app.ai_engine.red_pipeline import red_engine_for_stock
from app.services.news_service import fetch_stock_news
from app.fetcher import fetch_prices

router = APIRouter()
def fetch_market_prices(symbol: str, market: str):
    """
    Route data fetching based on market
    """

    market = market.upper()

    if market in ["NSE", "BSE"]:
        # Indian markets still use Yahoo Finance,
        # but symbol already has .NS or .BO
        return fetch_prices(symbol)

    # Global market
    return fetch_prices(symbol)

@router.get("/analyze/{symbol}")
def analyze_stock(symbol: str, market: str = "GLOBAL"):
    """
    Analyze stock using RED Engine
    """

    # 1️⃣ Fetch prices (optional – RED pipeline fetches internally,
    # but keeping this call validates symbol & market)
    _ = fetch_market_prices(symbol, market)

    # 2️⃣ Fetch news headlines (extract titles for RED engine)
    articles = fetch_stock_news(symbol)
    headlines = [a.get("title", "") for a in articles if a.get("title")]

    # 3️⃣ Call RED Engine pipeline
    result = red_engine_for_stock(
        stock_symbol=symbol,
        news_headlines=headlines
    )

    return result
