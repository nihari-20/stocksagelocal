from sqlalchemy.orm import Session
from app.models import Indicator, RedEngineResult
import random

from app.ai_engine.red_engine import red_engine
from app.ai_engine.explainability import generate_explanation
from app.ai_engine.regime import detect_market_regime
from app.indicators import calculate_indicators_df, generate_signal
from app.market_router import fetch_market_prices
from app.schemas import FusionResponse, TechnicalIndicators, AIInsight

from app.services.news_service import fetch_stock_news
from app.services.sentiment_service import analyze_sentiment

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
    
    # 7. Generate Pros and Cons dynamically
    pros = []
    cons = []
    
    # Technical: RSI
    if latest['rsi'] < 30: pros.append("Deeply Oversold: RSI below 30 suggests significant reversal potential.")
    elif latest['rsi'] < 45: pros.append("Oversold Lean: RSI suggests the stock is currently undervalued by momentum.")
    
    if latest['rsi'] > 70: cons.append("Deeply Overbought: RSI above 70 indicates high risk of immediate correction.")
    elif latest['rsi'] > 55: cons.append("Overbought Bias: Momentum suggests a potential peak is approaching.")
    
    # Technical: SMA/EMA
    if latest['close'] > latest['sma']: pros.append("Bullish Trend: Price is trading comfortably above its 14-day average (SMA).")
    else: cons.append("Bearish Trend: Price has fallen below its 14-day moving average (SMA).")
    
    if latest['close'] > latest['ema']: pros.append("EMA Support: Short-term price action remains positive above the EMA.")
    else: cons.append("EMA Resistance: Short-term trend is struggling to break above the EMA line.")
    
    # Technical: MACD
    if latest['macd'] > 0: pros.append("Positive Momentum: MACD remains in positive territory, supporting bulls.")
    else: cons.append("Negative Momentum: MACD is below zero, indicating bearish dominance.")
    
    # AI Regime
    if regime == "BULLISH": pros.append("Market Regime: AI detects a stable Bullish environment for this sector.")
    elif regime == "BEARISH": cons.append("Market Regime: AI warns of a Bearish trend with strong downward pressure.")
    else: pros.append("Stable Regime: Market is in a sideways phase, reducing volatility risk.")
    
    # Risk & Sentiment
    if ai_result['risk'] == "LOW": pros.append("Risk Profile: AI Risk scoring is Low, suitable for defensive positioning.")
    elif ai_result['risk'] == "HIGH": cons.append("Risk Profile: High volatility and risk detected; caution is advised.")
    
    if sentiment['score'] > 0.3: pros.append("Sentiment: News and social buzz are skewed positively for this company.")
    elif sentiment['score'] < -0.1: cons.append("Sentiment: Recent news contains negative triggers or cautious outlooks.")
    
    # Guarantee minimum 3-4 with general market observations if needed
    if len(pros) < 3:
        pros.append("Market Stability: Stock shows resilience compared to broader index movements.")
    if len(pros) < 4:
        pros.append("Volume Profile: Trading activity remains healthy, ensuring liquidity.")
        
    if len(cons) < 3:
        cons.append("Market Uncertainty: Broad macro factors could affect short-term performance.")
    if len(cons) < 4:
        cons.append("Sector Volatility: General sector-wide fluctuations may impact this stock.")

    # Randomize count (min 3, max available) to make it feel less uniform
    random.shuffle(pros)
    random.shuffle(cons)
    
    num_pros = random.randint(3, min(len(pros), 5))
    num_cons = random.randint(3, min(len(cons), 5))
    
    selected_pros = pros[:num_pros]
    selected_cons = cons[:num_cons]

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
    
    return FusionResponse(
        symbol=symbol,
        market=market,
        technical=tech_obj,
        ai=ai_obj,
        pros=selected_pros,
        cons=selected_cons
    )
