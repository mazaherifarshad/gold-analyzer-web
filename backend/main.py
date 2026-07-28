# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
import uvicorn
import sqlite3
import os
import random
import requests
from pathlib import Path
from contextlib import contextmanager

from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Index, UniqueConstraint, Text, and_
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

Base = declarative_base()

# ===== مدل‌ها =====
class MarketHistory(Base):
    __tablename__ = 'market_history'
    id = Column(Integer, primary_key=True)
    symbol = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(50), default='tgju')
    raw_data = Column(Text, nullable=True)

class MarketCandle(Base):
    __tablename__ = 'market_candles'
    id = Column(Integer, primary_key=True)
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

# ===== دیتابیس =====
DB_PATH = Path(__file__).parent / 'database' / 'market.db'
DB_PATH.parent.mkdir(parents=True, exist_ok=True)
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False}, poolclass=StaticPool, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
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

# ===== FastAPI =====
app = FastAPI(title="Zarinsanj API", version="3.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ===== مدل‌های پاسخ =====
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
    final_score: float
    recommendation: str
    confidence: int
    reasons: List[str]
    timestamp: str

# ===== تحلیل =====
def analyze_symbol(symbol: str, timeframe: str = '1m') -> dict:
    import pandas as pd
    import numpy as np
    
    with session_scope() as session:
        candles = session.query(MarketCandle).filter(
            MarketCandle.symbol == symbol,
            MarketCandle.timeframe == timeframe
        ).order_by(MarketCandle.candle_time).all()
        
        if len(candles) < 20:
            return {'error': f'Not enough candles for {symbol}'}
        
        df = pd.DataFrame([{
            'time': c.candle_time,
            'open': c.open,
            'high': c.high,
            'low': c.low,
            'close': c.close,
            'volume': c.volume
        } for c in candles])
        df.set_index('time', inplace=True)
        df = df.sort_index()
    
    # RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    current_rsi = rsi.iloc[-1] if not pd.isna(rsi.iloc[-1]) else 50
    
    # روند
    ema_9 = df['close'].ewm(span=9, adjust=False).mean()
    ema_21 = df['close'].ewm(span=21, adjust=False).mean()
    current_price = df['close'].iloc[-1]
    
    if current_price > ema_9.iloc[-1] and ema_9.iloc[-1] > ema_21.iloc[-1]:
        trend, trend_score = 'STRONG UPTREND', 80
    elif current_price > ema_9.iloc[-1]:
        trend, trend_score = 'UPTREND', 65
    elif current_price < ema_9.iloc[-1] and ema_9.iloc[-1] < ema_21.iloc[-1]:
        trend, trend_score = 'STRONG DOWNTREND', 20
    elif current_price < ema_9.iloc[-1]:
        trend, trend_score = 'DOWNTREND', 35
    else:
        trend, trend_score = 'CONSOLIDATION', 50
    
    final_score = (trend_score * 0.6) + (current_rsi * 0.4)
    
    if final_score >= 75:
        recommendation, confidence = 'STRONG BUY', 85
    elif final_score >= 60:
        recommendation, confidence = 'BUY', 70
    elif final_score >= 45:
        recommendation, confidence = 'HOLD', 55
    elif final_score >= 30:
        recommendation, confidence = 'SELL', 70
    else:
        recommendation, confidence = 'STRONG SELL', 85
    
    reasons = []
    if trend_score > 60:
        reasons.append(f"روند صعودی (امتیاز: {trend_score})")
    elif trend_score < 40:
        reasons.append(f"روند نزولی (امتیاز: {trend_score})")
    if current_rsi > 70:
        reasons.append(f"اشباع خرید (RSI: {current_rsi:.1f})")
    elif current_rsi < 30:
        reasons.append(f"اشباع فروش (RSI: {current_rsi:.1f})")
    
    return {
        'symbol': symbol,
        'current_price': float(current_price),
        'trend': trend,
        'trend_score': trend_score,
        'rsi': float(current_rsi),
        'momentum': 'BULLISH' if current_rsi > 50 else 'BEARISH' if current_rsi < 50 else 'NEUTRAL',
        'final_score': float(final_score),
        'recommendation': recommendation,
        'confidence': confidence,
        'reasons': reasons,
        'timestamp': datetime.now().isoformat()
    }

# ===== پیشنهاد سرمایه‌گذاری =====
def get_portfolio_recommendations(capital: float) -> List[Dict]:
    symbols = ['gold', 'usd', 'coin']
    analyses = {}
    for symbol in symbols:
        result = analyze_symbol(symbol)
        if 'error' not in result:
            analyses[symbol] = result
    
    if not analyses:
        return []
    
    returns = {}
    risks = {}
    for symbol, analysis in analyses.items():
        trend_factor = (analysis['trend_score'] - 50) / 50
        rsi_factor = (analysis['rsi'] - 50) / 50
        returns[symbol] = max(0.1, min(0.9, 0.5 + trend_factor * 0.3 + rsi_factor * 0.2))
        risks[symbol] = 0.3 + abs(analysis['rsi'] - 50) / 100
    
    sharpe = {}
    total_sharpe = 0
    for symbol in returns:
        s = returns[symbol] / (risks[symbol] + 0.01)
        sharpe[symbol] = s
        total_sharpe += s
    
    if total_sharpe == 0:
        total_sharpe = 1
    
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
        
        total = sum(allocations.values())
        if total > 0:
            for symbol in allocations:
                allocations[symbol] = allocations[symbol] / total
        
        amounts = {}
        for symbol, weight in allocations.items():
            amount = capital * weight
            price = analyses.get(symbol, {}).get('current_price', 1)
            quantity = amount / price if price > 0 else 0
            unit = 'قطعه' if symbol == 'coin' else 'واحد'
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
        
        total_return = sum(weight * returns.get(symbol, 0) for symbol, weight in allocations.items())
        total_risk = sum(weight * risks.get(symbol, 0) for symbol, weight in allocations.items())
        
        recommendations.append({
            'scenario': scenario['name'],
            'color': scenario['color'],
            'allocations': amounts,
            'expected_return': total_return * 100,
            'expected_risk': total_risk * 100,
            'sharpe_ratio': total_return / (total_risk + 0.01) if total_risk > 0 else 0
        })
    
    return recommendations

# ===== دریافت داده =====
def fetch_and_store_all():
    subdomains = ["call2", "call3", "call4"]
    call = random.choice(subdomains)
    url = f"https://{call}.tgju.org/ajax.json?rev=test"
    headers = {"accept": "*/*", "origin": "https://www.tgju.org", "referer": "https://www.tgju.org", "user-agent": "Mozilla/5.0"}
    
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    current = response.json()["current"]
    
    # قیمت‌ها به ریال هستند (هیچ ضربی انجام نمی‌شود)
    prices = {
        "gold": float(current["geram18"]["p"].replace(",", "")),
        "usd": float(current["price_dollar_rl"]["p"].replace(",", "")),
        "ounce": float(current["ons"]["p"].replace(",", "")),
        "coin": float(current["sekee"]["p"].replace(",", ""))
    }
    
    with session_scope() as session:
        for symbol, price in prices.items():
            session.add(MarketHistory(symbol=symbol, price=price, created_at=datetime.now(), source='tgju'))
    return prices

def build_candles_for_all_symbols():
    symbols = ['gold', 'usd', 'ounce', 'coin']
    with session_scope() as session:
        for symbol in symbols:
            ticks = session.query(MarketHistory).filter(MarketHistory.symbol == symbol).order_by(MarketHistory.created_at).all()
            if len(ticks) < 2:
                continue
            for i in range(len(ticks) - 1):
                candle_time = ticks[i].created_at.replace(second=0, microsecond=0)
                existing = session.query(MarketCandle).filter(
                    and_(MarketCandle.symbol == symbol, MarketCandle.timeframe == '1m', MarketCandle.candle_time == candle_time)
                ).first()
                if existing:
                    existing.open = ticks[i].price
                    existing.high = max(ticks[i].price, ticks[i+1].price)
                    existing.low = min(ticks[i].price, ticks[i+1].price)
                    existing.close = ticks[i+1].price
                    existing.volume += 2
                    existing.tick_count += 2
                else:
                    session.add(MarketCandle(
                        symbol=symbol, timeframe='1m', candle_time=candle_time,
                        open=ticks[i].price, high=max(ticks[i].price, ticks[i+1].price),
                        low=min(ticks[i].price, ticks[i+1].price), close=ticks[i+1].price,
                        volume=2, tick_count=2
                    ))

# ===== API =====
@app.get("/")
async def root():
    return {"name": "Zarinsanj API", "version": "3.1.0", "developer": "F.Mazaheri", "status": "online"}

@app.get("/prices", response_model=List[PriceResponse])
async def get_prices():
    try:
        subdomains = ["call2", "call3", "call4"]
        call = random.choice(subdomains)
        url = f"https://{call}.tgju.org/ajax.json?rev=test"
        response = requests.get(url, headers={"accept": "*/*", "origin": "https://www.tgju.org", "referer": "https://www.tgju.org", "user-agent": "Mozilla/5.0"}, timeout=10)
        response.raise_for_status()
        current = response.json()["current"]
        prices = {
            "gold": float(current["geram18"]["p"].replace(",", "")),
            "usd": float(current["price_dollar_rl"]["p"].replace(",", "")),
            "ounce": float(current["ons"]["p"].replace(",", "")),
            "coin": float(current["sekee"]["p"].replace(",", ""))
        }
        return [PriceResponse(symbol=s, price=p, timestamp=datetime.now().isoformat()) for s, p in prices.items()]
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Unable to fetch prices: {str(e)}")

@app.get("/analysis", response_model=List[AnalysisResponse])
async def get_all_analysis():
    results = []
    for symbol in ['gold', 'usd', 'ounce', 'coin']:
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

@app.get("/portfolio")
async def get_portfolio(capital: float = 10000000):
    try:
        recommendations = get_portfolio_recommendations(capital)
        if not recommendations:
            return {"status": "error", "message": "Unable to generate recommendations."}
        return {"status": "success", "capital": capital, "recommendations": recommendations, "timestamp": datetime.now().isoformat()}
    except Exception as e:
        return {"status": "error", "message": str(e)}

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
            added.append('tick_count')
        if 'updated_at' not in columns:
            cursor.execute("ALTER TABLE market_candles ADD COLUMN updated_at DATETIME")
            added.append('updated_at')
        conn.commit()
        conn.close()
        return {"status": "success", "message": "Database fixed", "columns_added": added}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/health")
async def health_check():
    try:
        with session_scope() as session:
            count = session.query(MarketHistory).count()
        return {"status": "healthy", "database": "connected", "records": count}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.post("/update")
async def update_data():
    try:
        fetch_and_store_all()
        build_candles_for_all_symbols()
        return {"status": "success", "message": "Data updated successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)