# -*- coding: utf-8 -*-
"""
TGJU Data Fetcher - نسخه نهایی با API رسمی
دریافت داده‌های بازار از سایت TGJU
"""

import random
import requests
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class TGJUClient:
    """
    کلاینت دریافت داده از TGJU با استفاده از API رسمی
    """
    
    # زیردامنه‌های مختلف برای پایداری بیشتر
    SUBDOMAINS = ["call2", "call3", "call4"]
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            "accept": "*/*",
            "origin": "https://www.tgju.org",
            "referer": "https://www.tgju.org",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
    
    def get_current_prices(self) -> Dict[str, float]:
        """
        دریافت قیمت‌های لحظه‌ای تمام نمادها
        بازگشت: دیکشنری با قیمت‌های gold, usd, ounce, coin
        """
        # انتخاب یک زیردامنه تصادفی
        subdomain = random.choice(self.SUBDOMAINS)
        url = f"https://{subdomain}.tgju.org/ajax.json?rev=test"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            current = data.get("current", {})
            
            # استخراج قیمت‌ها
            result = {}
            
            # طلای ۱۸ عیار
            if "geram18" in current:
                price_str = current["geram18"].get("p", "0").replace(",", "")
                result["gold"] = float(price_str)
            
            # دلار
            if "price_dollar_rl" in current:
                price_str = current["price_dollar_rl"].get("p", "0").replace(",", "")
                result["usd"] = float(price_str)
            
            # انس جهانی
            if "ons" in current:
                price_str = current["ons"].get("p", "0").replace(",", "")
                result["ounce"] = float(price_str)
            
            # سکه بهار آزادی
            if "sekee" in current:
                price_str = current["sekee"].get("p", "0").replace(",", "")
                result["coin"] = float(price_str)
            
            return result
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching data from TGJU: {e}")
            return {}
        except (KeyError, ValueError) as e:
            logger.error(f"Error parsing TGJU response: {e}")
            return {}
    
    def get_price(self, symbol: str) -> Optional[float]:
        """
        دریافت قیمت یک نماد خاص
        """
        prices = self.get_current_prices()
        return prices.get(symbol)


def fetch_and_store_all() -> Dict[str, int]:
    """
    دریافت و ذخیره‌سازی داده‌های تمام نمادها در دیتابیس
    بازگشت: تعداد تیک‌های ذخیره شده برای هر نماد
    """
    from backend.database.connection import session_scope
    from backend.database.models import MarketHistory
    
    client = TGJUClient()
    results = {symbol: 0 for symbol in ['gold', 'usd', 'ounce', 'coin']}
    
    # دریافت قیمت‌ها
    prices = client.get_current_prices()
    
    if not prices:
        print("❌ No data received from TGJU")
        return results
    
    print("\n📊 Data received from TGJU:")
    for symbol, price in prices.items():
        print(f"  {symbol}: {price:,.2f}")
    
    # ذخیره در دیتابیس
    with session_scope() as session:
        now = datetime.now()
        
        for symbol, price in prices.items():
            try:
                # بررسی وجود تیک تکراری در همین دقیقه
                start_of_minute = now.replace(second=0, microsecond=0)
                
                existing = session.query(MarketHistory).filter(
                    MarketHistory.symbol == symbol,
                    MarketHistory.created_at >= start_of_minute
                ).first()
                
                if not existing:
                    tick = MarketHistory(
                        symbol=symbol,
                        price=price,
                        created_at=now,
                        source='tgju'
                    )
                    session.add(tick)
                    results[symbol] = 1
                    print(f"  ✅ {symbol}: {price:,.2f} stored")
                else:
                    print(f"  ⏭️ {symbol}: Duplicate, skipped")
                    
            except Exception as e:
                logger.error(f"Error storing {symbol}: {e}")
                results[symbol] = 0
        
        session.commit()
    
    return results


def fetch_and_build_candles():
    """
    دریافت داده و ساخت شمع به صورت یکجا
    """
    from backend.candle.candle_engine import build_candles_for_all_symbols
    
    print("=" * 60)
    print("FETCHING DATA AND BUILDING CANDLES")
    print("=" * 60)
    
    # دریافت داده
    store_results = fetch_and_store_all()
    
    # ساخت شمع
    print("\n🔄 Building candles...")
    candle_results = build_candles_for_all_symbols()
    
    # نمایش نتایج
    print("\n" + "=" * 60)
    print("FINAL RESULTS:")
    print("=" * 60)
    
    for symbol in ['gold', 'usd', 'ounce', 'coin']:
        print(f"\n{symbol.upper()}:")
        print(f"  Ticks stored: {store_results.get(symbol, 0)}")
        if symbol in candle_results:
            print(f"  Candles:")
            for tf, count in candle_results[symbol].items():
                if count > 0:
                    print(f"    {tf}: {count}")
    
    return store_results, candle_results


if __name__ == "__main__":
    # تست مستقیم
    print("=" * 60)
    print("TGJU CLIENT TEST")
    print("=" * 60)
    
    client = TGJUClient()
    prices = client.get_current_prices()
    
    if prices:
        print("\n✅ Prices received successfully:")
        for symbol, price in prices.items():
            print(f"  {symbol}: {price:,.2f}")
        
        # ذخیره در دیتابیس
        print("\n💾 Storing in database...")
        fetch_and_store_all()
        
        print("\n" + "=" * 60)
        print("TEST COMPLETE!")
    else:
        print("\n❌ Failed to receive data from TGJU")