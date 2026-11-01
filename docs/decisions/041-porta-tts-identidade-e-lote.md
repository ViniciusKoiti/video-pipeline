# ADR 041 — Porta de voz: identidade do cache, lote e ciclo de vida

Data: 2026-11-01. Status: aceita (RF3 do [fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md),
gaps G04 e G05 da análise de gaps de 2026-10-31 (removida; o resumo está em [refatoracao-resultado](../refatoracao-resultado-2026-11-01.md), §4 e §7)). Decide a **porta**; extrair `VoiceKey`, a
biblioteca de WAVs e o narrador, e migrar `montar_episodio.py` e `shorts_tec.py`, vem depois (RF4/RF6).

## Contexto

A chave de cache da voz era montada em dois scripts, cada um com a sua fórmula, a partir do nome do provedor
na configuração (`gemini`, enquanto o adapter se chama `gemini_tts`). O adapter não dizia o que muda a fala:
a entrega do Chatterbox entrava só pelo nome (trocar `exaggeration` reaproveitava áudio errado), a neutra e o
fallback para ela nunca entravam, e o glossário do Kokoro tampouco. O lote, o fallback por cena e o
fechamento do processo da voz clonada eram `getattr` soltos nos scripts. Os adapters escreviam o WAV direto no
caminho final, então uma falha deixava arquivo pela metade.

## Decisão

- **`identity`** (chave do cache, no nome do WAV) é separada de `info.name` (exibição). Alias explícito:
  `GeminiTTS.identity = "gemini"`. Chatterbox local e Modal têm identidades distintas (`chatterbox`,
  `chatterbox_modal`), como os nomes de hoje.
- **`fingerprint(request)`**, uma só assinatura, recebe o pedido. A síntese e a identidade usam a mesma
  resolução de parâmetros efetivos (`_delivery_params`, `voice_for`, idioma, referência), e recusam o mesmo
  pedido com o mesmo erro. O texto não entra: quem monta o nome junta `fingerprint` e texto.
- **O que entra:** Kokoro `kokoro|<voz>`, `|pausa<ms>`, `|lexico<hash>`; Gemini `gemini|<modelo>|<voz>|<estilo>`;
  Chatterbox `<nome>|<modelo>|<idioma>|<hash da referência>`, `|pausa<ms>`, `|entrega:<nome>=<exag>,<cfg>`,
  `|neutro=<exag>,<cfg>` (só se a neutra, usada também como fallback, difere do padrão do modelo), `|frases300` e
  `|v<N>` (versão do corte e junção, só acima de 1). `request.voice` vale no Kokoro e no Gemini e é ignorado
  no Chatterbox, que clona a referência; glossário vale no Kokoro, é erro no Gemini e é ignorado no Chatterbox.
- **Nomes de hoje:** o Gemini, o Kokoro e o Chatterbox sem entrega seguem com a mesma chave (testado contra
  `voice_fingerprint`, `long_speech_tag` e `wav_name` reais). **Mudança declarada:** a entrega não neutra do
  Chatterbox passa a levar os valores (`|entrega:hook=0.8,0.3` no lugar de `|entrega:hook`); essas falas são
  geradas uma vez de novo. *(Revogado para o nome do WAV pela emenda da ADR 049 de 2026-11-01: o nome do longo
  volta a não levar os valores; `fingerprint` do adapter segue completo.)* Entrega desconhecida cai na neutra, nome e identidade. Subir `SPEECH_VERSION`
  regenera só as falas afetadas por uma mudança no corte ou na junção. **Aberto para o `VoiceKey`:** o Short
  nunca pôs pausa nem fala longa na chave; `fingerprint` de um pedido sem texto reproduz o nome dele de hoje,
  e usar isso evita regenerar Shorts já aprovados na escuta. Decidir ao migrar o `shorts_tec`.
- **Escrita:** `atomic_wav` publica o WAV só inteiro e válido (RIFF/WAVE com dados); falha mantém o anterior e
  não deixa temporário. O lote do Gemini corta em pasta temporária, confere todos os cortes e só então publica.
- **`BatchTTS`** (`max_batch_chars`, `synthesize_many`): um resultado por pedido, na ordem, com o `out_path` do
  pedido; uma voz e um idioma por lote. **`Closeable`** + `closing_tts`: quem constrói o TTS o fecha, também
  na exceção; quem o recebe do `Context` não fecha; `close()` é idempotente e o provedor volta a funcionar.
- **Lote e fallback** em `app/media/speech_batches.py`: agrupa só cenas seguidas, mesma voz e idioma, até o
  limite; pausa ou glossário vão sozinhos. Só `InvalidOutput` (corte recusado) gera cena a cena; outro erro vale
  para o grupo, sem rajada individual. `QuotaExhausted` interrompe tudo e as falas não tentadas voltam como
  `needs_review` ("não tentada"). Cada fala é um `SceneOutcome`; WAV inválido não conta como sucesso e some.

## Fora do escopo

`VoiceKey`, `VoiceLibrary`, `Narrator` e a migração dos scripts (os scripts seguem com a lógica deles, que
continua funcionando); `promote` e a limpeza de WAVs obsoletos depois de gerar o novo (RF6); a escrita atômica
do Kokoro só é exercida pelo teste lento (`extra tts`).
