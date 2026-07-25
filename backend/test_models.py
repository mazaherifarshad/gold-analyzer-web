import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from backend.database.connection import session_scope
from backend.database.models import MarketHistory, MarketCandle
from datetime import datetime

print("=" * 50)
print("TESTING DATABASE MODELS")
print("=" * 50)

try:
    with session_scope() as session:
        history = MarketHistory(symbol='test_gold', price=123.45, source='test')
        session.add(history)
        print("SUCCESS: MarketHistory saved!")
        
        candle = MarketCandle(
            symbol='test_gold',
            timeframe='1h',
            candle_time=datetime.now(),
            open=100, high=110, low=95, close=105, volume=1000
        )
        session.add(candle)
        print("SUCCESS: MarketCandle saved!")
        
        history_count = session.query(MarketHistory).count()
        candle_count = session.query(MarketCandle).count()
        print(f"History records: {history_count}")
        print(f"Candle records: {candle_count}")
        
        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("=" * 50)
        
except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()