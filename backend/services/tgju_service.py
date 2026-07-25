import requests

URL = "https://call4.tgju.org/ajax.json"


def _to_float(value):

    if value is None:
        return 0.0

    value = str(value)

    value = value.replace(",", "")
    value = value.replace("٬", "")
    value = value.strip()

    try:
        return float(value)
    except:
        return 0.0


def get_market_prices():

    try:

        response = requests.get(
            URL,
            timeout=15,
            headers={
                "User-Agent": "Mozilla/5.0"
            }
        )

        response.raise_for_status()

        data = response.json()["current"]

        return {

            "gold": _to_float(
                data["geram18"]["p"]
            ),

            "usd": _to_float(
                data["price_dollar_rl"]["p"]
            ),

            "ounce": _to_float(
                data["ons"]["p"]
            ),

            # سکه بهار آزادی
            "coin": _to_float(
                data["sekee"]["p"]
            )

        }

    except Exception as e:

        print("TGJU ERROR:", e)

        return None