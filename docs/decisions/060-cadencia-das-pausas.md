# 060 — Cadência das pausas: o silêncio entre frases sai do papel da frase

- **Status:** proposta (2026-11-15). Implementado e opcional por episódio (`voice/cadencia.json`); falta a escuta
  do dono para decidir se vira o padrão.
- **Data:** 2026-11-15
- **Pedido do dono:** "faça 1, 2, 3, 4" (2026-11-15), sobre a crítica da voz do `academia-dinheiro-pt`: "entre uma
  sentença e outra, o intervalo de silêncio tem praticamente a mesma duração fixa".
- **Relaciona-se com:** ADR 015 (pausas na narração), ADR 021 (legenda pelos silêncios do WAV), ADR 022 (entrega
  por cena), ADR 049 e 052 (voz por cena e estado), ADR 054 (cópia nivelada), ADR 058 (Azure Speech).

## Contexto

Medido nos 70 WAVs do `academia-dinheiro-pt` (Azure, `pt-BR-AntonioNeural`): todo WAV termina com 0,81 s de silêncio
(0,74 a 0,84 s) e as cenas são coladas sem intervalo, então as 69 trocas de cena têm ~0,82 s; dentro das cenas,
todo ponto dá ~0,89 s. Uma locução humana encurta a pausa quando a frase seguinte continua a anterior e alonga
depois de pergunta, antes de conclusão e na virada.

## Decisão

- **Plano pelo texto** (`app/media/pacing_plan.py`, puro): cada fim de frase recebe um silêncio pelo papel da
  frase: `continuacao_s` (a próxima começa por "E", "Mas", "Só que"...; 0,4 s), `ponto_s` (0,65 s),
  `conclusao_s` (a próxima começa por "Então", "No fim"...; 0,9 s), `pergunta_s` (1,0 s), `virada_s` (a cena
  seguinte tem entrega `turn` ou `invite`; 1,15 s) e `final_s` (0,8 s), mais `frase_longa_extra_s` (0,1 s) depois
  de frase com 25 palavras ou mais. Os valores são o padrão do modelo `VoicePacing`; o `voice/cadencia.json` do
  episódio pode trocar qualquer um.
- **Aplicação no áudio** (`app/media/voice_pacing.py`): o `silencedetect` (-40 dB) acha os silêncios; a cabeça vira
  0,05 s, a cauda vira o intervalo até a próxima cena e, dentro da cena, os silêncios de 0,65 s para cima viram os
  do plano, só quando a quantidade bate com a de fins de frase do texto (senão ficam como estão, e o estado da
  voz registra `internas_mantidas`). Ficam 60 ms do áudio original em volta de cada corte.
- **Cópia, não troca:** `voice/paced/<wav>-<hash>.wav`, depois do nivelamento (ADR 054) quando ele existe; o WAV
  bruto fica como está e mudar o plano não chama o TTS de novo. O tempo dos planos, a legenda e o `episode.json`
  saem da cópia, como já saíam do WAV.
- **Opcional por episódio:** sem `voice/cadencia.json`, nada muda (episódios aprovados não se mexem). Com o arquivo
  (`{}` usa o padrão), o `vp voice` e o `vp render` usam as cópias. Só no vídeo longo; o Short tem seus tempos
  (`vp short tempos`).

## Consequências

- No `academia-dinheiro-pt` (teste fora do episódio, `data/cache/teste-voz-academia-2026-11-15/`): as 70 cenas
  bateram fim de frase com silêncio; os silêncios passaram de 95 em 0,9 s para uma faixa de 0,4 a 1,3 s, e a fala
  inteira de 706,9 s para 688,0 s.
- Não muda a entonação nem a velocidade dentro da frase: isso é da voz (ADR 058, emenda de 2026-11-15; ADR 022).
- Se o dono aprovar na escuta, o próximo passo é tornar o padrão (arquivo ausente = cadência ligada) e rever os
  valores.
