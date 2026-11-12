"""Passo 5 — calcula tudo o que os painéis exibem e exporta em JSON.

O Python é o "motor" estatístico (funções validadas em 04_validar_estatistica.py).
O site HTML (docs/) e a página de extras do Streamlit só leem estes arquivos.

Saídas em docs/data/:
- meta.json        base, população, tamanho amostral e sorteio
- populacao.json   colunas compactas da população (para filtros no navegador)
- amostra.json     as 382 partidas sorteadas (mesmas colunas + nomes e placar)
- inferencia.json  as 4 hipóteses e os testes bônus
- extras.json      linha do tempo, ranking × vitória do favorito, Top N × demais, canhotos
"""
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm, t as tdist

BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE / "app"))
import estatistica as est  # noqa: E402
import hipoteses as hp  # noqa: E402
import analises as an  # noqa: E402

SAIDA = BASE / "docs" / "data"
ALFAS = [0.01, 0.05, 0.10]
CONF = 0.95

SUP = ["Dura", "Saibro", "Grama", "Carpete"]
NIV = ["Grand Slam", "ATP Finals", "Masters 1000", "ATP 500", "ATP 250"]
ROD = ["1ª rodada (R128)", "R64", "R32", "Oitavas (R16)", "Quartas", "Semifinal", "Final",
       "Fase de grupos", "3rd/4th"]


# ------------------------------------------------------------------ utilidades
def limpo(v):
    """Converte numpy/NaN para tipos que o JSON aceita."""
    if isinstance(v, dict):
        return {str(k): limpo(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [limpo(x) for x in v]
    if isinstance(v, (np.bool_, bool)):
        return bool(v)
    if isinstance(v, (np.integer,)):
        return int(v)
    if isinstance(v, (np.floating, float)):
        return None if np.isnan(v) else round(float(v), 6)
    return v


def salvar(nome: str, obj) -> None:
    caminho = SAIDA / nome
    caminho.write_text(json.dumps(limpo(obj), ensure_ascii=False, separators=(",", ":"), allow_nan=False),
                       encoding="utf-8")
    print(f"{nome:16s} {caminho.stat().st_size / 1024:8.0f} KB")


def codigo(serie: pd.Series, ordem: list) -> list:
    mapa = {c: i for i, c in enumerate(ordem)}
    return [mapa.get(v) if isinstance(v, str) else None for v in serie]


def inteiros(serie: pd.Series) -> list:
    return [None if pd.isna(v) else int(v) for v in serie]


def colunar(df: pd.DataFrame) -> dict:
    return {
        "ano": df["ano"].astype(int).tolist(),
        "sup": codigo(df["superficie"], SUP),
        "niv": codigo(df["nivel"], NIV),
        "rod": codigo(df["rodada"], ROD),
        "bo": df["melhor_de"].map({"Melhor de 3": 3, "Melhor de 5": 5}).astype(int).tolist(),
        "mao": codigo(df["mao_vencedor"], ["Destro", "Canhoto"]),
        "fav": [None if v is None or pd.isna(v) else int(v == "Sim") for v in df["favorito_venceu"]],
        "dec": (df["set_decisivo"] == "Sim").astype(int).tolist(),
        "min": inteiros(df["minutos"]),
        "ace": inteiros(df["aces_total"]),
        "df": inteiros(df["duplas_faltas_total"]),
        "idade": [None if pd.isna(v) else round(float(v), 1) for v in df["idade_vencedor"]],
        "alt": inteiros(df["altura_vencedor"]),
        "dif": inteiros(df["dif_ranking"]),
        "rv": inteiros(df["ranking_vencedor"]),
        "rp": inteiros(df["ranking_perdedor"]),
        "sets": df["sets_jogados"].astype(int).tolist(),
    }


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


# ------------------------------------------------------------------ extras
def extras(pop: pd.DataFrame, am: pd.DataFrame) -> dict:
    lg = an.longo(pop)
    top = {str(N): {s: an.top_vs_demais(lg, N, s) for s in ["Todas", "Dura", "Saibro", "Grama"]}
           for N in an.TOPS}
    return {
        "linha_tempo": an.linha_tempo(pop),
        "linha_tempo_rotulos": an.LINHA_TEMPO,
        "faixas_ranking": an.faixas_ranking(pop, am, CONF),
        "top_n": {"metricas": [{"chave": k, "nome": n, "unidade": u, "descricao": d}
                               for k, n, u, d in an.METRICAS], "por_n": top},
        "rodadas_por_nivel": rodadas_por_nivel(pop),
    }


def jogadores(pop: pd.DataFrame) -> dict:
    """Somas dos componentes de cada critério por jogador × ano × superfície × nível.

    O site soma essas linhas conforme os filtros e calcula as razões no navegador, com as
    mesmas fórmulas de app/analises.py. `checagem` traz valores calculados aqui no Python
    para conferir o JavaScript.
    """
    lg = an.longo(pop)
    por = ["jogador", "ano", "superficie", "nivel"]
    s = an.somas(lg, por).reset_index()
    nomes = lg["jogador"].value_counts().index.tolist()  # ordenado por nº de partidas
    idx = {n: i for i, n in enumerate(nomes)}
    col = {"j": s["jogador"].map(idx).tolist(), "ano": s["ano"].astype(int).tolist(),
           "sup": codigo(s["superficie"], SUP), "niv": codigo(s["nivel"], NIV),
           "mr": inteiros(s["melhor_rank"])}
    for c in an.COMPONENTES:
        col[c] = s[c].round().astype(int).tolist()
    finais = pop[pop["rodada"] == "Final"][["ano", "torneio", "nivel", "superficie", "vencedor", "perdedor", "placar"]]
    # checagem: ranking padrão (≥100 partidas, tudo) e o perfil do Federer
    tab = an.tabela_jogadores(lg)
    cheq = {c.chave: [[j, float(v)] for j, v in an.ranking_criterio(tab, c.chave)[c.chave].head(3).items()]
            for c in an.CRITERIOS}
    fed = an.perfil_jogador(lg, pop, "Roger Federer")["ficha"][["chave", "valor", "percentil", "posicao", "total"]]
    return {
        "nomes": nomes,
        "criterios": [{"chave": c.chave, "nome": c.nome, "num": c.num, "den": c.den, "maior_melhor": c.maior_melhor,
                       "tipo": c.tipo, "grupo": c.grupo, "desc": c.desc} for c in an.CRITERIOS],
        "linhas": col,
        "finais": finais.to_dict("list"),
        "checagem": {"top3": cheq, "federer": fed.to_dict("records")},
    }


def rodadas_por_nivel(pop: pd.DataFrame) -> dict:
    """Em que rodada cada nível de torneio começa (explica por que a R32 domina)."""
    primeira = {}
    ordem = {r: i for i, r in enumerate(ROD)}
    ordem["Fase de grupos"] = -1  # no ATP Finals a fase de grupos vem antes da semifinal
    for niv, g in pop.groupby("nivel"):
        por_torneio = g.groupby(["torneio", "ano"])["rodada"].apply(lambda r: min(r, key=lambda x: ordem.get(x, 99)))
        primeira[niv] = por_torneio.value_counts(normalize=True).round(4).to_dict()
    return primeira


def main() -> None:
    SAIDA.mkdir(parents=True, exist_ok=True)
    pop = pd.read_parquet(BASE / "dados" / "populacao.parquet")
    am = pd.read_csv(BASE / "amostra" / "amostra.csv")
    resumo = json.loads((BASE / "dados" / "resumo_populacao.json").read_text(encoding="utf-8"))
    tam = json.loads((BASE / "amostra" / "tamanho_amostral.json").read_text(encoding="utf-8"))

    salvar("meta.json", {"resumo": resumo, "tamanho": tam, "semente": 15112026,
                         "codigos": {"sup": SUP, "niv": NIV, "rod": ROD, "mao": ["Destro", "Canhoto"]}})
    salvar("populacao.json", colunar(pop))
    am_col = colunar(am)
    am_col.update({"id": am["id_partida"].tolist(), "torneio": am["torneio"].tolist(),
                   "vencedor": am["vencedor"].tolist(), "perdedor": am["perdedor"].tolist(),
                   "placar": am["placar"].tolist()})
    salvar("amostra.json", am_col)
    salvar("inferencia.json", inferencia(pop, am))
    salvar("extras.json", extras(pop, am))
    salvar("jogadores.json", jogadores(pop))


if __name__ == "__main__":
    main()
