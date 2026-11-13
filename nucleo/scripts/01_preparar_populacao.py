"""Passo 1 — monta a POPULAÇÃO a partir dos CSVs brutos da TML-Database.

População de interesse: todas as partidas de simples do circuito principal
da ATP entre 2000 e 2025 (Grand Slams, ATP Finals, Masters 1000, ATP 500 e
ATP 250) que foram concluídas em quadra.

Ficam fora:
- Copa Davis (D), Jogos Olímpicos (O) e eventos por equipes ou de exibição
  (nível A: ATP Cup, United Cup, Laver Cup, Next Gen Finals com sets curtos);
- partidas não concluídas: W/O (walkover), RET (abandono) e DEF (desclassificação).

Unidade amostral: a partida.
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "base" / "raw"
SAIDA = BASE / "base" / "populacao.parquet"
RESUMO = BASE / "base" / "resumo_populacao.json"

NIVEIS = {
    "G": "Grand Slam",
    "F": "ATP Finals",
    "M": "Masters 1000",
    "500": "ATP 500",
    "250": "ATP 250",
}
SUPERFICIES = {"Hard": "Dura", "Clay": "Saibro", "Grass": "Grama", "Carpet": "Carpete"}
RODADAS = {
    "R128": "1ª rodada (R128)", "R64": "R64", "R32": "R32", "R16": "Oitavas (R16)",
    "QF": "Quartas", "SF": "Semifinal", "F": "Final", "RR": "Fase de grupos",
}
MAOS = {"R": "Destro", "L": "Canhoto"}
SET_RE = re.compile(r"\d+-\d+")


def carregar_brutos() -> pd.DataFrame:
    arquivos = sorted(RAW.glob("*.csv"))
    if not arquivos:
        raise SystemExit("Sem CSVs em dados/raw — rode nucleo/scripts/00_baixar_dados.py antes.")
    return pd.concat([pd.read_csv(f, low_memory=False) for f in arquivos], ignore_index=True)


def montar_populacao(bruto: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    etapas = {"partidas_brutas_2000_2025": len(bruto)}

    df = bruto[bruto["tourney_level"].astype(str).isin(NIVEIS)].copy()
    etapas["apos_filtro_nivel"] = len(df)

    nao_concluida = df["score"].astype(str).str.contains(r"W/O|RET|DEF", regex=True)
    df = df[~nao_concluida].copy()
    etapas["apos_excluir_nao_concluidas"] = len(df)

    sets = df["score"].astype(str).apply(lambda s: len(SET_RE.findall(s)))
    rank_ok = df["winner_rank"].notna() & df["loser_rank"].notna()
    minutos = df["minutes"].where(df["minutes"].between(20, 720))  # <20 min = erro de registro

    pop = pd.DataFrame({
        "ano": df["tourney_date"].astype(str).str[:4].astype(int),
        "torneio": df["tourney_name"],
        "nivel": df["tourney_level"].astype(str).map(NIVEIS),
        "superficie": df["surface"].map(SUPERFICIES),
        "ambiente": df["indoor"].map({"O": "Aberto", "I": "Coberto"}),
        "rodada": df["round"].map(RODADAS).fillna(df["round"]),
        "melhor_de": df["best_of"].map({3: "Melhor de 3", 5: "Melhor de 5"}),
        "vencedor": df["winner_name"],
        "perdedor": df["loser_name"],
        "pais_vencedor": df["winner_ioc"],
        "mao_vencedor": df["winner_hand"].map(MAOS),
        "idade_vencedor": df["winner_age"].round(1),
        "altura_vencedor": df["winner_ht"],
        "ranking_vencedor": df["winner_rank"],
        "ranking_perdedor": df["loser_rank"],
        "minutos": minutos,
        "aces_total": df["w_ace"] + df["l_ace"],
        "duplas_faltas_total": df["w_df"] + df["l_df"],
        "sets_jogados": sets,
        "placar": df["score"],
        # perfil do perdedor (para a análise por jogador / top N)
        "pais_perdedor": df["loser_ioc"],
        "mao_perdedor": df["loser_hand"].map(MAOS),
        "idade_perdedor": df["loser_age"].round(1),
        "altura_perdedor": df["loser_ht"],
    })
    # estatísticas de saque de cada lado: v_ = vencedor, p_ = perdedor
    for lado, pref in (("v", "w"), ("p", "l")):
        for novo, orig in (("ace", "ace"), ("df", "df"), ("svpt", "svpt"), ("1in", "1stIn"),
                           ("1won", "1stWon"), ("2won", "2ndWon"), ("svgms", "SvGms"),
                           ("bpsav", "bpSaved"), ("bpfac", "bpFaced")):
            pop[f"{lado}_{novo}"] = df[f"{pref}_{orig}"].to_numpy()
    pop["decada"] = (pop["ano"] // 10 * 10).astype(str) + "s"
    pop["set_decisivo"] = np.where(pop["sets_jogados"] == df["best_of"], "Sim", "Não")
    pop["favorito_venceu"] = np.where(
        rank_ok, np.where(df["winner_rank"] < df["loser_rank"], "Sim", "Não"), None
    )
    pop["dif_ranking"] = (df["winner_rank"] - df["loser_rank"]).abs()
    pop = pop.reset_index(drop=True)
    pop.insert(0, "id_partida", np.arange(1, len(pop) + 1))

    etapas["N_populacao"] = len(pop)
    resumo = {
        "fonte": "TML-Database (Tennismylife) — https://github.com/Tennismylife/TML-Database",
        "periodo": f"{pop['ano'].min()}–{pop['ano'].max()}",
        "N": len(pop),
        "n_variaveis": pop.shape[1],
        "n_variaveis_brutas": bruto.shape[1],
        "etapas_filtro": etapas,
        "pct_ausentes": (pop.isna().mean() * 100).round(2).to_dict(),
        "n_torneios": int(pop[["torneio", "ano"]].drop_duplicates().shape[0]),
        "n_jogadores": int(pd.concat([pop["vencedor"], pop["perdedor"]]).nunique()),
    }
    return pop, resumo


def main() -> None:
    pop, resumo = montar_populacao(carregar_brutos())
    pop.to_parquet(SAIDA, index=False)
    RESUMO.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: resumo[k] for k in ("N", "n_variaveis", "etapas_filtro")}, indent=2))
    print(f"salvo {SAIDA.name} ({SAIDA.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
