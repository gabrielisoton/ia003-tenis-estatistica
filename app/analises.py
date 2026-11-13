"""Análises exploratórias extras (população), usadas pelo Streamlit e pelo exportador do site.

- Top N × demais: onde os melhores do ranking se diferenciam (saque, devolução, break points…)
- Ranking × zebras: chance de o favorito vencer conforme a diferença de ranking
- Linha do tempo: como o jogo mudou de 2000 a 2025
- Jogadores: ranking por critério e perfil individual (página extra "Jogadores")
"""
from __future__ import annotations

import re
from dataclasses import dataclass

import numpy as np
import pandas as pd

import estatistica as est

TOPS = [5, 10, 20, 50, 100]
FAIXAS = [(1, 5), (6, 10), (11, 25), (26, 50), (51, 100), (101, 200), (201, 100_000)]
METRICAS = [
    # chave, nome, unidade, descrição curta
    ("vitorias", "Vitórias", "%", "partidas vencidas"),
    ("saque_ganhos", "Pontos ganhos no saque", "%", "pontos vencidos quando o jogador saca"),
    ("primeiro_dentro", "1º saque dentro", "%", "primeiros saques que entram"),
    ("ganhos_1", "Pontos ganhos com o 1º saque", "%", "quando o 1º saque entra"),
    ("ganhos_2", "Pontos ganhos com o 2º saque", "%", "quando precisa do 2º saque"),
    ("devolucao", "Pontos ganhos na devolução", "%", "pontos vencidos quando o adversário saca"),
    ("bp_salvos", "Break points salvos", "%", "pressão defendida no próprio saque"),
    ("bp_convertidos", "Break points convertidos", "%", "chances de quebra aproveitadas"),
    ("aces_game", "Aces por game de saque", "n", ""),
    ("df_game", "Duplas faltas por game de saque", "n", ""),
    ("idade", "Idade média", "anos", ""),
    ("altura", "Altura média", "cm", ""),
    ("canhoto", "Canhotos", "%", ""),
]


def longo(df: pd.DataFrame) -> pd.DataFrame:
    """Uma linha por jogador em cada partida (vencedor e perdedor)."""
    base = df[["id_partida", "ano", "torneio", "superficie", "melhor_de", "nivel", "rodada"]]
    tb_v, tb_p = _tie_breaks(df["placar"])
    decisivo = (df["set_decisivo"] == "Sim").astype(int).to_numpy()
    lados = []
    for eu, ele, venceu, nome, rk, rko in (("v", "p", 1, "vencedor", "ranking_vencedor", "ranking_perdedor"),
                                           ("p", "v", 0, "perdedor", "ranking_perdedor", "ranking_vencedor")):
        d = base.copy()
        d["jogador"] = df[nome]
        d["rank"] = df[rk]
        d["rank_oponente"] = df[rko]
        d["venceu"] = venceu
        d["idade"] = df[f"idade_{nome}"]
        d["altura"] = df[f"altura_{nome}"]
        d["canhoto"] = (df[f"mao_{nome}"] == "Canhoto").astype(float).where(df[f"mao_{nome}"].notna())
        for c in ("ace", "df", "svpt", "1in", "1won", "2won", "svgms", "bpsav", "bpfac"):
            d[c] = df[f"{eu}_{c}"]
        for c in ("svpt", "1won", "2won", "bpsav", "bpfac"):
            d[f"o_{c}"] = df[f"{ele}_{c}"]
        # placar: tie-breaks na perspectiva do jogador; o set decisivo é sempre do vencedor da partida
        d["tb_jogados"] = tb_v + tb_p
        d["tb_vencidos"] = tb_v if venceu else tb_p
        d["decisivo_jogado"] = decisivo
        d["decisivo_vencido"] = decisivo * venceu
        d["final"] = (df["rodada"] == "Final").astype(int)
        d["titulo"] = d["final"] * venceu
        d["titulo_gs"] = d["titulo"] * (df["nivel"] == "Grand Slam").astype(int)
        d["vs_top10"] = (df[rko] <= 10).astype(int)
        d["vitoria_top10"] = d["vs_top10"] * venceu
        lados.append(d)
    return _componentes(pd.concat(lados, ignore_index=True))


_SET = re.compile(r"(\d+)-(\d+)")
_TB = {(7, 6), (13, 12), (4, 3)}  # 6-6 → 7-6; Wimbledon 2019–21: 12-12 → 13-12; Next Gen: 4-3


def _tie_breaks(placar: pd.Series) -> tuple[np.ndarray, np.ndarray]:
    """Tie-breaks vencidos pelo vencedor e pelo perdedor da partida.

    Cada set "a-b" do placar está do ponto de vista do vencedor: "7-6" é um tie-break que ele
    ganhou e "6-7" um que ele perdeu. Os parênteses (pontos do tie-break) são ignorados.
    """
    v, p = np.zeros(len(placar), int), np.zeros(len(placar), int)
    for i, txt in enumerate(placar.fillna("")):
        for a, b in _SET.findall(txt):
            a, b = int(a), int(b)
            if (a, b) in _TB:
                v[i] += 1
            elif (b, a) in _TB:
                p[i] += 1
    return v, p


def _componentes(lg: pd.DataFrame) -> pd.DataFrame:
    """Numeradores e denominadores de cada critério, por jogador-partida.

    As estatísticas de saque só entram quando a partida as tem completas (mesma regra de
    `metricas`); fora disso ficam NaN e não pesam nas somas.
    """
    ok = lg[["svpt", "o_svpt", "1in", "svgms"]].notna().all(axis=1) & (lg["svpt"] > 0) & (lg["o_svpt"] > 0)
    c = {
        "sv_pts": lg["svpt"], "sv_won": lg["1won"] + lg["2won"],
        "first_in": lg["1in"], "first_won": lg["1won"],
        "second_pts": lg["svpt"] - lg["1in"], "second_won": lg["2won"],
        "ret_pts": lg["o_svpt"], "ret_won": lg["o_svpt"] - lg["o_1won"] - lg["o_2won"],
        "bp_fac": lg["bpfac"], "bp_sav": lg["bpsav"],
        "bp_opp": lg["o_bpfac"], "bp_conv": lg["o_bpfac"] - lg["o_bpsav"],
        "aces": lg["ace"], "dfs": lg["df"], "sv_games": lg["svgms"],
    }
    lg["partida"] = 1
    for k, v in c.items():
        lg[k] = v.where(ok)
    return lg


# ------------------------------------------------------------------ jogadores
@dataclass(frozen=True)
class Criterio:
    chave: str
    nome: str
    num: str               # coluna somada no numerador
    den: str               # coluna somada no denominador
    maior_melhor: bool
    tipo: str              # "%" proporção (tem IC de Wilson) · "taxa" por game · "razao" · "n" contagem
    grupo: str
    desc: str


CRITERIOS = [
    Criterio("vitorias", "Vitórias", "venceu", "partida", True, "%", "Resultado", "partidas vencidas"),
    Criterio("vitorias_top10", "Vitórias contra Top 10", "vitoria_top10", "vs_top10", True, "%", "Resultado",
             "partidas vencidas contra quem estava no Top 10 do ranking"),
    Criterio("dominance", "Dominance ratio", "ret_won", "sv_pts", True, "razao", "Resultado",
             "% de pontos ganhos na devolução ÷ % de pontos perdidos no saque (acima de 1 = domina)"),
    Criterio("saque_ganhos", "Pontos ganhos no saque", "sv_won", "sv_pts", True, "%", "Saque",
             "pontos vencidos quando o jogador saca"),
    Criterio("primeiro_dentro", "1º saque dentro", "first_in", "sv_pts", True, "%", "Saque",
             "primeiros saques que entram"),
    Criterio("ganhos_1", "Pontos ganhos com o 1º saque", "first_won", "first_in", True, "%", "Saque",
             "quando o 1º saque entra"),
    Criterio("ganhos_2", "Pontos ganhos com o 2º saque", "second_won", "second_pts", True, "%", "Saque",
             "quando precisa do 2º saque"),
    Criterio("aces_game", "Aces por game de saque", "aces", "sv_games", True, "taxa", "Saque",
             "aces ÷ games de saque"),
    Criterio("df_game", "Duplas faltas por game de saque", "dfs", "sv_games", False, "taxa", "Saque",
             "duplas faltas ÷ games de saque (menor é melhor)"),
    Criterio("devolucao", "Pontos ganhos na devolução", "ret_won", "ret_pts", True, "%", "Devolução",
             "pontos vencidos quando o adversário saca"),
    Criterio("bp_convertidos", "Break points convertidos", "bp_conv", "bp_opp", True, "%", "Devolução",
             "chances de quebra aproveitadas"),
    Criterio("bp_salvos", "Break points salvos", "bp_sav", "bp_fac", True, "%", "Pressão",
             "pressão defendida no próprio saque"),
    Criterio("tie_breaks", "Tie-breaks vencidos", "tb_vencidos", "tb_jogados", True, "%", "Pressão",
             "sets decididos no tie-break"),
    Criterio("decisivos", "Sets decisivos vencidos", "decisivo_vencido", "decisivo_jogado", True, "%", "Pressão",
             "partidas que foram ao 3º set (melhor de 3) ou ao 5º (melhor de 5)"),
    Criterio("titulos", "Títulos", "titulo", "partida", True, "n", "Conquistas", "finais vencidas"),
    Criterio("finais", "Finais disputadas", "final", "partida", True, "n", "Conquistas", ""),
    Criterio("titulos_gs", "Títulos de Grand Slam", "titulo_gs", "partida", True, "n", "Conquistas", ""),
]
CRIT = {c.chave: c for c in CRITERIOS}
COMPONENTES = ["partida", "venceu", "vitoria_top10", "vs_top10", "sv_pts", "sv_won", "first_in", "first_won",
               "second_pts", "second_won", "ret_pts", "ret_won", "bp_fac", "bp_sav", "bp_opp", "bp_conv",
               "aces", "dfs", "sv_games", "tb_jogados", "tb_vencidos", "decisivo_jogado", "decisivo_vencido",
               "final", "titulo", "titulo_gs"]
NIVEIS = ["Grand Slam", "ATP Finals", "Masters 1000", "ATP 500", "ATP 250"]
SUPERFICIES = ["Dura", "Saibro", "Grama", "Carpete"]


def recortar(lg: pd.DataFrame, anos=None, superficies=None, niveis=None) -> pd.DataFrame:
    m = pd.Series(True, index=lg.index)
    if anos:
        m &= lg["ano"].between(*anos)
    if superficies:
        m &= lg["superficie"].isin(superficies)
    if niveis:
        m &= lg["nivel"].isin(niveis)
    return lg[m]


def somas(lg: pd.DataFrame, por) -> pd.DataFrame:
    """Soma numeradores e denominadores por grupo (jogador, superfície, ano…)."""
    s = lg.groupby(por, observed=True)[COMPONENTES].sum()
    s["melhor_rank"] = lg.groupby(por, observed=True)["rank"].min()
    return s


def valores(s: pd.DataFrame, confianca: float = 0.95) -> pd.DataFrame:
    """Valor de cada critério (razão das somas) e, nas proporções, o IC de Wilson."""
    out = pd.DataFrame(index=s.index)
    out["partidas"] = s["partida"].astype(int)
    out["V"] = s["venceu"].astype(int)
    out["D"] = out["partidas"] - out["V"]
    out["melhor_rank"] = s["melhor_rank"]
    for c in CRITERIOS:
        if c.tipo == "n":
            out[c.chave] = s[c.num].astype(int)
            continue
        if c.tipo == "razao":  # dominance ratio
            ret = s["ret_won"] / s["ret_pts"].replace(0, np.nan)
            perd = (s["sv_pts"] - s["sv_won"]) / s["sv_pts"].replace(0, np.nan)
            out[c.chave] = ret / perd.replace(0, np.nan)
            out[f"{c.chave}_n"] = s["sv_pts"] + s["ret_pts"]
            continue
        den = s[c.den].replace(0, np.nan)
        out[c.chave] = s[c.num] / den
        out[f"{c.chave}_n"] = s[c.den]
        if c.tipo == "%":
            _, li, ls = est.ic_wilson(s[c.num].to_numpy(float), den.to_numpy(float), confianca)
            out[f"{c.chave}_ic_inf"], out[f"{c.chave}_ic_sup"] = li, ls
    return out


def tabela_jogadores(lg: pd.DataFrame, anos=None, superficies=None, niveis=None,
                     min_partidas: int = 100, confianca: float = 0.95) -> pd.DataFrame:
    """Uma linha por jogador com todos os critérios no recorte (só quem tem ≥ min_partidas nele)."""
    t = valores(somas(recortar(lg, anos, superficies, niveis), "jogador"), confianca)
    return t[t["partidas"] >= min_partidas]


def medias_circuito(lg: pd.DataFrame, ref: pd.DataFrame | None = None) -> pd.Series:
    """Média do circuito em cada critério: razão das somas de todos os jogadores do recorte
    (por isso vitórias = 50% e dominance ratio = 1); nas contagens, média por jogador de `ref`."""
    m = valores(somas(lg.assign(_g=0), "_g")).iloc[0]
    for c in CRITERIOS:
        if c.tipo == "n":
            m[c.chave] = float(ref[c.chave].mean()) if ref is not None and len(ref) else np.nan
    return m


def media_circuito(lg: pd.DataFrame, c: Criterio, ref: pd.DataFrame | None = None) -> float:
    return float(medias_circuito(lg, ref)[c.chave])


def posicao(ref: pd.Series, valor: float, maior_melhor: bool) -> tuple[float, int, int]:
    """(percentil 0–100, posição, total).

    Percentil = % dos jogadores de referência que ele supera (empates contam meio);
    posição = 1 + quantos são estritamente melhores.
    """
    r = ref.dropna()
    if pd.isna(valor) or r.empty:
        return np.nan, 0, len(r)
    pior = int(((r < valor) if maior_melhor else (r > valor)).sum())
    melhor = int(((r > valor) if maior_melhor else (r < valor)).sum())
    empate = len(r) - pior - melhor
    return 100 * (pior + 0.5 * empate) / len(r), melhor + 1, len(r)


def ranking_criterio(tab: pd.DataFrame, chave: str) -> pd.DataFrame:
    """Tabela ordenada pelo critério, com posição e percentil dentro da própria tabela."""
    c = CRIT[chave]
    t = tab.dropna(subset=[chave]).copy()
    t = t.sort_values([chave, "partidas"], ascending=[not c.maior_melhor, False])
    t["posicao"] = t[chave].rank(method="min", ascending=not c.maior_melhor).astype(int)
    t["percentil"] = 100 * (t[chave].rank(method="average", ascending=c.maior_melhor) - 0.5) / len(t)
    return t


MEDALHAS = ["ouro", "prata", "bronze"]


def lideres(tab: pd.DataFrame, top: int = 10) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Os melhores de cada critério de uma vez.

    Devolve (podio, medalhas):
    - podio: uma linha por critério com os 3 primeiros, a vantagem do 1º sobre o 2º e, nas proporções,
      se a liderança é "isolada" (IC 95% de Wilson do 1º não toca o do 2º) ou um "empate técnico";
    - medalhas: quadro por jogador (ouros, pratas, bronzes e quantas vezes aparece no top `top`),
      ordenado por pontos (ouro 3, prata 2, bronze 1; desempate por ouros, pratas e top `top`), para
      premiar quem é forte em muitos critérios e não só imbatível em poucos. Nas contagens, valor 0
      não ganha medalha.
    """
    linhas, conta = [], {}
    for c in CRITERIOS:
        rk = ranking_criterio(tab, c.chave)
        if c.tipo == "n":
            rk = rk[rk[c.chave] > 0]
        if rk.empty:
            continue
        r = {"chave": c.chave, "grupo": c.grupo, "criterio": c.nome, "tipo": c.tipo, "n_jogadores": len(rk)}
        for k, med in enumerate(MEDALHAS):
            if k < len(rk):
                r[med] = rk.index[k]
                r[f"{med}_valor"] = rk.iloc[k][c.chave]
        if len(rk) > 1:
            v1, v2 = rk.iloc[0][c.chave], rk.iloc[1][c.chave]
            r["vantagem"] = v1 - v2 if c.maior_melhor else v2 - v1
            if c.tipo == "%":
                a, b = rk.iloc[0], rk.iloc[1]
                isolado = (a[f"{c.chave}_ic_inf"] > b[f"{c.chave}_ic_sup"] if c.maior_melhor
                           else a[f"{c.chave}_ic_sup"] < b[f"{c.chave}_ic_inf"])
                r["lideranca"] = "isolada" if isolado else "empate técnico"
        linhas.append(r)
        for k, nome in enumerate(rk.index[:top]):
            d = conta.setdefault(nome, {"ouro": 0, "prata": 0, "bronze": 0, f"top{top}": 0, "criterios": []})
            if k < 3:
                d[MEDALHAS[k]] += 1
            if k == 0:
                d["criterios"].append(c.nome)
            d[f"top{top}"] += 1
    podio = pd.DataFrame(linhas)
    med = pd.DataFrame.from_dict(conta, orient="index")
    if med.empty:
        return podio, med
    med["partidas"] = tab["partidas"].reindex(med.index)
    med["pontos"] = 3 * med["ouro"] + 2 * med["prata"] + med["bronze"]
    med = med.sort_values(["pontos", "ouro", "prata", f"top{top}"], ascending=False)
    med.index.name = "jogador"
    return podio, med


def perfil_jogador(lg: pd.DataFrame, pop: pd.DataFrame, nome: str, anos=None, superficies=None,
                   min_ref: int = 100, min_recorte: int = 20, confianca: float = 0.95) -> dict:
    """Tudo sobre um jogador no recorte (anos × superfícies).

    Referência dos percentis: os jogadores com ≥ `min_ref` partidas na base inteira que têm
    ≥ `min_recorte` partidas no recorte (sem recorte, são os 366 com ≥100 partidas). O percentil
    compara com os outros jogadores da referência; a posição conta o próprio jogador no total.
    """
    rec = recortar(lg, anos, superficies)
    eu = rec[rec["jogador"] == nome]
    todos = valores(somas(rec, "jogador"), confianca)
    carreira = lg["jogador"].value_counts()
    elegiveis = carreira[carreira >= min_ref].index
    ref = todos[todos.index.isin(elegiveis) & (todos["partidas"] >= min_recorte)]
    if eu.empty:
        return {"nome": nome, "vazio": True, "n_ref": len(ref)}
    linha = todos.loc[nome]
    circ = medias_circuito(rec, ref)
    outros = ref.drop(index=nome, errors="ignore")  # percentil = % dos OUTROS que ele supera

    ficha = []
    for c in CRITERIOS:
        v = linha[c.chave]
        pctl, pos, tot = posicao(outros[c.chave], v, c.maior_melhor)
        tot += 1  # posição "k-ésimo de N" conta o próprio jogador
        ficha.append({
            "chave": c.chave, "criterio": c.nome, "grupo": c.grupo, "tipo": c.tipo, "valor": v,
            "n": linha.get(f"{c.chave}_n", np.nan),
            "ic_inf": linha.get(f"{c.chave}_ic_inf", np.nan), "ic_sup": linha.get(f"{c.chave}_ic_sup", np.nan),
            "media": circ[c.chave], "percentil": pctl, "posicao": pos, "total": tot,
            "maior_melhor": c.maior_melhor,
        })
    ficha = pd.DataFrame(ficha)

    por_sup = valores(somas(eu, "superficie"), confianca)
    por_sup = por_sup.reindex([s for s in SUPERFICIES if s in por_sup.index])
    anual = valores(somas(eu, "ano"), confianca)

    p = pop[pop["ano"].between(*anos)] if anos else pop
    if superficies:
        p = p[p["superficie"].isin(superficies)]
    finais = p[(p["rodada"] == "Final") & ((p["vencedor"] == nome) | (p["perdedor"] == nome))]
    titulos = (finais[finais["vencedor"] == nome][["ano", "torneio", "nivel", "superficie", "perdedor", "placar"]]
               .sort_values(["ano", "torneio"], ascending=[False, True]).reset_index(drop=True))
    por_nivel = pd.DataFrame({
        "Títulos": titulos["nivel"].value_counts(),
        "Finais": finais["nivel"].value_counts(),
    }).reindex(NIVEIS).fillna(0).astype(int)
    por_nivel = por_nivel[por_nivel["Finais"] > 0]

    rk = eu.dropna(subset=["rank"])
    melhor = rk.loc[rk["rank"].idxmin()] if len(rk) else None
    return {
        "nome": nome, "vazio": False, "linha": linha, "ficha": ficha, "n_ref": len(ref),
        "por_superficie": por_sup, "anual": anual, "titulos": titulos, "por_nivel": por_nivel,
        "melhor_rank": int(melhor["rank"]) if melhor is not None else None,
        "melhor_rank_ano": int(melhor["ano"]) if melhor is not None else None,
        "anos": (int(eu["ano"].min()), int(eu["ano"].max())),
    }


def metricas(g: pd.DataFrame) -> dict:
    """Métricas agregadas (razão das somas, como no analytics de tênis)."""
    s = g.dropna(subset=["svpt", "o_svpt", "1in", "svgms"])
    s = s[(s["svpt"] > 0) & (s["o_svpt"] > 0)]
    div = lambda a, b: float(a / b) if b else None  # noqa: E731
    return {
        "n": len(g), "n_jogadores": int(g["jogador"].nunique()), "n_com_stats": len(s),
        "vitorias": float(g["venceu"].mean()) if len(g) else None,
        "saque_ganhos": div((s["1won"] + s["2won"]).sum(), s["svpt"].sum()),
        "primeiro_dentro": div(s["1in"].sum(), s["svpt"].sum()),
        "ganhos_1": div(s["1won"].sum(), s["1in"].sum()),
        "ganhos_2": div(s["2won"].sum(), (s["svpt"] - s["1in"]).sum()),
        "devolucao": div(s["o_svpt"].sum() - (s["o_1won"] + s["o_2won"]).sum(), s["o_svpt"].sum()),
        "bp_salvos": div(s["bpsav"].sum(), s["bpfac"].sum()),
        "bp_convertidos": div((s["o_bpfac"] - s["o_bpsav"]).sum(), s["o_bpfac"].sum()),
        "aces_game": div(s["ace"].sum(), s["svgms"].sum()),
        "df_game": div(s["df"].sum(), s["svgms"].sum()),
        "idade": float(g["idade"].mean()), "altura": float(g["altura"].mean()),
        "canhoto": float(g["canhoto"].mean()),
    }


def top_vs_demais(lg: pd.DataFrame, N: int, superficie: str = "Todas") -> dict:
    d = lg[lg["rank"].notna()]
    if superficie != "Todas":
        d = d[d["superficie"] == superficie]
    top, demais = d[d["rank"] <= N], d[d["rank"] > N]
    duelo = top[top["rank_oponente"] > N]
    entre_tops = top[top["rank_oponente"] <= N]
    jog = (top.groupby("jogador").agg(partidas=("venceu", "size"), vitorias=("venceu", "mean"))
           .sort_values("partidas", ascending=False).head(12).reset_index())
    return {"top": metricas(top), "demais": metricas(demais),
            "duelo": {"n": len(duelo), "vitorias_top": float(duelo["venceu"].mean()) if len(duelo) else None},
            "entre_tops": len(entre_tops) // 2, "jogadores": jog.to_dict("records")}


def faixas_ranking(pop: pd.DataFrame, am: pd.DataFrame | None = None, confianca: float = 0.95) -> list[dict]:
    def taxa(df, lo, hi, bo=None):
        m = df["dif_ranking"].between(lo, hi) & df["favorito_venceu"].notna()
        if bo:
            m &= df["melhor_de"] == bo
        x = df.loc[m, "favorito_venceu"]
        return int((x == "Sim").sum()), len(x)
    saida = []
    total = pop["dif_ranking"].notna().sum()
    for lo, hi in FAIXAS:
        rot = f"{lo}–{hi}" if hi < 100_000 else f"{lo}+"
        s, n = taxa(pop, lo, hi)
        s3, n3 = taxa(pop, lo, hi, "Melhor de 3")
        s5, n5 = taxa(pop, lo, hi, "Melhor de 5")
        item = {"faixa": rot, "pop_n": n, "pop_taxa": s / n, "pop_pct_partidas": n / total,
                "bo3": s3 / n3 if n3 else None, "bo5": s5 / n5 if n5 else None}
        if am is not None:
            sa, na = taxa(am, lo, hi)
            item["am_n"] = na
            if na:
                p, _, li, ls = est.ic_proporcao(sa, na, confianca)
                item.update({"am_taxa": p, "am_ic_inf": max(0.0, li), "am_ic_sup": min(1.0, ls)})
        saida.append(item)
    return saida


LINHA_TEMPO = {
    "minutos_bo3_media": ("Duração média, melhor de 3 (min)", "n"),
    "aces_media": ("Aces por partida (média)", "n"),
    "idade_vencedor": ("Idade média do vencedor (anos)", "n"),
    "altura_vencedor": ("Altura média do vencedor (cm)", "n"),
    "fav_vence": ("% de vitórias do favorito", "%"),
    "set_decisivo": ("% de partidas que vão ao set decisivo", "%"),
    "canhoto_vencedor": ("% de vitórias de canhotos", "%"),
}


def linha_tempo(pop: pd.DataFrame) -> list[dict]:
    linhas = []
    for ano, g in pop.groupby("ano"):
        b3 = g.loc[g["melhor_de"] == "Melhor de 3", "minutos"]
        fav = g["favorito_venceu"].dropna()
        linhas.append({
            "ano": int(ano), "n": len(g),
            "minutos_bo3_media": float(b3.mean()), "minutos_bo3_mediana": float(b3.median()),
            "aces_media": float(g["aces_total"].mean()), "aces_mediana": float(g["aces_total"].median()),
            "idade_vencedor": float(g["idade_vencedor"].mean()),
            "altura_vencedor": float(g["altura_vencedor"].mean()),
            "fav_vence": float((fav == "Sim").mean()),
            "set_decisivo": float((g["set_decisivo"] == "Sim").mean()),
            "canhoto_vencedor": float((g["mao_vencedor"] == "Canhoto").mean()),
        })
    return linhas
