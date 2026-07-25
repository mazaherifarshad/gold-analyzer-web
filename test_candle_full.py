# -*- coding: utf-8 -*-
"""
تست کامل شمع‌سازی با داده‌های واقعی
"""

from backend.database.connection import session_scope
from backend.database.models import MarketHistory, MarketCandle
from backend.services.tgju import TGJUClient
from backend.candle.candle_engine import build_candles_for_all_symbols, CandleEngine
from datetime import datetime, timedelta
import time

print("=" * 60)
print("FULL CANDLE ENGINE TEST")
print("=" * 60)

# 1. دریافت چندین تیک با فاصله زمانی
print("\n📊 Fetching multiple ticks...")
client = TGJUClient()

# دریافت ۵ تیک با فاصله ۱ دقیقه
with session_scope() as session:
    symbol = 'gold'
    
    # حذف تیک‌های قبلی برای این نماد
    session.query(MarketHistory).filter(MarketHistory.symbol == symbol).delete()
    
    # دریافت ۵ تیک متوالی با فاصله ۱ دقیقه
    for i in range(5):
        price_data = client.get_current_prices()
        if price_data and symbol in price_data:
            tick_time = datetime.now() - timedelta(minutes=(5 - i))
            tick = MarketHistory(
                symbol=symbol,
                price=price_data[symbol],
                created_at=tick_time,
                source='tgju'
            )
            session.add(tick)
            print(f"  ✅ Tick {i+1}: {price_data[symbol]:,.2f} at {tick_time.strftime('%H:%M:%S')}")
            time.sleep(1)  # فاصله ۱ ثانیه بین تیک‌ها
    
    session.commit()

# 2. ساخت شمع
print("\n🔄 Building candles...")
engine = CandleEngine()
candle_count = engine.build_all_candles_for_symbol('gold', '1m')
print(f"  ✅ {candle_count} candles built for 1m")

# 3. بررسی شمع‌های ساخته شده
with session_scope() as session:
    candles = session.query(MarketCandle).filter(
        MarketCandle.symbol == 'gold',
        MarketCandle.timeframe == '1m'
    ).order_by(MarketCandle.candle_time.desc()).all()
    
    print(f"\n📊 Found {len(candles)} candles:")
    for c in candles[:5]:  # نمایش ۵ شمع آخر
        print(f"  {c.candle_time.strftime('%H:%M')} | O:{c.open:,.2f} H:{c.high:,.2f} L:{c.low:,.2f} C:{c.close:,.2f}")

# 4. ساخت تمام تایم‌فریم‌ها
print("\n🔄 Building all timeframes...")
results = build_candles_for_all_symbols()

print("\n" + "=" * 60)
print("FINAL RESULTS:")
print("=" * 60)
for symbol, timeframes in results.items():
    if timeframes:
        print(f"\n{symbol.upper()}:")
        for tf, count in timeframes.items():
            if count > 0:
                print(f"  {tf}: {count} candles")

print("\n" + "=" * 60)
print("TEST COMPLETE!")