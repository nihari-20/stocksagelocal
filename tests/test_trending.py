from fetcher import fetch_indices

def test_trending_fetch():
    trending_symbols = ["TCS.NS", "IDEA.NS", "AAPL", "TSLA"]
    import time
    start_time = time.time()
    results = fetch_indices(trending_symbols)
    end_time = time.time()
    print(f"Fetch took {end_time - start_time:.2f} seconds")
    
    print("\n--- Raw Results from fetcher ---")
    for sym, data in results.items():
        print(f"{sym}: {data}")

    print("\n--- Mocking main.py processing ---")
    trending_list = []
    for sym in trending_symbols:
        s_data = results.get(sym)
        if s_data:
            change = s_data['change']
            action = "Hold"
            if change > 1.5: action = "Strong Buy"
            elif change > 0.5: action = "Buy"
            elif change < -1.5: action = "Strong Sell"
            elif change < -0.5: action = "Sell"

            # Replicate main.py formatting
            item = {
                "symbol": sym,
                "name": sym,
                "price": f"{s_data['price']:.2f}",
                "change": f"{s_data['change']:.2f}%", 
                "isPositive": s_data['change'] >= 0,
                "currency": "USD" if "NS" not in sym else "INR",
                "action": action
            }
            trending_list.append(item)
            print(f"✅ Processed {sym}: {item}")
        else:
            print(f"❌ Failed to fetch {sym}")

    print(f"\nTotal items ready for frontend: {len(trending_list)}")

if __name__ == "__main__":
    test_trending_fetch()
