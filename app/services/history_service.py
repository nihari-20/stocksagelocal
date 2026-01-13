from sqlalchemy.orm import Session
from app.models import Indicator, RedEngineResult

def get_indicator_history(db: Session, symbol: str, limit: int = 20):
    return (
        db.query(Indicator)
        .filter(Indicator.symbol == symbol)
        .order_by(Indicator.created_at.desc())
        .limit(limit)
        .all()
    )

def get_red_history(db: Session, symbol: str, limit: int = 20):
    return (
        db.query(RedEngineResult)
        .filter(RedEngineResult.symbol == symbol)
        .order_by(RedEngineResult.created_at.desc())
        .limit(limit)
        .all()
    )
