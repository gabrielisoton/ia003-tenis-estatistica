# 🎾 Tênis em números — o circuito ATP de 2000 a 2025

Projeto pessoal de analytics de tênis: todas as **66.819 partidas** do circuito principal da ATP entre 2000 e 2025, com saque, devolução, break points, tie-breaks e títulos de cada jogador.

- **Site:** https://gabrielisoton.github.io/ia003-tenis-estatistica/projeto/
- **App (Streamlit):** _a criar_ (arquivo principal `projeto/app/main.py`)

## Páginas
| Página | O que mostra |
|---|---|
| Início | A base, a população (o que entra e o que fica de fora), o que tem em cada partida, termos de uso |
| O circuito | Descritiva da população inteira, com filtros: superfícies, duração, aces, ranking |
| Explorar | Top N × demais, ranking × zebras (chance de o favorito vencer), linha do tempo 2000–2025 |
| Jogadores | Líderes de todos os critérios (pódio e quadro de medalhas), ranking por critério com IC 95% de Wilson e perfil completo de cada jogador |

## Como rodar (da raiz do repositório)
```bash
pip install -r requirements.txt
streamlit run projeto/app/main.py                 # app
python projeto/scripts/exportar_site.py           # gera projeto/site/data/*.json
python ferramentas/montar_site.py                 # monta _site/ com os dois sites
python -m http.server 8600 -d _site               # abre em http://localhost:8600/projeto/
```

## Estrutura
```
app/main.py      app Streamlit (st.navigation)
app/paginas/     Início, O circuito, Explorar, Jogadores
scripts/         exportar_site.py (JSON do site)
site/            index, circuito, explorar, jogadores + assets/ (jogadores.js, site.js) + data/
```
Os cálculos ficam em [`nucleo/analises.py`](../nucleo/analises.py) (critérios, líderes, perfis) e são reaproveitados pelas disciplinas.

## Origem
Nasceu do trabalho final da IA003 · Probabilidade e Estatística para IA (Especialização em IA, UFRGS), em [`disciplinas/ia003-probabilidade-estatistica/`](../disciplinas/ia003-probabilidade-estatistica/).

**Dados:** [TML-Database (Tennismylife)](https://github.com/Tennismylife/TML-Database). Uso pessoal, educacional e de pesquisa não comercial, com citação da fonte; uso comercial (inclusive treinar modelos de previsão para serviços comerciais) exige autorização ([termos](https://stats.tennismylife.org/tennis-match-database#usage-terms)).
