"""Carregamento da base compartilhada (com cache) e formatação de números em pt-BR.

A população vem de `nucleo/base/`, gerada por `nucleo/scripts/01_preparar_populacao.py`.
Dados de uma disciplina (por exemplo, a amostra da IA003) ficam na pasta da disciplina.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from nucleo.idiomas import ingles

BASE = Path(__file__).resolve().parent / "base"
FONTE_URL = "https://github.com/Tennismylife/TML-Database"
FONTE_NOME = "TML-Database (Tennismylife)"
TERMOS_URL = "https://stats.tennismylife.org/tennis-match-database#usage-terms"


@st.cache_data
def populacao() -> pd.DataFrame:
    return pd.read_parquet(BASE / "populacao.parquet")


@st.cache_data
def resumo() -> dict:
    return json.loads((BASE / "resumo_populacao.json").read_text(encoding="utf-8"))


def br(x, casas: int = 2) -> str:
    """Formata número no padrão brasileiro: 1.234,56 (em inglês, no app do projeto: 1,234.56)."""
    if x is None or (isinstance(x, float) and pd.isna(x)):
        return "—"
    s = f"{x:,.{casas}f}"
    if ingles():
        return s
    return s.replace(",", "_").replace(".", ",").replace("_", ".")


def pct(x, casas: int = 1) -> str:
    return br(100 * x, casas) + "%"
