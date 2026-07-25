def calculate_risk(trend, bubble):

    score = 50

    if trend["trend"] == "STRONG_BULL":
        score -= 20

    elif trend["trend"] == "BULL":
        score -= 10

    elif trend["trend"] == "STRONG_BEAR":
        score += 20

    elif trend["trend"] == "BEAR":
        score += 10

    if abs(bubble["percent"]) > 10:
        score += 20

    elif abs(bubble["percent"]) > 5:
        score += 10

    score = max(0, min(score, 100))

    return {
        "score": score
    }