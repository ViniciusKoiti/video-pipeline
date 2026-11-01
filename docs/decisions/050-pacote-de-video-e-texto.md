# ADR 050 — Pacote de vídeo e texto do gate 4

Data: 2026-11-01. Status: aceita. Fatia 3 do RF6 do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md).

## Contexto

`shorts_tec.py gate` monta o que o dono assiste e carimba no gate 4: `renders/final.mp4` e `legenda-post.txt`.
Ele copiava o vídeo **antes** de ler o `post.json` (um JSON ruim deixava um vídeo novo com a legenda de uma rodada
anterior, um pacote misturado), sobrescrevia os dois arquivos mesmo com o gate 4 já aprovado para os de hoje,
gravava direto no destino (uma interrupção deixava o MP4 cortado) e lia o post sem conferência (`KeyError`
cru). O id do episódio não era validado: um erro de digitação criava uma pasta nova.

## Decisão

- **`PackagePublisher`** (`app/pipeline/package.py`) valida tudo **antes de escrever**: id de episódio
  (`^[a-z0-9]+(-[a-z0-9]+)*$`); vídeo existente, `.mp4`, não vazio e que o ffprobe lê com duração maior que zero
  (medida injetada); texto do post pelo contrato (`posts[0].value[0].content` não vazio, título opcional e,
  se houver, texto). `read_post` levanta `PackageError` (`PipelineError`) com o arquivo e o campo. Falha aqui não
  escreve nada.
- **Mesmo vídeo e mesmo texto não escrevem nada** (`UNCHANGED`). Outro conteúdo passa pelo `WriteGuard` (ADR 039)
  **antes da primeira cópia**, só para o arquivo que mudaria: com o gate 4 aprovado para os arquivos de hoje, a
  troca é recusada (`ImmutableManifest`) e manda reabrir (`vp reopen --step preview`); repetir o mesmo pacote depois
  da aprovação não é erro.
- **Pacote completo é o que o marcador diz.** A publicação grava `renders/pacote.json` como `writing`, depois o
  vídeo (por temporário, conferido contra o hash da origem) e o texto, e só no fim o marcador `complete`
  (`PackageMarker`, hashes do vídeo e do texto). Falha em qualquer passo deixa `writing`: `package_problems` diz que
  a gravação foi interrompida, e repetir o comando termina o que faltou (se só o último passo faltou, termina só o
  marcador). Um arquivo trocado à mão depois de montado também é apontado. O marcador não entra no que o gate 4
  carimba. Episódio **sem marcador** (anterior a esta regra) segue valendo.
- **O Postiz respeita o pacote:** `gate4()` de `postiz_cadeia` devolve `pacote incompleto (...)` quando o gate 4
  está aprovado mas o pacote não está completo; isso vira bloqueio no `vp postiz pacote` e recusa no `schedule`,
  pelas regras de hoje.
- `shorts_tec.py gate` vira chamador fino do serviço, com os mesmos argumentos e a mesma saída (mais a nota
  "pacote montado" ou "já estava igual").

## Fora do escopo

O pacote do vídeo longo (`montar_episodio.py` grava `renders/final.mp4` pelo motor de render, na próxima fatia);
exigir o marcador em episódios antigos; o texto do `description.txt` e `credits.txt` do `vp export`.

## Emenda de 2026-11-01 (RF7, fatia 7a)

`shorts_tec.py gate` virou `vp short gate <mp4> <post.json> --episodio ID` (`app/commands/short_gate.py`), com a
mesma validação, o mesmo carimbo e a mesma saída. O `--episodio` agora é opção com espaço (`--episodio ID`); a
forma `--episodio=ID` continua valendo no `argparse`.
