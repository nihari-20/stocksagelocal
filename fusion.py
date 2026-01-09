def generate_final_insight(rsi, macd, sentiment, sentiment_score):
    """
    Rule-based fusion of technical indicators and sentiment
    """

    # Strong BUY condition
    if rsi < 30 and macd > 0 and sentiment == "Positive":
        return {
            "decision": "BUY",
            "confidence": 0.85,
            "reason": "Oversold stock with positive news sentiment"
        }

    # Strong SELL condition
    if rsi > 70 and macd < 0 and sentiment == "Negative":
        return {
            "decision": "SELL",
            "confidence": 0.85,
            "reason": "Overbought stock with negative news sentiment"
        }

    # Weak BUY
    if rsi < 35 and sentiment == "Positive":
        return {
            "decision": "BUY",
            "confidence": 0.65,
            "reason": "Positive sentiment with improving technicals"
        }

    # Weak SELL
    if rsi > 65 and sentiment == "Negative":
        return {
            "decision": "SELL",
            "confidence": 0.65,
            "reason": "Negative sentiment with weakening technicals"
        }

    # Default case
    return {
        "decision": "HOLD",
        "confidence": 0.50,
        "reason": "Mixed or neutral signals"
    }
