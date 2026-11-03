# Fila atual dos Shorts técnicos

Direção do dono em 2026-11-01: priorizar Java e planejar a explicação com animação
antes da voz e do render. Todo vídeo técnico precisa representar o impacto em System Design.
Ler `direcao-editorial.md` ao preparar cada pauta.

| Ordem | Recorte | Situação |
| --- | --- | --- |
| Próximo tema escolhido | CompletableFuture em Java | Tema e abordagem com animação/System Design decididos pelo dono; recorte da pauta em preparação |
| Em revisão | Concorrência em C, com fluxo animado | Vídeo desta sessão; não converter para Java nem refazer as medições |
| Backlog do lote anterior | Árvores | Pauta histórica aprovada, adiada na ordem pela prioridade Java |
| Backlog do lote anterior | Índices com SQLite | Pauta histórica aprovada, adiada na ordem pela prioridade Java |

Pauta do próximo tema: `data/episodes/short-completablefuture-java-pt/pauta.md`.
Recorte proposto: uma requisição que depende de duas consultas independentes,
com blocos animados para execução, combinação dos resultados e falha/timeout.
O vídeo deve explicar o efeito sobre latência e recursos da aplicação, com os limites
do modelo. As condições de demonstração e o recorte final ainda precisam ser validados.

O contador com `i++`, `synchronized` e `AtomicInteger` fica como ideia de backlog,
sem prioridade sobre o `CompletableFuture` escolhido pelo dono.

Enquanto não houver pauta Java aprovada, a rotina registra essa pendência; não escolhe
silenciosamente uma pauta antiga do calendário. O calendário de `serie.md` é histórico,
não uma alteração de agendamentos já existentes. Não há agendamento novo por esta fila.
