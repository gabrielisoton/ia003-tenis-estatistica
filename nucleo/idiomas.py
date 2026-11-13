"""Idiomas do projeto público (português do Brasil e inglês).

Duas peças:
- `T(pt, en)`: texto da interface escrito ao lado da tradução, no próprio código da página.
- `tr(rotulo)`: rótulos que vêm dos DADOS (superfícies, níveis, rodadas, critérios, métricas). O dicionário
  `EN` é a fonte única: o app Streamlit usa direto e o exportador do site grava em `projeto/site/data/en.json`.

O idioma só muda onde a página chama `seletor()` (o projeto). O app da disciplina IA003 nunca chama, então
`lingua()` devolve sempre "pt" lá, mesmo usando as funções compartilhadas do núcleo.
"""
from __future__ import annotations

IDIOMAS = {"pt": "🇧🇷 Português", "en": "🇺🇸 English"}

EN: dict[str, str] = {
    # superfícies, níveis, rodadas e categorias da base
    "Dura": "Hard", "Saibro": "Clay", "Grama": "Grass", "Carpete": "Carpet", "Todas": "All",
    "Grand Slam": "Grand Slam", "ATP Finals": "ATP Finals", "Masters 1000": "Masters 1000",
    "ATP 500": "ATP 500", "ATP 250": "ATP 250",
    "1ª rodada (R128)": "1st round (R128)", "R64": "R64", "R32": "R32", "Oitavas (R16)": "Round of 16",
    "Quartas": "Quarterfinal", "Semifinal": "Semifinal", "Final": "Final", "Fase de grupos": "Round robin",
    "Destro": "Right-handed", "Canhoto": "Left-handed", "Sim": "Yes", "Não": "No",
    "Melhor de 3": "Best of 3", "Melhor de 5": "Best of 5",
    # grupos de critérios
    "Resultado": "Results", "Saque": "Serve", "Devolução": "Return", "Pressão": "Under pressure",
    "Conquistas": "Trophies",
    # critérios (nucleo/analises.CRITERIOS) e métricas do Top N (METRICAS)
    "Vitórias": "Wins", "Vitórias contra Top 10": "Wins vs Top 10", "Dominance ratio": "Dominance ratio",
    "Pontos ganhos no saque": "Service points won", "1º saque dentro": "1st serve in",
    "Pontos ganhos com o 1º saque": "1st serve points won", "Pontos ganhos com o 2º saque": "2nd serve points won",
    "Aces por game de saque": "Aces per service game", "Duplas faltas por game de saque": "Double faults per service game",
    "Pontos ganhos na devolução": "Return points won", "Break points convertidos": "Break points converted",
    "Break points salvos": "Break points saved", "Tie-breaks vencidos": "Tie-breaks won",
    "Sets decisivos vencidos": "Deciding sets won", "Títulos": "Titles", "Finais disputadas": "Finals played",
    "Títulos de Grand Slam": "Grand Slam titles", "Idade média": "Average age", "Altura média": "Average height",
    "Canhotos": "Left-handers",
    # descrições dos critérios e das métricas
    "partidas vencidas": "matches won",
    "partidas vencidas contra quem estava no Top 10 do ranking": "matches won against players ranked in the Top 10",
    "% de pontos ganhos na devolução ÷ % de pontos perdidos no saque (acima de 1 = domina)":
        "% of return points won ÷ % of service points lost (above 1 = dominant)",
    "pontos vencidos quando o jogador saca": "points won when the player serves",
    "primeiros saques que entram": "first serves that go in",
    "quando o 1º saque entra": "when the first serve goes in",
    "quando precisa do 2º saque": "when a second serve is needed",
    "aces ÷ games de saque": "aces ÷ service games",
    "duplas faltas ÷ games de saque (menor é melhor)": "double faults ÷ service games (lower is better)",
    "pontos vencidos quando o adversário saca": "points won when the opponent serves",
    "chances de quebra aproveitadas": "break chances taken",
    "pressão defendida no próprio saque": "pressure defended on own serve",
    "sets decididos no tie-break": "sets decided in a tie-break",
    "partidas que foram ao 3º set (melhor de 3) ou ao 5º (melhor de 5)":
        "matches that went to a 3rd set (best of 3) or a 5th set (best of 5)",
    "finais vencidas": "finals won",
    # linha do tempo (nucleo/analises.LINHA_TEMPO)
    "Duração média, melhor de 3 (min)": "Average duration, best of 3 (min)",
    "Aces por partida (média)": "Aces per match (average)",
    "Idade média do vencedor (anos)": "Average age of the winner (years)",
    "Altura média do vencedor (cm)": "Average height of the winner (cm)",
    "% de vitórias do favorito": "% of wins by the favourite",
    "% de partidas que vão ao set decisivo": "% of matches that go to a deciding set",
    "% de vitórias de canhotos": "% of wins by left-handers",
    # medalhas e liderança (nucleo/analises.lideres)
    "ouro": "gold", "prata": "silver", "bronze": "bronze",
    "isolada": "clear", "empate técnico": "statistical tie",
    # quadra aberta/coberta e séries dos gráficos do painel descritivo (app Streamlit)
    "Aberto": "Outdoor", "Coberto": "Indoor", "População": "Population", "Amostra": "Sample",
}


def lingua() -> str:
    """Idioma escolhido no seletor do app ("pt" fora do Streamlit ou onde não há seletor)."""
    try:
        import streamlit as st
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        if get_script_run_ctx(suppress_warning=True) is None:  # scripts e exportadores rodam sem sessão
            return "pt"
        return st.session_state.get("lingua", "pt")
    except Exception:  # fora de uma sessão do Streamlit (scripts, testes)
        return "pt"


def ingles() -> bool:
    return lingua() == "en"


def T(pt: str, en: str) -> str:
    """Texto da interface no idioma escolhido."""
    return en if ingles() else pt


def tr(rotulo):
    """Traduz um rótulo vindo dos dados; o que não está no dicionário (nomes, torneios) fica igual."""
    if not ingles() or not isinstance(rotulo, str):
        return rotulo
    return EN.get(rotulo, rotulo)


def ordinal(n: int) -> str:
    """1º/2º… em português; 1st/2nd… em inglês."""
    if not ingles():
        return f"{n}º"
    suf = "th" if 10 <= n % 100 <= 20 else {1: "st", 2: "nd", 3: "rd"}.get(n % 10, "th")
    return f"{n}{suf}"


def seletor() -> str:
    """Seletor de idioma na barra lateral (só o app do projeto chama). Lembra a escolha na URL (?lang=en)."""
    import streamlit as st
    if "lingua" not in st.session_state:
        st.session_state["lingua"] = "en" if st.query_params.get("lang") == "en" else "pt"
    st.sidebar.radio("Idioma · Language", list(IDIOMAS), format_func=IDIOMAS.get, key="lingua", horizontal=True)
    if st.session_state["lingua"] == "en":
        st.query_params["lang"] = "en"
    elif "lang" in st.query_params:
        del st.query_params["lang"]
    return st.session_state["lingua"]
