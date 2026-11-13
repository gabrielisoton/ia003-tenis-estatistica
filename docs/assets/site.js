/* Navegação do site do trabalho da IA003 (lida por nucleo/web/comum.js). Carregar ANTES de comum.js.
   PROJETO: endereço do site do projeto relativo a este site (até a nota sair, o projeto fica em projeto/). */
window.SITE = {
  marca: "Estatística no Tênis",
  paginas: [
    ["index.html", "Aquecimento", "Base e amostra"],
    ["populacao.html", "1º set", "População"],
    ["amostra.html", "2º set", "Amostra"],
    ["inferencia.html", "3º set", "Inferência"],
  ],
  extras: { rotulo: "Fora da avaliação", dica: "Projeto público que nasceu deste trabalho",
            itens: [["projeto/index.html", "Para fãs de tênis", "Tênis em números"]] },
  rodape: "Atividade avaliativa final · IA003 Probabilidade e Estatística para IA · Especialização em IA · UFRGS",
};
