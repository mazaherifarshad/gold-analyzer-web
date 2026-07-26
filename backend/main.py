# -*- coding: utf-8 -*-
"""
FastAPI Server - Gold Market Analyzer API
نسخه نهایی با مدیریت دیتابیس و اندپوینت تعمیر
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import uvicorn
import sqlite3
import os
import random
import requests
from pathlib import Path
from contextlib import contextmanager

# ============ تنظیمات دیتابیس ============
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index, UniqueConstraint, Text, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

Base = declarative_base()

# ============ مدل‌های دیتابیس ============
class MarketHistory(Base):
    __tablename__ = 'market_history'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(50), default='tgju')
    raw_data = Column(Text, nullable=True)
    __table_args__ = (Index('idx_history_symbol_time', 'symbol', 'created_at'),)

class MarketCandle(Base):
    __tablename__ = 'market_candles'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False, index=True)
    candle_time = Column(DateTime, nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tick_count = Column(Integer, default=0)
    __table_args__ = (
        UniqueConstraint('symbol', 'timeframe', 'candle_time', name='uq_candle'),
        Index('idx_candle_symbol_timeframe_time', 'symbol', 'timeframe', 'candle_time'),
    )

class AnalysisResult(Base):
    __tablename__ = 'analysis_results'
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    analysis_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    score = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    recommendation = Column(String(20), nullable=False)
    details = Column(Text, nullable=True)
    trend_score = Column(Float, default=0)
    momentum_score = Column(Float, default=0)
    divergence_score = Column(Float, default=0)
    bubble_score = Column(Float, default=0)
    iran_market_score = Column(Float, default=0)
    smart_money_score = Column(Float, default=0)
    support_resistance_score = Column(Float, default=0)
    multi_timeframe_score = Column(Float, default=0)
    volatility_score = Column(Float, default=0)
    risk_score = Column(Float, default=0)
    volume_score = Column(Float, default=0)
    __table_args__ = (Index('idx_analysis_symbol_time', 'symbol', 'analysis_time'),)

# ============ اتصال به دیتابیس ============
DB_PATH = Path(__file__).parent / 'database' / 'market.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(
    DATABASE_URL,
    connect_args={'check_same_thread': False},
    poolclass=StaticPool,
    echo=False
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ایجاد جداول در اولین اجرا
Base.metadata.create_all(engine)

@contextmanager
def session_scope():
    """مدیریت خودکار Session"""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

# ============ FastAPI App ============
app = FastAPI(
    title="Gold Market Analyzer API",
    description="Professional AI-based Gold Market Analysis for Iranian Market",
    version="1.0.0"
)

# ============ CORS ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # برای تست، همه دامنه‌ها
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

# ============ تابع تحلیل ============
def analyze_symbol(symbol: str, timeframe: str = '1m') -> dict:
    """تحلیل یک نماد با استفاده از شمع‌ها"""
    import pandas as pd
    import numpy as np
    
    with session_scope() as session:
        candles = session.query(MarketCandle).filter(
            MarketCandle.symbol == symbol,
            MarketCandle.timeframe == timeframe
        ).order_by(MarketCandle.candle_time).all()
        
        if len(candles) < 10:
            return {'error': f'Not enough candles for {symbol} (need 10, have {len(candles)})'}
        
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
    if vol_status == 'HIGH':
        reasons.append(f"High volatility - caution advised ({vol:.2f}%)")
    
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

# ============ توابع سرویس‌ها (برای دریافت داده) ============
def fetch_and_store_all():
    """دریافت داده از TGJU و ذخیره در دیتابیس"""
    subdomains = ["call2", "call3", "call4"]
    call = random.choice(subdomains)
    url = f"https://{call}.tgju.org/ajax.json?rev=test"
    
    headers = {
        "accept": "*/*",
        "origin": "https://www.tgju.org",
        "referer": "https://www.tgju.org",
        "user-agent": "Mozilla/5.0"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    data = response.json()
    current = data["current"]
    
    prices = {
        "gold": float(current["geram18"]["p"].replace(",", "")),
        "usd": float(current["price_dollar_rl"]["p"].replace(",", "")),
        "ounce": float(current["ons"]["p"].replace(",", "")),
        "coin": float(current["sekee"]["p"].replace(",", ""))
    }
    
    with session_scope() as session:
        for symbol, price in prices.items():
            tick = MarketHistory(
                symbol=symbol,
                price=price,
                created_at=datetime.now(),
                source='tgju'
            )
            session.add(tick)
    
    return prices

def build_candles_for_all_symbols():
    """ساخت شمع از تیک‌ها - با جلوگیری از درج تکراری"""
    symbols = ['gold', 'usd', 'ounce', 'coin']
    
    with session_scope() as session:
        for symbol in symbols:
            ticks = session.query(MarketHistory).filter(
                MarketHistory.symbol == symbol
            ).order_by(MarketHistory.created_at).all()
            
            if len(ticks) < 2:
                continue
            
            # ساخت شمع ۱ دقیقه
            for i in range(len(ticks) - 1):
                candle_time = ticks[i].created_at.replace(second=0, microsecond=0)
                
                # بررسی وجود شمع تکراری
                existing = session.query(MarketCandle).filter(
                    and_(
                        MarketCandle.symbol == symbol,
                        MarketCandle.timeframe == '1m',
                        MarketCandle.candle_time == candle_time
                    )
                ).first()
                
                if existing:
                    # اگر شمع وجود دارد، آن را به‌روز می‌کنیم
                    existing.open = ticks[i].price
                    existing.high = max(ticks[i].price, ticks[i+1].price)
                    existing.low = min(ticks[i].price, ticks[i+1].price)
                    existing.close = ticks[i+1].price
                    existing.volume += 2
                    existing.tick_count += 2
                else:
                    # شمع جدید ایجاد می‌کنیم
                    candle = MarketCandle(
                        symbol=symbol,
                        timeframe='1m',
                        candle_time=candle_time,
                        open=ticks[i].price,
                        high=max(ticks[i].price, ticks[i+1].price),
                        low=min(ticks[i].price, ticks[i+1].price),
                        close=ticks[i+1].price,
                        volume=2,
                        tick_count=2
                    )
                    session.add(candle)

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
            "/update-get",
            "/fix-db",
            "/reset-db",
            "/health"
        ]
    }

@app.get("/prices", response_model=List[PriceResponse])
async def get_prices():
    """دریافت قیمت‌های لحظه‌ای"""
    subdomains = ["call2", "call3", "call4"]
    call = random.choice(subdomains)
    url = f"https://{call}.tgju.org/ajax.json?rev=test"
    
    headers = {
        "accept": "*/*",
        "origin": "https://www.tgju.org",
        "referer": "https://www.tgju.org",
        "user-agent": "Mozilla/5.0"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        current = data["current"]
        
        prices = {
            "gold": float(current["geram18"]["p"].replace(",", "")),
            "usd": float(current["price_dollar_rl"]["p"].replace(",", "")),
            "ounce": float(current["ons"]["p"].replace(",", "")),
            "coin": float(current["sekee"]["p"].replace(",", ""))
        }
        
        return [
            PriceResponse(
                symbol=symbol,
                price=price,
                timestamp=datetime.now().isoformat()
            )
            for symbol, price in prices.items()
        ]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unable to fetch prices: {str(e)}")

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
    """به‌روزرسانی داده‌ها از TGJU با POST"""
    try:
        fetch_and_store_all()
        build_candles_for_all_symbols()
        return {
            "status": "success",
            "message": "Data updated successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/update-get")
async def update_data_get():
    """به‌روزرسانی داده‌ها از TGJU با GET (برای تست در مرورگر)"""
    try:
        fetch_and_store_all()
        build_candles_for_all_symbols()
        return {
            "status": "success",
            "message": "Data updated successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/fix-db")
async def fix_database():
    """تعمیر دیتابیس - اضافه کردن ستون‌های گم‌شده"""
    import sqlite3
    from pathlib import Path
    
    try:
        db_path = Path(__file__).parent / 'database' / 'market.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # بررسی و اضافه کردن ستون‌ها به market_history
        cursor.execute("PRAGMA table_info(market_history)")
        columns = [col[1] for col in cursor.fetchall()]
        
        added = []
        if 'raw_data' not in columns:
            cursor.execute("ALTER TABLE market_history ADD COLUMN raw_data TEXT")
            added.append('raw_data')
            print("✅ Added raw_data column to market_history")
        
        if 'source' not in columns:
            cursor.execute("ALTER TABLE market_history ADD COLUMN source TEXT DEFAULT 'tgju'")
            added.append('source')
            print("✅ Added source column to market_history")
        
        # بررسی و اضافه کردن ستون‌ها به market_candles
        cursor.execute("PRAGMA table_info(market_candles)")
        columns = [col[1] for col in cursor.fetchall()]
        
        if 'tick_count' not in columns:
            cursor.execute("ALTER TABLE market_candles ADD COLUMN tick_count INTEGER DEFAULT 0")
            added.append('tick_count (market_candles)')
            print("✅ Added tick_count column to market_candles")
        
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE market_candles ADD COLUMN updated_at DATETIME")
            added.append('updated_at (market_candles)')
            print("✅ Added updated_at column to market_candles")
        
        conn.commit()
        conn.close()
        
        return {
            "status": "success",
            "message": "Database fixed successfully",
            "columns_added": added,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@app.get("/reset-db")
async def reset_database():
    """بازسازی کامل دیتابیس - هشدار: تمام داده‌ها حذف می‌شوند!"""
    global engine, SessionLocal
    
    try:
        # 1. بستن تمام اتصالات موجود
        # با ایجاد engine جدید، اتصالات قبلی بسته می‌شوند
        
        # 2. حذف فایل دیتابیس
        if DB_PATH.exists():
            os.remove(DB_PATH)
            print(f"✅ Database file removed: {DB_PATH}")
        
        # 3. ایجاد یک engine جدید و مستقل
        temp_engine = create_engine(
            f"sqlite:///{DB_PATH}",
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=False
        )
        
        # 4. ایجاد همه جداول با مدل‌های تعریف‌شده
        Base.metadata.create_all(temp_engine)
        print("✅ Tables recreated successfully")
        
        # 5. به‌روزرسانی engine و SessionLocal برای استفاده در کل برنامه
        engine = temp_engine
        SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine
        )
        
        return {
            "status": "success",
            "message": "Database reset successfully. All tables recreated.",
            "timestamp": datetime.now().isoformat()
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