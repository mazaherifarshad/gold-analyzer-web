export default function MarketScoreCard({ score }) {

    return (

        <div className="market-score-card">

            <div className="market-score-title">
                Market Score
            </div>

            <div className="market-score-value">
                {score}
            </div>

        </div>

    );

}