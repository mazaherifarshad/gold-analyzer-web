# -*- coding: utf-8 -*-
"""
تست کامل تحلیل با ماژول‌های موجود
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database.connection import session_scope
from backend.database.models import MarketCandle
from backend.analysis import engine as analysis_engine
from backend.analysis.ai_score import AIScore
from backend.analysis.trend import analyze_trend
from backend.analysis.momentum import analyze_momentum
from backend.analysis.volatility import analyze_volatility
from backend.candle.candle_engine import CandleEngine
import pandas as pd
from datetime import datetime, timedelta

print("=" * 60)
print("FULL ANALYSIS TEST")
print("=" * 60)

# 1. دریافت شمع‌ها از دیتابیس
print("\n📊 Loading candles from database...")

with session_scope() as session:
    candles = session.query(MarketCandle).filter(
        MarketCandle.symbol == 'gold',
        MarketCandle.timeframe == '5m'
    ).order_by(MarketCandle.candle_time).all()
    
    if len(candles) < 10:
        print(f"⚠️ Only {len(candles)} candles found. Need at least 10 for analysis.")
        print("   Adding some test candles...")
        
        # اگر شمع کافی نیست، چند شمع تست اضافه می‌کنیم
        base_price = 188250000
        now = datetime.now()
        
        # حذف شمع‌های قبلی
        session.query(MarketCandle).filter(
            MarketCandle.symbol == 'gold',
            MarketCandle.timeframe == '5m'
        ).delete()
        
        # ایجاد شمع‌های تست با روند صعودی
        for i in range(20):
            candle_time = now - timedelta(minutes=(i+1)*5)
            price_change = i * 5000  # روند صعودی
            candle = MarketCandle(
                symbol='gold',
                timeframe='5m',
                candle_time=candle_time,
                open=base_price + price_change,
                high=base_price + price_change + 2000,
                low=base_price + price_change - 1000,
                close=base_price + price_change + 1500,
                volume=100 + i * 10
            )
            session.add(candle)
        
        session.commit()
        print(f"✅ Added 20 test candles with uptrend")
        
        # دوباره دریافت
        candles = session.query(MarketCandle).filter(
            MarketCandle.symbol == 'gold',
            MarketCandle.timeframe == '5m'
        ).order_by(MarketCandle.candle_time).all()

print(f"✅ Found {len(candles)} candles")

# 2. تبدیل به DataFrame
print("\n🔄 Converting to DataFrame...")

data = []
for c in candles:
    data.append({
        'time': c.candle_time,
        'open': c.open,
        'high': c.high,
        'low': c.low,
        'close': c.close,
        'volume': c.volume
    })

df = pd.DataFrame(data)
df.set_index('time', inplace=True)
df = df.sort_index()

print(f"✅ DataFrame shape: {df.shape}")
print(f"   Close prices (last 5): {df['close'].tail().tolist()}")

# 3. اجرای تحلیل‌ها
print("\n📈 Running analysis modules...")

# Trend Analysis
try:
    trend_result = analyze_trend(df)
    print(f"  ✅ Trend: {trend_result}")
except Exception as e:
    print(f"  ❌ Trend error: {e}")
    trend_result = {}

# Momentum Analysis
try:
    momentum_result = analyze_momentum(df)
    print(f"  ✅ Momentum: {momentum_result}")
except Exception as e:
    print(f"  ❌ Momentum error: {e}")
    momentum_result = {}

# Volatility Analysis
try:
    volatility_result = analyze_volatility(df)
    print(f"  ✅ Volatility: {volatility_result}")
except Exception as e:
    print(f"  ❌ Volatility error: {e}")
    volatility_result = {}

# 4. AI Score
print("\n🤖 Calculating AI Score...")

try:
    # استفاده از ماژول AI Score موجود
    ai_score = AIScore()
    
    # تبدیل df به فرمت مناسب برای AI Score
    score_result = ai_score.calculate(df)
    
    if score_result:
        print(f"\n📊 AI Score Results:")
        print(f"  Score: {score_result.get('score', 0):.2f}")
        print(f"  Confidence: {score_result.get('confidence', 0):.2f}%")
        print(f"  Recommendation: {score_result.get('recommendation', 'HOLD')}")
        
        if 'reasons' in score_result:
            print(f"\n  Reasons:")
            for reason in score_result['reasons'][:5]:
                print(f"    - {reason}")
    else:
        print("  ❌ AI Score calculation returned empty result")
        
except Exception as e:
    print(f"  ❌ AI Score error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("ANALYSIS TEST COMPLETE!")