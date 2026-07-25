"""
Database Models for Gold Market Analyzer
مدل‌های دیتابیس برای تحلیل‌گر بازار طلا
"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index, UniqueConstraint, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class MarketHistory(Base):
    """مدل ذخیره‌سازی داده‌های Tick (لحظه‌ای)"""
    __tablename__ = 'market_history'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    symbol = Column(String(50), nullable=False, index=True)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    source = Column(String(50), default='tgju')
    
    __table_args__ = (
        Index('idx_history_symbol_time', 'symbol', 'created_at'),
    )
    
    def __repr__(self):
        return f"<MarketHistory(symbol='{self.symbol}', price={self.price})>"


class MarketCandle(Base):
    """مدل ذخیره‌سازی شمع‌های OHLC"""
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
    tick_count = Column(Integer, default=0)
    
    __table_args__ = (
        UniqueConstraint('symbol', 'timeframe', 'candle_time', name='uq_candle'),
        Index('idx_candle_symbol_timeframe_time', 'symbol', 'timeframe', 'candle_time'),
    )
    
    def to_dict(self) -> dict:
        return {
            'symbol': self.symbol,
            'timeframe': self.timeframe,
            'candle_time': self.candle_time.isoformat() if self.candle_time else None,
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume,
        }