export default function BubbleCard({ percent }) {

    return (

        <div className="bubble-card">

            <div className="bubble-title">
                Bubble
            </div>

            <div className="bubble-value">
                {percent.toFixed(2)}%
            </div>

        </div>

    );

}