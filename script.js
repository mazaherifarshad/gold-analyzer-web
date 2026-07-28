// ============================================
// داده‌های نمونه (شما با API خود جایگزین کنید)
// ============================================
const goldData = [
    { id: 1, title: 'طلای ۱۸ عیار', price: '۳,۴۵۰,۰۰۰', change: '+۰.۸٪', icon: 'fa-solid fa-coins', positive: true },
    { id: 2, title: 'سکه امامی', price: '۴۲,۸۰۰,۰۰۰', change: '-۰.۲٪', icon: 'fa-solid fa-circle', positive: false },
    { id: 3, title: 'دلار آزاد', price: '۵۸,۵۰۰', change: '+۱.۲٪', icon: 'fa-solid fa-dollar-sign', positive: true },
    { id: 4, title: 'یورو', price: '۶۲,۳۰۰', change: '+۰.۵٪', icon: 'fa-solid fa-euro-sign', positive: true },
    { id: 5, title: 'انس طلا', price: '۲,۰۳۵', change: '-۰.۱٪', icon: 'fa-solid fa-weight-scale', positive: false },
    { id: 6, title: 'نقره', price: '۲۴.۸۰', change: '+۰.۳٪', icon: 'fa-solid fa-gem', positive: true },
];

// ============================================
// رندر کارت‌ها
// ============================================
function renderCards(data) {
    const grid = document.getElementById('cardsGrid');
    if (!grid) return;

    if (data.length === 0) {
        grid.innerHTML = `<p style="grid-column:1/-1; text-align:center; color:#94a3b8; padding:40px 0;">نتیجه‌ای یافت نشد</p>`;
        return;
    }

    grid.innerHTML = data.map(item => `
        <div class="gold-card" data-id="${item.id}">
            <span class="card-icon"><i class="${item.icon}"></i></span>
            <div class="card-title">${item.title}</div>
            <div class="card-price">${item.price}</div>
            <span class="card-change ${item.positive ? 'change-positive' : 'change-negative'}">${item.change}</span>
        </div>
    `).join('');
}

// ============================================
// جستجو با مدیریت صفحه‌کلید (کلید ماجرا)
// ============================================
const searchInput = document.getElementById('goldSearch');
const suggestionsBox = document.getElementById('suggestions');
const clearBtn = document.getElementById('clearBtn');

// جلوگیری از بسته شدن صفحه‌کلید با کلیک روی سوجشن
suggestionsBox.addEventListener('mousedown', (e) => {
    e.preventDefault(); // جلوگیری از lose focus
});

// نمایش پیشنهادات هنگام تایپ
searchInput.addEventListener('input', function(e) {
    const query = this.value.trim().toLowerCase();
    const clear = document.getElementById('clearBtn');

    if (query.length > 0) {
        clear.style.display = 'block';
        const filtered = goldData.filter(item =>
            item.title.includes(query) ||
            item.price.includes(query)
        );

        if (filtered.length > 0) {
            suggestionsBox.innerHTML = filtered.map(item => `
                <div class="suggestion-item" data-id="${item.id}">
                    <i class="${item.icon}"></i>
                    <span>${item.title} - ${item.price}</span>
                </div>
            `).join('');
            suggestionsBox.classList.add('active');
        } else {
            suggestionsBox.innerHTML = `<div class="suggestion-item">موردی یافت نشد</div>`;
            suggestionsBox.classList.add('active');
        }
    } else {
        clear.style.display = 'none';
        suggestionsBox.classList.remove('active');
        renderCards(goldData);
    }
});

// کلیک روی هر پیشنهاد
suggestionsBox.addEventListener('click', function(e) {
    const item = e.target.closest('.suggestion-item');
    if (!item) return;
    const id = parseInt(item.dataset.id);
    const selected = goldData.find(d => d.id === id);
    if (selected) {
        searchInput.value = selected.title;
        suggestionsBox.classList.remove('active');
        document.getElementById('clearBtn').style.display = 'block';
        renderCards([selected]);
        // بستن صفحه‌کلید با blur
        searchInput.blur();
    }
});

// دکمه پاک کردن
clearBtn.addEventListener('click', function() {
    searchInput.value = '';
    this.style.display = 'none';
    suggestionsBox.classList.remove('active');
    renderCards(goldData);
    searchInput.focus(); // باز کردن صفحه‌کلید برای جستجوی جدید (اختیاری)
});

// کلیک بیرون برای بستن سوجشن
document.addEventListener('click', function(e) {
    if (!e.target.closest('.search-section')) {
        suggestionsBox.classList.remove('active');
    }
});

// ============================================
// کلید Enter برای جستجو (رفع هنگ)
// ============================================
searchInput.addEventListener('keydown', function(e) {
    if (e.key === 'Enter') {
        e.preventDefault();
        const query = this.value.trim();
        if (query) {
            const filtered = goldData.filter(item =>
                item.title.includes(query) ||
                item.price.includes(query)
            );
            renderCards(filtered);
            suggestionsBox.classList.remove('active');
            this.blur(); // بستن صفحه‌کلید
        }
    }
});

// ============================================
// مدیریت فوکوس برای جلوگیری از هنگ
// ============================================
searchInput.addEventListener('focus', function() {
    // هیچ کاری خاصی انجام نمی‌دهد، فقط برای اطمینان
    // اگر حجم داده سنگین است، اینجا می‌توانید lazy-load کنید
});

// ============================================
// بارگذاری اولیه
// ============================================
document.addEventListener('DOMContentLoaded', function() {
    renderCards(goldData);
    console.log('✅ زرین‌سنج با مدیریت صفحه‌کلید بارگذاری شد.');
});