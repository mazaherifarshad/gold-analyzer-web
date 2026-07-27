# -*- coding: utf-8 -*-
"""
مدیریت ریسک و محاسبه حد ضرر و سود
"""

from typing import Dict, Tuple
import math

class RiskManager:
    """مدیریت ریسک سرمایه‌گذاری"""
    
    def __init__(self, risk_percent: float = 2.0):
        """
        risk_percent: درصد ریسک به ازای هر معامله (پیش‌فرض ۲٪)
        """
        self.risk_percent = risk_percent
    
    def calculate_stop_loss(self, entry_price: float, risk_percent: float = None) -> float:
        """
        محاسبه حد ضرر
        """
        if risk_percent is None:
            risk_percent = self.risk_percent
        
        return entry_price * (1 - risk_percent / 100)
    
    def calculate_take_profit(self, entry_price: float, reward_ratio: float = 2.0) -> float:
        """
        محاسبه حد سود با نسبت ریسک به ریوارد
        """
        stop_loss = self.calculate_stop_loss(entry_price)
        risk_amount = entry_price - stop_loss
        return entry_price + (risk_amount * reward_ratio)
    
    def calculate_position_size(self, capital: float, entry_price: float, 
                                stop_loss_price: float) -> float:
        """
        محاسبه اندازه موقعیت (تعداد واحد) بر اساس سرمایه و حد ضرر
        """
        if entry_price <= 0 or stop_loss_price >= entry_price:
            return 0
        
        risk_per_unit = entry_price - stop_loss_price
        if risk_per_unit <= 0:
            return 0
        
        max_risk = capital * (self.risk_percent / 100)
        return max_risk / risk_per_unit
    
    def get_risk_metrics(self, capital: float, entry_price: float, 
                         current_price: float) -> Dict:
        """
        دریافت شاخص‌های ریسک
        """
        stop_loss = self.calculate_stop_loss(entry_price)
        take_profit = self.calculate_take_profit(entry_price)
        
        position_size = self.calculate_position_size(capital, entry_price, stop_loss)
        
        # محاسبه سود/ضرر احتمالی
        potential_loss = (entry_price - stop_loss) * position_size
        potential_profit = (take_profit - entry_price) * position_size
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_size,
            'max_loss': potential_loss,
            'max_profit': potential_profit,
            'risk_reward_ratio': (take_profit - entry_price) / (entry_price - stop_loss) if (entry_price - stop_loss) > 0 else 0
        }