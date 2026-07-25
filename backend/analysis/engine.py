import pandas as pd
import jdatetime
from zoneinfo import ZoneInfo

from database.database import (
    SessionLocal,
    MarketHistory
)

from analysis.indicators import (
    calculate_indicators
)

from analysis.trend import (
    detect_trend
)

from analysis.momentum import (
    detect_momentum
)

from analysis.divergence import (
    detect_divergence
)

from analysis.market_structure import (
    analyze_market_structure
)

from analysis.bubble import (
    calculate_bubble
)

from analysis.iran_market import (
    analyze_iran_market
)

from analysis.volume import (
    analyze_volume
)

from analysis.smart_money import (
    analyze_smart_money
)

from analysis.support_resistance import (
    analyze_support_resistance
)

from analysis.multi_timeframe import (
    analyze_multi_timeframe
)

from analysis.volatility import (
    analyze_volatility
)

from analysis.risk import (
    calculate_risk
)

from analysis.ai_score import (
    calculate_ai_score
)

from analysis.recommendation import (
    generate_recommendation
)



def run_analysis():

    db = SessionLocal()

    try:

        rows = (
            db.query(
                MarketHistory
            )
            .order_by(
                MarketHistory.id
            )
            .all()
        )

        if len(rows) < 60:

            return {

                "status": "waiting",

                "message":
                "داده کافی برای تحلیل وجود ندارد."

            }

        df = pd.DataFrame([

            {

                "gold": r.gold,

                "usd": r.usd,

                "ounce": r.ounce,

                "coin": r.coin,

                "time": r.created_at

            }

            for r in rows

        ])

        df = calculate_indicators(df)

        if df is None:

            return {

                "status": "waiting",

                "message":
                "اندیکاتورها قابل محاسبه نیستند."

            }        
        # -----------------------------
        # Trend Analysis
        # -----------------------------

        trend = detect_trend(df)

        momentum = detect_momentum(df)

        divergence = detect_divergence(df)

        structure = analyze_market_structure(df)

        volume = analyze_volume(df)

        smart_money = analyze_smart_money(df)

        support_resistance = analyze_support_resistance(df)

        multi_timeframe = analyze_multi_timeframe(df)

        volatility = analyze_volatility(df)

        # -----------------------------
        # آخرین داده بازار
        # -----------------------------

        last = df.iloc[-1]

        bubble = calculate_bubble(

            last["gold"],

            last["coin"],

            last["usd"],

            last["ounce"]

        )

        iran_market = analyze_iran_market(

            last["gold"],

            last["usd"],

            last["ounce"],

            last["coin"]

        )

        risk = calculate_risk(

            trend,

            bubble

        )        
        ai = calculate_ai_score(

            trend=trend,

            momentum=momentum,

            bubble=bubble,

            risk=risk,

            divergence=divergence,

            structure=structure,

            volume=volume,

            smart_money=smart_money,

            support_resistance=support_resistance,

            multi_timeframe=multi_timeframe,

            volatility=volatility,

            iran_market=iran_market

        )

        recommendation = generate_recommendation(
            ai
        )

        # -----------------------------
        # تبدیل تاریخ به شمسی
        # -----------------------------

        iran_time = (

            last["time"]

            .replace(
                tzinfo=ZoneInfo("UTC")
            )

            .astimezone(
                ZoneInfo("Asia/Tehran")
            )

        )

        shamsi = jdatetime.datetime.fromgregorian(

            datetime=iran_time

        )

        last_update = shamsi.strftime(

            "%Y/%m/%d %H:%M:%S"

        )        
        result = {

            "status": "ready",

            "market": {

                "gold": float(last["gold"]),

                "usd": float(last["usd"]),

                "ounce": float(last["ounce"]),

                "coin": float(last["coin"])

            },

            "market_score": ai["score"],

            "signal": ai["signal"],

            "trend": trend,

            "momentum": momentum,

            "divergence": divergence,

            "market_structure": structure,

            "bubble": bubble,

            "iran_market": iran_market,

            "volume": volume,

            "smart_money": smart_money,

            "support_resistance": support_resistance,

            "multi_timeframe": multi_timeframe,

            "volatility": volatility,

            "risk": risk,

            "ai": ai,

            "recommendation": recommendation,

            "last_update": last_update
        }        
        result["dashboard"] = {

            "buy_score": ai["score"],

            "risk_score": risk["score"],

            "trend_state": trend["trend"],

            "smart_money_state": smart_money["state"],

            "market_state": structure["trend"],

            "bubble_percent": iran_market["bubble_percent"],

            "iran_state": iran_market["state"],

            "volatility_state": volatility["state"],

            "multi_timeframe": multi_timeframe["state"],

            "recommendation": recommendation["signal"]

        }

        result["details"] = {

            "trend": trend,

            "momentum": momentum,

            "divergence": divergence,

            "bubble": bubble,

            "iran_market": iran_market,

            "smart_money": smart_money,

            "support_resistance": support_resistance,

            "multi_timeframe": multi_timeframe,

            "volatility": volatility,

            "risk": risk

        }      
        # -----------------------------
        # خلاصه هوش مصنوعی
        # -----------------------------

        result["analysis"] = {

            "score": ai["score"],

            "signal": ai["signal"],

            "strength": ai["strength"],

            "confidence": ai["confidence"],

            "confidence_text": ai["confidence_text"],

            "market_state": ai["market_state"],

            "reasons": ai["reasons"],

            "modules": ai["modules"]

        }

        result["recommendation"] = recommendation

        # -----------------------------
        # وضعیت کلی بازار
        # -----------------------------

        result["market_overview"] = {

            "trend": trend["trend"],

            "momentum": momentum["state"],

            "smart_money": smart_money["state"],

            "bubble_percent": iran_market["bubble_percent"],

            "risk": risk["score"],

            "last_price": float(last["gold"])

        }  
                
        # -----------------------------
        # خلاصه بازار برای رابط کاربری
        # -----------------------------

        result["summary"] = {

            "gold": float(last["gold"]),

            "usd": float(last["usd"]),

            "ounce": float(last["ounce"]),

            "coin": float(last["coin"]),

            "signal": recommendation["signal"],

            "title": recommendation["title"],

            "action": recommendation["action"],

            "summary": recommendation["summary"],

            "confidence": ai["confidence"],

            "market_state": ai["market_state"],

            "last_update": last_update

        }

        # -----------------------------
        # پیشنهادها
        # -----------------------------

        result["tips"] = recommendation["suggestions"]

        # -----------------------------
        # وضعیت سیستم
        # -----------------------------

        result["system"] = {

            "records": len(df),

            "analysis_version": "2.0",

            "status": "ONLINE"

        }

        return result
        
    except Exception as e:

        return {

            "status": "error",

            "message": str(e)

        }

    finally:

        db.close()