# -*- coding: utf-8 -*-
"""
مدیریت سرمایه و سبدگردانی - نسخه بهبودیافته
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass
from .scenario_weights import get_scenario_weights, get_all_scenarios
from ..risk.risk_manager import RiskManager

@dataclass
class Asset:
    symbol: str
    name: str
    price: float
    volatility: float
    trend_score: int
    rsi: float

class PortfolioManager:
    """مدیریت و تخصیص بهینه سرمایه"""
    
    def __init__(self, total_capital: float):
        self.total_capital = total_capital
        self.assets = []
        self.risk_manager = RiskManager()
    
    def add_asset(self, symbol: str, name: str, price: float, 
                  volatility: float, trend_score: int, rsi: float):
        """افزودن یک دارایی به پرتفوی"""
        self.assets.append(Asset(
            symbol=symbol,
            name=name,
            price=price,
            volatility=volatility,
            trend_score=trend_score,
            rsi=rsi
        ))
    
    def calculate_expected_return(self, asset: Asset) -> float:
        """محاسبه بازده مورد انتظار هر دارایی"""
        trend_factor = (asset.trend_score - 50) / 50
        rsi_factor = (asset.rsi - 50) / 50
        volatility_penalty = asset.volatility / 100
        
        expected_return = (trend_factor * 0.5 + rsi_factor * 0.3 - volatility_penalty * 0.2)
        return max(0, min(1, expected_return + 0.5))
    
    def calculate_risk_score(self, asset: Asset) -> float:
        """محاسبه نمره ریسک هر دارایی"""
        volatility_score = min(1, asset.volatility / 5)
        rsi_risk = abs(asset.rsi - 50) / 50
        trend_risk = abs(asset.trend_score - 50) / 50
        
        return min(1, volatility_score * 0.5 + rsi_risk * 0.3 + trend_risk * 0.2)
    
    def generate_recommendations(self) -> List[Dict]:
        """
        تولید پیشنهادات سرمایه‌گذاری با سناریوهای واقعی
        """
        if not self.assets:
            return []
        
        scenarios = get_all_scenarios()
        recommendations = []
        
        for scenario in scenarios:
            weights = get_scenario_weights(scenario['id'])
            
            # محاسبه تخصیص بر اساس وزن‌ها
            allocations = {}
            total_return = 0
            total_risk = 0
            
            for asset in self.assets:
                weight = weights.get(asset.symbol, 0)
                amount = self.total_capital * weight
                quantity = amount / asset.price if asset.price > 0 else 0
                
                # محاسبه بازده و ریسک
                expected_return = self.calculate_expected_return(asset) * weight
                risk_score = self.calculate_risk_score(asset) * weight
                total_return += expected_return
                total_risk += risk_score
                
                # محاسبه حد ضرر و سود
                risk_metrics = self.risk_manager.get_risk_metrics(
                    capital=amount,
                    entry_price=asset.price,
                    current_price=asset.price
                )
                
                allocations[asset.symbol] = {
                    'amount_toman': amount,
                    'quantity': quantity,
                    'weight_percent': weight * 100,
                    'price': asset.price,
                    'stop_loss': risk_metrics['stop_loss'],
                    'take_profit': risk_metrics['take_profit'],
                    'max_loss': risk_metrics['max_loss'],
                    'max_profit': risk_metrics['max_profit']
                }
            
            recommendations.append({
                'scenario': scenario['name'],
                'color': scenario['color'],
                'description': scenario['description'],
                'allocations': allocations,
                'expected_return': total_return * 100,
                'expected_risk': total_risk * 100,
                'sharpe_ratio': total_return / (total_risk + 0.01) if total_risk > 0 else 0
            })
        
        return recommendations