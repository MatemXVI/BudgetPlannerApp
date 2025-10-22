const incomeEl = document.getElementById('income');
const expenseEl = document.getElementById('expense');
const netEl = document.getElementById('net');
const addDemoBtn = document.getElementById('addDemoBtn');
const refreshBalanceBtn = document.getElementById('refreshBalanceBtn');
const txListEl = document.getElementById('txList');
const refreshTxBtn = document.getElementById('refreshTxBtn');

// Lightweight ping that does not depend on missing DOM elements
async function checkPing() {
  try {
    const res = await fetch('/api/ping');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    console.debug('Ping OK:', data);
  } catch (e) {
    console.warn('Ping error:', e);
  }
}

async function refreshBalance() {
  try {
    const res = await fetch('/api/reports/balance');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    if (incomeEl) incomeEl.textContent = data.income;
    if (expenseEl) expenseEl.textContent = data.expense;
    if (netEl) {
      netEl.textContent = data.net;
      netEl.classList.toggle('ok', parseFloat(data.net) >= 0);
      netEl.classList.toggle('err', parseFloat(data.net) < 0);
    }
  } catch (e) {
    console.error(e);
  }
}

async function loadRecentTransactions() {
  try {
    const res = await fetch('/api/transactions?limit=5');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const items = await res.json();
    if (!txListEl) return;
    if (!items.length) {
      txListEl.innerHTML = '<li class="muted">Brak transakcji</li>';
      return;
    }
    txListEl.innerHTML = items.map(tx => {
      const sign = tx.type === 'income' ? '+' : '-';
      const color = tx.type === 'income' ? 'style="color:#10b981"' : 'style="color:#ef4444"';
      const amount = `${sign}${tx.amount}`;
      const desc = tx.description ?? '';
      const date = tx.date ? new Date(tx.date).toLocaleString() : '';
      return `<li class="row" style="justify-content: space-between; border-bottom: 1px dashed rgba(255,255,255,0.12); padding: .35rem 0;">
        <span>${desc ? desc : '<span class="muted">(bez opisu)</span>'}<span class="muted"> • ${date}</span></span>
        <strong ${color}>${amount}</strong>
      </li>`;
    }).join('');
  } catch (e) {
    console.error('Błąd ładowania transakcji:', e);
    if (txListEl) txListEl.innerHTML = `<li class="err">Nie udało się pobrać listy: ${e?.message ?? e}</li>`;
  }
}

async function addDemoTx() {
  try {
    const sign = Math.random() > 0.5 ? 1 : -1;
    const amount = (Math.random() * 100 + 10).toFixed(2);
    const payload = {
      category_id: null,
      type: sign > 0 ? 'income' : 'expense',
      amount: amount,
      description: sign > 0 ? 'Demo przychód' : 'Demo wydatek',
      date: new Date().toISOString(),
      is_planned: false
    };
    const res = await fetch('/api/transactions', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await res.json();
    await refreshBalance();
    await loadRecentTransactions();
  } catch (e) {
    alert('Nie udało się dodać transakcji demo: ' + (e?.message ?? e));
  }
}

// Event listeners with null checks
addDemoBtn?.addEventListener('click', addDemoTx);
refreshBalanceBtn?.addEventListener('click', refreshBalance);
refreshTxBtn?.addEventListener('click', loadRecentTransactions);

// Initial load
refreshBalance();
loadRecentTransactions();
