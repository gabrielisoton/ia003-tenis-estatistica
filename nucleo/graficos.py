"""Gráficos e o painel descritivo compartilhado pelos Painéis 1 (população) e 2 (amostra).

Usar a MESMA função nos dois painéis garante que população e amostra sejam
comparadas exatamente com os mesmos gráficos e medidas.

Paleta validada para daltonismo (scripts do skill de dataviz):
- superfícies: dura azul, saibro terracota, grama verde-água, carpete cinza (extinta);
- população violeta × amostra amarelo "bola de tênis";
- Top N magenta × demais cinza.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from nucleo.dados import br, pct

COR_POP = "#6250d6"     # População (parâmetros)
COR_AM = "#c98500"      # Amostra (estatísticas)
COR_TOP = "#d55181"     # Top N
COR_DEMAIS = "#898781"  # Demais jogadores
COR_ERRO = "#e34948"
COR_NEUTRA = "#898781"
CORES = {"População": COR_POP, "Amostra": COR_AM}
CORES_SUP = {"Dura": "#2a78d6", "Saibro": "#eb6834", "Grama": "#1baf7a", "Carpete": "#898781"}

QUALI = {
    "superficie": "Superfície",
    "nivel": "Nível do torneio",
    "melhor_de": "Formato (sets)",
    "rodada": "Rodada",
    "mao_vencedor": "Mão do vencedor",
    "ambiente": "Quadra aberta/coberta",
    "favorito_venceu": "Favorito (melhor ranking) venceu?",
    "set_decisivo": "Foi ao set decisivo?",
}
QUANT = {
    "minutos": "Duração (minutos)",
    "aces_total": "Aces na partida (2 jogadores)",
    "duplas_faltas_total": "Duplas faltas na partida",
    "idade_vencedor": "Idade do vencedor (anos)",
    "altura_vencedor": "Altura do vencedor (cm)",
    "sets_jogados": "Sets jogados",
    "dif_ranking": "Diferença de ranking entre os jogadores",
}
# largura das faixas do histograma: variáveis inteiras usam faixas inteiras
LARGURA = {"minutos": 5, "aces_total": 1, "duplas_faltas_total": 1, "idade_vencedor": 1,
           "altura_vencedor": 1, "sets_jogados": 1}
NOTAS = {
    "minutos": "Faixas de 5 minutos. A cauda à direita vem das partidas melhor de 5 e das maratonas: "
               "Isner × Mahut, em Wimbledon 2010, durou 665 minutos.",
    "aces_total": "Faixas de 1 ace, porque é uma contagem inteira. A curva sobe até cerca de 6–9 aces e "
                  "depois desce devagar: poucas partidas de grandes sacadores, ou de 5 sets, puxam a média "
                  "para cima da mediana.",
    "duplas_faltas_total": "Contagem inteira. A maioria das partidas tem poucas duplas faltas, e a cauda "
                           "longa vem de jogos longos ou de dias ruins no saque.",
    "idade_vencedor": "A idade é contínua (anos com decimais), agrupada em faixas de 1 ano.",
    "altura_vencedor": "Os picos em 180, 183, 185, 188, 191 e 193 cm são reais. As alturas são registradas "
                       "em pés e polegadas e depois convertidas: 6'0\" = 183 cm, 6'1\" = 185 cm, "
                       "6'2\" = 188 cm. Por isso aparece um pico a cada 2,5 cm, que é uma polegada.",
    "sets_jogados": "Melhor de 3 termina em 2 ou 3 sets; melhor de 5, em 3, 4 ou 5.",
}
FAIXAS_RANKING = [(1, 5), (6, 10), (11, 25), (26, 50), (51, 100), (101, 200), (201, 100_000)]
ORDENS = {
    "superficie": ["Dura", "Saibro", "Grama", "Carpete"],
    "nivel": ["Grand Slam", "ATP Finals", "Masters 1000", "ATP 500", "ATP 250"],
    "rodada": ["1ª rodada (R128)", "R64", "R32", "Oitavas (R16)", "Quartas", "Semifinal",
               "Final", "Fase de grupos", "3rd/4th"],
    "melhor_de": ["Melhor de 3", "Melhor de 5"],
    "favorito_venceu": ["Sim", "Não"],
    "set_decisivo": ["Sim", "Não"],
}


def como_ler(texto: str) -> None:
    """Caixa didática 'Como ler' (para estudar e para o vídeo)."""
    with st.expander("📖 Como ler este gráfico", expanded=False):
        st.markdown(texto)


# ------------------------------------------------------------------ filtros
def filtros_sidebar(df: pd.DataFrame) -> dict:
    st.sidebar.header("Filtros")
    sup = st.sidebar.multiselect("Superfície", ORDENS["superficie"], default=ORDENS["superficie"])
    niv = st.sidebar.multiselect("Nível do torneio", ORDENS["nivel"], default=ORDENS["nivel"])
    a0, a1 = int(df["ano"].min()), int(df["ano"].max())
    anos = st.sidebar.slider("Anos", a0, a1, (a0, a1))
    top = st.sidebar.selectbox("Partidas com jogadores do…", ["Todas", "Top 5", "Top 10", "Top 20",
                                                              "Top 50", "Top 100"],
                               help="Mantém só partidas em que pelo menos um dos jogadores estava "
                                    "nesse corte do ranking no início do torneio.")
    st.sidebar.caption("Os filtros valem para todos os gráficos desta página.")
    return {"superficie": sup, "nivel": niv, "anos": anos, "top": top}


def filtrar(df: pd.DataFrame, f: dict) -> pd.DataFrame:
    m = df["superficie"].isin(f["superficie"]) & df["nivel"].isin(f["nivel"])
    m &= df["ano"].between(*f["anos"])
    if f.get("top", "Todas") != "Todas":
        n = int(f["top"].split()[1])
        m &= (df["ranking_vencedor"] <= n) | (df["ranking_perdedor"] <= n)
    return df[m]


# ------------------------------------------------------------------ medidas
def medidas(df: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for col, nome in QUANT.items():
        x = df[col].dropna()
        if x.empty:
            continue
        linhas.append({
            "Variável": nome, "n válido": len(x), "Média": x.mean(), "Mediana": x.median(),
            "Desvio-padrão": x.std(ddof=1), "CV (%)": 100 * x.std(ddof=1) / x.mean() if x.mean() else np.nan,
            "Mínimo": x.min(), "Q1": x.quantile(0.25), "Q3": x.quantile(0.75), "Máximo": x.max(),
            "Assimetria": x.skew(),
        })
    return pd.DataFrame(linhas).set_index("Variável")


def frequencias(df: pd.DataFrame, col: str) -> pd.DataFrame:
    cont = df[col].value_counts(dropna=True)
    ordem = [c for c in ORDENS.get(col, []) if c in cont.index] or list(cont.index)
    cont = cont.reindex(ordem)
    return pd.DataFrame({"Frequência": cont, "Proporção": cont / cont.sum()})


def faixa_ranking(serie: pd.Series) -> pd.Series:
    rot = [f"{a}–{b}" if b < 100_000 else f"{a}+" for a, b in FAIXAS_RANKING]
    bordas = [a - 0.5 for a, _ in FAIXAS_RANKING] + [100_000]
    return pd.cut(serie, bordas, labels=rot)


def _layout(fig: go.Figure, titulo: str, altura: int = 320) -> go.Figure:
    fig.update_layout(
        title=dict(text=titulo, x=0, font=dict(size=15)),
        height=altura, margin=dict(l=10, r=10, t=90, b=10),
        legend=dict(orientation="h", y=1.02, yanchor="bottom", x=0, title=None),
        barcornerradius=4, bargap=0.25, bargroupgap=0.06,
        hoverlabel=dict(font_size=13), separators=",.",
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor="rgba(137,135,129,0.25)", zeroline=False)
    return fig


# ------------------------------------------------------------------ gráficos
def barras(df: pd.DataFrame, col: str, rotulo: str, ref: pd.DataFrame | None = None,
           top: int | None = None, titulo: str | None = None) -> go.Figure:
    fig = go.Figure()
    series = [(rotulo, df)] if ref is None else [("População", ref), (rotulo, df)]
    base = ref if ref is not None else df
    cats = base[col].value_counts().head(top).index if top else None
    for nome, dado in series:
        fr = frequencias(dado, col) if col in df else None
        if top:
            fr = fr.reindex(cats).fillna(0)
            fr["Frequência"] = fr["Frequência"].astype(int)
        # cor segue a entidade: superfícies sempre com a cor da quadra quando há uma só série
        cor = ([CORES_SUP.get(c, COR_NEUTRA) for c in fr.index]
               if col == "superficie" and ref is None else CORES.get(nome, COR_POP))
        fig.add_bar(
            x=fr.index.astype(str), y=fr["Proporção"], name=nome, marker_color=cor,
            customdata=np.c_[fr["Frequência"]],
            text=[pct(p) for p in fr["Proporção"]], textposition="outside",
            hovertemplate="<b>%{x}</b><br>%{y:.1%} das partidas (n = %{customdata[0]:,})<extra>"
                          + nome + "</extra>",
        )
    fig.update_yaxes(tickformat=".0%", title="% das partidas")
    return _layout(fig, titulo or QUALI.get(col, col), 360)


def barras_faixa_ranking(df: pd.DataFrame, rotulo: str, ref: pd.DataFrame | None = None) -> go.Figure:
    def tabela(d):
        f = faixa_ranking(d["dif_ranking"].dropna()).value_counts(sort=False)
        return pd.DataFrame({"Frequência": f, "Proporção": f / f.sum()})
    fig = go.Figure()
    for nome, dado in ([(rotulo, df)] if ref is None else [("População", ref), (rotulo, df)]):
        fr = tabela(dado)
        fig.add_bar(x=fr.index.astype(str), y=fr["Proporção"], name=nome, marker_color=CORES.get(nome),
                    text=[pct(p) for p in fr["Proporção"]], textposition="outside",
                    customdata=np.c_[fr["Frequência"]],
                    hovertemplate="diferença de %{x} posições<br>%{y:.1%} das partidas "
                                  "(n = %{customdata[0]:,})<extra>" + nome + "</extra>")
    fig.update_yaxes(tickformat=".0%", title="% das partidas")
    fig.update_xaxes(title="Diferença de posições no ranking entre os dois jogadores")
    return _layout(fig, "Diferença de ranking entre os jogadores (em faixas)", 380)


def histograma(df: pd.DataFrame, col: str, rotulo: str, ref: pd.DataFrame | None = None) -> go.Figure:
    fig = go.Figure()
    series = [(rotulo, df)] if ref is None else [("População", ref), (rotulo, df)]
    base = ref if ref is not None else df
    lo, hi = base[col].quantile([0.0, 0.995])
    w = LARGURA.get(col, max((hi - lo) / 40, 1))
    inicio = (np.floor(lo / w) * w) - (0.5 if w == 1 else 0)  # faixas centradas nos inteiros
    for nome, dado in series:
        fig.add_histogram(
            x=dado.loc[dado[col] <= hi, col], name=nome, histnorm="percent",
            xbins=dict(start=inicio, end=hi + w, size=w),
            marker_color=CORES.get(nome, COR_POP), opacity=0.6 if ref is not None else 0.9,
            hovertemplate="%{x}: %{y:.1f}% das partidas<extra>" + nome + "</extra>",
        )
        media, mediana = dado[col].mean(), dado[col].median()
        sozinho = ref is None
        fig.add_vline(x=media, line_color=CORES.get(nome), line_width=2,
                      annotation_text=f"média {br(media, 1)}" if sozinho else None,
                      annotation_position="top right")
        fig.add_vline(x=mediana, line_color=CORES.get(nome), line_width=2, line_dash="dot",
                      annotation_text=f"mediana {br(mediana, 1)}" if sozinho else None,
                      annotation_position="top left")
    fig.update_layout(barmode="overlay", bargap=0.08)
    fig.update_yaxes(title="% das partidas")
    fig.update_xaxes(title=QUANT.get(col, col))
    return _layout(fig, f"Distribuição — {QUANT.get(col, col)}<br><sup>linha contínua = média · "
                        "pontilhada = mediana · os 0,5% maiores valores ficam fora do gráfico "
                        "(aparecem no boxplot)</sup>", 400)


def boxplot(df: pd.DataFrame, col: str, rotulo: str, ref: pd.DataFrame | None = None) -> go.Figure:
    fig = go.Figure()
    series = [(rotulo, df)] if ref is None else [("População", ref), (rotulo, df)]
    for nome, dado in series:
        fig.add_box(x=dado[col], name=nome, marker_color=CORES.get(nome), boxmean=True,
                    orientation="h", marker_size=4)
    fig.update_xaxes(title=QUANT.get(col, col))
    fig.update_layout(showlegend=False)
    return _layout(fig, "Boxplot (caixa = 50% centrais · traço = mediana · tracejado = média)",
                   240 if ref is None else 300)


def primeira_rodada(df: pd.DataFrame) -> pd.DataFrame:
    """Em que rodada cada tipo de torneio começa (explica por que a R32 domina)."""
    ordem = {r: i for i, r in enumerate(ORDENS["rodada"])}
    ordem["Fase de grupos"] = -1
    linhas = []
    for niv in ORDENS["nivel"]:
        g = df[df["nivel"] == niv]
        if g.empty:
            continue
        prim = g.groupby(["torneio", "ano"])["rodada"].apply(lambda r: min(r, key=lambda x: ordem.get(x, 99)))
        principal = prim.value_counts(normalize=True)
        linhas.append({"Nível": niv, "% das partidas da base": len(g) / len(df),
                       "Começa geralmente em": principal.index[0], "% dos torneios": principal.iloc[0]})
    t = pd.DataFrame(linhas)
    t["% das partidas da base"] = t["% das partidas da base"].map(pct)
    t["% dos torneios"] = t["% dos torneios"].map(pct)
    return t


# ------------------------------------------------------------- painel inteiro
def kpis(df: pd.DataFrame) -> None:
    c = st.columns(4)
    c[0].metric("Partidas", br(len(df), 0))
    c[1].metric("Período", f"{df['ano'].min()}–{df['ano'].max()}" if len(df) else "—")
    c[2].metric("Torneios (edições)", br(df[['torneio', 'ano']].drop_duplicates().shape[0], 0))
    jogadores = pd.concat([df["vencedor"], df["perdedor"]]).nunique()
    c[3].metric("Jogadores distintos", br(jogadores, 0))


def painel_descritivo(df: pd.DataFrame, rotulo: str, ref: pd.DataFrame | None = None) -> None:
    if df.empty:
        st.warning("Nenhuma partida com esses filtros.")
        return
    kpis(df)
    abas = st.tabs(["Variáveis qualitativas", "Variáveis quantitativas", "Tabelas"])

    with abas[0]:
        como_ler("Cada barra mostra **que fração das partidas** cai em cada categoria. As barras de um "
                 "gráfico somam 100%. Passe o mouse para ver o número de partidas."
                 + (" A barra **violeta** é a população inteira e a **amarela** é a amostra: quanto mais "
                    "parecidas, melhor a amostra representa a população." if ref is not None else ""))
        principais = ["superficie", "nivel", "melhor_de", "mao_vencedor",
                      "favorito_venceu", "set_decisivo"]
        for i in range(0, len(principais), 2):
            cols = st.columns(2)
            for c, var in zip(cols, principais[i:i + 2]):
                c.plotly_chart(barras(df, var, rotulo, ref), width="stretch")
        st.plotly_chart(barras(df, "rodada", rotulo, ref, titulo="Rodada — % das partidas jogadas em cada rodada"),
                        width="stretch")
        st.caption("**Por que a R32 tem mais partidas?** Quase metade da base é de torneios ATP 250, que têm "
                   "chave de 28 ou 32 jogadores e **começam na R32**. Só os Grand Slams começam na R128, e os "
                   "Masters começam na R64 ou na R128. Em cada torneio, a 1ª rodada é a que tem mais jogos.")
        st.dataframe(primeira_rodada(df), hide_index=True, width="stretch")
        st.plotly_chart(barras(df, "pais_vencedor", rotulo, ref, top=10, titulo="Top 10 países dos vencedores"),
                        width="stretch")

    with abas[1]:
        como_ler("O **histograma** mostra como os valores se distribuem: cada barra é uma faixa de valores, e a "
                 "altura indica a fração das partidas nessa faixa. A **média** é o centro de gravidade; a "
                 "**mediana** separa as partidas em duas metades. Quando há cauda longa à direita, a média fica "
                 "acima da mediana. O **boxplot** resume a mesma distribuição: a caixa contém os 50% centrais.")
        opcoes = [k for k in QUANT if k != "dif_ranking"] + ["dif_ranking"]
        var = st.selectbox("Variável quantitativa", opcoes, format_func=QUANT.get, key=f"quant_{rotulo}")
        if var == "dif_ranking":
            st.plotly_chart(barras_faixa_ranking(df, rotulo, ref), width="stretch")
            x = df[var].dropna()
            st.caption(f"Metade das partidas tem diferença de até **{br(x.median(), 0)} posições** (mediana). "
                       f"25% têm até {br(x.quantile(.25), 0)} e 75% têm até {br(x.quantile(.75), 0)}. A média "
                       f"({br(x.mean(), 0)}) é inflada por poucos jogos muito desiguais, que chegam a "
                       f"{br(x.max(), 0)} posições, por isso usamos faixas. Na página **Explorar** essas faixas "
                       "aparecem ligadas à chance de o favorito vencer.")
        else:
            st.plotly_chart(histograma(df, var, rotulo, ref), width="stretch")
            if var in NOTAS:
                st.caption(NOTAS[var])
            st.plotly_chart(boxplot(df, var, rotulo, ref), width="stretch")
        x = df[var].dropna()
        c = st.columns(5)
        c[0].metric("Média", br(x.mean()))
        c[1].metric("Mediana", br(x.median()))
        c[2].metric("Desvio-padrão", br(x.std(ddof=1)))
        c[3].metric("Assimetria", br(x.skew()))
        c[4].metric("n válido", br(len(x), 0))
        if x.skew() > 1:
            st.info("Distribuição assimétrica à direita: a média é puxada pelas partidas extremas e fica acima "
                    "da mediana. A mediana descreve melhor a partida típica.")

    with abas[2]:
        st.subheader("Medidas descritivas — variáveis quantitativas")
        st.dataframe(medidas(df).style.format(precision=2, thousands=".", decimal=","), width="stretch")
        st.subheader("Frequências — variáveis qualitativas")
        var = st.selectbox("Variável qualitativa", list(QUALI), format_func=QUALI.get, key=f"quali_{rotulo}")
        tab = frequencias(df, var)
        tab["Proporção"] = tab["Proporção"].map(pct)
        st.dataframe(tab, width="stretch")


# --------------------------------------------------------------- inferência
def grafico_ic(est: float, li: float, ls: float, h0: float, parametro: float,
               fmt, titulo: str, proporcao: bool = False) -> go.Figure:
    """Estimativa pontual + IC (amostra) contra H0 e o parâmetro populacional real."""
    fig = go.Figure()
    fig.add_scatter(x=[li, ls], y=["IC 95%", "IC 95%"], mode="lines", line=dict(color=COR_AM, width=6),
                    name="IC 95% (amostra)", hovertemplate="%{x}<extra>limite do IC</extra>")
    fig.add_scatter(x=[est], y=["IC 95%"], mode="markers", name="Estimativa pontual (amostra)",
                    marker=dict(color=COR_AM, size=16, line=dict(color="white", width=2)),
                    hovertemplate=f"estimativa: {fmt(est)}<extra></extra>")
    lado_h0, lado_par = ("top left", "top right") if h0 <= parametro else ("top right", "top left")
    fig.add_vline(x=h0, line_dash="dash", line_color=COR_NEUTRA, line_width=2,
                  annotation_text=f"H₀: {fmt(h0)}", annotation_position=lado_h0)
    fig.add_vline(x=parametro, line_color=COR_POP, line_width=3,
                  annotation_text=f"População: {fmt(parametro)}", annotation_position=lado_par)
    pad = (max(ls, h0, parametro) - min(li, h0, parametro)) * 0.15
    fig.update_xaxes(range=[min(li, h0, parametro) - pad, max(ls, h0, parametro) + pad],
                     tickformat=".0%" if proporcao else None)
    fig.update_yaxes(showticklabels=False, showgrid=False)
    fig.update_layout(showlegend=True)
    return _layout(fig, titulo, 230)


def grafico_cobertura(ics: list, parametro: float, fmt, proporcao: bool = False) -> tuple[go.Figure, float]:
    acerta = [li <= parametro <= ls for _, li, ls in ics]
    fig = go.Figure()
    for nome, cor, flag in [("IC contém o parâmetro", COR_AM, True),
                            ("IC NÃO contém o parâmetro", COR_ERRO, False)]:
        xs, ys = [], []
        for i, ((_, li, ls), ok) in enumerate(zip(ics, acerta), start=1):
            if ok == flag:
                xs += [li, ls, None]
                ys += [i, i, None]
        fig.add_scatter(x=xs, y=ys, mode="lines", line=dict(color=cor, width=2), name=nome, hoverinfo="skip")
    fig.add_scatter(x=[e for e, _, _ in ics], y=list(range(1, len(ics) + 1)), mode="markers",
                    marker=dict(color=COR_NEUTRA, size=4), name="Estimativa", showlegend=False,
                    hovertemplate="amostra %{y}: %{x}<extra></extra>")
    fig.add_vline(x=parametro, line_color=COR_POP, line_width=3,
                  annotation_text=f"Parâmetro populacional: {fmt(parametro)}")
    fig.update_yaxes(title="Amostra simulada nº", showgrid=False)
    fig.update_xaxes(tickformat=".0%" if proporcao else None)
    taxa = float(np.mean(acerta))
    return _layout(fig, f"{len(ics)} amostras simuladas · {pct(taxa)} dos ICs contêm o parâmetro", 520), taxa


def grafico_ics_grupos(itens: list[dict], fmt, titulo: str, cores: dict | None = None) -> go.Figure:
    """Vários ICs lado a lado (ex.: aces por superfície), com o parâmetro real de cada grupo."""
    fig = go.Figure()
    for it in itens:
        cor = (cores or {}).get(it["grupo"], COR_AM)
        fig.add_scatter(x=[it["ic_inf"], it["ic_sup"]], y=[it["grupo"]] * 2, mode="lines",
                        line=dict(color=cor, width=8), showlegend=False,
                        hovertemplate=f"IC 95%: {fmt(it['ic_inf'])} a {fmt(it['ic_sup'])}<extra>{it['grupo']}</extra>")
        fig.add_scatter(x=[it["media"]], y=[it["grupo"]], mode="markers", showlegend=False,
                        marker=dict(color=cor, size=15, line=dict(color="white", width=2)),
                        hovertemplate=f"amostra: {fmt(it['media'])} (n = {it['n']})<extra>{it['grupo']}</extra>")
        fig.add_scatter(x=[it["parametro"]], y=[it["grupo"]], mode="markers", showlegend=False,
                        marker=dict(color=COR_POP, size=14, symbol="line-ns", line=dict(color=COR_POP, width=4)),
                        hovertemplate=f"população: {fmt(it['parametro'])}<extra>{it['grupo']}</extra>")
    fig.add_scatter(x=[None], y=[None], mode="markers", name="média da amostra e IC 95%",
                    marker=dict(color=COR_NEUTRA, size=12))
    fig.add_scatter(x=[None], y=[None], mode="markers", name="média da população",
                    marker=dict(color=COR_POP, size=14, symbol="line-ns", line=dict(color=COR_POP, width=4)))
    return _layout(fig, titulo, 300)


def comparacao_medidas(pop: pd.DataFrame, am: pd.DataFrame) -> pd.DataFrame:
    mp, ma = medidas(pop), medidas(am)
    linhas = []
    for var in mp.index:
        for m in ["Média", "Mediana", "Desvio-padrão"]:
            p, a = mp.loc[var, m], ma.loc[var, m]
            linhas.append({"Variável": var, "Medida": m, "População": p, "Amostra": a,
                           "Diferença": a - p, "Diferença (%)": 100 * (a - p) / p if p else np.nan})
    return pd.DataFrame(linhas)


def comparacao_proporcoes(pop: pd.DataFrame, am: pd.DataFrame) -> pd.DataFrame:
    linhas = []
    for var, nome in QUALI.items():
        if var == "rodada":
            continue
        fp, fa = frequencias(pop, var)["Proporção"], frequencias(am, var)["Proporção"]
        for cat in fp.index:
            a = fa.get(cat, 0.0)
            linhas.append({"Variável": nome, "Categoria": cat, "População (%)": 100 * fp[cat],
                           "Amostra (%)": 100 * a, "Diferença (p.p.)": 100 * (a - fp[cat])})
    return pd.DataFrame(linhas)
