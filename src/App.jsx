import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function App() {
  const [prices, setPrices] = useState({});
  const [analysis, setAnalysis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);

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
    const interval = setInterval(fetchData, 60000); // هر ۱ دقیقه
    return () => clearInterval(interval);
  }, []);

  const getRecommendationColor = (rec) => {
    if (rec.includes('BUY')) return '#00c853';
    if (rec.includes('SELL')) return '#ff1744';
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
                <div className="price-value">{price.toLocaleString()}</div>
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
                    <strong>{item.current_price.toLocaleString()}</strong>
                  </div>
                  <div className="metric">
                    <span>روند</span>
                    <strong>{item.trend}</strong>
                  </div>
                  <div className="metric">
                    <span>RSI</span>
                    <strong>{item.rsi.toFixed(1)}</strong>
                  </div>
                  <div className="metric">
                    <span>امتیاز</span>
                    <strong>{item.final_score.toFixed(0)}/100</strong>
                  </div>
                </div>

                <div className="card-confidence">
                  <div className="confidence-bar">
                    <div 
                      className="confidence-fill"
                      style={{ width: `${item.confidence}%` }}
                    />
                  </div>
                  <span>اطمینان: {item.confidence}%</span>
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
        </>
      )}

      <footer className="footer">
        <p>📊 تحلیل‌گر حرفه‌ای بازار طلا و ارز ایران</p>
        <p>منبع داده: TGJU | نسخه ۱.۰.۰</p>
      </footer>
    </div>
  );
}

export default App;