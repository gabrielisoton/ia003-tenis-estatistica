"""O circuito em números: descritiva da população inteira, com filtros (reaproveita o painel descritivo do núcleo)."""
import streamlit as st

from nucleo import dados
from nucleo import graficos as g

st.title("O circuito em números")
st.caption("Todas as partidas do circuito principal da ATP concluídas entre 2000 e 2025. Use os filtros do menu "
           "lateral para recortar por superfície, nível do torneio, anos ou jogadores do Top N.")

pop = dados.populacao()
filtros = g.filtros_sidebar(pop)
g.painel_descritivo(g.filtrar(pop, filtros), "População")
