# ADR 047 — Cópias de briefs e catálogo de música com contrato de substituição

Data: 2026-11-01. Status: aceita. Fatia 4 do RF5 do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md). Feita pelo loop `docs/loop-refatoracao.md`.

## Contexto

`radar_resumo.py` e `formato_resumo.py` repetiam o mesmo contrato (copiar o resumo para o episódio, só trocar
com `--atualizar`, guardar o anterior com a data), mas guardavam com `rename` num nome que só tinha a data:
dois perfis do mesmo dia perdiam o primeiro, e o `rename` entre a troca e a escrita podia deixar o episódio sem
resumo. As pastas também eram resolvidas de jeitos diferentes (`data_dir` das configurações num, `ROOT/data` no
outro). `catalogo_musica.py` dizia "já está no episódio" mesmo quando o arquivo existente era outro, não
conferia o `sha256` do ativo contra o arquivo, deixava mídia órfã quando o `MusicTrack` recusava depois da cópia
e lia `catalog.json` inválido com `ValidationError` solta.

## Decisão

- **Briefs** (`app/pipeline/briefs.py`, `install_brief`): valida pelo contrato antes de qualquer escrita; o mesmo
  conteúdo não escreve nada; outro só entra com `replace`. Na troca, o anterior fica ao lado com a data dele no
  nome (`radar-brief.<data>.json`, `formato-brief-<data>.json`) e **nunca sobrescreve** um guardado antes: o mesmo
  nome com outro conteúdo ganha `.2`, `.3`; conteúdo idêntico reaproveita o arquivo. O guardado é gravado antes da
  troca e cada arquivo vai inteiro (`write_atomic`): uma falha deixa o atual no lugar. Com o episódio travado e
  sem criar a pasta de um episódio que não existe. Conteúdo atual ilegível é guardado com o hash no nome.
- **Catálogo** (`app/pipeline/music_library.py`): `add_track` valida arquivo, formato, licença (a da Audio
  Library ou CC com atribuição), título, clima e `bpm` **antes** de copiar; nunca substitui uma faixa do catálogo;
  grava mídia, ativo e `catalog.json` nessa ordem, cada um inteiro, e a faixa só existe depois do último. A
  sobra de uma tentativa que parou é sobrescrita na seguinte. `install_track` confere o arquivo contra o `sha256`
  do ativo, copia a mídia e publica o ativo por último, e **nunca troca** o que o episódio já tem: a mesma faixa
  não escreve nada, outra versão com o mesmo id é erro, mídia ausente é refeita, e ativo aprovado (status ou
  decisão do gate 3) com a mídia ausente é erro explícito.
- `load_music_catalog` traduz `catalog.json` fora do contrato em `MusicCatalogError` (`PipelineError`).
- As medidas de áudio (ffprobe, loudness) entram como `AudioProbe`, injetado: o serviço e os testes não rodam
  ffmpeg. Os três scripts viram chamadores finos, com os mesmos argumentos, e leem o `data_dir` das configurações.

## Fora do escopo

A escuta do dono (clima, voz cantada) e a licença da faixa continuam sendo dele; o código só confere o registro.
`vp`: os comandos continuam sendo scripts provisórios.
