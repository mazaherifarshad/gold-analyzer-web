import React, { useState, useEffect, useRef } from 'react';
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

  // ===== وضعیت بخش سرمایه‌گذاری =====
  const [capital, setCapital] = useState(50000000);
  const [capitalInput, setCapitalInput] = useState('50,000,000');
  const [userPreference, setUserPreference] = useState('gold'); // gold, usd, coin
  const [portfolio, setPortfolio] = useState(null);
  const [portfolioLoading, setPortfolioLoading] = useState(false);
  const [showPortfolio, setShowPortfolio] = useState(false);

  // ===== وضعیت ماشین حساب طلا =====
  const [goldCalc, setGoldCalc] = useState({
    weight: 1,
    sellerPrice: 0,
    karat: 740,
    commission: 2,
    finalPrice: 0,
    officialPrice: 0,
    difference: 0,
    isCheaper: false,
    commissionAmount: 0
  });
  const [showGoldCalc, setShowGoldCalc] = useState(false);

  // ===== وضعیت نمایشگر ارزش خرید (کیلومتر) =====
  const [buyMeterGold, setBuyMeterGold] = useState(50);
  const [buyMeterUsd, setBuyMeterUsd] = useState(50);

  // ===== اخبار لحظه‌ای =====
  const [news, setNews] = useState([]);

  // ===== Refs =====
  const updateInterval = useRef(null);

  // ===== دریافت داده‌های اصلی =====
  const fetchData = async (showLoading = true) => {
    try {
      if (showLoading) setLoading(true);
      const [pricesRes, analysisRes] = await Promise.all([
        axios.get(`${API_URL}/prices`),
        axios.get(`${API_URL}/analysis`)
      ]);
      
      const priceMap = {};
      pricesRes.data.forEach(p => priceMap[p.symbol] = p.price);
      setPrices(priceMap);
      setAnalysis(analysisRes.data);
      
      // محاسبه کیلومتر برای طلا و دلار
      const goldAnalysis = analysisRes.data.find(a => a.symbol === 'gold');
      const usdAnalysis = analysisRes.data.find(a => a.symbol === 'usd');
      
      if (goldAnalysis) {
        setBuyMeterGold(Math.min(100, Math.max(0, goldAnalysis.final_score || 50)));
      }
      if (usdAnalysis) {
        setBuyMeterUsd(Math.min(100, Math.max(0, usdAnalysis.final_score || 50)));
      }

      // تولید اخبار لحظه‌ای
      const newsItems = generateNews(analysisRes.data, priceMap);
      setNews(newsItems);
      
      setLastUpdate(new Date().toLocaleString('fa-IR'));
      setError(null);
    } catch (err) {
      setError('خطا در دریافت داده. لطفاً دوباره تلاش کنید.');
      console.error(err);
    } finally {
      if (showLoading) setLoading(false);
    }
  };

  // ===== تولید اخبار لحظه‌ای =====
  const generateNews = (analysisData, priceData) => {
    const items = [];
    const gold = analysisData.find(a => a.symbol === 'gold');
    const usd = analysisData.find(a => a.symbol === 'usd');
    const coin = analysisData.find(a => a.symbol === 'coin');

    if (gold) {
      const goldPrice = priceData.gold || 0;
      const rsi = gold.rsi || 50;
      let newsText = '';
      if (rsi > 70) newsText = `طلا با RSI ${rsi.toFixed(1)} در منطقه اشباع خرید قرار دارد. احتمال اصلاح قیمت وجود دارد.`;
      else if (rsi < 30) newsText = `طلا با RSI ${rsi.toFixed(1)} در منطقه اشباع فروش قرار دارد. احتمال بازگشت قیمت وجود دارد.`;
      else if (gold.trend?.includes('UP')) newsText = `طلا در روند صعودی قرار دارد و قیمت آن ${goldPrice.toLocaleString('fa-IR')} تومان است.`;
      else if (gold.trend?.includes('DOWN')) newsText = `طلا در روند نزولی قرار دارد و قیمت آن ${goldPrice.toLocaleString('fa-IR')} تومان است.`;
      else newsText = `طلا در حالت نوسانی قرار دارد و قیمت آن ${goldPrice.toLocaleString('fa-IR')} تومان است.`;
      items.push({ symbol: 'gold', text: newsText });
    }

    if (usd) {
      const usdPrice = priceData.usd || 0;
      const rsi = usd.rsi || 50;
      let newsText = '';
      if (rsi > 70) newsText = `دلار با RSI ${rsi.toFixed(1)} در منطقه اشباع خرید قرار دارد.`;
      else if (rsi < 30) newsText = `دلار با RSI ${rsi.toFixed(1)} در منطقه اشباع فروش قرار دارد.`;
      else if (usd.trend?.includes('UP')) newsText = `دلار در روند صعودی قرار دارد و قیمت آن ${usdPrice.toLocaleString('fa-IR')} تومان است.`;
      else if (usd.trend?.includes('DOWN')) newsText = `دلار در روند نزولی قرار دارد و قیمت آن ${usdPrice.toLocaleString('fa-IR')} تومان است.`;
      else newsText = `دلار در حالت نوسانی قرار دارد و قیمت آن ${usdPrice.toLocaleString('fa-IR')} تومان است.`;
      items.push({ symbol: 'usd', text: newsText });
    }

    if (coin) {
      const coinPrice = priceData.coin || 0;
      const rsi = coin.rsi || 50;
      let newsText = '';
      if (rsi > 70) newsText = `سکه با RSI ${rsi.toFixed(1)} در منطقه اشباع خرید قرار دارد.`;
      else if (rsi < 30) newsText = `سکه با RSI ${rsi.toFixed(1)} در منطقه اشباع فروش قرار دارد.`;
      else if (coin.trend?.includes('UP')) newsText = `سکه در روند صعودی قرار دارد و قیمت آن ${coinPrice.toLocaleString('fa-IR')} تومان است.`;
      else if (coin.trend?.includes('DOWN')) newsText = `سکه در روند نزولی قرار دارد و قیمت آن ${coinPrice.toLocaleString('fa-IR')} تومان است.`;
      else newsText = `سکه در حالت نوسانی قرار دارد و قیمت آن ${coinPrice.toLocaleString('fa-IR')} تومان است.`;
      items.push({ symbol: 'coin', text: newsText });
    }

    return items;
  };

  // ===== دریافت پیشنهادات سرمایه‌گذاری =====
  const fetchPortfolio = async () => {
    setPortfolioLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_URL}/portfolio`, {
        params: { capital, risk: 'moderate' }
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

  // ===== به‌روزرسانی دستی =====
  const updateData = async () => {
    try {
      await axios.post(`${API_URL}/update`);
      await fetchData(true);
    } catch (err) {
      setError('به‌روزرسانی ناموفق بود.');
    }
  };

  // ===== راه‌اندازی به‌روزرسانی خودکار =====
  useEffect(() => {
    fetchData(true);
    updateInterval.current = setInterval(() => {
      fetchData(false);
    }, 60000);
    return () => clearInterval(updateInterval.current);
  }, []);

  // ===== ماشین حساب طلا =====
  const calculateGold = () => {
    const goldPrice = prices.gold || 0;
    // قیمت رسمی بر اساس عیار و وزن
    const officialPrice = goldPrice * goldCalc.weight * (goldCalc.karat / 1000);
    // قیمت فروشنده + کارمزد
    const sellerPrice = goldCalc.sellerPrice || officialPrice;
    const commissionAmount = sellerPrice * (goldCalc.commission / 100);
    const finalPrice = sellerPrice + commissionAmount;
    const difference = sellerPrice - officialPrice;
    
    setGoldCalc(prev => ({
      ...prev,
      finalPrice: finalPrice,
      officialPrice: officialPrice,
      commissionAmount: commissionAmount,
      difference: difference,
      isCheaper: difference < 0
    }));
  };

  useEffect(() => {
    if (prices.gold) {
      calculateGold();
    }
  }, [prices.gold, goldCalc.weight, goldCalc.karat, goldCalc.sellerPrice, goldCalc.commission]);

  // ===== توابع کمکی =====
  const getRecommendationColor = (rec) => {
    if (rec?.includes('BUY')) return '#34c759';
    if (rec?.includes('SELL')) return '#ff3b30';
    return '#ffd60a';
  };

  const getSymbolName = (symbol) => {
    const names = {
      gold: 'طلا ۱۸ عیار',
      usd: 'دلار آمریکا',
      ounce: 'انس جهانی',
      coin: 'سکه بهار آزادی',
      half_coin: 'نیم سکه',
      quarter_coin: 'ربع سکه',
      gram_coin: 'سکه گرمی'
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

  // ===== مدیریت ورودی سرمایه =====
  const handleCapitalSelect = (e) => {
    const val = Number(e.target.value);
    setCapital(val);
    setCapitalInput(formatNumber(val));
  };

  const handleCapitalInput = (e) => {
    const raw = e.target.value.replace(/,/g, '');
    const num = Number(raw);
    if (!isNaN(num) && num >= 0) {
      setCapital(num);
      setCapitalInput(formatNumber(num));
    } else {
      setCapitalInput(e.target.value);
    }
  };

  const handleCapitalBlur = () => {
    if (isNaN(capital) || capital < 1000000) {
      setCapital(1000000);
      setCapitalInput('1,000,000');
    }
  };

  // ===== اطلاعات تحلیل =====
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
      <header className="header glass">
        <div className="header-left">
          <img src="/logo.png" alt="Zarinsanj" className="header-logo" />
          <h1>Zarinsanj</h1>
        </div>
        <div className="header-info">
          <span className="update-time">📅 {lastUpdate || 'در حال بارگذاری...'}</span>
          <button onClick={updateData} className="update-btn-glass" title="به‌روزرسانی">
            🔄
          </button>
          <button onClick={() => setDarkMode(!darkMode)} className="theme-btn-glass">
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>

      {error && <div className="error">{error}</div>}

      {loading ? (
        <div className="loading">⏳ در حال بارگذاری...</div>
      ) : (
        <>
          {/* ===== کیلومترهای خرید ===== */}
          <div className="meters-container">
            <div className="meter-card glass">
              <div className="meter-header">
                <span className="meter-icon">🥇</span>
                <span className="meter-title">میل به خرید طلا</span>
              </div>
              <div className="meter-bar-wrapper">
                <div className="meter-bar">
                  <div className="meter-fill" style={{ width: `${buyMeterGold}%`, background: buyMeterGold > 60 ? '#34c759' : buyMeterGold < 40 ? '#ff3b30' : '#ffd60a' }} />
                  <span className="meter-value">{Math.round(buyMeterGold)}%</span>
                </div>
              </div>
              <div className="meter-status">
                {buyMeterGold > 60 ? `🟢 ${Math.round(buyMeterGold)}% میل به خرید` : 
                 buyMeterGold < 40 ? `🔴 ${Math.round(buyMeterGold)}% میل به فروش` : 
                 `⚪ ${Math.round(buyMeterGold)}% بازار متعادل`}
              </div>
            </div>

            <div className="meter-card glass">
              <div className="meter-header">
                <span className="meter-icon">💵</span>
                <span className="meter-title">میل به خرید دلار</span>
              </div>
              <div className="meter-bar-wrapper">
                <div className="meter-bar">
                  <div className="meter-fill" style={{ width: `${buyMeterUsd}%`, background: buyMeterUsd > 60 ? '#34c759' : buyMeterUsd < 40 ? '#ff3b30' : '#ffd60a' }} />
                  <span className="meter-value">{Math.round(buyMeterUsd)}%</span>
                </div>
              </div>
              <div className="meter-status">
                {buyMeterUsd > 60 ? `🟢 ${Math.round(buyMeterUsd)}% میل به خرید` : 
                 buyMeterUsd < 40 ? `🔴 ${Math.round(buyMeterUsd)}% میل به فروش` : 
                 `⚪ ${Math.round(buyMeterUsd)}% بازار متعادل`}
              </div>
            </div>
          </div>

          {/* ===== قیمت‌های لحظه‌ای ===== */}
          <div className="prices-grid">
            {Object.entries(prices).map(([symbol, price]) => (
              <div key={symbol} className="price-card glass">
                <div className="price-symbol">{getSymbolName(symbol)}</div>
                <div className="price-value">{formatNumber(price)}</div>
              </div>
            ))}
          </div>

          {/* ===== تحلیل‌های تکنیکال با اخبار لحظه‌ای ===== */}
          <div className="analysis-grid">
            {analysis.map((item) => {
              const info = getAnalysisInfo(item.symbol);
              const newsItem = news.find(n => n.symbol === item.symbol);
              return (
                <div key={item.symbol} className="analysis-card glass">
                  <div className="card-header">
                    <h3>{getSymbolName(item.symbol)}</h3>
                    <div className="card-header-actions">
                      <span className="recommendation" style={{ backgroundColor: getRecommendationColor(item.recommendation) }}>
                        {item.recommendation}
                      </span>
                      <button className="info-btn" onClick={() => setShowInfo(item.symbol)}>ⓘ</button>
                    </div>
                  </div>
                  <div className="card-metrics">
                    <div className="metric"><span>قیمت</span><strong>{formatNumber(item.current_price)}</strong></div>
                    <div className="metric"><span>روند</span><strong>{item.trend}</strong></div>
                    <div className="metric"><span>RSI</span><strong>{item.rsi?.toFixed(1)}</strong></div>
                    <div className="metric"><span>امتیاز</span><strong>{item.final_score?.toFixed(0)}/100</strong></div>
                  </div>
                  {newsItem && (
                    <div className="news-item">
                      <span className="news-icon">📰</span>
                      <span className="news-text">{newsItem.text}</span>
                    </div>
                  )}
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

          {/* ===== ماشین حساب طلا ===== */}
          <div className="gold-calculator glass">
            <div className="calc-header">
              <h2>🧮 ماشین حساب طلا</h2>
              <button className="calc-toggle" onClick={() => setShowGoldCalc(!showGoldCalc)}>
                {showGoldCalc ? '🔽' : '🔼'}
              </button>
            </div>

            {showGoldCalc && (
              <div className="calc-body">
                <div className="calc-row">
                  <label>وزن (گرم)</label>
                  <input type="number" value={goldCalc.weight} onChange={(e) => setGoldCalc(prev => ({ ...prev, weight: Number(e.target.value) || 0 }))} min="0" step="0.01" />
                </div>
                <div className="calc-row">
                  <label>قیمت فروشنده (تومان)</label>
                  <input type="number" value={goldCalc.sellerPrice} onChange={(e) => setGoldCalc(prev => ({ ...prev, sellerPrice: Number(e.target.value) || 0 }))} min="0" />
                </div>
                <div className="calc-row">
                  <label>عیار</label>
                  <select value={goldCalc.karat} onChange={(e) => setGoldCalc(prev => ({ ...prev, karat: Number(e.target.value) }))}>
                    <option value="740">۷۴۰</option>
                    <option value="750">۷۵۰</option>
                    <option value="916">۹۱۶</option>
                    <option value="999">۹۹۹</option>
                  </select>
                </div>
                <div className="calc-row">
                  <label>کارمزد (%)</label>
                  <input type="number" value={goldCalc.commission} onChange={(e) => setGoldCalc(prev => ({ ...prev, commission: Number(e.target.value) || 0 }))} min="0" max="10" step="0.1" />
                </div>

                <button className="calc-btn" onClick={calculateGold}>🔍 محاسبه</button>

                <div className="calc-results">
                  <div className="calc-result-item">
                    <span>💰 قیمت رسمی (سایت)</span>
                    <strong>{formatNumber(goldCalc.officialPrice)} تومان</strong>
                  </div>
                  <div className="calc-result-item">
                    <span>💵 قیمت فروشنده با کارمزد</span>
                    <strong>{formatNumber(goldCalc.finalPrice)} تومان</strong>
                  </div>
                  <div className="calc-result-item">
                    <span>📊 کارمزد پرداختی</span>
                    <strong>{formatNumber(goldCalc.commissionAmount)} تومان</strong>
                  </div>
                  <div className="calc-result-item">
                    <span>📈 اختلاف با سایت</span>
                    <strong style={{ color: goldCalc.isCheaper ? '#34c759' : '#ff3b30' }}>
                      {goldCalc.isCheaper ? '✅ ارزان‌تر' : '❌ گران‌تر'} ({formatNumber(Math.abs(goldCalc.difference))} تومان)
                    </strong>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* ===== مشاور سرمایه‌گذاری (نسخه جدید) ===== */}
          <div className="portfolio-section glass">
            <div className="portfolio-header">
              <h2>💼 مشاور سرمایه‌گذاری</h2>
              <button className="portfolio-toggle-btn" onClick={() => setShowPortfolio(!showPortfolio)}>
                {showPortfolio ? '🔽' : '🔼'}
              </button>
            </div>
            <p className="portfolio-subtitle">نظر خود را در مورد اولویت سرمایه‌گذاری بگویید تا بهترین پیشنهاد را دریافت کنید.</p>

            {showPortfolio && (
              <>
                <div className="portfolio-controls">
                  <div className="capital-input-group">
                    <label>مبلغ سرمایه (تومان)</label>
                    <div className="capital-input-row">
                      <select value={capital} onChange={handleCapitalSelect} className="capital-select">
                        <option value="10000000">۱۰,۰۰۰,۰۰۰</option>
                        <option value="50000000">۵۰,۰۰۰,۰۰۰</option>
                        <option value="100000000">۱۰۰,۰۰۰,۰۰۰</option>
                        <option value="500000000">۵۰۰,۰۰۰,۰۰۰</option>
                        <option value="1000000000">۱,۰۰۰,۰۰۰,۰۰۰</option>
                        <option value="custom">سفارشی</option>
                      </select>
                      <input type="text" value={capitalInput} onChange={handleCapitalInput} onBlur={handleCapitalBlur} className="capital-text-input" dir="ltr" placeholder="مقدار دلخواه" />
                    </div>
                  </div>
                  <div className="preference-selector">
                    <label>اولویت سرمایه‌گذاری</label>
                    <select value={userPreference} onChange={(e) => setUserPreference(e.target.value)}>
                      <option value="gold">🥇 طلا</option>
                      <option value="usd">💵 دلار</option>
                      <option value="coin">🪙 سکه</option>
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
                      <span>📊 اولویت: {userPreference === 'gold' ? 'طلا' : userPreference === 'usd' ? 'دلار' : 'سکه'}</span>
                      <span>📅 {new Date(portfolio.timestamp).toLocaleString('fa-IR')}</span>
                    </div>

                    {/* نمایش ریسک‌ها و پیشنهادات */}
                    <div className="portfolio-risks">
                      <h4>⚠️ ریسک‌های موجود:</h4>
                      <ul>
                        <li>🔴 نوسان بالای بازار در شرایط فعلی</li>
                        <li>🟡 تأثیر اخبار سیاسی بر قیمت‌ها</li>
                        <li>🟢 فرصت خرید در قیمت‌های مناسب</li>
                      </ul>
                    </div>

                    <div className="portfolio-advice">
                      <h4>💡 پیشنهاد جایگزین:</h4>
                      <p>با توجه به شرایط بازار، پیشنهاد می‌شود به جای تمرکز بر یک دارایی، سبدی متشکل از {userPreference === 'gold' ? 'طلا و دلار' : userPreference === 'usd' ? 'دلار و طلا' : 'سکه و طلا'} تشکیل دهید تا ریسک شما کاهش یابد.</p>
                    </div>

                    {portfolio.recommendations.map((rec, idx) => {
                      const roundedAllocations = {};
                      const allowedAssets = ['gold', 'usd', 'coin'];
                      Object.entries(rec.allocations).forEach(([symbol, data]) => {
                        if (allowedAssets.includes(symbol)) {
                          let quantity = data.quantity;
                          let unit = 'واحد';
                          if (symbol === 'coin') {
                            quantity = Math.round(data.quantity);
                            unit = 'قطعه';
                          }
                          roundedAllocations[symbol] = {
                            ...data,
                            quantity: quantity,
                            amount_toman: data.amount_toman,
                            unit: unit
                          };
                        }
                      });
                      const updatedRec = { ...rec, allocations: roundedAllocations };
                      return (
                        <div key={idx} className="portfolio-card glass">
                          <div className="portfolio-card-header">
                            <span className="scenario-icon">{rec.color}</span>
                            <h4>سناریوی {rec.scenario}</h4>
                            <span className="sharpe-ratio">شارپ: {rec.sharpe_ratio.toFixed(2)}</span>
                          </div>
                          <div className="portfolio-allocations">
                            {Object.entries(updatedRec.allocations).map(([symbol, data]) => (
                              <div key={symbol} className="allocation-item">
                                <span className="allocation-symbol">{getSymbolName(symbol)}</span>
                                <span className="allocation-amount">{formatNumber(data.amount_toman)} تومان</span>
                                <span className="allocation-percent">({data.weight_percent.toFixed(1)}%)</span>
                                <span className="allocation-quantity">≈ {data.quantity} {data.unit || 'واحد'}</span>
                                <div className="allocation-bar"><div className="allocation-fill" style={{ width: `${data.weight_percent}%` }} /></div>
                              </div>
                            ))}
                          </div>
                          <div className="portfolio-metrics">
                            <span>📈 بازده: {rec.expected_return.toFixed(1)}%</span>
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

      {/* ===== پنجره اطلاعات ===== */}
      {showInfo && (
        <div className="info-modal" onClick={() => setShowInfo(null)}>
          <div className="info-modal-content glass">
            <button className="info-modal-close" onClick={() => setShowInfo(null)}>✕</button>
            {(() => {
              const info = getAnalysisInfo(showInfo);
              if (!info) return <p>اطلاعاتی موجود نیست.</p>;
              const item = analysis.find(a => a.symbol === showInfo);
              const newsItem = news.find(n => n.symbol === showInfo);
              return (
                <>
                  <h2>{info.title}</h2>
                  <div className="info-factors">
                    <h4>🔍 عوامل مؤثر در تحلیل امروز:</h4>
                    <ul>
                      {info.factors.map((factor, idx) => <li key={idx}>{factor}</li>)}
                    </ul>
                  </div>
                  {newsItem && (
                    <div className="info-news">
                      <h4>📰 اخبار لحظه‌ای:</h4>
                      <p>{newsItem.text}</p>
                    </div>
                  )}
                  <div className="info-recommendation">
                    <h4>💡 تحلیل نهایی:</h4>
                    <p>{info.recommendation}</p>
                  </div>
                  {item && (
                    <div className="info-stats">
                      <div><span>قیمت فعلی</span> <strong>{formatNumber(item.current_price)}</strong></div>
                      <div><span>امتیاز</span> <strong>{item.final_score?.toFixed(0)}/100</strong></div>
                      <div><span>توصیه</span> <strong>{item.recommendation}</strong></div>
                      <div><span>اطمینان</span> <strong>{item.confidence}%</strong></div>
                    </div>
                  )}
                </>
              );
            })()}
          </div>
        </div>
      )}

      {/* ===== FOOTER ===== */}
      <footer className="footer">
        <p>Zarinsanj © 2026 | توسعه‌دهنده: F.Mazaheri</p>
        <p style={{ fontSize: '12px', color: '#666' }}>منبع داده: TGJU | نسخه V1.3</p>
      </footer>
    </div>
  );
}

export default App;