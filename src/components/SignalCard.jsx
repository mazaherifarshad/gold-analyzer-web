export default function SignalCard({ signal }) {

    const description =
        signal.description ??
        "در حال تحلیل بازار...";

    return (

        <div className="signal-card">

            <h3>AI Recommendation</h3>

            <h1>{signal.signal}</h1>

            <p
                style={{
                    marginTop: 15,
                    lineHeight: 1.8,
                    textAlign: "right"
                }}
            >
                {description}
            </p>

        </div>

    );

}