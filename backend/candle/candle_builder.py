def build_all_missing_candles(ticks, timeframe):

    if not ticks:
        return []

    minutes = TIMEFRAMES[timeframe]

    groups = {}

    for tick in ticks:

        start = floor_time(
            tick.created_at,
            minutes
        )

        groups.setdefault(
            start,
            []
        ).append(tick)

    candles = []

    for start in sorted(groups):

        prices = [
            float(x.gold)
            for x in groups[start]
        ]

        candles.append({

            "symbol": "gold",

            "timeframe": timeframe,

            "candle_time": start,

            "open": prices[0],

            "high": max(prices),

            "low": min(prices),

            "close": prices[-1],

            "volume": len(prices)

        })

    return candles