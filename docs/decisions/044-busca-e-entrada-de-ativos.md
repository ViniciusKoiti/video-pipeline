# ADR 044 — Busca tolerante e entrada de ativos que não toca no aprovado

Data: 2026-11-01. Status: aceita. Segunda fatia do RF5 do
[fluxo de refatoração](../fluxo-refatoracao-solid-2026-11-01.md) (ativos). Gap G11 da
[análise](../analise-gaps-solid-2026-10-31.md).

## Contexto

`buscar_candidatos.py` pulava banco sem chave com um aviso e, sem nenhum banco, gravava arquivos vazios que
pareciam "busca sem resultado". Um provedor pago bloqueado caía no mesmo `except` da cota esgotada.
`baixar_escolhidos.py` baixava direto no caminho final e gravava `assets/<id>.json` por cima, mesmo de ativo
aprovado, trocando `used_in_scenes` por uma lista de uma cena e perdendo as associações anteriores.

## Decisão

- **Composição** (`app/bootstrap/archives.py`): `available_archives` devolve os bancos usáveis na ordem da
  cascata e os pulados com o motivo. Banco sem adapter ou com chave ausente (`ConfigurationError`) é pulado;
  qualquer outro erro ao montar o adapter é bug e sobe. `LazyContext.archives` não muda (continua abortando).
- **Busca** (`app/pipeline/assets.py`): `search_archives` registra a falha de um banco com o motivo
  (`quota_exhausted`, `invalid_output`...) e segue com os outros. Três situações são distintas: *sem resultado*
  (lista vazia sem falha), *falha de banco* (registrada) e *nenhum banco disponível* (`NoArchiveAvailable`, com o
  porquê de cada um, sem gravar candidatos). `PaidApiBlocked` é violação da regra de custo zero (§2.1) e
  interrompe a busca; erro de programação sobe. O arquivo de candidatos passa a registrar `razao` das falhas e
  `bancos_pulados`.
- **Entrada** (`AssetIntake`): com o episódio travado, mídia nova vai para um temporário e só então ao lugar,
  e o `assets/<id>.json` por último; falha antes dele deixa mídia sem JSON, que a próxima entrada do mesmo id
  sobrescreve. Ativo já baixado e íntegro (o `sha256` do JSON bate) não é baixado de novo: a cena é acrescentada
  a `used_in_scenes`, sem apagar as anteriores, e repetir a escolha não escreve nada. Mídia ausente ou diferente
  do `sha256` num ativo não aprovado é baixada de novo (`repaired`), mantendo as cenas.
- **Aprovado nunca é alterado**, nem JSON nem mídia: status de topo `approved` ou decisão do gate 3 ainda válida
  (o `WriteGuard`, ADR 039). O uso em outra cena fica só no `asset_id` do `scenes.json`, como `vp numeros` já
  faz. Aprovado com a mídia ausente ou diferente é `AssetError`: reabrir (`vp reopen --step assets --asset <id>`).
- O mesmo id é o mesmo ativo (o id vem do provedor): só se baixa de novo com a mídia ausente ou corrompida.
- `baixar_escolhidos.py` segue com os outros ativos quando um falha e sai com 1 se algum falhou.

## Fora do escopo

`vp assets` (continua stub; os scripts seguem como entrada); a conferência de pessoas, marcas e texto
(`usage_notes`, humana); validação das entradas do kit (G10) e briefs, próximas fatias do RF5.
