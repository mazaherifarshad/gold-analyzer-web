import pandas as pd


def analyze_market_structure(df: pd.DataFrame):

    if len(df) < 60:

        return {
            "trend": "نامشخص",
            "score": 0,
            "description": "داده کافی وجود ندارد."
        }

    high20 = df["gold"].tail(20).max()
    low20 = df["gold"].tail(20).min()

    last = float(df.iloc[-1]["gold"])

    distance_high = ((high20 - last) / high20) * 100
    distance_low = ((last - low20) / low20) * 100

    if distance_high < 1:

        return {

            "trend": "شکست مقاومت",

            "score": 12,

            "description":
            "قیمت در نزدیکی سقف ۲۰ دوره اخیر قرار دارد."

        }

    if distance_low < 1:

        return {

            "trend": "شکست حمایت",

            "score": -12,

            "description":
            "قیمت در نزدیکی کف ۲۰ دوره اخیر قرار دارد."

        }

    return {

        "trend": "رنج",

        "score": 0,

        "description":
        "بازار داخل محدوده نوسان می‌کند."

    }