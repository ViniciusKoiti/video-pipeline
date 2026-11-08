# Diagnóstico do fluxo de produção (auto-play / Cena e Conceito), 2026-11-07

Só leitura. Branch `serie-conceitos-short-1`, HEAD 09602bb (2026-11-03), 124 arquivos modificados ou novos sem
commit. Comandos rodados: `vp status`, `vp check`, `vp metricas pendentes`, `pytest`, `ruff`, `ffprobe`/`ffmpeg
ebur128` sobre finais já renderizados, `git`, `systemctl --user list-timers`, leitura de uma cópia do SQLite.
Nada foi renderizado, baixado, aprovado, reaberto, agendado ou enviado a provedor. `.env` não foi lido.

Marcação: **[V]** verificado no código, no arquivo ou por comando; **[I]** inferência.

## Resumo

O fluxo trava em dois lugares e perde qualidade em um terceiro. Trava na saída: nenhuma publicação jamais teve
leitura de métrica (zero leituras em 12 `metrics.json`, dez janelas de 7 dias vencidas, cinco ensaios sem
arquivo), e o comando que listaria as pendências quebra por quatro arquivos escritos fora do contrato; a decisão
do §12 "após 4 vídeos" não tem base. Trava também na produção diária de Shorts: a rotina da ADR 036 roda por
timer todo dia às 06:00 e parou no passo 1 em 05, 06 e 07/11 por falta de permissão em sessão não interativa,
com cinco Shorts do plano de novembro sem produção. Perde qualidade no gate 2: os dois últimos ensaios
publicados saíram com o último parecer do verificador "reprovado" e aprovação por `--sem-checagem`, depois de
três rodadas (o teto é dois), com mais de 95% das fichas apoiadas numa fonte só. Em torno disso há três riscos
estruturais: os "checks automáticos" do §4 não existem no código (os ensaios sem trilha saíram a −16 e −17 LUFS,
abaixo dos −14 do alvo, sem aviso); toda a refatoração de novembro e todas as decisões dos episódios vivem num
disco só (56 commits fora da `main`, 55 sem push, `data/episodes` fora do Git); e a documentação descreve
mecanismos que o código não tem ou já abandonou.

## 1. Mapa do fluxo real

| Etapa | Entrada → saída | Quem executa | Estado gravado | Em falha | Tempo / custo |
|---|---|---|---|---|---|
| Pauta, molde, partitura | tema do dono → `pauta.md`, `molde.json`, `partitura.md` | dono + skills `analise-de-formato`/`pauta` | nenhum | — | tokens do plano |
| Fontes | URL/arquivo → `sources.json`, `sources/*.txt`, `excerpts/*.md` | `vp sources add\|declared`, `vp excerpts` | nenhum (sem manifest) | nada escrito, exit 1; PDF ruim dá traceback [V `app/commands/sources.py:51`] | segundos; sem limite de tamanho [V `app/providers/http.py:132`] |
| Fichas | trechos → `facts.json` | agente `pesquisador` (opus) | nenhum | `vp check` acusa citação não literal [V `check.py:152`] | kira: ~US$ 6 equiv. |
| Gate 1 | `sources.json`+`facts.json` → `review.json` | dono, `vp approve --step sources` | hash dos dois JSON [V `gates_constants.py:14`] | não exige `vp check` [V `gates.py:110-152`] | — |
| Roteiro | fichas → `outline.md`, `scenes.json` | agente `roteirista` (HEAD `fable`, árvore `sonnet`) + `humanizer` | nenhum | `vp check`: erros bloqueiam exit, alertas não [V `cli.py:90-97`] | kira: ~US$ 5 |
| Checagem | roteiro → `checagem.json` | agente `verificador` (haiku) + `vp checagem` | parecer com hash | gate 2 exige parecer aprovado atual **ou** `--sem-checagem` [V `gates.py:129-135`] | death-note: 36 pareceres; depois da regra: 3–8 |
| Gate 2 | `scenes.json`+`outline.md` → `review.json` | dono | hash (sem `asset_id`, sem bloco numérico) | — | g1→g2: 2 h a 65 h |
| Imagens | plano → `candidatos/`, `assets/*.json` | skill `plano-de-imagens`, `vp assets search\|take` (Pexels, Pixabay, Unsplash; Commons/LoC/Flickr à mão, sem adapter [V `bootstrap/archives.py:21`]) | `review_status` no JSON | banco falho registrado; nenhum banco = erro | 9 a 53 ativos por ensaio |
| Gate 3 | mídia → `review.json` por ativo | dono | sha256 da mídia | `usage_notes` obrigatório | — |
| Trilha | roteiro + catálogo → `music.json` | agente `diretor-musical` (haiku) | nenhum | sem `music.json` nada cobra [V `check.py:580-582`] | 3 de 9 ensaios sem trilha |
| Voz | `scenes.json` → `voice/*.wav`, `voice/leveled/` | `vp voice`/`vp render` → `chatterbox_modal` (T4) | `manifest.json` só `steps.voice` [V `voice_state.py`] | fala pendente, retomada; `VoiceIncomplete` para o render | segundos por cena; crédito do Modal fora do código |
| Legendas | WAVs → `captions.srt`, `.key`, `.old.srt`, `.words.json` | código (Groq só com `--legenda-palavra`) | — | SRT inteiro refeito quando o nome de **um** WAV muda [V `captions.py:216-243`] | — |
| Montagem e render | `episode.json` → `renders/preview.mp4` ou `final.mp4` | `vp render`, Remotion por cena + ffmpeg | nenhum no manifest | final exige `review_status` aprovado no JSON do ativo (sem sha) [V `assembly.py:60-74`] | prévia 720p/10 cenas: ~4 min sem cache; final 1080p/12 min: ~1h46 (montaigne, `publicacao.md`) |
| Miniatura e textos | → `miniatura/`, `description.txt`, `credits.txt`, `comentario-fixado.txt`, `post.json` | skill `miniatura` + à mão; só o bloco de livros é código (`vp export livros`) | fora do carimbo do gate 4 [V `gates_constants.py:18-20`] | — | miniatura refeita: US$ 5,86 no kira |
| Gate 4 | render + `episode.json` + `captions.srt` + `legenda-post.txt` → `review.json` | dono, `vp approve --step preview` | hash | não exige gates 1–3, `vp check`, trilha nem descrição; exige `medicao.json` limpo se existir | g1→g4: 2,8 h a 65,8 h, mediana 11,6 h |
| Publicação | `post.json` → `registro.jsonl` → Postiz | `vp postiz upload → pacote → duvida-cega → duvida → schedule` (regra `ask`) | `registro.jsonl` termina em `agendado` | pacote bloqueia 404 e gate 4 inválido; schedule exige "segue" | 44 agendados, 44 com dúvida antes |
| Studio e métricas | à mão → `publicacao.md`, `metrics.json` | dono, `vp metricas` | `metrics.json` | `vp metricas pendentes` quebra [V] | 0 leituras |
| Short técnico | pauta → medição Java → roteiro → `narracao.*.json` → `content.*.json` → `vp short voz\|tempos\|sfx\|juntar` → `vp audio` → `vp short gate` → Postiz | rotina `short-diario` (timer systemd, `claude -p`, sonnet) | `manifest.json` voz; `renders/pacote.json` | parou em 05, 06 e 07/11 por permissão | US$ 0,4 a 1,1 equiv./dia |

## 2. Problemas, do mais caro ao mais barato

### 1. O laço de métricas nunca fechou e o comando que o cobra está quebrado
- **Classe:** falha silenciosa + passo manual repetido.
- **Evidência [V]:** `uv run vp metricas pendentes` sai com traceback `ValidationError` (`app/pipeline/metrics.py:74`
  via `all_metrics`): `short-lista-ligada-{pt,en}` e `short-idempotencia-java-{pt,en}` têm `format: "short"`
  (schema aceita `longo|reel|clipe|story`, `app/pipeline/models/_schemas_types.py:148`), `hypothesis` como objeto e
  `requests` com `due/reading`. Foram escritos à mão: nenhuma skill escreve `metrics.json` e `vp metricas iniciar`
  não aceita Short. Leituras: zero em 12 arquivos; d7 vencida em 10 (death-note 27/10, kira 28/10, historia 29/10,
  epicteto 30/10, confeitaria ×3, lista-ligada ×2, clipe Nabote); `hypothesis` nula nos 7 válidos; sem arquivo em
  montaigne, manipulacao, estoicismo, ayanokoji-ser-parecido e ayanokoji-provocacao.
- **Impacto:** a estratégia do canal (4 vídeos no recorte, decisão aos 28 dias) não tem dado; as d28 dos quatro
  primeiros ensaios vencem entre 17 e 20/11 e também vão passar em branco.
- **Teste:** rodar `uv run vp metricas pendentes`. Decisão de dado a tomar: acrescentar `short` ao `PublicationFormat`
  ou regravar os 4 arquivos como `reel` com `hypothesis` em texto; depois `vp metricas ler d7` nas 10 vencidas.

### 2. Gate 2 aprovado por cima do verificador nos dois últimos ensaios; teto de 2 rodadas sem rastro
- **Classe:** risco de qualidade + regra ambígua.
- **Evidência [V]:** `ayanokoji-provocacao-epicteto`: 5 pareceres, todos `rejected`; gate 2 aprovado duas vezes com
  `--sem-checagem` (notas: "rodadas 1 a 3 ... o dono autorizou a rodada 3"; "S25 e S30 corrigidos depois,
  conferidos por busca"); `vp status` mostra "parecer verificador reprovado · vale". `ayanokoji-ser-parecido`: 3
  pareceres `rejected`, aprovado com `--sem-checagem`. Pareceres gravados depois da regra de 2026-10-24:
  montaigne 4, manipulacao 6, estoicismo 8, ayanokoji-ser-parecido 3, ayanokoji-provocacao 5; nada registra
  "rodada", só pareceres. Fichas com uma fonte só: manipulacao 100/115, ayanokoji-ser-parecido 137/151,
  ayanokoji-provocacao 121/126, com 4 das 9 fontes na Wikipedia. `vp checagem` aceita qualquer JSON com
  `verdict` (`check_report.py:12-19`). A regra §6 "≥ 2 fontes independentes" não é código, só alerta por ficha.
- **Impacto:** o canal publica com a última palavra do verificador contrária, exatamente o risco §2.2. [I] O
  verificador em `haiku` desde 24/10 coincide com o aumento de rodadas e pareceres contrários; não há medição.
- **Teste:** uma rodada só-leitura do verificador sobre o `scenes.json` publicado do ayanokoji-provocacao; e
  `grep -c '"rejected"' data/episodes/*/checagem.json`.

### 3. Rotina diária de Shorts roda por timer e falha há três dias, enquanto o CLAUDE.md diz que está desligada
- **Classe:** gargalo + documentação desatualizada + risco de custo.
- **Evidência [V]:** `systemctl --user list-timers` → `short-diario.timer` diário 06:00; `deploy/rotina/short-diario.sh:19`
  roda `claude -p "/short-diario" --model claude-sonnet-5-5`; `data/rotina/2026-11-0{5,6,7}.md`: "parou no passo 1",
  `java` e `.venv/bin/vp` pedem aprovação; o comentário do script (linha 17) diz que as permissões vêm de
  `.claude/settings.json`, mas a allowlist está em `settings.local.json` e não tem `java`, `vp short`, `npx`,
  `ffmpeg`. Custo registrado nos `.log`: 0,37 a 1,06 US$ equiv./dia. CLAUDE.md §15: "ADR 036, proposta; timer
  desligado e a skill short-diario ainda por criar"; ADR 036 l.3-5: aceita em 2026-10-31, timer ligado.
- **Impacto:** rate limiter (14/11), consistent hashing (16/11), HashMap, cache e GC sem produção; `fila.md`
  desatualizada; o circuit breaker produzido em 05/11 espera revisão.
- **Teste:** `journalctl --user -u short-diario.service -n 20` e uma execução interativa de `/short-diario`.

### 4. Os "checks automáticos" do §4 não existem; ensaio sem trilha sai fora do alvo de volume
- **Classe:** risco de qualidade + documentação desatualizada.
- **Evidência [V]:** sem trilha, a junção faz só `-c:a aac -ac 2` (`app/render/ffmpeg.py:330-357`); loudness medida só
  se há `music` (`app/commands/render.py:139`). Medido nos finais: kira −16,5 LUFS, death-note −17,0, ayanokoji-provocacao
  −16,1 (sem trilha) contra epicteto −14,1 (com trilha). "Duração = voz", "áudio presente", "silêncio longo" e
  "16:9 no arquivo" não existem (grep em `app/`: `silencedetect` só em legendas e `speech_bounds` do Short; o
  render só mede `duration_ms`). O gate 4 exige só a existência do MP4 (`gates.py:249-254`).
- **Impacto:** 3 de 9 ensaios publicados 2 a 3 LU abaixo do alvo; um MP4 mudo passaria ao gate 4 só pela escuta.
- **Teste:** `ffmpeg -i renders/final.mp4 -af ebur128 -f null -` (feito); `ffprobe -show_streams` + `silencedetect=d=3`.
- **Não é problema aqui:** a duração do MP4 bateu com a soma das cenas nos três medidos.

### 5. Trabalho e decisões num disco só
- **Classe:** dívida técnica + risco operacional.
- **Evidência [V]:** `main` parou em 2026-10-31 (#217); 56 commits só na branch (RF0–RF7, ADRs 039–054), 55 sem
  push (`origin/serie-conceitos-short-1` tem 1 commit); 124 arquivos sem commit, 40 deles código ou config
  (`voice_polish.py`, `numbers_citations.py`, `schemas.py`, `providers.toml`, `video/src/*`); tarball
  `viniciusk-motion-kit-0.7.1.tgz` apagado e `@viniciuskoitin/motion-kit` 0.9.0 untracked (ADR 027 violada até o
  commit); ADR 055 e emendas da 007 e 054 só na árvore; `.gitignore:15` exclui `data/episodes/*` → `review.json`,
  `checagem.json`, `publicacao.md`, `scenes.json` de todos os episódios (20 GB) estão fora de qualquer repositório;
  `custo-death-note-fins-meios-20261019.md`, base do "~US$ 220", não existe. Worktree `numeros-rebase` com commit
  não integrado.
- **Impacto:** perda do disco apaga a trilha de gates e a refatoração; `git diff` de qualquer PR novo é ilegível.
- **Teste:** `git log --oneline origin/serie-conceitos-short-1..HEAD | wc -l` → 55; `git ls-files data/episodes | wc -l` → 1.

### 6. "Todo ensaio longo leva trilha" existe só em texto não commitado e nada cobra
- **Classe:** regra ambígua.
- **Evidência [V]:** CLAUDE.md §15 e skill `trilha` (diff não commitado); ADR 030 diz `music` opcional;
  `episode_build.py:116-119` e `check.py:579-582` ignoram a ausência; `vp status` não mostra. ayanokoji-provocacao
  (04/11, regra em vigor) sem `music.json` e sem uma palavra sobre trilha em `outline.md`/`pauta.md`/`publicacao.md`;
  kira idem (anterior à ADR 030); death-note tem a decisão registrada (`outline.md:551`).
- **Impacto:** o item 4 (volume) é consequência direta.
- **Teste:** `grep -il "trilha\|música" data/episodes/<id>/*.md` antes do gate 4; `python -c` lendo `episode.json["music"]`.

### 7. Gates independentes, render ignora o review e proteção parcial
- **Classe:** falha silenciosa (latente: não explorada nos 9 publicados).
- **Evidência [V]:** `record_decision` só verifica pré-requisito no gate 2 (`gates.py:110-152`): gate 4 e `vp postiz`
  passam sem gate 2 válido (`postiz_cadeia.py:86-97`); `vp render`/`vp voice` leem `scenes.json` direto
  (`render.py:45`, `voice.py:37`); render final confere `review_status` do JSON do ativo, não o sha nem a decisão
  (`assembly.py:60-74`); gate 1 não carimba `sources/*.txt`; `captions.srt` só é pendência no vertical
  (`gates.py:244-245`); `description.txt`, `credits.txt`, `music.json`, `post.json`, `miniatura/` sem proteção;
  `vp numeros --escrever` e `vp excerpts` escrevem fora do guard e sem lock.
- **Impacto:** roteiro alterado depois do gate 2 pode ser renderizado e agendado; `vp status` diria "MUDOU", nada bloqueia.
- **Teste:** num episódio de teste, aprovar `script`, trocar uma palavra da narração, `vp render --no-render` grava `episode.json`.

### 8. Decisões assinadas por `test`
- **Classe:** regra ambígua + falha silenciosa.
- **Evidência [V]:** 15 `review.json` com `"reviewer": "test"`; gate 4 de `estoicismo-mulheres-inabalavel`,
  `ayanokoji-ser-parecido`, `short-lista-ligada-{pt,en}` e gate 2 do estoicismo ×2; `reviewer.py:19-23` só avisa e segue.
- **Impacto:** a trilha de quem aprovou não vale como prova.
- **Teste:** `grep -l '"reviewer": "test"' data/episodes/*/review.json`; `VP_REVIEWER` no `.env` [I: não lido].

### 9. Depois de "agendado" ninguém registra nada
- **Classe:** passo manual repetido + risco de política.
- **Evidência [V]:** `registro.jsonl` tem só `upload`, `pacote`, `duvida`, `agendado` (57/79/56/44); nenhum evento
  "publicado", "ERROR" ou "Studio conferido"; os 9 `publicacao.md` listam a rotina do Studio e nenhum marca feito;
  rótulo de conteúdo sintético: "não marcar" em death-note, kira e historia, "decidir no Studio" nos demais;
  `schedule` não impede reenviar o mesmo hash já agendado (`postiz_cadeia.py:204-235`), só a fila `QUEUE` ±1 dia do Postiz.
- **Impacto:** o caso ayanokoji-ser-parecido (post de 31/10 não saiu) só foi pego à mão; rótulo de IA inconsistente
  entre vídeos do mesmo canal.
- **Teste:** `vp postiz posts --start --end` da semana e cruzar `postId` com os `agendado`.

### 10. Música no Short misturada fora do pipeline e agenda fora do plano
- **Classe:** passo manual + risco de política + irreprodutível.
- **Evidência [V]:** `final.pt.musica.mp4` e `final.en.musica.mp4` agendados em 07/11 para 08/11 17h; `vp short juntar`
  não aceita música (`short_mix.py:20-58`); nenhum script ou log da mistura; o `plano-animacao.md` dizia "mistura
  pendente"; plano de novembro marcava idempotência para 18/11 12h; canal pt com Shorts em 07, 08, 09 e 11/11; a
  dúvida cega apontou os dois riscos e seguiu; `fila.md` desatualizada.
- **Impacto:** volume final não medido; três Shorts por semana vira quatro em cinco dias (§12 "repetitivo").
- **Teste:** `vp audio renders/short-idempotencia-java/final.pt.musica.mp4 --episodio short-idempotencia-java-pt` (pede o dono e a sonda).

### 11. Regerar um WAV substitui o `captions.srt` inteiro e descarta a revisão humana
- **Classe:** falha silenciosa.
- **Evidência [V]:** chave = nomes de todos os WAVs (`captions.py:216-219`); chave diferente → SRT atual vira
  `captions.old.srt` (um backup só) e o gerado entra. `death-note-fins-meios` tem `captions.antes-revisao*.srt`,
  `captions.revisada-v1.srt` e tamanhos/horários compatíveis com restauração à mão [I].
- **Impacto:** ligar `voice_polish`, mudar glossário ou política de nivelamento troca o nome dos WAVs e dispara isso.
- **Teste:** editar um bloco do SRT num episódio de teste, mudar uma palavra, `vp render --no-render`, comparar.

### 12. Alertas do `vp check` não têm destino
- **Classe:** risco de qualidade.
- **Evidência [V]:** `vp check` sai 0 com qualquer número de alertas e `vp status` não os mostra; montaigne 116 alertas,
  ayanokoji-provocacao 123, kira 25 (18 de "uma fonte só"); `visual_need_violations` (§2.4) nunca é chamada em `app/`.
- **Teste:** `vp check <id> | grep -c alerta` antes de cada gate.

### 13. Gate `translation` ausente em Shorts agendados e `vp approve` sem o marcador do pacote
- **Classe:** falha silenciosa.
- **Evidência [V]:** `short-idempotencia-java-en` e `short-completablefuture-java-en` têm `traducao.json` mas o
  `review.json` só tem `assets`/`preview`; nada exige `translation` antes do `preview` ou do `postiz`;
  `vp approve --step preview` não consulta `package_problems` (só `postiz_cadeia.py:96`).
- **Teste:** `uv run vp traducao short-idempotencia-java-en`.

### 14. Custo sem medição atual
- **Classe:** risco de custo.
- **Evidência [V]:** relatório do kira (20/10) assume tudo Opus, coerente com `model: inherit` daquela data; desde
  24/10 verificador e diretor-musical em `haiku`, dúvida cega `sonnet`, roteirista `fable` no HEAD e `sonnet` +
  `effort: xhigh` na árvore sem emenda da ADR 009; `data/telemetry/usage.sqlite3` existe desde 24/10 com 0 linhas em
  todas as tabelas; sem importador no repo.
- **Impacto:** nenhuma base para a conta "US$ 25 a 50 por vídeo" nem para julgar a troca de modelos.
- **Teste:** `sqlite3 data/telemetry/usage.sqlite3 'select count(*) from requests'` → 0.

### 15. Provedores: tetos que só existem no texto
- **Classe:** risco de custo ou cota + dívida.
- **Evidência [V]:** `chatterbox_modal` declara `usd_per_call=0` e nenhum controle de crédito ou tempo de GPU
  (`chatterbox.py:50`, `deploy/modal_chatterbox.py:46-51`); erro do Modal vira `ProviderError` genérico, nunca
  `QuotaExhausted`, então cada fala restante ainda chama (`chatterbox.py:167-175`, `speech_batches.py:69-78`);
  `--legenda-palavra` em 16:9 envia o áudio à Groq e o render não usa (`render.py:70` × `remotion.py:241`);
  `limits.max_cloud_requests_per_episode` e `quota.json` dos bancos sem leitor; Gemini 10/dia só em docstring;
  `scripts/bench/earshot_retry.py` (Gemini) e `scripts/provisorio/gerar_imagens_klein.py` (Workers AI, `requests`
  não declarado no `pyproject.toml`) chamam remoto fora das portas e do `ensure_free`.
- **Teste:** teste unitário com worker falso devolvendo `{"ok": false}` para 3 falas e contar chamadas.

### 16. Documentação que descreve outro sistema
- **Classe:** documentação desatualizada.
- **Evidência [V]:** §15 ADR 036 (item 3); §7 "Chatterbox local" como voz final × `providers.toml` `chatterbox_modal`;
  §4 checks (item 4); §5 descreve `state.py` (`pending → running → ...`, cache por `input_hash`, `.lock` em
  `run_step`) que não tem chamador fora dos testes; ROADMAP "Etapa atual" (30/09) com seis pendências já feitas
  (`reopen`, `vp assets`, glossário, legendas, "nenhum vídeo publicado", scripts → vp); ADRs 030–050 citam
  `montar_episodio.py`, `shorts_tec.py`, `conferir_audio.py`, `catalogo_musica.py` removidos em 01/11; ADRs 002, 003
  e 005 citadas e inexistentes; mermaid "ADRs 001 a 052"; `renders/evolucao/` não existe; `npm run render` aponta
  para composição `Episode` inexistente; README "cinco skills" (há 16); permissões mortas em `settings*.json`
  (`publish.py` de scratchpad, `shorts_tec.py`, `conferir_audio.py`); `image-personagem-*.png` e `mermaid.txt` na raiz.

### 17. Código morto e duplicado
- **Classe:** dívida técnica.
- **Evidência [V]:** `run_step`, `run_scenes`, `for_each_scene`, `StateConstants.TRANSITIONS`, `protected_outputs`
  sem uso em `app/` ou `scripts/`; `pdftotext` e `ValueError` de `resolve_music`/`shot_bounds` fora do contrato da ADR
  045 (traceback); dois parsers de SRT, dois `silencedetect` com limiares diferentes, duas normalizações de áudio;
  `check.py` com 654 linhas; `is_approved_json` devolve `False` em JSON corrompido e deixa sobrescrever.

### 18. Cache do Remotion zerado e vídeo-régua sem versão
- **Classe:** gargalo + regra não cumprida.
- **Evidência [V]:** `template_hash` cobre `video/src`, `package-lock.json` e o kit (`remotion.py:39-44`); tudo isso
  mudou sem commit → o próximo `vp render` de qualquer episódio refaz todas as cenas; o §1 pede versão `vN` da
  régua a cada PR de visual e `renders/evolucao/` não existe.

### 19. Download de fonte sem limite
- **Classe:** risco operacional menor.
- **Evidência [V]:** `http.py:124-141` copia tudo; `sources.py:56` lê em memória; sem `Content-Type`; `/tmp` do WSL é RAM.

## 3. Lacunas já documentadas que continuam abertas

Do `pipeline-hoje.mermaid` (01/11) e do CLAUDE.md, todas confirmadas [V]:
- `vp new`, `script`, `scenes`, `gallery` e `subs` respondem "não implementado"; `vp export` só tem `livros`;
  créditos sem comando (e nada lê `attribution_text` dos ativos para gerar `credits.txt`).
- Tradução do longo: `translation.py` lê `narracao.json`, não `scenes.json`; só Shorts têm `traducao.json` (9).
  "Pronta e nunca usada" é otimista: para o longo não existe.
- Música no Short sem ducking nem entrada no `juntar`; grade de batidas do earshot usada só no resumo do `vp audio`.
- Pós-publicação só como risco listado no pacote.
- Instante de entrada dos cartões no kit a olho (SFX por deslocamento).
- SFX só nos Shorts (ADR 035); o piloto `lista-ligada-pt` publicou `final.mp4`, não `final-sfx.mp4`.
- ADR 010 (busca por vetor) sem arquivo; agente `revisor-de-risco` inexistente; #11 e M2–M7 em pausa; ADR 017 parte
  B, ADR 031 E, ADR 033 melhorias, ADR 034 adapters de prova e ADR 035 escuta do dono pendentes.
- OCR dos quadros: proposta de limiar 1,0 não aprovada; `text_fit.py` segue estimando por contagem de caracteres.
- Workers AI: porta `image_gen` sem adapter; geração vive em `scripts/provisorio/gerar_imagens_klein.py`.
- Commons, Library of Congress e Flickr Commons sem adapter (cascata §8 depende da mão).

## 4. O que não é problema

- `uv run pytest`: 1544 passaram em 3 min 52 s na árvore atual; `ruff check .` limpo [V].
- Cadeia do Postiz íntegra até "agendado": 44 agendamentos, 44 com dúvida cega antes, nenhum com último parecer
  "não segue", nenhum hash agendado duas vezes; gate 4 anterior ao primeiro agendamento nos 9 ensaios [V].
- Nenhum ativo `needs_review` entrou num `episode.json`; nenhuma mídia faltando; `Citacao` dentro de 10 quadros e
  8 s em todos (clipes longos só no ayanokoji-provocacao, cobertos pela emenda de 03/11) [V].
- Divulgação de voz clonada por IA nas 9 descrições; créditos e licenças nos 9 `credits.txt`; afiliado com aviso
  nos 8 com `livros.json` [V].
- Segredos: nenhum log de header ou URL; `TransportError` sem URL; `cookies.txt` ignorado e não commitado; o Modal
  nunca recebe a gravação, só nome e hash [V].
- Voz: falha de fala não derruba o episódio, retomada só do que falta, WAV substituído só depois de pronto; hash
  cobre glossário, referência e entrega [V].
- Citação literal das fichas é conferida de fato; claims obrigatórias em tudo que aparece na tela; aritmética de
  `calculation`/`receipt` refeita; aprovação cai sozinha quando o conteúdo muda [V].
- Ausência de `manifest.json` nos ensaios antigos é esperada: só a voz o grava desde 01/11 (ADR 052) [V].
- death-note sem trilha tem decisão registrada; 36 rodadas e kira sem trilha são anteriores às regras [V].
- Os `postiz-*.err` vazios são redirecionamentos da sessão, não erro [V].
- `vp status` e `vp check` tratam `metrics.json` inválido sem quebrar [V].
- Relatório de custo do kira é coerente com `model: inherit` da data; só não serve de base hoje [V].
- Todos os comandos e flags `vp` citados em skills, README e docs existem [V].

## 5. Limites

- Não rodei render, provedor, `vp medicao`, `vp traducao`, `vp audio` nem `gh`; "medição limpa" dos Shorts e o
  conteúdo dos problemas remanescentes dos pareceres ficam sem conferir.
- `.env` não lido: `VP_REVIEWER` ausente é inferência pelos reviewers gravados.
- Precedência entre `allow Bash(.venv/bin/vp postiz *)` (local) e `ask Bash(* postiz schedule *)` não testada;
  o mesmo vale para `allow Bash(.venv/bin/vp approve *)`, que permite a um agente aprovar gate sem prompt [I].
- "Rodada" do verificador não é gravada; contei pareceres.
- Mistura de música e SFX nos Shorts publicados: inferida por nomes de arquivo e pelo earshot, sem log.
- Custo por agente não é mensurável: `usage.sqlite3` vazio; só o relatório de 20/10.
- Horas humanas por episódio nunca registradas; usei horários dos gates.
- MCP `motion-kit` fora do ar nesta sessão: o template não foi conferido contra o kit.
- Worktree `numeros-rebase` não inspecionado além do commit.

## 6. Conferências adicionais a pedido do dono (mesmo dia)

**`vp medicao` em 18 Shorts** (idempotência pt/en, virtual threads pt/en, circuit breaker pt/en/ig, CompletableFuture
pt/en, índices SQLite pt/en, lista ligada pt/en, memory leak pt/en/ig, concorrência-fluxo pt/en): **todos "sem
problemas"** [V]. Só avisos de "número declarado e não usado na fala nem na tela"; no CompletableFuture os
declarados sem uso são 501, 309 e 309,5, que são os números centrais da lição: vale conferir se a fala os diz em
outra forma ("meio segundo"). Isso fecha o limite "medição limpa não verificada".

**`vp traducao` nas 10 pastas traduzidas**: 9 "sem problemas" [V]; `short-memory-leak-ig` está em inglês, derivado do
pt, e **não tem `traducao.json`**, logo nunca passou nem pode passar pelo gate `translation` (o
`short-circuit-breaker-java-ig` tem). Para `short-idempotencia-java-en` e `short-completablefuture-java-en`
(item 13) o conteúdo está íntegro; falta só a decisão no `review.json`.

**Precedência de permissões** (documentação oficial do Claude Code, páginas `permissions`, `settings`, `headless`,
`hooks`, lidas por agente; nenhuma configuração alterada):
- A ordem é **deny → ask → allow, por tipo de regra, em qualquer arquivo**; as listas de `allow` se somam e o
  `allow` do `settings.local.json` "não outranks um ask rule de um arquivo de projeto". Logo `ask
  Bash(* postiz schedule *)` prevalece sobre `allow Bash(.venv/bin/vp postiz *)`: em sessão interativa pede
  confirmação; em `claude -p` (a rotina) o que cai em `ask` é **negado**. O agendamento está protegido como a ADR
  025 pretende, tanto por `.venv/bin/vp` quanto por `uv run vp` (o `*` inicial casa qualquer programa).
- **`allow Bash(.venv/bin/vp approve *)` não tem `ask` correspondente**: em sessão interativa ou na rotina, um
  agente aprova gate 2, 3, 4 ou tradução sem prompt; a única barreira é o texto da skill `short-diario` ("nunca
  `vp approve`"). Um hook `PreToolUse` que saia com código 2 bloqueia mesmo com `allow` e recebe `agent_id` quando
  a chamada vem de subagente; é o único mecanismo que distingue agente de dono.
- Rotina em `claude -p`: `Bash(uv run *)` está liberado, então `uv run --no-sync vp ...` rodaria; o bloqueio de
  05–07/11 veio de `java`, `javac`, `mkdir` fora de `renders/*`, `npx` e `.venv/bin/vp` sem subcomando liberado.
  O comentário do `short-diario.sh:17` aponta para o arquivo errado (`settings.json`); a allowlist que vale é a do
  `settings.local.json`. Decisão do dono: ampliar a allowlist local ou rodar a rotina interativamente.
- Regras `allow` para script inexistente (`publish.py` de scratchpad) não têm efeito enquanto o arquivo não
  existir; se algo recriar o caminho, roda sem prompt. `/permissions` mostra cada regra e seu arquivo de origem.
