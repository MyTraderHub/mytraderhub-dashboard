/* MyTraderHub global dashboard helpers */

async function api(path, opts) {
  const res = await fetch(path, opts);
  if (!res.ok) throw new Error('API error ' + res.status);
  return res.json();
}

function escapeHtml(str) {
  if (str == null) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function fmtMoney(n) {
  const v = parseFloat(n) || 0;
  return '$' + v.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
}

function fmtPct(n) {
  const v = parseFloat(n) || 0;
  return (v >= 0 ? '+' : '') + v.toFixed(2) + '%';
}

function plClass(n) {
  const v = parseFloat(n) || 0;
  return v >= 0 ? 'pl-pos' : 'pl-neg';
}

function openOrderSheet(ticker, side, price, name) {
  const sheet = document.getElementById('order-sheet');
  if (!sheet) return;
  sheet.innerHTML =
    '<div class="sheet-panel">' +
    '<div class="sheet-header"><h2 class="sheet-title">' + escapeHtml(side.toUpperCase()) + ' ' + escapeHtml(ticker) + '</h2>' +
    '<button type="button" class="sheet-close tap-feedback" id="order-close">✕</button></div>' +
    '<p class="stat-sub">Order entry — use account page or full order flow</p>' +
    '</div>';
  sheet.classList.remove('hidden');
  document.getElementById('order-close').onclick = () => sheet.classList.add('hidden');
}

function setupPullToRefresh(fn) {
  let startY = 0;
  let pulling = false;
  const el = document.getElementById('main-content') || document.body;

  el.addEventListener('touchstart', e => {
    if (window.scrollY <= 0) {
      startY = e.touches[0].clientY;
      pulling = true;
    }
  }, { passive: true });

  el.addEventListener('touchend', e => {
    if (!pulling) return;
    pulling = false;
    const dy = e.changedTouches[0].clientY - startY;
    if (dy > 80 && window.scrollY <= 0 && typeof fn === 'function') {
      fn();
    }
  }, { passive: true });
}

async function loadMarketBar() {
  const el = document.getElementById('market-bar-inner');
  if (!el) return;
  try {
    const data = await api('/api/market_bar');
    el.innerHTML = (data.items || []).map(item =>
      '<span class="market-item">' +
      '<span class="market-sym">' + escapeHtml(item.symbol) + '</span>' +
      '<span>' + fmtMoney(item.price) + '</span>' +
      '<span class="' + plClass(item.change_pct) + '">' + fmtPct(item.change_pct) + '</span>' +
      '</span>'
    ).join(' · ');
  } catch (_) {
    el.innerHTML = '<span class="stat-sub">Market data unavailable</span>';
  }
}

document.addEventListener('DOMContentLoaded', () => {
  loadMarketBar();
  setInterval(loadMarketBar, 60000);
});
