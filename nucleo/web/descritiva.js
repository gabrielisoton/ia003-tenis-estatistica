/* Painel descritivo compartilhado pelo 1º set (população) e 2º set (amostra).
   Os dados chegam em colunas compactas (data/populacao.json e, na disciplina, amostra.json) e os
   filtros são aplicados no navegador. As medidas seguem as mesmas definições do pandas.
   Textos com T("pt", "en"): no site do projeto seguem o idioma escolhido; no da disciplina ficam em português. */

const QUALI = {
  sup: T("Superfície", "Surface"), niv: T("Nível do torneio", "Tournament level"), bo: T("Formato (sets)", "Format (sets)"),
  mao: T("Mão do vencedor", "Winner's playing hand"),
  fav: T("Favorito (melhor ranking) venceu?", "Did the favourite (better ranked) win?"),
  dec: T("Foi ao set decisivo?", "Did it go to a deciding set?"),
};
const QUANT = {
  min: { nome: T("Duração (minutos)", "Duration (minutes)"), largura: 5 },
  ace: { nome: T("Aces na partida (2 jogadores)", "Aces in the match (both players)"), largura: 1 },
  df: { nome: T("Duplas faltas na partida", "Double faults in the match"), largura: 1 },
  idade: { nome: T("Idade do vencedor (anos)", "Winner's age (years)"), largura: 1 },
  alt: { nome: T("Altura do vencedor (cm)", "Winner's height (cm)"), largura: 1 },
  sets: { nome: T("Sets jogados", "Sets played"), largura: 1 },
  dif: { nome: T("Diferença de ranking entre os jogadores", "Ranking gap between the players"), largura: null },
};
const NOTAS = {
  min: T("Faixas de 5 minutos. A cauda à direita vem das partidas melhor de 5 e das maratonas: Isner × Mahut, em Wimbledon 2010, durou 665 minutos.",
    "5-minute bins. The right tail comes from best-of-5 matches and marathons: Isner vs Mahut, at Wimbledon 2010, lasted 665 minutes."),
  ace: T("Faixas de 1 ace, porque é uma contagem inteira. A curva sobe até cerca de 6–9 aces e depois desce devagar: poucas partidas de grandes sacadores, ou de 5 sets, puxam a média para cima da mediana.",
    "1-ace bins, since it is a whole-number count. The curve rises to about 6–9 aces and then falls slowly: a few matches with big servers, or five-setters, pull the mean above the median."),
  df: T("Contagem inteira. A maioria das partidas tem poucas duplas faltas, e a cauda longa vem de jogos longos ou de dias ruins no saque.",
    "Whole-number count. Most matches have few double faults; the long tail comes from long matches or bad serving days."),
  idade: T("A idade é contínua (anos com decimais), agrupada em faixas de 1 ano.", "Age is continuous (years with decimals), grouped in 1-year bins."),
  alt: T("Os picos em 180, 183, 185, 188, 191 e 193 cm são reais. As alturas são registradas em pés e polegadas e depois convertidas: 6'0\" = 183 cm, 6'1\" = 185 cm, 6'2\" = 188 cm. Por isso aparece um pico a cada 2,5 cm, que é uma polegada.",
    "The peaks at 180, 183, 185, 188, 191 and 193 cm are real. Heights are recorded in feet and inches and then converted: 6'0\" = 183 cm, 6'1\" = 185 cm, 6'2\" = 188 cm. That is why there is a peak every 2.5 cm, which is one inch."),
  sets: T("Melhor de 3 termina em 2 ou 3 sets; melhor de 5, em 3, 4 ou 5.", "Best of 3 ends in 2 or 3 sets; best of 5 in 3, 4 or 5."),
};
const FAIXAS_RK = [[1, 5], [6, 10], [11, 25], [26, 50], [51, 100], [101, 200], [201, 1e9]];

/* ---------------- estatística descritiva (mesmas definições do pandas) ---------------- */
function valoresDe(d, idx, col) {
  const out = [];
  for (const i of idx) { const v = d[col][i]; if (v !== null && v !== undefined) out.push(v); }
  return out;
}
function quantil(ordenado, q) {           // interpolação linear (padrão do pandas)
  const pos = (ordenado.length - 1) * q, lo = Math.floor(pos), hi = Math.ceil(pos);
  return ordenado[lo] + (ordenado[hi] - ordenado[lo]) * (pos - lo);
}
function resumo(v) {
  const n = v.length;
  if (!n) return { n: 0 };
  const s = [...v].sort((a, b) => a - b);
  const media = v.reduce((a, b) => a + b, 0) / n;
  let m2 = 0, m3 = 0;
  for (const x of v) { const d = x - media; m2 += d * d; m3 += d * d * d; }
  const dp = Math.sqrt(m2 / (n - 1));
  const g1 = (m3 / n) / Math.pow(m2 / n, 1.5);
  const assim = n > 2 ? g1 * Math.sqrt(n * (n - 1)) / (n - 2) : NaN;  // = pandas .skew()
  return { n, media, mediana: quantil(s, .5), dp, q1: quantil(s, .25), q3: quantil(s, .75),
           min: s[0], max: s[n - 1], assim, q995: quantil(s, .995) };
}

/* ---------------- categorias ---------------- */
function cats(col, meta) {
  switch (col) {
    case "sup": return meta.codigos.sup.map((r, i) => [i, tr(r)]);
    case "niv": return meta.codigos.niv.map((r, i) => [i, tr(r)]);
    case "rod": return meta.codigos.rod.map((r, i) => [i, r]).filter(([, r]) => r !== "3rd/4th").map(([i, r]) => [i, tr(r)]);
    case "mao": return [[0, tr("Destro")], [1, tr("Canhoto")]];
    case "bo": return [[3, tr("Melhor de 3")], [5, tr("Melhor de 5")]];
    case "fav": case "dec": return [[1, tr("Sim")], [0, tr("Não")]];
  }
}
function frequencias(d, idx, col, meta) {
  const cont = new Map();
  let tot = 0;
  for (const i of idx) { const v = d[col][i]; if (v === null || v === undefined) continue; cont.set(v, (cont.get(v) || 0) + 1); tot++; }
  return cats(col, meta).map(([v, r]) => ({ rot: r, n: cont.get(v) || 0, p: tot ? (cont.get(v) || 0) / tot : 0 }));
}
function faixasRanking(d, idx) {
  const n = FAIXAS_RK.map(() => 0); let tot = 0;
  for (const i of idx) {
    const v = d.dif[i]; if (v === null) continue;
    const k = FAIXAS_RK.findIndex(([a, b]) => v >= a && v <= b); n[k]++; tot++;
  }
  return FAIXAS_RK.map(([a, b], k) => ({ rot: b > 1e8 ? `${a}+` : `${a}–${b}`, n: n[k], p: tot ? n[k] / tot : 0 }));
}

/* ---------------- filtros ---------------- */
function estadoFiltros(meta, anos) {
  return { sup: new Set([0, 1, 2, 3]), niv: new Set([0, 1, 2, 3, 4]), a0: anos[0], a1: anos[1], top: 0 };
}
function aplicarFiltros(d, f) {
  const idx = [];
  for (let i = 0; i < d.ano.length; i++) {
    if (!f.sup.has(d.sup[i]) || !f.niv.has(d.niv[i]) || d.ano[i] < f.a0 || d.ano[i] > f.a1) continue;
    if (f.top && !((d.rv[i] !== null && d.rv[i] <= f.top) || (d.rp[i] !== null && d.rp[i] <= f.top))) continue;
    idx.push(i);
  }
  return idx;
}
function montarFiltros(el, meta, f, aoMudar) {
  const anos = []; for (let a = 2000; a <= 2025; a++) anos.push(a);
  const chips = (grupo, lista, cor) => lista.map(([v, r]) =>
    `<button class="chip ${f[grupo].has(v) ? "on" : ""}" data-g="${grupo}" data-v="${v}">` +
    (cor ? `<span class="pt" style="background:${cor[r]}"></span>` : "") + `${r}</button>`).join("");
  el.className = "filtros";
  el.innerHTML = `
    <div class="grupo"><span class="rot">${T("Superfície", "Surface")}</span>${chips("sup", cats("sup", meta), CORES.sup)}</div>
    <div class="grupo"><span class="rot">${T("Nível", "Level")}</span>${chips("niv", cats("niv", meta))}</div>
    <div class="grupo"><span class="rot">${T("Anos", "Years")}</span>
      <select class="sel" data-a="a0">${anos.map(a => `<option ${a === f.a0 ? "selected" : ""}>${a}</option>`).join("")}</select>–
      <select class="sel" data-a="a1">${anos.map(a => `<option ${a === f.a1 ? "selected" : ""}>${a}</option>`).join("")}</select></div>
    <div class="grupo"><span class="rot">${T("Partidas com", "Matches with")}</span>
      <select class="sel" data-a="top">${[[0, T("todos os jogadores", "any players")], ...[5, 10, 20, 50, 100]
        .map(n => [n, T(`algum Top ${n}`, `a Top ${n} player`)])].map(([v, r]) => `<option value="${v}" ${v === f.top ? "selected" : ""}>${r}</option>`).join("")}</select></div>`;
  el.querySelectorAll(".chip").forEach(b => b.addEventListener("click", () => {
    const g = b.dataset.g, v = +b.dataset.v;
    if (f[g].has(v)) { if (f[g].size > 1) f[g].delete(v); } else f[g].add(v);
    b.classList.toggle("on", f[g].has(v)); aoMudar();
  }));
  el.querySelectorAll("select").forEach(s => s.addEventListener("change", () => {
    f[s.dataset.a] = +s.value;
    if (f.a0 > f.a1) [f.a0, f.a1] = [f.a1, f.a0];
    aoMudar();
  }));
}

/* ---------------- gráficos ---------------- */
// título preso ao topo do gráfico: a legenda e os rótulos de média/mediana ficam logo acima da área do gráfico, sem
// encostar no subtítulo (o título centralizado na margem invadia a legenda quando havia população × amostra).
// Com yanchor "top" o Plotly ancora pela 1ª linha e as demais sobem: cada <br> pede ~14 px a mais de folga, senão o
// título é cortado no alto.
const tituloNoTopo = text => ({ text, x: 0, xref: "container", y: 1, yref: "container", yanchor: "top",
  pad: { t: 10 + 14 * (text.match(/<br>/g) || []).length, l: 4 }, font: { size: 16, family: "Barlow Condensed" } });
function grafBarras(el, titulo, series, col) {
  const unica = series.length === 1;
  const traces = series.map(s => ({
    type: "bar", name: s.nome, x: s.freq.map(c => c.rot), y: s.freq.map(c => c.p),
    marker: { color: (unica && col === "sup") ? s.freq.map(c => CORES.sup[c.rot]) : s.cor },
    text: s.freq.map(c => pct(c.p)), textposition: "outside", cliponaxis: false,
    customdata: s.freq.map(c => c.n),
    hovertemplate: `<b>%{x}</b><br>%{y:.1%} ${T("das partidas", "of matches")} (n = %{customdata:,})<extra>${s.nome}</extra>`,
  }));
  plot(el, traces, { title: tituloNoTopo(titulo), height: unica ? 340 : 360,
    showlegend: !unica, yaxis: { tickformat: ".0%", title: T("% das partidas", "% of matches"), gridcolor: "rgba(137,135,129,.22)" },
    margin: { l: 56, r: 10, t: unica ? 64 : 84, b: 46 } });
}
function grafHist(el, col, series, base) {
  const q = QUANT[col], w = q.largura;
  const lo = base.min, hi = base.q995;
  const inicio = Math.floor(lo / w) * w - (w === 1 ? 0.5 : 0);
  const unica = series.length === 1;
  const traces = series.map(s => ({
    type: "histogram", name: s.nome, x: s.v.filter(x => x <= hi), histnorm: "percent",
    xbins: { start: inicio, end: hi + w, size: w }, marker: { color: s.cor }, opacity: unica ? .9 : .6,
    hovertemplate: `%{x}: %{y:.1f}% ${T("das partidas", "of matches")}<extra>${s.nome}</extra>`,
  }));
  const shapes = [], ann = [];
  series.forEach(s => {
    shapes.push({ type: "line", xref: "x", yref: "paper", x0: s.r.media, x1: s.r.media, y0: 0, y1: 1, line: { color: s.cor, width: 2 } });
    shapes.push({ type: "line", xref: "x", yref: "paper", x0: s.r.mediana, x1: s.r.mediana, y0: 0, y1: 1, line: { color: s.cor, width: 2, dash: "dot" } });
    if (unica) {
      ann.push({ x: s.r.media, y: 1, yref: "paper", xanchor: "left", yanchor: "bottom", text: ` ${T("média", "mean")} ${br(s.r.media, 1)}`, showarrow: false });
      ann.push({ x: s.r.mediana, y: 1, yref: "paper", xanchor: "right", yanchor: "bottom", text: `${T("mediana", "median")} ${br(s.r.mediana, 1)} `, showarrow: false });
    }
  });
  plot(el, traces, { barmode: "overlay", bargap: .08, height: 410, shapes, annotations: ann, showlegend: !unica,
    title: tituloNoTopo(T(`Distribuição — ${q.nome}<br><sup>linha contínua = média · pontilhada = mediana · os 0,5% maiores valores ficam fora do gráfico (aparecem no boxplot)</sup>`,
      `Distribution — ${q.nome}<br><sup>solid line = mean · dotted = median · the top 0.5% of values are off the chart (they show in the boxplot)</sup>`)),
    xaxis: { title: q.nome, showgrid: false }, yaxis: { title: T("% das partidas", "% of matches"), gridcolor: "rgba(137,135,129,.22)" },
    margin: { l: 56, r: 10, t: 104, b: 50 } });   // título (2 linhas) + legenda ou rótulos de média/mediana
}
function grafBox(el, col, series) {
  const traces = series.map(s => ({ type: "box", x: s.v, name: s.nome, marker: { color: s.cor, size: 3 },
    boxmean: true, orientation: "h", hoverinfo: "x" }));
  plot(el, traces, { height: series.length > 1 ? 260 : 200, showlegend: false,
    title: { text: T("Boxplot · caixa = 50% centrais · traço = mediana · tracejado = média",
      "Boxplot · box = middle 50% · line = median · dashed = mean"), x: 0, font: { size: 14 } },
    xaxis: { title: QUANT[col].nome }, margin: { l: 90, r: 10, t: 40, b: 46 } });
}

/* ---------------- painel inteiro ---------------- */
function placarFiltrado(el, d, idx) {
  const m = resumo(valoresDe(d, idx, "min")), a = resumo(valoresDe(d, idx, "ace"));
  let fav = 0, nf = 0; for (const i of idx) if (d.fav[i] !== null) { nf++; fav += d.fav[i]; }
  placar(el, [
    { rot: T("Partidas", "Matches"), num: br(idx.length, 0) },
    { rot: T("Duração mediana", "Median duration"), num: m.n ? `${br(m.mediana, 0)} min` : "—",
      sub: m.n ? `${T("média", "mean")} ${br(m.media, 1)} min` : "" },
    { rot: T("Aces por partida", "Aces per match"), num: a.n ? br(a.media, 1) : "—", sub: T("média dos 2 jogadores", "both players combined, mean") },
    { rot: T("Favorito venceu", "Favourite won"), num: nf ? pct(fav / nf) : "—", sub: T("jogador de melhor ranking", "better-ranked player") },
  ]);
}

function tabelaMedidas(d, idx) {
  const linhas = Object.entries(QUANT).map(([c, q]) => {
    const r = resumo(valoresDe(d, idx, c));
    return `<tr><td>${q.nome}</td>${[r.n, r.media, r.mediana, r.dp, r.min, r.q1, r.q3, r.max, r.assim]
      .map((v, k) => `<td class="n">${k === 0 ? br(v, 0) : br(v, 2)}</td>`).join("")}</tr>`;
  }).join("");
  return `<table class="t"><tr><th>${T("Variável", "Variable")}</th><th>n</th><th>${T("Média", "Mean")}</th><th>${T("Mediana", "Median")}</th>
    <th>${T("Desvio-padrão", "Std. deviation")}</th><th>${T("Mín.", "Min")}</th><th>Q1</th><th>Q3</th><th>${T("Máx.", "Max")}</th>
    <th>${T("Assimetria", "Skewness")}</th></tr>${linhas}</table>`;
}

/* Desenha o painel. `alvo` = série principal; `ref` = população para sobrepor (2º set). */
function painelDescritivo(raiz, meta, alvo, ref, estado) {
  const series = q => ref ? [{ nome: T("População", "Population"), cor: CORES.pop, ...q(ref) }, { nome: alvo.nome, cor: alvo.cor, ...q(alvo) }]
                          : [{ nome: alvo.nome, cor: alvo.cor, ...q(alvo) }];
  // qualitativas
  const q = raiz.querySelector("#quali");
  q.innerHTML = Object.keys(QUALI).map(c => `<div class="cartao"><div id="b-${c}" class="grafico"></div></div>`).join("") +
    `<div class="cartao" style="grid-column:1/-1"><div id="b-rod" class="grafico"></div>
      <p class="nota">${T(`<b>Por que a R32 tem mais partidas?</b> Quase metade da base é de torneios ATP 250, que têm chave de
      28 ou 32 jogadores e <b>começam na R32</b>. Só os Grand Slams começam na R128, e os Masters na R64 ou na R128. Em cada
      torneio, a 1ª rodada é a que tem mais jogos.`, `<b>Why does the R32 have the most matches?</b> Almost half of the data comes
      from ATP 250 events, which have 28- or 32-player draws and <b>start in the R32</b>. Only Grand Slams start in the R128,
      and Masters in the R64 or R128. In every tournament, the first round is the one with the most matches.`)}</p></div>`;
  for (const c of Object.keys(QUALI)) grafBarras(q.querySelector(`#b-${c}`), QUALI[c], series(s => ({ freq: frequencias(s.d, s.idx, c, meta) })), c);
  grafBarras(q.querySelector("#b-rod"), T("Rodada — % das partidas jogadas em cada rodada", "Round — % of matches played in each round"),
    series(s => ({ freq: frequencias(s.d, s.idx, "rod", meta) })), "rod");

  // quantitativas
  const sel = raiz.querySelector("#sel-quant");
  const desenharQuant = () => {
    const c = sel.value, alvoV = valoresDe(alvo.d, alvo.idx, c);
    const ser = series(s => { const v = valoresDe(s.d, s.idx, c); return { v, r: resumo(v) }; });
    const r = resumo(alvoV);
    const hist = raiz.querySelector("#hist"), box = raiz.querySelector("#box"), nota = raiz.querySelector("#nota-quant");
    if (c === "dif") {
      grafBarras(hist, T("Diferença de ranking entre os jogadores (em faixas)", "Ranking gap between the players (in bands)"),
        series(s => ({ freq: faixasRanking(s.d, s.idx) })), "dif");
      Plotly.purge(box); box.style.minHeight = "0"; box.innerHTML = "";
      nota.innerHTML = T(`Metade das partidas tem diferença de até <b>${br(r.mediana, 0)} posições</b> (mediana); 25% têm até
        ${br(r.q1, 0)} e 75% até ${br(r.q3, 0)}. A média (${br(r.media, 0)}) é inflada por poucos jogos muito desiguais, de até
        ${br(r.max, 0)} posições, por isso usamos faixas.`, `Half of the matches have a gap of up to <b>${br(r.mediana, 0)} places</b>
        (median); 25% up to ${br(r.q1, 0)} and 75% up to ${br(r.q3, 0)}. The mean (${br(r.media, 0)}) is inflated by a few very
        lopsided matches, with gaps of up to ${br(r.max, 0)} places, which is why we use bands.`);
    } else {
      box.style.minHeight = "";
      grafHist(hist, c, ser, ref ? resumo(valoresDe(ref.d, ref.idx, c)) : r);
      grafBox(box, c, ser);
      nota.textContent = NOTAS[c] || "";
    }
    raiz.querySelector("#mets-quant").innerHTML = [[T("Média", "Mean"), br(r.media)], [T("Mediana", "Median"), br(r.mediana)],
      [T("Desvio-padrão", "Std. deviation"), br(r.dp)], [T("Assimetria", "Skewness"), br(r.assim)], [T("n válido", "valid n"), br(r.n, 0)]]
      .map(([a, b]) => `<div class="met"><div class="rot">${a}</div><div class="num">${b}</div></div>`).join("") +
      (r.assim > 1 ? `<div class="aviso" style="grid-column:1/-1">${T(`Distribuição assimétrica à direita: a média é puxada pelas
        partidas extremas e fica acima da mediana. A mediana descreve melhor a partida típica.`, `Right-skewed distribution: the
        mean is pulled up by extreme matches and sits above the median. The median better describes the typical match.`)}</div>` : "");
  };
  sel.onchange = desenharQuant;
  desenharQuant();
  raiz.querySelector("#medidas").innerHTML = tabelaMedidas(alvo.d, alvo.idx);
}

function htmlPainel() {
  return `
  <div class="abas" id="abas-desc"><button class="on" data-a="quali">${T("Variáveis qualitativas", "Categorical variables")}</button>
    <button data-a="quant">${T("Variáveis quantitativas", "Numeric variables")}</button><button data-a="tab">${T("Medidas", "Summary statistics")}</button></div>
  <section class="painel-aba" data-p="quali">
    ${comoLer(T("Cada barra mostra <b>que fração das partidas</b> cai em cada categoria; as barras de um gráfico somam 100%. Passe o mouse para ver o número de partidas.",
      "Each bar shows <b>what share of matches</b> falls in each category; the bars in a chart add up to 100%. Hover to see the number of matches."))}
    <div class="grade g2" id="quali"></div></section>
  <section class="painel-aba" data-p="quant" hidden>
    ${comoLer(T("O <b>histograma</b> mostra como os valores se distribuem: cada barra é uma faixa de valores e a altura indica a fração das partidas nela. A <b>média</b> é o centro de gravidade; a <b>mediana</b> divide as partidas em duas metades. Com cauda longa à direita, a média fica acima da mediana. O <b>boxplot</b> resume a mesma distribuição: a caixa contém os 50% centrais.",
      "The <b>histogram</b> shows how the values are spread: each bar is a range of values and its height is the share of matches in it. The <b>mean</b> is the centre of gravity; the <b>median</b> splits the matches into two halves. With a long right tail, the mean sits above the median. The <b>boxplot</b> summarises the same distribution: the box holds the middle 50%."))}
    <div class="cartao"><label>${T("Variável", "Variable")}:
      <select class="sel" id="sel-quant">${Object.entries(QUANT).map(([c, q]) => `<option value="${c}">${q.nome}</option>`).join("")}</select></label>
      <div id="hist" class="grafico"></div><p class="nota" id="nota-quant"></p><div id="box"></div>
      <div class="mets" id="mets-quant"></div></div></section>
  <section class="painel-aba" data-p="tab" hidden><div class="cartao rolagem" id="medidas"></div></section>`;
}
function ligarAbas(raiz, sel = "#abas-desc") {
  const abas = raiz.querySelector(sel);
  abas.querySelectorAll("button").forEach(b => b.addEventListener("click", () => {
    abas.querySelectorAll("button").forEach(x => x.classList.toggle("on", x === b));
    const grupo = abas.parentElement;
    grupo.querySelectorAll(":scope > .painel-aba").forEach(p => p.hidden = p.dataset.p !== b.dataset.a);
    window.dispatchEvent(new Event("resize"));   // Plotly redimensiona os gráficos que estavam ocultos
  }));
}
