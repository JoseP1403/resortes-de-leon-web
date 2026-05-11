
const MONTHS = ['May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic', 'Ene', 'Feb', 'Mar', 'Abr', 'May'];

const DATA = {
  totals: [257.2, 16993.88, 64494.73, 51312.08, 50145.12, 26894.56, 28729.46, 195085.06, 137408.91, 190801.8, 135104.12, 258641.52, 29133.91],
  recesa: [0.0, 0.0, 0.0, 0.0, 700.0, 4910.0, 4357.12, 0.0, 0.0, 10115.0, 40038.1, 121814.7, 2920.32],
  redelsa: [257.2, 16993.88, 64494.73, 51312.08, 49445.12, 21984.56, 24372.34, 195085.06, 137408.91, 180686.8, 95066.02, 136826.82, 26213.59],
};

const PRODUCTS = [
{ name: 'PERNO S/MUESTRA', val: 283424.56 },
{ name: 'BARRA LISA F1554/GR55 25MM X 3.55 MTS', val: 45865.17 },
{ name: 'TORNILLO LAMINA 14 X 1 1/2', val: 30939.6 },
{ name: 'TORNILLO HEX. A325 1 X 3 1/2', val: 30906.08 },
{ name: 'TUERCA HEX. A325 5/8', val: 26584.84 },
{ name: 'TUERCA HEX. A325 1.3/8', val: 26250.0 },
{ name: 'BARRA LISA F1554/GR105 1" X 6 MTS', val: 24840.0 }
];

const YELLOW = '#F5C400';
const BLACK  = '#1a1a1a';
const GRAY   = 'rgba(128,128,128,0.1)';

function fmtK(v) {
  return 'Q' + (v >= 1000 ? Math.round(v / 1000) + 'k' : v);
}

function initLine() {
  new Chart(document.getElementById('lineChart'), {
    type: 'line',
    data: {
      labels: MONTHS,
      datasets: [{
        label: 'Total ventas',
        data: DATA.totals,
        borderColor: YELLOW,
        backgroundColor: 'rgba(245,196,0,0.10)',
        borderWidth: 2,
        pointBackgroundColor: YELLOW,
        pointRadius: 3,
        fill: true,
        tension: 0.35,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
    },
  });
}

function initBar() {
  new Chart(document.getElementById('barChart'), {
    type: 'bar',
    data: {
      labels: MONTHS,
      datasets: [
        { label: 'RECESA', data: DATA.recesa, backgroundColor: BLACK },
        { label: 'REDELSA', data: DATA.redelsa, backgroundColor: YELLOW },
      ],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
    },
  });
}

function initDonut() {

  const totalRecesa = DATA.recesa.reduce((a,b)=>a+b,0);
  const totalRedelsa = DATA.redelsa.reduce((a,b)=>a+b,0);

  new Chart(document.getElementById('donutChart'), {
    type: 'doughnut',
    data: {
      labels: ['RECESA', 'REDELSA'],
      datasets: [{
        data: [totalRecesa, totalRedelsa],
        backgroundColor: [BLACK, YELLOW],
        borderWidth: 0,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: { display: false }
      },
    },
  });
}

function renderProducts() {
  const container = document.getElementById('products');
  const maxVal = PRODUCTS[0].val;

  PRODUCTS.forEach(p => {
    const pct = Math.round((p.val / maxVal) * 100);

    const item = document.createElement('div');
    item.className = 'prod-item';

    item.innerHTML = `
      <div class="prod-name">${p.name}</div>
      <div class="prod-bar-wrap">
        <div class="prod-bar" style="width:${pct}%"></div>
      </div>
      <div class="prod-val">Q${Math.round(p.val / 1000)}k</div>
    `;

    container.appendChild(item);
  });
}

document.addEventListener('DOMContentLoaded', () => {
  initLine();
  initBar();
  initDonut();
  renderProducts();
});
