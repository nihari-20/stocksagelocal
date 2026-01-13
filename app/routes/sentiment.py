from fastapi import APIRouter
from app.services.news_service import fetch_stock_news
from app.services.sentiment_service import analyze_sentiment

router = APIRouter(
    prefix="/sentiment",
    tags=["Sentiment"]
)


@router.get("/{symbol}")
def get_sentiment(symbol: str):
    news = fetch_stock_news(symbol.upper())

    # ✅ Fallback for Indian / low-coverage stocks
    if not news:
        return {
            "symbol": symbol.upper(),
            "sentiment": "Neutral",
            "score": 0.0,
            "articles_used": 0,
            "note": "Limited news coverage for this stock"
        }

    result = analyze_sentiment(news)

    return {
        "symbol": symbol.upper(),
        "sentiment": result["sentiment"],
        "score": result["score"],
        "articles_used": len(news)
    }
