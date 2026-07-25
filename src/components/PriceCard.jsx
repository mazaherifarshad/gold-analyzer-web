export default function PriceCard({ title, value }) {

    return (

        <div className="price-card">

            <div className="price-title">
                {title}
            </div>

            <div className="price-value">
                {Number(value).toLocaleString()}
            </div>

        </div>

    );

}