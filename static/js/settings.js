/* Settings — plan usage + AI support chat */

const chatHistory = [];

function usageBarClass(pct) {
  if (pct >= 90) return 'usage-bar-danger';
  if (pct >= 70) return 'usage-bar-warn';
  return 'usage-bar-ok';
}

function renderPlanUsage(data) {
  const badge = document.getElementById('plan-badge');
  const renewal = document.getElementById('plan-renewal');
  const grid = document.getElementById('plan-usage-grid');
  if (!grid) return;

  if (badge) badge.textContent = data.plan_label || 'Free';
  if (renewal) renewal.textContent = (data.renewal || 'Monthly') + ' billing';

  const metrics = data.metrics || [];
  if (!metrics.length) {
    grid.innerHTML = '<p class="stat-sub plan-usage-empty">Unable to load usage</p>';
    return;
  }

  grid.innerHTML = metrics.map(m => {
    const pct = Math.min(parseFloat(m.pct) || 0, 100);
    const barClass = usageBarClass(pct);
    return (
      '<div class="plan-usage-item">' +
        '<div class="plan-usage-item-head">' +
          '<span class="plan-usage-label">' + escapeHtml(m.label) + '</span>' +
          '<span class="plan-usage-count">' + escapeHtml(String(m.used)) + ' / ' + escapeHtml(String(m.limit)) + '</span>' +
        '</div>' +
        '<div class="usage-bar-track">' +
          '<div class="usage-bar-fill ' + barClass + '" style="width:' + pct + '%"></div>' +
        '</div>' +
      '</div>'
    );
  }).join('');
}

async function loadPlanUsage() {
  try {
    const data = await api('/api/plan');
    renderPlanUsage(data);
  } catch (_) {
    const grid = document.getElementById('plan-usage-grid');
    if (grid) grid.innerHTML = '<p class="stat-sub plan-usage-empty">Unable to load plan usage</p>';
  }
}

function appendChatMessage(role, text) {
  const list = document.getElementById('ai-chat-messages');
  if (!list) return;
  const wrap = document.createElement('div');
  wrap.className = 'ai-msg ai-msg-' + (role === 'user' ? 'user' : 'bot');
  wrap.innerHTML = '<div class="ai-msg-bubble">' + escapeHtml(text) + '</div>';
  list.appendChild(wrap);
  list.scrollTop = list.scrollHeight;
}

function setChatLoading(on) {
  const btn = document.getElementById('ai-chat-send');
  const input = document.getElementById('ai-chat-input');
  if (btn) btn.disabled = on;
  if (input) input.disabled = on;
}

async function sendChatMessage(message) {
  setChatLoading(true);
  appendChatMessage('user', message);
  chatHistory.push({ role: 'user', content: message });

  try {
    const res = await fetch('/api/support/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, history: chatHistory.slice(-8) }),
    });
    const data = await res.json();
    if (!data.ok) {
      appendChatMessage('bot', data.error || 'Something went wrong. Please try again.');
      return;
    }
    appendChatMessage('bot', data.reply);
    chatHistory.push({ role: 'assistant', content: data.reply });
    loadPlanUsage();
  } catch (_) {
    appendChatMessage('bot', 'Connection error. Check your network and try again.');
  } finally {
    setChatLoading(false);
  }
}

function initHelpAccordions() {
  document.querySelectorAll('.help-accordion').forEach(details => {
    details.addEventListener('toggle', () => {
      if (!details.open) return;
      document.querySelectorAll('.help-accordion').forEach(other => {
        if (other !== details) other.open = false;
      });
    });
  });
}

function initAiChat() {
  const form = document.getElementById('ai-chat-form');
  const input = document.getElementById('ai-chat-input');
  if (!form || !input) return;

  form.addEventListener('submit', async e => {
    e.preventDefault();
    const text = input.value.trim();
    if (!text) return;
    input.value = '';
    await sendChatMessage(text);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  loadPlanUsage();
  initHelpAccordions();
  initAiChat();
});
