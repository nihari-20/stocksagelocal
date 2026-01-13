from fastapi import APIRouter
from app.fetcher import fetch_indices
from app.services.news_service import fetch_stock_news

router = APIRouter()

@router.get("/market-pulse")
def get_market_pulse():
    indices = ["^NSEI", "^BSESN", "^GSPC", "^CNX500"]
    data = fetch_indices(indices)
    
    pulse = []
    if "^NSEI" in data:
        pulse.append({
            "name": "Nifty 50",
            "price": f"{data['^NSEI']['price']:.2f}",
            "change": f"{data['^NSEI']['change']:.2f}%",
            "isPositive": data['^NSEI']['change'] >= 0
        })
    if "^BSESN" in data:
         pulse.append({
            "name": "Sensex",
            "price": f"{data['^BSESN']['price']:.2f}",
            "change": f"{data['^BSESN']['change']:.2f}%",
            "isPositive": data['^BSESN']['change'] >= 0
        })
    if "^GSPC" in data:
         pulse.append({
            "name": "S&P 500",
            "price": f"{data['^GSPC']['price']:.2f}",
            "change": f"{data['^GSPC']['change']:.2f}%",
            "isPositive": data['^GSPC']['change'] >= 0
        })
    if "^CNX500" in data:
         pulse.append({
            "name": "Nifty 500",
            "price": f"{data['^CNX500']['price']:.2f}",
            "change": f"{data['^CNX500']['change']:.2f}%",
            "isPositive": data['^CNX500']['change'] >= 0
        })

    return {
        "market_pulse": "Bullish" if any(p['isPositive'] for p in pulse) else "Mixed",
        "description": "Global markets are mixed today.",
        "confidence": 75,
        "indices": pulse
    }

@router.get("/news")
def get_general_news(symbol: str = "stock market"):
    query = f"{symbol} stock" if symbol != "stock market" else "stock market"
    raw_news = fetch_stock_news(query)
    
    formatted = []
    for article in raw_news:
        title = article.get("title", "No Title")
        sentiment = "Neutral"
        t_lower = title.lower()
        if any(x in t_lower for x in ["soar", "surge", "jump", "record", "bull", "gain", "high", "growth", "active"]):
             sentiment = "Positive"
        elif any(x in t_lower for x in ["plunge", "drop", "crash", "bear", "loss", "low", "weak", "down", "fall"]):
             sentiment = "Negative"
             
        formatted.append({
            "headline": title,
            "sentiment": sentiment,
            "url": article.get("url"),
            "image": article.get("urlToImage")
        })
    return formatted
