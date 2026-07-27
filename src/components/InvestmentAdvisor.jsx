import React, { useState } from 'react';
import axios from 'axios';
import './InvestmentAdvisor.css';

const API_URL = 'https://gold-analyzer-web.onrender.com';

function InvestmentAdvisor() {
  const [capital, setCapital] = useState(10000000); // ۱۰ میلیون تومان
  const [riskTolerance, setRiskTolerance] = useState('moderate');
  const [recommendations, setRecommendations] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchRecommendations = async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/portfolio`, {
        params: { capital, risk: riskTolerance }
      });
      setRecommendations(response.data);
    } catch (err) {
      setError('خطا در دریافت پیشنهادات. لطفاً دوباره تلاش کنید.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const formatPrice = (price) => {
    return price.toLocaleString('fa-IR');
  };

  return (
    <div className="investment-advisor">
      <h2>💼 مشاور سرمایه‌گذاری</h2>
      
      <div className="capital-input">
        <label>مبلغ سرمایه‌گذاری (تومان):</label>
        <input
          type="range"
          min="1000000"
          max="100000000"
          step="1000000"
          value={capital}
          onChange={(e) => setCapital(Number(e.target.value))}
        />
        <div className="capital-display">
          <span>{formatPrice(capital)} تومان</span>
        </div>
      </div>

      <div className="risk-selector">
        <label>سطح ریسک‌پذیری:</label>
        <div className="risk-buttons">
          <button 
            className={riskTolerance === 'conservative' ? 'active' : ''}
            onClick={() => setRiskTolerance('conservative')}
          >
            🟢 محافظه‌کارانه
          </button>
          <button 
            className={riskTolerance === 'moderate' ? 'active' : ''}
            onClick={() => setRiskTolerance('moderate')}
          >
            🟡 متعادل
          </button>
          <button 
            className={riskTolerance === 'aggressive' ? 'active' : ''}
            onClick={() => setRiskTolerance('aggressive')}
          >
            🔴 جسورانه
          </button>
        </div>
      </div>

      <button onClick={fetchRecommendations} className="analyze-btn">
        🔍 دریافت پیشنهادات
      </button>

      {loading && <div className="loading">⏳ در حال تحلیل...</div>}
      {error && <div className="error">{error}</div>}

      {recommendations && (
        <div className="recommendations">
          <h3>پیشنهادات سرمایه‌گذاری</h3>
          
          {recommendations.map((rec, index) => (
            <div key={index} className="recommendation-card">
              <div className="card-header">
                <span className="scenario-icon">{rec.color}</span>
                <h4>سناریوی {rec.scenario}</h4>
                <span className="sharpe-ratio">
                  نسبت شارپ: {rec.sharpe_ratio.toFixed(2)}
                </span>
              </div>
              
              <div className="allocations">
                {Object.entries(rec.allocations).map(([symbol, data]) => (
                  <div key={symbol} className="allocation-item">
                    <span className="symbol">{symbol.toUpperCase()}</span>
                    <div className="allocation-details">
                      <span>{formatPrice(data.amount_toman)} تومان</span>
                      <span>({data.weight_percent.toFixed(1)}%)</span>
                      <span className="quantity">
                        ≈ {data.quantity.toFixed(2)} واحد
                      </span>
                    </div>
                    <div className="progress-bar">
                      <div 
                        className="progress-fill"
                        style={{ width: `${data.weight_percent}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
              
              <div className="portfolio-metrics">
                <span>📈 بازده مورد انتظار: {rec.expected_return.toFixed(1)}%</span>
                <span>📉 ریسک: {rec.expected_risk.toFixed(1)}%</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default InvestmentAdvisor;