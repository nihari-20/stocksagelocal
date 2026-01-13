import os
import requests

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_stock_news(symbol: str):
    if not API_KEY:
        # Return mock news for demonstration/fallback
        return [
            {"title": "Global Markets Rally: Live Updates and Trends", "url": "https://www.google.com/search?q=Global+Stock+Markets+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1611974765270-ca1258634369?w=400", "source": {"name": "MarketWatch"}},
            {"title": "Technology Sector Surges: Weekly Performance Review", "url": "https://www.google.com/search?q=Tech+Sector+Stocks+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=400", "source": {"name": "Bloomberg"}},
            {"title": "Federal Reserve Outlook: Interest Rate Impacts", "url": "https://www.google.com/search?q=Fed+Rate+News&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1556740758-90de29294860?w=400", "source": {"name": "Reuters"}},
            {"title": "Energy Sector Shift: Renewable Growth Surpasses Forecasts", "url": "https://www.google.com/search?q=Energy+Market+News&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=400", "source": {"name": "CleanTech"}},
            {"title": "Corporate Earnings Season: Key Highlights and Surprises", "url": "https://www.google.com/search?q=Earnings+Season+Highlights&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=400", "source": {"name": "CNBC"}}
        ]

    # Enhanced targeted keywords for market impact
    impact_keywords = "(earnings OR dividend OR " + symbol + " news OR price target OR acquisition OR surge OR plunge)"
    
    # Clean symbol for search (e.g., IRFC.NS -> IRFC)
    clean_symbol = symbol.split('.')[0]
    
    query = f"({clean_symbol} OR {symbol}) AND {impact_keywords}"

    params = {
        "q": query,
        "language": "en",
        "sortBy": "relevancy", # Relevancy is better for targeted news
        "pageSize": 10,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        if response.status_code != 200:
            # Fallback to simple query if complex one fails
            params["q"] = f"{symbol} stock news"
            response = requests.get(BASE_URL, params=params, timeout=5)
            if response.status_code != 200:
                return []
        
        return response.json().get("articles", [])
    except Exception:
        return []
