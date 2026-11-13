"""App Streamlit do projeto público "Tênis em números".

Rodar localmente (da raiz do repositório):
    streamlit run projeto/app/main.py
No Streamlit Cloud: arquivo principal `projeto/app/main.py`.
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
if str(RAIZ) not in sys.path:  # torna o pacote `nucleo` importável
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from nucleo import recarga  # noqa: E402

recarga.preparar()
st.set_page_config(page_title="Tênis em números", page_icon="🎾", layout="wide")

PAGINAS = AQUI / "paginas"
pagina = st.navigation([
    st.Page(PAGINAS / "inicio.py", title="Início", icon="🎾", default=True),
    st.Page(PAGINAS / "circuito.py", title="O circuito", icon="📊", url_path="circuito"),
    st.Page(PAGINAS / "explorar.py", title="Explorar", icon="🏆", url_path="explorar"),
    st.Page(PAGINAS / "jogadores.py", title="Jogadores", icon="🎾", url_path="jogadores"),
])
pagina.run()
