"""Exporta em JSON tudo o que o site do projeto "Tênis em números" exibe (projeto/site/data/).

Saídas:
- meta.json        base, população e códigos das categorias
- populacao.json   colunas compactas da população (página "O circuito")
- extras.json      linha do tempo, ranking × vitória do favorito, Top N × demais
- jogadores.json   somas por jogador × ano × superfície × nível (filtros no navegador) e checagens
"""
import sys
from pathlib import Path

import pandas as pd

AQUI = Path(__file__).resolve().parents[1]           # pasta do projeto
sys.path.insert(0, str(AQUI.parent))                 # raiz do repositório
from nucleo import analises as an  # noqa: E402
from nucleo import exportacao as ex  # noqa: E402

SAIDA = AQUI / "site" / "data"
CONF = 0.95


# ------------------------------------------------------------------ extras
def extras(pop: pd.DataFrame) -> dict:
    lg = an.longo(pop)
    top = {str(N): {s: an.top_vs_demais(lg, N, s) for s in ["Todas", "Dura", "Saibro", "Grama"]}
           for N in an.TOPS}
    return {
        "linha_tempo": an.linha_tempo(pop),
        "linha_tempo_rotulos": an.LINHA_TEMPO,
        "faixas_ranking": an.faixas_ranking(pop, None, CONF),
        "top_n": {"metricas": [{"chave": k, "nome": n, "unidade": u, "descricao": d}
                               for k, n, u, d in an.METRICAS], "por_n": top},
        "rodadas_por_nivel": rodadas_por_nivel(pop),
    }


def jogadores(pop: pd.DataFrame) -> dict:
    """Somas dos componentes de cada critério por jogador × ano × superfície × nível.

    O site soma essas linhas conforme os filtros e calcula as razões no navegador, com as
    mesmas fórmulas de nucleo/analises.py. `checagem` traz valores calculados aqui no Python
    para conferir o JavaScript.
    """
    lg = an.longo(pop)
    por = ["jogador", "ano", "superficie", "nivel"]
    s = an.somas(lg, por).reset_index()
    nomes = lg["jogador"].value_counts().index.tolist()  # ordenado por nº de partidas
    idx = {n: i for i, n in enumerate(nomes)}
    col = {"j": s["jogador"].map(idx).tolist(), "ano": s["ano"].astype(int).tolist(),
           "sup": ex.codigo(s["superficie"], ex.SUP), "niv": ex.codigo(s["nivel"], ex.NIV),
           "mr": ex.inteiros(s["melhor_rank"])}
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
    ordem = {r: i for i, r in enumerate(ex.ROD)}
    ordem["Fase de grupos"] = -1  # no ATP Finals a fase de grupos vem antes da semifinal
    for niv, g in pop.groupby("nivel"):
        por_torneio = g.groupby(["torneio", "ano"])["rodada"].apply(lambda r: min(r, key=lambda x: ordem.get(x, 99)))
        primeira[niv] = por_torneio.value_counts(normalize=True).round(4).to_dict()
    return primeira


def main() -> None:
    pop = ex.populacao()
    ex.salvar(SAIDA, "meta.json", {"resumo": ex.resumo(), "codigos": ex.CODIGOS})
    ex.salvar(SAIDA, "populacao.json", ex.colunar(pop))
    ex.salvar(SAIDA, "extras.json", extras(pop))
    ex.salvar(SAIDA, "jogadores.json", jogadores(pop))


if __name__ == "__main__":
    main()
