from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime
from app.database import Base

# =========================
# EXISTING INDICATORS TABLE
# =========================
class Indicator(Base):
    __tablename__ = "indicators"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)

    rsi = Column(Float)
    sma = Column(Float)
    ema = Column(Float)
    macd = Column(Float)

    signal = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


# =========================
# NEW: RED ENGINE RESULTS
# =========================
class RedEngineResult(Base):
    __tablename__ = "red_engine_results"

    id = Column(Integer, primary_key=True, index=True)

    symbol = Column(String, index=True)
    market = Column(String)

    regime = Column(String)        # BULL / BEAR / SIDEWAYS
    confidence = Column(Float)     # 0–100
    risk = Column(String)          # LOW / MEDIUM / HIGH

    created_at = Column(DateTime, default=datetime.utcnow)
