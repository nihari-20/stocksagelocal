# market_router.py
# STEP 2 – Market Selection Routing

from fetcher import fetch_prices

def fetch_market_prices(symbol: str, market: str):
    """
    Route data fetching based on market
    """

    market = market.upper()

    if market in ["NSE", "BSE"]:
        # Indian markets still use Yahoo Finance,
        # but symbol already has .NS or .BO
        return fetch_prices(symbol)

    # Global market
    return fetch_prices(symbol)
