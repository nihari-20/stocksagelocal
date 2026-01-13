import numpy as np
import pandas as pd


def detect_market_regime(close_prices: pd.Series, rsi_series: pd.Series):
    """
    Detects the current market regime using volatility and RSI behavior.

    Returns:
        regime: Trending | Range-Bound | Volatile | Uncertain
    """

    # Daily returns
    returns = close_prices.pct_change().dropna()

    # Need at least a few points to calculate vol
    if len(returns) < 5:
        return "Uncertain"

    # ✅ FIX: ensure volatility is a scalar
    volatility = float(np.std(returns.values)) if len(returns) > 0 else 0.0

    # RSI characteristics
    try:
        # Get up to last 20 points, but handle if we have fewer
        recent_rsi = rsi_series.dropna()
        if recent_rsi.empty:
             return "Uncertain"
             
        recent_rsi = recent_rsi.iloc[-20:]
        
        rsi_range = float(recent_rsi.max() - recent_rsi.min())
        latest_rsi = float(recent_rsi.iloc[-1])
    except Exception:
        # Fallback if calculation fails
        return "Uncertain"

    # ----- Regime rules -----
    if volatility > 0.025:
        return "Volatile"

    if latest_rsi > 60 or latest_rsi < 40:
        return "Trending"

    if rsi_range < 15:
        return "Range-Bound"

    return "Uncertain"
