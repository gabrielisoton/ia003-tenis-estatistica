# Procedimento de seleção da amostra

- **Data do sorteio:** 12/11/2026
- **População:** 66.819 partidas (arquivo `nucleo/base/populacao.parquet`, uma linha por partida, com `id_partida` de 1 a N).
- **Tamanho da amostra:** n = 382. O cálculo está em `amostra/tamanho_amostral.json`, com confiança de 95%, margem de erro de 5% e p = 0.5. Sem correção finita, n₀ = 384.15; com a correção, n = 381.96.
- **Método:** amostragem aleatória simples **sem reposição**. Foi usado `pandas.DataFrame.sample(n=382, replace=False, random_state=15112026)`, que usa o gerador pseudoaleatório Mersenne Twister do NumPy.
- **Probabilidade de inclusão:** cada partida tem a mesma probabilidade de entrar na amostra, n/N = 382/66819 = 0.5717%.
- **Reprodutibilidade:** basta rodar `python disciplinas/ia003-probabilidade-estatistica/scripts/03_sortear_amostra.py` com a mesma população e a semente 15112026 para obter exatamente as mesmas 382 partidas.
- **Resultado:** `amostra/amostra.csv`, com 382 linhas e sem `id_partida` repetido.
