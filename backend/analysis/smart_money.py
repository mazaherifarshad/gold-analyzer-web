import pandas as pd


def analyze_smart_money(df: pd.DataFrame):

    if len(df) < 30:

        return {

            "score": 0,

            "state": "NO_DATA",

            "description": "داده کافی وجود ندارد."

        }

    last = df.iloc[-1]

    close = float(last["gold"])

    ema20 = float(last["ema20"])

    ema50 = float(last["ema50"])

    atr = float(last["atr"])

    score = 0

    reasons = []

    # قدرت روند

    if ema20 > ema50:

        score += 8

        reasons.append("EMA20 بالاتر از EMA50")

    else:

        score -= 8

        reasons.append("EMA20 پایین‌تر از EMA50")

    # فاصله قیمت از EMA20

    distance = ((close - ema20) / ema20) * 100

    if distance > 1:

        score += 3

        reasons.append("قیمت بالاتر از EMA20")

    elif distance < -1:

        score -= 3

        reasons.append("قیمت پایین‌تر از EMA20")

    # نوسان

    volatility = (atr / close) * 100

    if volatility > 1.5:

        score -= 2

        reasons.append("نوسان زیاد")

    else:

        score += 2

        reasons.append("نوسان کنترل‌شده")

    if score >= 10:

        state = "ACCUMULATION"

        description = "احتمال ورود پول هوشمند و فاز انباشت."

    elif score >= 4:

        state = "BULLISH"

        description = "قدرت خریداران بیشتر از فروشندگان است."

    elif score <= -10:

        state = "DISTRIBUTION"

        description = "احتمال خروج پول هوشمند و فاز توزیع."

    elif score <= -4:

        state = "BEARISH"

        description = "قدرت فروشندگان بیشتر است."

    else:

        state = "NEUTRAL"

        description = "سیگنال مشخصی از رفتار پول هوشمند دیده نمی‌شود."

    return {

        "score": score,

        "state": state,

        "description": description,

        "distance_from_ema20": round(distance, 2),

        "volatility_percent": round(volatility, 2),

        "reasons": reasons

    }