const statusEl = document.getElementById('status');
const btn = document.getElementById('checkBtn');

async function checkPing() {
  try {
    statusEl.textContent = 'Sprawdzanie...';
    const res = await fetch('/api/ping');
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const data = await res.json();
    statusEl.textContent = `OK: ${JSON.stringify(data)}`;
    statusEl.classList.remove('err');
    statusEl.classList.add('ok');
  } catch (e) {
    statusEl.textContent = `Błąd: ${e?.message ?? e}`;
    statusEl.classList.remove('ok');
    statusEl.classList.add('err');
  }
}

btn.addEventListener('click', checkPing);

// auto-check on load
checkPing();
