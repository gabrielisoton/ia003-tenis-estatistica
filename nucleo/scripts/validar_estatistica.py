"""Valida nucleo/estatistica.py contra o scipy e contra contas feitas à mão."""
import sys
from pathlib import Path

import numpy as np
from scipy import stats

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # raiz do repositório
from nucleo import estatistica as est  # noqa: E402

rng = np.random.default_rng(42)
TOL = 1e-9
falhas = 0


def confere(nome, a, b):
    global falhas
    ok = abs(a - b) < TOL
    falhas += not ok
    print(f"[{'OK ' if ok else 'ERRO'}] {nome}: {a:.12f} vs {b:.12f}")


# Teste t de uma média, nas três alternativas
x = rng.gamma(2.0, 50.0, size=382)  # dados assimétricos, como a duração das partidas
for alt, alt_sp in [("bilateral", "two-sided"), ("maior", "greater"), ("menor", "less")]:
    r = est.teste_t_media(x, 100, alt)
    ref = stats.ttest_1samp(x, 100, alternative=alt_sp)
    confere(f"t ({alt}) estatística", r.estatistica, ref.statistic)
    confere(f"t ({alt}) valor-p", r.valor_p, ref.pvalue)
ci = stats.ttest_1samp(x, 100).confidence_interval(0.95)
r = est.teste_t_media(x, 100)
confere("IC t inferior", r.ic_inf, ci.low)
confere("IC t superior", r.ic_sup, ci.high)

# Teste z de proporção, conferido à mão
s, n, p0 = 265, 382, 0.5
r = est.teste_z_proporcao(s, n, p0, "maior")
z_mao = (s / n - p0) / np.sqrt(p0 * (1 - p0) / n)
confere("z proporção", r.estatistica, z_mao)
confere("valor-p z (maior)", r.valor_p, stats.norm.sf(z_mao))
ph = s / n
confere("IC prop inferior", r.ic_inf, ph - 1.959963984540054 * np.sqrt(ph * (1 - ph) / n))
print(f"  (referência: valor-p do teste binomial exato = {stats.binomtest(s, n, p0, 'greater').pvalue:.3e})")

# IC de Wilson, inclusive nos extremos (0 e n sucessos) e com n pequeno
for s, n, conf in [(265, 382, 0.95), (0, 20, 0.95), (20, 20, 0.95), (3, 7, 0.90), (812, 1001, 0.99)]:
    _, li, ls = est.ic_wilson(s, n, conf)
    ref = stats.binomtest(s, n).proportion_ci(confidence_level=conf, method="wilson")
    confere(f"Wilson {s}/{n} ({conf:.0%}) inferior", li, ref.low)
    confere(f"Wilson {s}/{n} ({conf:.0%}) superior", ls, ref.high)
_, li_v, ls_v = est.ic_wilson(np.array([265, 0, 20]), np.array([382, 20, 20]))
confere("Wilson vetorizado = escalar", li_v[0], est.ic_wilson(265, 382)[1])

# Welch
a, b = rng.normal(17, 9, 30), rng.normal(8, 5, 130)
w = est.teste_welch(a, b)
ref = stats.ttest_ind(a, b, equal_var=False)
confere("Welch estatística", w["estatistica"], ref.statistic)
confere("Welch valor-p", w["valor_p"], ref.pvalue)

# Duas proporções: z² deve ser igual ao qui-quadrado sem correção de continuidade
d = est.teste_duas_proporcoes(52, 72, 196, 310)
chi2, p_chi, _, _ = stats.chi2_contingency([[52, 20], [196, 114]], correction=False)
confere("duas proporções z² = qui²", d["estatistica"] ** 2, chi2)
confere("duas proporções valor-p bilateral", d["valor_p"], p_chi)

# Cobertura dos ICs: deve ficar perto de 95%
pop = rng.gamma(2.0, 50.0, size=60000)
cob = est.cobertura_ic(pop, 382, repeticoes=2000, semente=1)
taxa = np.mean([li <= pop.mean() <= ls for _, li, ls in cob])
print(f"[{'OK ' if 0.93 < taxa < 0.97 else 'ERRO'}] cobertura simulada do IC 95%: {taxa:.3f}")
falhas += not (0.93 < taxa < 0.97)

print("\nTUDO OK" if falhas == 0 else f"\n{falhas} FALHA(S)")
sys.exit(falhas > 0)
