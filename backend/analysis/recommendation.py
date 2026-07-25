def generate_recommendation(ai):

    score = ai["score"]

    confidence = ai["confidence"]

    market_state = ai["market_state"]

    signal = ai["signal"]

    if score >= 85:

        title = "خرید بسیار قوی"

        action = (
            "شرایط اکثر شاخص‌های تکنیکال همسو هستند. "
            "در صورت رعایت مدیریت سرمایه، بازار در یکی از بهترین "
            "موقعیت‌های خرید قرار دارد."
        )

    elif score >= 70:

        title = "خرید"

        action = (
            "اکثر اندیکاتورها روند صعودی را تأیید می‌کنند. "
            "ورود پله‌ای پیشنهاد می‌شود."
        )

    elif score >= 55:

        title = "نگهداری"

        action = (
            "بازار هنوز سیگنال قطعی خرید یا فروش صادر نکرده است. "
            "بهتر است موقعیت فعلی حفظ شود."
        )

    elif score >= 40:

        title = "فروش پله‌ای"

        action = (
            "قدرت بازار در حال کاهش است. "
            "خروج تدریجی از موقعیت می‌تواند ریسک را کاهش دهد."
        )

    else:

        title = "فروش"

        action = (
            "اکثر شاخص‌ها احتمال ادامه افت قیمت را نشان می‌دهند. "
            "حفظ سرمایه نسبت به کسب سود اولویت دارد."
        )    
    # -------------------------
    # توضیح وضعیت بازار
    # -------------------------

    if market_state == "روند صعودی سالم":

        market_text = (
            "روند غالب بازار صعودی است و ریسک عمومی در سطح قابل قبول قرار دارد."
        )

    elif market_state == "روند نزولی پرریسک":

        market_text = (
            "بازار در روند نزولی قرار دارد و احتمال افزایش فشار فروش وجود دارد."
        )

    elif market_state == "بازار پرریسک":

        market_text = (
            "نوسانات و ریسک بازار بالاست؛ ورود با حجم بالا توصیه نمی‌شود."
        )

    else:

        market_text = (
            "بازار در وضعیت متعادل قرار دارد و نیاز به تأیید بیشتر دارد."
        )

    # -------------------------
    # توضیح میزان اطمینان
    # -------------------------

    if confidence >= 85:

        confidence_text = (
            "میزان اطمینان تحلیل بسیار بالا است."
        )

    elif confidence >= 70:

        confidence_text = (
            "میزان اطمینان تحلیل بالا است."
        )

    elif confidence >= 55:

        confidence_text = (
            "میزان اطمینان تحلیل متوسط است."
        )

    else:

        confidence_text = (
            "اطمینان تحلیل پایین است و بهتر است منتظر داده‌های بیشتر بمانید."
        )
            
    # -------------------------
    # نکات پیشنهادی
    # -------------------------

    suggestions = []

    if score >= 70:

        suggestions.append(
            "ورود سرمایه را به صورت پله‌ای انجام دهید."
        )

        suggestions.append(
            "حد ضرر را فراموش نکنید."
        )

    elif score >= 55:

        suggestions.append(
            "فعلاً موقعیت خود را حفظ کنید."
        )

        suggestions.append(
            "منتظر شکست مقاومت یا حمایت باشید."
        )

    elif score >= 40:

        suggestions.append(
            "در صورت سودده بودن، بخشی از موقعیت را نقد کنید."
        )

        suggestions.append(
            "از ورود سرمایه جدید خودداری کنید."
        )

    else:

        suggestions.append(
            "ریسک بازار بالا است."
        )

        suggestions.append(
            "تا صدور سیگنال جدید از خرید خودداری کنید."
        )

    summary = (

        f"{title} | "

        f"{market_state} | "

        f"امتیاز تحلیل: {score} از 100"

    )    
    return {

        "title": title,

        "signal": signal,

        "score": score,

        "action": action,

        "market_text": market_text,

        "confidence": confidence,

        "confidence_text": confidence_text,

        "summary": summary,

        "suggestions": suggestions

    }