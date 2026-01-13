from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import RedEngineResult
from app.schemas import RedEngineCreate, FusionResponse
from app.services.fusion_service import generate_fusion_insight
from app.symbol_mapper import normalize_symbol

router = APIRouter()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/red_engine/store")
def store_red_engine_result(
    data: RedEngineCreate,
    db: Session = Depends(get_db)
):
    record = RedEngineResult(
        symbol=data.symbol,
        market=data.market,
        regime=data.regime,
        confidence=data.confidence,
        risk=data.risk
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    return {
        "message": "RED engine result stored successfully",
        "symbol": record.symbol,
        "market": record.market,
        "regime": record.regime,
        "confidence": record.confidence,
        "risk": record.risk
    }

@router.get("/fusion/insight", response_model=FusionResponse)
def fusion_insight(symbol: str, market: str = "GLOBAL", db: Session = Depends(get_db)):
    # Normalize symbol
    final_symbol, resolved_market = normalize_symbol(symbol, market)
    
    insight = generate_fusion_insight(final_symbol, resolved_market, db)
    
    if not insight:
        raise HTTPException(status_code=404, detail=f"Not enough data to generate insight for {final_symbol}")
        
    return insight
