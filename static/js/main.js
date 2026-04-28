// PlotPick — frontend interactions

// Password eye toggle
document.addEventListener('click', (e) => {
  const btn = e.target.closest('.password-toggle');
  if (!btn) return;
  const input = btn.parentElement.querySelector('input');
  if (!input) return;
  input.type = input.type === 'password' ? 'text' : 'password';
  btn.textContent = input.type === 'password' ? '\u{1F441}' : '\u{1F648}';
});

// Password strength meter
document.addEventListener('input', (e) => {
  if (!e.target.matches('[data-strength]')) return;
  const val = e.target.value;
  const bar = document.querySelector('[data-strength-bar]');
  const label = document.querySelector('[data-strength-label]');
  if (!bar || !label) return;

  let score = 0;
  if (val.length >= 8) score++;
  if (/[A-Z]/.test(val)) score++;
  if (/\d/.test(val)) score++;
  if (/[^A-Za-z0-9]/.test(val)) score++;

  const levels = ['weak', 'fair', 'good', 'strong'];
  const labels = ['Weak', 'Fair', 'Good', 'Strong'];
  bar.classList.remove('weak', 'fair', 'good', 'strong');
  if (val.length === 0) { label.textContent = ''; return; }
  const idx = Math.min(score, 4) - 1;
  bar.classList.add(levels[Math.max(0, idx)]);
  label.textContent = labels[Math.max(0, idx)];
});

// Star rating
document.querySelectorAll('.star-rating.interactive').forEach(el => {
  const stars = el.querySelectorAll('.star');
  const input = el.parentElement.querySelector('input[name="stars"]');
  const setVisual = (n) => {
    stars.forEach((s, i) => s.classList.toggle('on', i < n));
  };
  stars.forEach((s, i) => {
    s.addEventListener('mouseenter', () => setVisual(i + 1));
    s.addEventListener('click', () => {
      if (input) input.value = i + 1;
      setVisual(i + 1);
    });
  });
  el.addEventListener('mouseleave', () => {
    const current = input ? parseInt(input.value || '0', 10) : 0;
    setVisual(current);
  });
  const initial = input ? parseInt(input.value || '0', 10) : 0;
  setVisual(initial);
});

// Character counter
document.querySelectorAll('[data-counter]').forEach(ta => {
  const counter = document.querySelector(`[data-counter-for="${ta.id}"]`);
  const update = () => {
    if (counter) counter.textContent = `${ta.value.length}/${ta.maxLength}`;
  };
  ta.addEventListener('input', update);
  update();
});

// Seat selection
(function () {
  const form = document.querySelector('#seat-form');
  if (!form) return;

  const seats = form.querySelectorAll('.seat:not(.reserved)');
  const selectionList = document.querySelector('#selection-list');
  const subtotalEl = document.querySelector('#seat-subtotal');
  const submitBtn = document.querySelector('#seat-submit');

  const updateSummary = () => {
    const selected = Array.from(form.querySelectorAll('.seat.selected'));
    if (selectionList) {
      selectionList.innerHTML = selected.length === 0
        ? '<p class="muted">No seats selected.</p>'
        : selected.map(s => {
            const cat = s.dataset.category;
            const badge = { regular: 'Regular', premium: 'Premium', vip: 'VIP' }[cat] || 'Seat';
            return `<div class="seat-line"><span>${s.dataset.label}</span><small>${badge} · $${s.dataset.price}</small></div>`;
          }).join('');
    }
    const total = selected.reduce((a, s) => a + parseFloat(s.dataset.price || '0'), 0);
    if (subtotalEl) subtotalEl.textContent = `$${total.toFixed(2)}`;
    if (submitBtn) submitBtn.disabled = selected.length === 0;
  };

  seats.forEach(btn => {
    btn.addEventListener('click', (e) => {
      e.preventDefault();
      btn.classList.toggle('selected');
      const input = form.querySelector(`input[value="${btn.dataset.seatId}"]`);
      if (input) input.checked = btn.classList.contains('selected');
      updateSummary();
    });
  });

  updateSummary();
})();

// Auto-hide toasts
setTimeout(() => {
  document.querySelectorAll('.toast.auto-dismiss').forEach(el => {
    el.style.transition = 'opacity .4s';
    el.style.opacity = '0';
    setTimeout(() => el.remove(), 500);
  });
}, 4500);
