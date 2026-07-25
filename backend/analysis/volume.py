import pandas as pd


def analyze_volume(df: pd.DataFrame):

    if "volume" not in df.columns:

        return {

            "score": 0,

            "state": "NO_DATA",

            "description": "اطلاعات حجم معاملات موجود نیست.",

            "ratio": 0

        }

    if len(df) < 20:

        return {

            "score": 0,

            "state": "NO_DATA",

            "description": "داده کافی وجود ندارد.",

            "ratio": 0

        }

    last_volume = float(df.iloc[-1]["volume"])

    avg_volume = float(

        df["volume"].tail(20).mean()

    )

    ratio = last_volume / avg_volume

    if ratio >= 2:

        score = 10

        state = "VERY_HIGH"

        description = "حجم معاملات بسیار بالاتر از میانگین است."

    elif ratio >= 1.3:

        score = 5

        state = "HIGH"

        description = "حجم معاملات بالاتر از میانگین است."

    elif ratio >= 0.8:

        score = 0

        state = "NORMAL"

        description = "حجم معاملات در محدوده طبیعی است."

    else:

        score = -5

        state = "LOW"

        description = "حجم معاملات کمتر از میانگین است."

    return {

        "score": score,

        "state": state,

        "description": description,

        "ratio": round(ratio, 2),

        "last_volume": round(last_volume),

        "average_volume": round(avg_volume)

    }