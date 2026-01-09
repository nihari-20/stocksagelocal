import yfinance as yf

def fetch_prices(symbol: str):
    # Try fetching as provided
    stock = yf.Ticker(symbol)
    data = stock.history(period="6mo")

    if data.empty:
        # Retry with .NS if not present and likely an Indian stock (or just retry generic)
        if not symbol.endswith(".NS") and not symbol.endswith(".BO"):
            print(f"Retrying {symbol} as {symbol}.NS...")
            stock = yf.Ticker(f"{symbol}.NS")
            data = stock.history(period="6mo")
            
        if data.empty:
            return None

    return data["Close"]

def fetch_indices(symbols: list[str]):
    results = {}
    for symbol in symbols:
        try:
            # Iterative fetch is slower but more robust against partial failures/timeouts
            stock = yf.Ticker(symbol)
            # Fetch slightly more data to ensure we have at least 2 days
            hist = stock.history(period="1mo")
            
            if hist.empty:
                print(f"No data found for {symbol}")
                continue
            
            # Use 'Close' column and drop NaNs
            closes = hist['Close'].dropna()
            
            if len(closes) >= 2:
                current = float(closes.iloc[-1])
                prev = float(closes.iloc[-2])
                
                # Double check for NaN (float('nan'))
                import math
                if math.isnan(current) or math.isnan(prev):
                     print(f"NaN data detected for {symbol}")
                     continue

                change = ((current - prev) / prev) * 100
                
                results[symbol] = {
                    "price": current,
                    "change": change
                }
            else:
                 print(f"Not enough data for {symbol} (len={len(closes)})")

        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue
            
    return results

def fetch_stock_details(symbol: str):
    try:
        stock = yf.Ticker(symbol)
        # Get history (1y for chart)
        hist = stock.history(period="1y")
        
        if hist.empty:
            return None
            
        # Get info
        info = stock.info
        
        # Calculate current params
        current_price = info.get('currentPrice', info.get('regularMarketPrice', hist['Close'].iloc[-1]))
        prev_close = info.get('previousClose', hist['Close'].iloc[-2] if len(hist) > 1 else current_price)
        change_pct = ((current_price - prev_close) / prev_close) * 100 if prev_close else 0.0
        currency = info.get('currency', 'USD') # Default USD
        
        # Format history
        # Frontend expects List<Map<String, dynamic>> with 'value' key?
        # Actually StockDetailScreen uses:
        # history.asMap().entries.map((e) => FlSpot(e.key.toDouble(), e.value['value']...))
        # Wait, the code says: `history = List<Map<String, dynamic>>.from(data['history']);` and `e.value['value']`.
        # So it expects a list of objects with a 'value' property.
        
        history_list = []
        for date, row in hist.iterrows():
            history_list.append({
                "time": date.strftime("%Y-%m-%d"),
                "value": row['Close']
            })
            
        # Stats
        stats = {
            "Open": info.get('open', hist['Open'].iloc[-1]),
            "High": info.get('dayHigh', hist['High'].iloc[-1]),
            "Low": info.get('dayLow', hist['Low'].iloc[-1]),
            "Vol": info.get('volume', hist['Volume'].iloc[-1]),
            "P/E": info.get('trailingPE', "N/A"),
            "Mkt Cap": info.get('marketCap', "N/A"),
            "52W High": info.get('fiftyTwoWeekHigh', "N/A"),
            "52W Low": info.get('fiftyTwoWeekLow', "N/A"),
        }
        
        return {
            "symbol": symbol,
            "price": current_price,
            "change_percent": change_pct,
            "currency": currency,
            "history": history_list,
            "stats": stats
        }
        
    except Exception as e:
        print(f"Error fetching details for {symbol}: {e}")
        return None
