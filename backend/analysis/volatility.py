import pandas as pd


def analyze_volatility(df: pd.DataFrame):

    if len(df) < 30:

        return {

            "score": 0,

            "state": "NO_DATA",

            "description": "داده کافی وجود ندارد."

        }

    last = df.iloc[-1]

    atr = float(last["atr"])

    price = float(last["gold"])

    atr_percent = (atr / price) * 100

    std20 = float(df["gold"].tail(20).std())

    std_percent = (std20 / price) * 100

    score = 0

    reasons = []

    if atr_percent < 0.30:

        score += 5

        reasons.append("نوسان بسیار پایین")

    elif atr_percent < 0.60:

        score += 2

        reasons.append("نوسان مناسب")

    elif atr_percent < 1.20:

        score -= 2

        reasons.append("نوسان نسبتاً بالا")

    else:

        score -= 6

        reasons.append("نوسان شدید")

    if std_percent > 1.5:

        score -= 4

        reasons.append("انحراف معیار بالا")

    elif std_percent < 0.5:

        score += 2

        reasons.append("ثبات قیمت")

    if score >= 5:

        state = "LOW"

        description = "بازار آرام و با ثبات است."

    elif score <= -5:

        state = "HIGH"

        description = "بازار پرنوسان است و مدیریت ریسک اهمیت بالایی دارد."

    else:

        state = "NORMAL"

        description = "نوسان بازار در محدوده طبیعی قرار دارد."

    return {

        "score": score,

        "state": state,

        "description": description,

        "atr_percent": round(atr_percent, 2),

        "std_percent": round(std_percent, 2),

        "reasons": reasons

    }