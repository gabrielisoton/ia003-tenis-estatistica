"""Início do projeto público: o que é, a base, a população e o que tem em cada partida."""
import pandas as pd
import streamlit as st

from nucleo import dados, enderecos, secoes
from nucleo.dados import br

res = dados.resumo()

st.title("🎾 Tênis em números · o circuito ATP de 2000 a 2025")
st.markdown(
    f"Todas as **{br(res['N'], 0)} partidas** do circuito principal da ATP entre 2000 e 2025, com estatísticas de "
    "saque, devolução, break points, tie-breaks e títulos de cada jogador. Use o menu lateral:"
)
c = st.columns(3)
c[0].markdown("**📊 O circuito**  \nComo é uma partida típica: superfícies, duração, aces, ranking. Com filtros.")
c[1].markdown("**🏆 Explorar**  \nO que separa a elite do resto, a chance de zebra e como o jogo mudou em 25 anos.")
c[2].markdown("**🎾 Jogadores**  \nQuem é o melhor em cada aspecto do jogo, o quadro de medalhas e o perfil de "
              "cada jogador.")

secoes.base(res, titulo="A base de dados", metrica_variaveis=(
    "Colunas na base processada", res["n_variaveis"],
    "Inclui as estatísticas de saque de vencedor e perdedor, usadas nas páginas Explorar e Jogadores."))
secoes.populacao(res, titulo="A população: o que entra e o que fica de fora", unidade="Unidade de análise")

st.subheader("O que tem em cada partida")
st.dataframe(pd.DataFrame([
    ["Torneio", "ano, torneio, nível, superfície, quadra aberta/coberta, rodada, melhor de 3 ou 5"],
    ["Resultado", "vencedor, perdedor, placar (sets e tie-breaks), duração em minutos"],
    ["Jogadores", "idade, altura, mão dominante, país e ranking ATP no início do torneio"],
    ["Saque (de cada jogador)", "aces, duplas faltas, pontos de saque, 1º saque dentro, pontos ganhos com o 1º e "
                                "com o 2º saque, games de saque, break points enfrentados e salvos"],
    ["Derivadas", "favorito venceu?, foi ao set decisivo?, diferença de ranking, sets jogados; e, por jogador, "
                  "pontos ganhos na devolução, break points convertidos, dominance ratio, tie-breaks e títulos"],
], columns=["Grupo", "Colunas"]), hide_index=True, width="stretch")
st.caption("Das 50 colunas brutas da base, ficaram de fora só identificadores (id do torneio, da partida e dos "
           "jogadores), cabeça de chave, forma de entrada (qualifier, wild card, lucky loser), pontos no ranking e "
           "tamanho da chave. Elas são boas candidatas para análises futuras.")
secoes.ausentes(res)
secoes.termos_de_uso()

st.divider()
st.markdown(f"**De onde veio:** o projeto nasceu do trabalho final da disciplina IA003 · Probabilidade e "
            f"Estatística para IA (Especialização em IA, UFRGS), que compara esta população com uma amostra "
            f"aleatória simples. [Ver o trabalho]({enderecos.APP_IA003}) · [Código]({enderecos.REPO}).")
