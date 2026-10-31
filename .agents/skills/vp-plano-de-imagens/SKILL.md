---
name: vp-plano-de-imagens
description: >
  Monte o plano de imagens de um episódio com roteiro aprovado: o que mostrar em cada
  plano, de onde vem e a conferência de pessoas, marcas e texto de cada ativo. Use depois
  do gate 2 e antes do gate 3; não baixa nada antes do dono validar o plano.
---

# Plano de imagens antes de qualquer download

Leia [AGENT.MD](../../../AGENT.MD) e o método em
[plano-de-imagens](../../../.claude/skills/plano-de-imagens/SKILL.md). Escreva só
`plano-imagens.md`, `decisoes-imagens.md` e, depois da validação do dono, os
`assets/<id>.json` e o `asset_id` dos planos. Não mude fala, âncora nem claim.

A imagem não pode afirmar o que a fala e as fontes não afirmam. Banco e imagem gerada são
ilustração, nunca registro do fato. Ativo sem licença registrada na lista fechada da
[ADR 007](../../../docs/decisions/007-contratos-de-dados.md) não entra; na dúvida de licença
ou de termos de um provedor, pare e pergunte.

Entregue o plano cena a cena (cena, tempo, âncora, tipo, ativo, licença) e **espere a
validação do dono** antes de baixar ou renderizar. Busca em provedor externo só quando o
dono pedir na sessão. Gravar ou trocar `asset_id` pode derrubar o gate 2: diga isso na
entrega. A aprovação do ativo é do dono (`vp approve <id> --step assets`).
