# -*- coding: utf-8 -*-
"""
Database Models for Gold Market Analyzer
این فایل شامل تمام مدل‌های دیتابیس است
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index, UniqueConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()


class MarketHistory(Base):
    """
    مدل ذخیره‌سازی داده‌های Tick (لحظه‌ای)
    این داده‌ها خام هستند و فقط برای ساخت شمع استفاده می‌شوند
    """
    __tablename__ = 'market_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)  # gold, usd, ounce, coin
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # اطلاعات اضافی برای ردیابی
    source = Column(String(50), default='tgju')
    raw_data = Column(Text, nullable=True)  # ذخیره داده خام برای دیباگ
    
    __table_args__ = (
        Index('idx_history_symbol_time', 'symbol', 'created_at'),
    )
    
    def __repr__(self):
        return f"<MarketHistory(symbol='{self.symbol}', price={self.price}, time={self.created_at})>"


class MarketCandle(Base):
    """
    مدل ذخیره‌سازی شمع‌های OHLC
    این داده‌ها منبع اصلی برای تحلیل هستند
    """
    __tablename__ = 'market_candles'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)  # gold, usd, ounce, coin
    timeframe = Column(String(10), nullable=False, index=True)  # 1m, 5m, 15m, 30m, 1h, 4h, 1d
    candle_time = Column(DateTime, nullable=False, index=True)  # زمان شروع شمع
    
    # قیمت‌های OHLC
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, default=0.0)
    
    # متادیتا
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # تعداد تیک‌های استفاده شده برای ساخت این شمع
    tick_count = Column(Integer, default=0)
    
    __table_args__ = (
        # هر ترکیب symbol + timeframe + candle_time یکتا است
        UniqueConstraint('symbol', 'timeframe', 'candle_time', name='uq_candle'),
        # ایندکس‌های ترکیبی برای کوئری‌های سریع
        Index('idx_candle_symbol_timeframe_time', 'symbol', 'timeframe', 'candle_time'),
        Index('idx_candle_timeframe_time', 'timeframe', 'candle_time'),
    )
    
    def to_dict(self) -> dict:
        """تبدیل به دیکشنری برای استفاده در API"""
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'candle_time': self.candle_time.isoformat() if self.candle_time else None,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
            'tick_count': self.tick_count
        }
    
    def __repr__(self):
        return f"<MarketCandle(symbol='{self.symbol}', tf='{self.timeframe}', time={self.candle_time}, O={self.open}, C={self.close})>"


class AnalysisResult(Base):
    """
    مدل ذخیره‌سازی نتایج تحلیل
    برای کش کردن نتایج و دسترسی سریع
    """
    __tablename__ = 'analysis_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    timeframe = Column(String(10), nullable=False)
    analysis_time = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # نتایج اصلی
    score = Column(Float, nullable=False)  # 0-100
    confidence = Column(Float, nullable=False)  # 0-100
    recommendation = Column(String(20), nullable=False)  # BUY, SELL, HOLD, STRONG_BUY, STRONG_SELL
    
    # جزئیات
    details = Column(Text, nullable=True)  # JSON با جزئیات کامل
    
    # امتیازات هر ماژول
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
    
    __table_args__ = (
        Index('idx_analysis_symbol_time', 'symbol', 'analysis_time'),
    )
    
    def __repr__(self):
        return f"<AnalysisResult(symbol='{self.symbol}', rec='{self.recommendation}', score={self.score})>"