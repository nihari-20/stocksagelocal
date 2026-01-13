def generate_explanation(
    signal: str,
    confidence: int,
    reasons: list,
    regime: str,
    risk: str,
    sentiment_confidence: float = None
):
    """
    Generates a detailed, human-readable explanation
    for RED Engine decisions.
    """

    summary_map = {
        "BUY": "The system detected aligned bullish signals indicating a potential upside opportunity.",
        "SELL": "The system detected aligned bearish signals indicating potential downside risk.",
        "HOLD": "The system detected uncertainty or conflicting signals and avoided taking a strong position."
    }

    explanation = {
        "signal": signal,
        "confidence": confidence,
        "risk": risk,
        "market_regime": regime,
        "summary": summary_map.get(signal, "Market condition unclear."),
        "reasons": reasons
    }

    # --- Explicit HOLD explanation ---
    if signal == "HOLD":
        explanation["why_hold"] = (
            "The decision was downgraded to HOLD due to uncertainty, signal disagreement, "
            "or insufficient confidence in current market conditions."
        )

    # --- Low confidence explanation ---
    if confidence < 50:
        explanation["low_confidence_reason"] = (
            "Low confidence indicates weak signal alignment or unstable market behavior."
        )

    # --- Sentiment disagreement explanation ---
    if sentiment_confidence is not None and sentiment_confidence < 0.4:
        explanation["sentiment_disagreement"] = (
            "Multiple sentiment models disagreed, reducing reliability of sentiment signals."
        )

    return explanation
