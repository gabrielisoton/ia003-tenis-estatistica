"""Página inicial do trabalho: a base de dados, a população e o desenho amostral."""
import pandas as pd
import streamlit as st

import dados_amostra as da
from nucleo import dados, enderecos, secoes

res = dados.resumo()
tam = da.tamanho_amostral()

st.title("🎾 Quem vence no tênis? Inferência estatística no circuito ATP (2000–2025)")
st.caption("Atividade avaliativa final · IA003 Probabilidade e Estatística para IA · "
           "Especialização em IA · UFRGS")

st.markdown(
    "Este app compara **toda a população** de partidas do circuito principal da ATP com uma "
    "**amostra aleatória simples** dela. Os parâmetros populacionais são calculados diretamente, "
    "e a inferência (intervalos de confiança e testes de hipóteses) usa **só a amostra**. "
    "Como conhecemos a população, dá para ver se a amostra acertou."
)
st.markdown("**Navegue pelos painéis no menu lateral:** 1 · População → 2 · Amostra → 3 · Inferência.")

secoes.base(res, metrica_variaveis=(
    "Variáveis selecionadas para a análise", 13,
    f"A base processada tem {res['n_variaveis']} colunas, incluindo as estatísticas de saque usadas no projeto "
    "Tênis em números."))
secoes.populacao(res)

st.subheader("Variáveis selecionadas")
st.dataframe(pd.DataFrame([
    ["superficie", "Qualitativa nominal", "Dura, saibro, grama ou carpete"],
    ["nivel", "Qualitativa ordinal", "Grand Slam, ATP Finals, Masters 1000, ATP 500, ATP 250"],
    ["melhor_de", "Qualitativa", "Melhor de 3 ou de 5 sets"],
    ["rodada", "Qualitativa ordinal", "Da 1ª rodada à final"],
    ["mao_vencedor", "Qualitativa nominal", "Destro ou canhoto"],
    ["favorito_venceu", "Qualitativa binária (derivada)", "O jogador com melhor ranking venceu?"],
    ["set_decisivo", "Qualitativa binária (derivada)", "A partida foi ao 3º set (melhor de 3) ou ao 5º set (melhor de 5)?"],
    ["minutos", "Quantitativa contínua", "Duração da partida em minutos"],
    ["aces_total", "Quantitativa discreta", "Aces dos dois jogadores somados"],
    ["duplas_faltas_total", "Quantitativa discreta", "Duplas faltas dos dois jogadores somadas"],
    ["idade_vencedor", "Quantitativa contínua", "Idade do vencedor no torneio (anos)"],
    ["altura_vencedor", "Quantitativa contínua", "Altura do vencedor (cm)"],
    ["dif_ranking", "Quantitativa discreta (derivada)", "Diferença absoluta de ranking ATP entre os jogadores"],
], columns=["Variável", "Tipo", "Descrição"]), hide_index=True, width="stretch")
secoes.ausentes(res)

st.header("3. Dimensionamento e seleção da amostra")
c1, c2 = st.columns(2)
with c1:
    st.markdown(f"""
**Parâmetros do cálculo** (tamanho amostral para estimar uma proporção, a mesma fórmula da calculadora USP/Bauru indicada no enunciado):
- Nível de confiança de **{dados.pct(tam['confianca'], 0)}** (z = {dados.br(tam['z'])}), o padrão em pesquisas.
- Margem de erro de **{dados.br(tam['margem_erro'] * 100, 0)} pontos percentuais**, suficiente para distinguir
  proporções como 50% e 65%.
- **p = 0,5**: sem informação prévia, é o valor que **maximiza** p(1−p). É o cenário mais conservador,
  que garante a margem de erro para qualquer proporção estudada.
""")
    st.latex(r"n_0=\frac{z^2\,p(1-p)}{E^2}=\frac{1{,}96^2\cdot 0{,}25}{0{,}05^2}\approx " + dados.br(tam["n0_pop_infinita"]))
    st.latex(r"n=\frac{n_0}{1+\frac{n_0-1}{N}}=\frac{" + dados.br(tam["n0_pop_infinita"]) + r"}{1+\frac{"
             + dados.br(tam["n0_pop_infinita"] - 1) + "}{" + dados.br(tam["N"], 0) + r"}}\approx "
             + dados.br(tam["n_corrigido"]) + r"\;\Rightarrow\; n=" + str(tam["n"]))
with c2:
    st.markdown(f"""
**Seleção da amostra aleatória simples (AAS):**
1. Cada partida da população recebeu um identificador de 1 a N.
2. Foram sorteadas **{tam['n']} partidas sem reposição** com `pandas.DataFrame.sample`, usando a
   semente fixa **15112026** para que o sorteio possa ser reproduzido.
3. Cada partida teve a mesma probabilidade de inclusão:
   n/N = {tam['n']}/{dados.br(tam['N'], 0)} ≈ {dados.pct(tam['n'] / tam['N'], 2)}.

Como n/N < 5%, a correção para população finita praticamente não altera os erros-padrão.
O código está em `disciplinas/ia003-probabilidade-estatistica/scripts/02_tamanho_amostral.py` e `03_sortear_amostra.py`.
""")

st.divider()
st.header("Para quem gosta de tênis")
st.markdown(f"""
Este trabalho deu origem ao projeto **Tênis em números**, que usa a mesma base para explorar o jogo e **não faz
parte da avaliação**: o que separa a elite do resto, a chance de zebra conforme o ranking, como o jogo mudou em
25 anos e quem é o melhor em cada aspecto (saque, devolução, break points, tie-breaks, títulos), com o perfil
completo de cada jogador. [Abrir o projeto]({enderecos.APP_PROJETO or enderecos.SITE_PROJETO}).
""")
