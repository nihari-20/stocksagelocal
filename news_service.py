import os
import requests

API_KEY = os.getenv("NEWS_API_KEY")
BASE_URL = "https://newsapi.org/v2/everything"

def fetch_stock_news(symbol: str):
    if not API_KEY:
        # Return mock news for demonstration/fallback
        return [
            {"title": "Global Markets Rally: Live Updates and Trends", "url": "https://www.google.com/search?q=Global+Stock+Markets+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1611974765270-ca1258634369?w=400", "source": {"name": "MarketWatch"}},
            {"title": "Technology Sector Surges: Weekly Performance Review", "url": "https://www.google.com/search?q=Tech+Sector+Stocks+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=400", "source": {"name": "Bloomberg"}},
            {"title": "Federal Reserve Cuts Rates: Latest Analyst Insights", "url": "https://www.google.com/search?q=Federal+Reserve+Interest+Rates+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1580519542036-c47de6196ba5?w=400", "source": {"name": "Reuters"}},
            {"title": "Energy Prices Drop: Market Outlook", "url": "https://www.google.com/search?q=Oil+Prices+Energy+Market+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1560958089-b8a1929cea89?w=400", "source": {"name": "TechCrunch"}},
            {"title": "Cryptocurrency Bull Run: Bitcoin & Ethereum Moves", "url": "https://www.google.com/search?q=Cryptocurrency+Market+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1518546305927-5a555bb7020d?w=400", "source": {"name": "CoinDesk"}},
            {"title": "Consumer Tech Growth: New Product Announcements", "url": "https://www.google.com/search?q=Consumer+Technology+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1531297461136-82lw9z1p1b?w=400", "source": {"name": "The Verge"}},
            {"title": "Retail Sector Gains: Consumer Spending Trends", "url": "https://www.google.com/search?q=Retail+Stocks+Consumer+Spending+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1523474253046-8cd2748b5fd2?w=400", "source": {"name": "CNBC"}},
            {"title": "Supply Chain Issues Ease: Manufacturing Updates", "url": "https://www.google.com/search?q=Global+Supply+Chain+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?w=400", "source": {"name": "WSJ"}},
            {"title": "Streaming Wars Intensify: Media & Entertainment News", "url": "https://www.google.com/search?q=Streaming+Services+Stock+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1574375927938-d5a98e8ffe85?w=400", "source": {"name": "Variety"}},
            {"title": "AI Revolution Soars: Artificial Intelligence Market News", "url": "https://www.google.com/search?q=Artificial+Intelligence+Stocks+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1573804633927-bfcbcd909acd?w=400", "source": {"name": "TechRadar"}},
            {"title": "Gaming Industry Mergers: Major Acquisitions", "url": "https://www.google.com/search?q=Video+Game+Industry+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1583511655857-d19b40a7a54e?w=400", "source": {"name": "Polygon"}},
            {"title": "EV Market Charges Ahead: Electric Vehicle Sector Update", "url": "https://www.google.com/search?q=Electric+Vehicle+Market+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1626804475297-411d8c6b7j4g?w=400", "source": {"name": "MotorTrend"}},
            {"title": "Space Economy Blasts Off: Aerospace & Defense News", "url": "https://www.google.com/search?q=Space+Industry+Stocks+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1517976487492-5750f3195933?w=400", "source": {"name": "Space.com"}},
            {"title": "Financial Sector Stable: Banking & Finance Updates", "url": "https://www.google.com/search?q=Banking+Sector+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1556740758-90de29294860?w=400", "source": {"name": "Forbes"}},
            {"title": "Real Estate Market Cools: Trends and Analysis", "url": "https://www.google.com/search?q=Real+Estate+Market+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=400", "source": {"name": "Zillow"}},
            {"title": "Green Tech Boom: Renewable Energy Developments", "url": "https://www.google.com/search?q=Renewable+Energy+Stocks+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=400", "source": {"name": "CleanTech"}},
            {"title": "Biotech Breakthrough: Latest Clinical Trials", "url": "https://www.google.com/search?q=Biotech+Pharma+Stock+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1584308666744-24d5c474f2ae?w=400", "source": {"name": "MedicalNews"}},
            {"title": "Remote Work Trends: Office Sector Weakness", "url": "https://www.google.com/search?q=Remote+Work+Trends+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1614728853970-3d77d13t2r?w=400", "source": {"name": "Business Insider"}},
            {"title": "Startup Scene Active: Venture Capital & funding", "url": "https://www.google.com/search?q=Venture+Capital+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1559136555-930d72f1d37c?w=400", "source": {"name": "TechCrunch"}},
            {"title": "Travel Rebound: Industry Recovery Report", "url": "https://www.google.com/search?q=Travel+Industry+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=400", "source": {"name": "Skift"}},
            {"title": "Semiconductor Demand High: Chip Market News", "url": "https://www.google.com/search?q=Semiconductor+Industry+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1555664424-778a69fbb007?w=400", "source": {"name": "AnandTech"}},
            {"title": "Currency Markets Active: Forex Weekly Wrap", "url": "https://www.google.com/search?q=Forex+Market+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1622630998477-20aa696c6604?w=400", "source": {"name": "ForexLive"}},
            {"title": "GDP Growth Solid: Economic Outlook", "url": "https://www.google.com/search?q=Global+Economy+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1563986768494-4dee46246bs6?w=400", "source": {"name": "CNBC"}},
            {"title": "Creative Tools Update: Digital Design News", "url": "https://www.google.com/search?q=Creative+Software+Industry+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1626785774573-4b799312c532?w=400", "source": {"name": "TheVerge"}},
            {"title": "Video Conferencing Shifts: Communication Tech Trends", "url": "https://www.google.com/search?q=Video+Conferencing+Market+News+latest&tbs=qdr:m", "urlToImage": "https://images.unsplash.com/photo-1588196749597-9ff075ee6b5b?w=400", "source": {"name": "Yahoo Finance"}}
        ]

    params = {
        "q": f"{symbol} stock",
        "language": "en",
        "sortBy": "publishedAt",
        "pageSize": 25,
        "apiKey": API_KEY
    }

    try:
        response = requests.get(BASE_URL, params=params, timeout=5)
        if response.status_code != 200:
            return []
        return response.json().get("articles", [])
    except Exception:
        return []
