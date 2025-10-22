const incomeEl = document.getElementById('income');
const expenseEl = document.getElementById('expense');
const netEl = document.getElementById('net');
const addDemoBtn = document.getElementById('addDemoBtn');
const refreshBalanceBtn = document.getElementById('refreshBalanceBtn');
const txListEl = document.getElementById('txList');
const refreshTxBtn = document.getElementById('refreshTxBtn');
const seedBtn = document.getElementById('seedBtn');
const clearBtn = document.getElementById('clearBtn');
const monthlyBtn = document.getElementById('monthlyBtn');
const catReportBtn = document.getElementById('catReportBtn');
const monthlyOut = document.getElementById('monthlyOut');
const catReportOut = document.getElementById('catReportOut');

// New form/list elements
const catForm = document.getElementById('catForm');
const catName = document.getElementById('catName');
const catColor = document.getElementById('catColor');
const catList = document.getElementById('catList');

const txForm = document.getElementById('txForm');
const txType = document.getElementById('txType');
const txAmount = document.getElementById('txAmount');
const txCategory = document.getElementById('txCategory');
const txDesc = document.getElementById('txDesc');
const txDate = document.getElementById('txDate');
const txPlanned = document.getElementById('txPlanned');

const fForm = document.getElementById('filterForm');
const fType = document.getElementById('fType');
const fCategory = document.getElementById('fCategory');
const fFrom = document.getElementById('fFrom');
const fTo = document.getElementById('fTo');
const fQ = document.getElementById('fQ');
const fLimit = document.getElementById('fLimit');
const txFiltered = document.getElementById('txFiltered');

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
        <span>${desc ? desc : '<span class=\"muted\">(bez opisu)</span>'}<span class=\"muted\"> • ${date}</span></span>
        <strong ${color}>${amount}</strong>
      </li>`;
    }).join('');
  } catch (e) {
    console.error('Błąd ładowania transakcji:', e);
    if (txListEl) txListEl.innerHTML = `<li class="err">Nie udało się pobrać listy: ${e?.message ?? e}</li>`;
  }
}

// Categories
async function loadCategories() {
  try {
    const res = await fetch('/api/categories');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const cats = await res.json();
    if (txCategory) {
      txCategory.innerHTML = '<option value="">(Brak)</option>' + cats.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    }
    if (fCategory) {
      fCategory.innerHTML = '<option value="">(Wszystkie)</option>' + cats.map(c => `<option value="${c.id}">${c.name}</option>`).join('');
    }
    if (catList) {
      if (!cats.length) {
        catList.innerHTML = '<li class="muted">Brak kategorii</li>';
      } else {
        catList.innerHTML = cats.map(c => `<li class="row" style="justify-content: space-between; border-bottom: 1px dashed rgba(255,255,255,0.12); padding:.35rem 0;">
          <span><span style="display:inline-block; width:10px; height:10px; background:${c.color ?? '#666'}; border-radius:50%; margin-right:8px;"></span>${c.name}</span>
          <button data-del-cat="${c.id}" style="background:#ef4444; color:white; border-color:rgba(255,255,255,0.2)">Usuń</button>
        </li>`).join('');
        // attach delete listeners
        catList.querySelectorAll('button[data-del-cat]')?.forEach(btn => {
          btn.addEventListener('click', async (e) => {
            const id = btn.getAttribute('data-del-cat');
            if (!id) return;
            if (!confirm('Usunąć kategorię? Transakcje zostaną odłączone.')) return;
            const r = await fetch(`/api/categories/${id}`, { method: 'DELETE' });
            if (!r.ok && r.status !== 204) {
              alert('Nie udało się usunąć kategorii');
              return;
            }
            await loadCategories();
            await refreshFiltered();
          });
        });
      }
    }
  } catch (e) {
    console.error('Błąd ładowania kategorii', e);
  }
}

if (catForm) {
  catForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const name = catName?.value?.trim();
      const color = catColor?.value || null;
      if (!name) return;
      const res = await fetch('/api/categories', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, color })
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await res.json();
      catName.value = '';
      await loadCategories();
    } catch (e) {
      alert('Nie udało się dodać kategorii: ' + (e?.message ?? e));
    }
  });
}

// Transactions form
if (txForm) {
  // default txDate to now
  try { if (txDate) txDate.value = new Date().toISOString().slice(0,16); } catch {}
  txForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    try {
      const amount = parseFloat(txAmount?.value || '0');
      if (!amount || amount <= 0) { alert('Podaj poprawną kwotę'); return; }
      const rawDate = txDate?.value ? new Date(txDate.value) : new Date();
      const payload = {
        category_id: txCategory?.value ? parseInt(txCategory.value, 10) : null,
        type: txType?.value || 'expense',
        amount: amount.toFixed(2),
        description: txDesc?.value || null,
        date: rawDate.toISOString(),
        is_planned: !!txPlanned?.checked
      };
      const res = await fetch('/api/transactions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      await res.json();
      txAmount.value = '';
      txDesc.value = '';
      txPlanned.checked = false;
      await refreshBalance();
      await loadRecentTransactions();
      await refreshFiltered();
    } catch (e) {
      alert('Nie udało się dodać transakcji: ' + (e?.message ?? e));
    }
  });
}

// Filtered transactions list
async function refreshFiltered() {
  if (!txFiltered) return;
  try {
    const params = new URLSearchParams();
    if (fType?.value) params.set('type', fType.value);
    if (fCategory?.value) params.set('category_id', fCategory.value);
    if (fFrom?.value) params.set('date_from', new Date(fFrom.value + 'T00:00:00').toISOString());
    if (fTo?.value) params.set('date_to', new Date(fTo.value + 'T23:59:59').toISOString());
    if (fQ?.value) params.set('q', fQ.value);
    if (fLimit?.value) params.set('limit', fLimit.value);
    const res = await fetch('/api/transactions?' + params.toString());
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const items = await res.json();
    if (!items.length) {
      txFiltered.innerHTML = '<li class="muted">Brak wyników</li>';
      return;
    }
    txFiltered.innerHTML = items.map(tx => {
      const sign = tx.type === 'income' ? '+' : '-';
      const color = tx.type === 'income' ? 'style="color:#10b981"' : 'style="color:#ef4444"';
      const amount = `${sign}${tx.amount}`;
      const desc = tx.description ?? '';
      const date = tx.date ? new Date(tx.date).toLocaleString() : '';
      const cat = tx.category_id ? '' : '<span class="muted">(brak kategorii)</span>';
      return `<li class="row" style="justify-content: space-between; border-bottom: 1px dashed rgba(255,255,255,0.12); padding:.35rem 0;">
        <span>${desc || '(bez opisu)'}<span class="muted"> • ${date}</span> ${cat}</span>
        <span class="row" style="gap:.5rem;">
          <strong ${color}>${amount}</strong>
          <button data-del-tx="${tx.id}" title="Usuń" style="background:#ef4444; color:white; border-color:rgba(255,255,255,0.2)">Usuń</button>
        </span>
      </li>`;
    }).join('');
    // delete
    txFiltered.querySelectorAll('button[data-del-tx]')?.forEach(btn => {
      btn.addEventListener('click', async () => {
        const id = btn.getAttribute('data-del-tx');
        if (!id) return;
        if (!confirm('Usunąć transakcję?')) return;
        const r = await fetch(`/api/transactions/${id}`, { method: 'DELETE' });
        if (!r.ok && r.status !== 204) { alert('Nie udało się usunąć'); return; }
        await refreshBalance();
        await loadRecentTransactions();
        await refreshFiltered();
      });
    });
  } catch (e) {
    txFiltered.innerHTML = `<li class="err">Błąd pobierania: ${e?.message ?? e}</li>`;
  }
}

if (fForm) {
  fForm.addEventListener('submit', async (e) => {
    e.preventDefault();
    await refreshFiltered();
  });
}

// Reports
async function fetchMonthly() {
  try {
    const res = await fetch('/api/reports/monthly');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const d = await res.json();
    if (monthlyOut) {
      monthlyOut.innerHTML = `<div class="row" style="gap:1.25rem; flex-wrap:wrap;">
        <div><strong>Rok:</strong> ${d.year}</div>
        <div><strong>Miesiąc:</strong> ${d.month}</div>
        <div><strong>Przychody:</strong> ${d.income}</div>
        <div><strong>Wydatki:</strong> ${d.expense}</div>
        <div><strong>Saldo:</strong> <span class="${parseFloat(d.net)>=0?'ok':'err'}">${d.net}</span></div>
      </div>`;
    }
  } catch (e) {
    if (monthlyOut) monthlyOut.textContent = 'Błąd pobierania: ' + (e?.message ?? e);
  }
}

async function fetchByCategory() {
  try {
    const res = await fetch('/api/reports/by-category');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const items = await res.json();
    if (!catReportOut) return;
    if (!items.length) {
      catReportOut.innerHTML = '<li class="muted">Brak danych</li>';
      return;
    }
    catReportOut.innerHTML = items.map(r => {
      const net = (parseFloat(r.income) - parseFloat(r.expense)).toFixed(2);
      const color = parseFloat(net) >= 0 ? 'style="color:#10b981"' : 'style="color:#ef4444"';
      return `<li class="row" style="justify-content: space-between; border-bottom: 1px dashed rgba(255,255,255,0.12); padding:.35rem 0;">
        <span>${r.category_name ?? '(Brak kategorii)'}</span>
        <span><span class="muted">+${r.income}</span> / <span class="muted">-${r.expense}</span> → <strong ${color}>${net}</strong></span>
      </li>`;
    }).join('');
  } catch (e) {
    if (catReportOut) catReportOut.innerHTML = `<li class="err">Błąd: ${e?.message ?? e}</li>`;
  }
}

// Data actions
async function clearAll() {
  try {
    if (!confirm('Na pewno usunąć wszystkie dane (transakcje i kategorie)?')) return;
    const res = await fetch('/api/debug/clear', { method: 'POST' });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    await res.json();
    await refreshBalance();
    await loadRecentTransactions();
    await loadCategories();
    await refreshFiltered();
    if (monthlyOut) monthlyOut.textContent = '(brak danych)';
    if (catReportOut) catReportOut.innerHTML = '';
  } catch (e) {
    alert('Nie udało się wyczyścić danych: ' + (e?.message ?? e));
  }
}

// Event listeners with null checks
refreshBalanceBtn?.addEventListener('click', refreshBalance);
refreshTxBtn?.addEventListener('click', loadRecentTransactions);
clearBtn?.addEventListener('click', clearAll);
monthlyBtn?.addEventListener('click', fetchMonthly);
catReportBtn?.addEventListener('click', fetchByCategory);

// Initial load
refreshBalance();
loadRecentTransactions();
loadCategories();
refreshFiltered();
