"""Núcleo compartilhado do projeto de tênis ATP.

Usado pelo projeto público (`projeto/`) e pelas disciplinas (`disciplinas/<código>/`):
- dados: carregamento da população e formatação pt-BR
- estatistica: ICs e testes com a fórmula explícita (validados contra o scipy)
- graficos: cores, layout e o painel descritivo dos apps Streamlit
- analises: formato longo, critérios por jogador, líderes, linha do tempo
- secoes: textos compartilhados "Base de dados" e "População" (Streamlit)
- recarga: mantém os apps no Streamlit Cloud coerentes depois de um push
- enderecos: links públicos dos sites e apps
"""
