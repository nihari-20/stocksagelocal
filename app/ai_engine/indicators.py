import pandas as pd
import numpy as np

# =====================================================
# Relative Strength Index (RSI)
# =====================================================
def calculate_rsi(close_prices: pd.Series, period: int = 14) -> pd.Series:
    """
    RSI measures momentum to identify overbought or oversold conditions.
    """
    delta = close_prices.diff()

    gain = delta.where(delta > 0, 0.0)
    loss = -delta.where(delta < 0, 0.0)

    avg_gain = gain.rolling(window=period, min_periods=period).mean()
    avg_loss = loss.rolling(window=period, min_periods=period).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi


# =====================================================
# Simple Moving Average (SMA)
# =====================================================
def calculate_sma(close_prices: pd.Series, period: int) -> pd.Series:
    """
    SMA calculates the average price over a fixed period.
    """
    return close_prices.rolling(window=period).mean()


# =====================================================
# Exponential Moving Average (EMA)
# =====================================================
def calculate_ema(close_prices: pd.Series, period: int) -> pd.Series:
    """
    EMA gives more weight to recent prices for faster reaction.
    """
    return close_prices.ewm(span=period, adjust=False).mean()


# =====================================================
# Moving Average Convergence Divergence (MACD)
# =====================================================
def calculate_macd(close_prices: pd.Series):
    """
    MACD identifies trend direction and momentum.
    """
    ema_12 = calculate_ema(close_prices, 12)
    ema_26 = calculate_ema(close_prices, 26)

    macd_line = ema_12 - ema_26
    signal_line = macd_line.ewm(span=9, adjust=False).mean()
    histogram = macd_line - signal_line

    return macd_line, signal_line, histogram
