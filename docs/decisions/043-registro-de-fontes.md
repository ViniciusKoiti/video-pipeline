# ADR 043 — Registro de fontes com id sob lock e recuperação definida

Data: 2026-11-01. Status: aceita. Primeira fatia do RF5 do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md) (fontes); ativos e briefs seguem em fatias
próprias. Gaps G02 e G10 da [análise](../analise-gaps-solid-2026-10-31.md).

## Contexto

`baixar_fonte.py` e `fonte_declarada.py` repetiam o mesmo registro: calculavam o próximo `source-NN` lendo o
`sources.json` sem lock (duas execuções repetiam o id), gravavam o manifesto antes dos trechos, registravam a
mesma URL duas vezes e podiam acrescentar fonte depois do gate 1 aprovado, mudando o que o dono carimbou.

## Decisão

- `app/pipeline/sources.py`: `from_bytes`, `fetch_url`, `from_file` e `declared` devolvem o mesmo
  `ExtractedSource` (original, extensão e parágrafos); `SourceRegistry.register` é o único registro. Os scripts
  são chamadores finos, com os mesmos argumentos. O download vai para uma pasta temporária: nada entra no
  episódio antes do registro.
- **Id sob lock:** o `source-NN` livre (maior número mais um) é calculado e usado com o episódio travado.
- **Repetição:** a mesma URL, ou entre as declaradas o mesmo texto, devolve a fonte existente com
  `created=False` e não escreve nada; título, autores ou notas novos não substituem o registrado. Outro texto
  declarado é outra fonte. (Uma página que mudou na web não vira nova fonte sozinha: usar outra URL ou um
  episódio novo.)
- **Gate 1 aprovado:** o `WriteGuard` (ADR 039) é consultado com o `sources.json` novo **antes** de qualquer
  arquivo; recusa com `ImmutableManifest` e a mensagem manda reabrir (`vp reopen --step sources`).
- **Recuperação:** original, texto e trechos são gravados com `write_atomic` (um `replace` por arquivo, não uma
  transação) e o `sources.json` por último. Falha antes do manifesto deixa arquivos de um id que o manifesto não
  tem; a próxima tentativa reaproveita o mesmo id, apaga originais órfãos de outra extensão e sobrescreve o
  resto. A fonte só existe depois do manifesto.
- Texto vazio e arquivo ausente são `SourceError`, antes de qualquer escrita.

## Fora do escopo

`vp sources` (o comando continua stub; os scripts seguem como entrada); busca e entrada de ativos, entradas do
kit e briefs (próximas fatias do RF5); validar a URL além do padrão `http(s)://` do schema.

## Emenda de 2026-11-01 (RF7, fatia 1): `vp sources`

Os dois scripts viraram o comando `vp sources` (`app/commands/sources.py`), com os mesmos argumentos:
`vp sources add <id> <url> --title ... --kind ... [--authors] [--interested] [--notes] [--file]` (era
`baixar_fonte.py`) e `vp sources declared <id> <arquivo> --title ...` (era `fonte_declarada.py`). O registro, o
guard do gate 1 e a escrita do `sources.json` por último seguem sendo o `SourceRegistry`; o comando só monta a
entrada. `scripts/provisorio/baixar_fonte.py` e `fonte_declarada.py` foram removidos (nenhuma skill ou agente os
chamava). `vp numeros` saiu do `app/cli.py` para `app/commands/numeros.py` sem mudar o comportamento, e o
baseline de tamanho do `cli.py` caiu de 301 para 229 linhas de código.
