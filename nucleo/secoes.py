"""Seções de texto compartilhadas pelos apps (trabalho da IA003 e projeto público).

Base de dados e população são as mesmas nos dois: o texto fica aqui, num lugar só.
O equivalente do site HTML é `nucleo/web/base.js`.
Os textos têm versão em inglês (`T`), usada só no app do projeto; no app da IA003 tudo fica em português.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from nucleo import dados
from nucleo.dados import br
from nucleo.idiomas import T


def base(res: dict, titulo: str = "1. A base de dados", metrica_variaveis: tuple | None = None) -> None:
    """Fonte, origem, contexto e números da base. `metrica_variaveis` = (rótulo, valor, ajuda)."""
    st.header(titulo)
    c1, c2 = st.columns([3, 2])
    brutas = br(res['etapas_filtro']['partidas_brutas_2000_2025'], 0)
    with c1:
        st.markdown(T(f"""
- **Fonte:** [{dados.FONTE_NOME}]({dados.FONTE_URL}). É uma base pública de partidas da ATP, com um
  arquivo por temporada desde 1968, mantida e atualizada pelo projeto Tennismylife
  ([stats.tennismylife.org](https://stats.tennismylife.org/tennis-match-database)).
- **Origem e esquema:** a TML segue o mesmo dicionário de dados da base *tennis_atp* de Jeff Sackmann
  (Tennis Abstract), referência em pesquisas de analytics no tênis. Essa base foi retirada do GitHub
  pelo autor em 2026.
- **Contexto e objetivo:** a base registra resultados, placares, perfil dos jogadores (idade, altura,
  mão dominante, país, ranking) e estatísticas de saque de cada partida. Serve para estudar desempenho,
  equilíbrio competitivo e capacidade preditiva do ranking.
- **Arquivos usados:** temporadas de 2000 a 2025, com {brutas}
  partidas e {res['n_variaveis_brutas']} variáveis brutas.
""", f"""
- **Source:** [{dados.FONTE_NOME}]({dados.FONTE_URL}). A public database of ATP matches, with one
  file per season since 1968, maintained and updated by the Tennismylife project
  ([stats.tennismylife.org](https://stats.tennismylife.org/tennis-match-database)).
- **Origin and schema:** TML follows the same data dictionary as Jeff Sackmann's *tennis_atp* database
  (Tennis Abstract), a reference in tennis analytics research. That database was taken down from GitHub
  by its author in 2026.
- **Context and purpose:** the database records results, scores, player profiles (age, height,
  dominant hand, country, ranking) and serve statistics for every match. It is used to study performance,
  competitive balance and how well the ranking predicts results.
- **Files used:** the 2000 to 2025 seasons, with {brutas}
  matches and {res['n_variaveis_brutas']} raw variables.
"""))
    with c2:
        st.metric(T("Partidas na população (N)", "Matches in the population (N)"), br(res["N"], 0))
        if metrica_variaveis:
            rot, valor, ajuda = metrica_variaveis
            st.metric(rot, valor, help=ajuda)
        st.metric(T("Edições de torneios", "Tournament editions"), br(res["n_torneios"], 0))
        st.metric(T("Jogadores distintos", "Distinct players"), br(res["n_jogadores"], 0))


def populacao(res: dict, titulo: str = "2. População de interesse e unidade amostral",
              unidade: str = "Unidade amostral") -> None:
    """Definição da população, o que ficou de fora e o funil de filtros."""
    st.header(titulo)
    st.markdown(T(f"""
- **População:** todas as partidas de simples do **circuito principal da ATP** de 2000 a 2025
  (Grand Slams, ATP Finals, Masters 1000, ATP 500 e ATP 250) **concluídas em quadra**.
- **{unidade}:** a **partida**.
- **Ficaram de fora:** Copa Davis, Jogos Olímpicos, eventos por equipes ou de exibição (ATP Cup,
  United Cup, Laver Cup e Next Gen Finals, que usa sets curtos) e partidas não concluídas
  (W/O, abandono ou desclassificação), porque elas não têm duração nem placar completo comparáveis.
""", f"""
- **Population:** every singles match on the **ATP main tour** from 2000 to 2025
  (Grand Slams, ATP Finals, Masters 1000, ATP 500 and ATP 250) **completed on court**.
- **{unidade}:** the **match**.
- **Left out:** Davis Cup, the Olympic Games, team or exhibition events (ATP Cup,
  United Cup, Laver Cup and the Next Gen Finals, which uses short sets) and matches that were not completed
  (walkovers, retirements or defaults), because they lack a comparable duration and full score.
"""))
    etapas = res["etapas_filtro"]
    st.dataframe(pd.DataFrame({
        T("Etapa", "Step"): [T("Partidas brutas 2000–2025", "Raw matches 2000–2025"),
                             T("Somente circuito principal", "Main tour only"),
                             T("Excluindo partidas não concluídas (população final)",
                               "Excluding matches not completed (final population)")],
        T("Partidas", "Matches"): [etapas["partidas_brutas_2000_2025"], etapas["apos_filtro_nivel"],
                                   etapas["apos_excluir_nao_concluidas"]],
    }), hide_index=True)


def ausentes(res: dict) -> None:
    aus = {k: v for k, v in res["pct_ausentes"].items() if v > 0}
    st.caption(T("Valores ausentes (% da população): ", "Missing values (% of the population): ") +
               ", ".join(f"{k} {br(v)}%" for k, v in aus.items()) +
               T(". As análises de cada variável usam as partidas com o dado disponível.",
                 ". The analysis of each variable uses the matches where that value is available."))


def termos_de_uso() -> None:
    st.caption(T(f"**Termos de uso da base:** a TML permite uso pessoal, educacional e de pesquisa não comercial, "
                 f"com citação da fonte; uso comercial (inclusive treinar modelos de previsão para serviços "
                 f"comerciais) exige autorização. [Termos atuais]({dados.TERMOS_URL}).",
                 f"**Database terms of use:** TML allows personal, educational and non-commercial research use, "
                 f"with attribution; commercial use (including training prediction models for commercial "
                 f"services) requires permission. [Current terms]({dados.TERMOS_URL})."))
