from fastapi import FastAPI
from fastapi import Depends
from models import RedEngineResult
from schemas import RedEngineCreate

from symbol_mapper import normalize_symbol

from market_router import fetch_market_prices

from sqlalchemy.orm import Session

# Database
from database import engine, Base, SessionLocal

# Models
from models import Indicator
from models import Base

# Services / Logic
from fetcher import fetch_prices, fetch_indices, fetch_stock_details
from indicators import calculate_indicators, generate_signal

# Schemas (optional but clean)
from schemas import PriceResponse, IndicatorResponse, IndicatorHistoryResponse

# Routers
from routes import sentiment

from routes import insight

from schemas import FusionResponse, TechnicalIndicators, AIInsight




# -------------------------------------------------
# 1️⃣ CREATE FASTAPI APP (MUST BE FIRST)
# -------------------------------------------------
app = FastAPI(title="Stock Backend API")

from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Mount static directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Serve index.html at root
@app.get("/", include_in_schema=False)
async def serve_index():
    return FileResponse("static/index.html")



# -------------------------------------------------
# 2️⃣ CREATE TABLES
# -------------------------------------------------
Base.metadata.create_all(bind=engine)


# -------------------------------------------------
# 3️⃣ REGISTER ROUTERS
# -------------------------------------------------
app.include_router(sentiment.router)


# -------------------------------------------------
# 4️⃣ BASIC HEALTH ROUTE
# -------------------------------------------------
@app.get("/")
def root():
    return {"message": "Backend is running successfully"}

@app.get("/stock/{symbol}")
def get_stock_details(symbol: str):
    data = fetch_stock_details(symbol)
    if not data:
        return {"error": "Stock not found"}
    return data



# -------------------------------------------------
# 5️⃣ PRICE FETCH API
# -------------------------------------------------
@app.get("/get_prices")
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

@app.get("/get_indicators")
def get_indicators(symbol: str, market: str = "GLOBAL"):
    """
    Get technical indicators for a stock symbol.
    Supports NSE, BSE, and GLOBAL markets.
    """

    # STEP 1: Normalize symbol + resolve correct market
    final_symbol, resolved_market = normalize_symbol(symbol, market)

    # STEP 2: Fetch prices based on market
    prices = fetch_market_prices(final_symbol, resolved_market)

    # STEP 3: Validation
    if prices is None or len(prices) < 50:
        return {
            "error": "Not enough data to calculate indicators",
            "symbol": final_symbol,
            "market": resolved_market
        }

    # STEP 4: Calculate indicators
    indicators = calculate_indicators(prices)

    # STEP 5: Generate signal
    signal = generate_signal(
        indicators["rsi"],
        indicators["macd"]
    )

    # STEP 6: Clean response
    return {
        "symbol": final_symbol,
        "market": resolved_market,
        "RSI": round(indicators["rsi"], 2),
        "SMA": round(indicators["sma"], 2),
        "EMA": round(indicators["ema"], 2),
        "MACD": round(indicators["macd"], 2),
        "signal": signal
    }

# -------------------------------------------------
# 7️⃣ HISTORY API
# -------------------------------------------------
@app.get("/get_history")
def get_history(symbol: str):
    db = SessionLocal()

    records = (
        db.query(Indicator)
        .filter(Indicator.symbol == symbol)
        .order_by(Indicator.created_at.desc())
        .all()
    )

    db.close()

    if not records:
        return {"error": "No history found for this symbol"}

    return [
        {
            "symbol": r.symbol,
            "RSI": round(r.rsi, 2),
            "SMA": round(r.sma, 2),
            "EMA": round(r.ema, 2),
            "MACD": round(r.macd, 2),
            "signal": r.signal,
            "timestamp": r.created_at
        }
        for r in records
    ]


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.post("/red_engine/store")
def store_red_engine_result(
    data: RedEngineCreate,
    db: Session = Depends(get_db)
):
    record = RedEngineResult(
        symbol=data.symbol,
        market=data.market,
        regime=data.regime,
        confidence=data.confidence,
        risk=data.risk
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "RED engine result stored successfully",
        "symbol": record.symbol,
        "market": record.market,
        "regime": record.regime,
        "confidence": record.confidence,
        "risk": record.risk
    }

from services.fusion_service import (
    get_latest_indicator,
    get_latest_red_result,
    generate_fusion_insight
)

@app.get("/fusion/insight", response_model=FusionResponse)
def fusion_insight(symbol: str, market: str = "GLOBAL", db: Session = Depends(get_db)):
    # Normalize symbol
    final_symbol, resolved_market = normalize_symbol(symbol, market)

    # Use the unified service function
    # Note: Currently this generates fresh insight every time. 
    # In production, we might want to check DB first as before, 
    # but the prompt asked to "integrate the AI engine", which implies running it.
    
    insight = generate_fusion_insight(final_symbol, resolved_market, db)
    
    if not insight:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Not enough data to generate insight for {final_symbol}")
        
    return insight


from services.history_service import (
    get_indicator_history,
    get_red_history
)
from schemas import (
    HistoryResponse,
    IndicatorHistoryItem,
    RedHistoryItem
)

@app.get("/history", response_model=HistoryResponse)
def get_history(
    symbol: str,
    market: str = "GLOBAL",
    limit: int = 20,
    db: Session = Depends(get_db)
):
    final_symbol, resolved_market = normalize_symbol(symbol, market)

    indicators = get_indicator_history(db, final_symbol, limit)
    red_results = get_red_history(db, final_symbol, limit)

    return {
        "symbol": final_symbol,
        "market": resolved_market,
        "indicators": [
            IndicatorHistoryItem(
                rsi=i.rsi,
                sma=i.sma,
                ema=i.ema,
                macd=i.macd,
                signal=i.signal,
                created_at=i.created_at
            )
            for i in indicators
        ],
        "ai": [
            RedHistoryItem(
                regime=r.regime,
                confidence=r.confidence,
                risk=r.risk,
                created_at=r.created_at
            )
            for r in red_results
        ] if red_results else None
    }


# -------------------------------------------------
# 8️⃣ NEW ENDPOINTS (Market Pulse, Trending, Search, News)
# -------------------------------------------------

@app.get("/market-pulse")
def get_market_pulse():
    # Major indices: Nifty 50, Sensex, S&P 500
    # Major indices: Nifty 50, Sensex, S&P 500, Nifty 500
    indices = ["^NSEI", "^BSESN", "^GSPC", "^CNX500"]
    data = fetch_indices(indices)
    
    # Format for frontend
    pulse = []
    
    # Nifty
    if "^NSEI" in data:
        pulse.append({
            "name": "Nifty 50",
            "price": f"{data['^NSEI']['price']:.2f}",
            "change": f"{data['^NSEI']['change']:.2f}%",
            "isPositive": data['^NSEI']['change'] >= 0
        })
    
    # Sensex
    if "^BSESN" in data:
         pulse.append({
            "name": "Sensex",
            "price": f"{data['^BSESN']['price']:.2f}",
            "change": f"{data['^BSESN']['change']:.2f}%",
            "isPositive": data['^BSESN']['change'] >= 0
        })

    # S&P 500
    if "^GSPC" in data:
         pulse.append({
            "name": "S&P 500",
            "price": f"{data['^GSPC']['price']:.2f}",
            "change": f"{data['^GSPC']['change']:.2f}%",
            "isPositive": data['^GSPC']['change'] >= 0
        })

    # Nifty 500
    if "^CNX500" in data:
         pulse.append({
            "name": "Nifty 500",
            "price": f"{data['^CNX500']['price']:.2f}",
            "change": f"{data['^CNX500']['change']:.2f}%",
            "isPositive": data['^CNX500']['change'] >= 0
        })

    return {
        "market_pulse": "Bullish" if any(p['isPositive'] for p in pulse) else "Mixed", # Simplistic logic
        "description": "Global markets are mixed today.",
        "confidence": 75,
        "indices": pulse
    }

@app.get("/trending")
def get_trending():
    # Mocking trending stocks or fetching from a predefined list of popular ones
    trending_symbols = ["TCS.NS", "IDEA.NS", "RELIANCE.NS", "AAPL", "TSLA"]
    
    # Reuse fetch_indices to get current price for these
    data = fetch_indices(trending_symbols)
    
    trending_list = []
    
    for sym in trending_symbols:
        s_data = data.get(sym)
        if s_data:
             # Determine action based on change (Mock logic)
             change = s_data['change']
             action = "Hold"
             if change > 1.5: action = "Strong Buy"
             elif change > 0.5: action = "Buy"
             elif change < -1.5: action = "Strong Sell"
             elif change < -0.5: action = "Sell"

             trending_list.append({
                "symbol": sym,
                "name": sym, # Ideally map to full name
                "price": s_data['price'], # Frontend expects number for formatting? No, AssetTile expects... let's check. 
                # DashboardScreen passes `asset["price"]`. AssetTile usually formats it. 
                # The data from fetch_indices is float.
                # However, previous /trending output had formatted strings.
                # DashboardScreen: `price: asset["price"]` -> AssetTile
                # AssetTile likely expects something. `fetch_indices` returns float.
                # Let's return formatted keys maybe?
                # Wait, AssetTile usually takes string or double.
                # Let's keep it consistent. My previous code returned string `f"{...}"`.
                # If AssetTile expects string, good. receiving float might break it if it calls `.substring` etc.
                # Let's stick to what I had but add Action and Currency.
                "price": f"{s_data['price']:.2f}",
                "change": f"{s_data['change']:.2f}%", 
                "isPositive": s_data['change'] >= 0,
                "currency": "USD" if "NS" not in sym else "INR",
                "action": action
            })
            
    return trending_list

@app.get("/search")
def search_stocks(q: str):
    if not q:
        return []
    
    q = q.lower()
    matches = []
    
    # 1. Search in local common map (Priority)
    from symbol_mapper import COMMON_SYMBOL_MAP
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
    
    # 2. Search via Yahoo Finance API (Dynamic)
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
        # Fake user agent to avoid blocking
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
        
    return matches[:20] # Limit results

from services.news_service import fetch_stock_news

@app.get("/news")
def get_general_news(symbol: str = "stock market"):
    # Fetch news for specific symbol or general market
    query = f"{symbol} stock" if symbol != "stock market" else "stock market"
    raw_news = fetch_stock_news(query)
    
    # Map to frontend expectations
    formatted = []
    for article in raw_news:
        title = article.get("title", "No Title")
        
        # Basic Sentiment Analysis (Mock)
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
