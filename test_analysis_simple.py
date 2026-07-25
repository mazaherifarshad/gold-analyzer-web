# -*- coding: utf-8 -*-
"""
تست ساده تحلیل - بدون وابستگی به engine.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database.connection import session_scope
from backend.database.models import MarketCandle
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

print("=" * 60)
print("SIMPLE ANALYSIS TEST")
print("=" * 60)

# 1. دریافت یا ایجاد شمع‌ها
print("\n📊 Preparing candles...")

# **نکته مهم: همه عملیات روی دیتابیس باید داخل یک session انجام شود**
with session_scope() as session:
    # بررسی تعداد شمع‌های موجود
    candle_count = session.query(MarketCandle).filter(
        MarketCandle.symbol == 'gold',
        MarketCandle.timeframe == '5m'
    ).count()
    
    if candle_count < 20:
        print(f"⚠️ Only {candle_count} candles found. Creating test data...")
        
        # حذف شمع‌های قبلی
        session.query(MarketCandle).filter(
            MarketCandle.symbol == 'gold',
            MarketCandle.timeframe == '5m'
        ).delete()
        
        # ایجاد شمع‌های تست با روند صعودی
        base_price = 188250000
        now = datetime.now()
        
        for i in range(30):
            candle_time = now - timedelta(minutes=(i+1)*5)
            # روند صعودی با نوسان
            trend = i * 8000
            noise = np.random.randint(-3000, 3000)
            price = base_price + trend + noise
            
            candle = MarketCandle(
                symbol='gold',
                timeframe='5m',
                candle_time=candle_time,
                open=price - 1000,
                high=price + 2000,
                low=price - 2000,
                close=price + 500,
                volume=100 + i * 5
            )
            session.add(candle)
        
        session.commit()
        print(f"✅ Created 30 test candles")
    
    # **دریافت داده‌ها و تبدیل به فرمت ساده در همان session**
    candles = session.query(MarketCandle).filter(
        MarketCandle.symbol == 'gold',
        MarketCandle.timeframe == '5m'
    ).order_by(MarketCandle.candle_time).all()
    
    print(f"✅ Found {len(candles)} candles")
    
    # **تبدیل به دیکشنری در داخل session (قبل از بسته شدن)**
    data = []
    for c in candles:
        data.append({
            'time': c.candle_time,  # حالا دسترسی به attributes در داخل session مجاز است
            'open': c.open,
            'high': c.high,
            'low': c.low,
            'close': c.close,
            'volume': c.volume
        })
    
    # بعد از اینجا session بسته می‌شود، اما ما داده‌ها را در لیست data داریم

# 2. تبدیل به DataFrame (خارج از session)
print("\n🔄 Converting to DataFrame...")

df = pd.DataFrame(data)
df.set_index('time', inplace=True)
df = df.sort_index()

print(f"✅ DataFrame shape: {df.shape}")

# 3. تحلیل ساده با pandas
print("\n📈 Simple Analysis:")

# محاسبه میانگین متحرک
df['sma_5'] = df['close'].rolling(window=5).mean()
df['sma_10'] = df['close'].rolling(window=10).mean()
df['sma_20'] = df['close'].rolling(window=20).mean()

current_price = df['close'].iloc[-1]
sma_5 = df['sma_5'].iloc[-1]
sma_10 = df['sma_10'].iloc[-1]
sma_20 = df['sma_20'].iloc[-1]

print(f"\n  Current Price: {current_price:,.2f}")
print(f"  SMA 5: {sma_5:,.2f}")
print(f"  SMA 10: {sma_10:,.2f}")
print(f"  SMA 20: {sma_20:,.2f}")

# تشخیص روند
if current_price > sma_5 > sma_10 > sma_20:
    trend = "STRONG UPTREND"
    trend_score = 80
elif current_price > sma_5 and current_price > sma_10:
    trend = "UPTREND"
    trend_score = 65
elif current_price < sma_5 < sma_10 < sma_20:
    trend = "STRONG DOWNTREND"
    trend_score = 20
elif current_price < sma_5 and current_price < sma_10:
    trend = "DOWNTREND"
    trend_score = 35
else:
    trend = "CONSOLIDATION"
    trend_score = 50

print(f"\n  Trend: {trend}")
print(f"  Trend Score: {trend_score}/100")

# 4. محاسبه RSI ساده
print("\n📊 Momentum Analysis:")

delta = df['close'].diff()
gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
rs = gain / loss
rsi = 100 - (100 / (1 + rs))
current_rsi = rsi.iloc[-1]

print(f"  RSI (14): {current_rsi:.2f}")

if current_rsi > 70:
    momentum = "OVERBOUGHT"
    momentum_score = 30
elif current_rsi < 30:
    momentum = "OVERSOLD"
    momentum_score = 70
elif current_rsi > 50:
    momentum = "BULLISH"
    momentum_score = 60
else:
    momentum = "BEARISH"
    momentum_score = 40

print(f"  Momentum: {momentum}")
print(f"  Momentum Score: {momentum_score}/100")

# 5. محاسبه نوسان
print("\n📊 Volatility Analysis:")

returns = df['close'].pct_change()
volatility = returns.rolling(window=10).std() * 100
current_vol = volatility.iloc[-1]
avg_vol = volatility.mean()

print(f"  Current Volatility: {current_vol:.2f}%")
print(f"  Average Volatility: {avg_vol:.2f}%")

if current_vol > avg_vol * 1.5:
    vol_status = "HIGH"
    vol_score = 30
elif current_vol < avg_vol * 0.5:
    vol_status = "LOW"
    vol_score = 70
else:
    vol_status = "NORMAL"
    vol_score = 50

print(f"  Volatility Status: {vol_status}")
print(f"  Volatility Score: {vol_score}/100")

# 6. امتیاز نهایی
print("\n🤖 Final Score:")

# وزن‌دهی
final_score = (
    trend_score * 0.40 +
    momentum_score * 0.30 +
    vol_score * 0.30
)

print(f"  Final Score: {final_score:.2f}/100")

# توصیه
if final_score >= 75:
    recommendation = "STRONG BUY"
    confidence = 80
elif final_score >= 60:
    recommendation = "BUY"
    confidence = 65
elif final_score >= 45:
    recommendation = "HOLD"
    confidence = 50
elif final_score >= 30:
    recommendation = "SELL"
    confidence = 65
else:
    recommendation = "STRONG SELL"
    confidence = 80

print(f"  Recommendation: {recommendation}")
print(f"  Confidence: {confidence}%")

# دلایل
print(f"\n  Reasons:")
if trend_score > 60:
    print(f"    - {trend} detected")
if current_rsi > 70:
    print(f"    - Overbought conditions (RSI: {current_rsi:.1f})")
elif current_rsi < 30:
    print(f"    - Oversold conditions (RSI: {current_rsi:.1f})")
if current_vol > avg_vol * 1.5:
    print(f"    - High volatility - caution advised")
elif current_vol < avg_vol * 0.5:
    print(f"    - Low volatility - stable market")

print("\n" + "=" * 60)
print("ANALYSIS TEST COMPLETE!")