# -*- coding: utf-8 -*-
"""
تحلیل اخبار و رویدادهای اقتصادی
"""

import requests
from typing import Dict, List
from datetime import datetime

class NewsAnalyzer:
    """تحلیل اخبار و رویدادهای اقتصادی"""
    
    def __init__(self):
        self.keywords = {
            'positive': ['افزایش', 'رشد', 'صعود', 'بهبود', 'مثبت', 'تثبیت', 'ثبات'],
            'negative': ['کاهش', 'ریزش', 'نزول', 'بحران', 'منفی', 'افت', 'سقوط'],
            'gold': ['طلا', 'gold', 'طلایی', 'انس', 'سکه'],
            'usd': ['دلار', 'dollar', 'ارز', 'نرخ ارز'],
            'interest': ['نرخ بهره', 'interest rate', 'بهره']
        }
    
    def analyze_news(self, news_items: List[Dict]) -> Dict:
        """
        تحلیل اخبار و محاسبه تأثیر بر بازار
        """
        impact_score = 0
        topics = []
        
        for item in news_items[:5]:
            text = item.get('title', '')
            sentiment = self._analyze_sentiment(text)
            impact_score += sentiment['score']
            
            for topic in sentiment.get('topics', []):
                if topic not in topics:
                    topics.append(topic)
        
        # نرمال‌سازی
        impact_score = max(-1, min(1, impact_score / 3))
        
        return {
            'impact_score': impact_score,
            'impact_level': 'high' if abs(impact_score) > 0.5 else 'medium' if abs(impact_score) > 0.2 else 'low',
            'topics': topics,
            'direction': 'positive' if impact_score > 0.2 else 'negative' if impact_score < -0.2 else 'neutral',
            'message': self._get_impact_message(impact_score)
        }
    
    def _analyze_sentiment(self, text: str) -> Dict:
        """تحلیل احساسات متن خبر"""
        score = 0
        topics = []
        
        for word in self.keywords['positive']:
            if word in text:
                score += 1
                if word in ['طلا', 'gold', 'انس', 'سکه']:
                    topics.append('gold')
                elif word in ['دلار', 'dollar', 'ارز']:
                    topics.append('usd')
        
        for word in self.keywords['negative']:
            if word in text:
                score -= 1
                if word in ['طلا', 'gold', 'انس', 'سکه']:
                    topics.append('gold')
                elif word in ['دلار', 'dollar', 'ارز']:
                    topics.append('usd')
        
        normalized_score = max(-1, min(1, score / 5))
        
        return {
            'score': normalized_score,
            'sentiment': 'positive' if normalized_score > 0.2 else 'negative' if normalized_score < -0.2 else 'neutral',
            'topics': list(set(topics))
        }
    
    def _get_impact_message(self, score: float) -> str:
        """دریافت پیام تأثیر خبر"""
        if score > 0.5:
            return "اخبار مثبت تأثیر قابل توجهی بر بازار داشته است."
        elif score > 0.2:
            return "اخبار تا حدودی مثبت هستند."
        elif score < -0.5:
            return "اخبار منفی تأثیر قابل توجهی بر بازار داشته است."
        elif score < -0.2:
            return "اخبار تا حدودی منفی هستند."
        else:
            return "اخبار تأثیر چندانی بر بازار ندارند."