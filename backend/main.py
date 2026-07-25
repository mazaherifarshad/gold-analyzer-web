# -*- coding: utf-8 -*-
"""
FastAPI Server - Gold Market Analyzer API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import uvicorn
import sqlite3
import os

from backend.database.connection import session_scope
from backend.database.models import MarketCandle, MarketHistory, AnalysisResult
from backend.services.tgju import TGJUClient, fetch_and_store_all
from backend.candle.candle_engine import build_candles_for_all_symbols

# ============ مدل‌های پاسخ API ============

class PriceResponse(BaseModel):
    symbol: str
    price: float
    timestamp: str

class AnalysisResponse(BaseModel):
    symbol: str
    current_price: float
    trend: str
    trend_score: int
    rsi: float
    momentum: str
    volatility: float
    final_score: float
    recommendation: str
    confidence: int
    reasons: List[str]
    timestamp: str

class CandleResponse(BaseModel):
    symbol: str
    timeframe: str
    candle_time: str
    open: float
    high: float
    low: float
    close: float
    volume: float

# ============ ایجاد App ============

app = FastAPI(
    title="Gold Market Analyzer API",
    description="Professional AI-based Gold Market Analysis for Iranian Market",
    version="1.0.0"
)

# ============ CORS تنظیمات ============

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # در تولید، دامنه‌های خاص را مشخص کنید
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ تابع تحلیل ============

def analyze_symbol(symbol: str, timeframe: str = '1m') -> dict:
    """تحلیل یک نماد"""
    from backend.database.connection import session_scope
    from backend.database.models import MarketCandle
    import pandas as pd
    
    with session_scope() as session:
        candles = session.query(MarketCandle).filter(
            MarketCandle.symbol == symbol,
            MarketCandle.timeframe == timeframe
        ).order_by(MarketCandle.candle_time).all()
        
        if len(candles) < 10:
            return {'error': f'Not enough candles for {symbol}'}
        
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
    
    # محاسبه اندیکاتورها
    df['sma_5'] = df['close'].rolling(window=5).mean()
    df['sma_10'] = df['close'].rolling(window=10).mean()
    df['sma_20'] = df['close'].rolling(window=20).mean()
    
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    returns = df['close'].pct_change()
    df['volatility'] = returns.rolling(window=10).std() * 100
    
    current = df.iloc[-1]
    
    # تحلیل روند
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
    
    # مومنتوم
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
    
    # نوسان
    vol = current['volatility']
    if pd.isna(vol) or vol == 0:
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
    
    # امتیاز نهایی
    final_score = trend_score * 0.40 + momentum_score * 0.30 + vol_score * 0.30
    
    # توصیه
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
    
    reasons = []
    if trend_score > 60:
        reasons.append(f"Uptrend detected (score: {trend_score})")
    elif trend_score < 40:
        reasons.append(f"Downtrend detected (score: {trend_score})")
    if rsi > 70:
        reasons.append(f"Overbought conditions (RSI: {rsi:.1f})")
    elif rsi < 30:
        reasons.append(f"Oversold conditions (RSI: {rsi:.1f})")
    
    return {
        'symbol': symbol,
        'current_price': current['close'],
        'trend': trend,
        'trend_score': trend_score,
        'rsi': rsi,
        'momentum': momentum,
        'volatility': vol,
        'volatility_status': vol_status,
        'final_score': final_score,
        'recommendation': recommendation,
        'confidence': confidence,
        'reasons': reasons,
        'candle_count': len(candles),
        'timestamp': datetime.now().isoformat()
    }

# ============ API Endpoints ============

@app.get("/")
async def root():
    return {
        "name": "Gold Market Analyzer API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "/prices",
            "/analysis",
            "/analysis/{symbol}",
            "/candles/{symbol}",
            "/update",
            "/fix-db",
            "/health"
        ]
    }

@app.get("/prices", response_model=List[PriceResponse])
async def get_prices():
    """دریافت قیمت‌های لحظه‌ای"""
    client = TGJUClient()
    prices = client.get_current_prices()
    
    if not prices:
        raise HTTPException(status_code=503, detail="Unable to fetch prices")
    
    return [
        PriceResponse(
            symbol=symbol,
            price=price,
            timestamp=datetime.now().isoformat()
        )
        for symbol, price in prices.items()
    ]

@app.get("/analysis", response_model=List[AnalysisResponse])
async def get_all_analysis():
    """دریافت تحلیل تمام نمادها"""
    symbols = ['gold', 'usd', 'ounce', 'coin']
    results = []
    
    for symbol in symbols:
        result = analyze_symbol(symbol)
        if 'error' not in result:
            results.append(AnalysisResponse(**result))
    
    return results

@app.get("/analysis/{symbol}", response_model=AnalysisResponse)
async def get_symbol_analysis(symbol: str):
    """دریافت تحلیل یک نماد خاص"""
    result = analyze_symbol(symbol)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    return AnalysisResponse(**result)

@app.get("/candles/{symbol}")
async def get_candles(symbol: str, timeframe: str = '1m', limit: int = 50):
    """دریافت شمع‌های یک نماد"""
    with session_scope() as session:
        candles = session.query(MarketCandle).filter(
            MarketCandle.symbol == symbol,
            MarketCandle.timeframe == timeframe
        ).order_by(MarketCandle.candle_time.desc()).limit(limit).all()
        
        return [
            {
                'time': c.candle_time.isoformat(),
                'open': c.open,
                'high': c.high,
                'low': c.low,
                'close': c.close,
                'volume': c.volume
            }
            for c in reversed(candles)
        ]

@app.post("/update")
async def update_data():
    """به‌روزرسانی داده‌ها از TGJU"""
    try:
        # دریافت داده‌های جدید
        fetch_and_store_all()
        
        # ساخت شمع‌ها
        build_candles_for_all_symbols()
        
        return {
            "status": "success",
            "message": "Data updated successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/fix-db")
async def fix_database():
    """تعمیر دیتابیس - اضافه کردن ستون‌های گم‌شده"""
    try:
        # مسیر دیتابیس
        db_path = os.path.join(os.path.dirname(__file__), "database", "market.db")
        
        # اتصال به دیتابیس
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # بررسی وجود ستون‌ها در market_history
        cursor.execute("PRAGMA table_info(market_history)")
        columns = [col[1] for col in cursor.fetchall()]
        
        # اضافه کردن ستون‌های گم‌شده
        added = []
        if 'raw_data' not in columns:
            cursor.execute("ALTER TABLE market_history ADD COLUMN raw_data TEXT")
            added.append('raw_data')
        
        if 'source' not in columns:
            cursor.execute("ALTER TABLE market_history ADD COLUMN source TEXT DEFAULT 'tgju'")
            added.append('source')
        
        # بررسی وجود ستون‌ها در market_candles
        cursor.execute("PRAGMA table_info(market_candles)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tick_count' not in columns:
            cursor.execute("ALTER TABLE market_candles ADD COLUMN tick_count INTEGER DEFAULT 0")
            added.append('tick_count (market_candles)')
        
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE market_candles ADD COLUMN updated_at DATETIME")
            added.append('updated_at (market_candles)')
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success", 
            "message": "Database repaired successfully",
            "columns_added": added
        }
        
    except Exception as e:
        return {
            "status": "error", 
            "message": str(e)
        }

@app.get("/health")
async def health_check():
    """بررسی سلامت سیستم"""
    try:
        with session_scope() as session:
            count = session.query(MarketHistory).count()
        return {
            "status": "healthy",
            "database": "connected",
            "records": count,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============ اجرا ============

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)