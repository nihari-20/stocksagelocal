import requests
import sys
import time

BASE_URL = "http://127.0.0.1:8000"

def test_endpoint(name, url):
    print(f"Testing {name} ({url})...", end=" ")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            print("✅ OK")
            try:
                print(response.json())
            except:
                print("(No JSON)")
            return True
        else:
            print(f"❌ Failed (Status: {response.status_code})")
            print(response.text)
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Connection Failed. Is the server running?")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("--- Backend Integration Verification ---")
    print(f"Target: {BASE_URL}")
    
    # 1. Check Root
    if not test_endpoint("Root", f"{BASE_URL}/"):
        print("!! Please ensure the backend is running via: uvicorn main:app --reload")
        sys.exit(1)

    # 2. Market Pulse
    test_endpoint("Market Pulse", f"{BASE_URL}/market-pulse")
    
    # 3. Trending
    test_endpoint("Trending", f"{BASE_URL}/trending")
    
    # 4. Search
    test_endpoint("Search (TCS)", f"{BASE_URL}/search?q=tcs")
    
    # 5. News
    test_endpoint("General News", f"{BASE_URL}/news")
    
    # 6. Insight (using fusion endpoint)
    # Use a symbol that likely works, e.g., AAPL if yfinance works
    test_endpoint("Stock Detail (AAPL)", f"{BASE_URL}/stock/AAPL")
    test_endpoint("Fusion Insight (AAPL)", f"{BASE_URL}/fusion/insight?symbol=AAPL")

    print("\n--- Done ---")

if __name__ == "__main__":
    main()
