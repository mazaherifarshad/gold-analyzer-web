import pandas as pd


def detect_momentum(df: pd.DataFrame):

    last = df.iloc[-1]

    score = 0

    reasons = []

    rsi = float(last["rsi"])

    macd = float(last["macd"])

    macd_signal = float(last["macd_signal"])

    if rsi >= 70:

        score -= 2
        reasons.append("اشباع خرید")

    elif rsi >= 60:

        score += 1
        reasons.append("قدرت خریداران")

    elif rsi <= 30:

        score += 2
        reasons.append("اشباع فروش")

    elif rsi <= 40:

        score -= 1
        reasons.append("قدرت فروشندگان")

    if macd > macd_signal:

        score += 2
        reasons.append("MACD صعودی")

    else:

        score -= 2
        reasons.append("MACD نزولی")

    if score >= 3:

        state = "قدرت صعودی"

    elif score <= -3:

        state = "قدرت نزولی"

    else:

        state = "قدرت متعادل"

    return {

        "score": score,

        "state": state,

        "rsi": round(rsi,2),

        "macd": round(macd,2),

        "macd_signal": round(macd_signal,2),

        "reasons": reasons

    }