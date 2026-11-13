"""Página inicial: a base de dados, a população e o desenho amostral."""
import pandas as pd
import streamlit as st

import dados

st.set_page_config(page_title="Tênis ATP — Estatística para IA", page_icon="🎾", layout="wide")

pop = dados.populacao()
res = dados.resumo()
tam = dados.tamanho_amostral()

st.title("🎾 Quem vence no tênis? Inferência estatística no circuito ATP (2000–2025)")
st.caption("Atividade avaliativa final · IA003 Probabilidade e Estatística para IA · "
           "Especialização em IA · UFRGS")

st.markdown(
    "Este app compara **toda a população** de partidas do circuito principal da ATP com uma "
    "**amostra aleatória simples** dela. Os parâmetros populacionais são calculados diretamente, "
    "e a inferência (intervalos de confiança e testes de hipóteses) usa **só a amostra**. "
    "Como conhecemos a população, dá para ver se a amostra acertou."
)
st.markdown("**Navegue pelos painéis no menu lateral:** 1 · População → 2 · Amostra → 3 · Inferência. "
            "As páginas marcadas como **Extra** ficam fora do trabalho avaliado (veja o fim desta página).")

st.header("1. A base de dados")
c1, c2 = st.columns([3, 2])
with c1:
    st.markdown(f"""
- **Fonte:** [{dados.FONTE_NOME}]({dados.FONTE_URL}). É uma base pública de partidas da ATP, com um
  arquivo por temporada desde 1968, mantida e atualizada pelo projeto Tennismylife
  ([stats.tennismylife.org](https://stats.tennismylife.org/tennis-match-database)).
- **Origem e esquema:** a TML segue o mesmo dicionário de dados da base *tennis_atp* de Jeff Sackmann
  (Tennis Abstract), referência em pesquisas de analytics no tênis. Essa base foi retirada do GitHub
  pelo autor em 2026.
- **Contexto e objetivo:** a base registra resultados, placares, perfil dos jogadores (idade, altura,
  mão dominante, país, ranking) e estatísticas de saque de cada partida. Serve para estudar desempenho,
  equilíbrio competitivo e capacidade preditiva do ranking.
- **Arquivos usados:** temporadas de 2000 a 2025, com {dados.br(res['etapas_filtro']['partidas_brutas_2000_2025'], 0)}
  partidas e {res['n_variaveis_brutas']} variáveis brutas.
""")
with c2:
    st.metric("Partidas na população (N)", dados.br(res["N"], 0))
    st.metric("Variáveis selecionadas para a análise", 13,
              help=f"A base processada tem {res['n_variaveis']} colunas, incluindo as estatísticas de saque "
                   "usadas na página Explorar.")
    st.metric("Edições de torneios", dados.br(res["n_torneios"], 0))
    st.metric("Jogadores distintos", dados.br(res["n_jogadores"], 0))

st.header("2. População de interesse e unidade amostral")
st.markdown("""
- **População:** todas as partidas de simples do **circuito principal da ATP** de 2000 a 2025
  (Grand Slams, ATP Finals, Masters 1000, ATP 500 e ATP 250) **concluídas em quadra**.
- **Unidade amostral:** a **partida**.
- **Ficaram de fora:** Copa Davis, Jogos Olímpicos, eventos por equipes ou de exibição (ATP Cup,
  United Cup, Laver Cup e Next Gen Finals, que usa sets curtos) e partidas não concluídas
  (W/O, abandono ou desclassificação), porque elas não têm duração nem placar completo comparáveis.
""")
etapas = res["etapas_filtro"]
st.dataframe(pd.DataFrame({
    "Etapa": ["Partidas brutas 2000–2025", "Somente circuito principal",
              "Excluindo partidas não concluídas (população final)"],
    "Partidas": [etapas["partidas_brutas_2000_2025"], etapas["apos_filtro_nivel"],
                 etapas["apos_excluir_nao_concluidas"]],
}), hide_index=True)

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
aus = {k: v for k, v in res["pct_ausentes"].items() if v > 0}
st.caption("Valores ausentes (% da população): " +
           ", ".join(f"{k} {dados.br(v)}%" for k, v in aus.items()) +
           ". As análises de cada variável usam as partidas com o dado disponível.")

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
O código está em `scripts/02_tamanho_amostral.py` e `scripts/03_sortear_amostra.py`.
""")

st.divider()
st.header("Extras · para fãs de tênis (fora da avaliação)")
st.markdown("""
Estas páginas vão além do que o trabalho pede. Usam a **população inteira**, são descritivas e **não fazem parte
da avaliação**. No menu lateral elas têm o prefixo **Extra ·**.
- **Extra · Explorar:** o que separa o Top N dos demais, a chance de zebra conforme a diferença de ranking e como o
  jogo mudou de 2000 a 2025.
- **Extra · Jogadores:** os líderes de todos os critérios de uma vez (pódio e quadro de medalhas), o ranking dos jogadores em cada aspecto do jogo (saque, devolução, break points, tie-breaks,
  títulos…) com o IC 95% de Wilson, e o perfil individual de cada jogador: percentil em cada critério, desempenho
  por superfície, evolução ano a ano e lista de títulos.
""")
