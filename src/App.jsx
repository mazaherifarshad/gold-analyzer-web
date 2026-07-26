import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'https://gold-analyzer-web.onrender.com';

function App() {
  const [prices, setPrices] = useState({});
  const [analysis, setAnalysis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [capital, setCapital] = useState(50000000);
  const [riskLevel, setRiskLevel] = useState('moderate');
  const [portfolio, setPortfolio] = useState(null);
  const [portfolioLoading, setPortfolioLoading] = useState(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [pricesRes, analysisRes] = await Promise.all([
        axios.get(`${API_URL}/prices`),
        axios.get(`${API_URL}/analysis`)
      ]);
      
      const priceMap = {};
      pricesRes.data.forEach(p => priceMap[p.symbol] = p.price);
      setPrices(priceMap);
      setAnalysis(analysisRes.data);
      setLastUpdate(new Date().toLocaleTimeString());
      setError(null);
    } catch (err) {
      setError('Unable to fetch data. Please try again.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchPortfolio = async () => {
    setPortfolioLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/portfolio`, {
        params: { capital, risk: riskLevel }
      });
      setPortfolio(response.data);
    } catch (err) {
      setError('Unable to fetch portfolio recommendations.');
      console.error(err);
    } finally {
      setPortfolioLoading(false);
    }
  };

  const updateData = async () => {
    try {
      await axios.post(`${API_URL}/update`);
      await fetchData();
    } catch (err) {
      setError('Update failed. Please try again.');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  const getRecommendationColor = (rec) => {
    if (rec?.includes('BUY')) return '#00c853';
    if (rec?.includes('SELL')) return '#ff1744';
    return '#ffd600';
  };

  const getSymbolName = (symbol) => {
    const names = {
      gold: 'طلا ۱۸ عیار',
      usd: 'دلار آمریکا',
      ounce: 'انس جهانی',
      coin: 'سکه بهار آزادی'
    };
    return names[symbol] || symbol;
  };

  const formatNumber = (num) => {
    return num.toLocaleString('fa-IR');
  };

  const getRiskLabel = (risk) => {
    const labels = {
      conservative: 'محافظه‌کارانه',
      moderate: 'متعادل',
      aggressive: 'جسورانه'
    };
    return labels[risk] || risk;
  };

  return (
    <div className="app">
      <header className="header">
        <h1>🏆 تحلیل‌گر بازار طلا</h1>
        <div className="header-info">
          <span>🕐 {lastUpdate || 'در حال بارگذاری...'}</span>
          <button onClick={updateData} className="update-btn">
            🔄 به‌روزرسانی
          </button>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">⏳ در حال بارگذاری...</div>
      ) : (
        <>
          {/* قیمت‌های لحظه‌ای */}
          <div className="prices-grid">
            {Object.entries(prices).map(([symbol, price]) => (
              <div key={symbol} className="price-card">
                <div className="price-symbol">{getSymbolName(symbol)}</div>
                <div className="price-value">{formatNumber(price)}</div>
              </div>
            ))}
          </div>

          {/* تحلیل‌ها */}
          <div className="analysis-grid">
            {analysis.map((item) => (
              <div key={item.symbol} className="analysis-card">
                <div className="card-header">
                  <h3>{getSymbolName(item.symbol)}</h3>
                  <span 
                    className="recommendation"
                    style={{ backgroundColor: getRecommendationColor(item.recommendation) }}
                  >
                    {item.recommendation}
                  </span>
                </div>
                
                <div className="card-metrics">
                  <div className="metric">
                    <span>قیمت</span>
                    <strong>{formatNumber(item.current_price)}</strong>
                  </div>
                  <div className="metric">
                    <span>روند</span>
                    <strong>{item.trend}</strong>
                  </div>
                  <div className="metric">
                    <span>RSI</span>
                    <strong>{item.rsi?.toFixed(1)}</strong>
                  </div>
                  <div className="metric">
                    <span>امتیاز</span>
                    <strong>{item.final_score?.toFixed(0)}/100</strong>
                  </div>
                </div>

                <div className="card-confidence">
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${item.confidence || 0}%` }}
                    />
                  </div>
                  <span>اطمینان: {item.confidence || 0}%</span>
                </div>

                {item.reasons && item.reasons.length > 0 && (
                  <div className="card-reasons">
                    {item.reasons.map((reason, idx) => (
                      <div key={idx} className="reason">• {reason}</div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* بخش سرمایه‌گذاری */}
          <div className="portfolio-section">
            <h2>💼 مشاور سرمایه‌گذاری</h2>
            <div className="portfolio-controls">
              <div className="capital-input">
                <label>مبلغ سرمایه (تومان):</label>
                <input
                  type="range"
                  min="1000000"
                  max="100000000"
                  step="1000000"
                  value={capital}
                  onChange={(e) => setCapital(Number(e.target.value))}
                />
                <span className="capital-display">{formatNumber(capital)} تومان</span>
              </div>
              <div className="risk-selector">
                <label>سطح ریسک:</label>
                <select value={riskLevel} onChange={(e) => setRiskLevel(e.target.value)}>
                  <option value="conservative">🟢 محافظه‌کارانه</option>
                  <option value="moderate">🟡 متعادل</option>
                  <option value="aggressive">🔴 جسورانه</option>
                </select>
              </div>
              <button onClick={fetchPortfolio} className="portfolio-btn" disabled={portfolioLoading}>
                {portfolioLoading ? '⏳ در حال تحلیل...' : '🔍 دریافت پیشنهادات'}
              </button>
            </div>

            {portfolio && portfolio.status === 'success' && (
              <div className="portfolio-results">
                <div className="portfolio-summary">
                  <span>💰 سرمایه: {formatNumber(portfolio.capital)} تومان</span>
                  <span>📊 سطح ریسک: {getRiskLabel(portfolio.risk_level)}</span>
                  <span>📅 {new Date(portfolio.timestamp).toLocaleString('fa-IR')}</span>
                </div>
                {portfolio.recommendations.map((rec, idx) => (
                  <div key={idx} className="portfolio-card">
                    <div className="portfolio-card-header">
                      <span className="scenario-icon">{rec.color}</span>
                      <h4>سناریوی {rec.scenario}</h4>
                      <span className="sharpe-ratio">نسبت شارپ: {rec.sharpe_ratio.toFixed(2)}</span>
                    </div>
                    <div className="portfolio-allocations">
                      {Object.entries(rec.allocations).map(([symbol, data]) => (
                        <div key={symbol} className="allocation-item">
                          <span className="allocation-symbol">{getSymbolName(symbol)}</span>
                          <span className="allocation-amount">{formatNumber(data.amount_toman)} تومان</span>
                          <span className="allocation-percent">({data.weight_percent.toFixed(1)}%)</span>
                          <span className="allocation-quantity">≈ {data.quantity.toFixed(2)} واحد</span>
                          <div className="allocation-bar">
                            <div className="allocation-fill" style={{ width: `${data.weight_percent}%` }} />
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
        </>
      )}

      <footer className="footer">
        <p>📊 تحلیل‌گر حرفه‌ای بازار طلا و ارز ایران</p>
        <p>منبع داده: TGJU | نسخه V1.0 | توسعه‌دهنده: F.Mazaheri</p>
        <p style={{fontSize: '12px', color: '#666', marginTop: '4px'}}>© 2026 Gold Market Analyzer. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;