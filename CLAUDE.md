# CLAUDE.md — video-pipeline

> Contexto persistente para o Claude Code neste repositório (lido no início de cada sessão). Curto e factual:
> o que o código, o `--help` e os arquivos já dizem fica fora. Preferências pessoais vão em `CLAUDE.local.md`
> (gitignored). Em conflito, valem `docs/spec-v0.4.md` e os registros em `docs/decisions/`.

## 1. O que é este projeto

Pipeline local, retomável e auditável para produzir vídeos narrados em inglês ou em português (ADR 008; voz por
idioma), 5–7 min, 16:9, H.264/AAC, até 1080p, sobre histórias reais. Cada episódio nasce de fontes verificáveis,
usa imagens de acervo com licença registrada, gera ilustrações apenas para lacunas, narra com TTS e sai como
`final.mp4` + `captions.srt` + `description.txt` + `credits.txt`.
**Publicação é sempre manual, após revisão humana.**

- **Recorte da validação:** expedições e desastres de 1880–1930, janela com fotografia em domínio público,
  jornais digitalizados gratuitos e memórias em DP. Piloto: expedição polar de cauda longa (Greely 1881–84,
  Karluk 1913 ou Belgica 1897–99). Episódio 2 ou 3: expedição sul-americana contada em inglês
  (Roosevelt–Rondon 1913–14), o diferencial do canal.
- **Formato explicativo (em teste, #48):** perfil de "dinheiro e poder" de uma pessoa ou família, no estilo How
  Money Works, com tom crítico e documentado (nem herói, nem vilão). Modelo em
  `docs/pesquisa/modelo-perfil-de-poder.md`. Primeiro caso: Grupo Votorantim / família Ermírio de Moraes, em
  pt-BR. O piloto documentário continua no roteiro.
- **Evitar:** sobrevivência recente (fotos de agência, vira 100% ilustração gerada), true crime,
  Titanic/Hindenburg/Everest 1996 (saturados), Segunda Guerra (oceano de concorrentes).

### Estado atual (2026-10-05)

Nenhum vídeo publicado; nada de produção em escala. Roteiro nas issues #1–#31, #41–#43, #48 e #69–#82.
Histórico, frentes candidatas e passos até publicar: `docs/ROADMAP.md` ("Etapa atual e pendências").

- **Foco (decisão do dono, 2026-09-29):** o vídeo não será publicado por enquanto; o trabalho é o template do
  formato explicativo (`video/`, Remotion + motion-kit), com calma, uma frente por vez. Em pausa: #11 e M2–M7 do
  piloto documentário.
- **Vídeo-régua:** o `votorantim-dinheiro` (conteúdo congelado) ganha uma versão `vN` ao fim de cada PR que muda o
  visual (template ou motion-kit), com a sonda de CPU antes; autorização do dono só para este vídeo. Script
  `scripts/provisorio/evolucao.py` (`gerar`, `guardar`, `comparar`, `lado-a-lado`), vídeos em
  `renders/evolucao/`, registro em `data/benchmarks/evolucao-template.md`. A folha de quadros marca os planos que
  mudaram: um PR de visual deve mudar só os que pretendia.
- **Voz (ADR 016, aceita em 2026-10-12):** Kokoro nos rascunhos (`tts`), voz clonada do dono no vídeo final
  (`tts_final = "chatterbox"`, `montar_episodio.py --voz-final`): Chatterbox local, no ambiente próprio dele
  (`CHATTERBOX_PYTHON` e `CHATTERBOX_REFERENCE` no `.env`), uma cena por vez e ~30 vezes mais lenta que o tempo
  real. A gravação de referência é dado pessoal: fora do Git, nunca enviada a provedor. Licença em
  `data/benchmarks/termos-chatterbox.md`. A Charon do Gemini (ADR 012) segue registrada (`--voz=gemini`; 3 chamadas
  por minuto e **10 por dia** na camada gratuita, termos em `data/benchmarks/termos-gemini-tts.md`) e é a voz do
  vídeo-régua, que não troca de voz.

## 2. Regras inegociáveis (ler antes de qualquer alteração)

1. **Custo zero durante a validação.** `MAX_API_SPEND_USD=0` e `ALLOW_PAID_API=false`. Nunca migrar
   para endpoint pago, comprar créditos ou trocar de modelo por conta própria. O plano do Claude do dono,
   usado pelos agentes das etapas criativas, não conta como API paga (ADR 009). Em 429, cota esgotada,
   modelo ausente ou licença incompatível: registrar o motivo em `review.json`, marcar a etapa como
   `needs_review` e parar **aquela cena**, sem bloquear as demais.
2. **Nenhuma fonte inventada.** O LLM escreve somente a partir de trechos extraídos de fontes reais já
   baixadas em `sources.json`. Toda `claim` tem `source_ids` — **inclusive o que aparece na tela**
   (número, data, citação, cargo, gráfico; ADR 008). Roteiro com claim sem suporte não passa da validação.
3. **Nenhum ativo sem licença registrada entra no render.** Campos obrigatórios em §6. Imagem sem
   licença identificável vai para `needs_review`.
4. **Stock e imagem gerada são ilustração**, nunca "registro" do fato. `visual_need` correto sempre;
   imagem sintética realista de fato histórico exige a divulgação de conteúdo alterado do YouTube.
5. **Revisão humana obrigatória** nos 4 gates: tema/fontes, roteiro, ativos/direitos, prévia/descrição.
   Score de IA não aprova direitos nem autenticidade histórica.
6. **Arquivos com `review_status: approved` são imutáveis para o código.** Nova execução reutiliza,
   nunca sobrescreve.
7. **Segredos só em `.env`** (fora do Git). Adapters não logam tokens, headers de auth nem URLs assinadas.
8. **No MVP não existe:** upload automático, Docker, banco de dados, FastAPI, LiteLLM, framework
   multiagente **no código**, segundo editor visual, render em nuvem. Fichas, roteiro e checagem podem
   ser feitos por agentes do Claude Code definidos no repo; o código só valida (`vp check`, ADR 009).
   **Um motor de render por formato de episódio** (ADR 001): `archival_documentary` com ffmpeg (piloto) e
   `explainer` com Remotion (protótipo da #48).
9. **Nenhuma dependência nova sem justificativa no commit e licença verificada.**
10. **Testes não acessam rede.** Provedores externos são mockados; respostas reais aprovadas viram
    fixtures em `data/cache/`.

## 3. Ambiente

- Windows + WSL2/Ubuntu. Python 3.12 em `.venv` (criado com `uv`; Kokoro exige < 3.13), PyTorch só-CPU,
  `ffmpeg`/`ffprobe`, `espeak-ng`, Ollama local só em `127.0.0.1` (detalhes na ADR 004). Node.js LTS (via `nvm`)
  só para o `explainer`: `cd video && npm ci` instala Remotion, @viniciusk/motion-kit e o Chrome headless pelo lock.
- `scripts/check_env.sh` valida o ambiente; rodar após mudança de máquina ou `.wslconfig`.
- O projeto vive em `~/projetos/auto-play` (filesystem Linux do WSL), nunca em `/mnt/c` ou `/mnt/e`; exports
  frios opcionais em `/mnt/e/VideoPipeline/exports`, copiados após o render.
- O WSL2 limita a memória a 50% do host por padrão. Aqui (host 19,4 GB / 16 threads): `memory=12GB`,
  `processors=12`, `swap=8GB`. Com 8 GB no host, modelo de texto menor ou remoto gratuito. Metas de planejamento:
  16 GB de RAM e 20 GB livres; GPU local não é pré-requisito.
- **Máquina limitada:** apps pesados no Windows derrubam a CPU a ~25%. A sonda `cpu_probe()` de
  `app/pipeline/bench.py` (acima de 0,3 s = limitada) vem antes de benchmark, render longo ou rodada de modelo
  local; medida com a máquina limitada é inválida. Nunca encerrar processos do dono.
- Interfaces de teste só em `127.0.0.1`. Um render por vez; tempo e memória de cada etapa em `data/benchmarks/`.

### Mapa do repositório

`app/pipeline/` etapas, estados e schemas · `app/providers/<função>/` porta (`base.py`) + um adapter por provedor ·
`app/bootstrap.py` único módulo que conhece adapters concretos · `app/render/` motor por formato · `video/` template
Remotion do `explainer` (ADR 008) · `.claude/agents/` e `.claude/skills/` etapas criativas (§15) · `prompts/local/`
prompts para modelo local · `config/providers.toml` implementação por função · `scripts/provisorio/` scripts até
virarem comandos `vp` · `data/episodes/<id>/` (`manifest.json`, `episode.json`, `sources.json`, `facts.json`,
`outline.md`, `scenes.json`, `review.json`, `radar-brief.json`, `pauta.md`, `sources/`, `excerpts/`, `assets/`,
`voice/`, `renders/`) ·
`data/benchmarks/` medições e termos dos provedores · `data/cache/` fora do Git. Variáveis de ambiente: nomes e
exemplos não secretos em `.env.example`.

### Arquitetura (ADR 006, diagrama em `docs/arquitetura.md`)

- Portas e adaptadores: cada função tem um `Protocol` em `app/providers/<função>/base.py` (ou
  `app/render/base.py`); as etapas recebem um `Context` explícito e só conhecem portas.
- Trocar de abordagem = novo adapter + registro em `app/bootstrap.py` + passar em
  `tests/test_contracts.py` + **uma linha** em `config/providers.toml`.
- Todo adapter declara `ProviderInfo(name, remote, usd_per_call)`; custo > 0 é recusado sem
  `ALLOW_PAID_API=true` e `MAX_API_SPEND_USD > 0`. `ProviderError` vira `needs_review` só na cena.
- `tests/test_architecture.py` falha se `app/pipeline/` importar adapter concreto ou biblioteca pesada.

## 4. Fluxo de trabalho

Nos Reels, antes das fontes: resumo do nicho no reels-radar (`radar_resumo.py`) → pauta (skill `pauta`), que o
dono aprova (ADR 018). O resumo é forma, nunca fato; o `vp check` avisa onde o roteiro foge dos padrões dele.
Todo roteiro declara o **objetivo** (`objective` no `scenes.json`, ADR 019): `noticiar`, `explicar` ou `opinar`, de
um a três na ordem em que aparecem, mais a promessa em uma frase. O objetivo e a tese de uma opinião vêm do dono.

Fontes (`sources.json`, ≥ 2 independentes; `vp excerpts` numera os trechos) → fichas `facts.json` (**gate 1**) →
roteiro e planos por cena, com `vp check` e agente verificador (**gate 2**) → busca visual em cascata e galeria
(**gate 3**) → voz por bloco → legendas → montagem e prévia → checks automáticos (abre no ffprobe, duração = voz,
áudio presente, sem silêncio longo, 16:9, nenhuma cena sem ativo aprovado) → prévia e descrição (**gate 4**) →
export. No gate 4, "ajustar imagem" volta à busca visual e "ajustar texto" volta ao roteiro. Depois, upload manual,
métricas aos 7 e 28 dias e a decisão após 4 vídeos no mesmo recorte (§12).
Diagrama completo: `docs/pipeline-flowchart.mermaid`.

## 5. Estados, cache e invalidação

- Estados por etapa em `data/episodes/<id>/manifest.json` (`app/pipeline/state.py`):
  `pending → running → needs_review → approved → completed`, ou `failed` (com o motivo).
- Chave de cache: `(episode_id, step, input_hash)`. O `input_hash` cobre o conteúdo das entradas **e** os
  parâmetros que mudam o resultado (modelo, voz, versão do motor). Hash igual = reutiliza a saída; hash
  diferente = reexecuta, **exceto** etapa `approved`: essa nunca é refeita nem sobrescrita sem
  `vp reopen <id> --step <s> --reason "..."`, registrado no `review.json` (§2.6).
- Uma execução por episódio de cada vez: trava em `data/episodes/<id>/.lock`.
- Invalidação: trocar uma imagem invalida **só** montagem e prévia; alterar texto narrado invalida voz do bloco,
  timing, legendas e render; alterar fonte invalida roteiro e tudo abaixo. Erros de rede, cota ou licença param a
  cena, não o episódio.
- Aprovação humana é registrada por `vp approve <id> --step <step>` (ou `vp reject`) em `review.json`, nunca
  editando `review_status` à mão no manifesto principal. Nos gates feitos por agente ou pessoa, a decisão carimba
  `sources.json` + `facts.json` (gate 1), `scenes.json` + `outline.md` (gate 2) ou o arquivo do ativo (gate 3);
  `vp status` mostra se ela ainda vale (ADR 009, emenda de gates por comando).
- **Modalidade do vídeo** (ADR 001): `app/pipeline/format_decision.py` recomenda o formato pelo tema
  (`vp new`) e pelas cenas (`vp scenes`), com pontuação e motivos; o humano confirma ou troca
  (`step: format`, `choice`). O formato confirmado escolhe o motor de render.

## 6. Contratos de dados (schemas pydantic em `app/pipeline/schemas.py`, ADR 007)

Os campos estão nos schemas; exemplo v1 completo em `tests/fixtures/episodes/pilot-example/`. O que o código não
revela:

- **Cena e planos (ADR 008, 011):** uma cena = um bloco de narração = um WAV, com uma lista de planos tipados
  (tipos em `schemas.py`; método de escolha na skill `roteiro-explicativo`). Cada plano se ancora num trecho da
  narração, e o tempo sai da posição da âncora sobre a duração real do WAV (`app/pipeline/shots.py`). A fonte do
  rodapé sai das `claims` e do `sources.json`; a tela não calcula razão nem soma que não esteja numa ficha.
  Cena sem planos = forma v1 (um plano de foto). `visual_need` ∈ `historical_exact | contextual_stock |
  map_or_graphic | illustrative_reconstruction`.
- **Objetivo (ADR 019):** `objective.kinds` (o primeiro manda na estrutura), `promise` e o campo de cada tipo
  (`event_date`, `question`, `thesis` + `thesis_by`). Opinião é dita como opinião e nunca vira dado na tela;
  notícia com mais de 30 dias gera alerta; roteiro sem objetivo também.
- **`sources.json`:** mínimo de 2 fontes independentes para os fatos principais. `Source.interested` marca fonte
  interessada (fato só com ela gera alerta); fontes com autor em comum (`Source.authors`) contam como uma só.
- **`facts.json` (ADR 009):** as fichas são a única base do roteiro. Cada evidência traz `excerpt_id` (parágrafo do
  texto extraído, `source-01#E7`) e uma `quote` **literal**, conferida pelo `vp check`; `open_questions` guarda o
  que as fontes não respondem. Com `facts.json`, toda afirmação do roteiro cita um trecho fichado.
- **Ativo** (`assets/<id>.json`): só chega a `approved` com licença da lista fechada da ADR 007 (PD, CC0, CC-BY
  incl. 3.0 BR, Flickr-NKCR, Pexels, Pixabay, Unsplash, Coverr, Generated, Original — **sem** CC-BY-SA e NC),
  `sha256`, e `usage_notes` para domínio público ou `author` + `attribution_text` para CC-BY. Ativo de banco de
  imagem leva a licença do próprio banco (ou CC0), `author`, `attribution_text` e, em `usage_notes`, a conferência
  de pessoas, marcas e texto (emenda de bancos de imagem). Imagem gerada tem também `generation`.
- **`review.json`:** fonte única das decisões humanas; entradas só acrescentadas, com `input_hash` do conteúdo
  revisado (mudou o conteúdo, a aprovação cai) e `choice` quando o humano troca a recomendação.
- **`episode.json`:** contrato do render; **mudar exige nova ADR**. É a única entrada do motor de montagem; se o
  motor for o Turbo, um adapter converte este arquivo para os parâmetros dele, nunca o contrário. Versão 1 (um
  visual por cena, ADR 001) ou 2 (planos contíguos, ADR 008); `language` `en` | `pt-BR`; `format` decide o motor;
  cenas com `start_ms`/`duration_ms` medidos da voz real e sem sobreposição.
  Apresentador opcional (`host`, só `explainer`; ADR 013): personagem Notionists (CC0) numa janela flutuante que
  muda de canto a cada cena; o canto sai de `app/media/host.py` e a boca, do áudio da cena. Pele `dono` (ADR 017,
  parte A): `"host": {"skin": "dono"}`, com 12 imagens e um `origem.json` em `host/dono/` da pasta do episódio
  (dado pessoal, fora do Git); sem o registro de origem o render para.
  Perfil vertical 9:16 (`orientation: portrait` em `scenes.json`, só `explainer`; ADR 014): 1080×1920, prévia
  720×1280, só `photo`, `broll`, `number`, `keyword`, `stamp`, `lower_third`, `compare` e `chart` (os outros planos
  são erro de validação), legenda queimada no final e área segura das plataformas para legenda, fonte, tarja e janela.

## 7. Provedores e política de escolha

| Função | Padrão | Candidato a teste | Critério de troca |
|---|---|---|---|
| Fichas, roteiro, cenas, checagem | Agentes do Claude Code + skills + `vp check` (ADR 009; a spec previa Ollama) | Ollama local (#27, checagem já medida em `data/benchmarks/checagem-local.md`); Groq e Gemini gratuitos; outro agente que leia as skills | Fidelidade ao texto-fonte e fatos que prendem, sem custo por chamada. |
| Narração | Kokoro local nos rascunhos; voz clonada do dono (Chatterbox local) no vídeo final (ADR 016) | Gemini TTS Charon (ADR 012, já com adapter) | Voz claramente melhor em escuta cega, nomes corretos, condições de dados aceitas, limite diário compatível. |
| Alinhamento de áudio | ffprobe + revisão manual | Groq Whisper gratuito, quando necessário | Corrigir problema concreto de legenda; não transcrever episódio inteiro sem necessidade. |
| Imagem para lacunas | Cloudflare Workers AI, FLUX.1 Schnell | Outro só após checar plano, direitos e cota | Qualidade útil dentro de custo zero. Acervo sempre antes de gerar. |
| Roteador de modelos | Nenhum | OpenRouter com variante `:free` | Só se o candidato direto falhar. |

- Um adapter por função expõe contratos simples: `generate_json()` (texto, só transporte),
  `synthesize_speech()`, `estimate_cost()`/`generate_image()`, `search_assets()`, `align()`, `render()`.
  `generate_script()` e `generate_scenes()` são funções do pipeline sobre `generate_json()`, para prompts
  e validação de claims ficarem num lugar só (ADR 006). `config/providers.toml` escolhe um padrão por função.
- Catálogos como free-llm-resources, free-ai-api-tiers e free-for-dev servem **só para descobrir** opções.
  Cotas e termos entram no código só depois de link oficial, data da consulta e teste com a conta real, em
  `data/benchmarks/`.
- Comparação pequena antes de tornar um remoto padrão: os mesmos 3 trechos (um nome próprio difícil, duas cenas
  com fatos verificáveis), um bloco de narração por voz, duas lacunas visuais. Anotar modelo/versão, endpoint,
  data, latência, unidades, limite observado, custo, consistência do JSON, erros, avaliação humana e URL dos
  termos. Boa redação não prova confiabilidade factual.

## 8. Política de imagens e cota

Ordem de busca por cena: (1) acervo interno já revisado → (2) Commons, Library of Congress e Flickr Commons para
pessoas, lugares e eventos específicos → (3) bancos de imagem para cenas genéricas (ondas, neve, céu): Pexels,
Pixabay e Unsplash por API, Coverr só à mão pelo site → (4) Workers AI, no máximo 2 alternativas, escolha humana →
(5) mapa, cronologia, citação curta permitida ou tela gráfica original. Cada cena recebe imagem relevante ou a
lacuna fica registrada.

- Busca em lote por consulta normalizada; cache de metadados e miniaturas; `sha256` para deduplicar;
  redimensionar só o ativo final escolhido; registrar headers de cota dos bancos quando existirem.
- Termos de cada banco em `data/benchmarks/termos-bancos-de-imagem.md`. Imagem de banco sem pessoa
  reconhecível doente ou tomando remédio, sem marca, logo, texto nem contexto político.
- Domínio público: publicado até 1930 é DP nos EUA; o Commons exige DP também no país de origem. Checar caso a
  caso e registrar o raciocínio em `usage_notes`.
- **Workers AI:** cota gratuita de 10.000 neurons/dia; uma imagem 1024×1024 com 4 passos ≈ 58 neurons (~170/dia).
  O teto de 12 imagens/episódio é editorial. O adapter estima o consumo antes de gerar, registra o uso do dia e
  devolve `quota_exhausted` em erro de cota. Gotchas: `num_steps` é obrigatório na prática; o filtro NSFW dá falso
  positivo com prompts curtos (código 3030: reescrever com contexto e tentar uma vez); modelos são aposentados sem
  aviso longo (modelo ausente → `needs_review`, sem trocar de modelo sozinho).

## 9. Voz, legendas e montagem

- Roteiro escrito diretamente no idioma do episódio (en ou pt-BR), com um WAV curto por bloco narrativo para
  trocar uma frase isolada. Glossário de pronúncia por episódio em `voice/glossary.json` (o Kokoro aceita
  fonemas customizados; o Gemini TTS e o Chatterbox não).
- Timing das cenas vem da duração real dos WAVs (ffprobe), nunca de estimativa do LLM.
- **Pausas dentro da narração (ADR 015):** `<short pause>` na `narration` (palavra, espaço, marca, espaço, palavra);
  `<long pause>` e outras tags são erro. A tela, a legenda e as âncoras dos planos usam o texto sem a marca
  (`app/media/narration.py`); cada marca vale 10 caracteres no tempo dos planos e no `vp check`. O Kokoro e o Chatterbox fazem
  silêncio (`pause_ms`); no Gemini, cena com pausa vai numa chamada só (o corte de lote recusa pausas internas longas).
- Legendas geradas após aprovação da voz, por alinhamento do texto com o áudio; nomes próprios sempre revisados.
  `captions.srt` é editável.
- Montagem: 20–35 entradas visuais para 5–7 min. Reutilizar um mapa quando o roteiro volta ao mesmo local.
  Movimento leve em foto só se o recorte preservar o assunto. Música e efeitos só com licença registrada por faixa.
- Motor **por formato** (ADR 001, `render` em `config/providers.toml`): `archival_documentary` → **ffmpeg puro**
  (`app/render/ffmpeg.py`); `explainer` → **Remotion + @viniciusk/motion-kit** (`app/render/remotion.py` e o
  template em `video/`; peças do kit editorial, tema `editorial`, mapa com contornos do Natural Earth em domínio
  público, cache por cena). O apresentador (ADR 013) vem de `video/src/HostWindow.tsx` (pele do dono em `donoSkin.ts`); sem `host`, nada muda.
  MoneyPrinterTurbo reprovado (branch `experimento-mpt`). Cena gráfica animada num documentário = clipe do
  motion-kit como ativo `Original` (#42). Comparação dos motores em
  `data/benchmarks/README.md`; entrada de teste em `tests/fixtures/episodes/engine-test/`.

## 10. CLI (`vp`, console script em `pyproject.toml`)

`vp --help` lista os comandos, mas só respondem de fato `bench`, `excerpts`, `check`, `approve`, `reject` e
`status`. `new`, `reopen`, `sources`, `script`, `scenes`, `assets`, `gallery`, `voice`, `subs`, `render` e `export`
saem com "ainda não implementado" e a etapa pendente; scripts em `scripts/provisorio/` cobrem fonte, voz e render
até virarem comandos. Um comando novo é um handler `(args, context)` registrado em `HANDLERS` (`app/cli.py`). Cada
comando é idempotente: reexecutar com o mesmo `input_hash` não refaz trabalho.

## 11. Ordem de implementação e critérios de aceite do piloto

Ordem: **(A)** experimento de motor da Fase 0 → **(B)** fixar `episode.json` e renderizar um episódio inteiro →
**(C)** CLI + Kokoro por bloco + timing + legendas → **(D)** adapters de busca/licença + galeria → **(E)** geração
condicional via Cloudflare + medidor de cota → **(F)** pesquisa assistida e revisão de roteiro com LLM →
**(G)** comparação pequena dos remotos, só para gargalo demonstrado. FastAPI e SQLite só quando arquivos e galeria
virarem obstáculo real.

Piloto aceito quando:

- [ ] Pauta + ≥ 2 fontes independentes para os fatos principais, em `sources.json`.
- [ ] Roteiro em inglês revisado, dividido em cenas, toda claim relevante com `source_ids`.
- [ ] Galeria com ≥ 1 opção visual por cena e direitos registrados; geração só para lacunas.
- [ ] Narração local, legendas editáveis, prévia renderizada, revisão por cena registrada.
- [ ] Export completo; **zero** custo de API paga.
- [ ] Métricas registradas: duração de cada etapa, imagens encontradas/geradas, decisões e rejeições humanas,
      horas humanas totais.

## 12. Validação de audiência e política do YouTube

- 4 vídeos longos no mesmo recorte em 4–6 semanas, títulos e capas próprios, **sem** anúncio pago (promoção paga
  altera a origem das visualizações e não conta para o Programa de Parcerias).
- Métricas manuais no YouTube Studio aos 7 e 28 dias: impressões orgânicas e origem do tráfego; CTR com contexto;
  retenção nos 30 s iniciais e duração média; retorno e comentários espontâneos (amigos não contam); tempo e custo
  por episódio. Sem integração com a API do YouTube nesta fase.
- **Política de conteúdo inautêntico (YPP, jul/2025):** o YouTube cita como exemplo de conteúdo mass-produced
  "histórias narradas com variações mínimas" e "slideshows com narração idêntica". É exatamente o risco deste
  formato. Defesa: pesquisa original, roteiro próprio por episódio, variação visual e de estrutura, edição real.
  Tratar isso como critério de aceite, não como risco genérico.
- Uso de IA continua monetizável quando o conteúdo é original e a divulgação de conteúdo sintético é feita.

## 13. Decisões pendentes e ajustes propostos sobre a spec v0.4

Registrar cada item como ADR quando decidido. Até lá, o código segue a spec.

1. **Recuperação de fontes (proposta forte; numeração dos trechos e fichas decididas na ADR 009).** `vp sources`
   baixa e extrai; `vp script` passa ao modelo **apenas** trechos numerados dessas fontes e exige que cada frase
   cite o trecho. Sem isso, o validador de schema aprova ficção bem formatada.
2. **Provedor de texto padrão** (modo sem agente; o das etapas criativas é a ADR 009). Spec: Ollama local.
   Proposta: Gemini/Groq gratuito para rascunho (fidelidade ao texto-fonte muito maior que modelos 7–8B em CPU),
   Ollama como fallback. Roteiro de história pública não é dado confidencial. Decidir após o benchmark da máquina.
3. ~~ffmpeg puro como candidato zero de montagem~~ **Decidido** na ADR 001: um motor por formato.
4. ~~`.wslconfig` com limite de memória explícito~~ **Feito** (§3, ADR 004).
5. **Flickr Commons** entrou na cascata de acervos ("no known copyright restrictions").
6. Pós-piloto (já previstas na spec): duração ideal do episódio; versões em português/espanhol.
7. **Busca por vetor (ADR 010, proposta ainda sem arquivo em `docs/decisions/`):** `vp search` sobre os trechos
   numerados, com embeddings locais em arquivo (sem banco). Serve para achar trechos; a prova continua literal no
   `vp check`. Entra quando as fontes passarem do que um agente lê de uma vez (ex.: jornais da Hemeroteca).
8. ~~B-roll de banco de imagens no gancho do explicativo~~ **Decidido** na emenda de bancos de imagem da ADR 007
   (2026-09-26): Pexels, Pixabay e Unsplash por API, Coverr só manual, sempre como ilustração (§2.4).

## 14. Como trabalhar neste repositório (instruções para o Claude Code)

- Antes de escrever código de uma etapa, ler o schema correspondente em `app/pipeline/schemas.py` e o manifesto
  de exemplo em `tests/fixtures/episodes/pilot-example/`.
- Chamar provedores externos (Pexels, Pixabay, Unsplash, Coverr, Cloudflare, Groq, Gemini) só quando o usuário
  pedir explicitamente naquela sessão. Ollama e Kokoro locais podem rodar.
- Arquivos em `data/episodes/*/` com `review_status: approved` ficam como estão; se um ajuste exigir mexer neles,
  parar e perguntar.
- Em dúvida sobre licença de um ativo ou termos de um provedor, parar e perguntar.
- Antes de encerrar qualquer tarefa, rodar `pytest` e `ruff check .`. Testes novos para toda etapa nova. Testes
  com modelos locais pesados levam `@pytest.mark.slow` e ficam fora da rodada padrão (`pytest -m slow`; usam
  `HF_HUB_OFFLINE=1`, sem rede).
- Commits pequenos e descritivos. Decisões de arquitetura viram `docs/decisions/NNN-titulo.md`. Ao mudar uma
  decisão registrada aqui, atualizar este arquivo no mesmo commit.
- Dependências só via `uv add` (com licença no comentário do `pyproject.toml`) e `uv.lock` versionado.
  Kokoro/PyTorch ficam no extra `tts`; testes rodam sem ele.
- Convenções: Python 3.11+ (3.12 no `.venv`), tipagem completa, pydantic v2 para manifestos, `pathlib`, sem estado
  global, um adapter por provedor em `app/providers/<função>/<provedor>.py` implementando o `Protocol` da função,
  logging estruturado sem segredos.
- Template do `explainer` (`video/`): consultar o kit pelo MCP `motion-kit` (skill `componentes-do-kit`) antes de
  escolher componente ou passar prop. O servidor lê o checkout `~/projetos/motion-kit`; cruzar com o SHA do pin.
- Animação de texto nos Reels (entrada, legenda palavra a palavra, lista que acumula): ler
  `docs/guia-animacao-de-texto.md` antes de propor ou implementar. É rascunho (2026-10-07): onde diz *decisão aberta*,
  perguntar ao dono; em conflito valem as ADRs.
- Etapas criativas: agentes em `.claude/agents/` com o método nas skills de `.claude/skills/`; o que eles escrevem
  passa pelo `vp check` e pelos gates humanos (ADR 009). Ver §15.
- Reels: o resumo do reels-radar (`~/projetos/radar-de-reels`, `RADAR_DIR` no `.env`) entra como cópia datada no
  episódio e orienta só a forma (ADR 018). Gerar ou atualizar o resumo é no outro projeto; coleta que gasta
  crédito só com decisão do dono. Nenhuma afirmação do roteiro sai do resumo.
- **Instruções a agentes, notas de fonte e exemplos:** só o que está nos trechos baixados. Citar fichas por id
  (F08) e trechos (`source-02#E46`) em vez de reescrever o fato; conferir na página antes de escrever uma nota;
  pedir gancho e promessa como pergunta neutra. Um fato ou enquadramento meu no prompt vira roteiro, e o
  `vp check` não pega.
- O escopo do MVP é o do §2.8; Docker, banco, fila, API web, framework multiagente no código e provedor pago ficam
  fora, e o motivo está em §2.

## 15. Agentes das etapas criativas (ADR 009)

Os agentes escrevem **só arquivos de dados** em `data/episodes/<id>/`; a aplicação valida (`vp check`) e o dono
decide nos gates. O método de cada etapa está na skill (Markdown portável: outro agente, um modelo local ou uma
pessoa podem seguir o mesmo método e passar pelo mesmo `vp check`); o arquivo do agente só define papel e
ferramentas. Agentes e skills novos aparecem numa sessão nova do Claude Code; as skills também rodam como
`/fichamento <id>`, `/roteiro-explicativo <id>`, `/checagem <id>`.

| Agente | Skill | Escreve | Ferramentas |
|---|---|---|---|
| `pesquisador` | `fichamento` | `facts.json` | Read, Grep, Glob, Write, Bash (`vp excerpts`, `vp check`) |
| `roteirista` | `roteiro-explicativo`, `humanizer-narracao` | `outline.md`, `scenes.json` | Read, Grep, Glob, Write, Edit, Bash (`vp check`) |
| `verificador` | `checagem` | nada (relatório) | Read, Grep, Glob; contexto limpo, só leitura |

Ordem: pesquisador → `vp check` → gate 1 (o dono escolhe os fatos) → roteirista → `vp check` → verificador →
voz + render → gate 2. O verificador devolve problema de ficha ao pesquisador e de roteiro ao roteirista; ficha
que muda faz o gate 1 voltar ao dono. Nos Reels, a skill `pauta` (sem agente próprio ainda) vem antes do
pesquisador, e pesquisador e roteirista leem o `radar-brief.json` do episódio (ADR 018).

**Modelo local (Ollama, #27).** `prompts/local/` guarda o método das etapas em prompts curtos, uma chamada por
unidade (uma afirmação, uma cena), com o schema de saída em código. Hoje só `checagem.md` (afirmação × trecho),
medido por `scripts/provisorio/checagem_local.py` (resultados em `data/benchmarks/checagem-local.md`). O `vp check`
e os gates continuam decidindo; o veredito do modelo é alerta.

**Agentes mais específicos (candidatos).** Criar só quando a etapa existir no código e houver necessidade
concreta. Cada um com skill própria, ferramentas mínimas e validação em código quando possível; nenhum aprova gate.

| Candidato | Etapa | O que faria | Quando criar |
|---|---|---|---|
| `curador-de-imagens` | ativos, gate 3 (#20–#23) | busca em Commons, LoC, Flickr Commons e Brasiliana; preenche `assets/*.json` com licença e `usage_notes`; propõe candidatos por plano | com `vp assets` |
| `arquivista` | fontes primárias (#26) | jornais e documentos de época (Hemeroteca Digital); confirma fatos de fonte única | com a busca por vetor |
| `planejador-de-planos` | roteiro (#28) | separa a escolha dos planos (tipo, âncora, ritmo) da escrita da narração | se o ritmo visual virar gargalo |
| `revisor-de-risco` | antes do gate 4 | pessoas vivas, empresa ativa, controvérsia atribuída, divulgação de IA | antes do primeiro episódio publicado com pessoas vivas |
| `pronuncia` | voz (#15) | glossário `voice/glossary.json` para nomes próprios | quando a voz errar nomes |
| `editor-de-descricao` | export (#18) | `description.txt` e `credits.txt` a partir das fontes e dos ativos | com `vp export` |

## Referências técnicas verificadas (23–24/09/2026)

Lista completa em `docs/spec-v0.4.md`: WSL, Ollama, Groq, Gemini, OpenRouter, Cloudflare Workers AI, Pexels,
Wikimedia Commons, Library of Congress, Kokoro-82M, FFmpeg, Remotion e as políticas do YouTube (monetização,
divulgação de IA, retenção/CTR, YPP).
