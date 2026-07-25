# -*- coding: utf-8 -*-
from backend.database.connection import session_scope
from backend.database.models import MarketHistory, MarketCandle
from backend.candle.candle_engine import CandleEngine
from datetime import datetime, timedelta

print("=" * 50)
print("DEBUGGING CANDLE ENGINE")
print("=" * 50)

# 1. بررسی تیک‌های موجود
with session_scope() as session:
    # حذف داده‌های تست قبلی
    session.query(MarketHistory).filter(MarketHistory.symbol == 'test_gold').delete()
    
    # اضافه کردن تیک‌های تست با زمان‌های دقیق‌تر
    now = datetime.now()
    test_ticks = [
        (100, now - timedelta(minutes=10)),
        (101, now - timedelta(minutes=9)),
        (102, now - timedelta(minutes=8)),
        (101.5, now - timedelta(minutes=7)),
        (103, now - timedelta(minutes=6)),
        (102.5, now - timedelta(minutes=5)),
        (103.5, now - timedelta(minutes=4)),
        (104, now - timedelta(minutes=3)),
        (103, now - timedelta(minutes=2)),
        (104.5, now - timedelta(minutes=1)),
    ]
    
    for price, time in test_ticks:
        tick = MarketHistory(
            symbol='test_gold',
            price=price,
            created_at=time,
            source='test'
        )
        session.add(tick)
    print("✅ 10 تیک تست اضافه شد!")

# 2. چک کردن تعداد تیک‌ها
with session_scope() as session:
    count = session.query(MarketHistory).filter(MarketHistory.symbol == 'test_gold').count()
    print(f"📊 تعداد تیک‌های test_gold: {count}")

# 3. ساخت شمع با موتور
print("\n🔄 در حال ساخت شمع...")
engine = CandleEngine()

# ساخت شمع برای یک تایم‌فریم خاص
candle_count = engine.build_all_candles_for_symbol('test_gold', '1m')
print(f"✅ شمع‌های ساخته شده برای 1m: {candle_count}")

# 4. چک کردن شمع‌های ساخته شده
with session_scope() as session:
    candles = session.query(MarketCandle).filter(
        MarketCandle.symbol == 'test_gold'
    ).all()
    print(f"\n📊 تعداد کل شمع‌های test_gold: {len(candles)}")
    
    if candles:
        print("\n📋 آخرین شمع‌ها:")
        for c in candles[-3:]:
            print(f"  {c.candle_time} | O:{c.open} H:{c.high} L:{c.low} C:{c.close}")

# 5. تست ساخت تمام تایم‌فریم‌ها
print("\n🔄 ساخت تمام تایم‌فریم‌ها...")
results = engine.build_all_timeframes('test_gold')

print("\n" + "=" * 50)
print("RESULTS:")
for tf, count in results.items():
    print(f"  {tf}: {count} candles")

print("\n" + "=" * 50)
print("DEBUG COMPLETE!")