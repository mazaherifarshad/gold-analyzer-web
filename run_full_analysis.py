# -*- coding: utf-8 -*-
"""
اجرای کامل تحلیل برای همه نمادها
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database.connection import session_scope
from backend.database.models import MarketCandle
from backend.services.tgju import TGJUClient, fetch_and_store_all
from backend.candle.candle_engine import build_candles_for_all_symbols
import pandas as pd
import numpy as np
from datetime import datetime

def analyze_symbol(symbol: str, timeframe: str = '1m') -> dict:
    """
    تحلیل یک نماد خاص
    
    Args:
        symbol: نام نماد (gold, usd, ounce, coin)
        timeframe: تایم‌فریم (1m, 5m, 15m, 30m, 1h, 4h, 1d)
    
    Returns:
        dict: نتایج تحلیل
    """
    
    with session_scope() as session:
        candles = session.query(MarketCandle).filter(
            MarketCandle.symbol == symbol,
            MarketCandle.timeframe == timeframe
        ).order_by(MarketCandle.candle_time).all()
        
        if len(candles) < 10:
            return {'error': f'Not enough candles for {symbol} (need 10, have {len(candles)})'}
        
        # تبدیل به DataFrame
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
    
    # ============ محاسبه اندیکاتورها ============
    
    # 1. میانگین متحرک ساده (SMA)
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    
    # 2. شاخص قدرت نسبی (RSI)
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 3. نوسان (Volatility)
    returns = df['close'].pct_change()
    df['volatility'] = returns.rolling(window=10).std() * 100
    
    # ============ تحلیل روند ============
    current = df.iloc[-1]
    
    if current['close'] > current['sma_5'] > current['sma_10'] > current['sma_20']:
        trend = 'STRONG UPTREND'
        trend_score = 80
    elif current['close'] > current['sma_5'] and current['close'] > current['sma_10']:
        trend = 'UPTREND'
        trend_score = 65
    elif current['close'] < current['sma_5'] < current['sma_10'] < current['sma_20']:
        trend = 'STRONG DOWNTREND'
        trend_score = 20
    elif current['close'] < current['sma_5'] and current['close'] < current['sma_10']:
        trend = 'DOWNTREND'
        trend_score = 35
    else:
        trend = 'CONSOLIDATION'
        trend_score = 50
    
    # ============ تحلیل مومنتوم ============
    rsi = current['rsi']
    if pd.isna(rsi):
        rsi = 50
        momentum = 'NEUTRAL'
        momentum_score = 50
    elif rsi > 70:
        momentum = 'OVERBOUGHT'
        momentum_score = 30
    elif rsi < 30:
        momentum = 'OVERSOLD'
        momentum_score = 70
    elif rsi > 50:
        momentum = 'BULLISH'
        momentum_score = 60
    else:
        momentum = 'BEARISH'
        momentum_score = 40
    
    # ============ تحلیل نوسان ============
    vol = current['volatility']
    if pd.isna(vol):
        vol = 0
        vol_status = 'NORMAL'
        vol_score = 50
    else:
        avg_vol = df['volatility'].mean()
        if pd.isna(avg_vol) or avg_vol == 0:
            vol_status = 'NORMAL'
            vol_score = 50
        elif vol > avg_vol * 1.5:
            vol_status = 'HIGH'
            vol_score = 30
        elif vol < avg_vol * 0.5:
            vol_status = 'LOW'
            vol_score = 70
        else:
            vol_status = 'NORMAL'
            vol_score = 50
    
    # ============ امتیاز نهایی ============
    final_score = (
        trend_score * 0.40 +
        momentum_score * 0.30 +
        vol_score * 0.30
    )
    
    # ============ توصیه نهایی ============
    if final_score >= 75:
        recommendation = 'STRONG BUY'
        confidence = 80
    elif final_score >= 60:
        recommendation = 'BUY'
        confidence = 65
    elif final_score >= 45:
        recommendation = 'HOLD'
        confidence = 50
    elif final_score >= 30:
        recommendation = 'SELL'
        confidence = 65
    else:
        recommendation = 'STRONG SELL'
        confidence = 80
    
    # ============ دلایل تحلیل ============
    reasons = []
    if trend_score > 60:
        reasons.append(f"Uptrend detected (score: {trend_score})")
    elif trend_score < 40:
        reasons.append(f"Downtrend detected (score: {trend_score})")
    
    if rsi > 70:
        reasons.append(f"Overbought conditions (RSI: {rsi:.1f})")
    elif rsi < 30:
        reasons.append(f"Oversold conditions (RSI: {rsi:.1f})")
    
    if vol_status == 'HIGH':
        reasons.append(f"High volatility - caution advised ({vol:.2f}%)")
    elif vol_status == 'LOW':
        reasons.append(f"Low volatility - stable market ({vol:.2f}%)")
    
    # ============ بازگشت نتیجه ============
    return {
        'symbol': symbol,
        'timeframe': timeframe,
        'current_price': current['close'],
        'trend': trend,
        'trend_score': trend_score,
        'rsi': rsi,
        'momentum': momentum,
        'momentum_score': momentum_score,
        'volatility': vol,
        'volatility_status': vol_status,
        'volatility_score': vol_score,
        'final_score': final_score,
        'recommendation': recommendation,
        'confidence': confidence,
        'reasons': reasons,
        'timestamp': datetime.now().isoformat(),
        'candle_count': len(candles)
    }


def print_analysis_result(result: dict):
    """چاپ زیبای نتایج تحلیل"""
    if 'error' in result:
        print(f"  ❌ {result['error']}")
        return
    
    print(f"\n  📊 {result['symbol'].upper()}:")
    print(f"    Price: {result['current_price']:,.2f}")
    print(f"    Candles: {result['candle_count']}")
    print(f"    Trend: {result['trend']} ({result['trend_score']}/100)")
    print(f"    RSI: {result['rsi']:.1f} - {result['momentum']}")
    print(f"    Volatility: {result['volatility']:.2f}% - {result['volatility_status']}")
    print(f"    Final Score: {result['final_score']:.1f}/100")
    print(f"    Recommendation: {result['recommendation']} (Confidence: {result['confidence']}%)")
    
    if result.get('reasons'):
        print(f"    Reasons:")
        for reason in result['reasons']:
            print(f"      - {reason}")


def main():
    """اجرای اصلی برنامه"""
    print("=" * 70)
    print("FULL MARKET ANALYSIS")
    print("=" * 70)
    
    # ============ 1. دریافت داده‌های جدید ============
    print("\n📊 Fetching latest data from TGJU...")
    client = TGJUClient()
    prices = client.get_current_prices()
    
    if prices:
        print("  ✅ Data received:")
        for symbol, price in prices.items():
            print(f"    {symbol}: {price:,.2f}")
        
        # ذخیره در دیتابیس
        print("\n💾 Storing in database...")
        fetch_and_store_all()
    else:
        print("  ⚠️ No new data from TGJU, using existing data...")
    
    # ============ 2. ساخت شمع‌های جدید ============
    print("\n🔄 Building candles...")
    build_candles_for_all_symbols()
    
    # ============ 3. تحلیل همه نمادها ============
    print("\n📈 Analyzing all symbols...")
    symbols = ['gold', 'usd', 'ounce', 'coin']
    results = {}
    
    for symbol in symbols:
        print(f"\n  Analyzing {symbol}...")
        result = analyze_symbol(symbol, '1m')  # استفاده از تایم‌فریم ۱ دقیقه
        
        if 'error' in result:
            print(f"    ❌ {result['error']}")
            # امتحان با تایم‌فریم ۵ دقیقه
            print(f"    🔄 Trying 5m timeframe...")
            result = analyze_symbol(symbol, '5m')
        
        if 'error' not in result:
            results[symbol] = result
            print(f"    ✅ {result['recommendation']} (Score: {result['final_score']:.1f})")
        else:
            print(f"    ❌ {result['error']}")
    
    # ============ 4. نمایش نتایج نهایی ============
    print("\n" + "=" * 70)
    print("FINAL RESULTS:")
    print("=" * 70)
    
    if results:
        for symbol, result in results.items():
            print_analysis_result(result)
    else:
        print("\n⚠️ No analysis results available.")
        print("   Please run 'python create_test_data.py' first to generate test data.")
    
    # ============ 5. خلاصه کلی ============
    print("\n" + "=" * 70)
    print("SUMMARY:")
    print("=" * 70)
    
    buy_count = sum(1 for r in results.values() if r.get('recommendation') in ['BUY', 'STRONG BUY'])
    sell_count = sum(1 for r in results.values() if r.get('recommendation') in ['SELL', 'STRONG SELL'])
    hold_count = sum(1 for r in results.values() if r.get('recommendation') == 'HOLD')
    
    print(f"  🟢 BUY: {buy_count}")
    print(f"  🟡 HOLD: {hold_count}")
    print(f"  🔴 SELL: {sell_count}")
    print(f"  📊 Total: {len(results)} symbols analyzed")
    
    print("\n" + "=" * 70)
    print("ANALYSIS COMPLETE!")
    print("=" * 70)


if __name__ == "__main__":
    main()