---
name: vp-trilha
description: >
  Escreva o plano da trilha sonora de um episódio (music.json): faixa do catálogo, onde
  entra e sai, papel e nível. Use depois do gate 2 e antes da voz final e do render; não
  ouve áudio nem inclui faixa fora do catálogo.
---

# Trilha que segue a virada do roteiro

Leia [CLAUDE.md](../../../CLAUDE.md) e o método em [trilha](../../../.claude/skills/trilha/SKILL.md).
Escreva só `data/episodes/<id>/music.json` (`MusicPlan` em
[schemas.py](../../../app/pipeline/schemas.py), [ADR 030](../../../docs/decisions/030-trilha-por-diretor-musical.md)).
As faixas vêm só de `data/music/catalog.json`; nenhuma faixa fora dele e nenhuma com voz
cantada sob a narração.

Você não ouve as faixas: escolha pelas etiquetas do catálogo e pelo que a narração faz em
cada cena (`delivery`, viradas, frases do dono). As âncoras são trechos literais da
narração, sem as marcas de pausa. O dono decide ouvindo a prévia.

Execute `.venv/bin/vp check <id>` e corrija só os erros de `music.json`. Para cada faixa
usada, `scripts/provisorio/catalogo_musica.py usar <id> <faixa>` copia o ativo; a
aprovação da faixa é do dono. Entregue as faixas escolhidas e por quê, onde ficam os
silêncios e o que o dono precisa ouvir com atenção.
