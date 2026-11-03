# CompletableFuture em Java: plano de animação

Plano feito antes de voz e render, como manda a direção editorial (`renders/serie-conceitos/direcao-editorial.md`).
Forma: o `flow` do motion-kit para o mecanismo (nós, setas, estados e dados em trânsito) e `code` e `versus`
para o código e a comparação. Os tempos das cenas de fluxo são **ilustração sincronizada à fala**, não tempos
da medição; os números da tela vêm só de `medicao.json`.

## Controle obrigatório (quadro da direção editorial)

| Item | Definido para este tema | Antes da voz/render | Depois do render |
| --- | --- | --- | --- |
| Aplicação | API de produto que consulta preço e estoque; pool de 4 threads; requisição que espera a resposta | Cenário na pauta e nas cenas `desenho` e `prazo` | Nós `Requisição`, `Pool`, `Consulta preço`, `Consulta estoque`, `thenCombine` reconhecíveis |
| Decisão de System Design | Juntar as duas consultas com `thenCombine` em vez de esperar uma depois da outra; e definir o prazo e o pool | Pergunta e decisão explícitas no gancho e no fecho | A relação entre a composição, o pool e o prazo aparece na animação |
| Benefício e limite | Benefício: a resposta espera pelo caminho mais longo (medido: 309,5 ms contra 501 ms, com as latências simuladas). Limite: o prazo responde ao cliente, mas nesta demonstração a tarefa segue até 2006 ms | Fontes: Javadoc (`fontes.md`) e medição (`demo/resultado.txt`) | Afirmações conferidas contra `medicao.json` e contra a fala |
| Explicação visual | Fluxo composto; estados `waiting`, `running`, `done`, `timeout`; dado `resposta` saindo do `thenCombine`; cena de prazo com `chega tarde` | Sequência planejada abaixo, ligada à fala | Quadros antes/durante/depois abertos e conferidos (pendente) |

**Situação do controle:** preenchido no plano; a conferência depois do render continua pendente (sem render).

## Cenas

| Cena (`id`) / trecho da fala | Estado inicial | Blocos e conexões | Ação visível | Estado final | Fonte |
| --- | --- | --- | --- | --- | --- |
| `gancho` (hook, capa) / "Em Java, a API consulta preço e estoque: espera um e depois o outro, ou junta?" | Pergunta na capa | Texto com a palavra "juntar" em destaque | Nomear Java e a pergunta | Expectativa explícita de composição | Pauta |
| `desenho` (flow) / "As duas consultas partem juntas, num pool de quatro threads. O thenCombine espera as duas e monta a resposta." | Requisição em espera; `thenCombine` em espera | Requisição → Pool (2 tarefas) → Consulta preço e Consulta estoque → thenCombine → Requisição | O pool dispara as duas; estoque termina primeiro (2,0 s); preço termina (2,6 s); `thenCombine` roda e manda `resposta` de volta | Requisição concluída (3,8 s) | Javadoc (`thenCombine`); medição (pool 4) |
| `codigo` (code, passos em 1,5 s e 4,5 s) / "Cada consulta vira um CompletableFuture. O thenCombine só roda quando as duas terminam." | Código inteiro aceso | Linhas 1–4: duas chamadas `supplyAsync`; linhas 5–6: `thenCombine` e `join` | Passo 1: duas tarefas no pool, sem esperar. Passo 2: `thenCombine` espera as duas | Código entendido como "espera pelas duas" | Javadoc (`supplyAsync`, `thenCombine`) |
| `comparacao` (versus, vencedor em 3 s) / "Na medição, em sequência, quinhentos e um milissegundos. Composto, trezentos e nove e meio." | Dois painéis: sequencial e composto | Painel esquerdo: preço 300 ms, depois estoque 200 ms; direito: as duas ao mesmo tempo | Acende o composto (309,5 ms) | Composto menor, com a diferença explicada pelo caminho mais longo | Medição (medianas 501.0 e 309.5) |
| `prazo` (flow, 7 s) / "Com prazo de meio segundo, a resposta sai com timeout. Nesta demonstração, a tarefa segue rodando." | Requisição em espera; tarefa lenta em execução | Requisição → Consulta estoque (lenta) | A requisição passa a `timeout` em 0,8 s; a tarefa continua `running` e termina em 2,3 s; o dado `chega tarde` volta sem uso | Resposta de erro ao cliente; a tarefa segue ocupando o pool até o fim | Javadoc (`orTimeout`, `cancel`); medição (`prazo` 508,1 / 2006,1) |
| `prazo-medido` (categories) / "A resposta saiu em quinhentos e oito. A tarefa só terminou em dois mil e seis." | Duas barras | Resposta com prazo; tarefa termina | Barra da tarefa à destaque | 508,1 ms contra 2006,1 ms | Medição |
| `fecho` (end_card) / "Onde a sua API deixa esperar? Comenta o que você mediria." | Último quadro do fluxo | Pergunta final | Convite à continuação | Pergunta sobre a própria API | Pedido editorial |

## Pontos a conferir na revisão

- Na cena `prazo`, o estado `timeout` do nó Requisição e o estado `done` da tarefa precisam aparecer em quadros
  diferentes; abrir antes/durante/depois.
- O dado `chega tarde` não pode parecer que alterou a resposta: confirmar que a seta chega depois do `timeout`.
- Os tempos dos estados são ilustração: a legenda do rodapé diz "medição" só para os números da tela.
- Fora deste plano: `presenter` (janela do dono) não entra nesta versão.
