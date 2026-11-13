"""Seções de texto compartilhadas pelos apps (trabalho da IA003 e projeto público).

Base de dados e população são as mesmas nos dois: o texto fica aqui, num lugar só.
O equivalente do site HTML é `nucleo/web/base.js`.
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from nucleo import dados
from nucleo.dados import br


def base(res: dict, titulo: str = "1. A base de dados", metrica_variaveis: tuple | None = None) -> None:
    """Fonte, origem, contexto e números da base. `metrica_variaveis` = (rótulo, valor, ajuda)."""
    st.header(titulo)
    c1, c2 = st.columns([3, 2])
    with c1:
        st.markdown(f"""
- **Fonte:** [{dados.FONTE_NOME}]({dados.FONTE_URL}). É uma base pública de partidas da ATP, com um
  arquivo por temporada desde 1968, mantida e atualizada pelo projeto Tennismylife
  ([stats.tennismylife.org](https://stats.tennismylife.org/tennis-match-database)).
- **Origem e esquema:** a TML segue o mesmo dicionário de dados da base *tennis_atp* de Jeff Sackmann
  (Tennis Abstract), referência em pesquisas de analytics no tênis. Essa base foi retirada do GitHub
  pelo autor em 2026.
- **Contexto e objetivo:** a base registra resultados, placares, perfil dos jogadores (idade, altura,
  mão dominante, país, ranking) e estatísticas de saque de cada partida. Serve para estudar desempenho,
  equilíbrio competitivo e capacidade preditiva do ranking.
- **Arquivos usados:** temporadas de 2000 a 2025, com {br(res['etapas_filtro']['partidas_brutas_2000_2025'], 0)}
  partidas e {res['n_variaveis_brutas']} variáveis brutas.
""")
    with c2:
        st.metric("Partidas na população (N)", br(res["N"], 0))
        if metrica_variaveis:
            rot, valor, ajuda = metrica_variaveis
            st.metric(rot, valor, help=ajuda)
        st.metric("Edições de torneios", br(res["n_torneios"], 0))
        st.metric("Jogadores distintos", br(res["n_jogadores"], 0))


def populacao(res: dict, titulo: str = "2. População de interesse e unidade amostral",
              unidade: str = "Unidade amostral") -> None:
    """Definição da população, o que ficou de fora e o funil de filtros."""
    st.header(titulo)
    st.markdown(f"""
- **População:** todas as partidas de simples do **circuito principal da ATP** de 2000 a 2025
  (Grand Slams, ATP Finals, Masters 1000, ATP 500 e ATP 250) **concluídas em quadra**.
- **{unidade}:** a **partida**.
- **Ficaram de fora:** Copa Davis, Jogos Olímpicos, eventos por equipes ou de exibição (ATP Cup,
  United Cup, Laver Cup e Next Gen Finals, que usa sets curtos) e partidas não concluídas
  (W/O, abandono ou desclassificação), porque elas não têm duração nem placar completo comparáveis.
""")
    etapas = res["etapas_filtro"]
    st.dataframe(pd.DataFrame({
        "Etapa": ["Partidas brutas 2000–2025", "Somente circuito principal",
                  "Excluindo partidas não concluídas (população final)"],
        "Partidas": [etapas["partidas_brutas_2000_2025"], etapas["apos_filtro_nivel"],
                     etapas["apos_excluir_nao_concluidas"]],
    }), hide_index=True)


def ausentes(res: dict) -> None:
    aus = {k: v for k, v in res["pct_ausentes"].items() if v > 0}
    st.caption("Valores ausentes (% da população): " +
               ", ".join(f"{k} {br(v)}%" for k, v in aus.items()) +
               ". As análises de cada variável usam as partidas com o dado disponível.")


def termos_de_uso() -> None:
    st.caption(f"**Termos de uso da base:** a TML permite uso pessoal, educacional e de pesquisa não comercial, "
               f"com citação da fonte; uso comercial (inclusive treinar modelos de previsão para serviços "
               f"comerciais) exige autorização. [Termos atuais]({dados.TERMOS_URL}).")
