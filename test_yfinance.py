import yfinance as yf
import pandas as pd

def test_fetch():
    indices = ["^NSEI", "^BSESN", "^GSPC", "^CNX500"]
    print(f"Fetching indices: {indices}")
    try:
        data = yf.download(indices, period="5d", group_by='ticker', threads=False, progress=False)
        print("\nData Columns:")
        print(data.columns)
        print("\nData Head:")
        print(data.head())
        
        print("\nChecking structure expectations...")
        if isinstance(data.columns, pd.MultiIndex):
            print("Columns are MultiIndex.")
            if "^NSEI" in data.columns.levels[0]:
                 print("^NSEI found in level 0.")
            else:
                 print("^NSEI NOT found in level 0. Level 0 values:", data.columns.levels[0])
        else:
            print("Columns are NOT MultiIndex.")
            
    except Exception as e:
        print(f"Error fetching indices: {e}")

    print("\n----------------\n")
    
    symbol = "AAPL"
    print(f"Fetching single symbol: {symbol}")
    try:
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1y")
        print(f"History empty? {hist.empty}")
        if not hist.empty:
            print(hist.head())
        
        info = stock.info
        print("Info keys sample:", list(info.keys())[:5])
    except Exception as e:
        print(f"Error fetching single symbol: {e}")

if __name__ == "__main__":
    test_fetch()
