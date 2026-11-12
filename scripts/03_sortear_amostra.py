"""Passo 3 — sorteia a Amostra Aleatória Simples (AAS) sem reposição.

Cada uma das N partidas da população tem a mesma probabilidade n/N de entrar
na amostra. A semente fixa torna o sorteio reproduzível: quem rodar este script
com a mesma população obtém exatamente as mesmas partidas.
"""
import json
from datetime import date
from pathlib import Path

import pandas as pd

BASE = Path(__file__).resolve().parents[1]
SEMENTE = 15112026  # data de entrega do trabalho (15/11/2026)


def main() -> None:
    pop = pd.read_parquet(BASE / "dados" / "populacao.parquet")
    calc = json.loads((BASE / "amostra" / "tamanho_amostral.json").read_text(encoding="utf-8"))
    n, N = calc["n"], len(pop)

    amostra = pop.sample(n=n, replace=False, random_state=SEMENTE).sort_values("id_partida")
    assert amostra["id_partida"].is_unique and len(amostra) == n
    amostra.to_csv(BASE / "amostra" / "amostra.csv", index=False, encoding="utf-8")

    N_fmt = f"{N:_}".replace("_", ".")
    doc = f"""# Procedimento de seleção da amostra

- **Data do sorteio:** {date.today():%d/%m/%Y}
- **População:** {N_fmt} partidas (arquivo `dados/populacao.parquet`, uma linha por partida, com `id_partida` de 1 a N).
- **Tamanho da amostra:** n = {n}. O cálculo está em `amostra/tamanho_amostral.json`, com confiança de {calc['confianca']:.0%}, margem de erro de {calc['margem_erro']:.0%} e p = {calc['p']}. Sem correção finita, n₀ = {calc['n0_pop_infinita']}; com a correção, n = {calc['n_corrigido']}.
- **Método:** amostragem aleatória simples **sem reposição**. Foi usado `pandas.DataFrame.sample(n={n}, replace=False, random_state={SEMENTE})`, que usa o gerador pseudoaleatório Mersenne Twister do NumPy.
- **Probabilidade de inclusão:** cada partida tem a mesma probabilidade de entrar na amostra, n/N = {n}/{N} = {n / N:.4%}.
- **Reprodutibilidade:** basta rodar `python scripts/03_sortear_amostra.py` com a mesma população e a semente {SEMENTE} para obter exatamente as mesmas {n} partidas.
- **Resultado:** `amostra/amostra.csv`, com {n} linhas e sem `id_partida` repetido.
"""
    (BASE / "amostra" / "sorteio.md").write_text(doc, encoding="utf-8")
    print(f"AAS: {len(amostra)} de {N} partidas (semente {SEMENTE})")
    print(amostra[["id_partida", "ano", "torneio", "vencedor", "perdedor", "placar"]].head(8).to_string(index=False))


if __name__ == "__main__":
    main()
