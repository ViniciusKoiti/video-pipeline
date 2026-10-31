---
name: vp-pauta
description: >
  Prepare a pauta de um vídeo neste workspace com público, pergunta, objetivo do dono,
  requisitos de evidência e hipótese de engajamento. Use antes da pesquisa ou para
  revisar o direcionamento; não escreve roteiro nem baixa fontes.
---

# Pauta antes da pesquisa

Leia [CLAUDE.md](../../../CLAUDE.md) e o pedido do dono. Identifique o episódio em
`data/episodes/<id>/`. Só escreva `pauta.md`; conteúdo aprovado recebe proposta separada.
Não edite manifestos, código, gates ou outros episódios.

Use público, ângulo e objetivo já fornecidos pelo dono. Se faltarem, apresente opções e
agrupe as dúvidas sem escolher objetivo ou tese por ele. `objective.kinds` contém
`noticiar`, `explicar`, `opinar` na ordem do vídeo; campos em
[schemas.py](../../../app/pipeline/schemas.py) e [ADR 019](../../../docs/decisions/019-objetivo-do-video.md).
O estágio do funil (`topo`, `meio`, `fundo`) e o que a chamada final pede também são do dono;
no fundo, nomeie a oferta. Ver [ADR 026](../../../docs/decisions/026-estagio-do-funil.md).

Com `radar-brief.json`, leia `how_to_read`, `caveats`, data, nicho e amostra antes das
recomendações. Separe padrões de indícios; temas viram perguntas neutras às fontes.
Não copie títulos, frases ou imagens de terceiros. Para pauta com radar, siga o método
da [pauta existente](../../../.claude/skills/pauta/SKILL.md). Sem radar, entregue somente
rascunho baseado no pedido do dono, marcando a ausência de validação pelo radar.
Não invente amostra, tendência ou fato para completar o rascunho.

Organize a pauta com público, objetivo/pendências, promessa proposta, recorte, perguntas
neutras, forma, evidência mínima, lacunas e critério de parada. A promessa só se mantém
se as fontes a sustentarem. Ligação com a vida do espectador exige evidência própria.

Compare temas por relevância para esse público, pergunta específica, evidência independente,
diferença editorial e viabilidade visual. Lacuna essencial de evidência impede a escolha,
mesmo que o tema pareça popular. Notas são julgamento editorial, não previsão de viralização.
Registre uma hipótese, uma variável controlável e a métrica a observar; sem métricas
próprias, declare a hipótese não testada.

Termine com dúvidas agrupadas e decisão editorial pendente. A pauta é decidida pelo dono
antes dos downloads; não há comando `vp approve --step pauta`.
