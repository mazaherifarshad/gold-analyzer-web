# -*- coding: utf-8 -*-
"""
دریافت داده‌های تاریخی با درخواست‌های متوالی
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database.connection import session_scope
from backend.database.models import MarketHistory
from backend.services.tgju import TGJUClient
from datetime import datetime, timedelta
import time
import random
import requests
import json

def fetch_multiple_ticks(symbol: str, count: int = 20) -> int:
    """
    دریافت چندین تیک با فاصله زمانی
    """
    client = TGJUClient()
    stored_count = 0
    
    print(f"  📥 Fetching {count} ticks for {symbol}...")
    
    for i in range(count):
        try:
            # دریافت قیمت فعلی
            prices = client.get_current_prices()
            
            if symbol in prices and prices[symbol]:
                price = prices[symbol]
                
                # زمان: هر تیک با ۱ دقیقه فاصله از زمان فعلی
                tick_time = datetime.now() - timedelta(minutes=(count - i))
                
                with session_scope() as session:
                    # بررسی وجود تیک تکراری
                    existing = session.query(MarketHistory).filter(
                        MarketHistory.symbol == symbol,
                        MarketHistory.created_at >= tick_time - timedelta(seconds=30),
                        MarketHistory.created_at <= tick_time + timedelta(seconds=30)
                    ).first()
                    
                    if not existing:
                        tick = MarketHistory(
                            symbol=symbol,
                            price=price,
                            created_at=tick_time,
                            source='tgju_multiple'
                        )
                        session.add(tick)
                        session.commit()
                        stored_count += 1
                        print(f"    ✅ Tick {i+1}: {price:,.2f} at {tick_time.strftime('%H:%M:%S')}")
                    else:
                        print(f"    ⏭️ Tick {i+1}: Duplicate, skipped")
                
                # فاصله بین درخواست‌ها
                time.sleep(1)
                
            else:
                print(f"    ❌ No price for {symbol}")
                time.sleep(0.5)
                
        except Exception as e:
            print(f"    ❌ Error: {e}")
            time.sleep(1)
    
    return stored_count


def fetch_multiple_for_all(count: int = 20):
    """
    دریافت چندین تیک برای تمام نمادها
    """
    print("=" * 60)
    print("FETCHING MULTIPLE TICKS")
    print("=" * 60)
    print(f"\n⏱️ This will take about {count * 4} seconds...")
    
    symbols = ['gold', 'usd', 'ounce', 'coin']
    total_ticks = 0
    
    for symbol in symbols:
        print(f"\n📊 Processing {symbol}...")
        # حذف تیک‌های قبلی این نماد
        with session_scope() as session:
            session.query(MarketHistory).filter(
                MarketHistory.symbol == symbol,
                MarketHistory.source == 'tgju_multiple'
            ).delete()
            session.commit()
        
        count_stored = fetch_multiple_ticks(symbol, count)
        total_ticks += count_stored
        print(f"  ✅ {symbol}: {count_stored} ticks stored")
        time.sleep(2)  # فاصله بین نمادها
    
    print("\n" + "=" * 60)
    print(f"✅ TOTAL: {total_ticks} ticks stored")
    print("=" * 60)
    
    return total_ticks


def check_ticks_count():
    """بررسی تعداد تیک‌های هر نماد"""
    with session_scope() as session:
        print("\n📊 Current ticks in database:")
        for symbol in ['gold', 'usd', 'ounce', 'coin']:
            count = session.query(MarketHistory).filter(
                MarketHistory.symbol == symbol
            ).count()
            print(f"  {symbol}: {count}")


if __name__ == "__main__":
    # دریافت تیک‌های متوالی
    total = fetch_multiple_for_all(count=15)  # ۱۵ تیک برای هر نماد
    
    if total > 0:
        # بررسی تعداد تیک‌ها
        check_ticks_count()
        
        # ساخت شمع
        print("\n🔄 Building candles from new data...")
        from backend.candle.candle_engine import build_candles_for_all_symbols
        results = build_candles_for_all_symbols()
        
        print("\n📊 Candle results:")
        for symbol, timeframes in results.items():
            print(f"\n  {symbol}:")
            total_candles = 0
            for tf, count in timeframes.items():
                if count > 0:
                    print(f"    {tf}: {count}")
                    total_candles += count
            if total_candles == 0:
                print(f"    ❌ No candles built")
        
        # اجرای تحلیل
        print("\n" + "=" * 60)
        print("RUNNING ANALYSIS...")
        print("=" * 60)
        os.system("python run_full_analysis.py")
    else:
        print("\n⚠️ No ticks received. Please check your connection.")