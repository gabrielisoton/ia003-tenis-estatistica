"""Explorar — análises extras com a população: Top N × demais, ranking × zebras, linha do tempo."""
import hashlib
import importlib
from pathlib import Path

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

import analises as an
import dados
import graficos as g
from dados import br, pct

# O Streamlit (inclusive no Cloud, depois de um push) não recarrega módulos locais já importados:
# sem isto, a página nova rodaria com uma versão antiga de analises.py em memória.
an = importlib.reload(an)


@st.cache_resource
def _versao_vista() -> dict:
    return {"md5": None}


# o st.cache_data guarda resultados calculados pela versão anterior de analises.py (a chave do cache só olha o
# código desta página): quando analises.py muda, limpa o cache uma vez para não servir tabelas antigas.
_md5 = hashlib.md5(Path(an.__file__).read_bytes()).hexdigest()
if _versao_vista()["md5"] != _md5:
    st.cache_data.clear()
    _versao_vista()["md5"] = _md5

st.set_page_config(page_title="Extra · Explorar", page_icon="🎾", layout="wide")
st.info("**Extra · fora da avaliação da disciplina.** Página para quem gosta de tênis: usa a população "
        "inteira e não faz parte do trabalho avaliado (Painéis 1–3).", icon="🎾")
st.title("Explorar · O que separa os melhores do resto?")
st.caption("Análises extras, descritivas, feitas com a **população inteira** (66.819 partidas). Vão além do "
           "exigido no trabalho, mas ajudam a entender o jogo e conversam com IA.")

pop, am = dados.populacao(), dados.amostra()


@st.cache_data
def longo():
    return an.longo(pop)


@st.cache_data
def comparar(N: int, superficie: str) -> dict:
    return an.top_vs_demais(longo(), N, superficie)


aba_top, aba_rank, aba_tempo = st.tabs(["🏆 Top N × demais", "🎯 Ranking e zebras", "📈 Linha do tempo"])

# ------------------------------------------------------------------ Top N
with aba_top:
    c1, c2 = st.columns([1, 2])
    N = c1.select_slider("Comparar o Top…", options=an.TOPS, value=10, format_func=lambda n: f"Top {n}")
    sup = c2.radio("Superfície", ["Todas", "Dura", "Saibro", "Grama"], horizontal=True)
    r = comparar(N, sup)
    t, d = r["top"], r["demais"]
    g.como_ler(f"Cada partida tem dois jogadores. Aqui olhamos **cada jogador em cada partida** (por isso há "
               f"mais linhas do que partidas) e o classificamos como **Top {N}** se ele estava entre os {N} primeiros "
               f"do ranking no início daquele torneio. Um mesmo jogador pode estar no Top {N} num ano e fora em "
               f"outro. As porcentagens são **somas de pontos**: por exemplo, \"pontos ganhos no saque\" = todos "
               f"os pontos que o grupo venceu sacando ÷ todos os pontos que sacou.")
    m = st.columns(4)
    m[0].metric(f"Top {N} vence quem está fora do Top {N}", pct(r["duelo"]["vitorias_top"]),
                help=f"{br(r['duelo']['n'], 0)} partidas Top × não-Top")
    m[1].metric(f"Vitórias do Top {N} (geral)", pct(t["vitorias"]))
    m[2].metric("Vitórias dos demais", pct(d["vitorias"]))
    m[3].metric(f"Jogador-partidas do Top {N}", br(t["n"], 0), help=f"{t['n_jogadores']} jogadores diferentes")

    # onde eles se diferenciam: diferença em pontos percentuais
    pcts = [(k, nome) for k, nome, u, _ in an.METRICAS if u == "%" and k not in ("vitorias", "canhoto")]
    difs = [(nome, 100 * (t[k] - d[k])) for k, nome in pcts]
    difs.sort(key=lambda x: x[1])
    fig = go.Figure(go.Bar(
        x=[v for _, v in difs], y=[n for n, _ in difs], orientation="h",
        marker_color=[g.COR_TOP if v >= 0 else g.COR_DEMAIS for _, v in difs],
        text=[f"{'+' if v >= 0 else ''}{br(v, 1)} p.p." for _, v in difs], textposition="outside",
        hovertemplate="%{y}: %{x:+.1f} p.p.<extra></extra>"))
    fig.update_xaxes(title=f"Top {N} − demais (pontos percentuais)", zeroline=True,
                     zerolinecolor="rgba(137,135,129,.6)")
    st.plotly_chart(g._layout(fig, f"Onde o Top {N} se diferencia ({sup.lower() if sup != 'Todas' else 'todas as superfícies'})", 420),
                    width="stretch")
    maior = difs[-1]
    st.info(f"**Leitura:** a maior vantagem do Top {N} está em **{maior[0].lower()}** "
            f"(+{br(maior[1], 1)} p.p.). Diferenças de 3 a 5 pontos percentuais por ponto parecem pequenas, mas "
            "num jogo com mais de 150 pontos viram vários games e, no fim, a vitória. O tênis é decidido nas margens.")

    linhas = []
    for k, nome, u, desc in an.METRICAS:
        fmt = (lambda v: pct(v)) if u == "%" else (lambda v: br(v, 2 if u == "n" else 1))
        dif = (t[k] - d[k]) * (100 if u == "%" else 1)
        linhas.append({"Métrica": nome, f"Top {N}": fmt(t[k]), "Demais": fmt(d[k]),
                       "Diferença": f"{'+' if dif >= 0 else ''}{br(dif, 2 if u == 'n' else 1)}{' p.p.' if u == '%' else ''}",
                       "O que mede": desc})
    c1, c2 = st.columns([3, 2])
    c1.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch", height=500)
    with c2:
        st.markdown(f"**Quem mais jogou como Top {N}** ({sup.lower() if sup != 'Todas' else 'todas as superfícies'})")
        jog = pd.DataFrame(r["jogadores"]).rename(columns={"jogador": "Jogador", "partidas": "Partidas",
                                                           "vitorias": "% vitórias"})
        jog["% vitórias"] = jog["% vitórias"].map(pct)
        st.dataframe(jog, hide_index=True, width="stretch", height=460)
    st.caption("**Sobre o corte:** Top 5 e Top 10 mostram a elite (Big 3 e poucos outros), com grupos menores. "
               "Top 50 e Top 100 comparam o \"jogador de circuito principal\" com quem vem dos qualificatórios e "
               "Challengers. O corte que mais conta uma história é o **Top 10**: elite × resto.")

# ------------------------------------------------------------------ ranking
with aba_rank:
    st.subheader("Quanto maior a diferença de ranking, maior a chance de o favorito vencer?")
    fx = pd.DataFrame(an.faixas_ranking(pop, am))
    fig = go.Figure()
    fig.add_scatter(x=fx["faixa"], y=fx["pop_taxa"], mode="lines+markers", name="População (todas)",
                    line=dict(color=g.COR_POP, width=3), marker=dict(size=9),
                    customdata=fx["pop_n"], hovertemplate="%{x}: %{y:.1%} (n = %{customdata:,})<extra>População</extra>")
    fig.add_scatter(x=fx["faixa"], y=fx["bo5"], mode="lines", name="População — melhor de 5",
                    line=dict(color=g.COR_POP, width=2, dash="dot"), hovertemplate="%{x}: %{y:.1%}<extra>Melhor de 5</extra>")
    fig.add_scatter(x=fx["faixa"], y=fx["bo3"], mode="lines", name="População — melhor de 3",
                    line=dict(color=g.COR_POP, width=2, dash="dash"), hovertemplate="%{x}: %{y:.1%}<extra>Melhor de 3</extra>")
    fig.add_scatter(x=fx["faixa"], y=fx["am_taxa"], mode="markers", name="Amostra (IC 95%)",
                    marker=dict(color=g.COR_AM, size=11, line=dict(color="white", width=1.5)),
                    error_y=dict(type="data", symmetric=False, array=fx["am_ic_sup"] - fx["am_taxa"],
                                 arrayminus=fx["am_taxa"] - fx["am_ic_inf"], color=g.COR_AM, thickness=2),
                    customdata=fx["am_n"], hovertemplate="%{x}: %{y:.1%} (n = %{customdata})<extra>Amostra</extra>")
    fig.add_hline(y=0.5, line_dash="dash", line_color=g.COR_NEUTRA, annotation_text="50% = moeda")
    fig.update_yaxes(tickformat=".0%", title="% de vitórias do favorito", range=[0.3, 1])
    fig.update_xaxes(title="Diferença de posições no ranking")
    st.plotly_chart(g._layout(fig, "Vitória do favorito por faixa de diferença de ranking", 460), width="stretch")
    g.como_ler("Cada ponto é a % de partidas vencidas pelo jogador mais bem ranqueado, para jogos com aquela "
               "diferença de posições. Quando os dois estão próximos no ranking (1–5 posições), o favorito vence "
               "pouco mais que uma moeda. Com mais de 200 posições de diferença, vence quase 4 em cada 5. Os pontos "
               "**amarelos** são a amostra, com barras de IC: são largas porque cada faixa tem poucas partidas.")
    st.info("**Conexão com IA:** um modelo de previsão de tênis precisa ser **calibrado**: quando ele diz \"70% de "
            "chance\", o favorito deve vencer cerca de 70% das vezes. Esta curva é o ponto de partida de um modelo "
            "simples, de uma variável só. Repare também que, para a mesma diferença, o favorito vence mais no "
            "**melhor de 5**: jogos longos reduzem a chance de zebra.")

# ------------------------------------------------------------------ tempo
with aba_tempo:
    lt = pd.DataFrame(an.linha_tempo(pop))
    var = st.selectbox("Indicador", list(an.LINHA_TEMPO), format_func=lambda k: an.LINHA_TEMPO[k][0])
    nome, unid = an.LINHA_TEMPO[var]
    fig = go.Figure(go.Scatter(x=lt["ano"], y=lt[var], mode="lines+markers", line=dict(color=g.COR_POP, width=3),
                               marker=dict(size=7), customdata=lt["n"],
                               hovertemplate="%{x}: %{y:" + (".1%" if unid == "%" else ".1f") +
                                             "} (%{customdata:,} partidas)<extra></extra>"))
    if var == "minutos_bo3_media":
        fig.add_scatter(x=lt["ano"], y=lt["minutos_bo3_mediana"], mode="lines", name="mediana",
                        line=dict(color=g.COR_POP, dash="dot"), hovertemplate="mediana %{y:.0f}<extra></extra>")
    if unid == "%":
        fig.update_yaxes(tickformat=".0%")
    fig.update_layout(showlegend=False)
    st.plotly_chart(g._layout(fig, f"{nome} por temporada", 420), width="stretch")
    a0, a1 = lt.iloc[0], lt.iloc[-1]
    st.caption(f"De {a0['ano']} a {a1['ano']}: {nome.lower()} foi de "
               f"{pct(a0[var]) if unid == '%' else br(a0[var], 1)} para {pct(a1[var]) if unid == '%' else br(a1[var], 1)}. "
               "Em 2020 houve bem menos partidas por causa da pandemia, então aquele ano oscila mais.")
    st.markdown("""
**Destaques:**
- As partidas **ficaram mais longas**: o melhor de 3 passou de cerca de 91 para 109 minutos. Uma hipótese é o jogo
  mais físico, com trocas longas do fundo de quadra. A base não permite testar a causa.
- A **idade dos vencedores subiu** até cerca de 2015 (era do Big 3 e dos veteranos) e depois começou a cair com a
  nova geração.
- A % de vitórias do favorito **subiu na era de domínio do Big 3** (cerca de 68% entre 2009 e 2016) e **voltou a
  cerca de 64%** depois. O circuito ficou mais imprevisível.
""")
