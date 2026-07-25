from database.database import SessionLocal, MarketHistory
from services.tgju_service import get_market_prices


def update_market():

    print("UPDATE MARKET STARTED")

    data = get_market_prices()

    print("DATA =", data)

    if not data:
        print("NO DATA")
        return

    db = SessionLocal()

    try:

        row = MarketHistory(
            gold=data["gold"],
            usd=data["usd"],
            ounce=data["ounce"],
            coin=data["coin"]
        )

        db.add(row)
        db.commit()

        print("DATABASE UPDATED")

    except Exception as e:

        db.rollback()

        print("DATABASE ERROR:", e)

    finally:

        db.close()