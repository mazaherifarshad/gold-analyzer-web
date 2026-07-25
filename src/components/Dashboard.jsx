import useApi from "../hooks/useApi";

import Loading from "./Loading";
import Error from "./Error";

import PriceCard from "./PriceCard";
import SignalCard from "./SignalCard";
import RiskCard from "./RiskCard";
import BubbleCard from "./BubbleCard";
import TrendCard from "./TrendCard";
import MarketScoreCard from "./MarketScoreCard";
import UpdateCard from "./UpdateCard";

export default function Dashboard() {

    const { data, loading, error } = useApi("/analysis", 10000);

    if (loading) return <Loading />;

    if (error) return <Error message={error} />;

    if (data.status !== "ready")
        return <Error message={data.message} />;

    return (

        <div className="dashboard">

            <div className="cards">

                <SignalCard
                    signal={data.recommendation}
                />

                <MarketScoreCard
                    score={data.market_score}
                />

                <RiskCard
                    score={data.risk.score}
                />

                <BubbleCard
                    percent={data.bubble.percent}
                />

                <TrendCard
                    trend={data.trend}
                />

                <UpdateCard
                    time={data.last_update}
                />

            </div>

            <div className="prices">

                <PriceCard
                    title="Gold"
                    value={data.market.gold}
                />

                <PriceCard
                    title="Dollar"
                    value={data.market.usd}
                />

                <PriceCard
                    title="Ounce"
                    value={data.market.ounce}
                />

                <PriceCard
                    title="Coin"
                    value={data.market.coin}
                />

            </div>

        </div>

    );

}