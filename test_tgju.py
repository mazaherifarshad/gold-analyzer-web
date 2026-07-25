# -*- coding: utf-8 -*-
"""
تست اتصال به TGJU
"""

from backend.services.tgju import TGJUClient, fetch_and_store_all
from backend.database.connection import session_scope
from backend.database.models import MarketHistory, MarketCandle
from backend.candle.candle_engine import build_candles_for_all_symbols

print("=" * 50)
print("TESTING TGJU CONNECTION")
print("=" * 50)

# تست کلاینت
client = TGJUClient()

print("\n📊 Getting current prices...")
prices = client.get_current_prices()

if prices:
    print("\n✅ Current prices received:")
    for symbol, price in prices.items():
        print(f"  {symbol}: {price:,.2f}")
else:
    print("❌ No prices received. Check internet connection.")
    exit()

# ذخیره در دیتابیس
print("\n💾 Storing data in database...")
results = fetch_and_store_all()

print(f"\n📊 Data stored:")
for symbol, count in results.items():
    print(f"  {symbol}: {count} ticks")

# چک کردن تعداد تیک‌ها
print("\n📊 Total ticks in database:")
with session_scope() as session:
    for symbol in ['gold', 'usd', 'ounce', 'coin']:
        count = session.query(MarketHistory).filter(
            MarketHistory.symbol == symbol
        ).count()
        print(f"  {symbol}: {count}")

# ساخت شمع از داده‌های جدید
print("\n🔄 Building candles from new data...")
candle_results = build_candles_for_all_symbols()

print("\n📊 Candles built:")
for symbol, timeframes in candle_results.items():
    print(f"\n  {symbol}:")
    for tf, count in timeframes.items():
        if count > 0:
            print(f"    {tf}: {count}")

print("\n" + "=" * 50)
print("TEST COMPLETE!")