"""
CRUD Operations for Database
عملیات پایه دیتابیس
"""

from sqlalchemy.orm import Session
from sqlalchemy import desc, and_, func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from .models import MarketHistory, MarketCandle, AnalysisResult


class MarketHistoryCRUD:
    """عملیات روی داده‌های Tick"""
    
    @staticmethod
    def create(session: Session, symbol: str, price: float, 
               created_at: Optional[datetime] = None,
               raw_data: Optional[str] = None) -> MarketHistory:
        """ذخیره یک تیک جدید"""
        if created_at is None:
            created_at = datetime.utcnow()
            
        record = MarketHistory(
            symbol=symbol,
            price=price,
            created_at=created_at,
            raw_data=raw_data
        )
        session.add(record)
        session.flush()
        return record
    
    @staticmethod
    def get_latest(session: Session, symbol: str) -> Optional[MarketHistory]:
        """دریافت آخرین تیک برای یک نماد"""
        return session.query(MarketHistory).filter(
            MarketHistory.symbol == symbol
        ).order_by(desc(MarketHistory.created_at)).first()
    
    @staticmethod
    def get_range(session: Session, symbol: str, 
                  start_time: datetime, end_time: datetime) -> List[MarketHistory]:
        """دریافت تیک‌های یک بازه زمانی"""
        return session.query(MarketHistory).filter(
            and_(
                MarketHistory.symbol == symbol,
                MarketHistory.created_at >= start_time,
                MarketHistory.created_at <= end_time
            )
        ).order_by(MarketHistory.created_at).all()
    
    @staticmethod
    def get_count(session: Session, symbol: str) -> int:
        """تعداد تیک‌های یک نماد"""
        return session.query(MarketHistory).filter(
            MarketHistory.symbol == symbol
        ).count()


class MarketCandleCRUD:
    """عملیات روی داده‌های شمع"""
    
    @staticmethod
    def create_or_update(session: Session, symbol: str, timeframe: str,
                         candle_time: datetime, open_price: float,
                         high: float, low: float, close: float,
                         volume: float = 0.0, tick_count: int = 0) -> MarketCandle:
        """ایجاد یا به‌روزرسانی یک شمع"""
        
        # بررسی وجود شمع
        existing = session.query(MarketCandle).filter(
            and_(
                MarketCandle.symbol == symbol,
                MarketCandle.timeframe == timeframe,
                MarketCandle.candle_time == candle_time
            )
        ).first()
        
        if existing:
            # به‌روزرسانی
            existing.open = open_price
            existing.high = max(existing.high, high) if existing.high else high
            existing.low = min(existing.low, low) if existing.low else low
            existing.close = close
            existing.volume += volume
            existing.tick_count += tick_count
            existing.updated_at = datetime.utcnow()
            session.flush()
            return existing
        else:
            # ایجاد جدید
            candle = MarketCandle(
                symbol=symbol,
                timeframe=timeframe,
                candle_time=candle_time,
                open=open_price,
                high=high,
                low=low,
                close=close,
                volume=volume,
                tick_count=tick_count
            )
            session.add(candle)
            session.flush()
            return candle
    
    @staticmethod
    def get_candles(session: Session, symbol: str, timeframe: str,
                    limit: int = 100, offset: int = 0) -> List[MarketCandle]:
        """دریافت شمع‌های یک نماد و تایم‌فریم"""
        return session.query(MarketCandle).filter(
            and_(
                MarketCandle.symbol == symbol,
                MarketCandle.timeframe == timeframe
            )
        ).order_by(desc(MarketCandle.candle_time)).limit(limit).offset(offset).all()
    
    @staticmethod
    def get_candles_since(session: Session, symbol: str, timeframe: str,
                          since: datetime) -> List[MarketCandle]:
        """دریافت شمع‌های یک بازه زمانی"""
        return session.query(MarketCandle).filter(
            and_(
                MarketCandle.symbol == symbol,
                MarketCandle.timeframe == timeframe,
                MarketCandle.candle_time >= since
            )
        ).order_by(MarketCandle.candle_time).all()
    
    @staticmethod
    def get_candle_count(session: Session, symbol: str, timeframe: str) -> int:
        """تعداد شمع‌های یک نماد و تایم‌فریم"""
        return session.query(MarketCandle).filter(
            and_(
                MarketCandle.symbol == symbol,
                MarketCandle.timeframe == timeframe
            )
        ).count()
    
    @staticmethod
    def get_latest_candle(session: Session, symbol: str, timeframe: str) -> Optional[MarketCandle]:
        """دریافت آخرین شمع"""
        return session.query(MarketCandle).filter(
            and_(
                MarketCandle.symbol == symbol,
                MarketCandle.timeframe == timeframe
            )
        ).order_by(desc(MarketCandle.candle_time)).first()


class AnalysisResultCRUD:
    """عملیات روی نتایج تحلیل"""
    
    @staticmethod
    def create(session: Session, symbol: str, timeframe: str,
               score: float, confidence: float, recommendation: str,
               details: Dict[str, Any]) -> AnalysisResult:
        """ذخیره نتیجه تحلیل"""
        
        result = AnalysisResult(
            symbol=symbol,
            timeframe=timeframe,
            score=score,
            confidence=confidence,
            recommendation=recommendation,
            details=str(details) if details else None,
            # امتیازات ماژول‌ها از details استخراج می‌شود
            trend_score=details.get('trend', 0),
            momentum_score=details.get('momentum', 0),
            divergence_score=details.get('divergence', 0),
            bubble_score=details.get('bubble', 0),
            iran_market_score=details.get('iran_market', 0),
            smart_money_score=details.get('smart_money', 0),
            support_resistance_score=details.get('support_resistance', 0),
            multi_timeframe_score=details.get('multi_timeframe', 0),
            volatility_score=details.get('volatility', 0),
            risk_score=details.get('risk', 0),
            volume_score=details.get('volume', 0)
        )
        session.add(result)
        session.flush()
        return result
    
    @staticmethod
    def get_latest(session: Session, symbol: str) -> Optional[AnalysisResult]:
        """دریافت آخرین تحلیل برای یک نماد"""
        return session.query(AnalysisResult).filter(
            AnalysisResult.symbol == symbol
        ).order_by(desc(AnalysisResult.analysis_time)).first()
    
    @staticmethod
    def get_history(session: Session, symbol: str, limit: int = 50) -> List[AnalysisResult]:
        """دریافت تاریخچه تحلیل‌ها"""
        return session.query(AnalysisResult).filter(
            AnalysisResult.symbol == symbol
        ).order_by(desc(AnalysisResult.analysis_time)).limit(limit).all()