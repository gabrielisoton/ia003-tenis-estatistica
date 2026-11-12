"""Passo 2 — calcula o tamanho da amostra para estimar uma proporção.

Fórmula (população infinita):   n0 = z² · p(1−p) / E²
Correção para população finita: n  = n0 / (1 + (n0 − 1) / N)

Parâmetros e justificativa
- Confiança 95% (z = 1,96): padrão em pesquisas, equilibra precisão e custo.
- Margem de erro E = 5 p.p.: suficiente para distinguir proporções como 50% e 65%.
- p = 0,5: sem informação prévia, é o valor que MAXIMIZA p(1−p) = 0,25, ou seja,
  o cenário mais conservador (garante a margem para qualquer proporção estudada).
"""
import json
import math
from pathlib import Path

from scipy.stats import norm

BASE = Path(__file__).resolve().parents[1]
CONFIANCA = 0.95
MARGEM_ERRO = 0.05
P_PLANEJAMENTO = 0.5


def tamanho_amostral(N: int, confianca: float = CONFIANCA, e: float = MARGEM_ERRO,
                     p: float = P_PLANEJAMENTO) -> dict:
    z = norm.ppf(1 - (1 - confianca) / 2)
    n0 = z**2 * p * (1 - p) / e**2
    n_finito = n0 / (1 + (n0 - 1) / N)
    return {
        "N": N, "confianca": confianca, "z": round(z, 4), "margem_erro": e, "p": p,
        "n0_pop_infinita": round(n0, 2), "n_corrigido": round(n_finito, 2),
        "n": math.ceil(n_finito),
    }


def main() -> None:
    resumo = json.loads((BASE / "dados" / "resumo_populacao.json").read_text(encoding="utf-8"))
    calc = tamanho_amostral(resumo["N"])
    (BASE / "amostra").mkdir(exist_ok=True)
    (BASE / "amostra" / "tamanho_amostral.json").write_text(json.dumps(calc, indent=2), encoding="utf-8")
    print(json.dumps(calc, indent=2))


if __name__ == "__main__":
    main()
