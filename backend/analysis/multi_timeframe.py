import pandas as pd


def analyze_multi_timeframe(df: pd.DataFrame):

    if len(df) < 60:

        return {

            "score": 0,

            "state": "NO_DATA",

            "description": "داده کافی برای تحلیل چندبازه‌ای وجود ندارد."

        }

    ema20 = float(df.iloc[-1]["ema20"])
    ema50 = float(df.iloc[-1]["ema50"])

    ema20_mid = float(df.iloc[-20]["ema20"])
    ema50_mid = float(df.iloc[-20]["ema50"])

    ema20_old = float(df.iloc[-60]["ema20"])
    ema50_old = float(df.iloc[-60]["ema50"])

    score = 0

    reasons = []

    # کوتاه مدت

    if ema20 > ema50:

        score += 5

        reasons.append("روند کوتاه‌مدت صعودی")

    else:

        score -= 5

        reasons.append("روند کوتاه‌مدت نزولی")

    # میان مدت

    if ema20_mid > ema50_mid:

        score += 5

        reasons.append("روند میان‌مدت صعودی")

    else:

        score -= 5

        reasons.append("روند میان‌مدت نزولی")

    # بلند مدت

    if ema20_old > ema50_old:

        score += 5

        reasons.append("روند بلندمدت صعودی")

    else:

        score -= 5

        reasons.append("روند بلندمدت نزولی")

    if score >= 10:

        state = "STRONG_UP"

        description = "تمام بازه‌های زمانی روند صعودی را تأیید می‌کنند."

    elif score >= 3:

        state = "UP"

        description = "اکثر بازه‌های زمانی صعودی هستند."

    elif score <= -10:

        state = "STRONG_DOWN"

        description = "تمام بازه‌های زمانی روند نزولی را تأیید می‌کنند."

    elif score <= -3:

        state = "DOWN"

        description = "اکثر بازه‌های زمانی نزولی هستند."

    else:

        state = "MIXED"

        description = "بین بازه‌های زمانی اختلاف نظر وجود دارد."

    return {

        "score": score,

        "state": state,

        "description": description,

        "reasons": reasons

    }