"""Monta o site publicado juntando os sites do repositório e os arquivos web compartilhados.

    python ferramentas/montar_site.py            → _site/ (preview local: python -m http.server 8600 -d _site)
    python ferramentas/montar_site.py --saida X  → outra pasta

O GitHub Actions (.github/workflows/pages.yml) roda este script e publica _site/ no GitHub Pages.

LAYOUT diz onde cada site fica no endereço publicado. Até a nota da IA003 sair, o trabalho fica na
raiz (links entregues) e o projeto em /projeto/. Depois de renomear o repositório, inverter:
    {"projeto/site": "", "disciplinas/ia003-probabilidade-estatistica/site": "disciplinas/ia003"}
(e ajustar os links relativos nos site.js e em nucleo/enderecos.py).
"""
from __future__ import annotations

import argparse
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
WEB_COMPARTILHADO = RAIZ / "nucleo" / "web"
LAYOUT = {
    "disciplinas/ia003-probabilidade-estatistica/site": "",
    "projeto/site": "projeto",
}
# endereços antigos → novos (para links já compartilhados continuarem funcionando)
REDIRECIONAR = {
    "explorar.html": "projeto/explorar.html",
    "jogadores.html": "projeto/jogadores.html",
}
MODELO_REDIRECT = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Página movida</title>
<meta http-equiv="refresh" content="0; url={destino}"><link rel="canonical" href="{destino}"></head>
<body><p>Esta página mudou de endereço: <a href="{destino}">{destino}</a>.</p></body></html>
"""


def montar(saida: Path) -> None:
    if saida.exists():
        shutil.rmtree(saida)
    saida.mkdir(parents=True)
    for origem, destino in LAYOUT.items():
        alvo = saida / destino if destino else saida
        shutil.copytree(RAIZ / origem, alvo, dirs_exist_ok=True)
        for arquivo in WEB_COMPARTILHADO.iterdir():
            if (alvo / "assets" / arquivo.name).exists():
                raise SystemExit(f"Conflito: {origem}/assets/{arquivo.name} também existe em nucleo/web/")
            shutil.copy2(arquivo, alvo / "assets" / arquivo.name)
    for antigo, novo in REDIRECIONAR.items():
        caminho = saida / antigo
        if caminho.exists():
            raise SystemExit(f"Conflito: {antigo} existe e também seria um redirecionamento")
        caminho.write_text(MODELO_REDIRECT.format(destino=novo), encoding="utf-8")
    (saida / ".nojekyll").write_text("", encoding="utf-8")
    arquivos = [p for p in saida.rglob("*") if p.is_file()]
    print(f"site montado em {saida} ({len(arquivos)} arquivos)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--saida", type=Path, default=RAIZ / "_site")
    montar(ap.parse_args().saida.resolve())
