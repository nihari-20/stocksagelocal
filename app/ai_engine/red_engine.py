def red_engine(
    tech_score: float,
    sentiment: dict,
    regime: str
):
    """
    RED Engine:
    Regime-based weighting
    Ensemble sentiment awareness
    Disagreement-aware HOLD logic
    """

    reasons = []
    score = 0.0
    risk = "Medium"

    # -------------------------------
    # 1. Regime-based weighting
    # -------------------------------
    if regime == "Trending":
        score += tech_score * 0.6
        score += sentiment["score"] * 0.4
        reasons.append("Trending market favors technical indicators")

    elif regime == "Volatile":
        score += tech_score * 0.4
        score += sentiment["score"] * 0.6
        reasons.append("Volatile market favors sentiment signals")
        risk = "High"

    else:  # Range-Bound or Uncertain
        score += tech_score * 0.5
        score += sentiment["score"] * 0.5
        reasons.append("Uncertain market leads to balanced weighting")

    # -------------------------------
    # 2. Disagreement handling
    # -------------------------------
    if sentiment["confidence"] < 0.4:
        reasons.append("Low agreement between sentiment models")
        return {
            "signal": "HOLD",
            "confidence": 35,
            "risk": risk,
            "reasons": reasons
        }

    # -------------------------------
    # -------------------------------
    # 3. Final decision
    # -------------------------------
    if score > 0.4:
        signal = "BUY"
        # Confidence increases as score moves away from 0.4 threshold towards 1.0
        # Range 0.4 -> 1.0 maps to roughly 50% -> 90%
        raw_conf = min(abs(score) * 100, 95)
    elif score < -0.4:
        signal = "SELL"
        raw_conf = min(abs(score) * 100, 95)
    else:
        signal = "HOLD"
        # For HOLD, peak confidence shouldn't be too high unless we are essentially flat.
        # Reduce peak from 90 to 75. 
        # dist is 1.0 (at score 0) to 0.0 (at score 0.4)
        dist = 1.0 - (abs(score) / 0.4) 
        
        # Base confidence for HOLD: 40% -> 75%
        # Add dynamic variance based on 'dist' so it's not always 73%
        # Use simple non-linear curve to add variety
        raw_conf = 40 + (dist * 35) + (score * 5) # add small perturbation based on sign of score

    # -------------------------------
    # 4. Mix in Input Confidence (Data Quality)
    # -------------------------------
    # If sentiment confidence is low (e.g. no news), drag down the result.
    # sentiment['confidence'] is typically 0.3 (no news) or 0.7 (news found).
    # Let's average it in with a weight.
    
    input_conf_factor = sentiment.get("confidence", 0.5) * 100
    
    # Final Confidence = Weighted avg of Signal Strength (70%) and Data Quality (30%)
    final_conf = (raw_conf * 0.7) + (input_conf_factor * 0.3)
    
    # Round to 1 decimal place to avoid int truncation "grouping" everything
    confidence = float(max(final_conf, 40))

    if confidence < 50:
        risk = "High"

    return {
        "signal": signal,
        "confidence": confidence,
        "risk": risk,
        "reasons": reasons
    }
