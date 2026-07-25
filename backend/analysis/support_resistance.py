import pandas as pd


def analyze_support_resistance(df: pd.DataFrame):

    if len(df) < 60:

        return {

            "score": 0,

            "state": "NO_DATA",

            "description": "داده کافی وجود ندارد."

        }

    last_price = float(df.iloc[-1]["gold"])

    support = float(df["gold"].tail(30).min())

    resistance = float(df["gold"].tail(30).max())

    distance_support = (
        (last_price - support)
        / support
    ) * 100

    distance_resistance = (
        (resistance - last_price)
        / resistance
    ) * 100

    score = 0

    reasons = []

    if distance_support <= 1:

        score += 10

        reasons.append(
            "قیمت نزدیک حمایت است."
        )

    elif distance_support <= 3:

        score += 4

        reasons.append(
            "قیمت بالای حمایت قرار دارد."
        )

    if distance_resistance <= 1:

        score -= 10

        reasons.append(
            "قیمت نزدیک مقاومت است."
        )

    elif distance_resistance <= 3:

        score -= 4

        reasons.append(
            "قیمت نزدیک مقاومت قرار گرفته است."
        )

    if score >= 8:

        state = "BUY_ZONE"

        description = "بازار در محدوده مناسب خرید قرار دارد."

    elif score <= -8:

        state = "SELL_ZONE"

        description = "بازار در محدوده مناسب فروش قرار دارد."

    else:

        state = "RANGE"

        description = "بازار بین حمایت و مقاومت در حال نوسان است."

    return {

        "score": score,

        "state": state,

        "description": description,

        "support": round(support),

        "resistance": round(resistance),

        "distance_support": round(distance_support,2),

        "distance_resistance": round(distance_resistance,2),

        "reasons": reasons

    }