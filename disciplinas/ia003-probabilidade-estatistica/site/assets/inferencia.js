/* 3º set — inferência. Os resultados vêm prontos de data/inferencia.json (calculados e validados no
   Python). Só a simulação didática de 100 ICs roda aqui, sorteando da população no navegador. */

const SINAL = { bilateral: "≠", maior: ">", menor: "<" };
const FMT = { P1: v => pct(v), P2: v => pct(v), M1: v => `${br(v, 1)} min`, M2: v => br(v, 2) };
let ALFA = 0.05;

function decisaoTexto(h, alfa) {
  const rej = h.valor_p < alfa, poder = h.por_alfa[String(alfa)].poder, f = FMT[h.id];
  const s = h.tipo === "proporção" ? "p" : "μ";
  if (rej && h.h0_falsa && poder < 0.5)
    return `✅ <b>Decisão correta, mas com sorte:</b> H₀ é falsa na população (${s} = ${f(h.parametro)}), porém a diferença
      para ${f(h.h0)} é tão pequena que o poder do teste era de só ${pct(poder)}. A rejeição veio em boa parte do
      <b>erro amostral</b>: esta amostra se afastou de H₀ mais do que a população. Com outra semente, o mais provável
      seria não rejeitar.`;
  if (rej && h.h0_falsa) return `✅ <b>Decisão correta:</b> H₀ é falsa na população e o teste a rejeitou.`;
  if (rej) return `❌ <b>Erro tipo I:</b> o teste rejeitou uma H₀ que é verdadeira na população.`;
  if (h.h0_falsa)
    return `⚠️ <b>Erro tipo II:</b> na população H₀ é falsa (${s} = ${f(h.parametro)} ≠ ${f(h.h0)}), mas a diferença é
      pequena. O poder do teste para detectá-la com n = ${h.n} era de só ${pct(poder)}, então não rejeitar era o resultado
      mais provável.`;
  return `✅ <b>Decisão correta:</b> H₀ é verdadeira na população e o teste não a rejeitou.`;
}

function cartaoHipotese(el, h) {
  const f = FMT[h.id], s = h.tipo === "proporção" ? "p" : "μ", sinal = SINAL[h.alt];
  const rej = h.valor_p < ALFA, poder = h.por_alfa[String(ALFA)].poder;
  const nomeTeste = h.tipo === "proporção" ? "z para uma proporção" : "t para uma média";
  el.innerHTML = `
    <div class="grade g2">
      <div>
        <h3 style="margin-top:0">${h.pergunta}</h3>
        <p><b>Por que importa:</b> ${h.justificativa}</p>
        <p><b>Parâmetro:</b> ${h.parametro_nome}.</p>
        <ul><li><b>H₀:</b> ${s} = ${f(h.h0)}</li><li><b>H₁:</b> ${s} ${sinal} ${f(h.h0)}</li>
          <li><b>Nível de significância:</b> α = ${pct(ALFA, 0)} · teste ${nomeTeste}
            (${h.alt === "maior" ? "unilateral à direita" : "bilateral"})</li></ul>
      </div>
      <div class="placar-h"></div>
    </div>
    <div class="formula"></div>
    ${comoLer(`<ul>
      <li><b>Estatística ${h.tipo === "proporção" ? "z" : "t"}:</b> quantos <i>erros-padrão</i> a estimativa da amostra está
        longe do valor de H₀. Perto de 0 = compatível com H₀; além de ±2 = bem improvável sob H₀.</li>
      <li><b>Erro-padrão:</b> o tamanho típico do erro amostral. Ele diminui quando n aumenta (√n no denominador).</li>
      <li><b>Valor-p:</b> a chance de ver uma amostra tão extrema quanto esta <b>se H₀ fosse verdadeira</b>. Valor-p pequeno
        → a amostra é estranha demais para H₀ → rejeitamos H₀.</li>
      <li><b>IC 95%:</b> a faixa de valores plausíveis para o parâmetro. O método acerta em 95% das amostras.</li></ul>`)}
    <div class="cartao" style="margin-top:12px">
      <h3 style="margin-top:0">Hawk-Eye: a estimativa da amostra × H₀ × o valor real</h3>
      <div class="grafico hk" style="min-height:210px"></div>
      <p>${seloHawkeye(h.contem)}</p>
      ${comoLer(`A <b>barra amarela</b> é o IC calculado com a amostra e a <b>bola</b> é a estimativa pontual. A <b>linha
        tracejada cinza</b> é o valor afirmado por H₀ e a <b>linha violeta</b> é o valor verdadeiro da população. Se o
        tracejado ficar <b>fora</b> da barra, a amostra contradiz H₀. Se a linha violeta ficar <b>dentro</b> da barra, o IC
        acertou: <b>IN</b>.`)}
    </div>
    <div class="conclusao ${rej ? "rej" : "nrej"}">${rej
      ? `<b>Conclusão (amostra):</b> valor-p ${h.valor_p < 1e-4 ? "< 0,0001" : "= " + br(h.valor_p, 4)} &lt; α = ${pct(ALFA, 0)} →
         <b>rejeitamos H₀</b>. Há evidência estatística de que ${s} ${sinal} ${f(h.h0)}.`
      : `<b>Conclusão (amostra):</b> valor-p = ${br(h.valor_p, 4)} ≥ α = ${pct(ALFA, 0)} → <b>não rejeitamos H₀</b>. Os dados são
         compatíveis com ${s} = ${f(h.h0)}, o que <b>não prova</b> que H₀ seja verdadeira: só não há evidência contra ela.`}</div>
    <details class="como-ler"><summary>Condições de aplicação do teste</summary>
      <table class="t">${h.condicoes.map(c => `<tr><td>${c.condicao}</td><td class="n">${typeof c.valor === "number" ? br(c.valor, 2) : c.valor}</td>
        <td>${c.ok ? "✅ atendida" : "⚠️ não atendida"}</td></tr>`).join("")}</table>
      <p class="nota">${h.tipo === "média"
        ? "A variável é assimétrica à direita, mas com n grande o <b>Teorema Central do Limite</b> garante que a média amostral tem distribuição aproximadamente normal. Por isso o teste t é adequado."
        : "Para usar a aproximação normal, a amostra precisa de pelo menos 10 \"sucessos\" e 10 \"fracassos\" esperados. Com n = 382, isso é folgado."}</p>
    </details>
    <h3>Comparação com a população</h3>
    <div class="mets">
      <div class="met"><div class="rot">Parâmetro populacional</div><div class="num">${f(h.parametro)}</div>
        <div class="nota">N = ${br(h.N_sub, 0)}</div></div>
      <div class="met"><div class="rot">Erro amostral</div><div class="num">${h.tipo === "proporção"
        ? (h.erro_amostral >= 0 ? "+" : "") + br(100 * h.erro_amostral, 2) + " p.p." : (h.erro_amostral >= 0 ? "+" : "") + br(h.erro_amostral, 2)}</div>
        <div class="nota">estimativa − parâmetro</div></div>
      <div class="met"><div class="rot">IC contém o parâmetro?</div><div class="num">${h.contem ? "Sim" : "Não"}</div></div>
      <div class="met"><div class="rot">Poder do teste</div><div class="num">${pct(poder)}</div>
        <div class="nota">chance de rejeitar H₀, dado o valor real</div></div>
    </div>
    <p>${decisaoTexto(h, ALFA)}</p>
    ${comoLer(`<ul><li><b>Erro tipo I:</b> rejeitar uma H₀ verdadeira (alarme falso). A chance é α.</li>
      <li><b>Erro tipo II:</b> não rejeitar uma H₀ falsa (deixar passar).</li>
      <li><b>Poder:</b> a chance de o teste perceber que H₀ é falsa. Alto quando a diferença real é grande ou n é grande;
        baixo quando a diferença é minúscula.</li></ul>`)}`;

  placar(el.querySelector(".placar-h"), [
    { rot: "n (amostra)", num: h.n, sub: h.unidade },
    { rot: "Estimativa pontual", num: f(h.estimativa) },
    { rot: `Estatística ${h.tipo === "proporção" ? "z" : "t"}`, num: br(h.estatistica, 3), sub: h.gl ? `${h.gl} graus de liberdade` : "" },
    { rot: "Valor-p", num: vp(h.valor_p) },
    { rot: "IC 95%", num: `${f(h.ic_inf)} – ${f(h.ic_sup)}` },
  ]);
  const tex = h.tipo === "proporção"
    ? String.raw`z=\frac{\hat p-p_0}{\sqrt{p_0(1-p_0)/n}}=\frac{${tx(br(h.estimativa, 4))}-${tx(br(h.h0, 4))}}{\sqrt{${tx(br(h.h0, 4))}(1-${tx(br(h.h0, 4))})/${h.n}}}=${tx(br(h.estatistica, 3))}\qquad IC=\hat p\pm z_{0{,}975}\sqrt{\hat p(1-\hat p)/n}`
    : String.raw`t=\frac{\bar x-\mu_0}{s/\sqrt n}=\frac{${tx(br(h.estimativa, 2))}-${tx(br(h.h0, 0))}}{${tx(br(h.ep, 3))}}=${tx(br(h.estatistica, 3))}\qquad IC=\bar x\pm t_{0{,}975;\,${h.gl}}\cdot s/\sqrt n`;
  katexEm(el.querySelector(".formula"), tex);
  hawkeye(el.querySelector(".hk"), { est: h.estimativa, li: h.ic_inf, ls: h.ic_sup, h0: h.h0, param: h.parametro,
    fmt: f, proporcao: h.tipo === "proporção" });
}

function tabelaResumo(el, hs) {
  el.innerHTML = `<table class="t"><tr><th>Hipótese</th><th>H₀</th><th>H₁</th><th>Estimativa</th><th>IC 95%</th>
    <th>Parâmetro real</th><th>IC contém?</th><th>Valor-p</th><th>Decisão</th><th>Na população</th></tr>` +
    hs.map(h => { const f = FMT[h.id], s = h.tipo === "proporção" ? "p" : "μ";
      return `<tr><td><b>${h.id}</b> · ${h.pergunta}</td><td>${s} = ${f(h.h0)}</td><td>${s} ${SINAL[h.alt]} ${f(h.h0)}</td>
        <td class="n">${f(h.estimativa)}</td><td class="n">${f(h.ic_inf)} – ${f(h.ic_sup)}</td><td class="n">${f(h.parametro)}</td>
        <td>${h.contem ? "✅ Sim" : "❌ Não"}</td><td class="n">${vp(h.valor_p)}</td>
        <td>${h.valor_p < ALFA ? "Rejeita H₀" : "Não rejeita H₀"}</td><td>${h.h0_falsa ? "H₀ falsa" : "H₀ verdadeira"}</td></tr>`; }).join("") + "</table>";
}

/* ---------------- simulação de ICs (no navegador) ---------------- */
function rng(semente) {          // mulberry32: gerador pseudoaleatório com semente
  let a = semente >>> 0;
  return () => { a |= 0; a = a + 0x6D2B79F5 | 0; let t = Math.imul(a ^ a >>> 15, 1 | a);
    t = t + Math.imul(t ^ t >>> 7, 61 | t) ^ t; return ((t ^ t >>> 14) >>> 0) / 4294967296; };
}
function valoresHipotese(h, pop) {
  const v = [];
  for (let i = 0; i < pop.ano.length; i++) {
    if (h.id === "P1" && pop.fav[i] !== null) v.push(pop.fav[i]);
    else if (h.id === "P2") v.push(pop.dec[i]);
    else if (h.id === "M1" && pop.bo[i] === 3 && pop.min[i] !== null) v.push(pop.min[i]);
    else if (h.id === "M2" && pop.ace[i] !== null) v.push(pop.ace[i]);
  }
  return v;
}
function simular(valores, n, reps, tipo, critico, semente) {
  const r = rng(semente), N = valores.length, saida = [];
  for (let k = 0; k < reps; k++) {
    const usados = new Set(); let soma = 0, soma2 = 0;
    while (usados.size < n) { const i = Math.floor(r() * N); if (usados.has(i)) continue; usados.add(i);
      soma += valores[i]; soma2 += valores[i] * valores[i]; }
    const m = soma / n;
    const ep = tipo === "proporção" ? Math.sqrt(m * (1 - m) / n) : Math.sqrt((soma2 - n * m * m) / (n - 1)) / Math.sqrt(n);
    saida.push([m, m - critico * ep, m + critico * ep]);
  }
  return saida;
}
function grafCobertura(el, ics, param, proporcao, fmt) {
  const ok = ics.map(([, a, b]) => a <= param && param <= b);
  const seg = flag => { const x = [], y = []; ics.forEach(([, a, b], i) => { if (ok[i] === flag) { x.push(a, b, null); y.push(i + 1, i + 1, null); } }); return { x, y }; };
  const s1 = seg(true), s2 = seg(false);
  plot(el, [
    { x: s1.x, y: s1.y, mode: "lines", line: { color: CORES.amostra, width: 2.5 }, name: "IC contém o parâmetro (IN)", hoverinfo: "skip" },
    { x: s2.x, y: s2.y, mode: "lines", line: { color: CORES.erro, width: 2.5 }, name: "IC não contém (OUT)", hoverinfo: "skip" },
    { x: ics.map(c => c[0]), y: ics.map((_, i) => i + 1), mode: "markers", marker: { color: "#14211b", size: 4 },
      showlegend: false, hovertemplate: "amostra %{y}: %{x}<extra></extra>" },
  ], { height: 540, shapes: [{ type: "line", xref: "x", yref: "paper", x0: param, x1: param, y0: 0, y1: 1, line: { color: CORES.pop, width: 3 } }],
    annotations: [{ x: param, y: 1, yref: "paper", yanchor: "bottom", text: `valor real ${fmt(param)}`, showarrow: false, font: { color: CORES.pop } }],
    xaxis: { tickformat: proporcao ? ".0%" : null }, yaxis: { title: "amostra simulada nº", showgrid: false } });
  return ok.filter(Boolean).length / ok.length;
}

/* ---------------- bônus ---------------- */
function bonus(el, b) {
  const a = b.aces_superficie, fm = b.formato, c = b.canhotos;
  el.innerHTML = `
  <div class="abas" id="abas-bonus"><button class="on" data-a="aces">Aces por superfície</button>
    <button data-a="fmt">Zebras: melhor de 3 × 5</button><button data-a="canh">Canhotos × destros</button></div>
  <section class="painel-aba" data-p="aces">
    <h3>A superfície muda a quantidade de aces?</h3>
    <p>A grama é rápida e a bola quica baixo, o que favorece o saque. O saibro é lento e a bola quica alto, o que favorece a
      devolução. A quadra dura fica no meio. Comparamos a média de aces nas três superfícies (o carpete fica de fora: só 10
      partidas na amostra, superfície extinta em 2009).</p>
    <div class="cartao"><div id="g-aces" class="grafico"></div>
      <p class="nota"><span class="leg"><i style="background:var(--tinta)"></i>bola = média da amostra · barra = IC 95%</span>
        <span class="leg"><i style="background:var(--pop)"></i>traço = média real da população</span></p></div>
    <p><b>Comparações par a par</b> (t de Welch, H₀: médias iguais). Como fazemos <b>3 testes</b>, usamos a correção de
      <b>Bonferroni</b>: cada valor-p é multiplicado por 3, para que a chance total de um alarme falso continue em 5%.</p>
    <div class="cartao rolagem"><table class="t"><tr><th>Comparação</th><th>n</th><th>Diferença (amostra)</th><th>IC 95%</th><th>t</th>
      <th>Valor-p (Bonferroni)</th><th>Decisão (5%)</th><th>Diferença real</th></tr>
      ${a.pares.map(p => `<tr><td>${p.a} − ${p.b}</td><td>${p.n_a} × ${p.n_b}</td><td class="n">${br(p.diferenca, 1)}</td>
        <td class="n">${br(p.ic_inf, 1)} a ${br(p.ic_sup, 1)}</td><td class="n">${br(p.estatistica, 2)}</td><td class="n">${vp(p.valor_p_bonferroni)}</td>
        <td>${p.rejeita_bonferroni ? "Diferença significativa" : "Não significativa"}</td><td class="n">${br(p.dif_pop, 1)}</td></tr>`).join("")}</table></div>
    <div class="aula"><strong>Leitura</strong>O saibro tem claramente menos aces que a dura e a grama. Já grama × dura não deu
      diferença significativa na amostra, embora na população a grama tenha cerca de ${br(a.pares[0].dif_pop, 1)} aces a mais.
      O motivo é o tamanho: só ${a.pares[0].n_a} partidas de grama na amostra deixam o IC largo. É um erro tipo II causado por
      um subgrupo pequeno.</div>
  </section>
  <section class="painel-aba" data-p="fmt" hidden>
    <h3>O favorito vence mais em partidas melhor de 5 sets?</h3>
    <p>Ideia: em jogos mais longos, a sorte de um set isolado pesa menos e a qualidade aparece mais. Teste de
      <b>diferença entre duas proporções</b>: <b>H₀:</b> p₅ = p₃ · <b>H₁:</b> p₅ &gt; p₃.</p>
    <div id="pl-fmt"></div><div id="f-fmt"></div>
    <div class="conclusao ${fm.valor_p < ALFA ? "rej" : "nrej"}"><b>Conclusão:</b> valor-p = ${br(fm.valor_p, 4)}
      ${fm.valor_p < ALFA ? "&lt;" : "≥"} α = ${pct(ALFA, 0)} → <b>${fm.valor_p < ALFA ? "rejeitamos" : "não rejeitamos"} H₀</b>.
      Na população a diferença existe (${br(100 * fm.pop_diferenca, 1)} p.p. a favor do melhor de 5), mas com só ${fm.n1}
      partidas melhor de 5 na amostra o teste fica no limite da significância.</div>
  </section>
  <section class="painel-aba" data-p="canh" hidden>
    <h3>Canhotos levam vantagem sobre destros?</h3>
    <p>Diz-se que canhotos têm vantagem porque os adversários estão menos acostumados com eles. Olhamos só os
      <b>duelos canhoto × destro</b> e testamos se o canhoto vence mais da metade: <b>H₀:</b> p = 50% · <b>H₁:</b> p &gt; 50%.</p>
    <div id="pl-canh"></div>
    <div class="conclusao ${c.valor_p < ALFA ? "rej" : "nrej"}"><b>Conclusão:</b> ${c.valor_p < ALFA ? "rejeitamos" : "não rejeitamos"} H₀.
      E a população confirma: em ${br(c.N, 0)} duelos, o canhoto venceu ${pct(c.parametro)}. No circuito principal, ser canhoto
      <b>não</b> dá vantagem nos resultados, o que contraria o senso comum. Os canhotos aparecem em ${pct(c.pct_canhoto_vencedores)}
      das vitórias e em ${pct(c.pct_canhoto_perdedores)} das derrotas, praticamente a mesma fatia.</div>
  </section>`;
  ligarAbas(el, "#abas-bonus");
  const it = a.ics;
  plot(el.querySelector("#g-aces"), [
    ...it.map(g => ({ x: [g.ic_inf, g.ic_sup], y: [g.superficie, g.superficie], mode: "lines", line: { color: CORES.sup[g.superficie], width: 10 },
      showlegend: false, hovertemplate: `IC 95%: ${br(g.ic_inf, 1)} a ${br(g.ic_sup, 1)}<extra>${g.superficie}</extra>` })),
    { x: it.map(g => g.media), y: it.map(g => g.superficie), mode: "markers", showlegend: false,
      marker: { color: "#dcf04a", size: 16, line: { color: "#14211b", width: 2 } }, customdata: it.map(g => g.n),
      hovertemplate: "amostra: %{x:.1f} aces (n = %{customdata})<extra></extra>" },
    { x: it.map(g => g.parametro), y: it.map(g => g.superficie), mode: "markers", showlegend: false,
      marker: { color: CORES.pop, size: 22, symbol: "line-ns", line: { color: CORES.pop, width: 4 } },
      hovertemplate: "população: %{x:.1f} aces<extra></extra>" },
  ], { height: 280, title: { text: "Aces por partida: IC 95% da média por superfície", x: 0, font: { size: 16, family: "Barlow Condensed" } },
    xaxis: { title: "aces por partida", showgrid: true, gridcolor: "rgba(137,135,129,.22)" }, margin: { l: 70, r: 20, t: 50, b: 50 } });
  placar(el.querySelector("#pl-fmt"), [
    { rot: "Melhor de 5 (amostra)", num: pct(fm.p1), sub: `n = ${fm.n1}` },
    { rot: "Melhor de 3 (amostra)", num: pct(fm.p2), sub: `n = ${fm.n2}` },
    { rot: "Diferença", num: `${br(100 * fm.diferenca, 1)} p.p.`, sub: `IC 95%: ${br(100 * fm.ic_inf, 1)} a ${br(100 * fm.ic_sup, 1)} p.p.` },
    { rot: "z · valor-p", num: `${br(fm.estatistica, 2)} · ${br(fm.valor_p, 3)}` },
    { rot: "Diferença real", num: `${br(100 * fm.pop_diferenca, 1)} p.p.`, sub: `${pct(fm.pop_p1)} × ${pct(fm.pop_p2)}` },
  ]);
  katexEm(el.querySelector("#f-fmt"), String.raw`z=\frac{\hat p_5-\hat p_3}{\sqrt{\hat p(1-\hat p)\left(\frac1{n_5}+\frac1{n_3}\right)}}\quad\text{com } \hat p=\frac{x_5+x_3}{n_5+n_3}`);
  placar(el.querySelector("#pl-canh"), [
    { rot: "Duelos na amostra", num: c.n },
    { rot: "Canhoto venceu (amostra)", num: pct(c.estimativa), sub: `IC 95%: ${pct(c.ic_inf)} a ${pct(c.ic_sup)}` },
    { rot: "Valor-p", num: br(c.valor_p, 4) },
    { rot: "População", num: pct(c.parametro), sub: `${br(c.N, 0)} duelos` },
  ]);
}
