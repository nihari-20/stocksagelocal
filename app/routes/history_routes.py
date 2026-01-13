from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Indicator
from app.symbol_mapper import normalize_symbol
from app.services.history_service import get_indicator_history, get_red_history
from app.schemas import HistoryResponse, IndicatorHistoryItem, RedHistoryItem

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/get_history")
def get_original_history(symbol: str):
    db = SessionLocal()
    records = (
        db.query(Indicator)
        .filter(Indicator.symbol == symbol)
        .order_by(Indicator.created_at.desc())
        .all()
    )
    db.close()

    if not records:
        return {"error": "No history found for this symbol"}

    return [
        {
            "symbol": r.symbol,
            "RSI": round(r.rsi, 2),
            "SMA": round(r.sma, 2),
            "EMA": round(r.ema, 2),
            "MACD": round(r.macd, 2),
            "signal": r.signal,
            "timestamp": r.created_at
        }
        for r in records
    ]

@router.get("/history", response_model=HistoryResponse)
def get_history(
    symbol: str,
    market: str = "GLOBAL",
    limit: int = 20,
    db: Session = Depends(get_db)
):
    final_symbol, resolved_market = normalize_symbol(symbol, market)

    indicators = get_indicator_history(db, final_symbol, limit)
    red_results = get_red_history(db, final_symbol, limit)

    return {
        "symbol": final_symbol,
        "market": resolved_market,
        "indicators": [
            IndicatorHistoryItem(
                rsi=i.rsi,
                sma=i.sma,
                ema=i.ema,
                macd=i.macd,
                signal=i.signal,
                created_at=i.created_at
            )
            for i in indicators
        ],
        "ai": [
            RedHistoryItem(
                regime=r.regime,
                confidence=r.confidence,
                risk=r.risk,
                created_at=r.created_at
            )
            for r in red_results
        ] if red_results else None
    }
