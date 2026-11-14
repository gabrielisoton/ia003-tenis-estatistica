/* Funções compartilhadas pelos sites (trabalho da IA003 e projeto público). Fica em nucleo/web/ e é copiada
   para o assets/ de cada site por ferramentas/montar_site.py.
   Os números vêm do data/*.json de cada site, gerados pelos scripts exportar_site.py.
   O site só desenha: nenhum teste estatístico é recalculado aqui (exceto a simulação didática).
   A barra de navegação de cada site é declarada em assets/site.js (window.SITE). */

const CORES = {
  pop: "#6250d6", amostra: "#c98500", top: "#d55181", demais: "#898781",
  neutra: "#898781", erro: "#d03b3b", ok: "#0ca30c",
  sup: { "Dura": "#2a78d6", "Saibro": "#eb6834", "Grama": "#1baf7a", "Carpete": "#898781",
         "Hard": "#2a78d6", "Clay": "#eb6834", "Grass": "#1baf7a", "Carpet": "#898781" },
};

// navegação: cada site define window.SITE em assets/site.js
//   { marca, paginas: [[href, sobretítulo, nome]], extras: { rotulo, dica, itens: [[href, sobretítulo, nome]] }, rodape,
//     idiomas }  — com idiomas: true, cada texto pode ser [pt, en] e aparece o seletor PT/EN na barra
const SITE = window.SITE || { marca: "Estatística no Tênis", paginas: [], extras: null, rodape: "" };

/* ---------------- idioma ----------------
   Só o site que declara SITE.idiomas troca de idioma (o trabalho da IA003 fica sempre em português, mesmo que o
   visitante tenha escolhido inglês no projeto, que está no mesmo domínio).
   - texto fixo no HTML: <span data-l="pt">…</span><span data-l="en">…</span> (o CSS esconde o outro idioma);
     atributos: data-en-title, data-en-placeholder, data-en-aria-label; <title data-en="…">
   - texto montado no JS: T("português", "English")
   - rótulos que vêm dos dados (superfícies, critérios…): tr(rótulo), com o dicionário data/en.json
     (gerado de nucleo/idiomas.py, o mesmo que o app Streamlit usa) */
const IDIOMA = (() => {
  if (!SITE.idiomas) return "pt";
  const q = new URLSearchParams(location.search).get("lang");
  try {
    if (q === "en" || q === "pt") localStorage.setItem("lingua", q);
    return (q || localStorage.getItem("lingua")) === "en" ? "en" : "pt";
  } catch (e) { return q === "en" ? "en" : "pt"; }
})();
const EM_INGLES = IDIOMA === "en";
document.documentElement.dataset.lang = IDIOMA;
if (EM_INGLES) document.documentElement.lang = "en";
const T = (pt, en) => EM_INGLES ? en : pt;
const L = x => Array.isArray(x) ? T(x[0], x[1]) : x;          // texto do site.js: "pt" ou ["pt", "en"]
let _EN = {};
const tr = s => EM_INGLES && typeof s === "string" ? (_EN[s] ?? s) : s;
const ordinal = n => !EM_INGLES ? `${n}º`
  : n + ((n % 100 >= 11 && n % 100 <= 13) ? "th" : ({ 1: "st", 2: "nd", 3: "rd" }[n % 10] || "th"));
function trocarIdioma(l) {
  try { localStorage.setItem("lingua", l); } catch (e) { /* sem armazenamento: vale só a URL */ }
  const u = new URL(location.href);
  u.searchParams.set("lang", l);
  location.replace(u);
}
function aplicarIdiomaFixo() {
  if (!EM_INGLES) return;
  const t = document.querySelector("title[data-en]"); if (t) document.title = t.dataset.en;
  for (const a of ["title", "placeholder", "aria-label"])
    document.querySelectorAll(`[data-en-${a}]`).forEach(el => el.setAttribute(a, el.getAttribute(`data-en-${a}`)));
}

/* ---------------- dados ---------------- */
const _cache = {};
const _json = nome => fetch(`data/${nome}.json`).then(r => {
  if (!r.ok) throw new Error(`Falha ao carregar ${nome}.json`);
  return r.json();
});
// em inglês, o dicionário dos rótulos chega antes de qualquer dado (tr() já funciona quando a página desenha)
const _dicionario = EM_INGLES ? _json("en").then(d => { _EN = d; }).catch(() => {}) : Promise.resolve();
async function carregar(nome) {
  if (!_cache[nome]) _cache[nome] = _dicionario.then(() => _json(nome));
  return _cache[nome];
}

/* ---------------- formatação (pt-BR, ou en-US no site em inglês) ---------------- */
function br(x, casas = 2) {
  if (x === null || x === undefined || Number.isNaN(x)) return "—";
  return Number(x).toLocaleString(EM_INGLES ? "en-US" : "pt-BR", { minimumFractionDigits: casas, maximumFractionDigits: casas });
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
    <a class="marca" href="index.html"><span class="bola"></span> ${L(SITE.marca)}</a>
    ${SITE.paginas.map(([href, set, nome]) =>
      `<a class="item ${href === atual ? "ativo" : ""}" href="${href}"><small>${L(set)}</small>${L(nome)}</a>`).join("")}
    ${SITE.extras ? `<span class="nav-sep" title="${L(SITE.extras.dica) || ""}">${L(SITE.extras.rotulo)}</span>` +
      SITE.extras.itens.map(([href, set, nome]) =>
        `<a class="item extra ${href === atual ? "ativo" : ""}" href="${href}"><small>${L(set)}</small>${L(nome)}</a>`).join("") : ""}
    ${SITE.idiomas ? `<span class="idioma" role="group" aria-label="Idioma · Language">${[["pt", "Português"], ["en", "English"]]
      .map(([l, n]) => `<button type="button" data-idioma="${l}" class="${l === IDIOMA ? "on" : ""}" title="${n}" lang="${l}"
        aria-pressed="${l === IDIOMA}">${l.toUpperCase()}</button>`).join("")}</span>` : ""}
  </div>`;
  nav.querySelectorAll("[data-idioma]").forEach(b => b.addEventListener("click", () => {
    if (b.dataset.idioma !== IDIOMA) trocarIdioma(b.dataset.idioma); }));
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
  return `<details class="como-ler"><summary>📖 ${T("Como ler", "How to read")}</summary><div>${texto}</div></details>`;
}

function katexEm(el, tex, display = true) {
  if (window.katex) katex.render(tex, el, { displayMode: display, throwOnError: false });
  else el.textContent = tex;
}

/* ---------------- Plotly: tema ---------------- */
const PLOTLY_CONFIG = { displayModeBar: false, responsive: true, locale: EM_INGLES ? "en" : "pt-BR" };
function layoutBase(extra = {}) {
  return Object.assign({
    font: { family: "Barlow, system-ui, sans-serif", size: 14, color: "#14211b" },
    paper_bgcolor: "rgba(0,0,0,0)", plot_bgcolor: "rgba(0,0,0,0)",
    separators: EM_INGLES ? ".," : ",.", margin: { l: 56, r: 18, t: 46, b: 52 },
    hoverlabel: { font: { family: "Barlow", size: 13 } },
    legend: { orientation: "h", y: 1.02, yanchor: "bottom", x: 0 },
    xaxis: { showgrid: false, zeroline: false, linecolor: "#c3c2b7", automargin: true },
    yaxis: { gridcolor: "rgba(137,135,129,.22)", zeroline: false, automargin: true },
    bargap: 0.25, barcornerradius: 4,
  }, extra);
}
function plot(el, dados, layout = {}) {
  // com responsive: true o Plotly não estica a caixa do gráfico até a altura pedida: ela fica no min-height do CSS e
  // o fim do gráfico (eixo x) vazava por baixo do texto seguinte. A caixa passa a ter a altura do próprio gráfico.
  if (layout.height) (typeof el === "string" ? document.getElementById(el) : el).style.minHeight = layout.height + "px";
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
  f.innerHTML = `${SITE.rodape ? L(SITE.rodape) + "<br>" : ""}
    ${T("Dados", "Data")}: <a href="https://github.com/Tennismylife/TML-Database">TML-Database (Tennismylife)</a>, ATP 2000–2025, ${T("uso educacional", "educational use")}.`;
  document.body.append(f);
}

document.addEventListener("DOMContentLoaded", () => { aplicarIdiomaFixo(); montarNav(); rodape(); });
