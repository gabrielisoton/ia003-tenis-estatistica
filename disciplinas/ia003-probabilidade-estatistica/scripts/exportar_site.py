"""Exporta em JSON tudo o que o site do trabalho da IA003 exibe (disciplinas/ia003-…/site/data/).

O Python é o "motor" estatístico (funções validadas em nucleo/scripts/validar_estatistica.py).
O site só lê estes arquivos.

Saídas:
- meta.json        base, população, tamanho amostral e sorteio
- populacao.json   colunas compactas da população (para filtros no navegador)
- amostra.json     as 382 partidas sorteadas (mesmas colunas + nomes e placar)
- inferencia.json  as 4 hipóteses e os testes bônus
"""
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm, t as tdist

AQUI = Path(__file__).resolve().parents[1]           # pasta da disciplina
RAIZ = AQUI.parents[1]
sys.path.insert(0, str(RAIZ))
sys.path.insert(0, str(AQUI / "app"))
import hipoteses as hp  # noqa: E402
import pandas as pd  # noqa: E402
from nucleo import estatistica as est  # noqa: E402
from nucleo import exportacao as ex  # noqa: E402

SAIDA = AQUI / "site" / "data"
ALFAS = [0.01, 0.05, 0.10]
CONF = 0.95


# ------------------------------------------------------------------ inferência
def inferencia(pop: pd.DataFrame, am: pd.DataFrame) -> dict:
    saida = []
    for h in hp.HIPOTESES:
        r = hp.rodar(h, am, 0.05, CONF)
        param, sigma, N_sub = hp.parametro(h, pop)
        por_alfa = {}
        for a in ALFAS:
            pw = hp.poder(h, param, sigma, r.n, a)
            por_alfa[str(a)] = {"rejeita": r.valor_p < a, "poder": pw}
        critico_sim = (norm.ppf(1 - (1 - CONF) / 2) if h["tipo"] == "proporção"
                       else tdist.ppf(1 - (1 - CONF) / 2, r.n - 1))
        saida.append({
            **{k: h[k] for k in ("id", "aba", "tipo", "var", "filtro", "h0", "alt", "parametro_nome",
                                 "pergunta", "justificativa", "unidade")},
            "n": r.n, "estimativa": r.estimativa, "ep": r.erro_padrao_ic, "critico": r.critico,
            "ic_inf": r.ic_inf, "ic_sup": r.ic_sup, "estatistica": r.estatistica, "gl": r.gl,
            "valor_p": r.valor_p,
            "desvio_amostral": None if h["tipo"] == "proporção" else float(np.std(hp.valores(h, am), ddof=1)),
            "condicoes": [{"condicao": k, "valor": v[0], "ok": v[1]} for k, v in r.condicoes.items()],
            "parametro": param, "sigma_pop": sigma, "N_sub": N_sub,
            "contem": r.ic_inf <= param <= r.ic_sup, "erro_amostral": r.estimativa - param,
            "h0_falsa": hp.h0_falsa(h, param), "por_alfa": por_alfa, "critico_simulacao": critico_sim,
        })
    return {"confianca": CONF, "alfas": ALFAS, "hipoteses": saida, "bonus": bonus(pop, am)}


def bonus(pop: pd.DataFrame, am: pd.DataFrame) -> dict:
    # 1) O favorito vence mais em melhor de 5 do que em melhor de 3?
    def fav(df, bo):
        x = df.loc[(df["melhor_de"] == bo) & df["favorito_venceu"].notna(), "favorito_venceu"]
        return int((x == "Sim").sum()), len(x)
    s5, n5 = fav(am, "Melhor de 5")
    s3, n3 = fav(am, "Melhor de 3")
    formato = est.teste_duas_proporcoes(s5, n5, s3, n3, "maior")
    ps5, pn5 = fav(pop, "Melhor de 5")
    ps3, pn3 = fav(pop, "Melhor de 3")
    formato.update({"pop_p1": ps5 / pn5, "pop_p2": ps3 / pn3, "pop_diferenca": ps5 / pn5 - ps3 / pn3,
                    "rotulo1": "Melhor de 5", "rotulo2": "Melhor de 3"})

    # 2) Aces por superfície: IC de cada uma + comparações par a par (Welch, Bonferroni)
    sup_ics = []
    for s in ["Dura", "Saibro", "Grama"]:
        x = am.loc[am["superficie"] == s, "aces_total"].dropna()
        media, dp, ep, li, ls, gl = est.ic_media_t(x, CONF)
        sup_ics.append({"superficie": s, "n": len(x), "media": media, "ic_inf": li, "ic_sup": ls,
                        "parametro": pop.loc[pop["superficie"] == s, "aces_total"].mean(),
                        "mediana": float(x.median())})
    pares = []
    for a, b in [("Grama", "Dura"), ("Dura", "Saibro"), ("Grama", "Saibro")]:
        w = est.teste_welch(am.loc[am.superficie == a, "aces_total"], am.loc[am.superficie == b, "aces_total"])
        p_bonf = min(1.0, w["valor_p"] * 3)
        dif_pop = (pop.loc[pop.superficie == a, "aces_total"].mean()
                   - pop.loc[pop.superficie == b, "aces_total"].mean())
        pares.append({"a": a, "b": b, **{k: w[k] for k in ("n_a", "n_b", "media_a", "media_b", "diferenca",
                                                             "ic_inf", "ic_sup", "estatistica", "gl", "valor_p")},
                      "valor_p_bonferroni": p_bonf, "rejeita_bonferroni": p_bonf < 0.05, "dif_pop": dif_pop})

    # 3) Canhoto × destro: o canhoto vence mais da metade desses duelos?
    def canhoto(df):
        m = df["mao_vencedor"].notna() & df["mao_perdedor"].notna() & (df["mao_vencedor"] != df["mao_perdedor"])
        x = df.loc[m, "mao_vencedor"]
        return int((x == "Canhoto").sum()), len(x)
    sc, nc = canhoto(am)
    canh = est.teste_z_proporcao(sc, nc, 0.5, "maior").dict()
    psc, pnc = canhoto(pop)
    canh.update({"parametro": psc / pnc, "N": pnc,
                 "pct_canhoto_vencedores": float((pop["mao_vencedor"] == "Canhoto").mean()),
                 "pct_canhoto_perdedores": float((pop["mao_perdedor"] == "Canhoto").mean())})
    return {"formato": formato, "aces_superficie": {"ics": sup_ics, "pares": pares}, "canhotos": canh}


def main() -> None:
    pop = ex.populacao()
    am = pd.read_csv(AQUI / "amostra" / "amostra.csv")
    tam = json.loads((AQUI / "amostra" / "tamanho_amostral.json").read_text(encoding="utf-8"))

    ex.salvar(SAIDA, "meta.json", {"resumo": ex.resumo(), "tamanho": tam, "semente": 15112026,
                                   "codigos": ex.CODIGOS})
    ex.salvar(SAIDA, "populacao.json", ex.colunar(pop))
    am_col = ex.colunar(am)
    am_col.update({"id": am["id_partida"].tolist(), "torneio": am["torneio"].tolist(),
                   "vencedor": am["vencedor"].tolist(), "perdedor": am["perdedor"].tolist(),
                   "placar": am["placar"].tolist()})
    ex.salvar(SAIDA, "amostra.json", am_col)
    ex.salvar(SAIDA, "inferencia.json", inferencia(pop, am))


if __name__ == "__main__":
    main()
