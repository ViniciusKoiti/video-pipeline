# ADR 052 — Estado da voz por cena no manifest.json

Data: 2026-11-01. Status: aceita. Fatia 5 do RF6 do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md). Usa o contrato do ADR 040 (`StepState.scenes`).

## Contexto

O `manifest.json` guarda o estado por etapa e, desde o RF2, um registro por cena, mas nada o escrevia para a voz e
nada o lia: uma rodada que parava (cota esgotada, WAV inválido) só imprimia a mensagem. Quem chegasse depois, ou
o `vp status`, não sabia quais falas ficaram para trás nem por quê. Retomar já funcionava, mas só porque os nomes
dos WAVs são o cache.

## Decisão

- **`produce_with_state`** (`app/pipeline/voice_state.py`) roda o `Narrator` com o episódio travado e grava, no
  fim, um registro por fala em `steps.voice`: `completed` com o WAV (caminho relativo), ou `needs_review` com o
  motivo (`quota_exhausted`, `invalid_output`...) e o detalhe. A etapa fica `completed` quando todas estão
  prontas e `needs_review` quando falta alguma (produção incompleta, `pending_scenes`). O `input_hash` é o hash
  dos nomes de WAV de todas as falas (`Narrator.input_hash`): muda com qualquer texto, voz ou entrega.
- **Erro que não é de provedor** (bug, lock aninhado) fica registrado como `failed`, com a mensagem, e a exceção
  sobe, como no `run_scenes`; o que já estava pronto para a mesma entrada segue registrado. O lock sai com a
  exceção. A geração não aninha `store.lock` (um lock só, o de `produce_with_state`).
- **Retomar é rodar de novo.** O que decide o que gerar continua sendo a biblioteca (os nomes dos arquivos), não o
  estado: um processo novo só pede o que falta. O estado diz a quem chega depois o que ficou para trás.
- **`voice_pending`** lê o estado e confere se os WAVs registrados ainda existem (`WAV ausente`); o `vp status` o
  mostra em `pendências` (`pending_pieces` junta isso às peças do vídeo montado). Episódio sem estado de voz não
  mostra nada.
- **Longo e Short:** `montar_episodio.generate_voice` usa o `context.store`; `shorts_tec.generate_voice` trata a pasta
  de produção como o episódio (`JsonFileStore(folder.parent)`, id `folder.name`): os Shorts também são episódios em
  `data/episodes/`. Os dois gravam o relatório.

## Fora do escopo

Estado por cena do render (o cache por cena é do motor Remotion e não passa pelo `manifest.json`); mostrar o
estado da voz em outra parte do `vp status` além das pendências; marcar `running` no começo da rodada para detectar
um processo morto (hoje o estado só muda ao fim, e o cache dos arquivos já cobre a retomada).
