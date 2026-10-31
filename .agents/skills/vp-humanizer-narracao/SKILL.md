---
name: vp-humanizer-narracao
description: >
  Reescreva a narração em pt-BR de um scenes.json para soar como uma pessoa falando, sem
  mudar o que ela afirma. Use no fim do roteiro e antes da checagem; não altera fatos,
  números, nomes, âncoras dos planos nem a promessa.
---

# Narração que soa falada

Leia [AGENT.MD](../../../AGENT.MD) e o método em
[humanizer-narracao](../../../.claude/skills/humanizer-narracao/SKILL.md) (adaptação MIT de
blader/humanizer; a licença está na pasta dessa skill). Só edite o texto de `narration` em
`data/episodes/<id>/scenes.json`.

Nenhum fato, número, data, nome, cargo, relação ou causa entra, sai ou muda. Se uma frase
pede um detalhe que não está nas fichas, escreva uma frase mais simples. Preserve as
âncoras dos planos (o trecho que cada plano cita tem de continuar existindo na narração) e
as marcas de pausa `<short pause>`. Opinião do dono continua dita como opinião.

Depois de editar, execute `.venv/bin/vp check <id>`. Reescrever a narração derruba o gate 2
e o parecer do verificador: diga isso na entrega e liste o que mudou cena a cena, para o
dono e a checagem reverem. A aprovação é do dono.
