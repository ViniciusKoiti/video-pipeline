---
name: vp-roteiro
description: >
  Escreva ou revise outline.md e scenes.json de um episódio a partir de fichas
  aprovadas e do objetivo do dono, com narração e planos rastreáveis. Use na etapa
  de roteiro; não pesquisa fatos, produz voz, renderiza ou aprova gates.
---

# Roteiro que entrega a promessa

Leia [AGENT.MD](../../../AGENT.MD), `pauta.md`, `facts.json`, `sources.json` e a decisão
do gate 1 (`.venv/bin/vp status <id>`). Só escreva `outline.md` e `scenes.json` em
`data/episodes/<id>/`. Verifique gate `script` e status das cenas; não sobrescreva
conteúdo aprovado, entregue proposta separada. Sem fichas aprovadas, exponha a pendência
antes de fechar o roteiro.

Use `ScenesManifest` e `Objective` em [schemas.py](../../../app/pipeline/schemas.py).
O dono define tipos e tese. Preserve ordem; notícia requer `event_date`, explicação
requer `question`, opinião requer `thesis` e `thesis_by`. Não transforme opinião em
número ou fato na tela. Se faltarem definições ou evidência para a promessa, devolva
a lacuna ao dono; não troque o objetivo para aproveitar fichas disponíveis.

Para explainer, siga [roteiro-explicativo](../../../.claude/skills/roteiro-explicativo/SKILL.md);
carregue [planos](../../../.claude/skills/roteiro-explicativo/planos.md) só quando escolher
tipos/campos. Para documentário, use contratos e fixtures de formato em
`tests/fixtures/episodes/pilot-example/`; não transplante tipos incompatíveis.

Abra com pergunta, tensão ou consequência sustentada; desenvolva a resposta em cenas
que acrescentem evidência ou mecanismo e feche cumprindo a promessa. Registre no
outline a função de cada bloco e as fichas usadas. Títulos e legendas não prometem
mais que o vídeo entrega. Não force "você" sem ficha de impacto comprovado.

Com radar, registre no outline os padrões relevantes seguidos ou desvios justificados;
`hint` continua hipótese. Faça planos ancorados na narração, com claims inclusive para
dados, relações e texto na tela. Vertical aceita apenas os tipos do schema.
Não estime `duration_ms` no JSON: timing final vem dos WAVs reais. A duração estimada
pertence ao relatório/outline. Só `<short pause>` é marca de pausa válida.

Passe [humanizer-narracao](../../../.claude/skills/humanizer-narracao/SKILL.md) para
melhorar oralidade preservando força, escopo e atribuição. Execute `.venv/bin/vp check <id>`
após a última edição. Entregue pergunta, promessa, gancho, duração estimada, lacunas e
alertas. Encaminhe a versão final para `$vp-checagem`; não registre aprovação do gate 2.
