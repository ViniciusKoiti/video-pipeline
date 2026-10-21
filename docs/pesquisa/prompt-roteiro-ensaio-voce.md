# Prompt: roteiro de ensaio "sobre você" a partir da análise das referências

Cole numa sessão nova do Claude Code, na raiz do repositório. Troque `<id>` pelo episódio (hoje,
`historia-vencedores`). A sessão nova não sabe nada da conversa de 2026-10-20: tudo o que ela precisa está nos
arquivos abaixo.

---

Quero continuar o roteiro do episódio `<id>`, um ensaio de filosofia com anime no molde do Filosofatos, com **quem
assiste no centro**. A análise dos canais de referência já foi feita; não refaça a coleta nem as medições.

**Leia antes, nesta ordem:**
1. `docs/pesquisa/roteiro-referencias-2026-10-20.md`: a síntese. Em especial a seção 3, "O assunto e a
   narrativa" e "A narrativa medida", com a decisão do dono de 2026-10-20 e os números dos 10 vídeos mais vistos.
2. `docs/pesquisa/exemplo-roteiro-ensaio-voce-2026-10-20.md`: o roteiro de base, com as etiquetas [PERGUNTA],
   [HIPÓTESE] e [DONO]. As frases marcadas "[DONO, aprovada em 2026-10-20]" são do dono e não mudam.
3. `docs/pesquisa/molde-bebop-death-note-2026-10-20.md`: o que veio do vídeo de Cowboy Bebop (só forma).
4. `.agents/skills/analise-de-formato/batidas.md`: os tipos de batida, se precisar medir o nosso roteiro.
5. No episódio, `data/episodes/<id>/`: `pauta.md`, `selecao-gate1.md`, `facts.json` e, se existirem, `outline.md`
   e `scenes.json`.
6. As skills `roteiro-explicativo` e `humanizer-narracao`, e o `CLAUDE.md`.

**O que já foi decidido (não reabra):**
- O assunto do vídeo é quem assiste; a obra é um caso entre outros. "Você" entra só como pergunta, como hipótese
  marcada ("Pensa num…") ou como frase do dono. Nunca afirme como fato o que o espectador faz.
- A fala não cita fonte ("segundo…", nome de site ou de autor de estudo). A fonte vai no rodapé. A leitura de
  crítico entra sem nome ("há quem leia que…"). A fala de personagem entra como fala.
- O pensador entra como personagem da cena, com o nome dito.
- Uma chamada só no fim (ADR 026, topo).

**Onde você para e me pergunta:**
- **Frase do dono que falta ou que muda:** escreva de 2 a 3 opções na forma do Filosofatos e me pergunte com
  `AskUserQuestion`, uma pergunta por posição. A forma é: pequena e cotidiana, ligada ao tema; o roteiro que muda
  ("eu ia abrir dizendo…"); ou a tese virada contra o narrador no fecho. Não copie nenhuma frase dele. Só entra o
  que eu escolher e confirmar que é verdade.
- **Gates:** o gate 1 é meu (`vp approve <id> --step sources`), e o gate 2 vem depois do `vp check` e do parecer do
  agente `verificador`. Não registre aprovação por mim.
- **Ficha nova, fonte nova, gasto ou serviço novo:** pergunte antes.
- **Voz e render:** só depois do gate 2 e com o meu pedido.

**Passos:**
1. Leia `scenes.json`, se existir, e rode `vp check <id>`. Se não existir, use o agente `roteirista` com o exemplo
   como base.
2. Rode o agente `verificador` e grave o parecer com `vp checagem`. Problema de ficha volta ao fichamento, e
   problema de roteiro, ao roteirista.
3. Marque as batidas do nosso roteiro com um agente às cegas (`batidas.md`, id cego `V0N`) e rode `narrativa.py
   medir`. Compare com a mediana dos 10 de cima, que está na síntese. A distância que mais importa é a voz do
   narrador: confissão mais opinião, cerca de 20% do tempo.
4. Me traga, em poucas linhas, as 3 diferenças que mais pesam e as perguntas pendentes, agrupadas.

**Regras do projeto que não mudam:** fato só de trecho fichado; opinião marcada como minha ("Pra mim…"); custo zero.
Sem `rm` em comando composto, e saídas refeitas em pasta nova. Se mexer em código, rode `pytest` e `ruff check .`
antes de encerrar.
