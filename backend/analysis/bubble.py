PURE_GOLD_WEIGHT = 7.322381

OUNCE_TO_GRAM = 31.103431


def calculate_bubble(gold, coin, usd, ounce):

    intrinsic = (

        ounce *

        usd *

        PURE_GOLD_WEIGHT /

        OUNCE_TO_GRAM

    )

    difference = coin - intrinsic

    percent = (difference / intrinsic) * 100

    return {

        "intrinsic": round(intrinsic),

        "market": round(coin),

        "difference": round(difference),

        "percent": round(percent, 2)

    }