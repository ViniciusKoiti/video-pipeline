# ADR 048 — Entradas do Short validadas na leitura; o conteúdo do kit passa intacto

Data: 2026-11-01. Status: aceita. Fatia 5 do RF5 (fecha o RF5) do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md). Gap G10 da
análise de gaps de 2026-10-31 (removida; o resumo está em [refatoracao-resultado](../refatoracao-resultado-2026-11-01.md), §4 e §7). Feita pelo loop de refatoração (prompt removido em 2026-11-01).

## Contexto

`shorts_tec.py` lia o JSON do `motion-video` como `dict[str, Any]` e confiava nele: `fps` 0 dava
`ZeroDivisionError` em `scene_starts`, `durationSec` ausente, `NaN` ou negativo passava, e id de cena repetido
sobrescrevia em silêncio. `fit_durations` alterava o `dict` no lugar. `voiced` repassava `item["speech"]` sem
conferir se o trecho cabia no WAV e juntava `folder / item["wav"]` sem checar `..`. A narração aceitava
qualquer texto em `delivery` e cena repetida. Erros chegavam como `KeyError`, `ZeroDivisionError` ou `SystemExit`.

## Decisão

- **`MotionContent`** (`app/pipeline/models/motion_content.py`) guarda o JSON do kit (`raw`) e só interpreta
  o que o auto-play usa: `scenes`, `durationSec`, `fps` e `host`. Todo o resto fica como veio e volta em `dumps`
  (UTF-8, sem escapar o texto). Nenhum método altera o objeto: `fitted` devolve outro, com cópia profunda, e
  `starts` mantém a conta do `motion-video` (frames inteiros por cena).
- **`app/pipeline/motion_inputs.py`** valida na leitura e levanta `MotionInputError` (`PipelineError`), com o
  arquivo, a cena e o campo: `scenes` lista não vazia de objetos; `id` texto não vazio e único; `durationSec`
  número finito maior que zero (booleano não vale); `type` texto não vazio; `fps` inteiro a partir de 1 (padrão
  30). `fit_content` confere as falas antes de ajustar (cenas que existem, tempo finito e não negativo).
- **Fala gerada** (`load_voiced`): o registro tem de existir, o WAV fica relativo à pasta (sem `..`, sem caminho
  absoluto nem `\`) e existe, `speech` é `[começo, fim]` finitos com `0 <= começo < fim <= duração do WAV` (folga de
  50 ms para o ffprobe) e cada cena tem uma fala. A duração do WAV entra como função injetada: os testes não
  rodam ffprobe.
- **Narração:** `NarrationLine` exige texto não vazio (sem as pontas em branco), `delivery` entre as cinco da ADR
  022 (`neutral`, `hook`, `turn`, `calm`, `invite`) e cena não vazia; `Narration` exige `language`, ao menos uma
  linha e cena sem repetição. A fala sem cena (`scene` nulo) continua permitida. `language` deixou de ter o padrão
  `pt-BR` implícito do script: os 28 arquivos reais já o trazem.
- **Chamadores:** `shorts_tec.py` e `conferir_audio.py` usam o módulo; `fit_durations` e `scene_starts` saíram do
  script (os testes migraram, com a semântica de não alterar o original). `PAD_SEC` e `HOST_HIDDEN_TYPES` foram
  para `MotionConstants`.
- **Os arquivos reais passam:** os 77 conteúdos (com o ida-e-volta idêntico ao original), as 28 narrações e os 18
  registros de fala atuais carregam com as regras acima (conferido na implementação, só leitura). A exceção são
  cópias históricas versionadas (`*.v1.voz.json`) cujos WAVs antigos foram limpos e que o código não carrega.

## Fora do escopo

`ShortProduction`, o `VoicedNarration` que escreve o registro de fala e o `AudioReviewPlan` (RF6); `translation.py`
segue lendo o `content` cru em `content_problems`.

## Emenda de 2026-11-01 (RF7, fatia 7b)

O `shorts_tec.py` acabou: `tempos`, `sfx`, `juntar` e `boca` viraram `vp short tempos|sfx|juntar|boca`
(`app/commands/short_*.py`), sobre `app/pipeline/short_timing.py` (falas, tempos, efeitos), `short_join.py`
(quais falas entram e o comando do ffmpeg), `short_mouth.py` (batidas e envelope da boca) e
`app/media/short_mix.py` (filtro e execução do ffmpeg). As entradas continuam validadas na leitura
(`MotionInputError`); o que era `SystemExit` virou erro do projeto: `ShortAssemblyError` (fala que não cabe, cena
inexistente, plano de efeitos com erro) e `MixError` (ffmpeg da junção falhou, com o fim da mensagem dele). A saída
impressa e os arquivos escritos são os mesmos, com uma diferença: as mensagens de erro saem com o prefixo
`vp short:` e a opção de valor é `--saida PATH` (a forma `--saida=PATH` continua valendo).
