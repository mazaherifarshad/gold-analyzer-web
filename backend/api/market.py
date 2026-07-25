from fastapi import APIRouter, HTTPException
from sqlalchemy import desc

from database.database import (
    SessionLocal,
    MarketHistory
)

from services.tgju import get_market_data

router = APIRouter(
    tags=["Market"]
)


@router.get("/market/live")
def market_live():

    try:

        return get_market_data()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )


@router.get("/market/latest")
def market_latest():

    db = SessionLocal()

    try:

        row = (

            db.query(MarketHistory)

            .order_by(desc(MarketHistory.id))

            .first()

        )

        if row is None:

            raise HTTPException(

                status_code=404,

                detail="No market data found"

            )

        return {

            "gold": row.gold,

            "usd": row.usd,

            "ounce": row.ounce,

            "coin": row.coin,

            "time": row.created_at

        }

    finally:

        db.close()


@router.get("/market/history")
def market_history(limit: int = 300):

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