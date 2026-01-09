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

    if len(returns) < 20:
        return "Uncertain"

    # ✅ FIX: ensure volatility is a scalar
    volatility = float(np.std(returns.values))

    # RSI characteristics
    recent_rsi = rsi_series.dropna().iloc[-20:]
    rsi_range = float(recent_rsi.max() - recent_rsi.min())
    latest_rsi = float(recent_rsi.iloc[-1])

    # ----- Regime rules -----
    if volatility > 0.025:
        return "Volatile"

    if rsi_range < 15:
        return "Range-Bound"

    if latest_rsi > 60 or latest_rsi < 40:
        return "Trending"

    return "Uncertain"
