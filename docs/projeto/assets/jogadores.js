/* Extra · Jogadores — ranking por critério e perfil individual.
   Mesmas fórmulas de app/analises.py: razão das somas, IC de Wilson, percentil e posição.
   `conferir()` compara com os valores calculados no Python (jogadores.json → checagem). */

const Z975 = 1.959963984540054;
const SUPS = ["Dura", "Saibro", "Grama", "Carpete"];
const NIVS = ["Grand Slam", "ATP Finals", "Masters 1000", "ATP 500", "ATP 250"];
const COMP = ["partida", "venceu", "vitoria_top10", "vs_top10", "sv_pts", "sv_won", "first_in", "first_won",
  "second_pts", "second_won", "ret_pts", "ret_won", "bp_fac", "bp_sav", "bp_opp", "bp_conv",
  "aces", "dfs", "sv_games", "tb_jogados", "tb_vencidos", "decisivo_jogado", "decisivo_vencido",
  "final", "titulo", "titulo_gs"];

function wilson(s, n, z = Z975) {
  if (!n) return [null, null];
  const p = s / n, z2 = z * z, d = 1 + z2 / n;
  const centro = (p + z2 / (2 * n)) / d, meia = z / d * Math.sqrt(p * (1 - p) / n + z2 / (4 * n * n));
  return [centro - meia, centro + meia];
}

/* soma as linhas (jogador × ano × superfície × nível) que passam no filtro, agrupando por `chaveDe` */
function somar(L, filtro, chaveDe) {
  const g = new Map();
  for (let i = 0; i < L.j.length; i++) {
    if (!filtro(i)) continue;
    const k = chaveDe(i);
    let s = g.get(k);
    if (!s) { s = { mr: null }; COMP.forEach(c => s[c] = 0); g.set(k, s); }
    for (const c of COMP) s[c] += L[c][i];
    const mr = L.mr[i]; if (mr !== null && (s.mr === null || mr < s.mr)) s.mr = mr;
  }
  return g;
}
function valores(s, CRIT) {
  const v = { partidas: s.partida, V: s.venceu, D: s.partida - s.venceu, melhor_rank: s.mr };
  for (const c of CRIT) {
    if (c.tipo === "n") { v[c.chave] = s[c.num]; continue; }
    if (c.tipo === "razao") {
      const ret = s.ret_pts ? s.ret_won / s.ret_pts : null, perd = s.sv_pts ? (s.sv_pts - s.sv_won) / s.sv_pts : null;
      v[c.chave] = ret !== null && perd ? ret / perd : null; v[c.chave + "_n"] = s.sv_pts + s.ret_pts; continue;
    }
    const den = s[c.den];
    v[c.chave] = den ? s[c.num] / den : null; v[c.chave + "_n"] = den;
    if (c.tipo === "%") [v[c.chave + "_ic_inf"], v[c.chave + "_ic_sup"]] = wilson(s[c.num], den);
  }
  return v;
}
function fmtC(c, v) {
  if (v === null || v === undefined || Number.isNaN(v)) return "—";
  return c.tipo === "%" ? pct(v) : c.tipo === "taxa" ? br(v, 3) : c.tipo === "razao" ? br(v, 2) : br(v, 0);
}
const fmtIC = (c, li, ls) => c.tipo !== "%" || li === null || li === undefined ? "—" : `${pct(li)} a ${pct(ls)}`;
const fmtPctl = p => br(p, (p > 99 && p < 100) || (p > 0 && p < 1) ? 1 : 0) + "%";

/* posição e percentil — idênticos a analises.posicao */
function posicao(ref, valor, maiorMelhor) {
  const r = ref.filter(x => x !== null && x !== undefined && !Number.isNaN(x));
  if (valor === null || valor === undefined || !r.length) return [null, 0, r.length];
  let pior = 0, melhor = 0;
  for (const x of r) { if (maiorMelhor ? x < valor : x > valor) pior++; else if (maiorMelhor ? x > valor : x < valor) melhor++; }
  const emp = r.length - pior - melhor;
  return [100 * (pior + .5 * emp) / r.length, melhor + 1, r.length];
}
/* ranking — idêntico a analises.ranking_criterio (rank "min" para a posição, "average" para o percentil) */
function rankear(tab, c) {
  const t = tab.filter(r => r[c.chave] !== null && r[c.chave] !== undefined && !Number.isNaN(r[c.chave]));
  t.sort((a, b) => (c.maior_melhor ? b[c.chave] - a[c.chave] : a[c.chave] - b[c.chave]) || b.partidas - a.partidas);
  const n = t.length, vals = t.map(r => r[c.chave]);
  const asc = [...vals].sort((a, b) => a - b);
  const mediaRank = v => {  // rank médio ascendente (1..n) de v
    let lo = 0, hi = n; while (lo < hi) { const m = (lo + hi) >> 1; asc[m] < v ? lo = m + 1 : hi = m; }
    let fim = lo; while (fim < n && asc[fim] === v) fim++;
    return (lo + 1 + fim) / 2;
  };
  t.forEach(r => {
    const v = r[c.chave];
    r.posicao = 1 + vals.filter(x => c.maior_melhor ? x > v : x < v).length;
    const ra = c.maior_melhor ? mediaRank(v) : n + 1 - mediaRank(v);
    r.percentil = 100 * (ra - .5) / n;
  });
  return t;
}
function mediasCircuito(L, filtro, CRIT, ref) {
  const tot = somar(L, filtro, () => 0).get(0);
  const m = tot ? valores(tot, CRIT) : {};
  for (const c of CRIT) if (c.tipo === "n") m[c.chave] = ref && ref.length ? ref.reduce((a, r) => a + r[c.chave], 0) / ref.length : null;
  return m;
}
function tabelaJogadores(J, anos, sups, nivs, minimo) {
  const L = J.linhas, f = i => L.ano[i] >= anos[0] && L.ano[i] <= anos[1] && sups.has(L.sup[i]) && nivs.has(L.niv[i]);
  const g = somar(L, f, i => L.j[i]), tab = [];
  for (const [j, s] of g) { const v = valores(s, J.criterios); if (v.partidas >= minimo) { v.nome = J.nomes[j]; tab.push(v); } }
  return { tab, medias: mediasCircuito(L, f, J.criterios, tab) };
}
function carreira(J) {
  if (!J._car) { J._car = new Map(); const L = J.linhas; for (let i = 0; i < L.j.length; i++) J._car.set(L.j[i], (J._car.get(L.j[i]) || 0) + L.partida[i]); }
  return J._car;
}
function perfil(J, nome, anos, sups, minRef = 100, minRec = 20) {
  const L = J.linhas, idNome = J.nomes.indexOf(nome);
  const f = i => L.ano[i] >= anos[0] && L.ano[i] <= anos[1] && sups.has(L.sup[i]);
  const todos = somar(L, f, i => L.j[i]);
  if (!todos.has(idNome)) return { vazio: true };
  const car = carreira(J), CR = J.criterios;
  const ref = [];
  for (const [j, s] of todos) { if (car.get(j) >= minRef && s.partida >= minRec) { const v = valores(s, CR); v.j = j; ref.push(v); } }
  const eu = valores(todos.get(idNome), CR), circ = mediasCircuito(L, f, CR, ref);
  const outros = ref.filter(r => r.j !== idNome);
  const ficha = CR.map(c => {
    const [pc, pos, tot] = posicao(outros.map(r => r[c.chave]), eu[c.chave], c.maior_melhor);
    return { c, valor: eu[c.chave], n: eu[c.chave + "_n"], ic_inf: eu[c.chave + "_ic_inf"], ic_sup: eu[c.chave + "_ic_sup"],
             media: circ[c.chave], percentil: pc, posicao: pos, total: tot + 1 };
  });
  const fe = i => f(i) && L.j[i] === idNome;
  const porSup = [...somar(L, fe, i => L.sup[i])].sort((a, b) => a[0] - b[0]).map(([k, s]) => ({ sup: SUPS[k], ...valores(s, CR) }));
  const anual = [...somar(L, fe, i => L.ano[i])].sort((a, b) => a[0] - b[0]).map(([k, s]) => ({ ano: k, ...valores(s, CR) }));
  const F = J.finais, fins = [];
  for (let i = 0; i < F.ano.length; i++) {
    if (F.ano[i] < anos[0] || F.ano[i] > anos[1] || !sups.has(SUPS.indexOf(F.superficie[i]))) continue;
    if (F.vencedor[i] === nome || F.perdedor[i] === nome)
      fins.push({ ano: F.ano[i], torneio: F.torneio[i], nivel: F.nivel[i], sup: F.superficie[i], venceu: F.vencedor[i] === nome,
                  oponente: F.vencedor[i] === nome ? F.perdedor[i] : F.vencedor[i], placar: F.placar[i] });
  }
  let melhor = null; anual.forEach(a => { if (a.melhor_rank !== null && (!melhor || a.melhor_rank < melhor.rank)) melhor = { rank: a.melhor_rank, ano: a.ano }; });
  return { vazio: false, eu, ficha, nRef: ref.length, porSup, anual, finais: fins, melhor,
           anos: [anual[0].ano, anual[anual.length - 1].ano] };
}

/* mínimo de partidas sugerido para o recorte — idêntico a minimo_sugerido no Streamlit:
   10 por temporada, entre 20 e 100 (um ano só → 20; com 100 fixo, uma temporada isolada ficava vazia) */
const minimoSugerido = (a0, a1) => Math.min(100, Math.max(20, 10 * (a1 - a0 + 1)));
/* quem mais jogou no recorte (para explicar por que um ranking ficou vazio) */
function maxPartidas(J, anos, sups, nivs) {
  const L = J.linhas, f = i => L.ano[i] >= anos[0] && L.ano[i] <= anos[1] && sups.has(L.sup[i]) && nivs.has(L.niv[i]);
  let mx = 0; for (const s of somar(L, f, i => L.j[i]).values()) mx = Math.max(mx, s.partida);
  return mx;
}
const avisoVazio = (minimo, mx) => `<div class="aviso">${mx ? `Ninguém tem ${minimo} partidas nesse recorte: quem mais jogou
  fez ${mx}. Reduza o mínimo de partidas ou amplie o recorte.` : "Não há partidas nesse recorte."}</div>`;

/* líderes de todos os critérios — idêntico a analises.lideres:
   pódio (3 primeiros, vantagem do 1º, liderança isolada × empate técnico pelo IC de Wilson) e
   quadro de medalhas ordenado por pontos (1º = 3, 2º = 2, 3º = 1; desempate por ouros, pratas, top N) */
const MEDALHAS = ["ouro", "prata", "bronze"];
function lideres(tab, CR, top = 10) {
  const podio = [], conta = new Map();
  for (const c of CR) {
    let rk = rankear(tab.map(r => ({ ...r })), c);
    if (c.tipo === "n") rk = rk.filter(r => r[c.chave] > 0);
    if (!rk.length) continue;
    const p = { c, n: rk.length };
    MEDALHAS.forEach((m, k) => { if (rk[k]) { p[m] = rk[k].nome; p[m + "_valor"] = rk[k][c.chave]; } });
    if (rk.length > 1) {
      const a = rk[0], b = rk[1];
      p.vantagem = c.maior_melhor ? a[c.chave] - b[c.chave] : b[c.chave] - a[c.chave];
      if (c.tipo === "%") {
        const iso = c.maior_melhor ? a[c.chave + "_ic_inf"] > b[c.chave + "_ic_sup"] : a[c.chave + "_ic_sup"] < b[c.chave + "_ic_inf"];
        p.lideranca = iso ? "isolada" : "empate técnico";
      }
    }
    podio.push(p);
    rk.slice(0, top).forEach((r, k) => {
      if (!conta.has(r.nome)) conta.set(r.nome, { nome: r.nome, ouro: 0, prata: 0, bronze: 0, top: 0, criterios: [], partidas: r.partidas,
        ouro_criterios: [], prata_criterios: [], bronze_criterios: [], top_criterios: [] });
      const d = conta.get(r.nome);
      if (k < 3) { d[MEDALHAS[k]]++; d[MEDALHAS[k] + "_criterios"].push(c.nome); }
      if (k === 0) d.criterios.push(c.nome);
      d.top++; d.top_criterios.push(`${c.nome} (${k + 1}º)`);
    });
  }
  const med = [...conta.values()];
  med.forEach(d => d.pontos = 3 * d.ouro + 2 * d.prata + d.bronze);
  med.sort((a, b) => b.pontos - a.pontos || b.ouro - a.ouro || b.prata - a.prata || b.top - a.top);
  return { podio, med };
}

/* dica flutuante: qualquer elemento com data-dica mostra o texto ao passar o mouse (ou ao tocar/focar).
   Fica no <body>, então não é cortada pelas tabelas com rolagem. */
function ligarDicas(raiz = document) {
  let caixa = document.getElementById("dica-flutuante");
  if (!caixa) { caixa = document.createElement("div"); caixa.id = "dica-flutuante"; caixa.setAttribute("role", "tooltip"); caixa.hidden = true; document.body.append(caixa); }
  const mostrar = el => {
    caixa.innerHTML = el.dataset.dica; caixa.hidden = false;
    const r = el.getBoundingClientRect(), w = caixa.offsetWidth, h = caixa.offsetHeight;
    let x = r.left + r.width / 2 - w / 2, y = r.top - h - 8;
    if (y < 8) y = r.bottom + 8;
    caixa.style.left = Math.max(8, Math.min(x, innerWidth - w - 8)) + "px"; caixa.style.top = y + "px";
  };
  const esconder = () => { caixa.hidden = true; };
  raiz.addEventListener("mouseover", e => { const el = e.target.closest("[data-dica]"); if (el) mostrar(el); });
  raiz.addEventListener("mouseout", e => { const el = e.target.closest("[data-dica]"); if (el && !el.contains(e.relatedTarget)) esconder(); });
  raiz.addEventListener("focusin", e => { const el = e.target.closest("[data-dica]"); if (el) mostrar(el); });
  raiz.addEventListener("focusout", esconder);
  addEventListener("scroll", esconder, true);
}

/* caixa de busca com lista suspensa (substitui o <datalist>, que só mostra opções que batem com o texto
   já digitado — com "Roger Federer" preenchido, a lista nunca abria) */
function combobox(input, opcoes, detalhe, aoEscolher, maxItens = 150) {
  const sem = s => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase();
  const chaves = opcoes.map(sem);
  const caixa = document.createElement("div");
  caixa.className = "combo";
  input.parentNode.insertBefore(caixa, input);
  caixa.append(input);
  const seta = document.createElement("button");
  seta.type = "button"; seta.className = "combo-seta"; seta.setAttribute("aria-label", "Abrir lista"); seta.textContent = "▾";
  const lista = document.createElement("ul");
  lista.className = "combo-lista"; lista.setAttribute("role", "listbox"); lista.hidden = true;
  caixa.append(seta, lista);
  input.setAttribute("role", "combobox"); input.setAttribute("autocomplete", "off"); input.setAttribute("aria-expanded", "false");
  let atual = input.value, itens = [], foco = -1;

  const abrir = (filtrar = true) => {
    const q = filtrar ? sem(input.value.trim()) : "";
    itens = [];
    for (let i = 0; i < opcoes.length && itens.length < maxItens; i++) if (!q || chaves[i].includes(q)) itens.push(i);
    lista.innerHTML = itens.length
      ? itens.map((i, k) => `<li role="option" data-k="${k}" class="${opcoes[i] === atual ? "sel" : ""}">${opcoes[i]}<small>${detalhe(i)}</small></li>`).join("")
        + (itens.length === maxItens ? `<li class="vazio">Digite para refinar a busca…</li>` : "")
      : `<li class="vazio">Nenhum jogador com "${input.value}"</li>`;
    foco = Math.max(0, itens.findIndex(i => opcoes[i] === atual));
    lista.hidden = false; input.setAttribute("aria-expanded", "true"); marcar();
  };
  const fechar = () => { lista.hidden = true; input.setAttribute("aria-expanded", "false"); };
  const marcar = () => lista.querySelectorAll("li[data-k]").forEach(li => {
    const on = +li.dataset.k === foco; li.classList.toggle("foco", on); if (on) li.scrollIntoView({ block: "nearest" }); });
  const escolher = k => { if (itens[k] === undefined) return; atual = opcoes[itens[k]]; input.value = atual; fechar(); aoEscolher(atual); };

  input.addEventListener("focus", () => { input.select(); abrir(false); });
  input.addEventListener("click", () => { if (lista.hidden) abrir(false); });
  input.addEventListener("input", () => abrir(true));
  input.addEventListener("keydown", e => {
    if (e.key === "ArrowDown") { e.preventDefault(); if (lista.hidden) abrir(false); else { foco = Math.min(foco + 1, itens.length - 1); marcar(); } }
    else if (e.key === "ArrowUp") { e.preventDefault(); foco = Math.max(foco - 1, 0); marcar(); }
    else if (e.key === "Enter") { e.preventDefault(); if (!lista.hidden) escolher(foco); }
    else if (e.key === "Escape") { input.value = atual; fechar(); input.blur(); }
  });
  input.addEventListener("blur", () => setTimeout(() => { if (!caixa.contains(document.activeElement)) { input.value = atual; fechar(); } }, 150));
  seta.addEventListener("mousedown", e => { e.preventDefault(); if (!lista.hidden) fechar(); else if (document.activeElement === input) abrir(false); else input.focus(); });
  lista.addEventListener("mousedown", e => { e.preventDefault(); const li = e.target.closest("li[data-k]"); if (li) escolher(+li.dataset.k); });
  return { definir: v => { atual = v; input.value = v; } };
}

/* compara com os valores calculados no Python */
function conferir(J) {
  const tudo = new Set([0, 1, 2, 3]), niv = new Set([0, 1, 2, 3, 4]);
  const { tab } = tabelaJogadores(J, [2000, 2025], tudo, niv, 100);
  const erros = [];
  for (const c of J.criterios) {
    const top = rankear(tab.map(r => ({ ...r })), c).slice(0, 3).map(r => [r.nome, r[c.chave]]);
    J.checagem.top3[c.chave].forEach(([n, v], k) => {
      if (!top[k] || top[k][0] !== n || Math.abs(top[k][1] - v) > 1e-5) erros.push(`top3 ${c.chave} #${k + 1}: ${top[k]} × ${n} ${v}`);
    });
  }
  const p = perfil(J, "Roger Federer", [2000, 2025], tudo);
  J.checagem.federer.forEach(ref => {
    const f = p.ficha.find(x => x.c.chave === ref.chave);
    const ok = (a, b) => (a === null && b === null) || Math.abs(a - b) < 1e-4;
    if (!ok(f.valor, ref.valor) || !ok(f.percentil, ref.percentil) || f.posicao !== ref.posicao || f.total !== ref.total)
      erros.push(`federer ${ref.chave}: JS ${f.valor} ${f.percentil} ${f.posicao}/${f.total} × PY ${ref.valor} ${ref.percentil} ${ref.posicao}/${ref.total}`);
  });
  return erros;
}
