from apscheduler.schedulers.background import BackgroundScheduler

from config import UPDATE_INTERVAL

from database.database import (
    SessionLocal,
    MarketHistory
)

from services.tgju import get_market_data
from services.logger import logger


scheduler = BackgroundScheduler()


def update_market():

    db = SessionLocal()

    try:

        market = get_market_data()

        row = MarketHistory(

            gold=market["gold"],

            usd=market["usd"],

            ounce=market["ounce"],

            coin=market["coin"]

        )

        db.add(row)

        db.commit()

        logger.info("Market Saved")

    except Exception as e:

        logger.error(f"Scheduler Error : {e}")

    finally:

        db.close()


def start_scheduler():

    if scheduler.running:
        return

    scheduler.add_job(

        update_market,

        trigger="interval",

        seconds=UPDATE_INTERVAL,

        max_instances=1,

        replace_existing=True,

        id="market_update"

    )

    update_market()

    scheduler.start()

    logger.info("Scheduler Started")