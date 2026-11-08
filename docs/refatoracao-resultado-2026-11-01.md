# Refatoração SOLID: o que ficou (2026-11-01)

Resumo do que a refatoração RF0–RF7 deixou no código, de como estender e do que continua aberto. Substitui as
análises de 2026-10-31 (gaps, scripts, tamanho dos módulos e desenho em objetos), removidas ao fim do RF7:
estão no Git (ver o fim deste documento). O registro de cada fatia, com os critérios e as provas, continua em
[fluxo-refatoracao-solid-2026-11-01.md](fluxo-refatoracao-solid-2026-11-01.md); as decisões, nas ADRs 037–052.

## 1. A estrutura de hoje

| Camada | Pasta | O que tem | Regra (guarda em `tests/`) |
|---|---|---|---|
| Entrada | `app/cli.py`, `app/commands/` | `HANDLERS` + `build_parser`; um módulo por verbo (`add_arguments` e `run`) | só orquestra; erros esperados sobem para `app.commands.errors.run` (ADR 045) |
| Composição | `app/bootstrap/`, `app/settings/` | monta o `Context` e escolhe os adaptadores por `config/providers.toml` | só aqui se conhecem adaptadores concretos (`test_architecture`) |
| Domínio | `app/pipeline/` | schemas, `check`, gates, proteção, voz, montagem, pacote, fontes, ativos, Short | só conhece portas; não importa adaptador nem `app.settings` |
| Mídia | `app/media/` | ffprobe, loudness, legenda, narração, envelope, mixagem, earshot | usa só `models` e `schemas` do pipeline |
| Adaptadores | `app/providers/`, `app/render/`, `app/storage/` | um por provedor, motor ou armazenamento | recebem parâmetros explícitos |

Cada arquivo de `app/` tem até 200 linhas de código e cada função até 50 (`tests/test_tamanho_modulos.py`, com
catraca em `tests/baseline_tamanho_app.json`). Modelos ficam um por arquivo em `app/<área>/models/` (ADR 037) e
constantes em classes `*Constants` com `Final` (ADR 038). Todo erro esperado herda de `PipelineError`.

## 2. Como estender

- **Comando novo:** módulo em `app/commands/<nome>.py` com `add_arguments(parser)` e `run(args, context)`,
  registrado em `HANDLERS` e em `build_parser` (`app/cli.py`); a lógica vai para um serviço em `app/pipeline/`.
  Teste pelo caminho real: parser + `HANDLERS` + `app.commands.errors.run` (exemplos: `tests/test_short_command.py`,
  `tests/test_audio_command.py`).
- **Provedor novo:** adaptador em `app/providers/<função>/<provedor>.py` + registro em `app/bootstrap/__init__.py` +
  passar em `tests/test_contracts.py` + uma linha em `config/providers.toml`.
- **Escrita de arquivo de episódio:** pelo `ManifestStore` e, onde há gate, pelo `ReviewWriteGuard` (ADR 039); o
  aprovado só se libera com `vp reopen`.
- **Etapa por cena:** `scene_step` (ADR 040); a voz grava o relatório por cena no `manifest.json` (ADR 052).
- **Antes de commitar:** `bash scripts/check_qualidade.sh` (lint, Mypy estrito em `app/` e a suíte; é o mesmo do
  pré-commit e do CI).

## 3. Dos scripts aos comandos

| Script de `scripts/provisorio/` | Comando | Serviço | ADR |
|---|---|---|---|
| `baixar_fonte`, `fonte_declarada` | `vp sources add\|declared` | `pipeline/sources.py` | 043 |
| `buscar_candidatos`, `baixar_escolhidos` | `vp assets search\|take` | `pipeline/assets.py`, `candidates.py` | 044 |
| `radar_resumo`, `formato_resumo` | `vp briefs radar\|formato` | `pipeline/briefs.py` | 047 |
| `catalogo_musica` | `vp music adicionar\|usar\|listar` | `pipeline/music_library.py` | 047 |
| `livros_afiliado` | `vp export livros` | `pipeline/affiliate.py` | — |
| `metricas` | `vp metricas iniciar\|ler\|pendentes\|tabela` | `pipeline/metrics.py` | — |
| `montar_episodio` | `vp voice`, `vp render` | `voice_production`, `episode_build`, `caption_production`, `assembly` | 049, 051, 052 |
| `shorts_tec` | `vp short voz\|tempos\|sfx\|juntar\|boca\|gate` | `short_voice`, `short_timing`, `short_join`, `short_mouth`, `package` | 035, 048, 049, 050 |
| `conferir_audio` | `vp audio` | `pipeline/audio_review.py` | 035 |

Ficaram como scripts: `evolucao.py` e `sprites_apresentador.py` (`scripts/provisorio/`, ferramentas do dono sem
comando), `checagem_local.py` e `teste_voz_gemini.py` (`scripts/bench/`, medições) e `clipe_tempos.py` e
`clipe_reconhecer.py` (`scripts/ferramentas/`, letra do clipe do Nabote, feitas uma vez).

## 4. Os gaps de 2026-10-31 e o que os fechou

| Gap | Fechado por | Observação |
|---|---|---|
| G01 aprovação e estado sem a mesma proteção | RF1, ADR 039 | `ReviewWriteGuard` deriva a proteção do `review.json` |
| G02 publicação de arquivos sem garantia uniforme | ADR 041, 050, 051 | WAV atômico (`atomic_wav`), pacote com marcador `writing` até o último arquivo, `episode.json` inteiro ou nada |
| G03 falha parcial impede a retomada | RF2, ADR 040 e 052 | uma rodada refaz só as cenas que faltam |
| G04 contrato TTS e de lote incompleto | RF3, ADR 041 | identidade, impressão digital, lote com corte recusado e fechamento |
| G05 identidade do cache indefinida | ADR 041 e 049 | o nome dos WAVs já gerados **não mudou** (decisão do dono); os valores da entrega clonada não entram no nome |
| G06 comandos independentes × `Production.run()` | ADR 042 e 051 | `vp voice` só gera voz; `vp render` monta e renderiza; sem `Production.run()` |
| G07 `Context` largo e com configuração | RF4, ADR 042 | `Context` declara as capacidades usadas; o núcleo não lê `Settings` |
| G08 `EpisodeFolder` com várias políticas | **não implementado** | a classe não foi criada; o acesso é o `ManifestStore` e os serviços |
| G09 tipos compartilhados no orquestrador | RF0, ADR 037 | modelos em `models/`, uma classe por arquivo |
| G10 modelos sem invariantes | ADR 048 e 046 | entradas do Short e do SFX validadas na leitura |
| G11 contratos de acervo e registro | ADR 043, 044 e 047 | registro de fontes sob lock; ativo aprovado nunca é alterado |
| G12 guardas não acompanham o desenho | RF0, `test_architecture` e demais | arquitetura, modelos, constantes, tamanho, erros e tipagem no gate |

## 5. O que ficou aberto

- **Do dono:** `.claude/settings.local.json` ainda libera `shorts_tec.py` e `conferir_audio.py` por caminho (os
  scripts não existem mais) e não tem regra para `vp short *` nem `vp audio *` (critério 3 do RF7).
- **Não implementado:** `EpisodeFolder` (G08) e o `AudioReviewPlan` do desenho original; os comandos `vp new`,
  `script`, `scenes`, `gallery` e `subs` (respondem "não implementado"; a legenda sai de `vp render`); o `export`
  completo (só `vp export livros`; vídeo, legenda e `credits.txt` não têm comando).
- **Não exercitado:** o earshot de verdade (`vp audio` só com pedido do dono e a sonda de CPU), o render real
  (Remotion) depois do RF6 e o vídeo-régua (`evolucao.py gerar`, que agora chama `vp render --preview`).
- **Documentação:** o `svg/arquitetura-atual.svg` segue o de 22/10 até o `plantuml` rodar sobre a fonte nova.
- **Passo a passo de cada fatia:** o documento de fluxo guarda as provas com dado real (voz, `episode.json`,
  pacote do gate, junção, cortes do `vp audio`).

## 6. Decisões (ADRs 037–052)

037 modelos por área · 038 constantes por área · 039 proteção de escrita pelo `review.json` · 040 etapa por cena
com retomada · 041 porta de voz (identidade, lote, ciclo de vida) · 042 operações, contexto e fronteiras · 043
registro de fontes · 044 busca e entrada de ativos · 045 tratamento único de erros (com a emenda do
`ManifestInvalid`) · 046 entradas do SFX · 047 cópias de briefs e catálogo de música · 048 entradas do Short ·
049 `VoiceKey`, biblioteca e narrador · 050 pacote do gate 4 · 051 montagem e render por porta · 052 estado da voz
por cena.

## 7. Onde estão as análises removidas

Os quatro documentos de 2026-10-31 (`analise-gaps-solid`, `analise-scripts-provisorios`, `analise-tamanho-modulos`,
`desenho-orientado-a-objetos`) e o `loop-refatoracao.md` saíram na limpeza de 2026-11-01. Para ler um deles:
`git log --diff-filter=D --oneline -- docs/<arquivo>` acha o commit da remoção, e `git show <commit>^:docs/<arquivo>`
mostra o conteúdo.
