"""App Streamlit do projeto público "Tênis em números".

Rodar localmente (da raiz do repositório):
    streamlit run projeto/app/main.py
No Streamlit Cloud: arquivo principal `projeto/app/main.py`.

Bilíngue (português/inglês): o seletor da barra lateral guarda a escolha em `st.session_state["lingua"]`
e na URL (`?lang=en`); os textos usam `T(pt, en)` e `tr(rótulo)` de `nucleo/idiomas.py`.
"""
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
RAIZ = AQUI.parents[1]
if str(RAIZ) not in sys.path:  # torna o pacote `nucleo` importável
    sys.path.insert(0, str(RAIZ))

import streamlit as st  # noqa: E402

from nucleo import idiomas, recarga  # noqa: E402
from nucleo.idiomas import T  # noqa: E402

recarga.preparar()
st.set_page_config(page_title="Tênis em números", page_icon="🎾", layout="wide")
idiomas.seletor()
if idiomas.ingles():
    st.set_page_config(page_title="Tennis by numbers")

PAGINAS = AQUI / "paginas"
pagina = st.navigation([
    st.Page(PAGINAS / "inicio.py", title=T("Início", "Home"), icon="🎾", default=True),
    st.Page(PAGINAS / "circuito.py", title=T("O circuito", "The tour"), icon="📊", url_path="circuito"),
    st.Page(PAGINAS / "explorar.py", title=T("Explorar", "Explore"), icon="🏆", url_path="explorar"),
    st.Page(PAGINAS / "jogadores.py", title=T("Jogadores", "Players"), icon="🎾", url_path="jogadores"),
])
pagina.run()
