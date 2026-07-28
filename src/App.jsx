import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'https://gold-analyzer-web.onrender.com';

function App() {
  const [prices, setPrices] = useState({});
  const [analysis, setAnalysis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const [showInfo, setShowInfo] = useState(null);

  // سرمایه‌گذاری با کیبورد مجازی
  const [capital, setCapital] = useState(0);
  const [capitalDisplay, setCapitalDisplay] = useState('');
  const [userPreference, setUserPreference] = useState('gold');
  const [portfolio, setPortfolio] = useState(null);
  const [portfolioLoading, setPortfolioLoading] = useState(false);
  const [showPortfolio, setShowPortfolio] = useState(false);

  // ماشین حساب (محاسبه خودکار)
  const [goldCalc, setGoldCalc] = useState({
    weight: 1,
    sellerPrice: 0,
    karat: 750,
    commission: 0,
    officialPrice: 0,
    finalSellerPrice: 0,
    finalOfficialPrice: 0,
    difference: 0,
    isCheaper: false
  });
  const [showGoldCalc, setShowGoldCalc] = useState(false);

  const [buyMeterGold, setBuyMeterGold] = useState(50);
  const [buyMeterUsd, setBuyMeterUsd] = useState(50);
  const [news, setNews] = useState([]);
  const updateInterval = useRef(null);

  // دریافت داده
  const fetchData = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      const [pricesRes, analysisRes] = await Promise.all([
        axios.get(`${API_URL}/prices`),
        axios.get(`${API_URL}/analysis`)
      ]);
      
      const priceMap = {};
      pricesRes.data.forEach(p => { priceMap[p.symbol] = p.price; });
      setPrices(priceMap);
      setAnalysis(analysisRes.data);
      
      const gold = analysisRes.data.find(a => a.symbol === 'gold');
      const usd = analysisRes.data.find(a => a.symbol === 'usd');
      if (gold) setBuyMeterGold(Math.min(100, Math.max(0, gold.final_score || 50)));
      if (usd) setBuyMeterUsd(Math.min(100, Math.max(0, usd.final_score || 50)));
      
      setNews(generateNews(analysisRes.data));
      setLastUpdate(new Date().toLocaleString('fa-IR'));
      setError(null);
    } catch (err) {
      setError('خطا در دریافت داده');
      console.error(err);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  const generateNews = (analysisData) => {
    const items = [];
    const gold = analysisData.find(a => a.symbol === 'gold');
    const usd = analysisData.find(a => a.symbol === 'usd');
    const coin = analysisData.find(a => a.symbol === 'coin');
    if (gold) {
      const rsi = gold.rsi || 50;
      items.push({ symbol: 'gold', text: rsi > 70 ? 'طلا در منطقه اشباع خرید' : rsi < 30 ? 'طلا در منطقه اشباع فروش' : 'طلا در وضعیت متعادل' });
    }
    if (usd) {
      const rsi = usd.rsi || 50;
      items.push({ symbol: 'usd', text: rsi > 70 ? 'دلار در منطقه اشباع خرید' : rsi < 30 ? 'دلار در منطقه اشباع فروش' : 'دلار در وضعیت متعادل' });
    }
    if (coin) {
      const rsi = coin.rsi || 50;
      items.push({ symbol: 'coin', text: rsi > 70 ? 'سکه در منطقه اشباع خرید' : rsi < 30 ? 'سکه در منطقه اشباع فروش' : 'سکه در وضعیت متعادل' });
    }
    return items;
  };

  const fetchPortfolio = async () => {
    if (capital === 0) { setError('لطفاً مبلغ سرمایه را وارد کنید.'); return; }
    setPortfolioLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/portfolio`, { params: { capital } });
      setPortfolio(response.data);
      setShowPortfolio(true);
    } catch (err) {
      setError('خطا در دریافت پیشنهادات');
    } finally {
      setPortfolioLoading(false);
    }
  };

  const updateData = async () => {
    try {
      await axios.post(`${API_URL}/update`);
      await fetchData(true);
    } catch (err) {
      setError('به‌روزرسانی ناموفق بود.');
    }
  };

  useEffect(() => {
    fetchData(true);
    updateInterval.current = setInterval(() => fetchData(false), 60000);
    return () => clearInterval(updateInterval.current);
  }, []);

  // ماشین حساب خودکار
  useEffect(() => {
    if (prices.gold) calculateGold();
  }, [prices.gold, goldCalc.weight, goldCalc.karat, goldCalc.sellerPrice, goldCalc.commission]);

  const calculateGold = () => {
    const basePrice = prices.gold || 0;
    const sellerPrice = goldCalc.sellerPrice > 0 ? goldCalc.sellerPrice : basePrice;
    const finalSeller = sellerPrice + (sellerPrice * goldCalc.commission / 100);
    const finalOfficial = basePrice + (basePrice * goldCalc.commission / 100);
    setGoldCalc(prev => ({
      ...prev,
      officialPrice: basePrice,
      finalSellerPrice: finalSeller,
      finalOfficialPrice: finalOfficial,
      difference: finalSeller - finalOfficial,
      isCheaper: finalSeller < finalOfficial
    }));
  };

  // کیبورد مجازی
  const handleNumberClick = (num) => {
    if (num === '000') {
      setCapital(prev => prev * 1000);
      setCapitalDisplay(prev => prev + '000');
    } else if (num === '⌫') {
      const newDisplay = capitalDisplay.slice(0, -1);
      setCapitalDisplay(newDisplay);
      setCapital(Number(newDisplay.replace(/,/g, '')) || 0);
    } else {
      const newDisplay = capitalDisplay + num;
      setCapitalDisplay(newDisplay);
      setCapital(Number(newDisplay.replace(/,/g, '')) || 0);
    }
  };

  const formatMoney = (num) => num ? num.toLocaleString('fa-IR') : '۰';
  const getSymbolName = (symbol) => ({ gold: 'طلا', usd: 'دلار', ounce: 'انس', coin: 'سکه' }[symbol] || symbol);

  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      <header className="header glass">
        <div className="header-left">
          <img src="/logo.png" alt="Zarinsanj" className="header-logo" />
          <div className="header-titles"><h1>Zarinsanj</h1><span className="header-subtitle">زرین‌سنج</span></div>
        </div>
        <div className="header-info">
          <span className="update-time">📅 {lastUpdate || 'در حال بارگذاری...'}</span>
          <button onClick={updateData} className="update-btn-glass">🔄</button>
          <button onClick={() => setDarkMode(!darkMode)} className="theme-btn-glass">{darkMode ? '☀️' : '🌙'}</button>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      {loading ? <div className="loading">⏳ در حال بارگذاری...</div> : (
        <>
          {/* کیلومترها */}
          <div className="meters-container">
            <div className="meter-card glass">
              <div className="meter-header"><span className="meter-icon">🥇</span><span className="meter-title">میل به خرید طلا</span></div>
              <div className="meter-bar-wrapper"><div className="meter-bar"><div className="meter-fill" style={{ width: `${buyMeterGold}%` }} /><span className="meter-value">{Math.round(buyMeterGold)}%</span></div></div>
              <div className="meter-status">{buyMeterGold > 60 ? `🟢 ${Math.round(buyMeterGold)}% میل به خرید` : buyMeterGold < 40 ? `🔴 ${Math.round(buyMeterGold)}% میل به فروش` : `⚪ ${Math.round(buyMeterGold)}% بازار متعادل`}</div>
            </div>
            <div className="meter-card glass">
              <div className="meter-header"><span className="meter-icon">💵</span><span className="meter-title">میل به خرید دلار</span></div>
              <div className="meter-bar-wrapper"><div className="meter-bar"><div className="meter-fill" style={{ width: `${buyMeterUsd}%` }} /><span className="meter-value">{Math.round(buyMeterUsd)}%</span></div></div>
              <div className="meter-status">{buyMeterUsd > 60 ? `🟢 ${Math.round(buyMeterUsd)}% میل به خرید` : buyMeterUsd < 40 ? `🔴 ${Math.round(buyMeterUsd)}% میل به فروش` : `⚪ ${Math.round(buyMeterUsd)}% بازار متعادل`}</div>
            </div>
          </div>

          {/* قیمت‌ها (درست) */}
          <div className="prices-grid">
            {Object.entries(prices).map(([symbol, price]) => (
              <div key={symbol} className="price-card glass"><div className="price-symbol">{getSymbolName(symbol)}</div><div className="price-value">{formatMoney(price)} ریال</div></div>
            ))}
          </div>

          {/* تحلیل‌ها */}
          <div className="analysis-grid">
            {analysis.map((item) => (
              <div key={item.symbol} className="analysis-card glass">
                <div className="card-header">
                  <h3>{getSymbolName(item.symbol)}</h3>
                  <div className="card-header-actions">
                    <span className="recommendation" style={{ backgroundColor: item.recommendation?.includes('BUY') ? '#34c759' : item.recommendation?.includes('SELL') ? '#ff3b30' : '#ffd60a' }}>{item.recommendation}</span>
                    <button className="info-btn" onClick={() => setShowInfo(item.symbol)}>ⓘ</button>
                  </div>
                </div>
                <div className="card-metrics">
                  <div className="metric"><span>قیمت</span><strong>{formatMoney(item.current_price)} ریال</strong></div>
                  <div className="metric"><span>روند</span><strong>{item.trend}</strong></div>
                  <div className="metric"><span>RSI</span><strong>{item.rsi?.toFixed(1)}</strong></div>
                  <div className="metric"><span>امتیاز</span><strong>{item.final_score?.toFixed(0)}/100</strong></div>
                </div>
                {news.find(n => n.symbol === item.symbol) && <div className="news-item"><span className="news-icon">📰</span><span className="news-text">{news.find(n => n.symbol === item.symbol).text}</span></div>}
                <div className="card-confidence"><div className="confidence-bar"><div className="confidence-fill" style={{ width: `${item.confidence || 0}%` }} /></div><span>اطمینان: {item.confidence || 0}%</span></div>
              </div>
            ))}
          </div>

          {/* ماشین حساب (محاسبه خودکار) */}
          <div className="gold-calculator glass">
            <div className="calc-header"><h2>🧮 ماشین حساب طلا</h2><button className="calc-toggle" onClick={() => setShowGoldCalc(!showGoldCalc)}>{showGoldCalc ? '🔽' : '🔼'}</button></div>
            {showGoldCalc && (
              <div className="calc-body">
                <div className="calc-info"><span>💰 قیمت پایه سایت (هر گرم طلا با عیار ۷۵۰):</span><strong>{formatMoney(prices.gold || 0)} ریال</strong></div>
                <div className="calc-row"><label>وزن (گرم)</label><input type="number" value={goldCalc.weight} onChange={(e) => setGoldCalc(prev => ({ ...prev, weight: Number(e.target.value) || 0 }))} min="0.1" step="0.1" /></div>
                <div className="calc-row"><label>عیار</label><select value={goldCalc.karat} onChange={(e) => setGoldCalc(prev => ({ ...prev, karat: Number(e.target.value) }))} className={darkMode ? '' : 'light-select'}><option value="740">۷۴۰</option><option value="750">۷۵۰ (۱۸ عیار)</option><option value="916">۹۱۶ (۲۲ عیار)</option><option value="999">۹۹۹ (۲۴ عیار)</option></select></div>
                <div className="calc-row"><label>قیمت فروشنده (ریال)</label><input type="number" value={goldCalc.sellerPrice} onChange={(e) => setGoldCalc(prev => ({ ...prev, sellerPrice: Number(e.target.value) || 0 }))} min="0" placeholder="مثلاً 185000000" /><span className="calc-hint">💰 قیمت هر گرم طلا با عیار انتخابی در سایت: {formatMoney((prices.gold || 0) * (goldCalc.karat / 750))} ریال</span></div>
                <div className="calc-row"><label>کارمزد (%)</label><input type="number" value={goldCalc.commission} onChange={(e) => setGoldCalc(prev => ({ ...prev, commission: Number(e.target.value) || 0 }))} min="0" max="10" step="0.1" placeholder="۰" /></div>
                <div className="calc-results">
                  <div className="calc-result-item"><span>💰 قیمت فروشنده با کارمزد</span><strong>{formatMoney(goldCalc.finalSellerPrice)} ریال</strong><small>قیمت فروشنده: {formatMoney(goldCalc.sellerPrice)} + کارمزد {goldCalc.commission}%</small></div>
                  <div className="calc-result-item"><span>🏛️ قیمت سایت با کارمزد</span><strong>{formatMoney(goldCalc.finalOfficialPrice)} ریال</strong><small>قیمت سایت: {formatMoney(goldCalc.officialPrice)} + کارمزد {goldCalc.commission}%</small></div>
                  <div className="calc-result-item"><span>📊 اختلاف قیمت</span><strong style={{ color: goldCalc.isCheaper ? '#34c759' : '#ff3b30' }}>{goldCalc.isCheaper ? '✅ ارزان‌تر' : '❌ گران‌تر'} ({formatMoney(Math.abs(goldCalc.difference))} ریال)</strong><small>{goldCalc.isCheaper ? `فروشنده ${formatMoney(Math.abs(goldCalc.difference))} ریال ارزان‌تر از سایت` : `فروشنده ${formatMoney(Math.abs(goldCalc.difference))} ریال گران‌تر از سایت`}</small></div>
                </div>
              </div>
            )}
          </div>

          {/* سرمایه‌گذاری با کیبورد مجازی */}
          <div className="portfolio-section glass">
            <div className="portfolio-header"><h2>💼 مشاور سرمایه‌گذاری</h2><button className="portfolio-toggle-btn" onClick={() => setShowPortfolio(!showPortfolio)}>{showPortfolio ? '🔽' : '🔼'}</button></div>
            <p className="portfolio-subtitle">مبلغ سرمایه را با صفحه کلید مجازی وارد کنید.</p>
            {showPortfolio && (
              <>
                <div className="portfolio-controls">
                  <div className="capital-input-group">
                    <label>مبلغ سرمایه (ریال)</label>
                    <div className="capital-display"><span>{capitalDisplay || '۰'}</span></div>
                    <div className="virtual-keyboard">
                      <div className="keyboard-row"><button onClick={() => handleNumberClick('1')}>1</button><button onClick={() => handleNumberClick('2')}>2</button><button onClick={() => handleNumberClick('3')}>3</button><button onClick={() => handleNumberClick('000')} className="key-zero">000</button></div>
                      <div className="keyboard-row"><button onClick={() => handleNumberClick('4')}>4</button><button onClick={() => handleNumberClick('5')}>5</button><button onClick={() => handleNumberClick('6')}>6</button><button onClick={() => handleNumberClick('⌫')} className="key-delete">⌫</button></div>
                      <div className="keyboard-row"><button onClick={() => handleNumberClick('7')}>7</button><button onClick={() => handleNumberClick('8')}>8</button><button onClick={() => handleNumberClick('9')}>9</button><button onClick={() => handleNumberClick('0')}>0</button></div>
                    </div>
                  </div>
                  <div className="preference-selector"><label>اولویت سرمایه‌گذاری</label><select value={userPreference} onChange={(e) => setUserPreference(e.target.value)} className={darkMode ? '' : 'light-select'}><option value="gold">🥇 طلا</option><option value="usd">💵 دلار</option><option value="coin">🪙 سکه</option></select></div>
                  <button onClick={fetchPortfolio} className="portfolio-btn" disabled={portfolioLoading}>{portfolioLoading ? '⏳ در حال تحلیل...' : '🔍 دریافت پیشنهادات'}</button>
                </div>
                {portfolio?.status === 'success' && (
                  <div className="portfolio-results">
                    <div className="portfolio-summary"><span>💰 سرمایه: {formatMoney(portfolio.capital)} ریال</span><span>📊 اولویت: {userPreference === 'gold' ? 'طلا' : userPreference === 'usd' ? 'دلار' : 'سکه'}</span><span>📅 {new Date(portfolio.timestamp).toLocaleString('fa-IR')}</span></div>
                    {portfolio.recommendations.map((rec, idx) => (
                      <div key={idx} className="portfolio-card glass">
                        <div className="portfolio-card-header"><span className="scenario-icon">{rec.color}</span><h4>سناریوی {rec.scenario}</h4></div>
                        <div className="portfolio-allocations">
                          {Object.entries(rec.allocations).map(([symbol, data]) => (
                            <div key={symbol} className="allocation-item">
                              <span className="allocation-symbol">{getSymbolName(symbol)}</span>
                              <span className="allocation-amount">{formatMoney(data.amount_toman)} ریال</span>
                              <span className="allocation-percent">({data.weight_percent.toFixed(1)}%)</span>
                              <span className="allocation-quantity">≈ {symbol === 'coin' ? Math.round(data.quantity) : data.quantity} {symbol === 'coin' ? 'قطعه' : 'واحد'}</span>
                              <div className="allocation-bar"><div className="allocation-fill" style={{ width: `${data.weight_percent}%` }} /></div>
                            </div>
                          ))}
                        </div>
                        <div className="portfolio-metrics"><span>📈 بازده: {rec.expected_return.toFixed(1)}%</span><span>📉 ریسک: {rec.expected_risk.toFixed(1)}%</span></div>
                      </div>
                    ))}
                  </div>
                )}
              </>
            )}
          </div>
        </>
      )}

      <footer className="footer"><p>Zarinsanj © 2026 | توسعه‌دهنده: F.Mazaheri</p><p style={{ fontSize: '12px', color: '#666' }}>منبع داده: TGJU | نسخه V3.1</p></footer>
    </div>
  );
}

export default App;