"""App Streamlit do trabalho da IA003: Base e amostra · Painéis 1, 2 e 3.

Rodar localmente (da raiz do repositório):
    streamlit run disciplinas/ia003-probabilidade-estatistica/app/main.py
No Streamlit Cloud, até a nota sair, o app entregue usa o atalho `app/Home.py`, que executa este arquivo.
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[2]
for caminho in (str(RAIZ), str(AQUI)):  # `nucleo` (compartilhado) e os módulos deste app
    if caminho not in sys.path:
        sys.path.insert(0, caminho)

import streamlit as st  # noqa: E402

from nucleo import enderecos, recarga  # noqa: E402

recarga.preparar(AQUI, ("dados_amostra", "hipoteses"))
st.set_page_config(page_title="Tênis ATP — Estatística para IA", page_icon="🎾", layout="wide")

PAGINAS = AQUI / "paginas"
pagina = st.navigation([
    st.Page(PAGINAS / "inicio.py", title="Home", icon="🎾", default=True),
    st.Page(PAGINAS / "painel_1_populacao.py", title="Painel 1 · População", url_path="Painel_1_·_População"),
    st.Page(PAGINAS / "painel_2_amostra.py", title="Painel 2 · Amostra", url_path="Painel_2_·_Amostra"),
    st.Page(PAGINAS / "painel_3_inferencia.py", title="Painel 3 · Inferência", url_path="Painel_3_·_Inferência"),
])
st.sidebar.caption(f"Quer explorar mais o jogo? O projeto [Tênis em números]"
                   f"({enderecos.APP_PROJETO or enderecos.SITE_PROJETO}) usa a mesma base e fica fora da avaliação.")
pagina.run()
