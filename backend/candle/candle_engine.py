# -*- coding: utf-8 -*-
"""
Candle Engine - تبدیل تیک‌ها به شمع‌های OHLC
این ماژول قلب سیستم است که داده‌های لحظه‌ای را به شمع تبدیل می‌کند
"""

from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc

from backend.database.models import MarketHistory, MarketCandle
from backend.database.connection import session_scope
import logging

logger = logging.getLogger(__name__)


class CandleEngine:
    """
    موتور ساخت شمع از تیک‌ها
    """
    
    # تایم‌فریم‌های پشتیبانی شده به دقیقه
    TIMEFRAMES = {
        '1m': 1,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '1h': 60,
        '4h': 240,
        '1d': 1440
    }
    
    def __init__(self, session: Optional[Session] = None):
        self.session = session
        
    def _get_session(self) -> Session:
        """دریافت session دیتابیس"""
        if self.session is None:
            return session_scope().__enter__()
        return self.session
    
    def _round_time(self, dt: datetime, timeframe: str) -> datetime:
        """
        گرد کردن زمان به شروع تایم‌فریم مربوطه
        مثلاً برای 5m: 09:03 -> 09:00
        """
        minutes = self.TIMEFRAMES.get(timeframe, 1)
        
        if timeframe == '1d':
            return dt.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # محاسبه دقیقه‌های گذشته از نیمه‌شب
        total_minutes = dt.hour * 60 + dt.minute
        rounded_minutes = (total_minutes // minutes) * minutes
        hour = rounded_minutes // 60
        minute = rounded_minutes % 60
        
        return dt.replace(hour=hour, minute=minute, second=0, microsecond=0)
    
    def build_candle_from_ticks(self, ticks: List[MarketHistory]) -> Optional[Dict]:
        """
        ساخت یک شمع از لیست تیک‌ها
        """
        if not ticks:
            return None
        
        # مرتب‌سازی تیک‌ها بر اساس زمان
        sorted_ticks = sorted(ticks, key=lambda t: t.created_at)
        
        # قیمت‌های OHLC
        open_price = sorted_ticks[0].price
        close_price = sorted_ticks[-1].price
        high_price = max(t.price for t in sorted_ticks)
        low_price = min(t.price for t in sorted_ticks)
        
        # نماد و زمان
        symbol = sorted_ticks[0].symbol
        candle_time = self._round_time(sorted_ticks[0].created_at, '1m')  # پیش‌فرض 1 دقیقه
        
        return {
            'symbol': symbol,
            'timeframe': '1m',
            'candle_time': candle_time,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': len(ticks),  # تعداد تیک‌ها به عنوان حجم
            'tick_count': len(ticks)
        }
    
    def get_ticks_for_candle(self, session: Session, symbol: str, 
                             start_time: datetime, end_time: datetime) -> List[MarketHistory]:
        """
        دریافت تیک‌های یک بازه زمانی مشخص
        """
        return session.query(MarketHistory).filter(
            and_(
                MarketHistory.symbol == symbol,
                MarketHistory.created_at >= start_time,
                MarketHistory.created_at < end_time
            )
        ).order_by(MarketHistory.created_at).all()
    
    def build_all_candles_for_symbol(self, symbol: str, timeframe: str = '1m') -> int:
        """
        ساخت تمام شمع‌های یک نماد از تیک‌های موجود
        بازگشت: تعداد شمع‌های ساخته شده
        """
        with session_scope() as session:
            # دریافت اولین و آخرین تیک
            first_tick = session.query(MarketHistory).filter(
                MarketHistory.symbol == symbol
            ).order_by(MarketHistory.created_at).first()
            
            last_tick = session.query(MarketHistory).filter(
                MarketHistory.symbol == symbol
            ).order_by(desc(MarketHistory.created_at)).first()
            
            if not first_tick or not last_tick:
                logger.warning(f"No ticks found for symbol: {symbol}")
                return 0
            
            # زمان شروع و پایان
            start_time = self._round_time(first_tick.created_at, timeframe)
            end_time = self._round_time(last_tick.created_at, timeframe)
            
            # محاسبه فاصله زمانی به دقیقه
            minutes_diff = int((end_time - start_time).total_seconds() / 60)
            step_minutes = self.TIMEFRAMES.get(timeframe, 1)
            
            if minutes_diff <= 0:
                return 0
            
            candle_count = 0
            current_time = start_time
            
            while current_time <= end_time:
                next_time = current_time + timedelta(minutes=step_minutes)
                
                # دریافت تیک‌های این بازه
                ticks = self.get_ticks_for_candle(
                    session, symbol, current_time, next_time
                )
                
                if ticks:
                    # ساخت شمع
                    candle_data = self.build_candle_from_ticks(ticks)
                    if candle_data:
                        candle_data['timeframe'] = timeframe
                        candle_data['candle_time'] = current_time
                        
                        # ذخیره در دیتابیس
                        self._save_candle(session, candle_data)
                        candle_count += 1
                
                current_time = next_time
            
            logger.info(f"Built {candle_count} candles for {symbol} ({timeframe})")
            return candle_count
    
    def _save_candle(self, session: Session, candle_data: Dict) -> MarketCandle:
        """
        ذخیره یا به‌روزرسانی یک شمع در دیتابیس
        """
        # بررسی وجود شمع
        existing = session.query(MarketCandle).filter(
            and_(
                MarketCandle.symbol == candle_data['symbol'],
                MarketCandle.timeframe == candle_data['timeframe'],
                MarketCandle.candle_time == candle_data['candle_time']
            )
        ).first()
        
        if existing:
            # به‌روزرسانی
            existing.open = candle_data['open']
            existing.high = max(existing.high, candle_data['high'])
            existing.low = min(existing.low, candle_data['low'])
            existing.close = candle_data['close']
            existing.volume += candle_data.get('volume', 0)
            existing.tick_count += candle_data.get('tick_count', 0)
            session.flush()
            return existing
        else:
            # ایجاد جدید
            candle = MarketCandle(
                symbol=candle_data['symbol'],
                timeframe=candle_data['timeframe'],
                candle_time=candle_data['candle_time'],
                open=candle_data['open'],
                high=candle_data['high'],
                low=candle_data['low'],
                close=candle_data['close'],
                volume=candle_data.get('volume', 0),
                tick_count=candle_data.get('tick_count', 0)
            )
            session.add(candle)
            session.flush()
            return candle
    
    def build_all_timeframes(self, symbol: str) -> Dict[str, int]:
        """
        ساخت تمام تایم‌فریم‌ها برای یک نماد
        بازگشت: دیکشنری با تعداد شمع‌های ساخته شده برای هر تایم‌فریم
        """
        results = {}
        
        for timeframe in self.TIMEFRAMES.keys():
            count = self.build_all_candles_for_symbol(symbol, timeframe)
            results[timeframe] = count
        
        return results
    
    def get_latest_candle(self, symbol: str, timeframe: str = '1m') -> Optional[MarketCandle]:
        """
        دریافت آخرین شمع برای یک نماد و تایم‌فریم
        """
        with session_scope() as session:
            return session.query(MarketCandle).filter(
                and_(
                    MarketCandle.symbol == symbol,
                    MarketCandle.timeframe == timeframe
                )
            ).order_by(desc(MarketCandle.candle_time)).first()
    
    def get_candles(self, symbol: str, timeframe: str = '1m', 
                    limit: int = 100) -> List[MarketCandle]:
        """
        دریافت شمع‌های اخیر برای یک نماد و تایم‌فریم
        """
        with session_scope() as session:
            return session.query(MarketCandle).filter(
                and_(
                    MarketCandle.symbol == symbol,
                    MarketCandle.timeframe == timeframe
                )
            ).order_by(desc(MarketCandle.candle_time)).limit(limit).all()


def build_candles_for_all_symbols() -> Dict[str, Dict[str, int]]:
    """
    ساخت شمع برای تمام نمادهای موجود در دیتابیس
    """
    with session_scope() as session:
        # دریافت لیست نمادهای موجود
        symbols = session.query(MarketHistory.symbol).distinct().all()
        symbols = [s[0] for s in symbols]
    
    engine = CandleEngine()
    results = {}
    
    for symbol in symbols:
        if symbol != 'test_gold':  # حذف داده‌های تست
            print(f"Building candles for {symbol}...")
            results[symbol] = engine.build_all_timeframes(symbol)
    
    return results


# تابع برای اجرای مستقیم
if __name__ == "__main__":
    print("=" * 50)
    print("CANDLE ENGINE - Building candles from ticks")
    print("=" * 50)
    
    results = build_candles_for_all_symbols()
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    print("=" * 50)
    for symbol, timeframes in results.items():
        print(f"\n{symbol}:")
        for tf, count in timeframes.items():
            print(f"  {tf}: {count} candles")