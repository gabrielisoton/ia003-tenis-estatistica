"""Mantém um app Streamlit coerente quando o código muda com o servidor rodando.

No Streamlit Cloud, um push atualiza os arquivos, mas o processo continua com os módulos
já importados em memória, e o `st.cache_data` continua servindo resultados calculados pela
versão antiga (a chave do cache só considera o código da função da página). Isso já quebrou
o app duas vezes (AttributeError e KeyError).

`preparar()` é chamada no início de cada `main.py`, a cada execução: guarda o md5 dos módulos
locais e, quando ele muda, recarrega os módulos e limpa o cache uma única vez.
"""
from __future__ import annotations

import hashlib
import importlib
import sys
from pathlib import Path

import streamlit as st

NUCLEO = Path(__file__).resolve().parent
# ordem de recarga: dependências antes de quem as importa
MODULOS_NUCLEO = ["nucleo.idiomas", "nucleo.enderecos", "nucleo.dados", "nucleo.estatistica", "nucleo.graficos",
                  "nucleo.analises", "nucleo.secoes"]


@st.cache_resource
def _estado() -> dict:
    return {"md5": None}


def _md5(arquivos: list[Path]) -> str:
    h = hashlib.md5()
    for a in sorted(arquivos):
        h.update(a.read_bytes())
    return h.hexdigest()


def preparar(pasta_app: Path | None = None, modulos_app: tuple[str, ...] = ()) -> None:
    """`pasta_app`/`modulos_app`: módulos locais do próprio app (ex.: hipoteses da IA003)."""
    arquivos = list(NUCLEO.glob("*.py")) + (list(Path(pasta_app).glob("*.py")) if pasta_app else [])
    atual, estado = _md5(arquivos), _estado()
    if estado["md5"] is not None and estado["md5"] != atual:
        for nome in [*MODULOS_NUCLEO, *modulos_app]:
            if nome in sys.modules:
                importlib.reload(sys.modules[nome])
        st.cache_data.clear()
    estado["md5"] = atual
