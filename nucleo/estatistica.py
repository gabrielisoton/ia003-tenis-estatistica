"""Funções de inferência escritas com a fórmula explícita (para aprender o que
cada biblioteca faz por baixo). Todas são validadas contra o scipy em
scripts/04_validar_estatistica.py.

Convenções
- alternativa: "bilateral" (≠), "maior" (>) ou "menor" (<).
- Os ICs são sempre bilaterais, no nível `confianca`.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
from scipy.stats import norm, t

ALTERNATIVAS = {"bilateral": "≠", "maior": ">", "menor": "<"}


def _valor_p(estatistica: float, alternativa: str, cdf, sf) -> float:
    if alternativa == "maior":
        return float(sf(estatistica))
    if alternativa == "menor":
        return float(cdf(estatistica))
    return float(2 * sf(abs(estatistica)))


@dataclass
class Resultado:
    tipo: str              # "proporção" ou "média"
    n: int
    estimativa: float      # p̂ ou x̄
    erro_padrao_ic: float  # EP usado no IC
    critico: float         # z ou t crítico do IC
    ic_inf: float
    ic_sup: float
    valor_h0: float
    alternativa: str
    estatistica: float     # z ou t observado
    gl: int | None         # graus de liberdade (só no t)
    valor_p: float
    alfa: float
    rejeita_h0: bool
    condicoes: dict

    def dict(self) -> dict:
        return asdict(self)


# ---------------------------------------------------------------- proporção
def ic_proporcao(sucessos: int, n: int, confianca: float = 0.95) -> tuple[float, float, float, float]:
    """IC de Wald: p̂ ± z·√(p̂(1−p̂)/n). Retorna (p̂, EP, li, ls)."""
    p_hat = sucessos / n
    ep = np.sqrt(p_hat * (1 - p_hat) / n)
    z = norm.ppf(1 - (1 - confianca) / 2)
    return p_hat, ep, p_hat - z * ep, p_hat + z * ep


def ic_wilson(sucessos, n, confianca: float = 0.95):
    """IC de Wilson (escore) para uma proporção. Retorna (p̂, li, ls).

    Centro = (p̂ + z²/2n) / (1 + z²/n);  meia-largura = z/(1 + z²/n) · √(p̂(1−p̂)/n + z²/4n²).
    Ao contrário do IC de Wald, nunca sai de [0, 1] e não colapsa para largura zero quando
    p̂ = 0 ou p̂ = 1 — por isso é o indicado para n pequeno ou proporções extremas.
    Aceita números ou arrays (calcula elemento a elemento); n = 0 devolve NaN.
    """
    s = np.asarray(sucessos, dtype=float)
    n = np.asarray(n, dtype=float)
    z = norm.ppf(1 - (1 - confianca) / 2)
    with np.errstate(divide="ignore", invalid="ignore"):
        p_hat = s / n
        den = 1 + z**2 / n
        centro = (p_hat + z**2 / (2 * n)) / den
        meia = z / den * np.sqrt(p_hat * (1 - p_hat) / n + z**2 / (4 * n**2))
    li, ls = centro - meia, centro + meia
    if p_hat.ndim == 0:
        return float(p_hat), float(li), float(ls)
    return p_hat, li, ls


def teste_z_proporcao(sucessos: int, n: int, p0: float, alternativa: str = "bilateral",
                      alfa: float = 0.05, confianca: float = 0.95) -> Resultado:
    """Teste z para uma proporção: z = (p̂ − p0) / √(p0(1−p0)/n).

    No teste o erro-padrão usa p0 (vale sob H0); no IC usa p̂.
    """
    p_hat, ep_ic, li, ls = ic_proporcao(sucessos, n, confianca)
    ep_h0 = np.sqrt(p0 * (1 - p0) / n)
    z_obs = (p_hat - p0) / ep_h0
    vp = _valor_p(z_obs, alternativa, norm.cdf, norm.sf)
    condicoes = {
        "n·p0 ≥ 10": (n * p0, n * p0 >= 10),
        "n·(1−p0) ≥ 10": (n * (1 - p0), n * (1 - p0) >= 10),
        "n·p̂ ≥ 10 (IC)": (sucessos, sucessos >= 10),
        "n·(1−p̂) ≥ 10 (IC)": (n - sucessos, n - sucessos >= 10),
    }
    return Resultado("proporção", n, p_hat, ep_ic, norm.ppf(1 - (1 - confianca) / 2), li, ls,
                     p0, alternativa, float(z_obs), None, vp, alfa, vp < alfa, condicoes)


# -------------------------------------------------------------------- média
def ic_media_t(valores, confianca: float = 0.95) -> tuple[float, float, float, float, float, int]:
    """IC t: x̄ ± t(n−1)·s/√n. Retorna (x̄, s, EP, li, ls, gl)."""
    x = np.asarray(valores, dtype=float)
    x = x[~np.isnan(x)]
    n = x.size
    media, s = x.mean(), x.std(ddof=1)
    ep = s / np.sqrt(n)
    tc = t.ppf(1 - (1 - confianca) / 2, df=n - 1)
    return media, s, ep, media - tc * ep, media + tc * ep, n - 1


def teste_t_media(valores, mu0: float, alternativa: str = "bilateral",
                  alfa: float = 0.05, confianca: float = 0.95) -> Resultado:
    """Teste t para uma média: t = (x̄ − μ0) / (s/√n), com n−1 graus de liberdade."""
    x = np.asarray(valores, dtype=float)
    x = x[~np.isnan(x)]
    media, s, ep, li, ls, gl = ic_media_t(x, confianca)
    t_obs = (media - mu0) / ep
    vp = _valor_p(t_obs, alternativa, lambda v: t.cdf(v, gl), lambda v: t.sf(v, gl))
    assimetria = float(((x - media) ** 3).mean() / x.std(ddof=0) ** 3)
    condicoes = {
        "Amostra aleatória (AAS)": ("sim", True),
        "n ≥ 30 (TCL)": (x.size, x.size >= 30),
        "Assimetria da amostra": (round(assimetria, 2), abs(assimetria) < 2 or x.size >= 100),
    }
    return Resultado("média", int(x.size), float(media), float(ep),
                     float(t.ppf(1 - (1 - confianca) / 2, gl)), float(li), float(ls),
                     mu0, alternativa, float(t_obs), gl, vp, alfa, vp < alfa, condicoes)


def teste_welch(a, b, alternativa: str = "bilateral", alfa: float = 0.05,
                confianca: float = 0.95) -> dict:
    """Diferença de médias (a − b) sem supor variâncias iguais (Welch)."""
    a = np.asarray(a, float); a = a[~np.isnan(a)]
    b = np.asarray(b, float); b = b[~np.isnan(b)]
    va, vb = a.var(ddof=1) / a.size, b.var(ddof=1) / b.size
    ep = np.sqrt(va + vb)
    gl = (va + vb) ** 2 / (va**2 / (a.size - 1) + vb**2 / (b.size - 1))
    dif = a.mean() - b.mean()
    t_obs = dif / ep
    vp = _valor_p(t_obs, alternativa, lambda v: t.cdf(v, gl), lambda v: t.sf(v, gl))
    tc = t.ppf(1 - (1 - confianca) / 2, gl)
    return {"n_a": a.size, "n_b": b.size, "media_a": a.mean(), "media_b": b.mean(),
            "diferenca": dif, "ic_inf": dif - tc * ep, "ic_sup": dif + tc * ep,
            "estatistica": t_obs, "gl": gl, "valor_p": vp, "rejeita_h0": vp < alfa}


def teste_duas_proporcoes(s1: int, n1: int, s2: int, n2: int, alternativa: str = "bilateral",
                          alfa: float = 0.05, confianca: float = 0.95) -> dict:
    """Diferença de proporções (p1 − p2).

    Teste: z com proporção combinada (vale sob H0: p1 = p2).
    IC: p̂1 − p̂2 ± z·√(p̂1(1−p̂1)/n1 + p̂2(1−p̂2)/n2).
    """
    p1, p2 = s1 / n1, s2 / n2
    pc = (s1 + s2) / (n1 + n2)
    ep_h0 = np.sqrt(pc * (1 - pc) * (1 / n1 + 1 / n2))
    z_obs = (p1 - p2) / ep_h0
    vp = _valor_p(z_obs, alternativa, norm.cdf, norm.sf)
    ep_ic = np.sqrt(p1 * (1 - p1) / n1 + p2 * (1 - p2) / n2)
    zc = norm.ppf(1 - (1 - confianca) / 2)
    return {"n1": n1, "n2": n2, "p1": p1, "p2": p2, "diferenca": p1 - p2,
            "ic_inf": p1 - p2 - zc * ep_ic, "ic_sup": p1 - p2 + zc * ep_ic,
            "estatistica": float(z_obs), "valor_p": vp, "rejeita_h0": vp < alfa,
            "condicoes_ok": min(s1, n1 - s1, s2, n2 - s2) >= 5}


# -------------------------------------------------------------------- poder
def _poder(valor_verdadeiro, valor_h0, ep_h0, ep_real, alternativa, alfa):
    """P(rejeitar H0) quando o parâmetro real é `valor_verdadeiro` (aprox. normal)."""
    if alternativa == "maior":
        c = valor_h0 + norm.ppf(1 - alfa) * ep_h0
        return float(norm.sf((c - valor_verdadeiro) / ep_real))
    if alternativa == "menor":
        c = valor_h0 - norm.ppf(1 - alfa) * ep_h0
        return float(norm.cdf((c - valor_verdadeiro) / ep_real))
    z = norm.ppf(1 - alfa / 2)
    return float(norm.sf((valor_h0 + z * ep_h0 - valor_verdadeiro) / ep_real)
                 + norm.cdf((valor_h0 - z * ep_h0 - valor_verdadeiro) / ep_real))


def poder_proporcao(p_real: float, p0: float, n: int, alternativa: str, alfa: float = 0.05) -> float:
    return _poder(p_real, p0, np.sqrt(p0 * (1 - p0) / n), np.sqrt(p_real * (1 - p_real) / n),
                  alternativa, alfa)


def poder_media(mu_real: float, mu0: float, sigma: float, n: int, alternativa: str,
                alfa: float = 0.05) -> float:
    ep = sigma / np.sqrt(n)
    return _poder(mu_real, mu0, ep, ep, alternativa, alfa)


# ------------------------------------------------------------- simulação
def cobertura_ic(populacao, n: int, repeticoes: int = 100, tipo: str = "média",
                 confianca: float = 0.95, semente: int = 0) -> list[tuple[float, float, float]]:
    """Sorteia `repeticoes` AAS de tamanho n e devolve (estimativa, li, ls) de cada uma.

    Para tipo="proporção", `populacao` deve ser 0/1.
    """
    rng = np.random.default_rng(semente)
    pop = np.asarray(populacao, dtype=float)
    pop = pop[~np.isnan(pop)]
    saida = []
    for _ in range(repeticoes):
        am = rng.choice(pop, size=n, replace=False)
        if tipo == "proporção":
            est, _, li, ls = ic_proporcao(int(am.sum()), n, confianca)
        else:
            est, _, _, li, ls, _ = ic_media_t(am, confianca)
        saida.append((float(est), float(li), float(ls)))
    return saida
