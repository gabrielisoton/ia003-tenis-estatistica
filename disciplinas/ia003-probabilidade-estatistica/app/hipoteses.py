"""Definição única das hipóteses do trabalho, usada pelo Streamlit e pelo site HTML.

Cada hipótese diz: que subconjunto da base usar, qual variável, o evento de
interesse (proporção) e os valores de H0/H1. Os cálculos ficam em estatistica.py.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from nucleo import estatistica as est

HIPOTESES = [
    {
        "id": "P1", "aba": "P1 · Favorito vence?", "tipo": "proporção",
        "var": "favorito_venceu", "filtro": "com_ranking",
        "h0": 0.5, "alt": "maior",
        "parametro_nome": "p = proporção de partidas vencidas pelo jogador de melhor ranking",
        "pergunta": "O jogador com melhor ranking vence mais da metade das partidas?",
        "justificativa": "Se o ranking ATP não tivesse poder preditivo, o favorito venceria 50% das vezes, "
                         "como numa moeda. Essa é a linha de base de qualquer modelo de IA de previsão de "
                         "resultados: um modelo só tem valor se superar o simples \"aposte no favorito\".",
        "unidade": "partidas com ranking dos dois jogadores",
    },
    {
        "id": "P2", "aba": "P2 · Set decisivo", "tipo": "proporção",
        "var": "set_decisivo", "filtro": "todas",
        "h0": 1 / 3, "alt": "bilateral",
        "parametro_nome": "p = proporção de partidas que vão ao set decisivo",
        "pergunta": "Uma em cada três partidas vai ao set decisivo?",
        "justificativa": "A proporção de partidas que chegam ao set decisivo (3º set no melhor de 3, 5º no "
                         "melhor de 5) mede o equilíbrio competitivo do circuito. O valor de 1/3 é uma "
                         "referência comum de comentaristas.",
        "unidade": "todas as partidas",
    },
    {
        "id": "M1", "aba": "M1 · Duração", "tipo": "média",
        "var": "minutos", "filtro": "melhor_de_3",
        "h0": 100.0, "alt": "bilateral",
        "parametro_nome": "μ = duração média (minutos) das partidas melhor de 3",
        "pergunta": "Uma partida melhor de 3 sets dura, em média, 1h40 (100 minutos)?",
        "justificativa": "A duração média orienta a grade de TV, a programação das quadras e o planejamento "
                         "físico dos jogadores. 1h40 é a referência usual de mercado.",
        "unidade": "partidas melhor de 3 com duração registrada",
    },
    {
        "id": "M2", "aba": "M2 · Aces", "tipo": "média",
        "var": "aces_total", "filtro": "todas",
        "h0": 10.0, "alt": "bilateral",
        "parametro_nome": "μ = número médio de aces por partida (os dois jogadores somados)",
        "pergunta": "Uma partida tem, em média, 10 aces (cerca de 5 por jogador)?",
        "justificativa": "Os aces resumem o domínio do saque, a principal arma do tênis moderno. Cinco aces "
                         "por jogador é uma referência intuitiva de partida \"normal\".",
        "unidade": "partidas com estatísticas de saque",
    },
]
POR_ID = {h["id"]: h for h in HIPOTESES}


def subconjunto(h: dict, df: pd.DataFrame) -> pd.DataFrame:
    if h["filtro"] == "com_ranking":
        return df[df["favorito_venceu"].notna()]
    if h["filtro"] == "melhor_de_3":
        return df[df["melhor_de"] == "Melhor de 3"]
    return df


def valores(h: dict, df: pd.DataFrame) -> np.ndarray:
    """Vetor usado na inferência: 0/1 para proporção, números para média (sem ausentes)."""
    x = subconjunto(h, df)[h["var"]].dropna()
    return (x == "Sim").to_numpy(float) if h["tipo"] == "proporção" else x.to_numpy(float)


def rodar(h: dict, df: pd.DataFrame, alfa: float = 0.05, confianca: float = 0.95) -> est.Resultado:
    x = valores(h, df)
    if h["tipo"] == "proporção":
        return est.teste_z_proporcao(int(x.sum()), len(x), h["h0"], h["alt"], alfa, confianca)
    return est.teste_t_media(x, h["h0"], h["alt"], alfa, confianca)


def parametro(h: dict, pop: pd.DataFrame) -> tuple[float, float, int]:
    """(parâmetro populacional, desvio-padrão populacional, N do subconjunto)."""
    x = valores(h, pop)
    return float(x.mean()), float(x.std(ddof=0)), len(x)


def poder(h: dict, param: float, sigma: float, n: int, alfa: float) -> float:
    if h["tipo"] == "proporção":
        return est.poder_proporcao(param, h["h0"], n, h["alt"], alfa)
    return est.poder_media(param, h["h0"], sigma, n, h["alt"], alfa)


def h0_falsa(h: dict, param: float) -> bool:
    if h["alt"] == "maior":
        return param > h["h0"]
    if h["alt"] == "menor":
        return param < h["h0"]
    return not np.isclose(param, h["h0"])
