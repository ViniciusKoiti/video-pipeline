# ADR 046 — Entradas dos efeitos sonoros validadas na leitura

Data: 2026-11-01. Status: aceita. Fatia 3 do RF5 do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md), na parte dos efeitos sonoros (ADR 035). Gap
G10 da análise de gaps de 2026-10-31 (removida; o resumo está em [refatoracao-resultado](../refatoracao-resultado-2026-11-01.md), §4 e §7). Feita pelo loop de refatoração (prompt removido em 2026-11-01).

## Contexto

`load_kit` indexava o `sounds.json` do SFX Kit direto (`record["sync"]["at"]`): campo faltando virava
`KeyError` cru. Nada conferia duração positiva, `onset <= body_end <= duration`, id repetido (o último
sobrescrevia em silêncio), `sha256` bem formado nem se `file` ficava dentro da pasta do kit (`kit.path` monta
`root/file` sem checar). O `sfx.json` do vídeo era lido por `SfxPlan.model_validate_json` em cada script, com
`ValidationError` solta. `NaN` e `Infinity` passam no `json.loads` do Python.

## Decisão

- **Invariantes no modelo:** `SfxSound` exige `duration > 0`, tempos finitos, `0 <= sync_at <= duration`,
  `0 <= onset <= body_end <= duration` (folga de 1 µs para o arredondamento do kit), `file` relativo sem `..`
  (`RelPath`) e `sha256` bem formado (`Sha256`). `SfxCue` exige `sound`, `scene` e `text` (quando há) não vazios,
  `offset_s` e `gain_db` finitos.
- **Leitura em `app/pipeline/sfx_inputs.py`:** `parse_kit` e `load_plan` traduzem JSON inválido, campo
  faltando e valor fora do contrato em `SfxInputError` (`PipelineError`, também `ValueError`), com o som
  (`sounds.json, som 3 (whoosh-x): ...`) ou o efeito (`sfx.json: cues.0.offset_s: ...`) na mensagem, e recusam id
  repetido. Falha antes de qualquer junção ou escrita. `load_kit` e `shorts_tec.py`/`conferir_audio.py` usam as duas.
- **Só o que o auto-play usa é interpretado.** Os demais campos do kit (`tuning`, `adapt`, `description`...) são
  ignorados, e o arquivo nunca é reescrito: o `sounds.json` é do dono e só de leitura para o código.
- **O kit real passa:** os 320 sons de `data/sfx/kit/` carregam com as regras acima (conferido na implementação).

## Fora do escopo

`MotionContent` (o JSON do `motion-video` do kit de animação: fps, durações, fala dentro do WAV, preservação de
campos desconhecidos ao carregar e salvar) e as entradas de narração do Short: dependem de `shorts_tec.py`
migrar para `app/` e ficam para a próxima fatia, junto com briefs e catálogo de música.
