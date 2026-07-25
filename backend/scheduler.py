from apscheduler.schedulers.background import BackgroundScheduler

from services.market_updater import update_market

scheduler = BackgroundScheduler()


def start_scheduler():

    print("STARTING SCHEDULER...")

    update_market()      # اجرای فوری

    scheduler.add_job(
        update_market,
        "interval",
        minutes=1,
        max_instances=1,
        coalesce=True
    )

    scheduler.start()

    print("SCHEDULER STARTED")