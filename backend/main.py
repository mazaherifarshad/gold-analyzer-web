# -*- coding: utf-8 -*-
"""
زرین‌سنج API - نسخه نهایی
Zarinsanj API - Final Version
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

Base.metadata.create_all(engine)

@contextmanager
def session_scope():
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
    title="Zarinsanj API",
    description="تحلیل‌گر حرفه‌ای بازار طلا و ارز ایران",
    version="2.1.0"
)

# ============ CORS ============
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ مدل‌های پاسخ ============
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
    volatility_status: str
    final_score: float
    recommendation: str
    confidence: int
    reasons: List[str]
    candle_count: int
    timestamp: str

# ============ اطلاعات نسخه ============
APP_VERSION = "V2.1"
DEVELOPER = "F.Mazaheri"
COPYRIGHT = "© 2026 Zarinsanj. All rights reserved."

# ============ تابع تحلیل هوشمند ============
def analyze_symbol(symbol: str, timeframe: str = '1m') -> dict:
    """تحلیل کامل با محاسبات دقیق و اندیکاتورهای پیشرفته"""
    import pandas as pd
    import numpy as np
    
    with session_scope() as session:
        candles = session.query(MarketCandle).filter(
            MarketCandle.symbol == symbol,
            MarketCandle.timeframe == timeframe
        ).order_by(MarketCandle.candle_time).all()
        
        if len(candles) < 20:
            return {'error': f'Not enough candles for {symbol} (need 20, have {len(candles)})'}
        
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
    
    # ===== اندیکاتورهای پیشرفته =====
    
    # 1. EMA
    df['ema_9'] = df['close'].ewm(span=9, adjust=False).mean()
    df['ema_21'] = df['close'].ewm(span=21, adjust=False).mean()
    df['ema_50'] = df['close'].ewm(span=50, adjust=False).mean()
    
    # 2. MACD
    ema_fast = df['close'].ewm(span=12, adjust=False).mean()
    ema_slow = df['close'].ewm(span=26, adjust=False).mean()
    df['macd'] = ema_fast - ema_slow
    df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
    df['macd_histogram'] = df['macd'] - df['macd_signal']
    
    # 3. RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    # 4. باند بولینگر
    df['bb_middle'] = df['close'].rolling(window=20).mean()
    df['bb_std'] = df['close'].rolling(window=20).std()
    df['bb_upper'] = df['bb_middle'] + (df['bb_std'] * 2)
    df['bb_lower'] = df['bb_middle'] - (df['bb_std'] * 2)
    
    # 5. ATR
    high_low = df['high'] - df['low']
    high_close = (df['high'] - df['close'].shift()).abs()
    low_close = (df['low'] - df['close'].shift()).abs()
    ranges = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    df['atr'] = ranges.rolling(window=14).mean()
    
    # 6. Stochastic Oscillator
    low_14 = df['low'].rolling(window=14).min()
    high_14 = df['high'].rolling(window=14).max()
    df['stoch_k'] = 100 * ((df['close'] - low_14) / (high_14 - low_14))
    df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
    
    # ===== شاخص‌های ترکیبی =====
    current = df.iloc[-1]
    
    # 1. امتیاز روند (ترکیب EMA و MACD)
    trend_score = 50
    if current['close'] > current['ema_9'] > current['ema_21']:
        trend_score = 75
    elif current['close'] > current['ema_9']:
        trend_score = 65
    elif current['close'] < current['ema_9'] < current['ema_21']:
        trend_score = 25
    elif current['close'] < current['ema_9']:
        trend_score = 35
    
    # 2. امتیاز مومنتوم (RSI + Stochastic)
    rsi = current['rsi']
    stoch_k = current['stoch_k'] if not pd.isna(current['stoch_k']) else 50
    
    if not pd.isna(rsi) and not pd.isna(stoch_k):
        if rsi > 70 and stoch_k > 80:
            momentum_score = 70  # Overbought
        elif rsi < 30 and stoch_k < 20:
            momentum_score = 30  # Oversold
        elif rsi > 60 and stoch_k > 60:
            momentum_score = 65
        elif rsi < 40 and stoch_k < 40:
            momentum_score = 35
        elif rsi > 50:
            momentum_score = 60
        else:
            momentum_score = 40
    else:
        momentum_score = 50
    
    # 3. امتیاز نوسان (ATR)
    atr = current['atr'] if not pd.isna(current['atr']) else 0
    avg_atr = df['atr'].mean() if not pd.isna(df['atr'].mean()) else 1
    
    if atr > 0 and avg_atr > 0:
        if atr > avg_atr * 1.5:
            volatility_score = 70
            volatility_status = 'HIGH'
        elif atr < avg_atr * 0.5:
            volatility_score = 30
            volatility_status = 'LOW'
        else:
            volatility_score = 50
            volatility_status = 'NORMAL'
    else:
        volatility_score = 50
        volatility_status = 'NORMAL'
    
    # 4. امتیاز موقعیت در باند بولینگر
    bb_position = 50
    if current['bb_upper'] != current['bb_lower']:
        bb_position = (current['close'] - current['bb_lower']) / (current['bb_upper'] - current['bb_lower']) * 100
    bb_score = 50 + (bb_position - 50) * 0.3
    
    # 5. امتیاز MACD
    macd_score = 50
    if not pd.isna(current['macd']) and not pd.isna(current['macd_signal']):
        if current['macd'] > current['macd_signal'] and current['macd_histogram'] > 0:
            macd_score = 70
        elif current['macd'] < current['macd_signal'] and current['macd_histogram'] < 0:
            macd_score = 30
        elif current['macd'] > current['macd_signal']:
            macd_score = 60
        else:
            macd_score = 40
    
    # ===== امتیاز نهایی هوشمند =====
    final_score = (
        trend_score * 0.30 +
        momentum_score * 0.25 +
        volatility_score * 0.15 +
        bb_score * 0.15 +
        macd_score * 0.15
    )
    
    # محدود کردن به بازه 0-100
    final_score = max(0, min(100, final_score))
    
    # ===== تشخیص روند =====
    if trend_score > 65 and macd_score > 60:
        trend = 'STRONG UPTREND'
    elif trend_score > 60:
        trend = 'UPTREND'
    elif trend_score < 35 and macd_score < 40:
        trend = 'STRONG DOWNTREND'
    elif trend_score < 40:
        trend = 'DOWNTREND'
    else:
        trend = 'CONSOLIDATION'
    
    # ===== مومنتوم =====
    if momentum_score > 60:
        momentum = 'BULLISH'
    elif momentum_score < 40:
        momentum = 'BEARISH'
    else:
        momentum = 'NEUTRAL'
    
    # ===== توصیه =====
    if final_score >= 75:
        recommendation = 'STRONG BUY'
        confidence = 85
    elif final_score >= 60:
        recommendation = 'BUY'
        confidence = 70
    elif final_score >= 45:
        recommendation = 'HOLD'
        confidence = 55
    elif final_score >= 30:
        recommendation = 'SELL'
        confidence = 70
    else:
        recommendation = 'STRONG SELL'
        confidence = 85
    
    # ===== دلایل =====
    reasons = []
    if trend_score > 60:
        reasons.append(f"روند صعودی (امتیاز: {trend_score:.0f})")
    elif trend_score < 40:
        reasons.append(f"روند نزولی (امتیاز: {trend_score:.0f})")
    
    if rsi > 70:
        reasons.append(f"اشباع خرید (RSI: {rsi:.1f})")
    elif rsi < 30:
        reasons.append(f"اشباع فروش (RSI: {rsi:.1f})")
    
    if volatility_status == 'HIGH':
        reasons.append(f"نوسان بالا (ATR: {atr:.0f})")
    elif volatility_status == 'LOW':
        reasons.append(f"نوسان پایین (ATR: {atr:.0f})")
    
    if macd_score > 60:
        reasons.append(f"سیگنال خرید MACD (هیستوگرام: {current['macd_histogram']:.2f})")
    elif macd_score < 40:
        reasons.append(f"سیگنال فروش MACD (هیستوگرام: {current['macd_histogram']:.2f})")
    
    # ===== بازگشت نتیجه =====
    return {
        'symbol': symbol,
        'current_price': float(current['close']),
        'trend': trend,
        'trend_score': int(trend_score),
        'rsi': float(rsi) if not pd.isna(rsi) else 50,
        'momentum': momentum,
        'volatility': float(atr),
        'volatility_status': volatility_status,
        'final_score': float(final_score),
        'recommendation': recommendation,
        'confidence': confidence,
        'reasons': reasons,
        'candle_count': len(candles),
        'timestamp': datetime.now().isoformat()
    }

# ============ تابع مشاور سرمایه‌گذاری هوشمند ============
def get_portfolio_recommendations(capital: float) -> List[Dict]:
    """تولید پیشنهادات سرمایه‌گذاری با محاسبات دقیق"""
    
    symbols = ['gold', 'usd', 'coin']
    analyses = {}
    for symbol in symbols:
        result = analyze_symbol(symbol)
        if 'error' not in result:
            analyses[symbol] = result
    
    if not analyses:
        return []
    
    # ===== محاسبه بازده و ریسک =====
    returns = {}
    risks = {}
    for symbol, analysis in analyses.items():
        # بازده مورد انتظار
        trend_factor = (analysis['trend_score'] - 50) / 50
        rsi_factor = (analysis['rsi'] - 50) / 50
        expected_return = trend_factor * 0.5 + rsi_factor * 0.3
        returns[symbol] = max(0.1, min(0.9, expected_return + 0.5))
        
        # ریسک
        volatility_risk = min(1, analysis['volatility'] / 100) if analysis['volatility'] > 0 else 0.3
        trend_risk = abs(analysis['trend_score'] - 50) / 50
        risks[symbol] = volatility_risk * 0.6 + trend_risk * 0.4
    
    # ===== نسبت شارپ =====
    sharpe = {}
    total_sharpe = 0
    for symbol in returns:
        if risks[symbol] > 0:
            s = returns[symbol] / risks[symbol]
        else:
            s = returns[symbol] / 0.01
        sharpe[symbol] = s
        total_sharpe += s
    
    if total_sharpe == 0:
        total_sharpe = 1
    
    # ===== تولید ۳ سناریو =====
    scenarios = [
        {'name': 'محافظه‌کارانه', 'multiplier': 0.7, 'color': '🟢'},
        {'name': 'متعادل', 'multiplier': 1.0, 'color': '🟡'},
        {'name': 'جسورانه', 'multiplier': 1.3, 'color': '🔴'}
    ]
    
    recommendations = []
    for scenario in scenarios:
        allocations = {}
        for symbol in sharpe:
            raw_weight = (sharpe[symbol] / total_sharpe) * scenario['multiplier']
            allocations[symbol] = min(raw_weight, 0.5)
        
        # نرمال‌سازی
        total = sum(allocations.values())
        if total > 0:
            for symbol in allocations:
                allocations[symbol] = allocations[symbol] / total
        
        # محاسبه مقادیر
        amounts = {}
        for symbol, weight in allocations.items():
            amount = capital * weight
            price = analyses.get(symbol, {}).get('current_price', 1)
            quantity = amount / price if price > 0 else 0
            unit = 'قطعه' if symbol == 'coin' else 'واحد'
            
            # گرد کردن سکه
            if symbol == 'coin':
                quantity = max(1, round(quantity))
                amount = quantity * price
            
            amounts[symbol] = {
                'amount_toman': amount,
                'quantity': quantity,
                'weight_percent': weight * 100,
                'price': price,
                'unit': unit
            }
        
        # محاسبه بازده و ریسک کل سبد
        total_return = 0
        total_risk = 0
        for symbol, weight in allocations.items():
            total_return += weight * returns.get(symbol, 0)
            total_risk += weight * risks.get(symbol, 0)
        
        recommendations.append({
            'scenario': scenario['name'],
            'color': scenario['color'],
            'allocations': amounts,
            'expected_return': total_return * 100,
            'expected_risk': total_risk * 100,
            'sharpe_ratio': total_return / (total_risk + 0.01) if total_risk > 0 else 0
        })
    
    return recommendations

# ============ توابع دریافت داده ============
def fetch_and_store_all():
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
    symbols = ['gold', 'usd', 'ounce', 'coin']
    
    with session_scope() as session:
        for symbol in symbols:
            ticks = session.query(MarketHistory).filter(
                MarketHistory.symbol == symbol
            ).order_by(MarketHistory.created_at).all()
            
            if len(ticks) < 2:
                continue
            
            for i in range(len(ticks) - 1):
                candle_time = ticks[i].created_at.replace(second=0, microsecond=0)
                existing = session.query(MarketCandle).filter(
                    and_(
                        MarketCandle.symbol == symbol,
                        MarketCandle.timeframe == '1m',
                        MarketCandle.candle_time == candle_time
                    )
                ).first()
                
                if existing:
                    existing.open = ticks[i].price
                    existing.high = max(ticks[i].price, ticks[i+1].price)
                    existing.low = min(ticks[i].price, ticks[i+1].price)
                    existing.close = ticks[i+1].price
                    existing.volume += 2
                    existing.tick_count += 2
                else:
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
        "name": "Zarinsanj API",
        "version": APP_VERSION,
        "developer": DEVELOPER,
        "copyright": COPYRIGHT,
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
            "/health",
            "/portfolio"
        ]
    }

@app.get("/prices", response_model=List[PriceResponse])
async def get_prices():
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
    symbols = ['gold', 'usd', 'ounce', 'coin']
    results = []
    
    for symbol in symbols:
        result = analyze_symbol(symbol)
        if 'error' not in result:
            results.append(AnalysisResponse(**result))
    
    return results

@app.get("/analysis/{symbol}", response_model=AnalysisResponse)
async def get_symbol_analysis(symbol: str):
    result = analyze_symbol(symbol)
    if 'error' in result:
        raise HTTPException(status_code=404, detail=result['error'])
    return AnalysisResponse(**result)

@app.get("/candles/{symbol}")
async def get_candles(symbol: str, timeframe: str = '1m', limit: int = 50):
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
    try:
        db_path = Path(__file__).parent / 'database' / 'market.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(market_history)")
        columns = [col[1] for col in cursor.fetchall()]
        
        added = []
        if 'raw_data' not in columns:
            cursor.execute("ALTER TABLE market_history ADD COLUMN raw_data TEXT")
            added.append('raw_data')
        
        if 'source' not in columns:
            cursor.execute("ALTER TABLE market_history ADD COLUMN source TEXT DEFAULT 'tgju'")
            added.append('source')
        
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
    global engine, SessionLocal
    
    try:
        if DB_PATH.exists():
            os.remove(DB_PATH)
        
        temp_engine = create_engine(
            f"sqlite:///{DB_PATH}",
            connect_args={'check_same_thread': False},
            poolclass=StaticPool,
            echo=False
        )
        
        Base.metadata.create_all(temp_engine)
        
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

@app.get("/portfolio")
async def get_portfolio(capital: float = 10000000):
    try:
        recommendations = get_portfolio_recommendations(capital)
        if not recommendations:
            return {
                "status": "error",
                "message": "Unable to generate recommendations. Not enough data."
            }
        
        return {
            "status": "success",
            "capital": capital,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat(),
            "version": APP_VERSION,
            "developer": DEVELOPER
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)