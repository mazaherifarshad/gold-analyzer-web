import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

const API_URL = 'https://gold-analyzer-web.onrender.com';

function App() {
  // ===== وضعیت‌ها =====
  const [prices, setPrices] = useState({});
  const [analysis, setAnalysis] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const [showInfo, setShowInfo] = useState(null);

  // ===== وضعیت بخش سرمایه‌گذاری (ارزش‌افزوده) =====
  const [capital, setCapital] = useState(50000000);
  const [capitalInput, setCapitalInput] = useState('50,000,000');
  const [riskLevel, setRiskLevel] = useState('moderate');
  const [portfolio, setPortfolio] = useState(null);
  const [portfolioLoading, setPortfolioLoading] = useState(false);
  const [showPortfolio, setShowPortfolio] = useState(false);

  // ===== دریافت داده‌های اصلی =====
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
      setLastUpdate(new Date().toLocaleTimeString('fa-IR'));
      setError(null);
    } catch (err) {
      setError('خطا در دریافت داده. لطفاً دوباره تلاش کنید.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  // ===== دریافت پیشنهادات سرمایه‌گذاری (فقط وقتی کاربر درخواست دهد) =====
  const fetchPortfolio = async () => {
    setPortfolioLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/portfolio`, {
        params: { capital, risk: riskLevel }
      });
      setPortfolio(response.data);
      setShowPortfolio(true);
    } catch (err) {
      setError('خطا در دریافت پیشنهادات سرمایه‌گذاری.');
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
      setError('به‌روزرسانی ناموفق بود.');
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 60000);
    return () => clearInterval(interval);
  }, []);

  // ===== توابع کمکی =====
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

  const parseNumber = (str) => Number(str.replace(/,/g, ''));

  const handleSliderChange = (e) => {
    const val = Number(e.target.value);
    setCapital(val);
    setCapitalInput(formatNumber(val));
  };

  const handleInputChange = (e) => {
    const raw = e.target.value.replace(/,/g, '');
    const num = Number(raw);
    if (!isNaN(num) && num >= 0) {
      setCapital(num);
      setCapitalInput(formatNumber(num));
    } else {
      setCapitalInput(e.target.value);
    }
  };

  const handleInputBlur = () => {
    if (isNaN(capital) || capital < 1000000) {
      setCapital(1000000);
      setCapitalInput('1,000,000');
    }
  };

  // ===== اطلاعات تحلیل (برای پنجره کامنت) =====
  const getAnalysisInfo = (symbol) => {
    const info = {
      gold: {
        title: 'تحلیل طلا ۱۸ عیار',
        factors: [
          'قیمت جهانی طلا (انس) تأثیر مستقیم بر قیمت داخلی دارد.',
          'نرخ ارز (دلار/تومان) یکی از مهم‌ترین عوامل تعیین‌کننده است.',
          'نرخ تورم در ایران باعث افزایش تقاضا برای طلا به‌عنوان دارایی امن می‌شود.',
          'تنش‌های سیاسی و اقتصادی منطقه بر قیمت طلا تأثیرگذار است.',
          'تقاضای داخلی برای طلا در ایام خاص (مثل عروسی‌ها) افزایش می‌یابد.'
        ],
        recommendation: 'طلا در بلندمدت یک دارایی امن محسوب می‌شود، اما در کوتاه‌مدت نوسان دارد.'
      },
      usd: {
        title: 'تحلیل دلار آمریکا',
        factors: [
          'نرخ ارز در بازار آزاد تحت تأثیر عرضه و تقاضا قرار دارد.',
          'سیاست‌های پولی بانک مرکزی بر نرخ دلار تأثیر می‌گذارد.',
          'صادرات و واردات کشور تعیین‌کننده اصلی نرخ ارز است.',
          'تحریم‌های بین‌المللی باعث افزایش نرخ دلار می‌شود.',
          'نرخ تورم و رشد اقتصادی بر ارزش پول ملی تأثیر دارد.'
        ],
        recommendation: 'دلار تحت تأثیر عوامل سیاسی و اقتصادی زیادی قرار دارد و نوسان بالایی دارد.'
      },
      ounce: {
        title: 'تحلیل انس جهانی طلا',
        factors: [
          'قیمت دلار آمریکا (DXY) رابطه معکوس با قیمت انس دارد.',
          'نرخ بهره فدرال رزرو بر جذابیت طلا تأثیر می‌گذارد.',
          'تنش‌های ژئوپلیتیکی باعث افزایش قیمت انس می‌شود.',
          'تقاضای فیزیکی برای طلا از سوی کشورهای بزرگ مصرف‌کننده.',
          'سرمایه‌گذاری در صندوق‌های طلا (ETF) بر قیمت تأثیر دارد.'
        ],
        recommendation: 'انس جهانی به‌عنوان قیمت مرجع طلا در جهان شناخته می‌شود و تحت تأثیر عوامل بین‌المللی است.'
      },
      coin: {
        title: 'تحلیل سکه بهار آزادی',
        factors: [
          'قیمت طلای ۱۸ عیار پایه اصلی قیمت سکه است.',
          'نرخ ارز (دلار/تومان) تأثیر مستقیم بر قیمت سکه دارد.',
          'نرخ بهره بانکی بر جذابیت سرمایه‌گذاری در سکه تأثیر می‌گذارد.',
          'تقاضای فصلی (مخصوصاً در ایام خاص مثل عید) افزایش می‌یابد.',
          'وضعیت اقتصادی کشور و تورم بر قیمت سکه تأثیر دارد.'
        ],
        recommendation: 'سکه بهار آزادی یکی از محبوب‌ترین ابزارهای سرمایه‌گذاری در ایران است.'
      }
    };
    return info[symbol] || null;
  };

  // ============================================================
  return (
    <div className={`app ${darkMode ? 'dark' : 'light'}`}>
      {/* ===== HEADER ===== */}
      <header className="header">
        <div className="header-left">
          <div className="header-logo-text">ز</div>
          <h1>🏆 زرین‌سنج</h1>
        </div>
        <div className="header-info">
          <button onClick={() => setDarkMode(!darkMode)} className="theme-btn">
            {darkMode ? '☀️' : '🌙'}
          </button>
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
          {/* ===== قیمت‌های لحظه‌ای ===== */}
          <div className="prices-grid">
            {Object.entries(prices).map(([symbol, price]) => (
              <div key={symbol} className="price-card">
                <div className="price-symbol">{getSymbolName(symbol)}</div>
                <div className="price-value">{formatNumber(price)}</div>
              </div>
            ))}
          </div>

          {/* ===== تحلیل‌های تکنیکال ===== */}
          <div className="analysis-grid">
            {analysis.map((item) => {
              const info = getAnalysisInfo(item.symbol);
              return (
                <div key={item.symbol} className="analysis-card">
                  <div className="card-header">
                    <h3>{getSymbolName(item.symbol)}</h3>
                    <div className="card-header-actions">
                      <span className="recommendation" style={{ backgroundColor: getRecommendationColor(item.recommendation) }}>
                        {item.recommendation}
                      </span>
                      <button className="info-btn" onClick={() => setShowInfo(item.symbol)} title="مشاهده جزئیات تحلیل">ⓘ</button>
                    </div>
                  </div>
                  <div className="card-metrics">
                    <div className="metric"><span>قیمت</span><strong>{formatNumber(item.current_price)}</strong></div>
                    <div className="metric"><span>روند</span><strong>{item.trend}</strong></div>
                    <div className="metric"><span>RSI</span><strong>{item.rsi?.toFixed(1)}</strong></div>
                    <div className="metric"><span>امتیاز</span><strong>{item.final_score?.toFixed(0)}/100</strong></div>
                  </div>
                  <div className="prediction">
                    <span>🔮 پیش‌بینی: </span>
                    <span className={item.trend?.includes('UP') ? 'bullish' : 'bearish'}>
                      {item.trend?.includes('UP') ? '🟢 صعودی' : item.trend?.includes('DOWN') ? '🔴 نزولی' : '⚪ خنثی'}
                    </span>
                  </div>
                  <div className="card-confidence">
                    <div className="confidence-bar"><div className="confidence-fill" style={{ width: `${item.confidence || 0}%` }} /></div>
                    <span>اطمینان: {item.confidence || 0}%</span>
                  </div>
                  {item.reasons?.length > 0 && (
                    <div className="card-reasons">
                      {item.reasons.map((reason, idx) => <div key={idx} className="reason">• {reason}</div>)}
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* ===== وضعیت کلی بازار ===== */}
          <div className="market-status">
            <h2>📊 وضعیت کلی بازار</h2>
            <div className="status-grid">
              <div className="status-card">
                <span className="status-label">حباب بازار</span>
                <span className="status-value bubble">🟡 متوسط</span>
              </div>
              <div className="status-card">
                <span className="status-label">ریسک کلی</span>
                <span className="status-value risk">🔴 بالا</span>
              </div>
              <div className="status-card">
                <span className="status-label">اخبار اقتصادی</span>
                <span className="status-value news">🔵 مثبت</span>
              </div>
              <div className="status-card">
                <span className="status-label">پیشنهاد کلی</span>
                <span className="status-value recommendation">🟡 صبر کنید</span>
              </div>
            </div>
            <div className="status-note">
              <p>⚠️ وضعیت بازار نشان‌دهنده نوسان بالا و ریسک زیاد است. بهتر است در شرایط فعلی از معاملات پرریسک خودداری کنید.</p>
            </div>
          </div>

          {/* ===== مشاور سرمایه‌گذاری (ارزش‌افزوده) ===== */}
          <div className="portfolio-section">
            <div className="portfolio-header">
              <h2>💼 مشاور سرمایه‌گذاری</h2>
              <button 
                className="portfolio-toggle-btn"
                onClick={() => setShowPortfolio(!showPortfolio)}
              >
                {showPortfolio ? '🔽 بستن' : '🔼 باز کردن'}
              </button>
            </div>
            <p className="portfolio-subtitle">
              با وارد کردن مبلغ سرمایه، بهترین پیشنهاد خرید را بر اساس تحلیل‌های لحظه‌ای دریافت کنید.
            </p>

            {showPortfolio && (
              <>
                <div className="portfolio-controls">
                  <div className="capital-input-group">
                    <label>مبلغ سرمایه (تومان):</label>
                    <div className="capital-input-row">
                      <input type="range" min="1000000" max="1000000000" step="1000000" value={capital} onChange={handleSliderChange} className="capital-slider" />
                      <input type="text" value={capitalInput} onChange={handleInputChange} onBlur={handleInputBlur} className="capital-text-input" dir="ltr" />
                    </div>
                    <span className="capital-hint">حداقل: ۱,۰۰۰,۰۰۰ | حداکثر: ۱,۰۰۰,۰۰۰,۰۰۰</span>
                  </div>
                  <div className="risk-selector">
                    <label>سطح ریسک‌پذیری:</label>
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

                {portfolio?.status === 'success' && (
                  <div className="portfolio-results">
                    <div className="portfolio-summary">
                      <span>💰 سرمایه: {formatNumber(portfolio.capital)} تومان</span>
                      <span>📊 سطح ریسک: {getRiskLabel(portfolio.risk_level)}</span>
                      <span>📅 {new Date(portfolio.timestamp).toLocaleString('fa-IR')}</span>
                    </div>
                    {portfolio.recommendations.map((rec, idx) => {
                      const roundedAllocations = {};
                      Object.entries(rec.allocations).forEach(([symbol, data]) => {
                        if (symbol === 'coin') {
                          roundedAllocations[symbol] = {
                            ...data,
                            quantity: Math.round(data.quantity),
                            amount_toman: Math.round(data.quantity) * data.price
                          };
                        } else {
                          roundedAllocations[symbol] = data;
                        }
                      });
                      const updatedRec = { ...rec, allocations: roundedAllocations };
                      return (
                        <div key={idx} className="portfolio-card">
                          <div className="portfolio-card-header">
                            <span className="scenario-icon">{rec.color}</span>
                            <h4>سناریوی {rec.scenario}</h4>
                            <span className="sharpe-ratio">نسبت شارپ: {rec.sharpe_ratio.toFixed(2)}</span>
                          </div>
                          <div className="portfolio-allocations">
                            {Object.entries(updatedRec.allocations).map(([symbol, data]) => (
                              <div key={symbol} className="allocation-item">
                                <span className="allocation-symbol">{getSymbolName(symbol)}</span>
                                <span className="allocation-amount">{formatNumber(data.amount_toman)} تومان</span>
                                <span className="allocation-percent">({data.weight_percent.toFixed(1)}%)</span>
                                <span className="allocation-quantity">
                                  {symbol === 'coin' ? `≈ ${Math.round(data.quantity)} قطعه` : `≈ ${data.quantity.toFixed(2)} واحد`}
                                </span>
                                <div className="allocation-bar"><div className="allocation-fill" style={{ width: `${data.weight_percent}%` }} /></div>
                              </div>
                            ))}
                          </div>
                          <div className="portfolio-metrics">
                            <span>📈 بازده مورد انتظار: {rec.expected_return.toFixed(1)}%</span>
                            <span>📉 ریسک: {rec.expected_risk.toFixed(1)}%</span>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                )}
                {portfolio?.status === 'error' && <div className="portfolio-error">{portfolio.message}</div>}
              </>
            )}
          </div>
        </>
      )}

      {/* ===== پنجره اطلاعات (کامنت) ===== */}
      {showInfo && (
        <div className="info-modal" onClick={() => setShowInfo(null)}>
          <div className="info-modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="info-modal-close" onClick={() => setShowInfo(null)}>✕</button>
            {(() => {
              const info = getAnalysisInfo(showInfo);
              if (!info) return <p>اطلاعاتی موجود نیست.</p>;
              const item = analysis.find(a => a.symbol === showInfo);
              return (
                <>
                  <h2>{info.title}</h2>
                  <div className="info-factors">
                    <h4>🔍 عوامل مؤثر در تحلیل:</h4>
                    <ul>
                      {info.factors.map((factor, idx) => <li key={idx}>{factor}</li>)}
                    </ul>
                  </div>
                  <div className="info-recommendation">
                    <h4>💡 توصیه تحلیل:</h4>
                    <p>{info.recommendation}</p>
                  </div>
                  {item && (
                    <div className="info-stats">
                      <div><span>قیمت فعلی:</span> <strong>{formatNumber(item.current_price)}</strong></div>
                      <div><span>امتیاز تحلیل:</span> <strong>{item.final_score?.toFixed(0)}/100</strong></div>
                      <div><span>توصیه:</span> <strong>{item.recommendation}</strong></div>
                      <div><span>اطمینان:</span> <strong>{item.confidence}%</strong></div>
                    </div>
                  )}
                  <p className="info-timestamp">آخرین به‌روزرسانی: {lastUpdate}</p>
                </>
              );
            })()}
          </div>
        </div>
      )}

      {/* ===== FOOTER ===== */}
      <footer className="footer">
        <p>📊 زرین‌سنج - تحلیل‌گر حرفه‌ای بازار طلا و ارز ایران</p>
        <p>منبع داده: TGJU | نسخه V1.0 | توسعه‌دهنده: F.Mazaheri</p>
        <p style={{ fontSize: '12px', color: '#666', marginTop: '4px' }}>© 2026 Zarinsanj. All rights reserved.</p>
      </footer>
    </div>
  );
}

export default App;