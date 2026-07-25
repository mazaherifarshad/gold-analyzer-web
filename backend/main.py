# -*- coding: utf-8 -*-
"""
FastAPI Server - Gold Market Analyzer API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from datetime import datetime
import uvicorn
import sqlite3
import os

from backend.database.connection import session_scope, engine
from backend.database.models import MarketCandle, MarketHistory, AnalysisResult, Base
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

# ... (بقیه مدل‌ها و توابع مانند قبل) ...

# ============ ایجاد App ============

app = FastAPI(
    title="Gold Market Analyzer API",
    description="Professional AI-based Gold Market Analysis for Iranian Market",
    version="1.0.0"
)

# ============ CORS ============

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============ تابع تحلیل (مانند قبل) ============
# ... (تابع analyze_symbol اینجا قرار می‌گیرد) ...

# ============ اندپوینت‌های API ============

@app.get("/")
async def root():
    return {
        "name": "Gold Market Analyzer API",
        "version": "1.0.0",
        "status": "online",
        "endpoints": [
            "/prices", "/analysis", "/analysis/{symbol}",
            "/candles/{symbol}", "/update", "/update-get",
            "/fix-db", "/reset-db", "/health"
        ]
    }

# ... (سایر اندپوینت‌ها مانند prices, analysis, candles, update, fix-db, health مانند قبل) ...

# ============ اندپوینت جدید برای بازسازی دیتابیس ============

@app.get("/reset-db")
async def reset_database():
    """بازسازی کامل دیتابیس - هشدار: تمام داده‌ها حذف می‌شوند!"""
    try:
        # 1. حذف فایل دیتابیس
        db_path = os.path.join(os.path.dirname(__file__), "database", "market.db")
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"✅ Database file removed: {db_path}")
        
        # 2. ایجاد مجدد دیتابیس و جداول
        Base.metadata.create_all(engine)
        print("✅ Tables recreated successfully")
        
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

# ============ اجرا ============

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)