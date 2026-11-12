"""Painel 3 — Inferência estatística (só com a amostra) e comparação com a população."""
import numpy as np
import pandas as pd
import streamlit as st

import dados
import estatistica as est
import graficos as g
import hipoteses as hp
from dados import br, pct

st.set_page_config(page_title="3 · Inferência", page_icon="🎾", layout="wide")
st.title("Painel 3 · Inferência estatística e comparação com a população")
st.caption("Intervalos de confiança e testes usam **somente a amostra** (AAS, n = 382). "
           "O parâmetro populacional é calculado diretamente e aparece só para comparação.")

pop, am = dados.populacao(), dados.amostra()
ALFA = st.sidebar.select_slider("Nível de significância (α)", [0.01, 0.05, 0.10], value=0.05,
                                format_func=lambda a: f"{a:.0%}")
CONF = 0.95
st.sidebar.caption(f"Os intervalos de confiança são de {CONF:.0%}. O padrão do trabalho é α = 5%.")

with st.container(border=True):
    st.markdown("""
#### 🎯 O que estamos fazendo aqui? (a ideia em 4 passos)
1. **Fingimos que não conhecemos a população.** Na vida real quase nunca temos todos os dados, só uma amostra.
2. **Com as 382 partidas sorteadas, estimamos um número da população**, como a % de vitórias do favorito.
   Damos um **palpite** (a estimativa pontual) e uma **margem** em volta dele (o intervalo de confiança, IC).
3. **Testamos uma afirmação** (a hipótese H₀, por exemplo "o favorito vence só 50%"). O **valor-p** responde:
   *se H₀ fosse verdade, qual a chance de uma amostra mostrar algo tão extremo quanto o que vimos?*
   Se essa chance for menor que α (5%), consideramos H₀ improvável e a **rejeitamos**.
4. **Conferimos com a população.** Como temos todas as 66.819 partidas, dá para ver se o IC "acertou" o valor
   real e se a decisão do teste foi correta. Isso é impossível na prática, mas ótimo para aprender.
""")

SINAL = est.ALTERNATIVAS
FMT = {"P1": pct, "P2": pct, "M1": lambda v: f"{br(v, 1)} min", "M2": lambda v: br(v, 2)}


def cartao(h: dict) -> dict:
    r = hp.rodar(h, am, ALFA, CONF)
    param, sigma, N_sub = hp.parametro(h, pop)
    f = FMT[h["id"]]
    sinal = SINAL[h["alt"]]
    simbolo = "p" if h["tipo"] == "proporção" else "μ"

    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader(h["pergunta"])
        st.markdown(f"**Por que importa:** {h['justificativa']}")
        st.markdown(f"**Parâmetro:** {h['parametro_nome']}.")
        st.markdown(f"- **H₀:** {simbolo} = {f(h['h0'])}\n- **H₁:** {simbolo} {sinal} {f(h['h0'])}\n"
                    f"- **Nível de significância:** α = {pct(ALFA, 0)} · "
                    f"teste {'z para uma proporção' if h['tipo'] == 'proporção' else 't para uma média'}"
                    f" ({'unilateral à direita' if h['alt'] == 'maior' else 'bilateral'})")
    with c2:
        m = st.columns(2)
        m[0].metric("n (amostra)", r.n, help=h["unidade"])
        m[1].metric("Estimativa pontual", f(r.estimativa))
        m[0].metric(f"Estatística {'z' if h['tipo'] == 'proporção' else 't'}", br(r.estatistica, 3),
                    help=None if r.gl is None else f"{r.gl} graus de liberdade")
        m[1].metric("Valor-p", "< 0,0001" if r.valor_p < 1e-4 else br(r.valor_p, 4))
        st.metric("IC 95%", f"[{f(r.ic_inf)} ; {f(r.ic_sup)}]")

    if h["tipo"] == "proporção":
        st.latex(r"z=\frac{\hat p-p_0}{\sqrt{p_0(1-p_0)/n}}=\frac{" + br(r.estimativa, 4) + "-" + br(h["h0"], 4)
                 + r"}{\sqrt{" + br(h["h0"], 4) + r"(1-" + br(h["h0"], 4) + ")/" + str(r.n) + "}}="
                 + br(r.estatistica, 3) + r"\qquad IC=\hat p\pm z_{0{,}975}\sqrt{\hat p(1-\hat p)/n}")
    else:
        st.latex(r"t=\frac{\bar x-\mu_0}{s/\sqrt n}=\frac{" + br(r.estimativa, 2) + "-" + br(h["h0"], 0)
                 + "}{" + br(r.erro_padrao_ic, 3) + "}=" + br(r.estatistica, 3)
                 + r"\qquad IC=\bar x\pm t_{0{,}975;\," + str(r.gl) + r"}\cdot s/\sqrt n")
    g.como_ler(
        f"- **Estatística {'z' if h['tipo'] == 'proporção' else 't'}:** quantos *erros-padrão* a estimativa da "
        f"amostra está longe do valor de H₀. Perto de 0 = compatível com H₀; além de ±2 = bem improvável sob H₀.\n"
        f"- **Erro-padrão:** o tamanho típico do erro amostral. Ele diminui quando n aumenta (√n no denominador).\n"
        f"- **Valor-p:** a chance de ver uma amostra tão extrema quanto esta **se H₀ fosse verdadeira**. "
        f"Valor-p pequeno → a amostra é estranha demais para H₀ → rejeitamos H₀.\n"
        f"- **IC 95%:** a faixa de valores plausíveis para o parâmetro. O método acerta em 95% das amostras.")

    st.plotly_chart(g.grafico_ic(r.estimativa, r.ic_inf, r.ic_sup, h["h0"], param, f,
                                 "Estimativa e IC da amostra × H₀ × parâmetro real",
                                 proporcao=h["tipo"] == "proporção"), width="stretch")
    g.como_ler("A **barra amarela** é o IC calculado com a amostra e a **bolinha** é a estimativa pontual. A "
               "**linha tracejada cinza** é o valor afirmado por H₀ e a **linha violeta** é o valor verdadeiro "
               "da população. Se o tracejado ficar **fora** da barra, a amostra contradiz H₀. Se a linha "
               "violeta ficar **dentro** da barra, o IC acertou.")

    if r.rejeita_h0:
        st.success(f"**Conclusão (amostra):** valor-p {'< 0,0001' if r.valor_p < 1e-4 else '= ' + br(r.valor_p, 4)}"
                   f" < α = {pct(ALFA, 0)} → **rejeitamos H₀**. Há evidência estatística de que "
                   f"{simbolo} {sinal} {f(h['h0'])}.")
    else:
        st.info(f"**Conclusão (amostra):** valor-p = {br(r.valor_p, 4)} ≥ α = {pct(ALFA, 0)} → **não rejeitamos "
                f"H₀**. Os dados são compatíveis com {simbolo} = {f(h['h0'])}, o que **não prova** que H₀ seja "
                f"verdadeira: só não há evidência contra ela.")

    with st.expander("Condições de aplicação do teste", expanded=False):
        st.dataframe(pd.DataFrame([{"Condição": k,
                                    "Valor": br(v[0], 2) if isinstance(v[0], (int, float)) else str(v[0]),
                                    "Atendida?": "✅ sim" if v[1] else "⚠️ não"}
                                   for k, v in r.condicoes.items()]), hide_index=True, width="stretch")
        if h["tipo"] == "média":
            st.markdown("A variável é assimétrica à direita, mas com n grande o **Teorema Central do Limite** "
                        "garante que a média amostral tem distribuição aproximadamente normal. Por isso o teste "
                        "t é adequado.")
            st.plotly_chart(g.histograma(hp.subconjunto(h, am).dropna(subset=[h["var"]]), h["var"], "Amostra"),
                            width="stretch")
        else:
            st.markdown("Para usar a aproximação normal, a amostra precisa ter pelo menos 10 \"sucessos\" e 10 "
                        "\"fracassos\" esperados. Com n = 382, isso é folgado.")

    st.markdown("#### Comparação com a população")
    contem = r.ic_inf <= param <= r.ic_sup
    h0_falsa = hp.h0_falsa(h, param)
    poder = hp.poder(h, param, sigma, r.n, ALFA)
    if r.rejeita_h0 and h0_falsa and poder < 0.5:
        decisao = (f"✅ Decisão correta, mas **com sorte**: H₀ é falsa na população ({simbolo} = {f(param)}), "
                   f"porém a diferença para {f(h['h0'])} é tão pequena que o poder do teste era de só "
                   f"{pct(poder)}. A rejeição veio em boa parte do **erro amostral**: esta amostra se afastou de "
                   f"H₀ mais do que a população. Com outra semente, o mais provável seria não rejeitar.")
    elif r.rejeita_h0 and h0_falsa:
        decisao = "✅ Decisão correta: H₀ é falsa na população e o teste a rejeitou."
    elif r.rejeita_h0:
        decisao = "❌ Erro tipo I: o teste rejeitou uma H₀ que é verdadeira na população."
    elif h0_falsa:
        decisao = (f"⚠️ Erro tipo II: na população H₀ é falsa ({simbolo} = {f(param)} ≠ {f(h['h0'])}), mas a "
                   f"diferença é pequena. O poder do teste para detectá-la com n = {r.n} era de só "
                   f"{pct(poder)}, então não rejeitar era o resultado mais provável.")
    else:
        decisao = "✅ Decisão correta: H₀ é verdadeira na população e o teste não a rejeitou."
    m = st.columns(4)
    m[0].metric("Parâmetro populacional", f(param), help=f"N = {br(N_sub, 0)} {h['unidade']}")
    m[1].metric("Erro amostral (estimativa − parâmetro)",
                br(100 * (r.estimativa - param), 2) + " p.p." if h["tipo"] == "proporção"
                else br(r.estimativa - param, 2))
    m[2].metric("IC contém o parâmetro?", "Sim" if contem else "Não")
    m[3].metric("Poder do teste (aprox.)", pct(poder),
                help="Probabilidade de o teste rejeitar H₀, dado o valor real da população.")
    st.markdown(decisao)
    g.como_ler("- **Erro tipo I:** rejeitar uma H₀ verdadeira (alarme falso). A chance é α = 5%.\n"
               "- **Erro tipo II:** não rejeitar uma H₀ falsa (deixar passar).\n"
               "- **Poder:** a chance de o teste perceber que H₀ é falsa. Ele é alto quando a diferença real é "
               "grande ou o n é grande, e baixo quando a diferença é minúscula.")
    return {"Hipótese": h["id"], "Pergunta": h["pergunta"], "H₀": f"{simbolo} = {f(h['h0'])}",
            "H₁": f"{simbolo} {sinal} {f(h['h0'])}", "Estimativa": f(r.estimativa),
            "IC 95%": f"[{f(r.ic_inf)} ; {f(r.ic_sup)}]", "Parâmetro real": f(param),
            "IC contém?": "Sim" if contem else "Não",
            "Valor-p": "< 0,0001" if r.valor_p < 1e-4 else br(r.valor_p, 4),
            "Decisão": "Rejeita H₀" if r.rejeita_h0 else "Não rejeita H₀",
            "Na população": "H₀ falsa" if h0_falsa else "H₀ verdadeira"}


abas = st.tabs([h["aba"] for h in hp.HIPOTESES] + ["Resumo e comparação", "Variabilidade amostral",
                                                     "Bônus", "Limitações"])
linhas = []
for aba, h in zip(abas, hp.HIPOTESES):
    with aba:
        linhas.append(cartao(h))

with abas[4]:
    st.subheader("Resumo das quatro hipóteses")
    st.dataframe(pd.DataFrame(linhas), hide_index=True, width="stretch")
    st.markdown("""
**Como ler esta tabela**
- **Estimativa pontual × IC:** a estimativa é o melhor palpite único. O IC é a faixa de valores plausíveis para
  o parâmetro: ele é centrado na estimativa e sua largura reflete o erro-padrão.
- **IC × teste:** em um teste bilateral, rejeitar H₀ ao nível de 5% equivale a o valor de H₀ cair **fora** do
  IC de 95%.
- **Amostra × população:** como conhecemos a população, dá para verificar se cada IC "acertou". Na prática nunca
  sabemos isso. O que o método garante é que **95% dos ICs construídos assim** contêm o parâmetro (veja a aba
  *Variabilidade amostral*).
- **Não rejeitar ≠ aceitar:** quando o valor real está muito perto de H₀, o teste com n = 382 não tem poder para
  detectar a diferença. É um erro tipo II esperado, não uma falha do método.
""")

with abas[5]:
    st.subheader("Se tivéssemos sorteado outra amostra?")
    st.markdown("A simulação sorteia várias AAS do mesmo tamanho a partir da população e calcula o IC 95% de cada "
                "uma. Cerca de 95% delas devem conter o parâmetro real: esse é o significado de \"95% de "
                "confiança\". A confiança é no **método**, não em um intervalo específico.")
    c1, c2 = st.columns([1, 3])
    with c1:
        escolha = st.radio("Parâmetro", [h["id"] for h in hp.HIPOTESES],
                           format_func=lambda i: hp.POR_ID[i]["aba"])
        reps = st.slider("Número de amostras", 20, 200, 100, step=20)
        semente = st.number_input("Semente da simulação", value=1, step=1)
    h = hp.POR_ID[escolha]

    @st.cache_data
    def simular(id_hipotese: str, reps: int, semente: int):
        hh = hp.POR_ID[id_hipotese]
        valores = hp.valores(hh, pop)
        n = len(hp.valores(hh, am))
        return est.cobertura_ic(valores, n, reps, hh["tipo"], CONF, semente), float(valores.mean()), n

    ics, param_sim, n_sim = simular(escolha, reps, int(semente))
    fig, taxa = g.grafico_cobertura(ics, param_sim, FMT[escolha], proporcao=h["tipo"] == "proporção")
    with c2:
        st.plotly_chart(fig, width="stretch")
    with c1:
        st.metric("ICs que contêm o parâmetro", pct(taxa))
        st.caption(f"Cada amostra simulada tem n = {n_sim}, o mesmo tamanho da amostra real nesta hipótese.")

with abas[6]:
    bonus = st.radio("Teste bônus", ["Aces por superfície", "Zebras: melhor de 3 × melhor de 5",
                                     "Canhotos × destros"], horizontal=True)
    if bonus == "Aces por superfície":
        st.subheader("A superfície muda a quantidade de aces?")
        st.markdown("A grama é rápida e a bola quica baixo, o que favorece o saque. O saibro é lento e a bola quica "
                    "alto, o que favorece a devolução. A quadra dura fica no meio. Comparamos a média de aces nas "
                    "três superfícies (o carpete fica de fora: só 10 partidas na amostra, superfície extinta "
                    "em 2009).")
        itens = []
        for s in ["Grama", "Dura", "Saibro"]:
            x = am.loc[am["superficie"] == s, "aces_total"].dropna()
            media, _, _, li, ls, _ = est.ic_media_t(x, CONF)
            itens.append({"grupo": s, "n": len(x), "media": media, "ic_inf": li, "ic_sup": ls,
                          "parametro": pop.loc[pop["superficie"] == s, "aces_total"].mean()})
        st.plotly_chart(g.grafico_ics_grupos(itens, lambda v: br(v, 1), "Aces por partida: IC 95% da média por "
                                             "superfície (amostra) e média real (população)", g.CORES_SUP),
                        width="stretch")
        st.markdown("**Comparações par a par** (t de Welch, H₀: médias iguais, bilateral). Como fazemos **3 testes**, "
                    "usamos a correção de **Bonferroni**: cada valor-p é multiplicado por 3, para que a chance total "
                    "de um alarme falso continue em 5%.")
        linhas_p = []
        for a, b in [("Grama", "Dura"), ("Dura", "Saibro"), ("Grama", "Saibro")]:
            w = est.teste_welch(am.loc[am.superficie == a, "aces_total"], am.loc[am.superficie == b, "aces_total"])
            pb = min(1.0, w["valor_p"] * 3)
            dif_pop = (pop.loc[pop.superficie == a, "aces_total"].mean()
                       - pop.loc[pop.superficie == b, "aces_total"].mean())
            linhas_p.append({"Comparação": f"{a} − {b}", "n": f"{w['n_a']} × {w['n_b']}",
                             "Diferença (amostra)": br(w["diferenca"], 1),
                             "IC 95%": f"[{br(w['ic_inf'], 1)} ; {br(w['ic_sup'], 1)}]",
                             "t": br(w["estatistica"], 2),
                             "Valor-p (Bonferroni)": "< 0,0001" if pb < 1e-4 else br(pb, 4),
                             "Decisão (α = 5%)": "Diferença significativa" if pb < 0.05 else "Não significativa",
                             "Diferença real (população)": br(dif_pop, 1)})
        st.dataframe(pd.DataFrame(linhas_p), hide_index=True, width="stretch")
        st.info("**Leitura:** saibro tem claramente menos aces que dura e grama. Já grama × dura não deu diferença "
                "significativa na amostra, embora na população a grama tenha cerca de 3,7 aces a mais. O motivo é o "
                "tamanho: só 30 partidas de grama na amostra, o que deixa o IC largo. É um erro tipo II causado por "
                "um subgrupo pequeno.")
    elif bonus == "Zebras: melhor de 3 × melhor de 5":
        st.subheader("O favorito vence mais em partidas melhor de 5 sets?")
        st.markdown("Ideia: em jogos mais longos, a sorte de um set isolado pesa menos e a qualidade aparece mais. "
                    "Teste de **diferença entre duas proporções**.\n- **H₀:** p₅ = p₃\n- **H₁:** p₅ > p₃ "
                    "(o favorito vence mais no melhor de 5)")

        def fav(df, bo):
            x = df.loc[(df["melhor_de"] == bo) & df["favorito_venceu"].notna(), "favorito_venceu"]
            return int((x == "Sim").sum()), len(x)
        s5, n5 = fav(am, "Melhor de 5")
        s3, n3 = fav(am, "Melhor de 3")
        d = est.teste_duas_proporcoes(s5, n5, s3, n3, "maior", ALFA)
        ps5, pn5 = fav(pop, "Melhor de 5")
        ps3, pn3 = fav(pop, "Melhor de 3")
        m = st.columns(5)
        m[0].metric("Melhor de 5 (amostra)", pct(d["p1"]), help=f"n = {n5}")
        m[1].metric("Melhor de 3 (amostra)", pct(d["p2"]), help=f"n = {n3}")
        m[2].metric("Diferença e IC 95%", f"{br(100 * d['diferenca'], 1)} p.p.",
                    help=f"IC: [{br(100 * d['ic_inf'], 1)} ; {br(100 * d['ic_sup'], 1)}] p.p.")
        m[3].metric("z / valor-p", f"{br(d['estatistica'], 2)} / {br(d['valor_p'], 4)}")
        m[4].metric("Diferença real (população)", f"{br(100 * (ps5 / pn5 - ps3 / pn3), 1)} p.p.",
                    help=f"{pct(ps5 / pn5)} × {pct(ps3 / pn3)}")
        st.latex(r"z=\frac{\hat p_5-\hat p_3}{\sqrt{\hat p(1-\hat p)\left(\frac1{n_5}+\frac1{n_3}\right)}}"
                 r"\quad\text{com } \hat p = \frac{x_5+x_3}{n_5+n_3}\text{ (proporção combinada)}")
        (st.success if d["rejeita_h0"] else st.info)(
            f"**Conclusão:** valor-p = {br(d['valor_p'], 4)} {'<' if d['rejeita_h0'] else '≥'} α → "
            f"**{'rejeitamos' if d['rejeita_h0'] else 'não rejeitamos'} H₀**. Na população a diferença existe "
            f"({br(100 * (ps5 / pn5 - ps3 / pn3), 1)} p.p. a favor do melhor de 5), mas com só {n5} partidas melhor "
            f"de 5 na amostra o teste fica no limite da significância.")
    else:
        st.subheader("Canhotos levam vantagem sobre destros?")
        st.markdown("Diz-se que canhotos têm vantagem porque os adversários estão menos acostumados com eles. "
                    "Olhamos só os **duelos canhoto × destro** e testamos se o canhoto vence mais da metade.\n"
                    "- **H₀:** p = 50%\n- **H₁:** p > 50%")

        def canh(df):
            mm = df["mao_vencedor"].notna() & df["mao_perdedor"].notna() & (df["mao_vencedor"] != df["mao_perdedor"])
            x = df.loc[mm, "mao_vencedor"]
            return int((x == "Canhoto").sum()), len(x)
        s, n = canh(am)
        r = est.teste_z_proporcao(s, n, 0.5, "maior", ALFA)
        ps, pn = canh(pop)
        m = st.columns(4)
        m[0].metric("Duelos na amostra", n)
        m[1].metric("Canhoto venceu (amostra)", pct(r.estimativa),
                    help=f"IC 95%: [{pct(r.ic_inf)} ; {pct(r.ic_sup)}]")
        m[2].metric("Valor-p", br(r.valor_p, 4))
        m[3].metric("População", pct(ps / pn), help=f"{br(pn, 0)} duelos canhoto × destro")
        pv = (pop["mao_vencedor"] == "Canhoto").mean()
        pp = (pop["mao_perdedor"] == "Canhoto").mean()
        (st.success if r.rejeita_h0 else st.info)(
            f"**Conclusão:** {'rejeitamos' if r.rejeita_h0 else 'não rejeitamos'} H₀. E a população confirma: em "
            f"{br(pn, 0)} duelos, o canhoto venceu {pct(ps / pn)}. No circuito principal, ser canhoto **não** dá "
            f"vantagem nos resultados, o que contraria o senso comum. Os canhotos aparecem em {pct(pv)} das vitórias "
            f"e em {pct(pp)} das derrotas, praticamente a mesma fatia.")

with abas[7]:
    st.subheader("Limitações da análise")
    st.markdown("""
- **Independência:** a AAS trata cada partida como unidade, mas partidas do mesmo jogador ou torneio não são
  totalmente independentes (Federer, Nadal e Djokovic aparecem em centenas delas). Os erros-padrão podem estar um
  pouco subestimados.
- **Assimetria:** duração e aces têm cauda longa à direita. Isso inclui a partida Isner × Mahut em Wimbledon 2010,
  com 665 minutos e 216 aces. O TCL resolve a inferência para a média com n = 382, mas a **mediana** descreve
  melhor a partida típica.
- **Dados ausentes:** cerca de 1% das partidas não tem duração ou estatísticas de saque. As análises usam os casos
  disponíveis, assumindo que a falta é aleatória.
- **Definição da população:** excluímos W/O e abandonos. As conclusões valem para **partidas concluídas do circuito
  principal**, não para Challengers, qualificatórios ou o circuito feminino.
- **Um único sorteio:** cada conclusão vem de uma amostra. Outra semente daria estimativas um pouco diferentes (veja
  a aba *Variabilidade amostral*), e decisões perto do limite de α podem mudar.
- **Mudança ao longo do tempo:** 26 temporadas misturam eras diferentes (bolas, quadras e estilos de jogo). Os
  parâmetros são médias do período, não de um ano específico.
- **Subgrupos pequenos:** a amostra foi dimensionada para proporções da base inteira. Em subgrupos (grama ≈ 8% da
  amostra, melhor de 5 ≈ 17%) a precisão é bem menor, como mostram os testes bônus.
""")
