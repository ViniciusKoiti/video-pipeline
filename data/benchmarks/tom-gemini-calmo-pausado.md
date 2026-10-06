# Teste de tom: Gemini TTS "calmo e pausado" (2026-10-05)

Uma chamada (1 das 10 do dia), `gemini-3.8-flash-tts`, voz Charon, S01 a S03 do `votorantim-dinheiro` num só texto,
separadas por `<long pause>`, sem cortar o áudio. O dono autorizou a chamada nesta sessão.

- **Direção de fala testada:** "narração de documentário em português do Brasil, com sotaque brasileiro; tom
  calmo, reflexivo e pausado; ritmo lento, com respiros entre as ideias" (a atual diz "tom calmo, informativo e
  neutro; ritmo moderado").
- **Texto:** o da régua com 7 marcas `<short pause>` de teste (2 em S01, 3 em S02, 2 em S03), por exemplo:
  "O banco ofereceu um bilhão, `<short pause>` se a usina fosse de vinte mil toneladas por ano." As marcas só
  existem no teste; o `scenes.json` não mudou.
- **Medido:** 37,2 s no total. A voz atual (WAVs do cache) soma 33,5 s para o mesmo texto; com 2 s de silêncio de
  emenda no áudio de comparação, 35,5 s. Ritmo +11%. Pausas de 0,3 s ou mais: 10 (de 0,30 a 1,50 s; a voz
  atual tem 9, de 0,32 a 1,63 s, as naturais entre frases). Se as 7 marcas tivessem sido faladas, o áudio teria
  ~7 s a mais; não parece ter acontecido, mas só a escuta confirma.
- **Arquivos (fora do Git):** `data/benchmarks/voz-gemini/tom/novo-calmo-pausado-s01-s03.wav` e
  `atual-s01-s03.wav` (a atual, com 1 s de pausa entre as cenas).
- **Pendente:** o dono ouvir os dois e dizer se o tom serve.
