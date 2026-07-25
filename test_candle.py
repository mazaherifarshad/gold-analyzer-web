# -*- coding: utf-8 -*-
from backend.candle.candle_engine import build_candles_for_all_symbols
from backend.database.connection import session_scope
from backend.database.models import MarketHistory
from datetime import datetime, timedelta  # <-- این خط اضافه شد

print("=" * 50)
print("TESTING CANDLE ENGINE")
print("=" * 50)

# اول چند تیک تست اضافه می‌کنیم
with session_scope() as session:
    # حذف داده‌های تست قبلی
    session.query(MarketHistory).filter(MarketHistory.symbol == 'test_gold').delete()
    
    # اضافه کردن تیک‌های تست
    test_ticks = [
        (100, datetime.now() - timedelta(minutes=5)),
        (101, datetime.now() - timedelta(minutes=4)),
        (102, datetime.now() - timedelta(minutes=3)),
        (101.5, datetime.now() - timedelta(minutes=2)),
        (103, datetime.now() - timedelta(minutes=1)),
        (102.5, datetime.now()),
    ]
    
    for price, time in test_ticks:
        tick = MarketHistory(
            symbol='test_gold',
            price=price,
            created_at=time,
            source='test'
        )
        session.add(tick)
    print("✅ Test ticks added!")

# حالا شمع‌ها را می‌سازیم
print("\nBuilding candles...")
results = build_candles_for_all_symbols()

print("\n" + "=" * 50)
print("RESULTS:")
for symbol, timeframes in results.items():
    print(f"\n{symbol}:")
    for tf, count in timeframes.items():
        print(f"  {tf}: {count} candles")

print("\n" + "=" * 50)
print("CANDLE ENGINE TEST COMPLETE!")