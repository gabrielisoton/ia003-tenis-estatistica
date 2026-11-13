"""Início do projeto público: o que é, a base, a população e o que tem em cada partida."""
import pandas as pd
import streamlit as st

from nucleo import dados, enderecos, secoes
from nucleo.dados import br
from nucleo.idiomas import T

res = dados.resumo()

st.title(T("🎾 Tênis em números · o circuito ATP de 2000 a 2025",
           "🎾 Tennis by numbers · the ATP tour from 2000 to 2025"))
st.markdown(T(
    f"Todas as **{br(res['N'], 0)} partidas** do circuito principal da ATP entre 2000 e 2025, com estatísticas de "
    "saque, devolução, break points, tie-breaks e títulos de cada jogador. Use o menu lateral:",
    f"All **{br(res['N'], 0)} matches** on the ATP main tour between 2000 and 2025, with serve, return, "
    "break point, tie-break and title statistics for every player. Use the side menu:"
))
c = st.columns(3)
c[0].markdown(T("**📊 O circuito**  \nComo é uma partida típica: superfícies, duração, aces, ranking. Com filtros.",
                "**📊 The tour**  \nWhat a typical match looks like: surfaces, duration, aces, ranking. With filters."))
c[1].markdown(T("**🏆 Explorar**  \nO que separa a elite do resto, a chance de zebra e como o jogo mudou em 25 anos.",
                "**🏆 Explore**  \nWhat sets the elite apart from the rest, the chance of an upset and how the game "
                "changed over 25 years."))
c[2].markdown(T("**🎾 Jogadores**  \nQuem é o melhor em cada aspecto do jogo, o quadro de medalhas e o perfil de "
                "cada jogador.",
                "**🎾 Players**  \nWho is the best at each aspect of the game, the medal table and a profile of "
                "every player."))

secoes.base(res, titulo=T("A base de dados", "The database"), metrica_variaveis=(
    T("Colunas na base processada", "Columns in the processed database"), res["n_variaveis"],
    T("Inclui as estatísticas de saque de vencedor e perdedor, usadas nas páginas Explorar e Jogadores.",
      "Includes the serve statistics of winner and loser, used on the Explore and Players pages.")))
secoes.populacao(res, titulo=T("A população: o que entra e o que fica de fora",
                               "The population: what is in and what is left out"),
                 unidade=T("Unidade de análise", "Unit of analysis"))

st.subheader(T("O que tem em cada partida", "What each match contains"))
st.dataframe(pd.DataFrame([
    [T("Torneio", "Tournament"),
     T("ano, torneio, nível, superfície, quadra aberta/coberta, rodada, melhor de 3 ou 5",
       "year, tournament, level, surface, outdoor/indoor court, round, best of 3 or 5")],
    [T("Resultado", "Result"),
     T("vencedor, perdedor, placar (sets e tie-breaks), duração em minutos",
       "winner, loser, score (sets and tie-breaks), duration in minutes")],
    [T("Jogadores", "Players"),
     T("idade, altura, mão dominante, país e ranking ATP no início do torneio",
       "age, height, dominant hand, country and ATP ranking at the start of the tournament")],
    [T("Saque (de cada jogador)", "Serve (for each player)"),
     T("aces, duplas faltas, pontos de saque, 1º saque dentro, pontos ganhos com o 1º e "
       "com o 2º saque, games de saque, break points enfrentados e salvos",
       "aces, double faults, service points, 1st serves in, 1st and 2nd serve points won, "
       "service games, break points faced and saved")],
    [T("Derivadas", "Derived"),
     T("favorito venceu?, foi ao set decisivo?, diferença de ranking, sets jogados; e, por jogador, "
       "pontos ganhos na devolução, break points convertidos, dominance ratio, tie-breaks e títulos",
       "did the favourite win?, did it go to a deciding set?, ranking difference, sets played; and, per player, "
       "return points won, break points converted, dominance ratio, tie-breaks and titles")],
], columns=[T("Grupo", "Group"), T("Colunas", "Columns")]), hide_index=True, width="stretch")
st.caption(T("Das 50 colunas brutas da base, ficaram de fora só identificadores (id do torneio, da partida e dos "
             "jogadores), cabeça de chave, forma de entrada (qualifier, wild card, lucky loser), pontos no ranking e "
             "tamanho da chave. Elas são boas candidatas para análises futuras.",
             "Of the database's 50 raw columns, the only ones left out are identifiers (tournament, match and "
             "player ids), seeding, entry type (qualifier, wild card, lucky loser), ranking points and "
             "draw size. They are good candidates for future analyses."))
secoes.ausentes(res)
secoes.termos_de_uso()

st.divider()
st.markdown(T(f"**De onde veio:** o projeto nasceu do trabalho final da disciplina IA003 · Probabilidade e "
              f"Estatística para IA (Especialização em IA, UFRGS), que compara esta população com uma amostra "
              f"aleatória simples. [Ver o trabalho]({enderecos.APP_IA003}) · [Código]({enderecos.REPO}).",
              f"**Where it came from:** the project grew out of the final assignment for the course IA003 · "
              f"Probability and Statistics for AI (AI specialisation programme, UFRGS), which compares this "
              f"population with a simple random sample. [See the assignment, in Portuguese]({enderecos.APP_IA003}) "
              f"· [Code]({enderecos.REPO})."))
