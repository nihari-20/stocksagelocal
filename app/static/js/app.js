const API_URL = ""; // Relative path setup

// --- Dashboard Functions ---

async function fetchMarketPulse() {
    try {
        const res = await fetch(`${API_URL}/market-pulse`);
        const data = await res.json();

        const grid = document.getElementById('marketPulseGrid');
        grid.innerHTML = '';

        data.indices.forEach(idx => {
            const card = document.createElement('div');
            card.className = 'card';
            const isPos = idx.isPositive;

            // Auto-detect currency based on index name
            const currency = (idx.name.includes("Nifty") || idx.name.includes("Sensex")) ? "₹" : "$";

            card.innerHTML = `
                <div class="card-title">${idx.name}</div>
                <div class="card-value">${currency}${idx.price}</div>
                <div class="card-change ${isPos ? 'positive' : 'negative'}">
                    ${isPos ? '▲' : '▼'} ${idx.change}
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (e) {
        console.error("Pulse Error", e);
    }
}

async function fetchTrending() {
    try {
        const res = await fetch(`${API_URL}/trending`);
        const data = await res.json();

        const grid = document.getElementById('trendingGrid');
        grid.innerHTML = ''; // Clear loading

        data.forEach(stock => {
            const card = document.createElement('div');
            card.className = 'card';
            card.onclick = () => window.location.href = `/static/stock.html?symbol=${stock.symbol}`;

            const isPos = stock.isPositive;
            // Assume Trending logic knows region, or default to checking symbol for obvious Indian ones (mock)
            // For real implementation this would come from backend. For now, check if it looks like Ticker
            let currency = "$";
            if (stock.symbol && (stock.symbol.endsWith(".NS") || stock.symbol.endsWith(".BO") || stock.symbol.match(/^[A-Z]+$/) && !['AAPL', 'TSLA', 'GOOG', 'NVDA', 'AMZN', 'MSFT', 'META'].includes(stock.symbol))) {
                // Heuristic: If it's not a famous US tech stock, assume Indian for this local demo context or add robust check
                // For safety in this demo, let's look for "Nifty" or just default based on a list.
            }
            // Better heuristic: US stocks in this app are the famous tech ones. 
            if (['AAPL', 'TSLA', 'GOOG', 'NVDA', 'AMZN', 'MSFT', 'META', 'NFLX', 'AMD', 'SPY', 'QQQ'].includes(stock.symbol)) {
                currency = "$";
            } else {
                currency = "₹"; // Default to INR for local context if not known US
            }

            card.innerHTML = `
                <div style="display:flex; justify-content:space-between; margin-bottom:8px;">
                    <div class="card-title" style="margin:0; font-weight:700; color:var(--text-primary)">${stock.symbol}</div>
                    <span style="font-size:0.8rem; background:var(--bg-tertiary); padding:2px 6px; border-radius:4px;">${stock.action}</span>
                </div>
                <div class="card-value" style="font-size:1.25rem;">${currency}${stock.price}</div>
                <div class="card-change ${isPos ? 'positive' : 'negative'}">
                    ${isPos ? '▲' : '▼'} ${stock.change}
                </div>
            `;
            grid.appendChild(card);
        });
    } catch (e) {
        console.error("Trending Error", e);
    }
}

function setupSearch(inputId, resultsId) {
    const input = document.getElementById(inputId);
    const resultsParam = document.getElementById(resultsId);

    if (!input || !resultsParam) return; // Skip if element doesn't exist

    let debounce;

    input.addEventListener('input', (e) => {
        clearTimeout(debounce);
        const q = e.target.value;
        if (q.length < 2) {
            resultsParam.classList.remove('active');
            return;
        }

        debounce = setTimeout(async () => {
            try {
                const res = await fetch(`${API_URL}/search?q=${q}`);
                const data = await res.json();

                resultsParam.innerHTML = '';
                if (data.length > 0) {
                    resultsParam.classList.add('active');
                    data.forEach(item => {
                        const div = document.createElement('div');
                        div.className = 'result-item';
                        div.innerHTML = `
                        <div>
                            <span style="font-weight:600; color:var(--text-primary)">${item.symbol}</span>
                            <span style="margin-left:8px; color:var(--text-secondary); font-size:0.9rem;">${item.name}</span>
                        </div>
                        <span style="font-size:0.8rem; padding:2px 6px; background:var(--bg-tertiary); border-radius:4px;">${item.type}</span>
                    `;
                        div.onclick = () => window.location.href = `/static/stock.html?symbol=${item.symbol}`;
                        resultsParam.appendChild(div);
                    });
                } else {
                    resultsParam.classList.remove('active');
                }
            } catch (e) { console.error("Search error", e); }
        }, 300);
    });

    // Check click outside
    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !resultsParam.contains(e.target)) {
            resultsParam.classList.remove('active');
        }
    });
}

// Auto-init global search
document.addEventListener('DOMContentLoaded', () => {
    // Init global search (in navbar)
    setupSearch('globalSearch', 'globalSearchResults');

    // Init hero search (in dashboard only)
    setupSearch('stockSearch', 'searchResults');
});

// --- Stock Details Functions ---

async function loadStockDetails(symbol) {
    try {
        // 1. Fetch Insight (Fusion)
        const resInsight = await fetch(`${API_URL}/fusion/insight?symbol=${symbol}`);
        if (!resInsight.ok) throw new Error("Stock not found");
        const insight = await resInsight.json();

        // 2. Fetch History for Chart
        const resHistory = await fetch(`${API_URL}/get_prices?symbol=${symbol}`);
        const historyData = await resHistory.json();

        // 3. Fetch Stock News
        const resNews = await fetch(`${API_URL}/news?symbol=${symbol}`);
        const newsData = await resNews.json();

        renderStockPage(symbol, insight, historyData, newsData);

    } catch (e) {
        console.error(e);
        document.getElementById('loadingState').innerText = "Error loading data. Stock might be invalid.";
    }
}

function renderStockPage(symbol, insight, history, newsData) {
    document.getElementById('loadingState').style.display = 'none';
    document.getElementById('contentState').style.display = 'block';

    // Header
    document.getElementById('sName').innerText = symbol;
    document.getElementById('sSymbol').innerText = symbol;
    const market = insight.market || "GLOBAL";
    document.getElementById('sMarket').innerText = market;

    // Currency Logic
    const currency = (market === "INDIA" || market === "NSE" || market === "BSE") ? "₹" : "$";

    // Update Price from History (latest)
    if (history && history.prices) {
        const dates = Object.keys(history.prices);
        const lastDate = dates[dates.length - 1];
        const lastPrice = history.prices[lastDate];
        document.getElementById('sPrice').innerText = currency + lastPrice.toFixed(2);

        // Render Chart
        renderChart(history.prices);
    }

    // AI Insight
    if (insight.ai) {
        const ai = insight.ai;
        const regimeEl = document.getElementById('aiRegime');
        regimeEl.innerText = ai.regime;

        // Color code regime
        if (ai.regime.includes("Bull")) regimeEl.style.color = "var(--accent-primary)";
        else if (ai.regime.includes("Bear")) regimeEl.style.color = "var(--accent-error)";
        else regimeEl.style.color = "var(--accent-warning)";

        document.getElementById('aiConfidence').innerText = (ai.confidence * 100).toFixed(0) + "%";

        // Risk
        const riskFill = document.getElementById('riskFill');

        let width = "33%";
        let color = "var(--accent-primary)";

        if (ai.risk === "HIGH") { width = "90%"; color = "var(--accent-error)"; }
        else if (ai.risk === "MEDIUM") { width = "60%"; color = "var(--accent-warning)"; }
        else { width = "30%"; color = "var(--accent-primary)"; }

        riskFill.style.width = width;
        riskFill.style.background = color;
    }

    // Technicals
    if (insight.technical) {
        const tech = insight.technical;
        document.getElementById('indRSI').innerText = tech.RSI.toFixed(2);
        document.getElementById('indMACD').innerText = tech.MACD.toFixed(2);
        document.getElementById('indSignal').innerText = tech.signal;

        const sigEl = document.getElementById('indSignal');
        if (tech.signal === "BUY") sigEl.style.color = "var(--accent-primary)";
        else if (tech.signal === "SELL") sigEl.style.color = "var(--accent-error)";
    }

    // Pros & Cons
    const prosList = document.getElementById('prosList');
    const consList = document.getElementById('consList');

    if (prosList && insight.pros) {
        prosList.innerHTML = '';
        insight.pros.forEach(pro => {
            const li = document.createElement('li');
            li.style.cssText = "color: var(--text-secondary); margin-bottom: 12px; display: flex; align-items: flex-start; gap: 8px; font-size: 0.95rem;";
            li.innerHTML = `<span style="color: var(--accent-primary);">✓</span> <span>${pro}</span>`;
            prosList.appendChild(li);
        });
    }

    if (consList && insight.cons) {
        consList.innerHTML = '';
        insight.cons.forEach(con => {
            const li = document.createElement('li');
            li.style.cssText = "color: var(--text-secondary); margin-bottom: 12px; display: flex; align-items: flex-start; gap: 8px; font-size: 0.95rem;";
            li.innerHTML = `<span style="color: var(--accent-error);">✕</span> <span>${con}</span>`;
            consList.appendChild(li);
        });
    }

    // 4. Render Stock News
    // 4. Render Stock News
    const newsGrid = document.getElementById('stockNewsGrid');
    if (newsGrid && newsData) {
        newsGrid.innerHTML = '';
        newsGrid.className = 'news-grid'; // Use grid layout

        if (newsData.length === 0) {
            newsGrid.innerHTML = '<div style="color:var(--text-secondary)">No specific news found.</div>';
        } else {
            newsData.slice(0, 5).forEach((item, index) => { // Show top 5
                const div = document.createElement('div');
                div.className = 'news-card';

                // Stagger animation
                div.style.animationDelay = `${index * 0.1}s`;

                div.onclick = () => window.open(item.url, '_blank');

                const source = item.source || "MarketWire";
                const dateStr = item.datetime ? new Date(item.datetime).toLocaleDateString() : "Recent";
                const sentClass = item.sentiment === 'Positive' ? 'positive' : (item.sentiment === 'Negative' ? 'negative' : 'neutral');

                div.innerHTML = `
                    <div class="news-header">
                        <span class="news-source">${source}</span>
                        <div class="news-title">${item.headline}</div>
                    </div>
                    <div class="news-footer">
                        <span style="font-size:0.8rem; color:var(--text-muted)">${dateStr}</span>
                        <span class="sentiment-badge ${sentClass}">${item.sentiment}</span>
                    </div>
                `;
                newsGrid.appendChild(div);
            });
        }
    }
}

let priceChartInstance = null;

function renderChart(pricesObj) {
    const ctx = document.getElementById('priceChart').getContext('2d');

    const labels = Object.keys(pricesObj);
    const data = Object.values(pricesObj);

    if (priceChartInstance) priceChartInstance.destroy();

    const gradient = ctx.createLinearGradient(0, 0, 0, 400);
    gradient.addColorStop(0, 'rgba(0, 208, 156, 0.2)');
    gradient.addColorStop(1, 'rgba(0, 208, 156, 0.0)');

    priceChartInstance = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Price',
                data: data,
                borderColor: '#00d09c',
                backgroundColor: gradient,
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1e1e1e',
                    titleColor: '#eef2f5',
                    bodyColor: '#eef2f5',
                    borderColor: '#2c2c2e',
                    borderWidth: 1
                }
            },
            scales: {
                x: {
                    grid: { display: false, drawBorder: false },
                    ticks: { color: '#616e7c', maxTicksLimit: 6 }
                },
                y: {
                    grid: { color: '#2c2c2e', borderDash: [5, 5] },
                    ticks: { color: '#616e7c' }
                }
            }
        }
    });
}
