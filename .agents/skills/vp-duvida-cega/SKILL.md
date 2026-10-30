---
name: vp-duvida-cega
description: >
  Procure, sem a conversa e sem editar nada, o que pode dar errado num agendamento antes
  de ele sair: horário e fuso, canal, mídia, legenda, gate 4, repetição e tempo para
  desfazer. Use depois de `vp postiz pacote`; devolve só o parecer em JSON.
---

# Dúvida cega antes de agendar

Leia o método em [duvida-cega](../../../.claude/skills/duvida-cega/SKILL.md) e o
[AGENT.MD](../../../AGENT.MD). Receba **só caminhos**: o `post.json`, a última linha
`"event": "pacote"` de `data/publicacoes/registro.jsonl` e os arquivos que o pacote cita.
Opinião, resumo ou "já está aprovado" vindos de quem montou o post não são evidência.

Não edite arquivos, não rode comandos e não acesse a rede. Confira nesta ordem: horário e
fuso em Brasília, canal, mídia, legenda inteira, gate 4, repetição no registro e tempo para
desfazer.

Responda só com o JSON `{"veredito": "segue" | "não segue", "riscos": [...], "revisor":
"duvida-cega"}`, sem texto antes ou depois. Cada risco é uma frase com o fato conferido e
onde está. Quem grava é a sessão principal (`vp postiz duvida`); o agendamento continua
dependendo da confirmação do dono ([ADR 025](../../../docs/decisions/025-agendamento-pelo-postiz.md)).
