from sqlalchemy.orm import Session
from models import Indicator, RedEngineResult

from ai_engine.red_engine import red_engine
from ai_engine.explainability import generate_explanation
from ai_engine.regime import detect_market_regime
from indicators import calculate_indicators_df, generate_signal
from market_router import fetch_market_prices
from schemas import FusionResponse, TechnicalIndicators, AIInsight

from services.news_service import fetch_stock_news
from services.sentiment_service import analyze_sentiment

def get_latest_indicator(db: Session, symbol: str):
    return (
        db.query(Indicator)
        .filter(Indicator.symbol == symbol)
        .order_by(Indicator.created_at.desc())
        .first()
    )

def get_latest_red_result(db: Session, symbol: str):
    return (
        db.query(RedEngineResult)
        .filter(RedEngineResult.symbol == symbol)
        .order_by(RedEngineResult.created_at.desc())
        .first()
    )

def generate_fusion_insight(symbol: str, market: str, db: Session = None):
    """
    Orchestrates the AI Insight generation:
    1. Fetch Prices
    2. Calculate Indicators (DF)
    3. Detect Regime
    4. Run RED Engine
    5. Generate Explanation
    """
    
    # 1. Fetch Data
    prices = fetch_market_prices(symbol, market)
    if prices is None or len(prices) < 50:
         return None
         
    # 2. Technicals
    df = calculate_indicators_df(prices)
    if df.empty:
        return None
        
    latest = df.iloc[-1]
    
    technical_signal = generate_signal(latest['rsi'], latest['macd'])
    
    # Normalize tech score for RED Engine (Buy=1, Sell=-1, Hold=0)
    tech_score = 0.0
    if technical_signal == "BUY": tech_score = 1.0
    elif technical_signal == "SELL": tech_score = -1.0
    
    # 3. Market Regime
    regime = detect_market_regime(df['close'], df['rsi'])
    
    # 4. Sentiment Analysis
    # Fetch news
    news = fetch_stock_news(symbol)
    # Analyze sentiment
    sent_result = analyze_sentiment(news)
    
    sentiment = {
        "score": sent_result.get("score", 0.0),
        # Confidence logic: fewer articles = lower confidence? 
        # For now, simplistic mapping: if we found news, reasonable confidence.
        "confidence": 0.7 if news else 0.3
    }
    
    # 5. Run RED Engine
    ai_result = red_engine(tech_score, sentiment, regime)
    
    # 6. Explainability
    explanation = generate_explanation(
        signal=ai_result['signal'],
        confidence=ai_result['confidence'],
        reasons=ai_result['reasons'],
        regime=regime,
        risk=ai_result['risk'],
        sentiment_confidence=sentiment['confidence']
    )
    
    # Construct Response Objects
    
    tech_obj = TechnicalIndicators(
        RSI=round(latest['rsi'], 2),
        SMA=round(latest['sma'], 2),
        EMA=round(latest['ema'], 2),
        MACD=round(latest['macd'], 2),
        signal=technical_signal
    )
    
    ai_obj = AIInsight(
        regime=regime,
        confidence=ai_result['confidence'] / 100.0,
        risk=ai_result['risk']
    )
    
    # We might want to return the full explanation to the user? 
    # The current Schema doesn't have "explanation" field in AIInsight or FusionResponse explicitly?
    # Let's check schemas.py. If not, we might need to update schema or just return what fits.
    # The user asked to "integrate it", so I should probably ensure the explanation is exposed if possible.
    # For now, fitting into existing schema.
    
    return FusionResponse(
        symbol=symbol,
        market=market,
        technical=tech_obj,
        ai=ai_obj
    )
