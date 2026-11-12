"""Painel 2 — Análise descritiva da amostra, comparada com a população."""
import streamlit as st

import dados
import graficos as g

st.set_page_config(page_title="2 · Amostra", page_icon="🎾", layout="wide")
st.title("Painel 2 · Análise descritiva da amostra")
st.caption("Amostra aleatória simples das partidas da população. Os valores aqui são "
           "**estatísticas**: mudariam se outra amostra fosse sorteada.")

pop, am = dados.populacao(), dados.amostra()

with st.container(border=True):
    st.markdown("""
#### 🎯 O que estamos vendo aqui?
- **De onde vem a amostra:** das 66.819 partidas da população, o computador **sorteou 382**, como num
  sorteio de bingo em que cada partida tinha a mesma chance de sair. Todos os números desta página são
  calculados **só com essas 382 partidas** (a lista completa está no final da página).
- **O que queremos ver:** se a amostra é um "retrato em miniatura" da população. Se o sorteio foi bem feito,
  as proporções e médias da amostra devem ficar **perto** das da população, mas não iguais.
- **Por que não são iguais?** Por acaso. Cada sorteio traz partidas diferentes, e essa diferença natural se
  chama **erro amostral**. Ela não é um defeito: é justamente o que o Painel 3 mede com os intervalos
  de confiança.
""")

filtros = g.filtros_sidebar(pop)
pop_f, am_f = g.filtrar(pop, filtros), g.filtrar(am, filtros)

comparar = st.toggle("Sobrepor a população nos gráficos", value=True,
                     help="Mostra população (violeta) e amostra (amarelo) lado a lado.")
if len(am_f) < 30:
    st.warning(f"Com esses filtros sobram só {len(am_f)} partidas na amostra: as estatísticas ficam muito "
               "instáveis. Isso é a variabilidade amostral em ação.")

g.painel_descritivo(am_f, "Amostra", ref=pop_f if comparar else None)

st.header("População × amostra")
g.como_ler("Cada linha compara a **estatística da amostra** com o **parâmetro da população**, nos mesmos filtros. "
           "Diferenças pequenas e **sem direção sistemática** (ora para cima, ora para baixo) são o esperado em "
           "um sorteio aleatório: são **erro amostral**, não viés. Viés seria a amostra errar sempre para o mesmo "
           "lado, por exemplo se só tivéssemos sorteado finais.")
c1, c2 = st.columns(2)
with c1:
    st.subheader("Variáveis quantitativas")
    st.dataframe(g.comparacao_medidas(pop_f, am_f).style.format(
        {"População": "{:.2f}", "Amostra": "{:.2f}", "Diferença": "{:+.2f}", "Diferença (%)": "{:+.1f}%"},
        decimal=",", thousands="."), hide_index=True, width="stretch", height=520)
with c2:
    st.subheader("Variáveis qualitativas")
    st.dataframe(g.comparacao_proporcoes(pop_f, am_f).style.format(
        {"População (%)": "{:.1f}", "Amostra (%)": "{:.1f}", "Diferença (p.p.)": "{:+.1f}"},
        decimal=",", thousands="."), hide_index=True, width="stretch", height=520)

st.header("As partidas sorteadas")
st.caption(f"{len(am_f)} partidas da amostra com os filtros atuais (de {len(am)} no total). "
           "`id_partida` é o número da partida na população, de 1 a 66.819.")
st.dataframe(am_f[["id_partida", "ano", "torneio", "nivel", "superficie", "rodada", "vencedor", "perdedor",
                   "placar", "minutos", "aces_total", "favorito_venceu"]],
             hide_index=True, width="stretch", height=420)
