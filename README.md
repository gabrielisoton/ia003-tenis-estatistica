# 🎾 Quem vence no tênis? Inferência estatística no circuito ATP (2000–2025)

Atividade avaliativa final da disciplina **IA003 — Probabilidade e Estatística para IA** (Especialização em IA, UFRGS).

O projeto compara **toda a população** de partidas do circuito principal da ATP (N = 66.819) com uma **amostra aleatória simples** de n = 382 partidas. Os parâmetros populacionais são calculados diretamente; os intervalos de confiança e os testes de hipóteses usam **somente a amostra**.

## Links de entrega
**Site (HTML, GitHub Pages)**
- Base e amostragem: https://gabrielisoton.github.io/ia003-tenis-estatistica/
- Painel 1 · População: https://gabrielisoton.github.io/ia003-tenis-estatistica/populacao.html
- Painel 2 · Amostra: https://gabrielisoton.github.io/ia003-tenis-estatistica/amostra.html
- Painel 3 · Inferência: https://gabrielisoton.github.io/ia003-tenis-estatistica/inferencia.html

**Extras (fora da avaliação):** [Explorar](https://gabrielisoton.github.io/ia003-tenis-estatistica/explorar.html) (Top N × demais, ranking × zebras, linha do tempo) e [Jogadores](https://gabrielisoton.github.io/ia003-tenis-estatistica/jogadores.html) (ranking por critério e perfil de cada jogador).

**App (Streamlit Community Cloud):** https://ia003-tenis-estatistica.streamlit.app. Os painéis 1–3 ficam no menu lateral, e as páginas "Extra" (Explorar e Jogadores) estão fora da avaliação.

- **Vídeo (YouTube):** _a preencher_
- **Base original:** [TML-Database (Tennismylife)](https://github.com/Tennismylife/TML-Database). O esquema de colunas é o mesmo da base *tennis_atp* de Jeff Sackmann (Tennis Abstract), que foi removida do GitHub em 2026.

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

## Como reproduzir
```bash
pip install -r requirements.txt
python scripts/00_baixar_dados.py          # baixa os CSVs 2000–2025 da TML
python scripts/01_preparar_populacao.py    # gera dados/populacao.parquet
python scripts/02_tamanho_amostral.py      # n = 382
python scripts/03_sortear_amostra.py       # AAS com semente 15112026
python scripts/04_validar_estatistica.py   # confere as fórmulas contra o scipy
streamlit run app/Home.py
```

## Estrutura
```
app/                 aplicativo Streamlit (Home + pages/)
  estatistica.py     IC e testes escritos com a fórmula explícita
  graficos.py        painel descritivo compartilhado pelos Painéis 1 e 2
dados/               população processada (parquet) e resumo
amostra/             amostra sorteada, cálculo de n e procedimento do sorteio
scripts/             pipeline reprodutível 00 → 05 (05 exporta os resultados em JSON para o site)
docs/                site HTML estático (GitHub Pages), que lê docs/data/*.json
```

Dados: TML-Database (Tennismylife), uso educacional, com citação da fonte.
