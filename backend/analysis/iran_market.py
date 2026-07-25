import math


def analyze_iran_market(

    gold,
    usd,
    ounce,
    coin

):

    # وزن طلای خالص سکه بهار آزادی (گرم)
    PURE_GOLD_WEIGHT = 7.322381

    # اونس به گرم
    OUNCE_TO_GRAM = 31.103431

    # ارزش ذاتی سکه
    intrinsic = (
        ounce *
        usd *
        PURE_GOLD_WEIGHT /
        OUNCE_TO_GRAM
    )

    bubble = coin - intrinsic

    bubble_percent = (
        bubble /
        intrinsic
    ) * 100

    score = 0

    reasons = []

    if bubble_percent < 2:

        score += 15

        reasons.append(
            "حباب بسیار پایین"
        )

    elif bubble_percent < 5:

        score += 8

        reasons.append(
            "حباب طبیعی"
        )

    elif bubble_percent < 8:

        score -= 5

        reasons.append(
            "حباب نسبتاً بالا"
        )

    else:

        score -= 15

        reasons.append(
            "حباب بسیار بالا"
        )

    # نسبت دلار به طلا

    dollar_gold_ratio = gold / usd

    if dollar_gold_ratio > 95:

        score += 3

    elif dollar_gold_ratio < 90:

        score -= 3

    # ارزش واقعی طلای موجود در سکه

    gold_value = (
        gold *
        8.133
    )

    premium = coin - gold_value

    premium_percent = (
        premium /
        gold_value
    ) * 100

    if premium_percent < 5:

        score += 5

        reasons.append(
            "پریمیوم پایین"
        )

    elif premium_percent > 15:

        score -= 8

        reasons.append(
            "پریمیوم بالا"
        )

    if score > 20:
        score = 20

    if score < -20:
        score = -20

    if score >= 10:

        state = "بسیار مثبت"

    elif score >= 3:

        state = "مثبت"

    elif score <= -10:

        state = "بسیار منفی"

    elif score <= -3:

        state = "منفی"

    else:

        state = "متعادل"

    return {

        "score": score,

        "state": state,

        "intrinsic_coin": round(intrinsic),

        "coin_bubble": round(bubble),

        "bubble_percent": round(
            bubble_percent,
            2
        ),

        "gold_value": round(
            gold_value
        ),

        "premium": round(
            premium
        ),

        "premium_percent": round(
            premium_percent,
            2
        ),

        "dollar_gold_ratio": round(
            dollar_gold_ratio,
            2
        ),

        "reasons": reasons

    }