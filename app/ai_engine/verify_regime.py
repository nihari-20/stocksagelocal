import pandas as pd
import numpy as np
import sys
import os

# Add parent directory to path so we can import ai_engine
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.ai_engine.regime import detect_market_regime

def test_regime():
    print("Testing Market Regime AI...")
    
    # Case 1: Empty Data
    empty_prices = pd.Series([])
    empty_rsi = pd.Series([])
    res = detect_market_regime(empty_prices, empty_rsi)
    print(f"Empty Data: {res} (Expected: Uncertain)")
    assert res == "Uncertain"

    # Case 2: Short Data
    short_prices = pd.Series([100, 101, 102])
    short_rsi = pd.Series([50, 55, 60])
    res = detect_market_regime(short_prices, short_rsi)
    print(f"Short Data: {res} (Expected: Uncertain)")
    assert res == "Uncertain"

    # Case 3: Volatile
    # High variance returns
    vol_prices = pd.Series([100, 110, 90, 115, 85] * 10) 
    vol_rsi = pd.Series([50] * 50)
    res = detect_market_regime(vol_prices, vol_rsi)
    print(f"Volatile Data: {res} (Expected: Volatile)")
    assert res == "Volatile"
    
    # Case 4: Trending
    # Low vol, RSI high
    trend_prices = pd.Series(np.linspace(100, 150, 50))
    trend_rsi = pd.Series([70] * 50)
    res = detect_market_regime(trend_prices, trend_rsi)
    print(f"Trending Data: {res} (Expected: Trending)")
    assert res == "Trending"

    print("ALL TESTS PASSED")

if __name__ == "__main__":
    try:
        test_regime()
    except AssertionError as e:
        print("TEST FAILED")
        sys.exit(1)
    except Exception as e:
        print(f"CRASHED: {e}")
        sys.exit(1)
