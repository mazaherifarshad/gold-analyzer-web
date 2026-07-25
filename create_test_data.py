# -*- coding: utf-8 -*-
"""
ایجاد داده‌های تست برای همه نمادها
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database.connection import session_scope
from backend.database.models import MarketHistory, MarketCandle
from datetime import datetime, timedelta
import random

def create_test_ticks(symbol: str, count: int = 50):
    """ایجاد تیک‌های تست برای یک نماد"""
    
    base_prices = {
        'gold': 188000000,
        'usd': 1920000,
        'ounce': 4000,
        'coin': 1880000000
    }
    
    base_price = base_prices.get(symbol, 1000000)
    
    with session_scope() as session:
        # حذف تیک‌های قبلی این نماد
        session.query(MarketHistory).filter(
            MarketHistory.symbol == symbol,
            MarketHistory.source == 'test_data'
        ).delete()
        
        now = datetime.now()
        ticks_created = 0
        
        for i in range(count):
            # قیمت با نوسان تصادفی
            change = random.randint(-10000, 10000)
            price = base_price + change + (i * 1000)  # روند صعودی ملایم
            
            # زمان: هر تیک با ۱ دقیقه فاصله
            tick_time = now - timedelta(minutes=(count - i))
            
            tick = MarketHistory(
                symbol=symbol,
                price=price,
                created_at=tick_time,
                source='test_data'
            )
            session.add(tick)
            ticks_created += 1
        
        session.commit()
        print(f"  ✅ {symbol}: Created {ticks_created} test ticks")
        return ticks_created


def create_all_test_data():
    """ایجاد داده‌های تست برای تمام نمادها"""
    print("=" * 60)
    print("CREATING TEST DATA")
    print("=" * 60)
    
    symbols = ['gold', 'usd', 'ounce', 'coin']
    total = 0
    
    for symbol in symbols:
        print(f"\n📊 Creating data for {symbol}...")
        count = create_test_ticks(symbol, 30)
        total += count
    
    print("\n" + "=" * 60)
    print(f"✅ TOTAL: {total} test ticks created")
    print("=" * 60)
    
    return total


def build_candles_from_test():
    """ساخت شمع از داده‌های تست"""
    from backend.candle.candle_engine import build_candles_for_all_symbols
    
    print("\n🔄 Building candles from test data...")
    results = build_candles_for_all_symbols()
    
    print("\n📊 Candle results:")
    for symbol, timeframes in results.items():
        print(f"\n  {symbol}:")
        total = 0
        for tf, count in timeframes.items():
            if count > 0:
                print(f"    {tf}: {count}")
                total += count
        if total == 0:
            print(f"    ❌ No candles built")
    
    return results


if __name__ == "__main__":
    # ایجاد داده‌های تست
    create_all_test_data()
    
    # ساخت شمع
    build_candles_from_test()
    
    # اجرای تحلیل
    print("\n" + "=" * 60)
    print("RUNNING ANALYSIS...")
    print("=" * 60)
    os.system("python run_full_analysis.py")