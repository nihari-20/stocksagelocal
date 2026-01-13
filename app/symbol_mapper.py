# symbol_mapper.py
# STEP 1 – Stock Symbol Normalization (Indian + Global)

COMMON_SYMBOL_MAP = {
    # 🇮🇳 INDIAN STOCKS
    "tcs": "TCS",
    "tata consultancy services": "TCS",
    "reliance": "RELIANCE",
    "infosys": "INFY",
    "hdfc bank": "HDFCBANK",
    "icici bank": "ICICIBANK",
    "state bank of india": "SBIN",
    "sbi": "SBIN",
    "wipro": "WIPRO",
    "itc": "ITC",
    "larsen and toubro": "LT",
    "lt": "LT",

    # 🌍 GLOBAL STOCKS
    "apple": "AAPL",
    "apple inc": "AAPL",
    "tesla": "TSLA",
    "tesla inc": "TSLA",
    "google": "GOOGL",
    "alphabet": "GOOGL",
    "microsoft": "MSFT",
    "amazon": "AMZN",
    "meta": "META",
    "facebook": "META",
    "nvidia": "NVDA",
}


def normalize_symbol(symbol: str, market: str = "GLOBAL") -> str:
    if not symbol:
        return None

    cleaned = symbol.lower().strip()
    base_symbol = COMMON_SYMBOL_MAP.get(cleaned, symbol.upper())
    market = market.upper()

    # If symbol already has exchange suffix, trust it
    if base_symbol.endswith(".NS"):
        return base_symbol, "NSE"
    if base_symbol.endswith(".BO"):
        return base_symbol, "BSE"

    # Apply market routing
    if market == "NSE":
        return f"{base_symbol}.NS", "NSE"
    elif market == "BSE":
        return f"{base_symbol}.BO", "BSE"

    return base_symbol, "GLOBAL"
