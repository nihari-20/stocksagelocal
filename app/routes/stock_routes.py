from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.fetcher import fetch_prices, fetch_stock_details
from app.indicators import calculate_indicators, generate_signal
from app.symbol_mapper import normalize_symbol
from app.market_router import fetch_market_prices

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/stock/{symbol}")
def get_stock_details(symbol: str):
    data = fetch_stock_details(symbol)
    if not data:
        return {"error": "Stock not found"}
    return data

@router.get("/get_prices")
def get_prices(symbol: str):
    prices = fetch_prices(symbol)
    if prices is None:
        return {"error": "Invalid stock symbol or no data available"}

    price_dict = {
        str(date.date()): float(value)
        for date, value in prices.tail(5).items()
    }

    return {
        "symbol": symbol,
        "prices": price_dict
    }

@router.get("/get_indicators")
def get_indicators(symbol: str, market: str = "GLOBAL"):
    """
    Get technical indicators for a stock symbol.
    Supports NSE, BSE, and GLOBAL markets.
    """
    final_symbol, resolved_market = normalize_symbol(symbol, market)
    prices = fetch_market_prices(final_symbol, resolved_market)

    if prices is None or len(prices) < 50:
        return {
            "error": "Not enough data to calculate indicators",
            "symbol": final_symbol,
            "market": resolved_market
        }

    indicators = calculate_indicators(prices)
    signal = generate_signal(indicators["rsi"], indicators["macd"])

    return {
        "symbol": final_symbol,
        "market": resolved_market,
        "RSI": round(indicators["rsi"], 2),
        "SMA": round(indicators["sma"], 2),
        "EMA": round(indicators["ema"], 2),
        "MACD": round(indicators["macd"], 2),
        "signal": signal
    }

@router.get("/trending")
def get_trending():
    from app.fetcher import fetch_indices
    trending_symbols = ["TCS.NS", "IDEA.NS", "RELIANCE.NS", "AAPL", "TSLA"]
    data = fetch_indices(trending_symbols)
    
    trending_list = []
    for sym in trending_symbols:
        s_data = data.get(sym)
        if s_data:
             change = s_data['change']
             action = "Hold"
             if change > 1.5: action = "Strong Buy"
             elif change > 0.5: action = "Buy"
             elif change < -1.5: action = "Strong Sell"
             elif change < -0.5: action = "Sell"

             trending_list.append({
                "symbol": sym,
                "name": sym,
                "price": f"{s_data['price']:.2f}",
                "change": f"{s_data['change']:.2f}%", 
                "isPositive": s_data['change'] >= 0,
                "currency": "USD" if "NS" not in sym else "INR",
                "action": action
            })
    return trending_list

@router.get("/search")
def search_stocks(q: str):
    if not q:
        return []
    
    q = q.lower()
    matches = []
    
    from app.symbol_mapper import COMMON_SYMBOL_MAP
    seen = set()
    
    for name, code in COMMON_SYMBOL_MAP.items():
        if q in name or q in code.lower():
            if code not in seen:
                matches.append({
                    "symbol": code,
                    "name": name.title(),
                    "type": "Common"
                })
                seen.add(code)
    
    try:
        import requests
        url = "https://query2.finance.yahoo.com/v1/finance/search"
        params = {
            "q": q,
            "quotesCount": 10,
            "newsCount": 0,
            "enableFuzzyQuery": "false",
            "quotesQueryId": "tss_match_phrase_query"
        }
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        response = requests.get(url, params=params, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            if "quotes" in data:
                for quote in data["quotes"]:
                    symbol = quote.get("symbol")
                    if symbol and symbol not in seen:
                        matches.append({
                            "symbol": symbol,
                            "name": quote.get("longname", quote.get("shortname", symbol)),
                            "type": quote.get("quoteType", "Unknown"),
                            "exchange": quote.get("exchange", "Unknown")
                        })
                        seen.add(symbol)
    except Exception as e:
        print(f"Yahoo search failed: {e}")
        
    return matches[:20]
