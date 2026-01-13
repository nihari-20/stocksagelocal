import requests

def test_search():
    q = "AAPL"
    url = "https://query2.finance.yahoo.com/v1/finance/search"
    params = {
        "q": q,
        "quotesCount": 10,
        "newsCount": 0,
        "enableFuzzyQuery": "false",
        "quotesQueryId": "tss_match_phrase_query"
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    print(f"Searching for {q}...")
    try:
        response = requests.get(url, params=params, headers=headers, timeout=5)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Quotes found:", len(data.get("quotes", [])))
            if "quotes" in data and len(data["quotes"]) > 0:
                print("First quote:", data["quotes"][0].get("symbol"))
        else:
            print("Response:", response.text)
    except Exception as e:
        print(f"Search failed: {e}")

if __name__ == "__main__":
    test_search()
