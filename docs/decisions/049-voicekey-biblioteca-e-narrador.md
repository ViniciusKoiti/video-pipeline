# ADR 049 — `VoiceKey`, biblioteca de falas e narrador

Data: 2026-11-01. Status: aceita. Fatia 1 do RF6 do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md). Decisão do dono em 2026-11-01: **manter o nome
atual dos WAVs** (pendência da seção 5 do fluxo, ADR 041).

## Contexto

`montar_episodio.py` (longo) e `shorts_tec.py` (Short) montavam, cada um a seu jeito, a chave do WAV, o laço de
`glob`/`unlink` das versões antigas, o lote e o fechamento do TTS. Os dois **apagavam as versões antigas antes
de gerar a nova**: uma falha ou uma cota esgotada deixava a cena sem fala. Os nomes eram fórmulas diferentes
(`<cena>-<provedor>-<hash>.wav` e `<cena>-<provedor>-<idioma>-<hash>.wav`).

## Decisão

- **`VoiceKey`** (`app/pipeline/models/voice_key.py`): cena, provedor (a **identidade** do cache,
  `TTSProvider.identity`, não o nome de exibição), idioma, `fingerprint` e texto falado. O hash é
  `sha256(f"{fingerprint}|{spoken}")[:10]`, e o nome vem do `Naming` da biblioteca: `LONG` ou `SHORT`.
- **Os nomes de hoje não mudam, nos dois formatos.** No **longo**, o `fingerprint` é a identidade completa do
  adapter (ADR 041): pausa, fala longa e a entrega. No **Short**, por decisão do dono, é o nome de hoje: a identidade
  de um pedido **sem texto** (sem `|pausa` nem `|frases`) mais a entrega pelo nome, no formato antigo
  (`|entrega:hook`), só nas vozes clonadas. Isso mantém os WAVs dos Shorts já aprovados na escuta, com pausa ou
  entrega. O custo está registrado: o nome do Short não acompanha uma mudança de `pause_ms` nem dos valores de
  `exaggeration` e `cfg_weight` da entrega. Os testes comparam, para Kokoro, Gemini e Chatterbox (local e Modal),
  quatro textos e três entregas, com as funções reais `wav_name`, `voice_fingerprint` e `long_speech_tag`.
  A mudança declarada da ADR 041 (a entrega não neutra do **longo** passa a levar os valores) continua valendo.
- **`VoiceLibrary`** (`app/pipeline/voice.py`) é só arquivos: `path`, `has` (o arquivo é um WAV válido, e um
  corrompido no lugar da fala conta como ausente), `stale` (mesmo começo de nome e **exatamente** um hash de 10
  caracteres; nada de outra cena, provedor, idioma ou arquivo que não seja um hash) e `prune`.
- **`Narrator`** gera as falas que faltam com um `TTSProvider` emprestado (quem o constrói o fecha,
  `closing_tts`): `plan` (só as sem WAV), `synthesize` (lote, fallback e cota da ADR 041 por
  `synthesize_requests`) e `produce` (uma saída por fala, na ordem). **A fala nova só substitui a antiga depois
  de pronta:** o WAV é medido (finito e maior que zero; falha do ffprobe vale como inválido) e só então as versões
  antigas são podadas. Falha, WAV inválido ou cota esgotada deixam o anterior utilizável, e um WAV novo que não
  mede some. Retomar é rodar de novo: o cache são os nomes dos arquivos, e um processo novo só pede o que falta.
- A medida do WAV e o glossário (`respell`) entram como funções injetadas: o núcleo não roda ffprobe nem lê
  arquivo de glossário.

## Fora do escopo

Migrar `montar_episodio.py` e `shorts_tec.py` para o `Narrator` (próxima fatia); o registro `<narração>.voz.json`
e o trecho falado (`speech_bounds`); `Production`, `subs` e `render`.
