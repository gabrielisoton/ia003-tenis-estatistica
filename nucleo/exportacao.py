"""Utilidades dos exportadores de JSON dos sites (projeto e disciplinas).

O Python é o "motor" estatístico; os sites HTML só leem os JSON gerados.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]
BASE = RAIZ / "nucleo" / "base"

SUP = ["Dura", "Saibro", "Grama", "Carpete"]
NIV = ["Grand Slam", "ATP Finals", "Masters 1000", "ATP 500", "ATP 250"]
ROD = ["1ª rodada (R128)", "R64", "R32", "Oitavas (R16)", "Quartas", "Semifinal", "Final",
       "Fase de grupos", "3rd/4th"]
CODIGOS = {"sup": SUP, "niv": NIV, "rod": ROD, "mao": ["Destro", "Canhoto"]}


def populacao() -> pd.DataFrame:
    return pd.read_parquet(BASE / "populacao.parquet")


def resumo() -> dict:
    return json.loads((BASE / "resumo_populacao.json").read_text(encoding="utf-8"))


def limpo(v):
    """Converte numpy/NaN para tipos que o JSON aceita."""
    if isinstance(v, dict):
        return {str(k): limpo(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [limpo(x) for x in v]
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return None if np.isnan(v) else round(float(v), 6)
    return v


def salvar(saida: Path, nome: str, obj) -> None:
    saida.mkdir(parents=True, exist_ok=True)
    caminho = saida / nome
    caminho.write_text(json.dumps(limpo(obj), ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                       encoding="utf-8")
    print(f"{nome:16s} {caminho.stat().st_size / 1024:8.0f} KB")


def codigo(serie: pd.Series, ordem: list) -> list:
    mapa = {c: i for i, c in enumerate(ordem)}
    return [mapa.get(v) if isinstance(v, str) else None for v in serie]


def inteiros(serie: pd.Series) -> list:
    return [None if pd.isna(v) else int(v) for v in serie]


def colunar(df: pd.DataFrame) -> dict:
    """Colunas compactas das partidas (para os filtros e o painel descritivo no navegador)."""
    return {
        "ano": df["ano"].astype(int).tolist(),
        "sup": codigo(df["superficie"], SUP),
        "niv": codigo(df["nivel"], NIV),
        "rod": codigo(df["rodada"], ROD),
        "bo": df["melhor_de"].map({"Melhor de 3": 3, "Melhor de 5": 5}).astype(int).tolist(),
        "mao": codigo(df["mao_vencedor"], ["Destro", "Canhoto"]),
        "fav": [None if v is None or pd.isna(v) else int(v == "Sim") for v in df["favorito_venceu"]],
        "dec": (df["set_decisivo"] == "Sim").astype(int).tolist(),
        "min": inteiros(df["minutos"]),
        "ace": inteiros(df["aces_total"]),
        "df": inteiros(df["duplas_faltas_total"]),
        "idade": [None if pd.isna(v) else round(float(v), 1) for v in df["idade_vencedor"]],
        "alt": inteiros(df["altura_vencedor"]),
        "dif": inteiros(df["dif_ranking"]),
        "rv": inteiros(df["ranking_vencedor"]),
        "rp": inteiros(df["ranking_perdedor"]),
        "sets": df["sets_jogados"].astype(int).tolist(),
    }
