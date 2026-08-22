const COLORS = {
  usd_brl: '#2458e6',
  cdi: '#7656d8',
  selic_monthly: '#f07a31',
  ipca: '#158264',
};

const TITLES = {
  usd_brl: 'USD / BRL exchange rate',
  cdi: 'CDI daily benchmark',
  selic_monthly: 'Monthly accumulated Selic',
  ipca: 'Monthly IPCA inflation',
};

const state = { data: null, series: 'usd_brl', range: 365, points: [] };

const formatDate = (value, options = { day: '2-digit', month: 'short', year: 'numeric' }) =>
  new Intl.DateTimeFormat('en-US', options).format(new Date(`${value}T12:00:00Z`));

const formatValue = (slug, value) => {
  if (slug === 'usd_brl') return `R$ ${value.toFixed(4)}`;
  if (slug === 'cdi') return `${value.toFixed(2)}% / day`;
  return `${value.toFixed(2)}%`;
};

const setKpi = (slug, valueId, deltaId) => {
  const records = state.data.series[slug].records;
  const latest = records.at(-1);
  const previous = records.at(-2);
  const delta = latest.value - previous.value;
  document.getElementById(valueId).textContent = formatValue(slug, latest.value);
  document.getElementById(deltaId).textContent = `${delta >= 0 ? '↑' : '↓'} ${Math.abs(delta).toFixed(slug === 'usd_brl' ? 4 : 2)} · ${formatDate(latest.date)}`;
};

function filteredRecords() {
  const records = state.data.series[state.series].records;
  if (state.range === 'all') return records;
  const cutoff = new Date(records.at(-1).date);
  cutoff.setUTCDate(cutoff.getUTCDate() - Number(state.range));
  return records.filter((record) => new Date(record.date) >= cutoff);
}

function renderChart() {
  const canvas = document.getElementById('series-chart');
  const wrap = canvas.parentElement;
  const ratio = window.devicePixelRatio || 1;
  const width = wrap.clientWidth;
  const height = wrap.clientHeight;
  canvas.width = width * ratio;
  canvas.height = height * ratio;
  const ctx = canvas.getContext('2d');
  ctx.scale(ratio, ratio);

  const records = filteredRecords();
  const pad = { top: 26, right: 22, bottom: 42, left: 58 };
  const chartW = width - pad.left - pad.right;
  const chartH = height - pad.top - pad.bottom;
  const values = records.map((record) => record.value);
  const rawMin = Math.min(...values);
  const rawMax = Math.max(...values);
  const spread = rawMax - rawMin || 1;
  const min = rawMin - spread * 0.12;
  const max = rawMax + spread * 0.12;
  const x = (index) => pad.left + (index / Math.max(records.length - 1, 1)) * chartW;
  const y = (value) => pad.top + (1 - (value - min) / (max - min)) * chartH;

  ctx.clearRect(0, 0, width, height);
  ctx.font = '10px DM Mono, monospace';
  ctx.fillStyle = '#858681';
  ctx.strokeStyle = 'rgba(17,19,21,.09)';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i += 1) {
    const py = pad.top + (chartH / 4) * i;
    const value = max - ((max - min) / 4) * i;
    ctx.beginPath(); ctx.moveTo(pad.left, py); ctx.lineTo(width - pad.right, py); ctx.stroke();
    ctx.fillText(value.toFixed(state.series === 'usd_brl' ? 2 : 2), 2, py + 4);
  }

  const gradient = ctx.createLinearGradient(0, pad.top, 0, height - pad.bottom);
  gradient.addColorStop(0, `${COLORS[state.series]}33`);
  gradient.addColorStop(1, `${COLORS[state.series]}00`);
  ctx.beginPath();
  records.forEach((record, index) => {
    const px = x(index); const py = y(record.value);
    if (index === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
  });
  ctx.lineTo(x(records.length - 1), height - pad.bottom);
  ctx.lineTo(x(0), height - pad.bottom);
  ctx.closePath(); ctx.fillStyle = gradient; ctx.fill();

  ctx.beginPath();
  records.forEach((record, index) => {
    const px = x(index); const py = y(record.value);
    if (index === 0) ctx.moveTo(px, py); else ctx.lineTo(px, py);
  });
  ctx.strokeStyle = COLORS[state.series]; ctx.lineWidth = 2.5; ctx.stroke();

  const ticks = Math.min(5, records.length);
  for (let i = 0; i < ticks; i += 1) {
    const index = Math.round((records.length - 1) * (i / Math.max(ticks - 1, 1)));
    ctx.fillStyle = '#858681';
    ctx.fillText(formatDate(records[index].date, { month: 'short', year: '2-digit' }), x(index) - 15, height - 15);
  }

  state.points = records.map((record, index) => ({ x: x(index), y: y(record.value), record }));
  document.getElementById('chart-title').textContent = TITLES[state.series];
  document.getElementById('chart-period').textContent = `${formatDate(records[0].date)} — ${formatDate(records.at(-1).date)}`;
}

function showTooltip(event) {
  if (!state.points.length) return;
  const canvas = event.currentTarget;
  const rect = canvas.getBoundingClientRect();
  const pointerX = (event.touches?.[0]?.clientX ?? event.clientX) - rect.left;
  const point = state.points.reduce((best, current) =>
    Math.abs(current.x - pointerX) < Math.abs(best.x - pointerX) ? current : best
  );
  const tooltip = document.getElementById('chart-tooltip');
  tooltip.hidden = false;
  tooltip.style.left = `${point.x}px`;
  tooltip.style.top = `${point.y}px`;
  tooltip.innerHTML = `<strong>${formatValue(state.series, point.record.value)}</strong><br>${formatDate(point.record.date)}`;
}

function renderRealRate() {
  const selic = new Map(state.data.series.selic_monthly.records.map((r) => [r.date, r.value]));
  const comparable = state.data.series.ipca.records
    .filter((record) => selic.has(record.date))
    .map((record) => ({ date: record.date, value: Number((selic.get(record.date) - record.value).toFixed(2)) }))
    .slice(-12);
  const latest = comparable.at(-1);
  document.getElementById('real-rate').textContent = `${latest.value.toFixed(2)}%`;
  const bars = document.getElementById('real-rate-bars');
  const max = Math.max(...comparable.map((item) => Math.abs(item.value)), 1);
  bars.innerHTML = comparable.map((item) =>
    `<div class="mini-bar" style="height:${Math.max(8, Math.abs(item.value) / max * 100)}%"><span>${formatDate(item.date, {month:'short'})} · ${item.value.toFixed(2)}%</span></div>`
  ).join('');
}

async function init() {
  const response = await fetch('data/financial-series.json');
  if (!response.ok) throw new Error('Unable to load dashboard data');
  state.data = await response.json();
  document.getElementById('freshness').textContent = new Intl.DateTimeFormat('en-US', { dateStyle: 'medium', timeStyle: 'short' }).format(new Date(state.data.generated_at));
  setKpi('usd_brl', 'kpi-usd', 'delta-usd');
  setKpi('cdi', 'kpi-cdi', 'delta-cdi');
  setKpi('selic_monthly', 'kpi-selic', 'delta-selic');
  setKpi('ipca', 'kpi-ipca', 'delta-ipca');
  renderRealRate(); renderChart();
}

document.querySelectorAll('[data-series]').forEach((button) => button.addEventListener('click', () => {
  state.series = button.dataset.series;
  document.querySelectorAll('[data-series]').forEach((item) => item.setAttribute('aria-selected', String(item === button)));
  renderChart();
}));
document.querySelectorAll('[data-range]').forEach((button) => button.addEventListener('click', () => {
  state.range = button.dataset.range;
  document.querySelectorAll('[data-range]').forEach((item) => item.classList.toggle('active', item === button));
  renderChart();
}));
const canvas = document.getElementById('series-chart');
canvas.addEventListener('mousemove', showTooltip);
canvas.addEventListener('touchmove', showTooltip, { passive: true });
canvas.addEventListener('mouseleave', () => { document.getElementById('chart-tooltip').hidden = true; });
window.addEventListener('resize', () => { if (state.data) renderChart(); });

init().catch((error) => {
  document.getElementById('freshness').textContent = 'Data temporarily unavailable';
  console.error(error);
});
