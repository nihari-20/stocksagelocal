from fetcher import fetch_indices
import json

def test_indian():
    symbols = ["TCS.NS", "RELIANCE.NS"]
    results = fetch_indices(symbols)
    
    with open("indian_stock_results.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    test_indian()
