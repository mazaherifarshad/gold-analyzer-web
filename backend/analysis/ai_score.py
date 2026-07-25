from math import floor


def clamp(value, minimum, maximum):

    if value < minimum:
        return minimum

    if value > maximum:
        return maximum

    return value


def calculate_ai_score(

    trend,

    momentum,

    divergence,

    structure,

    bubble,

    iran_market,

    volume,

    smart_money,

    support_resistance,

    multi_timeframe,

    volatility,

    risk

):

    score = 50

    reasons = []

    # ------------------------
    # Trend
    # ------------------------

    score += trend["score"]

    reasons.append(

        f"Trend : {trend['score']}"

    )

    # ------------------------
    # Momentum
    # ------------------------

    score += momentum["score"]

    reasons.append(

        f"Momentum : {momentum['score']}"

    )

    # ------------------------
    # Divergence
    # ------------------------

    score += divergence["score"]

    reasons.append(

        f"Divergence : {divergence['score']}"

    )    
    # ------------------------
    # Market Structure
    # ------------------------

    score += structure["score"]

    reasons.append(

        f"Structure : {structure['score']}"

    )

    # ------------------------
    # Iran Market
    # ------------------------

    score += iran_market["score"]

    reasons.append(

        f"Iran Market : {iran_market['score']}"

    )

    # ------------------------
    # Bubble
    # ------------------------

    bubble_score = 0

    if bubble["percent"] < 2:

        bubble_score = 5

    elif bubble["percent"] < 5:

        bubble_score = 2

    elif bubble["percent"] < 10:

        bubble_score = -3

    else:

        bubble_score = -8

    score += bubble_score

    reasons.append(

        f"Bubble : {bubble_score}"

    )

    # ------------------------
    # Volume
    # ------------------------

    score += volume["score"]

    reasons.append(

        f"Volume : {volume['score']}"

    )    
    # ------------------------
    # Smart Money
    # ------------------------

    score += smart_money["score"]

    reasons.append(

        f"Smart Money : {smart_money['score']}"

    )

    # ------------------------
    # Support / Resistance
    # ------------------------

    score += support_resistance["score"]

    reasons.append(

        f"Support/Resistance : {support_resistance['score']}"

    )

    # ------------------------
    # Multi Timeframe
    # ------------------------

    score += multi_timeframe["score"]

    reasons.append(

        f"Multi Timeframe : {multi_timeframe['score']}"

    )

    # ------------------------
    # Volatility
    # ------------------------

    score += volatility["score"]

    reasons.append(

        f"Volatility : {volatility['score']}"

    )

    # ------------------------
    # Risk
    # ------------------------

    risk_penalty = floor(risk["score"] / 10)

    score -= risk_penalty

    reasons.append(

        f"Risk : -{risk_penalty}"

    )   
    # ------------------------
    # محدود کردن امتیاز
    # ------------------------

    score = clamp(score, 0, 100)

    if score >= 85:

        signal = "🟢 خرید بسیار قوی"

        strength = "VERY_STRONG_BUY"

    elif score >= 70:

        signal = "🟢 خرید"

        strength = "BUY"

    elif score >= 55:

        signal = "🟡 نگهداری"

        strength = "HOLD"

    elif score >= 40:

        signal = "🟠 فروش پله‌ای"

        strength = "LIGHT_SELL"

    else:

        signal = "🔴 فروش"

        strength = "SELL"   
    # ------------------------
    # سطح اطمینان تحلیل
    # ------------------------

    confidence = 50

    confidence += abs(trend["score"]) * 2

    confidence += abs(momentum["score"])

    confidence += abs(structure["score"])

    confidence += abs(multi_timeframe["score"])

    confidence -= risk_penalty * 2

    confidence = clamp(confidence, 0, 100)

    if confidence >= 85:

        confidence_text = "بسیار بالا"

    elif confidence >= 70:

        confidence_text = "بالا"

    elif confidence >= 55:

        confidence_text = "متوسط"

    else:

        confidence_text = "پایین"

    # ------------------------
    # وضعیت بازار
    # ------------------------

    if score >= 70 and risk["score"] <= 40:

        market_state = "روند صعودی سالم"

    elif score <= 35 and risk["score"] >= 70:

        market_state = "روند نزولی پرریسک"

    elif risk["score"] >= 70:

        market_state = "بازار پرریسک"

    else:

        market_state = "بازار متعادل"
        
        
    # ------------------------
    # خروجی نهایی
    # ------------------------

    return {

        "score": int(score),

        "signal": signal,

        "strength": strength,

        "confidence": int(confidence),

        "confidence_text": confidence_text,

        "market_state": market_state,

        "reasons": reasons,

        "modules": {

            "trend": trend["score"],

            "momentum": momentum["score"],

            "divergence": divergence["score"],

            "market_structure": structure["score"],

            "iran_market": iran_market["score"],

            "bubble": bubble_score,

            "volume": volume["score"],

            "smart_money": smart_money["score"],

            "support_resistance": support_resistance["score"],

            "multi_timeframe": multi_timeframe["score"],

            "volatility": volatility["score"],

            "risk_penalty": -risk_penalty

        }

    }