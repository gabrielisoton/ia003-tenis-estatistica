"""Carregamento dos dados (com cache) e formatação de números em pt-BR."""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

RAIZ = Path(__file__).resolve().parents[1]
FONTE_URL = "https://github.com/Tennismylife/TML-Database"
FONTE_NOME = "TML-Database (Tennismylife)"


@st.cache_data
def populacao() -> pd.DataFrame:
    return pd.read_parquet(RAIZ / "dados" / "populacao.parquet")


@st.cache_data
def amostra() -> pd.DataFrame:
    return pd.read_csv(RAIZ / "amostra" / "amostra.csv")


@st.cache_data
def resumo() -> dict:
    return json.loads((RAIZ / "dados" / "resumo_populacao.json").read_text(encoding="utf-8"))


@st.cache_data
def tamanho_amostral() -> dict:
    return json.loads((RAIZ / "amostra" / "tamanho_amostral.json").read_text(encoding="utf-8"))


def br(x, casas: int = 2) -> str:
    """Formata número no padrão brasileiro: 1.234,56."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    s = f"{x:,.{casas}f}"
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x, casas: int = 1) -> str:
    return br(100 * x, casas) + "%"
