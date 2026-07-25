import pandas as pd


def detect_divergence(df: pd.DataFrame):

    if len(df) < 30:

        return {
            "type": "NONE",
            "score": 0,
            "description": "داده کافی وجود ندارد."
        }

    price_now = float(df.iloc[-1]["gold"])
    price_prev = float(df.iloc[-6]["gold"])

    rsi_now = float(df.iloc[-1]["rsi"])
    rsi_prev = float(df.iloc[-6]["rsi"])

    macd_now = float(df.iloc[-1]["macd"])
    macd_prev = float(df.iloc[-6]["macd"])

    if price_now > price_prev and rsi_now < rsi_prev:

        return {

            "type": "BEARISH",

            "score": -15,

            "description":
            "واگرایی منفی RSI مشاهده شده و احتمال اصلاح قیمت وجود دارد."

        }

    if price_now < price_prev and rsi_now > rsi_prev:

        return {

            "type": "BULLISH",

            "score": 15,

            "description":
            "واگرایی مثبت RSI مشاهده شده و احتمال بازگشت روند وجود دارد."

        }

    if price_now > price_prev and macd_now < macd_prev:

        return {

            "type": "BEARISH_MACD",

            "score": -10,

            "description":
            "واگرایی منفی MACD مشاهده شده است."

        }

    if price_now < price_prev and macd_now > macd_prev:

        return {

            "type": "BULLISH_MACD",

            "score": 10,

            "description":
            "واگرایی مثبت MACD مشاهده شده است."

        }

    return {

        "type": "NONE",

        "score": 0,

        "description":
        "واگرایی معناداری مشاهده نشد."

    }