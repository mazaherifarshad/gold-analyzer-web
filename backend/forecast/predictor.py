# -*- coding: utf-8 -*-
"""
پیش‌بینی قیمت و تحلیل آینده‌نگری
"""

import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from typing import Dict, List, Tuple

class PricePredictor:
    """پیش‌بینی قیمت با استفاده از مدل‌های آماری"""
    
    def __init__(self, prediction_days: int = 7):
        self.prediction_days = prediction_days
    
    def predict_linear(self, prices: List[float]) -> Dict:
        """
        پیش‌بینی با رگرسیون خطی
        """
        if len(prices) < 5:
            return {'error': 'داده‌های کافی برای پیش‌بینی وجود ندارد'}
        
        X = np.array(range(len(prices))).reshape(-1, 1)
        y = np.array(prices)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # پیش‌بینی برای روزهای آینده
        future_X = np.array(range(len(prices), len(prices) + self.prediction_days)).reshape(-1, 1)
        predictions = model.predict(future_X)
        
        # محاسبه دقت (R²)
        r2_score = model.score(X, y)
        
        return {
            'method': 'linear_regression',
            'predictions': predictions.tolist(),
            'confidence': max(0, min(100, r2_score * 100)),
            'trend': 'up' if predictions[-1] > prices[-1] else 'down',
            'next_day': predictions[0] if len(predictions) > 0 else None,
            'last_price': prices[-1],
            'price_change': predictions[-1] - prices[-1]
        }
    
    def predict_polynomial(self, prices: List[float], degree: int = 2) -> Dict:
        """
        پیش‌بینی با رگرسیون چندجمله‌ای
        """
        if len(prices) < 10:
            return {'error': 'داده‌های کافی برای پیش‌بینی وجود ندارد'}
        
        X = np.array(range(len(prices))).reshape(-1, 1)
        y = np.array(prices)
        
        poly = PolynomialFeatures(degree=degree)
        X_poly = poly.fit_transform(X)
        
        model = LinearRegression()
        model.fit(X_poly, y)
        
        future_X = np.array(range(len(prices), len(prices) + self.prediction_days)).reshape(-1, 1)
        future_X_poly = poly.transform(future_X)
        predictions = model.predict(future_X_poly)
        
        return {
            'method': f'polynomial_{degree}',
            'predictions': predictions.tolist(),
            'trend': 'up' if predictions[-1] > prices[-1] else 'down',
            'next_day': predictions[0] if len(predictions) > 0 else None,
            'last_price': prices[-1],
            'price_change': predictions[-1] - prices[-1]
        }