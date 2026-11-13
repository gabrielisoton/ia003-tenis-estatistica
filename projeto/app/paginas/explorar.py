"""Explorar — Top N × demais, ranking × zebras e linha do tempo (população inteira)."""
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nucleo import analises as an
from nucleo import dados
from nucleo import graficos as g
from nucleo.dados import br, pct
from nucleo.idiomas import T, tr

st.title(T("Explorar · O que separa os melhores do resto?", "Explore · What sets the best apart from the rest?"))
st.caption(T("Análises descritivas feitas com a **população inteira** (66.819 partidas do circuito principal, "
             "2000–2025). Ajudam a entender o jogo e conversam com IA.",
             "Descriptive analyses of the **whole population** (66,819 main-tour matches, "
             "2000–2025). They help explain the game and connect with AI."))

pop = dados.populacao()


@st.cache_data
def longo():
    return an.longo(pop)


@st.cache_data
def comparar(N: int, superficie: str) -> dict:
    return an.top_vs_demais(longo(), N, superficie)


aba_top, aba_rank, aba_tempo = st.tabs([T("🏆 Top N × demais", "🏆 Top N vs the rest"),
                                        T("🎯 Ranking e zebras", "🎯 Ranking and upsets"),
                                        T("📈 Linha do tempo", "📈 Timeline")])

# ------------------------------------------------------------------ Top N
with aba_top:
    c1, c2 = st.columns([1, 2])
    N = c1.select_slider(T("Comparar o Top…", "Compare the Top…"), options=an.TOPS, value=10,
                         format_func=lambda n: f"Top {n}", key="tp_n")
    sup = c2.radio(T("Superfície", "Surface"), ["Todas", "Dura", "Saibro", "Grama"], horizontal=True,
                   format_func=tr, key="tp_sup")
    r = comparar(N, sup)
    t, d = r["top"], r["demais"]
    recorte_sup = tr(sup).lower() if sup != "Todas" else T("todas as superfícies", "all surfaces")
    g.como_ler(T(f"Cada partida tem dois jogadores. Aqui olhamos **cada jogador em cada partida** (por isso há "
                 f"mais linhas do que partidas) e o classificamos como **Top {N}** se ele estava entre os {N} primeiros "
                 f"do ranking no início daquele torneio. Um mesmo jogador pode estar no Top {N} num ano e fora em "
                 f"outro. As porcentagens são **somas de pontos**: por exemplo, \"pontos ganhos no saque\" = todos "
                 f"os pontos que o grupo venceu sacando ÷ todos os pontos que sacou.",
                 f"Every match has two players. Here we look at **each player in each match** (which is why there "
                 f"are more rows than matches) and label them **Top {N}** if they were among the top {N} in the "
                 f"ranking at the start of that tournament. The same player can be in the Top {N} one year and out "
                 f"of it the next. The percentages are **sums of points**: for example, \"service points won\" = all "
                 f"the points the group won on serve ÷ all the points it served."))
    m = st.columns(4)
    m[0].metric(T(f"Top {N} vence quem está fora do Top {N}", f"Top {N} beats players outside the Top {N}"),
                pct(r["duelo"]["vitorias_top"]),
                help=T(f"{br(r['duelo']['n'], 0)} partidas Top × não-Top", f"{br(r['duelo']['n'], 0)} Top vs non-Top matches"))
    m[1].metric(T(f"Vitórias do Top {N} (geral)", f"Top {N} wins (overall)"), pct(t["vitorias"]))
    m[2].metric(T("Vitórias dos demais", "Wins by the rest"), pct(d["vitorias"]))
    m[3].metric(T(f"Jogador-partidas do Top {N}", f"Top {N} player-matches"), br(t["n"], 0),
                help=T(f"{t['n_jogadores']} jogadores diferentes", f"{t['n_jogadores']} different players"))

    # onde eles se diferenciam: diferença em pontos percentuais
    pp = T("p.p.", "pp")
    pcts = [(k, nome) for k, nome, u, _ in an.METRICAS if u == "%" and k not in ("vitorias", "canhoto")]
    difs = [(tr(nome), 100 * (t[k] - d[k])) for k, nome in pcts]
    difs.sort(key=lambda x: x[1])
    fig = go.Figure(go.Bar(
        x=[v for _, v in difs], y=[n for n, _ in difs], orientation="h",
        marker_color=[g.COR_TOP if v >= 0 else g.COR_DEMAIS for _, v in difs],
        text=[f"{'+' if v >= 0 else ''}{br(v, 1)} {pp}" for _, v in difs], textposition="outside",
        hovertemplate="%{y}: %{x:+.1f} " + pp + "<extra></extra>"))
    fig.update_xaxes(title=T(f"Top {N} − demais (pontos percentuais)", f"Top {N} − the rest (percentage points)"),
                     zeroline=True, zerolinecolor="rgba(137,135,129,.6)")
    st.plotly_chart(g._layout(fig, T(f"Onde o Top {N} se diferencia ({recorte_sup})",
                                     f"Where the Top {N} stands out ({recorte_sup})"), 420),
                    width="stretch")
    maior = difs[-1]
    st.info(T(f"**Leitura:** a maior vantagem do Top {N} está em **{maior[0].lower()}** "
              f"(+{br(maior[1], 1)} p.p.). Diferenças de 3 a 5 pontos percentuais por ponto parecem pequenas, mas "
              "num jogo com mais de 150 pontos viram vários games e, no fim, a vitória. O tênis é decidido nas margens.",
              f"**Takeaway:** the Top {N}'s biggest edge is in **{maior[0].lower()}** "
              f"(+{br(maior[1], 1)} pp). Gaps of 3 to 5 percentage points per point look small, but "
              "in a match with more than 150 points they add up to several games and, in the end, the win. "
              "Tennis is decided at the margins."))

    linhas = []
    col_top, col_dem, col_dif = f"Top {N}", T("Demais", "Rest"), T("Diferença", "Difference")
    for k, nome, u, desc in an.METRICAS:
        fmt = (lambda v: pct(v)) if u == "%" else (lambda v: br(v, 2 if u == "n" else 1))
        dif = (t[k] - d[k]) * (100 if u == "%" else 1)
        linhas.append({T("Métrica", "Metric"): tr(nome), col_top: fmt(t[k]), col_dem: fmt(d[k]),
                       col_dif: f"{'+' if dif >= 0 else ''}{br(dif, 2 if u == 'n' else 1)}{' ' + pp if u == '%' else ''}",
                       T("O que mede", "What it measures"): tr(desc)})
    c1, c2 = st.columns([3, 2])
    c1.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch", height=500)
    with c2:
        st.markdown(T(f"**Quem mais jogou como Top {N}** ({recorte_sup})",
                      f"**Who played the most as a Top {N} player** ({recorte_sup})"))
        col_v = T("% vitórias", "% wins")
        jog = pd.DataFrame(r["jogadores"]).rename(columns={"jogador": T("Jogador", "Player"),
                                                           "partidas": T("Partidas", "Matches"),
                                                           "vitorias": col_v})
        jog[col_v] = jog[col_v].map(pct)
        st.dataframe(jog, hide_index=True, width="stretch", height=460)
    st.caption(T("**Sobre o corte:** Top 5 e Top 10 mostram a elite (Big 3 e poucos outros), com grupos menores. "
                 "Top 50 e Top 100 comparam o \"jogador de circuito principal\" com quem vem dos qualificatórios e "
                 "Challengers. O corte que mais conta uma história é o **Top 10**: elite × resto.",
                 "**About the cut-off:** Top 5 and Top 10 show the elite (the Big 3 and a few others), in smaller "
                 "groups. Top 50 and Top 100 compare the \"main-tour player\" with those coming through qualifying "
                 "and Challengers. The cut-off that tells the clearest story is the **Top 10**: elite vs the rest."))

# ------------------------------------------------------------------ ranking
with aba_rank:
    st.subheader(T("Quanto maior a diferença de ranking, maior a chance de o favorito vencer?",
                   "The bigger the ranking gap, the more likely the favourite wins?"))
    fx = pd.DataFrame(an.faixas_ranking(pop))
    n_pop, n_bo5, n_bo3 = T("População", "Population"), tr("Melhor de 5"), tr("Melhor de 3")
    fig = go.Figure()
    fig.add_scatter(x=fx["faixa"], y=fx["pop_taxa"], mode="lines+markers", name=T("População (todas)", "Population (all)"),
                    line=dict(color=g.COR_POP, width=3), marker=dict(size=9),
                    customdata=fx["pop_n"], hovertemplate="%{x}: %{y:.1%} (n = %{customdata:,})<extra>" + n_pop + "</extra>")
    fig.add_scatter(x=fx["faixa"], y=fx["bo5"], mode="lines", name=T("População — melhor de 5", "Population — best of 5"),
                    line=dict(color=g.COR_POP, width=2, dash="dot"), hovertemplate="%{x}: %{y:.1%}<extra>" + n_bo5 + "</extra>")
    fig.add_scatter(x=fx["faixa"], y=fx["bo3"], mode="lines", name=T("População — melhor de 3", "Population — best of 3"),
                    line=dict(color=g.COR_POP, width=2, dash="dash"), hovertemplate="%{x}: %{y:.1%}<extra>" + n_bo3 + "</extra>")
    fig.add_hline(y=0.5, line_dash="dash", line_color=g.COR_NEUTRA, annotation_text=T("50% = moeda", "50% = coin flip"))
    fig.update_yaxes(tickformat=".0%", title=T("% de vitórias do favorito", "% of wins by the favourite"), range=[0.3, 1])
    fig.update_xaxes(title=T("Diferença de posições no ranking", "Difference in ranking places"))
    st.plotly_chart(g._layout(fig, T("Vitória do favorito por faixa de diferença de ranking",
                                     "Favourite's win rate by ranking-gap band"), 460), width="stretch")
    g.como_ler(T("Cada ponto é a % de partidas vencidas pelo jogador mais bem ranqueado, para jogos com aquela "
                 "diferença de posições. Quando os dois estão próximos no ranking (1–5 posições), o favorito vence "
                 "pouco mais que uma moeda. Com mais de 200 posições de diferença, vence quase 4 em cada 5. As linhas "
                 "tracejada e pontilhada separam os jogos melhor de 3 e melhor de 5.",
                 "Each point is the % of matches won by the higher-ranked player, for matches with that "
                 "gap in places. When the two are close in the ranking (1–5 places), the favourite wins "
                 "only a little more often than a coin flip. With a gap of more than 200 places, they win almost 4 "
                 "times out of 5. The dashed and dotted lines split best-of-3 and best-of-5 matches."))
    st.info(T("**Conexão com IA:** um modelo de previsão de tênis precisa ser **calibrado**: quando ele diz \"70% de "
              "chance\", o favorito deve vencer cerca de 70% das vezes. Esta curva é o ponto de partida de um modelo "
              "simples, de uma variável só. Repare também que, para a mesma diferença, o favorito vence mais no "
              "**melhor de 5**: jogos longos reduzem a chance de zebra.",
              "**Link to AI:** a tennis prediction model needs to be **calibrated**: when it says \"70% "
              "chance\", the favourite should win about 70% of the time. This curve is the starting point of a "
              "simple, single-variable model. Notice too that, for the same gap, the favourite wins more often in "
              "**best of 5**: longer matches reduce the chance of an upset."))

# ------------------------------------------------------------------ tempo
with aba_tempo:
    lt = pd.DataFrame(an.linha_tempo(pop))
    var = st.selectbox(T("Indicador", "Indicator"), list(an.LINHA_TEMPO),
                       format_func=lambda k: tr(an.LINHA_TEMPO[k][0]), key="lt_var")
    nome, unid = an.LINHA_TEMPO[var]
    nome = tr(nome)
    fig = go.Figure(go.Scatter(x=lt["ano"], y=lt[var], mode="lines+markers", line=dict(color=g.COR_POP, width=3),
                               marker=dict(size=7), customdata=lt["n"],
                               hovertemplate="%{x}: %{y:" + (".1%" if unid == "%" else ".1f") +
                                             "} (%{customdata:,} " + T("partidas", "matches") + ")<extra></extra>"))
    if var == "minutos_bo3_media":
        mediana = T("mediana", "median")
        fig.add_scatter(x=lt["ano"], y=lt["minutos_bo3_mediana"], mode="lines", name=mediana,
                        line=dict(color=g.COR_POP, dash="dot"), hovertemplate=mediana + " %{y:.0f}<extra></extra>")
    if unid == "%":
        fig.update_yaxes(tickformat=".0%")
    fig.update_layout(showlegend=False)
    st.plotly_chart(g._layout(fig, T(f"{nome} por temporada", f"{nome} by season"), 420), width="stretch")
    a0, a1 = lt.iloc[0], lt.iloc[-1]
    v0 = pct(a0[var]) if unid == '%' else br(a0[var], 1)
    v1 = pct(a1[var]) if unid == '%' else br(a1[var], 1)
    st.caption(T(f"De {a0['ano']} a {a1['ano']}: {nome.lower()} foi de {v0} para {v1}. "
                 "Em 2020 houve bem menos partidas por causa da pandemia, então aquele ano oscila mais.",
                 f"From {a0['ano']} to {a1['ano']}: {nome[0].lower() + nome[1:]} went from {v0} to {v1}. "
                 "2020 had far fewer matches because of the pandemic, so that year swings more."))
    st.markdown(T("""
**Destaques:**
- As partidas **ficaram mais longas**: o melhor de 3 passou de cerca de 91 para 109 minutos. Uma hipótese é o jogo
  mais físico, com trocas longas do fundo de quadra. A base não permite testar a causa.
- A **idade dos vencedores subiu** até cerca de 2015 (era do Big 3 e dos veteranos) e depois começou a cair com a
  nova geração.
- A % de vitórias do favorito **subiu na era de domínio do Big 3** (cerca de 68% entre 2009 e 2016) e **voltou a
  cerca de 64%** depois. O circuito ficou mais imprevisível.
""", """
**Highlights:**
- Matches **got longer**: best of 3 went from about 91 to 109 minutes. One hypothesis is a more physical
  game, with long baseline rallies. The database does not allow us to test the cause.
- The **age of winners rose** until about 2015 (the era of the Big 3 and the veterans) and then started to fall
  with the new generation.
- The favourite's win rate **rose during the Big 3's era of dominance** (about 68% between 2009 and 2016) and
  **fell back to about 64%** afterwards. The tour became less predictable.
"""))
