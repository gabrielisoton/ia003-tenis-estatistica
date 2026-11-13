"""Extra · Jogadores — líderes de todos os critérios, ranking por critério e perfil individual (população inteira)."""
import importlib

import numpy as np
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

st.set_page_config(page_title="Extra · Jogadores", page_icon="🎾", layout="wide")
st.info("**Extra · fora da avaliação da disciplina.** Página para quem gosta de tênis: usa a população "
        "inteira e não faz parte do trabalho avaliado (Painéis 1–3).", icon="🎾")
st.title("Jogadores · Quem é o melhor em cada aspecto do jogo?")
st.caption("Todas as partidas do circuito principal da ATP de 2000 a 2025 (66.819 partidas). Os números cobrem só "
           "esse recorte, **sem Challengers, qualificatórios, Copa Davis nem Olimpíadas**, então diferem das "
           "estatísticas oficiais de carreira.")

pop = dados.populacao()
A0, A1 = int(pop["ano"].min()), int(pop["ano"].max())
CONF = 0.95


@st.cache_data
def longo() -> pd.DataFrame:
    return an.longo(pop)


@st.cache_data
def tabela(anos, superficies, niveis, minimo) -> tuple[pd.DataFrame, pd.Series]:
    lg = longo()
    tab = an.tabela_jogadores(lg, anos, list(superficies), list(niveis), minimo, CONF)
    medias = an.medias_circuito(an.recortar(lg, anos, list(superficies), list(niveis)), tab)
    return tab, medias


@st.cache_data
def perfil(nome, anos, superficies) -> dict:
    return an.perfil_jogador(longo(), pop, nome, anos, list(superficies) or None, confianca=CONF)


@st.cache_data
def jogadores() -> pd.Series:
    return longo()["jogador"].value_counts()


@st.cache_data
def max_partidas(anos, superficies, niveis) -> int:
    r = an.recortar(longo(), anos, list(superficies), list(niveis))
    return int(r["jogador"].value_counts().max()) if len(r) else 0


def minimo_sugerido(anos) -> int:
    """10 partidas por temporada do recorte, entre 20 e 100: uma temporada só → 20; 10 anos ou mais → 100.
    Com 100 fixo, um ano isolado ficava vazio (quem mais joga faz ~90 partidas por temporada)."""
    return int(min(100, max(20, 10 * (anos[1] - anos[0] + 1))))


def ajustar_minimo(chave_anos: str, chave_min: str) -> None:
    st.session_state[chave_min] = minimo_sugerido(st.session_state[chave_anos])


def aviso_vazio(anos, sups, nivs, minimo) -> None:
    if not sups or not nivs:
        st.warning("Escolha pelo menos uma superfície e um nível de torneio.")
        return
    mx = max_partidas(anos, tuple(sups), tuple(nivs))
    st.warning(f"Ninguém tem {minimo} partidas nesse recorte: quem mais jogou fez {mx}. Reduza o mínimo de "
               "partidas ou amplie o recorte." if mx else "Não há partidas nesse recorte.")


AJUDA_MIN = ("Ajusta sozinho quando você muda os anos (10 por temporada, entre 20 e 100), mas pode ser editado. "
             "Com poucas partidas o IC fica largo e o 1º lugar pode ser sorte.")
for _k in ("ld_min", "rk_min"):
    st.session_state.setdefault(_k, 100)


def fmt(c: an.Criterio, v) -> str:
    if v is None or pd.isna(v):
        return "—"
    if c.tipo == "%":
        return pct(v)
    if c.tipo == "taxa":
        return br(v, 3)
    if c.tipo == "razao":
        return br(v, 2)
    return br(v, 0)


def fmt_ic(c: an.Criterio, li, ls) -> str:
    return "—" if c.tipo != "%" or pd.isna(li) else f"{pct(li)} a {pct(ls)}"


def fmt_pctl(p) -> str:
    """Percentil com 1 casa só perto dos extremos (para 99,7% não virar "100%")."""
    return br(p, 1 if (99 < p < 100 or 0 < p < 1) else 0) + "%"


def eixo(fig: go.Figure, c: an.Criterio, eixo_x: bool = True) -> None:
    upd = fig.update_xaxes if eixo_x else fig.update_yaxes
    upd(tickformat=".0%" if c.tipo == "%" else None, separatethousands=True)


ROTULO_CRIT = {c.chave: f"{c.grupo} · {c.nome}" for c in an.CRITERIOS}
CORES_MED = {"ouro": "#c98500", "prata": "#a8a6a0", "bronze": "#8c5a3c"}
ICONE_MED = {"ouro": "🥇", "prata": "🥈", "bronze": "🥉"}
TOP_MED = 10


@st.cache_data
def lideres(anos, superficies, niveis, minimo):
    tab, _ = tabela(anos, superficies, niveis, minimo)
    return an.lideres(tab, TOP_MED) if len(tab) else (pd.DataFrame(), pd.DataFrame())


aba_lid, aba_rank, aba_perfil = st.tabs(["🏆 Líderes de cada critério", "🏅 Ranking por critério",
                                         "🎾 Perfil do jogador"])

# =================================================================== líderes
with aba_lid:
    c1, c2 = st.columns([3, 1])
    anos_l = c1.slider("Anos", A0, A1, (A0, A1), key="ld_anos", on_change=ajustar_minimo,
                       args=("ld_anos", "ld_min"), help="Escolha o mesmo ano nas duas pontas para ver uma temporada só.")
    min_l = c2.number_input("Mínimo de partidas", 1, 1000, step=10, key="ld_min",
                            help="Só disputa a liderança quem jogou pelo menos isso no recorte. " + AJUDA_MIN)
    c3, c4 = st.columns(2)
    sups_l = c3.multiselect("Superfície", an.SUPERFICIES, default=an.SUPERFICIES, key="ld_sup")
    nivs_l = c4.multiselect("Nível do torneio", an.NIVEIS, default=an.NIVEIS, key="ld_niv")
    pod, med = lideres(anos_l, tuple(sups_l), tuple(nivs_l), int(min_l))
    if not sups_l or not nivs_l or pod.empty:
        aviso_vazio(anos_l, sups_l, nivs_l, int(min_l))
    else:
        dono = med.index[0]
        isoladas = pod.get("lideranca", pd.Series(dtype=object))
        m = st.columns([1.8, 1, 1, 1])
        d = med.iloc[0]
        m[0].metric("Mais dominante", dono, help="Quem soma mais pontos no quadro de medalhas "
                                                 "(1º lugar = 3, 2º = 2, 3º = 1).")
        m[1].metric("Pontos", br(d["pontos"], 0),
                    help=f"{int(d['ouro'])} 🥇 · {int(d['prata'])} 🥈 · {int(d['bronze'])} 🥉 em {len(pod)} critérios")
        m[2].metric(f"Vezes no top {TOP_MED}", br(med.iloc[0][f"top{TOP_MED}"], 0), help=f"em {len(pod)} critérios")
        m[3].metric("Lideranças isoladas", f"{int((isoladas == 'isolada').sum())} de {int(isoladas.notna().sum())}",
                    help="Proporções em que o IC 95% do 1º não toca o do 2º: a vantagem não é só sorte.")

        # ---------------- pódio de todos os critérios
        st.subheader("Pódio de cada critério")
        def celula(r, medalha):
            if pd.isna(r.get(medalha)):
                return "—"
            return f"{r[medalha]} ({fmt(an.CRIT[r['chave']], r[f'{medalha}_valor'])})"
        def vantagem(r):
            c = an.CRIT[r["chave"]]
            v = r.get("vantagem")
            if pd.isna(v):
                return "—"
            if c.tipo == "%":
                return f"+{br(100 * v, 1)} p.p."
            return "+" + (br(v, 3) if c.tipo == "taxa" else br(v, 2) if c.tipo == "razao" else br(v, 0))
        tp = pd.DataFrame({
            "Grupo": pod["grupo"], "Critério": pod["criterio"],
            "🥇 1º": [celula(r, "ouro") for _, r in pod.iterrows()],
            "🥈 2º": [celula(r, "prata") for _, r in pod.iterrows()],
            "🥉 3º": [celula(r, "bronze") for _, r in pod.iterrows()],
            "Vantagem do 1º": [vantagem(r) for _, r in pod.iterrows()],
            "Liderança": pod["lideranca"].fillna("—") if "lideranca" in pod else "—",
        })
        st.dataframe(tp, hide_index=True, width="stretch", height=38 + 35 * len(tp))
        g.como_ler(
            "Cada linha é um critério, com os **três melhores** jogadores do recorte (entre os que têm o mínimo de "
            "partidas) e o valor de cada um. Em duplas faltas por game, o melhor é quem comete **menos**.\n\n"
            "**Vantagem do 1º** é a distância para o 2º colocado (em pontos percentuais nas proporções).\n\n"
            "**Liderança isolada × empate técnico:** nas proporções, comparamos os **IC 95% de Wilson** do 1º e do "
            "2º. Se os intervalos **não se tocam**, a liderança é *isolada*: dificilmente é fruto do acaso das "
            "partidas que cada um jogou. Se eles se sobrepõem, é um *empate técnico*: com esses dados não dá para "
            "afirmar quem é melhor. É um critério conservador (intervalos que se tocam um pouco ainda podem indicar "
            "diferença num teste formal), mas mostra a ideia de variabilidade amostral do Painel 3.")

        # ---------------- quadro de medalhas
        st.subheader("Quadro de medalhas · quem domina mais critérios")
        topm = med.head(15).iloc[::-1]
        fig = go.Figure()
        for medalha in an.MEDALHAS:
            fig.add_bar(y=topm.index, x=topm[medalha], orientation="h", name=f"{ICONE_MED[medalha]} {medalha}",
                        marker_color=CORES_MED[medalha],
                        text=[int(v) if v else "" for v in topm[medalha]], textposition="inside",
                        hovertemplate="<b>%{y}</b><br>%{x} " + medalha + "<extra></extra>")
        fig.update_layout(barmode="stack", legend_traceorder="normal")
        fig.update_xaxes(title="critérios (1º, 2º e 3º lugares)", dtick=1, showgrid=True,
                         gridcolor="rgba(137,135,129,0.25)")
        fig.update_yaxes(showgrid=False)
        st.plotly_chart(g._layout(fig, "Medalhas por jogador (15 com mais pontos)", 560),
                        width="stretch")
        tm = pd.DataFrame({
            "Jogador": med.index, "Pontos": med["pontos"], "🥇": med["ouro"], "🥈": med["prata"], "🥉": med["bronze"],
            f"Top {TOP_MED}": med[f"top{TOP_MED}"], "Partidas": med["partidas"],
            "Lidera em": ["; ".join(x) for x in med["criterios"]],
        })
        st.dataframe(tm, hide_index=True, width="stretch", height=420,
                     column_config={"Lidera em": st.column_config.TextColumn(width="large")})
        st.caption(f"**Pontos:** 1º lugar vale 3, 2º vale 2 e 3º vale 1; empates se desfazem por mais 1º lugares. "
                   "Assim, quem é forte em muitos critérios passa à frente de um especialista imbatível em poucos "
                   "(na base inteira, Karlović lidera 4 critérios, todos de saque). A coluna **Top "
                   f"{TOP_MED}** conta em quantos dos {len(pod)} critérios o jogador fica entre os {TOP_MED} melhores: "
                   "é a medida de quem é bom em **tudo**, não só excepcional em poucos aspectos. Nas contagens "
                   "(títulos, finais), quem tem zero não recebe medalha.")

# =================================================================== ranking
with aba_rank:
    c1, c2, c3 = st.columns([2, 2, 1])
    chave = c1.selectbox("Critério", [c.chave for c in an.CRITERIOS], format_func=ROTULO_CRIT.get, key="rk_crit")
    anos = c2.slider("Anos", A0, A1, (A0, A1), key="rk_anos", on_change=ajustar_minimo,
                     args=("rk_anos", "rk_min"), help="Escolha o mesmo ano nas duas pontas para ver uma temporada só.")
    minimo = c3.number_input("Mínimo de partidas", 1, 1000, step=10, key="rk_min",
                             help="Só entra no ranking quem jogou pelo menos isso no recorte. " + AJUDA_MIN)
    c4, c5 = st.columns(2)
    sups = c4.multiselect("Superfície", an.SUPERFICIES, default=an.SUPERFICIES, key="rk_sup")
    nivs = c5.multiselect("Nível do torneio", an.NIVEIS, default=an.NIVEIS, key="rk_niv")
    c = an.CRIT[chave]

    tab, medias = tabela(anos, tuple(sups), tuple(nivs), int(minimo))
    rk = an.ranking_criterio(tab, chave) if len(tab) else tab
    if not sups or not nivs or rk.empty:
        aviso_vazio(anos, sups, nivs, int(minimo))
    else:
        media = medias[chave]
        m = st.columns([1, 1.8, 1, 1])
        m[0].metric("Jogadores no ranking", br(len(rk), 0), help=f"com pelo menos {int(minimo)} partidas no recorte")
        m[1].metric("1º lugar", rk.index[0])
        m[2].metric(f"{c.nome} do 1º", fmt(c, rk.iloc[0][chave]))
        m[3].metric("Média do circuito", br(media, 1) if c.tipo == "n" else fmt(c, media),
                    help="Contagens: média por jogador do ranking. Demais critérios: razão das somas de todos "
                         "os jogadores do recorte (por isso vitórias = 50% e dominance ratio = 1).")

        top = rk.head(20).iloc[::-1]
        fig = go.Figure()
        hover = [f"<b>{j}</b><br>{c.nome}: {fmt(c, v)}" + (f"<br>IC 95%: {fmt_ic(c, li, ls)}" if c.tipo == "%" else "")
                 + f"<br>{br(n, 0)} partidas" for j, v, li, ls, n in
                 zip(top.index, top[chave], top.get(f"{chave}_ic_inf", top[chave]),
                     top.get(f"{chave}_ic_sup", top[chave]), top["partidas"])]
        if c.tipo == "n":
            fig.add_bar(x=top[chave], y=top.index, orientation="h", marker_color=g.COR_POP,
                        text=[fmt(c, v) for v in top[chave]], textposition="outside",
                        hovertext=hover, hoverinfo="text")
        else:
            erro = None
            if c.tipo == "%":
                erro = dict(type="data", symmetric=False, array=top[f"{chave}_ic_sup"] - top[chave],
                            arrayminus=top[chave] - top[f"{chave}_ic_inf"], color=g.COR_POP, thickness=2, width=4)
            fig.add_scatter(x=top[chave], y=top.index, mode="markers", error_x=erro, showlegend=False,
                            marker=dict(color=g.COR_POP, size=12, line=dict(color="white", width=1.5)),
                            hovertext=hover, hoverinfo="text")
        fig.add_vline(x=media, line_dash="dash", line_color=g.COR_NEUTRA, line_width=2,
                      annotation_text=f"média do circuito: {fmt(c, media)}", annotation_position="top")
        eixo(fig, c)
        fig.update_yaxes(showgrid=False)
        fig.update_xaxes(showgrid=True, gridcolor="rgba(137,135,129,0.25)", title=c.nome)
        sub = ("ponto = valor do jogador · traço = IC 95% de Wilson" if c.tipo == "%"
               else "menor é melhor" if not c.maior_melhor else "")
        st.plotly_chart(g._layout(fig, f"Top 20 · {c.nome}" + (f"<br><sup>{sub}</sup>" if sub else ""), 640),
                        width="stretch")
        g.como_ler(
            f"Cada linha é um jogador com pelo menos **{int(minimo)} partidas** no recorte. Os valores são "
            "**razões de somas**: em \"pontos ganhos no saque\", por exemplo, somamos todos os pontos que ele venceu "
            "sacando e dividimos por todos os pontos que sacou.\n\n"
            "**Por que o mínimo de partidas importa?** O valor de cada jogador é uma estimativa feita com as "
            "partidas que ele jogou, e o **traço** é o **intervalo de confiança de 95% de Wilson**. Com poucas "
            "partidas o intervalo fica largo e o \"1º lugar\" pode ser só sorte: baixe o mínimo para 10 e veja "
            "aparecerem líderes desconhecidos, com intervalos enormes. É a mesma ideia de variabilidade amostral "
            "do Painel 3. Usamos o IC de **Wilson** em vez do de Wald (p̂ ± z·EP) porque ele continua válido "
            "perto de 0% ou 100% e com n pequeno, e nunca sai do intervalo [0, 1].\n\n"
            "Quando dois intervalos se sobrepõem bastante, os dados não permitem dizer com segurança quem é "
            "melhor. Taxas por game, o dominance ratio e as contagens não têm IC de proporção.")
        if c.desc:
            st.caption(f"**{c.nome}:** {c.desc}.")

        t = pd.DataFrame({
            "Posição": rk["posicao"].map(lambda p: f"{p}º"),
            "Jogador": rk.index,
            "Partidas": rk["partidas"],
            "V–D": [f"{v}–{d}" for v, d in zip(rk["V"], rk["D"])],
            c.nome: [fmt(c, v) for v in rk[chave]],
        })
        if c.tipo == "%":
            t["IC 95% (Wilson)"] = [fmt_ic(c, li, ls) for li, ls in zip(rk[f"{chave}_ic_inf"], rk[f"{chave}_ic_sup"])]
            t["Base (n)"] = rk[f"{chave}_n"].astype(int)
        t["Percentil"] = rk["percentil"].round(0)
        t["Melhor ranking"] = rk["melhor_rank"]
        st.dataframe(t, hide_index=True, width="stretch", height=420, column_config={
            "Percentil": st.column_config.ProgressColumn("Percentil", min_value=0, max_value=100, format="%.0f",
                                                         help="% dos jogadores do ranking que ele supera"),
            "Melhor ranking": st.column_config.NumberColumn(format="%d"),
            "Base (n)": st.column_config.NumberColumn(help="Denominador da proporção: partidas, pontos, break "
                                                           "points ou tie-breaks, conforme o critério."),
        })

# =================================================================== perfil
with aba_perfil:
    cont = jogadores()
    nomes = list(cont.index)
    c1, c2, c3 = st.columns([2, 2, 2])
    nome = c1.selectbox("Jogador", nomes, index=nomes.index("Roger Federer"), key="pf_nome",
                        format_func=lambda j: f"{j} ({br(cont[j], 0)} partidas)",
                        help="Ordenados por número de partidas na base. Digite para buscar.")
    anos_p = c2.slider("Anos", A0, A1, (A0, A1), key="pf_anos")
    sups_p = c3.multiselect("Superfície", an.SUPERFICIES, default=an.SUPERFICIES, key="pf_sup")
    p = perfil(nome, anos_p, tuple(sups_p))

    if not sups_p or p["vazio"]:
        st.warning(f"{nome} não tem partidas nesse recorte.")
        st.stop()

    L, F = p["linha"], p["ficha"].set_index("chave")
    m = st.columns(6)
    m[0].metric("Partidas", br(L["partidas"], 0), help=f"{p['anos'][0]}–{p['anos'][1]} no recorte")
    m[1].metric("V–D", f"{int(L['V'])}–{int(L['D'])}")
    m[2].metric("Vitórias", pct(L["vitorias"]))
    m[3].metric("Títulos", br(L["titulos"], 0), help=f"{int(L['titulos_gs'])} de Grand Slam")
    m[4].metric("Finais", br(L["finais"], 0))
    m[5].metric("Melhor ranking", f"{p['melhor_rank']}º" if p["melhor_rank"] else "—",
                help=f"atingido em {p['melhor_rank_ano']} (ranking no início de cada torneio)"
                if p["melhor_rank"] else None)
    recorte = (f"{anos_p[0]}–{anos_p[1]}" if anos_p != (A0, A1) else "toda a base") + \
              ("" if set(sups_p) == set(an.SUPERFICIES) else " · " + ", ".join(s.lower() for s in sups_p))
    st.caption(f"Recorte: **{recorte}**. Percentil e posição comparam {nome} aos **{p['n_ref']} jogadores** com "
               "pelo menos 100 partidas na base que têm 20 ou mais partidas nesse recorte.")

    # ---------------------------------------------------- pontos fortes/fracos
    jogo = p["ficha"][(p["ficha"]["tipo"] != "n") & p["ficha"]["percentil"].notna()].sort_values("percentil")
    st.subheader("Pontos fortes e fracos")
    if len(jogo) >= 6:
        fortes, fracos = jogo.tail(3).iloc[::-1], jogo.head(3)
        cf, cw = st.columns(2)
        with cf:
            st.markdown("**💪 Pontos fortes**")
            for _, r in fortes.iterrows():
                c = an.CRIT[r["chave"]]
                st.markdown(f"- **{c.nome}**: {fmt(c, r['valor'])} · melhor que {fmt_pctl(r['percentil'])} dos "
                            f"demais ({r['posicao']}º de {r['total']})")
        with cw:
            st.markdown("**🔧 Pontos fracos (relativos)**")
            for _, r in fracos.iterrows():
                c = an.CRIT[r["chave"]]
                st.markdown(f"- **{c.nome}**: {fmt(c, r['valor'])} · melhor que {fmt_pctl(r['percentil'])} dos "
                            f"demais ({r['posicao']}º de {r['total']})")
    fig = go.Figure(go.Bar(
        x=jogo["percentil"], y=jogo["criterio"], orientation="h",
        marker_color=[g.COR_TOP if v >= 50 else g.COR_DEMAIS for v in jogo["percentil"]],
        text=[br(v, 0) for v in jogo["percentil"]], textposition="outside",
        customdata=np.c_[[fmt(an.CRIT[k], v) for k, v in zip(jogo["chave"], jogo["valor"])],
                         [f"{a}º de {b}" for a, b in zip(jogo["posicao"], jogo["total"])]],
        hovertemplate="<b>%{y}</b><br>valor: %{customdata[0]}<br>percentil %{x:.1f} · %{customdata[1]}<extra></extra>"))
    fig.add_vline(x=50, line_dash="dash", line_color=g.COR_NEUTRA, line_width=2,
                  annotation_text="50 = jogador típico", annotation_position="top")
    fig.update_xaxes(range=[0, 108], title="Percentil (% dos jogadores de referência que ele supera)")
    fig.update_yaxes(showgrid=False)
    st.plotly_chart(g._layout(fig, f"{nome} · percentil em cada aspecto do jogo", 520), width="stretch")
    g.como_ler("O **percentil** diz que fração dos outros jogadores de referência ele supera naquele critério: 90 significa "
               "melhor que 90% deles; 50 é o jogador típico. Barras **magenta** ficam acima da mediana; **cinza**, "
               "abaixo. Em duplas faltas por game, menor é melhor, então o percentil já vem invertido. \"Pontos "
               "fracos\" são relativos: até um campeão tem aspectos em que é apenas mediano.")

    # ---------------------------------------------------------- ficha completa
    st.subheader("Ficha completa · critério a critério")
    fic = p["ficha"]
    tf = pd.DataFrame({
        "Grupo": fic["grupo"],
        "Critério": fic["criterio"],
        "Valor": [fmt(an.CRIT[k], v) for k, v in zip(fic["chave"], fic["valor"])],
        "IC 95% (Wilson)": [fmt_ic(an.CRIT[k], li, ls) for k, li, ls in zip(fic["chave"], fic["ic_inf"], fic["ic_sup"])],
        "Média do circuito": [br(v, 1) if an.CRIT[k].tipo == "n" else fmt(an.CRIT[k], v)
                              for k, v in zip(fic["chave"], fic["media"])],
        "Percentil": fic["percentil"].round(0),
        "Posição": [f"{a}º de {b}" if a else "—" for a, b in zip(fic["posicao"], fic["total"])],
    })
    st.dataframe(tf, hide_index=True, width="stretch", height=640, column_config={
        "Percentil": st.column_config.ProgressColumn("Percentil", min_value=0, max_value=100, format="%.0f"),
    })
    st.caption("Média do circuito: razão das somas de todos os jogadores no recorte (vitórias = 50% e dominance ratio "
               "= 1 por construção); nas contagens, média por jogador de referência. O IC só existe para proporções.")

    # ----------------------------------------------------------- superfícies
    st.subheader("Cada aspecto por superfície")
    ps = p["por_superficie"]
    ps = ps[ps["partidas"] > 0]
    cg, ct = st.columns([2, 3])
    with cg:
        fig = go.Figure(go.Bar(
            x=ps.index, y=ps["vitorias"], marker_color=[g.CORES_SUP.get(s, g.COR_NEUTRA) for s in ps.index],
            error_y=dict(type="data", symmetric=False, array=ps["vitorias_ic_sup"] - ps["vitorias"],
                         arrayminus=ps["vitorias"] - ps["vitorias_ic_inf"], color=g.COR_NEUTRA, thickness=1.5),
            text=[pct(v) for v in ps["vitorias"]], textposition="inside", insidetextanchor="end",
            customdata=np.c_[ps["V"], ps["D"]],
            hovertemplate="<b>%{x}</b><br>%{y:.1%} de vitórias<br>%{customdata[0]}–%{customdata[1]}<extra></extra>"))
        fig.add_hline(y=0.5, line_dash="dash", line_color=g.COR_NEUTRA)
        fig.update_yaxes(tickformat=".0%", range=[0, 1.05], title="% de vitórias")
        st.plotly_chart(g._layout(fig, "Vitórias por superfície<br><sup>traço = IC 95% de Wilson</sup>", 400),
                        width="stretch")
    with ct:
        linhas = {"Partidas": [br(v, 0) for v in ps["partidas"]],
                  "V–D": [f"{v}–{d}" for v, d in zip(ps["V"], ps["D"])]}
        for c in an.CRITERIOS:
            linhas[c.nome] = [fmt(c, v) for v in ps[c.chave]]
        tsup = pd.DataFrame(linhas, index=ps.index).T
        tsup.index.name = "Critério"
        st.dataframe(tsup, width="stretch", height=640)

    # ---------------------------------------------------------- temporadas
    st.subheader("Evolução por temporada")
    an_ = p["anual"]
    opcoes = [c.chave for c in an.CRITERIOS]
    ch = st.selectbox("Critério", opcoes, format_func=ROTULO_CRIT.get, key="pf_crit")
    c = an.CRIT[ch]
    fig = go.Figure()
    erro = None
    if c.tipo == "%":
        erro = dict(type="data", symmetric=False, array=an_[f"{ch}_ic_sup"] - an_[ch],
                    arrayminus=an_[ch] - an_[f"{ch}_ic_inf"], color=g.COR_POP, thickness=1.2, width=3)
    fig.add_scatter(x=an_.index, y=an_[ch], mode="lines+markers", line=dict(color=g.COR_POP, width=3),
                    marker=dict(size=8), error_y=erro, customdata=an_["partidas"],
                    hovertext=[fmt(c, v) for v in an_[ch]],
                    hovertemplate="%{x}: %{hovertext} (%{customdata} partidas)<extra></extra>")
    if c.tipo != "n":
        fig.add_hline(y=F.loc[ch, "media"], line_dash="dash", line_color=g.COR_NEUTRA,
                      annotation_text=f"média do circuito: {fmt(c, F.loc[ch, 'media'])}",
                      annotation_position="bottom right")
    eixo(fig, c, eixo_x=False)
    fig.update_xaxes(dtick=1 if len(an_) <= 15 else 2)
    fig.update_layout(showlegend=False)
    st.plotly_chart(g._layout(fig, f"{nome} · {c.nome} por temporada"
                              + ("<br><sup>traço = IC 95% de Wilson; anos com poucas partidas têm IC largo</sup>"
                                 if c.tipo == "%" else ""), 400), width="stretch")
    c1, c2 = st.columns(2)
    with c1:
        fig = go.Figure(go.Bar(x=an_.index, y=an_["partidas"], marker_color=g.COR_POP,
                               customdata=np.c_[an_["V"], an_["D"]],
                               hovertemplate="%{x}: %{y} partidas (%{customdata[0]}–%{customdata[1]})<extra></extra>"))
        fig.update_yaxes(title="partidas")
        st.plotly_chart(g._layout(fig, "Partidas por temporada", 320), width="stretch")
    with c2:
        fig = go.Figure(go.Scatter(x=an_.index, y=an_["melhor_rank"], mode="lines+markers",
                                   line=dict(color=g.COR_TOP, width=3), marker=dict(size=7),
                                   hovertemplate="%{x}: %{y}º<extra>melhor ranking do ano</extra>"))
        fig.update_yaxes(autorange="reversed", title="posição (1 = topo)")
        st.plotly_chart(g._layout(fig, "Melhor ranking do ano", 320), width="stretch")
    st.caption("O ranking é o do início de cada torneio, por isso o \"melhor ranking do ano\" é o melhor que ele tinha "
               "ao entrar em quadra naquela temporada.")

    # --------------------------------------------------------------- títulos
    st.subheader("Títulos e finais")
    if p["por_nivel"].empty:
        st.markdown(f"{nome} não disputou finais nesse recorte.")
    else:
        c1, c2 = st.columns([1, 3])
        c1.dataframe(p["por_nivel"], width="stretch")
        tt = p["titulos"].rename(columns={"ano": "Ano", "torneio": "Torneio", "nivel": "Nível",
                                          "superficie": "Superfície", "perdedor": "Vice", "placar": "Placar"})
        if tt.empty:
            c2.markdown("Nenhum título no recorte.")
        else:
            c2.dataframe(tt, hide_index=True, width="stretch", height=380,
                         column_config={"Ano": st.column_config.NumberColumn(format="%d")})
