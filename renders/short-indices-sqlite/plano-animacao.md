# Índices no SQLite: plano de animação

Plano feito antes de voz e render (direção editorial de 2026-11-01). Forma: `flow` do motion-kit para o mecanismo
(o `SCAN` lendo a tabela, a busca descendo a árvore do índice, a escrita indo à tabela **e** ao índice), `code` para o
SQL e o plano, `versus` e `categories` para os números medidos. Os tempos dos estados nas cenas de fluxo são
**ilustração sincronizada à fala**, não tempos da medição; os números da tela vêm só de `medicao.json`.

## Controle obrigatório (quadro da direção editorial)

| Item | Definido para este tema | Antes da voz/render | Depois do render |
| --- | --- | --- | --- |
| Aplicação | Loja: tela "Meus pedidos" (API) → SQLite → tabela `pedidos` (1 milhão de linhas); Checkout grava pedidos novos | Cenário na pauta e nas cenas `sem-indice`, `com-indice`, `escrita` | Nós `Meus pedidos`, `SQLite`, `pedidos`, `Checkout`, `pedidos_cliente` reconhecíveis (pendente) |
| Decisão de System Design | Criar o índice em `cliente_id`, a coluna que a leitura da tela filtra, pagando na escrita | Gancho ("e o preço?"), `codigo` (a linha que muda o plano), `escrita` e o fecho (lida ou gravada?) | Relação entre ganho de leitura e custo de escrita dita na fala e vista nos fluxos (pendente) |
| Benefício e limite | Benefício: ms por consulta, sem e com índice (medido). Limite: gravar 10 mil pedidos sem e com índice, tempo de criar o índice, arquivo maior (medidos) | Fontes: `fontes.md` (Q1–Q4, E1–E2, F1–F2); medição: `demo/resultado.txt` | Afirmações conferidas contra `medicao.json` e a fala (pendente) |
| Explicação visual | `sem-indice`: a tabela fica `running` quase a cena toda (lê tudo); `com-indice`: árvore, a chave desce página a página até as linhas; `escrita`: o mesmo pedido vai à tabela e ao índice, e o índice termina depois | Sequência abaixo, ligada à fala | Quadros antes/durante/depois abertos e conferidos (pendente) |

## Cenas

| Cena (`id`) / trecho da fala | Estado inicial | Blocos e conexões | Ação visível | Estado final | Fonte |
| --- | --- | --- | --- | --- | --- |
| `gancho` (hook, capa) / "Uma linha de SQL deixou esta consulta N vezes mais rápida, e cobrou um preço." | Pergunta na capa | Texto com "o preço" em destaque, "SQL · SQLite" no kicker | Nomear a linguagem, o ganho e o custo | Expectativa: quanto e a que preço | Medição (N) |
| `sem-indice` (flow) / "Sem índice, a tela de pedidos pede os pedidos de um cliente e o banco lê a tabela inteira, um milhão de linhas." | Tudo `idle` | Meus pedidos → SQLite (`consulta`) → pedidos (`lê tudo`) → Meus pedidos (dado) | A tela espera; SQLite e tabela ficam `running` por ~3 s; o dado `pedidos` volta | Resposta chega depois de ler a tabela toda | Q1, E1; demo (1 milhão de linhas) |
| `codigo` (code, passos) / "Uma linha, o CREATE INDEX, e o plano troca SCAN por SEARCH." | Código inteiro | Linhas 1–3: SELECT e `-- SCAN pedidos`; 5–8: CREATE INDEX e `-- SEARCH ... USING INDEX` | Passo 1 acende o SCAN; passo 2 acende o índice e o SEARCH | A mesma consulta, outro plano | E1, E2; `EXPLAIN QUERY PLAN` da demo |
| `com-indice` (flow, `layout: tree`) / "O índice guarda os clientes em ordem, numa árvore, e a busca desce direto às linhas de um cliente." | Árvore `idle` | Raiz → páginas → folha → "pedidos do 42 017" | A chave `42 017` desce raiz → página → folha → linhas; cada nó fica `running` e depois `done` | Só um caminho aceso; o resto da árvore não é tocado | Q2, Q3, E2, F1. **Chaves didáticas** (50 000, 25 000…), não do banco |
| `comparacao` (versus) / os ms por consulta, sem e com índice | Dois painéis | Sem índice: `SCAN: 1 milhão de linhas`; com índice: `SEARCH: desce a árvore` | O painel com índice acende | O ganho, com o mecanismo nomeado em cada lado | Medição (medianas) |
| `escrita` (flow, turn) / "Mas cada pedido novo também entra no índice, e gravar dez mil pedidos ficou M vezes mais lento." | Tudo `idle` | Checkout → pedidos (`INSERT`) e Checkout → pedidos_cliente (`entrada`) | Dois dados `pedido` saem juntos; a tabela termina cedo, o índice fica `running` mais tempo | O custo está no índice | F2; medição (M) |
| `custo` (categories) / o tempo de criar o índice e o quanto o arquivo cresceu | Barras | Gravar sem índice, gravar com índice, criar o índice (ms) | A barra "com índice" em destaque | O preço medido | Medição |
| `fecho` (end_card) / "Por isso a decisão depende de quanto essa tabela é lida e gravada. Qual coluna você indexaria?" | Último quadro | Pergunta final | Convite | Decisão de System Design devolvida ao espectador | Pedido editorial |

## Pausas planejadas na fala

- `fecho`: uma pausa de cerca de 1 s entre "…lida e gravada." e "Qual coluna você indexaria?", dada pelo ponto final.
  É o tempo de o espectador pensar na própria tabela antes da pergunta; fica como está.
- Nenhuma outra pausa de 0,5 s ou mais dentro de uma fala. A da `escrita` (0,64 s na vírgula depois de "índice",
  1ª versão) não era planejada: a frase foi reescrita sem a vírgula e a fala refeita.

## Pontos a conferir na revisão

- `sem-indice`: a tabela precisa ficar acesa (`running`) bem mais tempo que qualquer passo da `com-indice`, sem que
  isso pareça um tempo medido: o rodapé diz "medido" só para os números.
- `com-indice`: rótulos das páginas com espaço que não quebra (U+00A0); o token não cobre a folha; os nós não
  tocados ficam `idle` até o fim.
- `escrita`: o índice termina depois da tabela; os dois dados saem ao mesmo tempo.
- Fora deste plano: janela do dono (`host`) e efeitos de cena.
