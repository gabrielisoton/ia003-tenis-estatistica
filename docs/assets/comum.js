/* Funções compartilhadas pelas páginas do site.
   Os números vêm de docs/data/*.json, gerados por scripts/05_exportar_resultados.py.
   O site só desenha: nenhum teste estatístico é recalculado aqui (exceto a simulação didática). */

const CORES = {
  pop: "#6250d6", amostra: "#c98500", top: "#d55181", demais: "#898781",
  neutra: "#898781", erro: "#d03b3b", ok: "#0ca30c",
  sup: { "Dura": "#2a78d6", "Saibro": "#eb6834", "Grama": "#1baf7a", "Carpete": "#898781" },
};

// Trabalho da disciplina (avaliado)
const PAGINAS = [
  ["index.html", "Aquecimento", "Base e amostra"],
  ["populacao.html", "1º set", "População"],
  ["amostra.html", "2º set", "Amostra"],
  ["inferencia.html", "3º set", "Inferência"],
];
// Extras para fãs de tênis (fora da avaliação)
const EXTRAS = [
  ["explorar.html", "Tie-break", "Explorar"],
  ["jogadores.html", "Vestiário", "Jogadores"],
];

/* ---------------- dados ---------------- */
const _cache = {};
async function carregar(nome) {
  if (!_cache[nome]) _cache[nome] = fetch(`data/${nome}.json`).then(r => {
    if (!r.ok) throw new Error(`Falha ao carregar ${nome}.json`);
    return r.json();
  });
  return _cache[nome];
}

/* ---------------- formatação pt-BR ---------------- */
function br(x, casas = 2) {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return Number(x).toLocaleString("pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
}
const pct = (x, casas = 1) => (x === null || x === undefined) ? "—" : br(100 * x, casas) + "%";
const tx = s => String(s).replace(/,/g, "{,}");  // vírgula decimal no KaTeX
const vp = p => p < 1e-4 ? "< 0,0001" : br(p, 4);

/* ---------------- navegação ---------------- */
function montarNav() {
  const atual = location.pathname.split("/").pop() || "index.html";
  const nav = document.createElement("nav");
  nav.className = "nav";
  nav.innerHTML = `<div class="nav-dentro">
    <a class="marca" href="index.html"><span class="bola"></span> Estatística no Tênis</a>
    ${PAGINAS.map(([href, set, nome]) =>
      `<a class="item ${href === atual ? "ativo" : ""}" href="${href}"><small>${set}</small>${nome}</a>`).join("")}
    ${EXTRAS.length ? `<span class="nav-sep" title="Fora da avaliação da disciplina">Extras</span>` +
      EXTRAS.map(([href, set, nome]) =>
        `<a class="item extra ${href === atual ? "ativo" : ""}" href="${href}"><small>${set}</small>${nome}</a>`).join("") : ""}
  </div>`;
  document.body.prepend(nav);
}

/* ---------------- quadra em SVG (fundo do hero) ---------------- */
function svgQuadra() {
  // proporções reais: 23,77 m × 10,97 m (duplas); simples 8,23 m; linha de saque a 6,40 m da rede
  return `<svg class="quadra" viewBox="0 0 1188 549" preserveAspectRatio="xMidYMid slice" aria-hidden="true">
    <g fill="none" stroke="#fff" stroke-width="5">
      <rect x="20" y="20" width="1148" height="509"/>
      <line x1="20" y1="83" x2="1168" y2="83"/><line x1="20" y1="466" x2="1168" y2="466"/>
      <line x1="285" y1="83" x2="285" y2="466"/><line x1="903" y1="83" x2="903" y2="466"/>
      <line x1="285" y1="274.5" x2="903" y2="274.5"/>
      <line x1="594" y1="10" x2="594" y2="539" stroke-dasharray="4 6" stroke-width="7"/>
      <line x1="20" y1="274.5" x2="40" y2="274.5"/><line x1="1148" y1="274.5" x2="1168" y2="274.5"/>
    </g></svg>`;
}

/* ---------------- componentes ---------------- */
function placar(el, itens) {
  el.classList.add("placar");
  el.innerHTML = itens.map(i => `<div class="cel"><div class="rot">${i.rot}</div>
    <div class="num">${i.num}</div>${i.sub ? `<div class="sub">${i.sub}</div>` : ""}</div>`).join("");
}

function comoLer(texto) {
  return `<details class="como-ler"><summary>📖 Como ler</summary><div>${texto}</div></details>`;
}

function katexEm(el, tex, display = true) {
  if (window.katex) katex.render(tex, el, { displayMode: display, throwOnError: false });
  else el.textContent = tex;
}

/* ---------------- Plotly: tema ---------------- */
const PLOTLY_CONFIG = { displayModeBar: false, responsive: true, locale: "pt-BR" };
function layoutBase(extra = {}) {
  return Object.assign({
    font: { family: "Barlow, system-ui, sans-serif", size: 14, color: "#14211b" },
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
    separators: ",.", margin: { l: 56, r: 18, t: 46, b: 52 },
    hoverlabel: { font: { family: "Barlow", size: 13 } },
    legend: { orientation: "h", y: 1.02, yanchor: "bottom", x: 0 },
    xaxis: { showgrid: false, zeroline: false, linecolor: "#c3c2b7", automargin: true },
    yaxis: { gridcolor: "rgba(137,135,129,.22)", zeroline: false, automargin: true },
    bargap: 0.25, barcornerradius: 4,
  }, extra);
}
function plot(el, dados, layout = {}) {
  return Plotly.react(el, dados, layoutBase(layout), PLOTLY_CONFIG);
}

/* Gráfico "Hawk-Eye": IC da amostra × H0 × parâmetro real, com selo IN/OUT */
function hawkeye(el, { est, li, ls, h0, param, fmt, proporcao = false }) {
  const xs = [li, ls, h0, param];
  const lo = Math.min(...xs), hi = Math.max(...xs), pad = (hi - lo) * 0.18;
  const dados = [
    { x: [li, ls], y: [0, 0], mode: "lines", line: { color: CORES.amostra, width: 14 }, name: "IC 95% (amostra)",
      hovertemplate: "%{x}<extra>limite do IC</extra>" },
    { x: [est], y: [0], mode: "markers", name: "estimativa (amostra)",
      marker: { color: "#dcf04a", size: 22, line: { color: "#14211b", width: 2 } },
      hovertemplate: `estimativa: ${fmt(est)}<extra></extra>` },
  ];
  const linhas = [
    { type: "line", x0: h0, x1: h0, y0: -1, y1: 1, line: { color: CORES.neutra, width: 2, dash: "dash" } },
    { type: "line", x0: param, x1: param, y0: -1, y1: 1, line: { color: CORES.pop, width: 3 } },
  ];
  const notas = [
    { x: h0, y: -1, yanchor: "top", text: `H₀ ${fmt(h0)}`, showarrow: false, font: { color: "#4b5650" } },
    { x: param, y: 1, yanchor: "bottom", text: `população ${fmt(param)}`, showarrow: false, font: { color: CORES.pop } },
  ];
  return plot(el, dados, {
    height: 210, shapes: linhas, annotations: notas, showlegend: true, margin: { l: 20, r: 20, t: 40, b: 40 },
    xaxis: { range: [lo - pad, hi + pad], tickformat: proporcao ? ".0%" : null, showgrid: false, zeroline: false },
    yaxis: { range: [-1.6, 1.6], visible: false },
  });
}
function seloHawkeye(contem) {
  return contem ? `<span class="selo in">● IN — o IC contém o valor real</span>`
                : `<span class="selo out">● OUT — o IC não contém o valor real</span>`;
}

function rodape() {
  const f = document.createElement("footer");
  f.innerHTML = `Atividade avaliativa final · IA003 Probabilidade e Estatística para IA · Especialização em IA · UFRGS<br>
    Dados: <a href="https://github.com/Tennismylife/TML-Database">TML-Database (Tennismylife)</a>, ATP 2000–2025, uso educacional.`;
  document.body.append(f);
}

document.addEventListener("DOMContentLoaded", () => { montarNav(); rodape(); });
