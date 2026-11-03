# Fila atual dos Shorts técnicos

Direção do dono em 2026-11-01: priorizar Java e planejar a explicação com animação
antes da voz e do render. Todo vídeo técnico precisa representar o impacto em System Design.
Ler `direcao-editorial.md` ao preparar cada pauta.

| Ordem | Recorte | Situação |
| --- | --- | --- |
| Agendado 03/11 10h (pt, en; Instagram 02/11) | CompletableFuture em Java | Produzido em 02/11 (`renders/short-completablefuture-java/`) |
| **Próximo tema aprovado** (dono, 2026-11-03) | Virtual threads em Java | Pauta aprovada em `data/episodes/short-virtual-threads-java-pt/pauta.md` (recorte com três modos; o modo `cpu` só se couber em 45 s; data de publicação a decidir): 10 mil requisições com I/O, pool de 200 × virtual threads × virtual com pool de 50 conexões |
| Em revisão | Concorrência em C, com fluxo animado | Vídeo desta sessão; não converter para Java nem refazer as medições |
| Backlog do lote anterior | Árvores | Pauta histórica aprovada, adiada na ordem pela prioridade Java |
| Agendado 04/11 12h (pt, en, Instagram) | Índices com SQLite | Escolhido pelo dono em 2026-11-03; produzido pt+en (`renders/short-indices-sqlite/`, registro em `data/rotina/2026-11-03.md`) |

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
