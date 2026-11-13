/* Seção compartilhada "A base de dados" + "População" dos dois sites (equivalente a nucleo/secoes.py).
   Uso: secaoBase(elemento, meta.resumo, { unidade: "Unidade amostral" }) */

function secaoBase(el, r, { unidade = "Unidade amostral", tituloPop = "População e unidade amostral" } = {}) {
  const e = r.etapas_filtro;
  el.innerHTML = `
  <div class="grade g2">
    <div class="cartao">
      <h3>Fonte e contexto</h3>
      <p><b>Fonte:</b> <a href="https://github.com/Tennismylife/TML-Database">TML-Database (Tennismylife)</a>,
        base pública de partidas da ATP desde 1968, com um arquivo por temporada, mantida pelo projeto
        <a href="https://stats.tennismylife.org/tennis-match-database">Tennismylife</a>.</p>
      <p><b>Esquema:</b> o mesmo dicionário de dados da base <i>tennis_atp</i> de Jeff Sackmann (Tennis Abstract),
        referência em analytics de tênis. Essa base foi retirada do GitHub pelo autor em 2026.</p>
      <p><b>Conteúdo:</b> resultado e placar, perfil dos jogadores (idade, altura, mão, país, ranking) e
        estatísticas de saque de cada partida.</p>
    </div>
    <div class="cartao">
      <h3>${tituloPop}</h3>
      <p><b>População:</b> todas as partidas de simples do circuito principal da ATP (Grand Slams, ATP Finals,
        Masters 1000, ATP 500 e 250) <b>concluídas</b> entre 2000 e 2025.</p>
      <p><b>${unidade}:</b> a partida.</p>
      <div class="funil">${[
        ["Partidas brutas 2000–2025", e.partidas_brutas_2000_2025],
        ["Só circuito principal", e.apos_filtro_nivel],
        ["Só partidas concluídas = população", e.apos_excluir_nao_concluidas],
      ].map(([rot, v], i) => `<div class="passo" style="margin-left:${i * 14}px;margin-right:${i * 14}px">
          <span>${rot}</span><b>${br(v, 0)}</b></div>`).join("")}</div>
      <p style="font-size:.9rem;color:var(--tinta-2)">Ficaram de fora a Copa Davis, as Olimpíadas, os eventos por
        equipes ou de exibição e as partidas não concluídas (W/O, abandono, desclassificação).</p>
    </div>
  </div>`;
}

function termosDeUso() {
  return `<p class="nota"><b>Termos de uso da base:</b> a TML permite uso pessoal, educacional e de pesquisa não
    comercial, com citação da fonte; uso comercial (inclusive treinar modelos de previsão para serviços comerciais)
    exige autorização. <a href="https://stats.tennismylife.org/tennis-match-database#usage-terms">Termos atuais</a>.</p>`;
}
