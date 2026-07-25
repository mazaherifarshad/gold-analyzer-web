# -*- coding: utf-8 -*-
"""
Trend Analysis Module
"""

import pandas as pd
import numpy as np


class TrendAnalyzer:
    """تحلیل روند با استفاده از EMA و MACD"""
    
    def analyze(self, df: pd.DataFrame) -> dict:
        """تحلیل روند قیمت"""
        if len(df) < 10:
            return {'trend': 'neutral', 'strength': 0}
        
        close = df['close']
        
        # محاسبه EMA
        ema_9 = close.ewm(span=9).mean()
        ema_21 = close.ewm(span=21).mean()
        ema_50 = close.ewm(span=50).mean()
        
        # تشخیص روند
        current_price = close.iloc[-1]
        trend = 'neutral'
        strength = 0
        
        if current_price > ema_9.iloc[-1] > ema_21.iloc[-1] > ema_50.iloc[-1]:
            trend = 'bullish'
            strength = 80
        elif current_price < ema_9.iloc[-1] < ema_21.iloc[-1] < ema_50.iloc[-1]:
            trend = 'bearish'
            strength = 80
        elif current_price > ema_9.iloc[-1] > ema_21.iloc[-1]:
            trend = 'bullish'
            strength = 60
        elif current_price < ema_9.iloc[-1] < ema_21.iloc[-1]:
            trend = 'bearish'
            strength = 60
        else:
            trend = 'neutral'
            strength = 30
        
        return {
            'trend': trend,
            'strength': strength,
            'ema_9': ema_9.iloc[-1],
            'ema_21': ema_21.iloc[-1],
            'ema_50': ema_50.iloc[-1] if len(close) >= 50 else None
        }