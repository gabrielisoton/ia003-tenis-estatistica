"""Dados próprios do trabalho da IA003: a amostra aleatória simples e o cálculo do tamanho amostral.
(A população é compartilhada e vem de `nucleo.dados`.)"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

AMOSTRA = Path(__file__).resolve().parents[1] / "amostra"


@st.cache_data
def amostra() -> pd.DataFrame:
    return pd.read_csv(AMOSTRA / "amostra.csv")


@st.cache_data
def tamanho_amostral() -> dict:
    return json.loads((AMOSTRA / "tamanho_amostral.json").read_text(encoding="utf-8"))
