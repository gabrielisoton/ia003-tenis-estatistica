"""ATALHO TEMPORÁRIO — mantém o link entregue do trabalho (https://ia003-tenis-estatistica.streamlit.app).

O app no Streamlit Cloud foi criado com o arquivo principal `app/Home.py`, e esse caminho não pode
ser trocado sem recriar o app. Este arquivo só executa o app real da disciplina.
Depois que a nota da IA003 sair: reimplantar o app com
`disciplinas/ia003-probabilidade-estatistica/app/main.py` e apagar esta pasta.
"""
import runpy
from pathlib import Path

runpy.run_path(str(Path(__file__).resolve().parents[1] / "disciplinas" / "ia003-probabilidade-estatistica"
                   / "app" / "main.py"), run_name="__main__")
