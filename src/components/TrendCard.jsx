export default function TrendCard({ trend }) {

    return (

        <div className="trend-card">

            <h3>Trend</h3>

            <h2>{trend.trend}</h2>

            <hr />

            <p>EMA20 : {trend.ema20.toLocaleString()}</p>

            <p>EMA50 : {trend.ema50.toLocaleString()}</p>

            <p>RSI : {trend.rsi.toFixed(2)}</p>

            <p>MACD : {trend.macd.toFixed(2)}</p>

        </div>

    );

}