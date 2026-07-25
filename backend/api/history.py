from fastapi import APIRouter
from sqlalchemy import desc

from database.database import (
    SessionLocal,
    MarketHistory
)

router = APIRouter(
    tags=["History"]
)


@router.get("/history")
def history(limit: int = 500):

    db = SessionLocal()

    try:

        rows = (
            db.query(MarketHistory)
            .order_by(desc(MarketHistory.id))
            .limit(limit)
            .all()
        )

        rows.reverse()

        return [
            {
                "id": r.id,
                "gold": r.gold,
                "usd": r.usd,
                "ounce": r.ounce,
                "coin": r.coin,
                "time": r.created_at
            }
            for r in rows
        ]

    finally:
        db.close()