---
name: vp-componentes-do-kit
description: >
  Consulte o motion-kit antes de escolher um componente ou passar uma prop no template do
  formato explicativo (video/). Use ao mexer no template; só leitura, não executa o kit
  nem altera o template sem pedido.
---

# Componentes do kit antes de escrever

Leia [CLAUDE.md](../../../CLAUDE.md) e o método em
[componentes-do-kit](../../../.claude/skills/componentes-do-kit/SKILL.md). O template
(`video/src/ShotView.tsx`, `video/src/Editorial.tsx`) usa `@viniciusk/motion-kit`.

Com o MCP `motion-kit` na sessão, use `describe_component` (sem argumento lista os
componentes; com `component` dá assinatura, defaults e exemplos) e `recommend_components`
(objetivo curado do kit; trate como pista). Sem o MCP, leia no checkout `~/projetos/motion-kit`
o catálogo `src/COMPONENTS.md` e o arquivo do componente. Prop que não aparece na resposta
se confirma no arquivo antes de ser dada como inexistente.

Confira contra a versão que o `video/` renderiza de fato (o tarball em `video/vendor/`,
[ADR 027](../../../docs/decisions/027-motion-kit-por-tarball-versionado.md)), não só contra o checkout.
Mudança de template ou de motion-kit passa pelo vídeo-régua ([CLAUDE.md](../../../CLAUDE.md) §1).
