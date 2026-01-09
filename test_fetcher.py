from fetcher import fetch_indices, fetch_stock_details
import time

def test_fetcher_module():
    indices = ["^NSEI", "^BSESN", "^GSPC", "^CNX500"]
    print(f"Testing fetch_indices with: {indices}")
    
    start = time.time()
    results = fetch_indices(indices)
    end = time.time()
    
    print(f"Time taken: {end - start:.2f}s")
    print("Results:")
    for sym, data in results.items():
        print(f"{sym}: {data}")
        
    print("\n----------------\n")
    
    symbol = "AAPL"
    print(f"Testing fetch_stock_details for {symbol}")
    details = fetch_stock_details(symbol)
    if details:
        print(f"Symbol: {details['symbol']}")
        print(f"Price: {details['price']}")
        print(f"History len: {len(details['history'])}")
    else:
        print("Details fetch failed.")

if __name__ == "__main__":
    test_fetcher_module()
