from pydantic import BaseModel
from datetime import datetime

# ---------- Request Schemas ----------

class StockRequest(BaseModel):
    symbol: str


# ---------- Response Schemas ----------

class PriceResponse(BaseModel):
    symbol: str
    prices: dict[str, float]


class IndicatorResponse(BaseModel):
    symbol: str
    RSI: float
    SMA: float
    EMA: float
    MACD: float
    signal: str


class IndicatorHistoryResponse(BaseModel):
    symbol: str
    RSI: float
    SMA: float
    EMA: float
    MACD: float
    signal: str
    timestamp: datetime



class RedEngineCreate(BaseModel):
    symbol: str
    market: str
    regime: str          # BULL / BEAR / SIDEWAYS
    confidence: float    # 0 - 100
    risk: str            # LOW / MEDIUM / HIGH


class RedEngineResponse(BaseModel):
    message: str
    symbol: str
    market: str
    regime: str
    confidence: float
    risk: str

from pydantic import BaseModel
from typing import Optional


# =========================
# TECHNICAL INDICATORS
# =========================
class TechnicalIndicators(BaseModel):
    RSI: float
    SMA: float
    EMA: float
    MACD: float
    signal: str


# =========================
# AI (RED ENGINE)
# =========================
class AIInsight(BaseModel):
    regime: str
    confidence: float
    risk: str


# =========================
# FUSION RESPONSE (FINAL)
# =========================
class FusionResponse(BaseModel):
    symbol: str
    market: str
    technical: TechnicalIndicators
    ai: Optional[AIInsight] = None   # backward compatible
    pros: List[str] = []
    cons: List[str] = []


from datetime import datetime
from typing import List, Optional

class IndicatorHistoryItem(BaseModel):
    rsi: float
    sma: float
    ema: float
    macd: float
    signal: str
    created_at: datetime


class RedHistoryItem(BaseModel):
    regime: str
    confidence: float
    risk: str
    created_at: datetime


class HistoryResponse(BaseModel):
    symbol: str
    market: str
    indicators: List[IndicatorHistoryItem]
    ai: Optional[List[RedHistoryItem]] = None
