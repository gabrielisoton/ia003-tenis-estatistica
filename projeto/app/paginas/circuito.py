"""O circuito em números: descritiva da população inteira, com filtros (reaproveita o painel descritivo do núcleo)."""
import streamlit as st

from nucleo import dados
from nucleo import graficos as g
from nucleo.idiomas import T

st.title(T("O circuito em números", "The tour in numbers"))
st.caption(T("Todas as partidas do circuito principal da ATP concluídas entre 2000 e 2025. Use os filtros do menu "
             "lateral para recortar por superfície, nível do torneio, anos ou jogadores do Top N.",
             "Every completed match on the ATP main tour between 2000 and 2025. Use the filters in the side "
             "menu to slice by surface, tournament level, years or Top N players."))

pop = dados.populacao()
filtros = g.filtros_sidebar(pop, prefixo="circ")
g.painel_descritivo(g.filtrar(pop, filtros), "População")
