# 036 — Rotina diária de Shorts: o pedido em pé do dono, até o pacote; gates e agendamento continuam dele

- **Status:** aceita pelo dono em 2026-10-31 ("deixo você fazer isso dessa vez"; "ativado agora"): ele criou a
  skill `short-diario` e a allowlist em `.claude/settings.local.json`, e o timer foi ligado às 21h35 BRT; primeira
  rodada vigiada em 2026-11-01 às 6h com a pauta 2 (concorrência). O agente não cria skill nem se agenda por conta
  própria (o classificador de permissão barra), por isso esses dois passos são do dono.
  Liga depois de dois Shorts da série feitos à mão, com o molde assentado, e da decisão do dono.
- **Relaciona-se com:** ADR 009 (agentes escrevem dados; gates por comando), ADR 024 (voz no Modal só com o pedido
  do dono), ADR 025 (Postiz: pacote, dúvida cega, `schedule` com confirmação), ADR 033 a 035 (Short por JSON,
  medição própria, efeitos e earshot), CLAUDE.md §2.1, §3 (máquina limitada), §12 (conteúdo repetitivo), §14.

## Contexto

O dono quer que todo dia um processo produza um Short da série "eu medi" e ele só valide. Hoje cada passo que
sai da máquina ou custa render só roda "com o pedido do dono na sessão" (CLAUDE.md §14; ADR 024). Uma rotina
agendada não tem sessão: o pedido precisa ser dado uma vez, em pé, com limites escritos.

Duas ferramentas foram comparadas em 2026-10-31: a rotina na nuvem do Claude Code (`/schedule`) roda fora da
máquina do dono, sem o `.env`, o Modal, o kit e os episódios locais, e não pode medir "na minha máquina"; o cron
local (`systemd --user` no WSL, já ativo, com `claude -p` sem terminal) roda onde tudo está.

## Decisão

1. **A rotina é local**: um timer `systemd --user` (`deploy/rotina/short-diario.timer`) chama
   `deploy/rotina/short-diario.sh`, que roda `claude -p "/short-diario"` na raiz do repositório, com `flock` para
   não sobrepor execuções e a sonda de CPU antes (máquina limitada = não roda, e registra).
2. **O que a rotina pode fazer sem perguntar** (o pedido em pé do dono, por esta ADR): tomar a **próxima pauta
   aprovada** da fila (`renders/serie-conceitos/serie.md`, ou `fila.md` quando houver), medir na máquina do dono,
   escrever roteiro, narrações, `content.json` e `medicao.json`, rodar `vp medicao`, `vp traducao`, `inspect` e
   `review` do kit, a **voz clonada no Modal** (ADR 024, na conta do dono), `tempos`, os renders, `sfx.json`,
   `juntar --sfx`, `conferir_audio.py`, as pastas de gate, os `post.json` e o `vp postiz pacote` de cada saída.
3. **O que a rotina nunca faz**: `vp approve` de qualquer gate (tradução e prévia continuam do dono),
   `vp postiz duvida` e `vp postiz schedule` (a dúvida cega lê o estado do gate 4, então vem depois da validação
   da manhã), pontuar título no vidIQ (crédito; a rotina usa o título provisório da pauta), publicar a pasta do
   código no `baixo-nivel-demos` (push é do dono), baixar ou gerar ativo com licença a conferir.
4. **Sem pauta aprovada, a rotina para** e registra "sem pauta". Cadência diária pede sete pautas por semana,
   aprovadas em lote; a rotina não escreve pauta.
5. **Registro**: cada execução escreve `data/rotina/AAAA-MM-DD.md` com o que fez, o que travou, os quadros do
   `review` para olhar e os comandos que faltam ao dono (`vp approve ...`, `vp postiz schedule ...`). A manhã do
   dono é ler esse arquivo, assistir, carimbar e confirmar.
6. **Permissões**: `claude -p` é não interativo; os comandos da rotina precisam estar na allowlist de
   `.claude/settings.json` (uv, node do kit, ffmpeg, `vp` exceto `approve` e `postiz schedule`). O `schedule` segue
   na regra `ask` e falha se tentado, que é o comportamento desejado.

## Trade-offs

- **Cruza a regra "só na sessão"**: por isso é ADR, e por isso o escopo está listado item a item. Qualquer passo
  fora da lista volta a exigir pedido na sessão.
- **Custo**: uma execução de agente por dia no plano do dono, segundos de GPU no Modal por Short, CPU da máquina
  por ~15 min. Zero em API paga.
- **Conteúdo repetitivo (§12)**: sete Shorts por semana no mesmo molde é o risco literal da política do YouTube.
  Cada um precisa de demonstração e número próprios; a pauta é o único lugar onde isso se garante, e ela é humana.
- **Máquina ocupada**: a rotina adia, não força. Um dia sem Short é um dia sem Short.
- **A rotina acelera erros tanto quanto acertos**: por isso liga só depois de dois Shorts à mão.

## Consequências

- Escritos: esta ADR, `deploy/rotina/short-diario.sh` (chama `claude -p "/short-diario"`; a skill é do dono),
  `short-diario.service` e `short-diario.timer` (desligados; `deploy/rotina/instalar.sh` liga).
- Pendente: a decisão do dono de ligar (`systemctl --user enable --now short-diario.timer`), a allowlist de
  permissões, o `fila.md` de pautas quando a série passar de uma por semana, e a primeira rodada vigiada.
