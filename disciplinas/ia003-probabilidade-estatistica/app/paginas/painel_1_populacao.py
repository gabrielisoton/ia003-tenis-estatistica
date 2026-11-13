"""Painel 1 — Análise descritiva da população."""
import streamlit as st

from nucleo import dados
from nucleo import graficos as g

st.title("Painel 1 · Análise descritiva da população")
st.caption("Todas as partidas do circuito principal da ATP concluídas entre 2000 e 2025. "
           "Os valores aqui são **parâmetros**: não há incerteza amostral.")

pop = dados.populacao()
filtros = g.filtros_sidebar(pop)
g.painel_descritivo(g.filtrar(pop, filtros), "População")
