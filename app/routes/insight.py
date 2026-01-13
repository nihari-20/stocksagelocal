from fastapi import APIRouter, HTTPException
from app.fetcher import fetch_prices
from app.indicators import calculate_indicators, generate_signal
from app.services.news_service import fetch_stock_news
from app.services.sentiment_service import analyze_sentiment
from app.services.fusion import generate_final_insight

router = APIRouter(
    prefix="/insight",
    tags=["Final Insight"]
)

from app.symbol_mapper import normalize_symbol

@router.get("/{symbol}")
def get_final_insight(symbol: str):
    # Normalize
    final_symbol, _ = normalize_symbol(symbol)
    
    # Use the robust fetch_prices
    prices = fetch_prices(final_symbol)

    if prices is None or len(prices) < 50:
        # Only error if fallback also failed
        raise HTTPException(
            status_code=404,  # Changed to 404 for not found
            detail=f"Not enough data to generic insight for {symbol} (tried {final_symbol})"
        )

    indicators = calculate_indicators(prices)

    # Technicals
    rsi = float(indicators["rsi"])
    macd = float(indicators["macd"])

    # Sentiment
    news = fetch_stock_news(symbol)
    sentiment_result = analyze_sentiment(news)

    sentiment = sentiment_result["sentiment"]
    sentiment_score = sentiment_result["score"]

    # Fusion
    insight = generate_final_insight(
        rsi=rsi,
        macd=macd,
        sentiment=sentiment,
        sentiment_score=sentiment_score
    )

    return {
        "symbol": symbol.upper(),
        "technical_indicators": {
            "RSI": round(rsi, 2),
            "MACD": round(macd, 2)
        },
        "sentiment": {
            "label": sentiment,
            "score": sentiment_score
        },
        "final_decision": insight["decision"],
        "confidence": insight["confidence"],
        "reason": insight["reason"]
    }
