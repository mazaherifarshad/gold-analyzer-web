import pandas as pd
import ta


def calculate_indicators(df):

    if len(df) < 50:
        return None

    close = pd.to_numeric(df["gold"], errors="coerce")

    df["ema20"] = ta.trend.ema_indicator(close, window=20)

    df["ema50"] = ta.trend.ema_indicator(close, window=50)

    df["rsi"] = ta.momentum.rsi(close, window=14)

    macd = ta.trend.MACD(close)

    df["macd"] = macd.macd()

    df["macd_signal"] = macd.macd_signal()

    df["atr"] = ta.volatility.average_true_range(
        high=close,
        low=close,
        close=close,
        window=14
    )

    df.fillna(0, inplace=True)

    return df