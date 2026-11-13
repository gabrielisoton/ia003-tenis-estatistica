/* Navegação do site do projeto "Tênis em números" (lida por nucleo/web/comum.js). Carregar ANTES de comum.js.
   O link da disciplina é relativo: até a nota da IA003 sair, o projeto fica em <site>/projeto/ e o trabalho na raiz. */
window.SITE = {
  marca: "Tênis em números",
  paginas: [
    ["index.html", "Início", "Base e população"],
    ["circuito.html", "Visão geral", "O circuito"],
    ["explorar.html", "Tie-break", "Explorar"],
    ["jogadores.html", "Vestiário", "Jogadores"],
  ],
  extras: { rotulo: "Origem", dica: "O projeto nasceu deste trabalho de disciplina",
            itens: [["../index.html", "IA003 · UFRGS", "Trabalho da disciplina"]] },
  rodape: "Projeto pessoal de analytics de tênis · nasceu do trabalho final da IA003 (Especialização em IA, UFRGS)",
};
