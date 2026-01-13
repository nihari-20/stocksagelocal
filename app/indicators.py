import pandas as pd

def calculate_indicators_df(prices):
    df = prices.to_frame(name="close")

    # SMA
    df["sma"] = df["close"].rolling(window=14).mean()

    # EMA
    df["ema"] = df["close"].ewm(span=14, adjust=False).mean()

    # RSI
    delta = df["close"].diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(window=14).mean()
    avg_loss = loss.rolling(window=14).mean()

    rs = avg_gain / avg_loss
    df["rsi"] = 100 - (100 / (1 + rs))

    # MACD
    ema_12 = df["close"].ewm(span=12, adjust=False).mean()
    ema_26 = df["close"].ewm(span=26, adjust=False).mean()
    df["macd"] = ema_12 - ema_26

    # ✅ CRITICAL FIX: remove NaN rows
    df = df.dropna()
    
    return df

def calculate_indicators(prices):
    df = calculate_indicators_df(prices)
    if df.empty:
        return None 
    return df.iloc[-1]

def generate_signal(rsi, macd):
    if rsi < 30 and macd > 0:
        return "BUY"
    elif rsi > 70 and macd < 0:
        return "SELL"
    else:
        return "HOLD"

