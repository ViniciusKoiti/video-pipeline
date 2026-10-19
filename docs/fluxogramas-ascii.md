# Fluxogramas da aplicação (ASCII)

Estado conferido em 2026-10-19 no código (`app/cli.py`, `app/bootstrap.py`, `config/providers.toml`,
`scripts/provisorio/montar_episodio.py`, `app/render/remotion.py`, `video/`). As regras valem como estão em `CLAUDE.md`
§2, §4 e §5. As versões em Mermaid são `docs/pipeline-flowchart.mermaid` (o desenho previsto) e
`docs/pipeline-hoje.mermaid` (de 2026-10-13).

Legenda:

```
+-----------+   etapa (comando, script ou agente)
#===========#   gate: decisão do dono (vp approve / vp reject)
<  ...  >       verificação em código ou por agente; volta se reprovar
[provisório]    script em scripts/provisorio/, ainda sem comando vp
[falta]         feito à mão hoje ou ainda não existe no código
```

## 1. Visão geral: do tema ao vídeo publicado

```
 ANTES DO EPISÓDIO
 +-----------------------------+      +----------------------------------+
 | validacao-de-nicho (skill)  |      | analise-de-formato (skill)       |
 | demanda: views por canal    |      | como o nicho edita: cortes, fala,|
 +--------------+--------------+      | texto na tela, voz, som          |
                |                     +----------------+-----------------+
                +---------------+----------------------+
                                v
                 +-----------------------------+
                 | DONO: tema, público,        |
                 | objetivo, tese, funil       |
                 +--------------+--------------+
                                v
                 +-----------------------------+     radar-brief.json (Reels)
                 | pauta.md (skill pauta)      |<--- só a forma, nunca fato
                 +--------------+--------------+
                                |
 1. FONTES E FICHAS             v
                 +-----------------------------+
                 | baixar_fonte.py [provisório]|---> sources.json (>= 2 independentes)
                 +--------------+--------------+
                                v
                 +-----------------------------+
                 | vp excerpts                 |---> excerpts/  (source-02#E46)
                 +--------------+--------------+
                                v
                 +-----------------------------+
                 | agente pesquisador          |---> facts.json (citação literal)
                 +--------------+--------------+
                                v
                 <  vp check  >  ---- erro ---->  volta ao pesquisador
                                v
                 #=============================#
                 #  GATE 1: fontes e fichas    #  vp approve <id> --step sources
                 #=============================#
                                |
 2. ROTEIRO                     v
                 +-----------------------------+
                 | agente roteirista           |---> outline.md + scenes.json
                 | (+ humanizer-narracao)      |     narração e planos por cena
                 +--------------+--------------+
                                v
                 <  vp check  >  ---- erro ---->  volta ao roteirista
                                v
                 <  agente verificador  > -- problema de roteiro --> roteirista
                    vp checagem             -- problema de ficha ----> pesquisador
                                |                 corrige a ficha, e o DONO
                                |                 reaprova o gate 1 antes de seguir
                                v
                 #=============================#
                 #  GATE 2: roteiro            #  vp approve <id> --step script
                 #=============================#
                                |
 3. IMAGENS E DIREITOS          v
                 +-----------------------------+
                 | skill plano-de-imagens      |---> plano-imagens.md
                 | plano por trecho: textura,  |     decisoes-imagens.md
                 | retrato, página, quadro     |
                 +--------------+--------------+
                                v
                 #=============================#
                 #  DONO valida o plano antes  #  nada é baixado antes disto
                 #  de baixar                  #
                 #=============================#
                                v
                 +-----------------------------+
                 | buscar_candidatos.py        |---> candidatos/ + folhas (folhas.py)
                 | baixar_escolhidos.py        |---> assets/<id>.<ext> + assets/<id>.json
                 | [provisório]                |     conferência do vídeo inteiro
                 | Commons e quadros oficiais  |     (conferencia.py); cookies só
                 | [falta: à mão]              |     com o consentimento do dono
                 +--------------+--------------+
                                v
                 <  vp check e verificador:  >  retrato só na fala sobre o autor;
                 <  as imagens também        >  quadro da obra nunca sob cena de
                                |               episódio; texto da imagem = fala
                                v
                 #=============================#
                 #  GATE 2 de novo, se o tipo  #  foto -> vídeo muda o roteiro;
                 #  de algum plano mudou       #  trocar só a imagem não (PR #169)
                 #=============================#
                                v
                 #=============================#
                 #  GATE 3: cada ativo         #  "trocar" volta à busca
                 #=============================#
                                |
 4. VOZ, LEGENDA E RENDER       v
                 +-----------------------------+
                 | prévia de trecho (2–3 min)  |---> data/episodes/<id>-trechoN/
                 | com a voz final             |     o dono julga voz e visual
                 | [falta: pasta montada à mão]|     antes do render longo
                 +--------------+--------------+
                                v
                 +-----------------------------+
                 | trilha (ADR 030, proposta)  |---> só faixa com licença registrada
                 | [falta]                     |
                 +--------------+--------------+
                                v
                 +-----------------------------+
                 | montar_episodio.py          |---> voice/, episode.json,
                 | [provisório] (fluxograma 3) |     captions.srt, renders/
                 | Remotion + motion-kit (8)   |
                 +--------------+--------------+
                                v
                 <  checks automáticos  >  abre no ffprobe, duração = voz, áudio,
                                v          sem silêncio longo, 16:9, todo plano com ativo
                 +-----------------------------+
                 | créditos e descrição        |---> credits.txt (banco, Commons,
                 | revisão de direitos e risco |     quadros Citacao), descrição,
                 | [falta: editor-de-descricao,|     divulgação de IA, risco de
                 |  revisor-de-risco]          |     Content ID
                 +--------------+--------------+
                                v
                 #=============================#
                 #  GATE 4: prévia, descrição  #  "ajustar imagem" -> 3
                 #  legenda do post, miniatura #  "ajustar texto"  -> 2
                 #=============================#  <== death-note-fins-meios (2026-10-19:
                                |                    gates 1, 2 e 3 aprovados)
 5. PUBLICAÇÃO                  v
                 +-----------------------------+
                 | upload manual, ou           |
                 | vp postiz (fluxograma 6)    |
                 +--------------+--------------+
                                v
                 +-----------------------------+
                 | métricas no Studio aos      |
                 | 7 e 28 dias                 |
                 +-----------------------------+
```

## 2. Gate 2 por dentro: roteiro até a aprovação

```
 facts.json aprovado (gate 1)
        |
        v
 +----------------+      +-----------+      +---------------------+
 | roteirista     |----->| vp check  |----->| verificador         |
 | scenes.json    |      | schemas,  |  ok  | lê só os arquivos,  |
 | outline.md     |<-----| claims,   |      | contexto limpo:     |
 +----------------+ erro | âncoras,  |      | o roteiro diz só o  |
        ^                | objetivo, |      | que os trechos      |
        |                | funil     |      | dizem?              |
        |                +-----------+      +----------+----------+
        |                                              |
        |              rejected (lista de problemas)   | vp checagem <id> parecer.json
        +----------------------------------------------+ ---> checagem.json
                                                       | approved
                                                       v
                                        #==============================#
                                        # dono lê (roteiro-leitura.md) #
                                        # vp approve --step script     #
                                        #==============================#
                                                       |
                         carimbo = hash de scenes.json + outline.md (review.json)
                         mudou uma vírgula depois? o carimbo cai: vp status mostra
```

O dono decide o objetivo, a tese e a opinião (`thesis_by: dono`). O roteirista escreve a opinião marcada
("pra mim", "a meu ver"), sem claim e sem texto na tela.

## 3. Montagem: `montar_episodio.py` (até virar `vp voice` e `vp render`)

```
 scenes.json (gate 2) + assets/ (gate 3)
        |
        v
 +--------------------------------------------------------------+
 | VOZ, uma cena = um WAV                                       |
 |  rascunho: tts = kokoro (local)                              |
 |  --voz-final: tts_final = chatterbox_modal (voz do dono, GPU)|
 |  --voz=<nome>: gemini | chatterbox | kokoro                  |
 |  cache: voice/<cena>-<voz>-<hash>.wav                        |
 |         hash = texto + modelo + voz + delivery               |
 +------------------------------+-------------------------------+
                                v
 +--------------------------------------------------------------+
 | TEMPO                                                        |
 |  ffprobe: duração real de cada WAV                           |
 |  app/pipeline/shots.py: âncora na narração -> início do plano|
 |  ---> episode.json v2 (contrato do render)                   |
 +------------------------------+-------------------------------+
                                v
 +--------------------------------------------------------------+
 | LEGENDA                                                      |
 |  por frase: captions.srt, tempo dos WAVs (editável)          |
 |  --legenda-palavra: Groq Whisper -> captions.words.json      |
 |  (o áudio sai da máquina: só com pedido do dono)             |
 +------------------------------+-------------------------------+
                                v
 +--------------------------------------------------------------+
 | RENDER (explainer -> Remotion, app/render/remotion.py)       |
 |  props por cena; b-roll como textura (ADR 031):              |
 |    mesmo vídeo em planos seguidos continua de onde parou     |
 |  chave da cena = hash(template, mídia, props, encode)        |
 |    já existe -> reutiliza .segments-remotion-*/<cena>-<k>.mp4|
 |    não existe -> node render-scenes.mjs                      |
 |                  (TMPDIR em data/cache/remotion-tmp, apagado)|
 |  cada plano vira uma peça do motion-kit (fluxograma 8)       |
 +------------------------------+-------------------------------+
                                v
 +--------------------------------------------------------------+
 | ffmpeg assemble: segmentos + WAVs                            |
 |  ---> renders/preview.mp4 (--preview, 720p) ou final.mp4     |
 +--------------------------------------------------------------+
```

## 4. Estados, cache e invalidação

```
 Estado de cada etapa (manifest.json, app/pipeline/state.py)

   pending --> running --> needs_review --> approved --> completed
                  |
                  +------> failed (com o motivo)

 Reexecução
   input_hash igual ............ reutiliza a saída
   input_hash diferente ........ refaz
   etapa approved .............. nunca refaz; só vp reopen --reason (em review.json)
   429, cota, licença .......... needs_review só naquela cena; as outras seguem

 O que uma mudança invalida
   fonte muda ........... roteiro -> voz -> tempo -> legenda -> render
   narração muda ........ voz da cena -> tempo -> legenda -> render
   imagem muda .......... só montagem e prévia
```

## 5. Arquitetura: portas e adaptadores (ADR 006)

```
          vp <comando>
               |
               v
 +----------------------------+          +-----------------------------+
 | app/cli.py (HANDLERS)      |--------->| app/pipeline/ (etapas)      |
 | bench excerpts check       |          | recebem um Context e só     |
 | approve reject status      |          | conhecem portas (Protocols) |
 | checagem postiz            |          +--------------+--------------+
 | video-acquire (sem commit) |                         |
 +-------------+--------------+                         v
               |                         +-----------------------------+
               v                         | portas: providers/*/base.py |
 +----------------------------+          | render/base.py              |
 | app/bootstrap.py           |          +--------------+--------------+
 | único que conhece adapters |                         ^ implementam
 | concretos                  |                         |
 +-------------+--------------+          +--------------+--------------+
               |                         | adapters                    |
               v                         |  text: ollama               |
 +----------------------------+          |  tts: kokoro, chatterbox,   |
 | config/providers.toml      |--------->|       chatterbox_modal,     |
 | uma linha por função       |  escolhe |       gemini                |
 | + .env (segredos)          |          |  archives: pexels, pixabay, |
 +----------------------------+          |       unsplash              |
                                         |  word_aligner: groq         |
                                         |  render: ffmpeg, remotion   |
                                         |   (remotion: video/ + kit)  |
                                         |  video_acquirer: yt_dlp     |
                                         +-----------------------------+

 Registrados sem adapter ainda: image_gen workers_ai; archives wikimedia_commons,
 library_of_congress, flickr_commons (o Commons hoje é baixado à mão, com o .json do ativo).
 Custo > 0 é recusado sem ALLOW_PAID_API=true e MAX_API_SPEND_USD > 0.
 tests/test_architecture.py falha se app/pipeline/ importar adapter concreto.
```

## 6. Publicação pelo Postiz (ADR 025)

```
 gate 4 aprovado + pedido do dono para AQUELE agendamento
        |
        v
 vp postiz integrations / settings ID ......... confere o canal
        v
 vp postiz upload VIDEO.mp4 ................... id + path da mídia, sha256 no registro
        v
 vp postiz pacote post.json --episode ID ...... pacote de decisão (não cria nada)
        v
 agente duvida-cega (só os arquivos) .......... parecer "segue" | "não segue"
        v
 vp postiz duvida post.json parecer.json ...... grava o parecer
        v
 vp postiz schedule post.json ................. pede a confirmação do dono (regra ask)
        |
        v
 data/publicacoes/registro.jsonl (cada passo)
```

## 7. Análise do nicho (skills, antes do episódio)

```
 validacao-de-nicho                       analise-de-formato
 +------------------------+               +-------------------------------+
 | coleta.py: canais e    |               | amostra -> baixar (cache, fora|
 | vídeos por tema        |               | do Git) -> medir (cortes,     |
 | medianas.py: views por |               | transcrição) -> analisar      |
 | vídeo, por canal       |               | (pandas)                      |
 +-----------+------------+               | folha_densa: quadro a 0,1 s   |
             |                            | decupagem: um quadro por corte|
             v                            | + a fala; voz.py: tom, pausas |
 docs/pesquisa/reports/                   +---------------+---------------+
 o nicho tem demanda?                                     v
                                          docs/pesquisa/: como o nicho
                                          edita; vira regra (ADR 031)
```

Material de terceiros fica em `data/cache/`, só para análise; nada dele entra no vídeo.
As duas skills (`.agents/skills/`) ainda não têm commit em 2026-10-19.

## 8. Onde entra o motion-kit (ADR 027, 029)

O motion-kit é um projeto vizinho (`~/projetos/motion-kit`). O auto-play nunca importa código do checkout: o
render usa só o pacote instalado em `video/`. O checkout serve para gerar uma versão nova e para consulta.

```
 PROJETO VIZINHO ~/projetos/motion-kit (monorepo)
 +-------------------------------------+
 | packages/motion-kit                 |
 | peças editoriais, gráficos, mapas,  |
 | efeitos, temas, apresentador, CLI   |
 +------+------------------------+-----+
        |                        |
        | versão nova:           | o servidor MCP lê o checkout
        | npm run check          | (pode estar à frente da versão instalada)
        | npm pack               v
        |            +-------------------------------+
        |            | MCP motion-kit                |
        |            | skill componentes-do-kit      |
        |            | "que peça usar? qual prop?"   |
        |            +-------------------------------+
        |              só consulta: cruzar com o tipo em node_modules/.../dist/
        v
 +-------------------------------------+
 | video/vendor/                       |  um arquivo só; o commit que troca
 | viniciusk-motion-kit-0.7.1.tgz      |  o arquivo diz de que commit do kit saiu
 +------------------+------------------+
                    | video/package.json: "file:vendor/viniciusk-motion-kit-0.7.1.tgz"
                    | cd video && npm ci   (o lock confere a integridade, sem rede para o kit)
                    v
 +-------------------------------------+
 | video/node_modules/                 |  <== É ISTO que o render usa
 |   @viniciusk/motion-kit             |
 |   dist/ (componentes)  bin/ (CLI)   |
 +------+-----------------------+------+
        | import                | node bin/motion-kit.mjs sprites check
        v                       v
 +---------------------------+  +-----------------------------------+
 | TEMPLATE video/src/       |  | app/media/host.py (ADR 029)       |
 | Root.tsx: composições     |  | confere a pele "dono" em camadas  |
 |   Scene, Shot, Clipe      |  | (sprites.json) antes do render;   |
 | Scene.tsx: entrada, fade, |  | se falhar, o render para          |
 |   tema (editorial, fx,    |  +-----------------------------------+
 |   motion, theme)          |
 | ShotView.tsx: um plano    |
 | Editorial.tsx: as peças   |
 |   (editorial, charts,     |
 |   geo, graph, fx)         |
 | HostWindow.tsx +          |
 |   donoSkin.ts (host)      |
 | theme.ts (theme)          |
 +-------------+-------------+
               ^
               | props de cada cena (JSON)
 +-------------+------------------------------------------------+
 | Python: montar_episodio.py -> app/render/remotion.py         |
 |   episode.json -> scene_props() -> request.json              |
 |   node video/render-scenes.mjs request.json                  |
 |     bundle(src/index.ts) -> composição "Scene" -> mp4/cena   |
 |   ffmpeg junta as cenas com os WAVs                          |
 +--------------------------------------------------------------+

 De plano do roteiro a peça do kit (Editorial.tsx; alguns exemplos)
   plano (scenes.json)     componente do kit             módulo
   photo (acervo)    --->  ArchivalPhoto                 editorial
   photo (banco)     --->  ImageBackground               fx
   broll             --->  FootageBackground (ADR 031)   fx
   keyword           --->  KineticHeadline               editorial
   quote (documento) --->  DocumentPage                  editorial
   quote (citação)   --->  Quote do template, animado    raiz do kit
                           com useSpringIn
   lower_third       --->  LowerThird                    editorial
   number            --->  Odometer                      raiz do kit
   chart, compare    --->  BarChart, ValueCompare ...    charts
   map               --->  GeoMap (Natural Earth)        geo
   network           --->  ExpandingNetwork              graph
   cena inteira      --->  SceneSlide, CameraRig,        raiz, motion,
                           SourceTag (rodapé), WordCaption  editorial
   host (opcional)   --->  janela do apresentador        host (+ host/dicebear)

 Quando o kit muda
   PR no motion-kit -> npm pack -> troca o .tgz em video/vendor -> npm ci
   -> nova versão do vídeo-régua (scripts/provisorio/evolucao.py, sonda de CPU antes)
   -> a folha de quadros deve mudar só os planos que o PR pretendia
```
