# 007 — Contratos de dados e política de licenças

- **Status:** aceito
- **Data:** 2026-09-25
- **Etapa do roadmap:** #3

## Contexto

O §6 do CLAUDE.md lista os campos dos manifestos, mas deixa em aberto a granularidade das cenas, como a
aprovação humana é registrada, quais licenças podem chegar ao render e o formato do vídeo. A
`docs/spec-v0.4.md` original não está no repositório; os contratos saem do CLAUDE.md.

## Decisões

1. **Uma cena = um bloco de narração = um WAV = um visual.** Com 20–35 cenas em 5–7 min (~14 s cada),
   trocar uma frase ou uma imagem invalida só aquela cena. Um mapa pode voltar em várias cenas, por isso o
   ativo usa `used_in_scenes` (lista) em vez do `used_in_scene` do §6.
2. **Claims citam fonte e, opcionalmente, trecho.** `source_ids` continua obrigatório (§2.2);
   `excerpt_ids` (`source-01#E3`) já existe e precisa pertencer às fontes citadas. Vira obrigatório quando
   a ADR 002 (etapa 26) for aceita.
3. **`review.json` é a fonte única das decisões humanas.** Entradas só são acrescentadas, por etapa,
   cena ou ativo, com `input_hash` do que foi revisado: se o conteúdo muda, a aprovação deixa de valer.
   O `review_status` dos outros manifestos é só reflexo, escrito pelo código.
4. **Lista fechada de licenças aceitas** para um ativo chegar a `approved`: `PD-US`, `PD-old`, `CC0-1.0`,
   `CC-BY-2.0/2.5/3.0/4.0`, `Flickr-NKCR`, `Pexels`, `Generated` (Workers AI) e `Original` (gráfico do
   projeto). Ficam **fora**, e portanto em revisão humana: CC-BY-SA (o compartilhamento pela mesma licença
   poderia alcançar o vídeo inteiro), qualquer NC (o canal pretende monetizar) e licença não identificada.
   Regras adicionais para aprovar: `sha256` do arquivo final; domínio público exige o raciocínio em
   `usage_notes`; CC-BY exige `author` e `attribution_text`; ativo de acervo exige `page_url`.
   Decisão de negócio do dono do projeto, não parecer jurídico.
5. **Formato do vídeo:** 1920×1080, 30 fps, áudio 48 kHz, 16:9 validado no `episode.json`; a prévia em
   1280×720 é opção do render, não do contrato.

## Consequências

- `app/pipeline/schemas.py` implementa tudo acima; `tests/fixtures/episodes/pilot-example/` é o exemplo
  de referência (conteúdo fictício, URLs `example.org`).
- Regras entre arquivos são funções: `unknown_source_refs` (§2.2) e `visual_need_violations` (§2.4:
  Pexels e Workers AI nunca como `historical_exact`).
- `script.json` ainda não tem schema: nasce na etapa 27 com o formato que o LLM precisar produzir.
- Ampliar a lista de licenças exige nova ADR.

## Emenda — 2026-09-26

`CC-BY-3.0-BR` (Creative Commons Atribuição 3.0 Brasil, mesmos termos do CC BY 3.0, usada pela Agência
Brasil) entra na lista, com as mesmas exigências de `author` e `attribution_text`. Aprovado pelo dono do
projeto na pesquisa da fatia Votorantim (`docs/pesquisa/votorantim-viabilidade.md`).

## Emenda — 2026-09-26 (bancos de imagem)

Pixabay, Unsplash e Coverr entram na lista ao lado do Pexels, para fotos e B-roll de ilustração (abertura v2 da
Votorantim, #48). Os termos foram lidos nas páginas oficiais em 2026-09-26 e estão registrados em
`data/benchmarks/termos-bancos-de-imagem.md`. Decisão do dono do projeto, não parecer jurídico.

1. **Licenças novas:** `Pixabay` (Content License), `Unsplash` (Unsplash License) e `Coverr` (licença própria da
   Coverr). A parte do acervo em CC0 (no Pexels, quando a página indica; no Pixabay, o que foi publicado antes de
   9/1/2019) entra como `CC0-1.0`. Um ativo de banco só é aprovado com a licença do próprio banco ou `CC0-1.0`, e
   a licença de um banco não vale para outro provedor.
2. **Regra comum para aprovar um ativo de banco** (Pexels, Pixabay, Unsplash, Coverr):
   - `page_url`;
   - `author` e `attribution_text`: o crédito vai para o `credits.txt` e a descrição mesmo quando a licença não
     exige, porque as APIs do Pexels e do Unsplash pedem;
   - `usage_notes` com a conferência humana dos direitos de terceiros, que as quatro licenças deixam com o
     usuário: nenhuma pessoa reconhecível em close, nenhuma pessoa retratada como doente ou tomando remédio,
     nenhuma marca, logo ou texto visível, nenhum uso em contexto político.
3. **Nunca registro:** os quatro bancos entram em `visual_need_violations` (nunca `historical_exact`, §2.4).
4. **Pixabay:** adapter pela API (100 requisições por 60 s, respostas em cache por 24 h, arquivo baixado em vez
   de hotlink). Sem aprovação de acesso completo, a foto chega a no máximo 1280 px: usar de preferência para vídeo.
5. **Unsplash:** adapter pela API, só para foto (a API não tem vídeo), em modo demo (50 requisições por hora).
   O adapter cumpre os termos da API:
   - chama `download_location` a cada download;
   - grava o crédito "Photo by <autor> on Unsplash", com links para o perfil do autor e para o Unsplash
     (`utm_source`, `utm_medium=referral`), no `credits.txt` e na descrição.

   A foto editada dentro do vídeo é tratada como obra derivada, que as diretrizes dispensam do hotlink ("If the
   image is remixed to create a derivative creative image, these results do not need to be hotlinked"). Essa
   leitura é do dono do projeto: os termos da API foram escritos para apps que exibem as imagens e não tratam de
   vídeo.
6. **Coverr:** só clipes baixados à mão pelo dono no site, sob a licença da página `/license`. Não há adapter de
   API enquanto a documentação da API disser que o acesso gratuito não cobre "commercial use", o que contradiz a
   página de desenvolvedores. Ficam de fora os vídeos da Shutterstock que aparecem nas listagens e os clipes
   marcados "AI Generated".
7. **Áudio:** o B-roll de banco entra sem som. O template já faz isso; os termos do Pexels e do Pixabay citam
   "audio or video samples" entre os possíveis direitos de terceiros.

## Emenda proposta — 2026-10-17 (programa de criadores do detentor)

**Status:** proposta, sem decisão. Depende da resposta da KADOKAWA ao e-mail sobre o CSP e da decisão do dono. Até
lá, nada muda no código nem na lista acima. Contexto: `docs/pesquisa/reports/Nicho recap de anime.md` (adendo CSP) e
`docs/pesquisa/research_notes/Nicho recap de anime/csp_kadokawa.md`.

1. **Licença nova `Holder-Program`.** Cobre trecho de vídeo ou quadro de uma obra de terceiros usado sob um
   programa oficial do próprio detentor (o primeiro caso é o Creator Support Program da KADOKAWA). Vale só para os
   títulos cuja diretriz publicada cubra o uso. Título sem diretriz continua fora.
2. **Para aprovar o ativo**, além de `sha256` e `page_url`:
   - `program` (ex.: `KADOKAWA-CSP`) e a obra: título, episódio e o `source_sha256` da importação (#156);
   - cópia datada da página da diretriz guardada no episódio, com URL, data e `sha256`. As diretrizes somem sem
     aviso; a de *Mattan* já sumiu;
   - limite da diretriz em segundos por episódio de origem e por vídeo publicado. O `vp check` soma os trechos de
     cada episódio, pelos PTS do índice da #156, e barra o que passar do limite;
   - `attribution_text` exigido pela diretriz, copiado para a descrição e o `credits.txt`;
   - `usage_notes` com a conferência humana de música, miniatura, voz e plataforma, e a data do pré-registro do canal.
3. **Só YouTube.** O vídeo com ativo `Holder-Program` não pode ser agendado em outra rede pelo `vp postiz`
   (ADR 025). Nas outras redes, só material próprio que leve ao vídeo do YouTube, se a diretriz permitir.
4. **Fora até haver resposta escrita do detentor:** personagem gerado por IA, fan art, música do anime e imagem de
   episódio na miniatura.
5. **Diretriz que muda ou some:** a cópia guardada prova a permissão na data. Ativo ainda não aprovado volta a
   `needs_review`; vídeo já publicado mantém o registro.
6. **Reivindicação esperada:** o detentor reivindica o vídeo e fica com parte ou toda a receita. A reivindicação não
   pode ser contestada, e isso deve constar no pacote do gate 4.

Decisão do dono do projeto, não parecer jurídico. Ao ser aceita, a emenda exige o schema novo em
`app/pipeline/schemas.py`, o check de tempo por episódio, o bloqueio no `vp postiz` e a atualização do §6 do CLAUDE.md
no mesmo commit.

## Emenda proposta — 2026-10-17 (citação para crítica: quadros e miniatura)

**Status:** aceita pelo dono em 2026-10-17 ("sim, aceito a emenda"), com as opções 3 (quadros parados como
citação dentro do vídeo) e 4 (quadro da obra na miniatura) e os limites abaixo. **Implementação pendente:** até o
schema e o check entrarem, nenhum ativo `Citacao` chega a `approved`.

**Implementada em 2026-10-17:**
- em `app/pipeline/schemas.py`: `Provider.OFFICIAL`, a licença `Citacao` e o campo `work`;
- no `vp check`: `citation_violations` (quadros por vídeo, tempo de tela estimado e proibição de B-roll);
- testes em `tests/test_citation.py`;
- §6 do CLAUDE.md atualizado.

O tempo real só existe depois da voz. A miniatura, as franquias fora e o strike ficam no gate, sem regra em
código. Contexto:
`docs/pesquisa/reports/Nicho recap de anime.md`, adendos de demanda e franquias. Decisão de risco do dono, não
parecer jurídico. A base é a citação para crítica (Lei 9.610/98, art. 46, III: "na medida justificada para o fim a
atingir") e o exemplo do YPP "Using clips for a critical review".

1. **Licença nova `Citacao`.** Cobre só quadro parado de uma obra que é assunto do argumento do vídeo (ensaio,
   análise, crítica). Ficam fora: trecho de vídeo, áudio da obra, painel em sequência que reproduza uma cena e
   arte promocional (pôster, key visual).
2. **Dentro do vídeo:**
   - até **10 quadros** por vídeo;
   - cada quadro na tela **só enquanto a narração comenta aquele quadro**, até **8 s**;
   - quadros seguidos não podem imitar movimento;
   - recorte e zoom para destacar o que se comenta são permitidos;
   - o quadro não pode ser espelhado nem disfarçado para escapar da detecção.
3. **Miniatura:** um quadro da obra, sem arte promocional, com texto ou gráfico nosso ocupando parte relevante da
   imagem. O dono confirma o risco da miniatura a cada vídeo, no gate 4.
4. **Origem do quadro: só material oficial público do detentor** (decisão do dono em 2026-10-17): trailer, PV,
   episódio publicado pelo próprio detentor ou licenciado no canal oficial dele, e site oficial. Mídia comprada
   fica para uma decisão futura. O print de streaming fica fora: a Crunchyroll limita o uso de capturas a fins não
   comerciais. A extração pode usar a #156 (frames com PTS) sobre essa origem, e o `page_url` aponta a publicação
   oficial. Para *Death Note* (2006; © D.N. Dream Partners, VAP, Shueisha, Madhouse, NTV), os candidatos são:
   - o trailer distribuído pela VIZ Media;
   - os 37 episódios que a VIZ publicou no próprio canal do YouTube, segundo a imprensa em 2022, só nos EUA. Isso
     falta conferir.
5. **Para aprovar o ativo:**
   - `sha256` e `page_url` (ou a descrição da mídia própria);
   - a obra (título, estúdio e detentor conhecido);
   - `usage_notes` com a **justificativa**: que trecho da narração o quadro ilustra e por quê;
   - `attribution_text` para a descrição e o `credits.txt`.

   Cada quadro passa pelo gate 3.
6. **Franquias fora** até haver evidência de como o detentor trata ensaios: obras da Toei (*One Piece*, *Dragon
   Ball*) e da ShoPro (*Pokémon*), que já tem strike por imagem parada.
7. **Reivindicação ou strike:**
   - registro no `review.json`;
   - nenhuma contestação sem decisão do dono;
   - **um strike suspende a série** até o dono revisar esta emenda.
8. **Contagem em código, quando aceita:** o `vp check` conta os quadros `Citacao` e o tempo de tela de cada um.

Ao ser aceita, a emenda pede no mesmo commit:
- a licença e os campos novos em `app/pipeline/schemas.py`;
- o check;
- a atualização do §2.3 e do §6 do CLAUDE.md.

## Emenda — 2026-10-21 (música da YouTube Audio Library)

**Status:** aceita pelo dono em 2026-10-21, junto com a ADR 030.

- A licença `YouTube-Audio-Library` entra na lista fechada. Ela vale só para faixas com `provider:
  youtube_audio_library`. O dono baixa essas faixas à mão pelo YouTube Studio, preferindo o filtro "Attribution
  not required".
- A faixa CC da biblioteca entra com a CC-BY da própria faixa, com `author` e `attribution_text`, como as
  outras CC-BY.
- `usage_notes` é obrigatório: título, data do download, tipo de licença mostrado na coluna "License type" e
  voz cantada (sim ou não).
- **Só vale em vídeo publicado no YouTube.** A página oficial não cobre o uso fora da plataforma
  (`data/benchmarks/termos-musica.md`). Corte para Reels, TikTok e afins sai sem essas faixas.
- Faixas do Pixabay Music e do Suno continuam fora, até uma decisão à parte (ADR 030).

## Emenda (2026-10-23): `metrics.json`, as métricas de publicação

Decisão do dono em 2026-10-23, sobre o contrato D6 que ele aceitou em 2026-10-14 (spec do workspace, "Medir e
fechar o ciclo"). Os vídeos começaram a sair em outubro e não havia onde registrar os números do §12.

- `data/episodes/<id>/metrics.json` (`PublicationMetrics`): `platform`, `channel`, `format` (`longo`, `reel`,
  `clipe`, `story`), `published_at` com fuso, `url`, `post_id` do Postiz, `series`, `duration_s`, `hypothesis` (a
  hipótese de forma, #122), `readings` nas janelas `d7` e `d28` e `requests` (pedidos vistos nos comentários,
  resumidos, sem dado pessoal). Publicação sem pasta de episódio (clipe, story) fica em
  `data/publicacoes/metricas/<id>.json`.
- Uma leitura traz `read_at` e os números lidos à mão: `views`, `likes`, `shares`, `comments`, `saves` (D6) e, no
  YouTube, `impressions`, `ctr_percent`, `avg_view_duration_s`, `retention_30s_percent`, `subscribers_gained` e
  `traffic_sources`. **O que não foi lido fica `null`, nunca zero.** Leitura antes de a janela fechar é erro; cada
  janela é lida uma vez (refazer é explícito).
- A data, o canal e o id do post vêm de `data/publicacoes/registro.jsonl` (ADR 025), que passa a ser versionado.
  Os números entram por `scripts/provisorio/metricas.py` (`iniciar`, `ler`, `pendentes`, `tabela`), até virar
  `vp metricas`. Sem API do YouTube nesta fase (§12).
- `vp status` mostra as janelas e lista as vencidas sem leitura nas pendências; `vp check` valida o arquivo e avisa.
- A tabela consolidada (`data/publicacoes/metricas.csv`, uma linha por janela) é gerada, nunca editada à mão, e só
  compara iguais com iguais (longo com longo, Reel com Reel).

## Emenda (2026-11-03): clipe em movimento como citação para crítica

**Status:** aceita pelo dono em 2026-11-03 ("EU ASSUMO OS RISCOS"), a pedido dele, para o guia mastermind estoico
(`data/episodes/guia-mastermind-estoico/pauta.md`). **Implementada em 2026-11-03 (parcial):** `Asset.media` (`still` ou `clip`), `origin` e `timecode`, o provedor
`owner_capture`, a regra "clipe só em B-roll, quadro parado só em foto" e a ausência de teto numérico, com testes em
`tests/test_citation.py`. O `vp numeros` lista quadros e clipes (tipo, cena, âncora, obra, timecode, origem e tempo de tela;
`app/pipeline/numbers_citations.py`). **Pendente:** o bloqueio do `vp postiz` fora do YouTube e conferir que o render
do B-roll de clipe sai sem o áudio da obra. Decisão de risco do dono, não parecer jurídico.
Estende a emenda de 2026-10-17 (citação para crítica); onde esta emenda não diz outra coisa, aquela vale.

1. **Clipe de obra de terceiros que é assunto do argumento** (ensaio, análise, crítica) passa a ser aceito como
   `Citacao` com `media: clip`, além do quadro parado (`media: still`). Continuam fora: o **áudio da obra** (o clipe
   entra sem som; a trilha e a voz são nossas), arte promocional e a obra como pano de fundo sem comentário.
2. **Sem teto numérico de clipes** (decisão do dono, 2026-11-03: "retire todos os limites"). Valem só duas condições,
   que sustentam a citação:
   - o clipe entra **sem o áudio da obra**;
   - cada clipe só está na tela **enquanto a narração comenta aquele trecho**.
   O `vp check` conta e lista os clipes e o tempo de tela de cada um no pacote do gate 4, sem barrar por número. O
   limite de 10 quadros parados de 8 s da emenda anterior vale só para `kind: still`.
3. **Tratamento visual.** Recorte, zoom e grade de cor (inclusive preto e branco) valem como escolha de estilo do
   canal. Ficam proibidos espelhar a imagem e alterar a velocidade ou a altura do áudio **para escapar da detecção**
   (continua a regra da emenda de 2026-10-17).
4. **Origem não precisa mais ser material oficial.** O dono escolhe a origem e responde por ela. Para aprovar o ativo:
   - `work` (título, episódio, estúdio e detentor conhecido), `timecode` de entrada e saída, `sha256` do clipe e a
     descrição de onde veio (`origin`);
   - `usage_notes` com a **justificativa**: que trecho da narração o clipe ilustra e por que o comentário o exige;
   - `attribution_text` para a descrição e o `credits.txt`;
   - a decisão do dono de assumir o risco registrada no `review.json` do ativo.
5. **Franquias.** A regra da emenda anterior (Toei, ShoPro fora) continua. *The Mentalist* (Warner Bros.) e as
   franquias do guia (*Classroom of the Elite*, *Death Note*) entram por decisão do dono, **um vídeo por vez**, e a
   primeira publicação com clipe é o teste: se vier reivindicação ou aviso, o próximo episódio com clipe espera a
   revisão desta emenda.
6. **Só YouTube.** Vídeo com clipe não é agendado em outra rede pelo `vp postiz`; nas outras redes sai só material
   próprio que leve ao vídeo.
7. **Reivindicação ou strike:**
   - a reivindicação é **esperada** e pode tirar a receita do vídeo ou bloqueá-lo em países; o pacote do gate 4 diz isso;
   - registro no `review.json`; nenhuma contestação sem decisão do dono;
   - **um strike suspende a série** até o dono revisar esta emenda.
8. **Miniatura:** sem mudança; o dono confirma o risco a cada vídeo, no gate 4.

Ao ser implementada, a emenda pede no mesmo commit: o campo `kind` e os campos de origem em
`app/pipeline/schemas.py` (modelos em arquivos próprios, ADR 037; constantes em classe, ADR 038), a contagem no
`vp check` (`citation_violations`), o bloqueio no `vp postiz`, testes em `tests/test_citation.py` e a atualização do
§6 do CLAUDE.md.

## Emenda (2026-11-09): clipe animado do projeto como ativo `Original`

**Contexto.** A ADR 001 (item 5) previu o "gráfico como ativo": uma cena gráfica animada vira um clipe gerado pelo projeto, registrado como ativo
`Original` com `sha256`, componente e props, e revisado no gate 3 como uma foto. O modelo `Asset` não permitia isso: a emenda de 2026-11-03 limitou
`media: clip` à licença `Citacao`, e não havia comando que registrasse um ativo sem banco de imagem. O episódio `mec-fechadura-pt` (37 planos `broll`
em 19 composições Remotion, nenhum com foto ou banco) expôs a lacuna. Escolha do dono em 2026-11-09: emendar a ADR e criar o comando, em vez de registrar
o MP4 à mão como foto.

**Decisões.**
1. `media: clip` vale também para a licença `Original`. A emenda de 2026-11-03 continua valendo para o clipe citado (`Citacao`), sem mudança.
2. Para um clipe `Original` chegar a `approved`: `provider: original`; `origin` com a **composição e o arquivo de código** que o geram (por exemplo
   `video/src/previews/<id>/index.tsx#<Composição> (variant=...)`); `usage_notes` com props, duração e a conferência de pessoas, marcas e texto de
   terceiros no clipe; `sha256` do `.mp4`. `timecode` não se aplica (é só do clipe citado) e é recusado.
3. `vp assets original <id> <cena> <arquivo.mp4> --asset-id ID --composicao ... --notas ...` copia o `.mp4` para `assets/<asset-id>.mp4` e grava
   `assets/<asset-id>.json` em `needs_review`, pelo mesmo caminho do `take` (`AssetIntake`): o JSON vai por último, repetir a mesma mídia é idempotente,
   a cena entra em `used_in_scenes` sem apagar as anteriores, uma nova renderização de ativo **não aprovado** substitui a mídia, e ativo **aprovado nunca é
   alterado** (mídia diferente de um aprovado é erro com a instrução de `vp reopen --step assets --asset <id>`). Só aceita `.mp4` existente e não vazio.
   Não chama banco, rede nem provedor pago.
4. A aprovação continua humana (`vp approve <id> --step assets --asset <asset-id>`, gate 3). Nada nesta emenda aprova direitos: a conferência de que o
   clipe não tem pessoa, marca nem texto de terceiros é de quem registra e de quem aprova.

**Fora desta emenda.** Cortar cada clipe nas âncoras reais da narração (o `vp render` ainda não gera clipes por plano a partir de composições) e o
render dos clipes em vídeo, que só acontece com autorização do dono.

**Implementação (mesmo commit).** `Asset._original_clip_problems` e as constantes `ORIGINAL_LICENSE` e `CLIP_LICENSES` (`app/pipeline/models/asset.py`,
`app/pipeline/constants/schemas_constants.py`); `AssetIntake.register_local` (`app/pipeline/assets.py`); subcomando `original` (`app/commands/assets.py`);
testes em `tests/test_assets_original.py`; §6 e §10 do CLAUDE.md.

## Emenda proposta (2026-11-14): imagem gerada pelo dono no Gemini como ativo `Generated`

**Status:** proposta, escrita a pedido do dono em 2026-11-14. Vale quando o dono aprovar. Ela registra o que já se faz na
prática desde a decisão do dono de 2026-10-27 (a pele dele, gerada no ChatGPT) e das imagens de `idade-media-ser-rico`
(2026-11-06). Decisão de risco do dono, não parecer jurídico.

**Contexto.** O item 4 desta ADR só aceita `Generated` do Workers AI (Cloudflare), e o código liga a `generation`
(prompt, modelo, semente e passos) a esse provedor (`Asset._generation_consistency`). O formato "como era ser X"
(ADR 055) passou a usar ilustrações geradas pelo dono no **app Gemini da conta pessoal dele**, registradas como `Generated`
com `provider: original` e o gerador "a confirmar" no texto. O dono confirmou o gerador em 2026-11-14 ("foi gerado via
Gemini"), e os termos do Google foram lidos no mesmo dia (`data/benchmarks/termos-gemini-imagem.md`). O vídeo com
essas imagens teve o melhor CTR do canal (4,2%).

**Decisões.**
1. **Imagem gerada pelo dono** num gerador dele entra como `license_id: Generated`, `provider: original`, sem o campo
   `generation`. Esse campo continua exclusivo do Workers AI, porque semente e passos só existem lá.
2. **Só entra gerador com termos registrados** em `data/benchmarks/`: páginas oficiais, data da consulta, quem é dono do
   resultado, uso comercial e aviso de IA. Hoje:
   - **Gemini** (app, conta pessoal): registrado em `termos-gemini-imagem.md`. O Google não reivindica a imagem
     gerada, nenhuma cláusula proíbe uso comercial, e é proibido apresentar a imagem como feita só por humano.
   - **ChatGPT**: `termos-chatgpt-imagem.md` segue pendente (as páginas recusam leitura automática). Vale a decisão do
     dono de 2026-10-27 para a pele dele. Imagem nova de cena no ChatGPT espera esse registro.
3. **Para chegar a `approved`** (gate 3):
   - `sha256` do arquivo;
   - `usage_notes` com o **gerador** ("Gemini, app, conta pessoal do dono"), a **data**, o **prompt** usado (ou o id do
     prompt no `prompts-cenas.md` do episódio), o estilo e a conferência de pessoas, marcas e texto;
   - `author` e `attribution_text` como nos outros ativos próprios.

   O mesmo vale para a linha do `registro.csv` do episódio.
4. **Limites do conteúdo**, além do §2.4 do CLAUDE.md (ilustração, nunca registro de época):
   - nada de rosto de pessoa real, franquia de terceiros nem estilo copiado de outro canal;
   - sem texto dentro da imagem;
   - valem os itens gerais da política de uso proibido do Google (direitos de terceiros, filtros, ódio, assédio,
     violência, conteúdo sexual).
5. **Aviso.** Os créditos e a descrição dizem "ilustrações geradas por IA". O rótulo de conteúdo alterado ou sintético
   do YouTube continua pela regra do §2.4: obrigatório para imagem **realista** de fato histórico; para desenho, é
   decisão do dono no gate 4.
6. **Ponto em aberto, decisão de risco do dono:** os termos do Google tratam como "consumidor" quem usa os serviços de
   forma pessoal e não comercial. As páginas não dizem se um canal monetizado muda a conta para "usuário empresarial",
   que tem outras regras de responsabilidade. Isso não tira o direito de usar a imagem.
7. **`idade-media-ser-rico`:** os ativos aprovados ficam como estão (§2.6), com o gerador "a confirmar" no texto. Esta
   emenda e `termos-gemini-imagem.md` são o registro do gerador. Corrigir os `usage_notes` exige reabrir o gate 3
   (`vp reopen --step assets --asset <id>`), se o dono quiser.

**Implementação.** Nenhuma mudança de código: o modelo já aceita `Generated` com `provider: original` e sem `generation`.
Pendentes:
- o registro em lote hoje é um script preso ao episódio anterior (`scripts/provisorio/registrar_imagens_ia.py`, com o
  episódio e o gerador fixos no código). Falta torná-lo parametrizado (episódio, gerador) ou criar um subcomando do
  `vp assets`;
- um aviso do `vp check` quando um `Generated` com `provider: original` não cita o gerador no `usage_notes`;
- ao aprovar: item 4 desta ADR e §6 e §8 do CLAUDE.md.

## Emenda (2026-11-14): clipe de anime como textura, sem comentário, num episódio

**Status:** aceita pelo dono em 2026-11-14 para o episódio `vazio-de-ter-tudo`, depois de saber que a emenda de
2026-11-03 só aceita clipe enquanto a narração comenta a obra e deixa fora "a obra como pano de fundo sem comentário".
Pergunta feita: "manter como fundo" pede emendar esta ADR, como decisão de risco do dono, com mais chance de
reivindicação do Content ID por obra; resposta: "Manter como fundo". Decisão de risco do dono, não parecer jurídico:
sem comentário, a citação para crítica deixa de sustentar o uso.

1. **Escopo:** só o episódio `vazio-de-ter-tudo` e os Shorts cortados dele. Outro episódio precisa de nova decisão.
2. **O que muda:** nesse episódio, clipes de anime podem entrar como B-roll de textura, sem a narração comentar a
   obra. O resto da emenda de 2026-11-03 continua: sem o áudio da obra; só no YouTube (Short com anime não vai para o
   Instagram); `work`, `timecode`, `origin` e `sha256` por ativo; `attribution_text` na descrição e no `credits.txt`;
   a decisão de risco registrada no `review.json` de cada ativo no gate 3.
3. **Origem:** só trailers e vídeos de divulgação publicados em canais oficiais ou de distribuidora licenciada
   (`data/episodes/vazio-de-ter-tudo/candidatos/anime/LEIAME.md`). Toei e ShoPro continuam fora.
4. **Sem truque de detecção:** recorte, zoom e cor valem como estilo; espelhar ou mudar velocidade ou altura para
   escapar da detecção continua proibido (emenda de 2026-10-17).
5. **Teste:** a primeira publicação é o teste. Reivindicação ou aviso vão para o `review.json` do episódio, e nenhum
   outro episódio usa textura de anime antes de o dono rever esta emenda.

## Emenda (2026-11-26): clipe de vídeo gerado pelo dono como ativo `Generated`

**Contexto.** O dono pediu, em 2026-11-26, um piloto de Short feito com clipes gerados no Google Flow
(`data/episodes/flow-piloto-colheita/`). O modelo só aceitava `media: clip` com `Citacao` ou `Original`. Os termos do
Flow foram lidos no mesmo dia (`data/benchmarks/termos-google-flow.md`): o Google não reivindica o resultado, mas não
libera o uso comercial por escrito. O dono decidiu seguir ("pode fazer as três"). Decisão de risco do dono, não parecer
jurídico.

**Decisões.**
1. `media: clip` vale também para `license_id: Generated`, com `provider: original` e sem o campo `generation`
   (que segue exclusivo do Workers AI), como a imagem gerada da emenda proposta de 2026-11-14.
2. Para chegar a `approved`: `origin` com o **gerador, o modelo e o projeto** de onde o clipe saiu; `usage_notes` com o
   prompt e a conferência de pessoas reais, marcas e texto no clipe; `sha256` do `.mp4`. `timecode` é recusado.
3. Só entra gerador com termos registrados em `data/benchmarks/` (hoje: `termos-google-flow.md`).
4. Clipe gerado é ilustração (§2.4), nunca registro do fato. A narração é sempre do projeto; do áudio do gerador,
   só o **som ambiente** (fogo, vento, animais) pode entrar, bem abaixo da voz e sem fala nem música geradas
   (decisão do dono de 2026-11-26, no piloto: a trilha do catálogo não combinava com a cena).
   Cena com aparência realista leva o rótulo de conteúdo sintético no Studio; a descrição diz que as cenas foram
   geradas por IA.
5. Aprovação humana no gate 3, como qualquer ativo.

**Implementação (mesmo commit).** `Asset._generated_clip_problems` e a constante `GENERATED_LICENSE` em
`CLIP_LICENSES` (`app/pipeline/models/asset.py`, `app/pipeline/constants/schemas_constants.py`); testes em
`tests/test_assets_generated_clip.py`.
