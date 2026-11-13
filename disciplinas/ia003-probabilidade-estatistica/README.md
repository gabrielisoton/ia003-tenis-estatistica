# 🎾 Quem vence no tênis? Inferência estatística no circuito ATP (2000–2025)

Atividade avaliativa final da disciplina **IA003 — Probabilidade e Estatística para IA** (Especialização em IA, UFRGS).

O trabalho compara **toda a população** de partidas do circuito principal da ATP (N = 66.819) com uma **amostra aleatória simples** de n = 382 partidas. Os parâmetros populacionais são calculados diretamente; os intervalos de confiança e os testes de hipóteses usam **somente a amostra**.

## Links de entrega
**Site (HTML, GitHub Pages)**
- Base e amostragem: https://gabrielisoton.github.io/ia003-tenis-estatistica/
- Painel 1 · População: https://gabrielisoton.github.io/ia003-tenis-estatistica/populacao.html
- Painel 2 · Amostra: https://gabrielisoton.github.io/ia003-tenis-estatistica/amostra.html
- Painel 3 · Inferência: https://gabrielisoton.github.io/ia003-tenis-estatistica/inferencia.html

**App (Streamlit Community Cloud):** https://ia003-tenis-estatistica.streamlit.app. Os painéis 1–3 ficam no menu lateral.

- **Vídeo (YouTube):** _a preencher_
- **Base original:** [TML-Database (Tennismylife)](https://github.com/Tennismylife/TML-Database). O esquema de colunas é o mesmo da base *tennis_atp* de Jeff Sackmann (Tennis Abstract), que foi removida do GitHub em 2026.

> Fora da avaliação: este trabalho deu origem ao projeto público **Tênis em números** (pasta [`projeto/`](../../projeto/)), que usa a mesma base para explorar o jogo.

## Painéis
| Página | Conteúdo |
|---|---|
| Home | Base, população, unidade amostral, variáveis, cálculo do tamanho amostral e sorteio |
| Painel 1 · População | KPIs, distribuições, frequências e medidas descritivas (com filtros) |
| Painel 2 · Amostra | A mesma análise só com a amostra, com sobreposição e tabelas população × amostra |
| Painel 3 · Inferência | 2 hipóteses de proporção e 2 de média: IC, estatística, valor-p, condições, comparação com o parâmetro real, poder do teste, simulação de 100 ICs, bônus de Welch e limitações |

## Hipóteses (α = 5%, IC 95%)
| | Pergunta | H₀ | Teste |
|---|---|---|---|
| P1 | O jogador de melhor ranking vence mais da metade das partidas? | p = 0,5 (H₁: p > 0,5) | z para uma proporção |
| P2 | Uma em cada três partidas vai ao set decisivo? | p = 1/3 (H₁: p ≠ 1/3) | z para uma proporção |
| M1 | Uma partida melhor de 3 dura, em média, 100 minutos? | μ = 100 (H₁: μ ≠ 100) | t para uma média |
| M2 | Uma partida tem, em média, 10 aces? | μ = 10 (H₁: μ ≠ 10) | t para uma média |

## Como reproduzir (da raiz do repositório)
```bash
pip install -r requirements.txt
python nucleo/scripts/00_baixar_dados.py                                   # CSVs 2000–2025 da TML
python nucleo/scripts/01_preparar_populacao.py                             # nucleo/base/populacao.parquet
python disciplinas/ia003-probabilidade-estatistica/scripts/02_tamanho_amostral.py   # n = 382
python disciplinas/ia003-probabilidade-estatistica/scripts/03_sortear_amostra.py    # AAS com semente 15112026
python nucleo/scripts/validar_estatistica.py                               # confere as fórmulas contra o scipy
python disciplinas/ia003-probabilidade-estatistica/scripts/exportar_site.py         # JSON do site
streamlit run disciplinas/ia003-probabilidade-estatistica/app/main.py
```

## Estrutura desta pasta
```
app/main.py          app Streamlit (st.navigation): Home + Painéis 1–3
app/paginas/         as páginas
app/hipoteses.py     definição única das 4 hipóteses (app e site)
app/dados_amostra.py leitura da amostra e do cálculo do tamanho amostral
amostra/             amostra sorteada, cálculo de n e procedimento do sorteio
scripts/             02 tamanho amostral, 03 sorteio, exportar_site (JSON do site)
site/                site HTML (index, populacao, amostra, inferencia) + data/*.json
```
O que é compartilhado com o projeto (base, população, `estatistica.py`, `graficos.py`, estilo do site) fica em [`nucleo/`](../../nucleo/).

Dados: TML-Database (Tennismylife), uso educacional, com citação da fonte.
