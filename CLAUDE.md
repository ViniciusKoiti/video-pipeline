# CLAUDE.md — video-pipeline

> Contexto persistente para o Claude Code neste repositório. Curto, factual e normativo: o que o código,
> `vp --help`, os schemas e as ADRs já detalham fica fora. Preferências pessoais vão em `CLAUDE.local.md`
> (gitignored); histórico de episódios e pendências ficam em `docs/ROADMAP.md`. Em conflito, valem `docs/decisions/`.
> Ao mudar uma decisão registrada aqui, atualize este arquivo no mesmo commit.

## 1. O que é este projeto

Pipeline local, retomável e auditável para produzir vídeos narrados em `pt-BR` ou `en` (ADR 008), 16:9 (ou 9:16
para Shorts/Reels, ADR 014), H.264/AAC até 1080p, saindo como `final.mp4` + `captions.srt` + `description.txt` +
`credits.txt`. Canal: **Cena e Conceito** (`@cenaeconceito`; nome e tag de afiliado em `config/canal.toml`).
Público (dono, 2026-11-14): jovens de 20 a 30 anos com desânimo profundo; tom acolhedor, sem energia de coach.

**Publicação só após revisão humana (gate 4) e autorização explícita do dono** (agendamento via `vp postiz`, §2.8).
Agendado não é publicado: confira no YouTube Studio antes de reenviar.

### Roteamento por formato (regras editoriais moram nas skills/docs)

| Formato | Motor (ADR 001) | Agente / Skill de Roteiro | Referência editorial |
| :--- | :--- | :--- | :--- |
| **Ensaio filosófico / cultural** (~8–9 min, seg/qua/sex) | `explainer` (Remotion) | `roteirista` / `roteiro-explicativo` | molde e partitura (ADR 031); `docs/pesquisa/roteiro-referencias-2026-10-20.md` e `retencao-idade-media-2026-11-14.md` |
| **Explicativo "dinheiro e poder"** | `explainer` (Remotion) | `roteirista` / `roteiro-explicativo` | `docs/pesquisa/modelo-perfil-de-poder.md` |
| **Ficção histórica** ("como era ser X") | `explainer` (Remotion) | `roteirista-ficcao-historica` | ADR 055 (dispensa fichas, fontes e `claims`) |
| **Documentário de arquivo** (1880–1930) | `archival_documentary` (ffmpeg) | `roteirista` / `roteiro-explicativo` | `tests/fixtures/episodes/pilot-example/` |
| **Shorts cortados de um longo** (9:16) | `explainer` vertical ou `motion-video` do kit | corte do roteiro aprovado | decisão do dono de 2026-11-09: pergunta de um personagem do kit (cena `cast`) na abertura e fecho `invite` de ~4–5 s chamando para o canal (§4) |
| **Reels de nicho** (9:16) | `explainer` vertical | `pauta` → `roteirista` | ADR 018 (radar → pauta), ADR 028 (gancho, conta, nota e cartão final) |
| **Série técnica "eu medi" / System Design** (Shorts) | `motion-video` do kit (`vp short`) | `shorts-tec`; rotina `short-diario` (ADR 036) | `renders/serie-conceitos/direcao-editorial.md` (quadro obrigatório antes de voz/render) |

Temas a evitar: sobrevivência recente (vira 100% ilustração gerada), true crime, Titanic/Hindenburg/Everest 1996
e Segunda Guerra (saturados).

## 2. Regras inegociáveis

1. **Custo zero na validação.** `MAX_API_SPEND_USD=0` e `ALLOW_PAID_API=false`. Nunca migrar para endpoint pago,
   comprar créditos ou trocar de modelo por conta própria (o plano do Claude do dono não é API paga, ADR 009). Em
   429, cota esgotada, modelo ausente ou licença incompatível: registrar em `review.json`, marcar a cena como
   `needs_review` e parar **apenas aquela cena**.
2. **Nenhuma fonte inventada.** O `pesquisador` só ficha trechos extraídos de fontes reais em `sources.json`, com
   citação literal conferida pelo `vp check`. No `roteirista`, toda afirmação de fato e dado na tela exige `claims`
   com `source_ids` (ADR 008). Exceção exclusiva: `roteirista-ficcao-historica` (`"fiction": true`, ADR 055).
   Vídeo de outro canal é pista de forma, nunca fonte.
3. **Nenhum ativo sem licença registrada entra no render.** Lista fechada da ADR 007 (PD, CC0, CC-BY incl. 3.0 BR,
   Flickr-NKCR, Pexels, Pixabay, Unsplash, Coverr, Generated, Original, Citacao e YouTube-Audio-Library, esta só no
   YouTube — **proibido** CC-BY-SA e NC). Campos obrigatórios em §5. Sem licença identificável → `needs_review`.
4. **Stock e imagem gerada são ilustração**, nunca registro do fato (`visual_need` correto sempre). Imagem
   sintética realista de fato histórico exige divulgação de conteúdo alterado no YouTube.
5. **Revisão humana obrigatória nos 4 gates:** (1) tema/fontes, (2) roteiro, (3) ativos/direitos, (4)
   prévia/descrição. Score de IA não aprova direitos nem autenticidade. A decisão é registrada por `vp approve` ou
   `vp reject`, nunca editando `review_status` à mão, com `VP_REVIEWER` configurado (o `git user.name` aqui é `test`).
6. **Imutabilidade de aprovação (ADR 039).** Arquivos com `review_status: approved` nunca são sobrescritos pelo
   código; só `vp reopen --step <s> --reason "..."` libera o alvo no `review.json`. Se um ajuste exigir mexer num
   arquivo aprovado, pare e pergunte.
7. **Segredos só em `.env`** (fora do Git). Adapters nunca logam tokens, headers de auth ou URLs assinadas.
8. **Escopo do MVP:** sem upload automático, Docker, FastAPI, LiteLLM, banco de dados (exceto SQLite local de
   telemetria editorial `vp usage`, ADR 032), render em nuvem ou framework multiagente no código. `vp postiz`
   (ADR 025, `docs/postiz.md`) só envia/agenda depois do gate 4, com o pacote do `vp postiz pacote`, a dúvida cega
   gravada por `vp postiz duvida`, a confirmação do dono pela regra `ask` do `.claude/settings.json` e cada passo em
   `data/publicacoes/registro.jsonl`.
9. **Dependências:** só via `uv add`, com justificativa no commit e licença verificada no comentário do
   `pyproject.toml`; `uv.lock` versionado.
10. **Testes não acessam rede.** Provedores externos são mockados via `tests/fakes/`; respostas aprovadas viram
    fixtures em `data/cache/`.

## 3. Ambiente e arquitetura

- **Ambiente:** Windows + WSL2/Ubuntu (`~/projetos/auto-play`, nunca `/mnt/c` ou `/mnt/e`). Python 3.12 (`.venv`,
  `uv sync --extra tts`; sem o extra, só CLI e testes), `ffmpeg`/`ffprobe`, `espeak-ng`, Node.js LTS em `video/`
  (`npm ci`). Validar ambiente com `scripts/check_env.sh`.
- **Máquina limitada:** antes de benchmark, render longo ou modelo local, rodar `cpu_probe()` (`app/pipeline/bench.py`;
  `> 0,3 s` = inválida). Um render por vez; temporários do Remotion ficam em `data/cache/remotion-tmp/`. Nunca
  encerrar processos do dono; interfaces de teste só em `127.0.0.1`.
- **Arquitetura (ADR 006, 037, 038, 042, 045):**
  - **Portas e adaptadores:** `Protocol` em `app/providers/<função>/base.py` (ou `app/render/base.py`); composição em
    `app/bootstrap/`. Núcleo (`app/pipeline`, `app/media`, `app/render`, `app/storage`) não lê `Settings` nem importa
    adapter concreto (`tests/test_architecture.py`). Trocar de abordagem = adapter novo + registro em
    `app/bootstrap/__init__.py` + `tests/test_contracts.py` + uma linha em `config/providers.toml`. Todo adapter
    declara `ProviderInfo(name, remote, usd_per_call)`; custo > 0 é recusado.
  - **Modelos e constantes:** uma classe por arquivo em `app/<área>/models/<nome>.py` (`tests/test_model_layout.py`);
    constantes imutáveis (`Final`, `tuple`, `frozenset`, `MappingProxyType`) em
    `app/<área>/constants/<resp>_constants.py` (`tests/test_constants_layout.py`).
  - **Erros:** toda exceção de domínio herda de `app.errors.PipelineError`; comandos sobem para
    `app.commands.errors.run` (`tests/test_errors_layout.py`).
  - **Tamanho (catraca):** até 200 linhas de código por módulo e 50 por função em `app/`; o que já passa está em
    `tests/baseline_tamanho_app.json` e só pode encolher. Código novo vai em módulo novo.
  - **Pacotes do pipeline (ADR 064):** `app/pipeline` se divide por etapa, em camadas: base (`schemas`, `models/`,
    `constants/`, `ports`) → `governance` → etapas (`research`, `script`, `visuals`, `sound`, `voice`,
    `publishing`, `bench`) → fluxos (`production`, `short`, `gates`, `status`). Nenhum módulo importa uma camada
    acima da sua, e não há ciclo entre etapas (`tests/test_pipeline_layers.py`). Módulo novo nasce no subpacote da
    etapa; enquanto houver módulo solto na raiz, ele declara a etapa em `ROOT_MODULES`.

### Mapa resumido do repositório

`app/pipeline/` etapas e schemas · `app/providers/` portas e adapters · `app/bootstrap/` composição · `app/render/`
motores (`ffmpeg`, `remotion`) · `app/media/` áudio, legenda, pronúncia e apresentador · `app/commands/` subcomandos
`vp` · `app/storage/` persistência JSON · `video/` template Remotion (`motion-kit`) · `.claude/agents/` e
`.claude/skills/` etapas criativas · `config/` (`canal.toml`, `providers.toml`) · `data/episodes/<id>/` artefatos do
episódio · `data/benchmarks/` medições e termos · `tests/fakes/` fakes das portas · `scripts/provisorio/` ferramentas
ainda sem comando.

## 4. Fluxo de trabalho, estados e retenção

- **Ordem das etapas:** Banco de ideias → Validação de tema (`validador-de-tema`, parecer por tema; o dono escolhe,
  skill `vp-validacao-de-tema`) → Pauta (título provisório, conceito de capa e hipótese; a hipótese vai para
  `metrics.json.hypothesis` quando houver dados reais de publicação) → Fontes (`sources.json`, ≥ 2 independentes)
  → Fichas (`facts.json`, **gate 1**) → `outline.md` + editor (montagem) → `scenes.json` + editor (edição) →
  `vp check` + `verificador`, no máximo 2 rodadas (**gate 2**) → Trilha (`music.json`) → `plano-de-imagens`
  validado pelo dono antes de baixar + busca visual (**gate 3**) → Voz (`vp voice`) + revisão fonética → Legendas
  → Render + `vp audio` (quando solicitado) → Prévia + metadados (`vp-metadados-youtube`: título, descrição, tags e
  lista do Studio) + miniatura (**gate 4**) → `vp postiz` → métricas aos 7 e 28 dias (`vp metricas`; sem anúncio pago, que muda a origem do tráfego e não conta para o YPP).
- **Relógio de retenção do vídeo longo (ADR 061, teste do dono de 2026-11-16):** a curva cai cerca de 60% até os
  2 min, e quem fica fica uns 3 min (`docs/pesquisa/retencao-idade-media-2026-11-14.md`).
  - A promessa central fecha **até 0:30**, sem preâmbulo sobre o próprio vídeo.
  - Entre **2:00 e 3:00** entra um gancho de retomada (antecipação forte ou pergunta nova) ou a virada prática.
  - Depois de uma pausa de aviso (CVV, saúde) vem um micro-gancho, antes do próximo bloco.
  - O roteirista marca o papel das cenas em `beat` (`promise`, `rehook`, `turn`, `pause`); o `vp check` confere
    pelo texto e, depois do `vp voice`, pela voz real, e mostra o que falhar como `atenção` para o gate 2.
- **Shorts cortados de um longo (dono, 2026-11-09):** abrem com a pergunta de um personagem do kit e fecham com o
  mesmo personagem chamando para o canal (voz clonada, `invite`, ~4–5 s para passar no nivelamento da ADR 054; a
  frase varia a cada Short). A descrição abre com "Dê uma olhada na história completa na descrição ou entrando no
  canal" e o link do longo. Um pedido só no fecho (ADR 028).
- **Estados e cache (`manifest.json`):** `pending → running → needs_review → approved → completed` (ou `failed`).
  Cache por `(episode_id, step, input_hash)` com trava única em `.lock`. Etapas por cena (ADR 040) refazem apenas
  cenas pendentes/falhas. Trocar imagem refaz só montagem e prévia; mudar a fala refaz voz da cena, tempo,
  legendas e render; mudar fonte refaz roteiro e tudo abaixo.
- **O que cada gate carimba:** `sources.json` + `facts.json` (1); `scenes.json` + `outline.md` (2); o arquivo do
  ativo (3); o render mais acabado com `episode.json`, legenda e texto do post (4, `--step preview`). Renderizar o
  final depois de aprovar a prévia pede nova decisão. `vp status` mostra se a decisão ainda vale.

## 5. Contratos de dados e direitos (resumo normativo)

Os detalhes de campos vivem em `app/pipeline/schemas.py`. Regras que o schema sozinho não impõe:

- **Objetivo e Opinião (ADR 019):** `objective.kinds` (`noticiar | explicar | opinar`) e `promise` obrigatórios; a
  tese (`thesis`, `thesis_by`) vem do dono. Opinião nunca vira dado na tela, mas deve ser expressa de forma
  **orgânica e conversacional** (*"na minha leitura"*, *"pelo menos é assim que enxergo"*), **nunca** com rótulos
  burocráticos como *"digo isso como opinião"*: o `vp check` dá erro (emenda de 2026-11-16).
- **Funil e CTA (ADR 026):** `funnel.stage` (`topo | meio | fundo`), `cta` e `offer` (só no `fundo`). No vídeo
  longo, a última cena une a pergunta dos comentários (`funnel.engagement`) **e**, depois dela, a chamada compatível
  com o estágio (inscrição ou próximo vídeo no topo; salvar, comentar ou próximo vídeo no meio; a oferta no fundo).
  Chamada que não pede o que o estágio pede, ou que não é dita na última cena, é erro no `vp check`. Short e Reel:
  um pedido só.
- **Ativo (`assets/<id>.json`):** `sha256` sempre; domínio público com o raciocínio em `usage_notes` (até 1930 é DP
  nos EUA; o Commons exige DP também no país de origem); CC-BY com `author` + `attribution_text`; banco de imagem
  com a licença do banco, `author`, `attribution_text` e a conferência de pessoas, marcas e texto em `usage_notes`
  (sem pessoa reconhecível doente ou tomando remédio, marca, logo, texto nem contexto político); imagem gerada com
  `generation`. Música: licença por faixa; a da Biblioteca de Áudio do YouTube só vale no YouTube (corte para Reel
  vai sem ela).
- **Citação de obras (`Citacao`, ADR 007):** quadro parado só de material oficial público (`provider: official`),
  com `work`, crédito e justificativa em `usage_notes`; teto de 10 por vídeo e 8 s cada. Clipe em movimento
  (`media: clip`, `origin`, `timecode`; `official` ou `owner_capture`) só em B-roll, **sem áudio da obra**, só no
  YouTube, comentado na narração e com a decisão de risco do dono no `review.json`. Clipe como textura, sem a
  narração comentar a obra, só existe na exceção do `vazio-de-ter-tudo` (2026-11-14); outro episódio pede decisão
  nova do dono. Miniatura com quadro da obra é decisão do gate 4. Um strike suspende a série.
- **`episode.json`** é o contrato do render: mudar exige nova ADR. **`review.json`** é a fonte única das decisões
  humanas, só com entradas acrescentadas.
- **Política YPP (conteúdo não original):** todo episódio exige pesquisa própria, variação visual/estrutural real e
  divulgação de conteúdo sintético quando aplicável (`support.google.com/youtube/answer/1311392`).
- **Descrição:** livros citados levam o link de afiliado da Amazon com o aviso exigido (`vp export livros <id>`).

## 6. Voz, pronúncia, legendas e montagem

- **Provedores de voz (`config/providers.toml`):** `kokoro` nos rascunhos; `chatterbox_modal` (ou `chatterbox` local)
  como voz final clonada (ADR 016, 024); `gemini` (Charon; 10 chamadas por dia, voz do vídeo-régua) como alternativa.
  **Ensaios do Cena e Conceito e Shorts cortados deles (dono, 2026-11-18):** `--voz azure_speech` com o Caio
  (`pt-BR-Caio:MAI-Voice-2.1`, prévia; exige avisar que a voz é sintética, na descrição e no Studio), estilo por
  trecho pelas marcas de emoção e glossário pela grafia da `fala` (ADR 063).
- **Marcas de emoção (ADR 063):** `<raiva>…</raiva>` em volta de uma frase ou oração, lista fechada em
  `NarrationConstants.EMOTION_TAGS`; somem das legendas, da tela e das âncoras; o Azure traduz em estilo
  (`[azure_speech.styles]`), as outras vozes falam o trecho na entrega da cena. Erro no `vp check` para marca
  desconhecida, sem fechar, aninhada ou vazia; atenção para menos de três palavras ou mais de duas por cena.
- **Gravação de referência da voz clonada:** dado pessoal, em `data/voice-references/`, fora do Git e nunca enviada
  a provedor, exceto o volume privado do dono no Modal (ADR 024), onde os WAVs já precisam estar: o cliente não envia.
  O `delivery` e o idioma escolhem a referência (ADR 053).
- **Trava fonética e `voice/glossary.json` (obrigatório antes do render final):**
  - Todo termo em língua estrangeira, sigla, título de episódio/obra ou nome próprio não nativo presente em
    `scenes.json` **deve** ter entrada em `voice/glossary.json` (`escrita` → `fala`) antes de rodar
    `vp voice --voz-final`; o `vp check` aponta como `atenção` os que achar por traço (nome sem traço, como
    "Einar", escapa). Com a voz final do Azure, cada termo leva também `ipa` (fonema exato; só no vídeo longo).
  - Título estrangeiro é dito uma vez, ou em português na narração com o original na tela (vale para qualquer voz).
  - A voz clonada não segue a grafia do glossário de forma estável: depois do `vp voice`, rodar
    `vp voice <id> --conferir` (Whisper local, ADR 062; modelo no cache com `uv run hf download
    openai/whisper-small`), ouvir a folha `voice/conferencia-escuta.wav` e pedir outra tomada do que soar errado
    com `--refazer <cenas>` antes da montagem final. No Short do `vp short`: `vp short checar` antes da primeira
    voz, `vp short conferir` depois e `vp short voz --refazer <falas>` (emenda de 2026-11-17 da ADR 062).
  - Usar `<short pause>` (espaço + marca + espaço) onde a síntese costuma colar palavras: antes de diálogo interno e
    logo depois de dois-pontos que abrem uma fala ou pergunta (o `vp check` avisa). Respeitar o teto das skills
    (uma por ~15 palavras, nunca no início nem no fim da cena). `<long pause>` e outras tags são erro.
- **Nivelamento e ritmo:** cópias em `voice/leveled/` com alvo −16 LUFS e pico −1,5 dBTP (ADR 054). Pausas por tipo
  de fim de frase via `voice/cadencia.json` (ADR 060, proposta e opcional por episódio; cópias em `voice/paced/`).
  Timing das cenas vem sempre do `ffprobe` real dos WAVs. Os nomes dos WAVs já gerados não mudam (ADR 049).
- **Legendas e áudio:** `captions.srt` gerado do WAV por frase (ADR 021) ou palavra a palavra no vertical via Groq
  Whisper (`--legenda-palavra`, ADR 023; tela sempre usa o texto do roteiro). Todo ensaio longo leva trilha
  (`music.json`, ADR 030), salvo decisão contrária no `outline.md`; ela entra com ducking perto de −14 LUFS, saída
  em estéreo. Nada cobra a trilha: conferir `music` no `episode.json` antes do gate 4. `vp audio` valida loudness e
  ataque (40 ms) via `earshot` quando solicitado.
- **Busca visual em cascata:** (1) acervo interno → (2) Commons / LoC / Flickr Commons (busca à mão; adapters ainda
  não implementados) → (3) Pexels / Pixabay / Unsplash por API (`vp assets search`), Coverr à mão → (4) imagem gerada
  só para lacuna, no máximo 2 opções por cena e 12 por episódio (teto editorial; hoje pelos scripts
  `scripts/provisorio/gerar_imagens_klein.py` e `imagens_navegador.py`, porque o adapter do Workers AI ainda não
  existe) → (5) mapa/gráfico original.

## 7. CLI (`vp`)

Use `vp --help` e `vp <comando> --help` para flags completas. Fluxo principal:

- **Preparação e checagem:** `vp sources`, `vp excerpts`, `vp briefs`, `vp check`, `vp checagem`, `vp numeros`,
  `vp status`, `vp bench`.
- **Ativos e mídia:** `vp assets`, `vp music`, `vp voice`, `vp render`, `vp audio`, `vp short`.
- **Governança e publicação:** `vp approve`, `vp reject`, `vp reopen`, `vp export` (hoje só `livros`), `vp metricas`,
  `vp traducao`, `vp medicao`, `vp postiz`, `vp usage`.
- `new`, `script`, `scenes`, `gallery` e `subs` ainda respondem "não implementado".

O `vp check` separa erro, alerta e `atenção` (o que o dono decide no gate 2). Todo comando é idempotente pelo
`input_hash`.

## 8. Como trabalhar neste repositório (Claude Code)

- **Antes de codar:** ler o schema da etapa em `app/pipeline/schemas.py` e o fixture `pilot-example`. Decisão de
  arquitetura vira `docs/decisions/NNN-titulo.md`.
- **Chamadas externas:** provedores pagos ou remotos com cota (Pexels, Pixabay, Unsplash, Cloudflare, Groq, Gemini,
  Azure) só com pedido explícito do dono na sessão. Kokoro e Ollama locais podem rodar. Em dúvida sobre licença de
  um ativo ou termos de um provedor, pare e pergunte.
- **Render só com pedido do dono.** Exceção: o vídeo-régua `votorantim-dinheiro` ganha uma versão `vN` ao fim de
  cada PR que muda o visual (template ou motion-kit), com a sonda de CPU antes (`scripts/provisorio/evolucao.py`,
  vídeos em `renders/evolucao/`, registro em `data/benchmarks/evolucao-template.md`).
- **Agentes criativos (`.claude/agents/` e `.claude/skills/`):** escrevem apenas arquivos de dados em
  `data/episodes/<id>/` (`pesquisador`, `roteirista`, `roteirista-ficcao-historica`, `editor-de-roteiro`,
  `diretor-musical`, `diretor-animacao`); `verificador`, `duvida-cega` e `validador-de-tema` só leem (este, também
  páginas públicas). Um piloto visual pedido ao
  `diretor-animacao` pode ter código em `video/src/previews/<id>/` e saídas em `renders/<id>/`.
  - Nunca passar fatos ou enquadramentos não fichados no prompt de um agente; citar por ID (`F08`, `source-02#E46`).
- **Template Remotion (`video/`):** consultar o MCP `motion-kit` (`componentes-do-kit`) e cruzar com `video/vendor/`
  antes de escolher componente/prop.
- **Pré-commit e verificação:** manter `.githooks` ativo (`git config core.hooksPath .githooks`): recusa arquivo
  acima de 50 MB e roda `scripts/check_qualidade.sh` (ruff, mypy estrito e pytest com os gates de arquitetura,
  modelos, constantes e tamanho). Antes de encerrar qualquer tarefa de código, rodar `uv run pytest` e
  `uv run ruff check .` (e `npm test` em `video/` se o template mudar). Teste com modelo local pesado leva
  `@pytest.mark.slow`.

### Referências antigas a este arquivo

Código e docs anteriores a 2026-11-16 citam a numeração antiga ("§N"). §1, §2.x e §3 seguem iguais; §4 e §5
(fluxo, estados, gates) → §4; §6 (contratos, campos do ativo) → §5; §7 (provedores) → §3 e §6; §8 (imagens e
cota) e §9 (voz, legendas, montagem) → §6; §10 (CLI) → §7; §12 (métricas e YPP) → §4 e §5; §14 e §15 (como
trabalhar, agentes) → §8. O texto antigo de §1 (estado), §7, §11, §13 e §15 (candidatos) está em `docs/ROADMAP.md`.
