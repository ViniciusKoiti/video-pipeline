---
name: vp-shorts-tec
description: >
  Monte um Short ou teaser de tecnologia (até uns 20 s) sobre uma ferramenta do dono, por
  JSON no motion-video do kit, com a voz clonada e o dono numa janela. Use quando o dono
  pedir um Short, teaser ou demo de projeto técnico dele; não vale para episódio longo.
---

# Short de tecnologia sobre o que o dono construiu

Leia [CLAUDE.md](../../../CLAUDE.md) e o método em [shorts-tec](../../../.claude/skills/shorts-tec/SKILL.md).
Episódio do Cena e Conceito segue [`$vp-roteiro`](../vp-roteiro/SKILL.md); Reel de pauta,
[`$vp-pauta`](../vp-pauta/SKILL.md). A frase do Short é "eu construí", nunca "eu achei":
conteúdo original ([CLAUDE.md](../../../CLAUDE.md) §12).

Todo número na tela tem a linha de origem no repositório da ferramenta; sem origem, fica
fora. Escreva só na pasta do Short (`data/episodes/<id>/`) e nos rascunhos em
`renders/<id>/`. A narração passa por `$vp-humanizer-narracao` antes de gravar.

Voz clonada no Modal ([ADR 024](../../../docs/decisions/024-voz-clonada-no-modal.md)), Groq
e qualquer outro serviço externo só com o pedido do dono na sessão, com `cpu_probe()` antes
do render. A pele do dono é dado pessoal: fora do Git. Posts seguem `docs/postiz.md` com
data, mídia e link como lacunas até existirem; nada é agendado sem o `vp postiz pacote`, a
`$vp-duvida-cega` e a autorização do dono ([ADR 025](../../../docs/decisions/025-agendamento-pelo-postiz.md)).
