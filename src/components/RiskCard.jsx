export default function RiskCard({ score }) {

    return (

        <div className="risk-card">

            <div className="risk-title">
                Risk
            </div>

            <div className="risk-value">
                {score}%
            </div>

        </div>

    );

}