# 015 — Pausas dentro da narração e tom calmo e pausado

- **Status:** aceito para as pausas na narração (2026-10-06, o dono aprovou a abordagem); o tom novo do Gemini segue proposto, pendente de o dono ouvir os áudios de teste
- **Data:** 2026-10-05
- **Etapa do roadmap:** voz (#15), roteiro explicativo (ADR 008)
- **Relaciona-se com:** ADR 008 (planos ancorados na narração), ADR 012 (voz Gemini e Kokoro)

## Contexto

O dono quer uma narração mais calma e com tempo, com pausas no ponto certo de dentro da frase ("Se você quer
realmente… aprender sobre isso, você… deve começar…"). Hoje a pausa só existe entre cenas (`<long pause>` no lote do
Gemini, `app/media/pauses.py`). Dentro da frase, o ritmo é o que o modelo decide. As notas dos termos do Gemini
(`data/benchmarks/termos-gemini-tts.md`) listam tags de pausa no texto (`<short pause>`, `<breath>`). O Kokoro não
tem tags. O tempo de cada plano vem da posição da âncora em caracteres sobre a duração real do WAV (ADR 008,
`app/pipeline/shots.py`), então uma pausa que não conta como caracteres desloca os planos seguintes.

Teste de 2026-10-05 (`data/benchmarks/tom-gemini-calmo-pausado.md`): com 7 `<short pause>` em três cenas e uma
direção de fala mais lenta, o áudio ficou 11% mais longo, com pausas de 0,3 a 1,5 s e sem sinal de a tag ter sido
falada (a confirmar de ouvido).

## Opções consideradas

1. **Marca no texto da narração** (escolhida): `<short pause>` no ponto exato, na própria `narration`.
2. **Campo à parte** com as posições das pausas (`pauses: [{after: "realmente"}]`). Não polui o texto, mas é mais
   um campo para manter em sincronia com a frase, e o modelo de roteiro precisaria escrevê-lo em dois lugares.
3. **Só pontuação** (vírgulas, reticências) e deixar a voz decidir. Sem controle: é o que acontece hoje.

## Decisão

- **Marca.** A `narration` aceita `<short pause>` (a tag do Gemini). `<long pause>` continua reservada ao lote de
  cenas, e qualquer outra tag `<…>` é erro de validação em `scenes.json` e no `vp check`. A marca não vem no começo
  nem no fim da narração, nem duas seguidas.
- **Texto falado e texto mostrado.** O que o Gemini recebe leva a marca; o que a tela, a legenda e as âncoras dos
  planos veem não leva (`app/media/narration.py`: `strip_pauses`). A âncora de um plano é procurada no texto sem
  marcas, então pode atravessar uma pausa.
- **Tempo dos planos.** Cada marca vale `PAUSE_CHARS = 10` caracteres no cálculo de posição das âncoras e na
  estimativa de duração do `vp check` (≈0,75 s a 13 caracteres por segundo; no teste as pausas ficaram entre 0,5 e
  1,1 s). Medido no Kokoro com pausas de 0,7–0,8 s: o erro do início de um plano depois de uma pausa cai de ~0,6 s
  (sem peso) para ~0,1 s (peso 10) na S02; na S01 sobra ~0,8 s, que vem do modelo proporcional por caracteres
  (ADR 008) e não da pausa. O tempo real das cenas continua vindo do WAV.
- **Kokoro.** O adapter divide o texto na marca, sintetiza os pedaços e junta com um silêncio (`pause_ms`, padrão
  300 em `config/providers.toml`, `[kokoro]`). O rascunho local passa a ter as mesmas pausas. O Kokoro já deixa
  ~0,4 s de silêncio nas pontas de cada trecho: com 600 ms a pausa real saiu de ~1,0 s, longa demais para o peso de
  10 caracteres; com 300 ms ficou em 0,70–0,79 s (medido em S01 e S02 da cópia local da régua).
- **Cache de voz.** A chave do WAV usa a `narration` com as marcas: mexer numa pausa regenera só aquela cena.
  No Kokoro, `pause_ms` entra na chave só das cenas que têm marca (as outras não mudam de chave).
- **Lote do Gemini.** Cena com `<short pause>` vai sozinha numa chamada. No teste de 2026-10-05 o corte de lote
  (`app/media/pauses.py`) foi **recusado** no áudio com marcas: a fronteira de 1,14 s não se destacou da pausa
  interna de 1,12 s (exige 30% a mais). Custo: com o tom pausado quase toda cena tem marca, então um episódio de ~10
  cenas gasta ~10 chamadas, o limite do dia. Vale testar, com uma chamada, `<long pause> <long pause>` como separador
  de cenas num lote com marcas; se a fronteira ficar 30% acima das pausas internas, o lote volta a valer.
- **Roteiro.** A skill `roteiro-explicativo` e o agente `roteirista` ganham a regra: pausa só onde o ouvinte
  respiraria (antes da informação nova, depois de uma pergunta), no máximo uma a cada ~15 palavras.
- **Tom (pendente de escuta).** Trocar `styles` em `[gemini_tts]` para "narração de documentário em português do
  Brasil, com sotaque brasileiro; tom calmo, reflexivo e pausado; ritmo lento, com respiros entre as ideias"
  invalida as vozes em cache e o próximo render final refaz tudo (10 chamadas por dia). Só entra depois de o
  dono ouvir `novo-calmo-pausado-s01-s03.wav` ao lado de `atual-s01-s03.wav`. `chars_per_second` do Gemini (13,0)
  precisa ser remedido com a nova direção, junto da v5 da régua.
- **Fora desta ADR:** `<breath>`, duração configurável por marca, SSML, alinhamento de legenda por Whisper.

## Consequências

- Código: `app/media/narration.py` (novo), `app/pipeline/schemas.py` (validação da narração e âncoras),
  `app/pipeline/shots.py` e `check.py` (peso da marca), `app/providers/tts/kokoro.py` (silêncio),
  `config/providers.toml`, `.claude/skills/roteiro-explicativo`, `CLAUDE.md` (§6 e §9) e testes.
- Cenas já aprovadas sem marcas não mudam. Marcas novas só valem para o formato `explainer` (o documentário usa
  outra voz e outro roteiro).
- O Gemini pode ler a tag em voz alta em alguns casos; a escuta de cada vídeo continua obrigatória (gate 4).
