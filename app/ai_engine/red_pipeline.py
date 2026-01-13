import yfinance as yf

from app.ai_engine.indicators import calculate_rsi, calculate_macd
from app.ai_engine.sentiment_ensemble import multi_source_sentiment
from app.ai_engine.regime import detect_market_regime
from app.ai_engine.red_engine import red_engine
from app.ai_engine.explainability import generate_explanation


def compute_tech_score(close_prices):
    """
    Converts indicators into a normalized technical score [-1, +1]
    """

    rsi_series = calculate_rsi(close_prices).dropna()

    if rsi_series.empty:
        return 0.0

    rsi = float(rsi_series.iloc[-1].item()) # ✅ scalar

    macd, signal, _ = calculate_macd(close_prices)
    macd_val = float(macd.dropna().iloc[-1].item())
    signal_val = float(signal.dropna().iloc[-1].item())

    score = 0.0

    # RSI contribution
    if rsi < 30:
        score += 0.5
    elif rsi > 70:
        score -= 0.5

    # MACD contribution
    if macd_val > signal_val:
        score += 0.5
    else:
        score -= 0.5

    return score


def red_engine_for_stock(
    stock_symbol: str,
    news_headlines: list
):
    """
    Full RED pipeline for a given stock.
    """

    # -------------------------------
    # 1. Load stock data
    # -------------------------------
    data = yf.download(stock_symbol, period="6mo", progress=False)

    if data.empty:
        return {"error": "No stock data available"}

    close = data["Close"]

    # -------------------------------
    # 2. Technical score (dynamic!)
    # -------------------------------
    tech_score = compute_tech_score(close)

    # -------------------------------
    # 3. Sentiment ensemble (dynamic!)
    # -------------------------------
    sentiment = multi_source_sentiment(news_headlines)

    # -------------------------------
    # 4. Market regime (dynamic!)
    # -------------------------------
    rsi_series = calculate_rsi(close)
    regime = detect_market_regime(close, rsi_series)

    # -------------------------------
    # 5. RED Engine decision
    # -------------------------------
    red_result = red_engine(
        tech_score=tech_score,
        sentiment=sentiment,
        regime=regime
    )

    # -------------------------------
    # 6. Explainability
    # -------------------------------
    explanation = generate_explanation(
        signal=red_result["signal"],
        confidence=red_result["confidence"],
        reasons=red_result["reasons"],
        regime=regime,
        risk=red_result["risk"],
        sentiment_confidence=sentiment["confidence"]
    )

    return explanation
