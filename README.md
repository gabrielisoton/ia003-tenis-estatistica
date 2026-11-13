# 🎾 Tênis ATP 2000–2025 · projeto e disciplinas

Um repositório, duas frentes que compartilham a mesma base de dados:

| | O que é | Links |
|---|---|---|
| [**Tênis em números**](projeto/) | Projeto público de analytics: o circuito, a elite × o resto, zebras e o perfil de cada jogador | [site](https://gabrielisoton.github.io/ia003-tenis-estatistica/projeto/) |
| [**IA003 · Probabilidade e Estatística para IA**](disciplinas/ia003-probabilidade-estatistica/) | Trabalho final da disciplina (UFRGS): população × amostra aleatória simples, IC e testes de hipóteses | [site](https://gabrielisoton.github.io/ia003-tenis-estatistica/) · [app](https://ia003-tenis-estatistica.streamlit.app) |

## Estrutura
```
nucleo/                         compartilhado por tudo (pacote Python `nucleo`)
  dados.py estatistica.py graficos.py analises.py secoes.py recarga.py exportacao.py enderecos.py
  base/                         população processada (parquet) e resumo; raw/ fica fora do git
  scripts/                      00 baixar dados · 01 preparar população · validar_estatistica
  web/                          estilo e JS comuns dos sites (copiados por ferramentas/montar_site.py)
projeto/                        "Tênis em números": app/, site/, scripts/
disciplinas/
  ia003-probabilidade-estatistica/   trabalho da IA003: app/, site/, amostra/, scripts/
ferramentas/montar_site.py      junta os sites em _site/ (preview local e GitHub Pages via Actions)
app/Home.py                     atalho temporário: mantém o link entregue do app da IA003 (ver abaixo)
```

## Como rodar
```bash
pip install -r requirements.txt
python nucleo/scripts/00_baixar_dados.py && python nucleo/scripts/01_preparar_populacao.py
python nucleo/scripts/validar_estatistica.py
streamlit run projeto/app/main.py                                     # app do projeto
streamlit run disciplinas/ia003-probabilidade-estatistica/app/main.py  # app da IA003
python ferramentas/montar_site.py && python -m http.server 8600 -d _site
```

## Adicionar uma nova disciplina
1. Criar `disciplinas/<código>-<nome>/` com `README.md`, e o que a disciplina pedir: `app/main.py` (copie o início do `main.py` da IA003: ele põe a raiz no `sys.path` e chama `nucleo.recarga.preparar()`), `notebooks/`, `scripts/`, `site/`.
2. Usar o que já existe em `nucleo/` (`dados.populacao()`, `analises.longo()`, `estatistica`, `graficos`) em vez de copiar.
3. Para publicar um site da disciplina: incluir a pasta em `LAYOUT` de `ferramentas/montar_site.py` e criar um `site/assets/site.js` com a navegação.
4. O que amadurecer e interessar ao público vai para `projeto/`; o que for útil a mais de um lugar vai para `nucleo/`.

> **Termos da base:** a TML permite uso pessoal, educacional e de pesquisa não comercial, com citação. Uso comercial, inclusive treinar modelos de previsão para serviços comerciais, exige autorização ([termos](https://stats.tennismylife.org/tennis-match-database#usage-terms)).

## Depois da nota da IA003 (pendente)
1. Renomear o repositório para `tenis-atp`.
2. Em `ferramentas/montar_site.py`, inverter o `LAYOUT` (projeto na raiz, IA003 em `disciplinas/ia003/`) e ajustar `nucleo/enderecos.py` e os `site.js`.
3. Criar um repositório-ponte `ia003-tenis-estatistica` com redirecionamentos para os endereços novos.
4. Reimplantar o app da IA003 no Streamlit Cloud com `disciplinas/ia003-probabilidade-estatistica/app/main.py` e apagar `app/Home.py`.

Dados: [TML-Database (Tennismylife)](https://github.com/Tennismylife/TML-Database), ATP 2000–2025, uso educacional com citação da fonte.
