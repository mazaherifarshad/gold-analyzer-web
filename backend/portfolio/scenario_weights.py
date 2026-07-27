# -*- coding: utf-8 -*-
"""
وزن‌دهی سناریوهای مختلف سرمایه‌گذاری
"""

# وزن‌های پیشنهادی برای هر سناریو
SCENARIO_WEIGHTS = {
    'conservative': {
        'gold': 0.50,   # ۵۰٪ طلا (دارایی امن)
        'usd': 0.20,    # ۲۰٪ دلار
        'ounce': 0.05,  # ۵٪ انس (نوسان بالا)
        'coin': 0.25    # ۲۵٪ سکه
    },
    'moderate': {
        'gold': 0.35,   # ۳۵٪ طلا
        'usd': 0.25,    # ۲۵٪ دلار
        'ounce': 0.15,  # ۱۵٪ انس
        'coin': 0.25    # ۲۵٪ سکه
    },
    'aggressive': {
        'gold': 0.20,   # ۲۰٪ طلا
        'usd': 0.15,    # ۱۵٪ دلار
        'ounce': 0.30,  # ۳۰٪ انس (بازده بالا)
        'coin': 0.35    # ۳۵٪ سکه
    }
}

def get_scenario_weights(scenario: str) -> dict:
    """
    دریافت وزن‌های یک سناریو
    """
    return SCENARIO_WEIGHTS.get(scenario, SCENARIO_WEIGHTS['moderate'])

def get_all_scenarios():
    """
    دریافت لیست تمام سناریوها با توضیحات
    """
    return [
        {
            'id': 'conservative',
            'name': 'محافظه‌کارانه',
            'color': '🟢',
            'description': 'مناسب برای سرمایه‌گذاران با ریسک‌پذیری پایین. تمرکز بر حفظ سرمایه و بازده پایدار.',
            'weights': SCENARIO_WEIGHTS['conservative']
        },
        {
            'id': 'moderate',
            'name': 'متعادل',
            'color': '🟡',
            'description': 'مناسب برای سرمایه‌گذاران با ریسک‌پذیری متوسط. ترکیبی از بازده و امنیت.',
            'weights': SCENARIO_WEIGHTS['moderate']
        },
        {
            'id': 'aggressive',
            'name': 'جسورانه',
            'color': '🔴',
            'description': 'مناسب برای سرمایه‌گذاران با ریسک‌پذیری بالا. هدف کسب بازده حداکثری.',
            'weights': SCENARIO_WEIGHTS['aggressive']
        }
    ]