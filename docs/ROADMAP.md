# Roadmap — etapas entregáveis (#1–#31, #41–#43, #48, #69–#82)

Cada etapa é uma issue no GitHub com o mesmo número (etapa N = issue #N) e pertence a um milestone
que segue a ordem de implementação do §11 do `CLAUDE.md`. Gerado a partir de uma fonte única;
detalhes e critérios de aceite completos estão nas issues.

Fluxo técnico de refatoração (2026-11-01):
[sequência SOLID com gates RF0–RF7](fluxo-refatoracao-solid-2026-11-01.md), baseada no inventário dos scripts
e nos gaps de arquitetura. A situação histórica dos episódios e das issues abaixo é preservada.

## Situação em 2026-09-29

O formato explicativo (#48, #69–#82, no fim deste arquivo) passou na frente do piloto documentário. O histórico
e as pendências em ordem estão em "Etapa atual e pendências", logo abaixo da tabela.

| Issues | Situação |
|---|---|
| #1–#10 | Fechadas. |
| #11 | Em pausa até o modelo de planos estabilizar. |
| #12 | Parcial: `vp approve`, `vp reject` e `vp status` (PR #67); faltam `vp new` e `vp reopen`. |
| #13, #16 | `vp voice` e `vp render` (RF7, 2026-11-01) fazem voz e render; o script `montar_episodio.py` saiu. |
| #15 | Adapter Kokoro existe (usado no `vp bench` e no script de voz); falta o glossário de pronúncia. |
| #19–#22 | Adapters Pexels, Pixabay e Unsplash feitos na #48 (PRs #61–#63); Commons e Arquivo Nacional só pelos scripts provisórios de busca e download; `vp assets` não existe. |
| #26 | Parcial: `vp sources add\|declared` (RF7, ex-`baixar_fonte.py` do PR #68) e `vp excerpts`. |
| #27, #28 | Adapter Ollama existe; `vp script` e `vp scenes` não. Desde a ADR 009, fichas, roteiro e cenas saem dos agentes (pesquisador, roteirista, verificador) validados pelo `vp check`; o Ollama ficou como candidato (§7). |
| #14, #17, #18, #23–#25, #29–#31, #41, #42 | Não começadas. #17 (legendas) e #18 (pacote) são necessárias antes de publicar. |
| M2–M7 do piloto documentário | Em pausa. |

## Estado e pendências movidos do `CLAUDE.md` em 2026-11-16

O `CLAUDE.md` passou ao formato curto e normativo do dono (2026-11-16). O que era estado, história e pendência
veio para cá sem mudança de texto; as regras em vigor ficaram lá. Referências "§N" antigas: ver o mapa no fim do
`CLAUDE.md`.

### Recortes e linhas do canal (era o §1)

- **Recorte da validação:** expedições e desastres de 1880–1930, janela com fotografia em domínio público,
  jornais digitalizados gratuitos e memórias em DP. Piloto: expedição polar de cauda longa (Greely 1881–84,
  Karluk 1913 ou Belgica 1897–99). Episódio 2 ou 3: expedição sul-americana contada em inglês
  (Roosevelt–Rondon 1913–14), o diferencial do canal.
- **Formato explicativo (em teste, #48):** perfil de "dinheiro e poder" de uma pessoa ou família, no estilo How
  Money Works, com tom crítico e documentado (nem herói, nem vilão). Modelo em
  `docs/pesquisa/modelo-perfil-de-poder.md`. Primeiro caso: Grupo Votorantim / família Ermírio de Moraes, em
  pt-BR. O piloto documentário continua no roteiro.
- **Público e duração (decisão do dono, 2026-11-14):** jovens de 20 a 30 anos com desânimo profundo. O próximo longo
  testa 8 a 9 min no lugar de ~12: as curvas de retenção dos dois melhores longos são iguais no mesmo relógio, e as
  pessoas ficam uns 3 min (`docs/pesquisa/retencao-idade-media-2026-11-14.md`; seção "Retenção e público" das
  skills de roteiro e de edição).
- **Ensaio (épico #164, desde 2026-10):** vídeo longo (~12 min) em pt-BR no molde do nicho de ensaio sobre filosofia
  (ADR 031): título e miniatura falam do pensador ou da ideia; o anime entra só como caso dentro. Canais de referência
  Filosofatos e Inferno de Dante (`docs/pesquisa/roteiro-referencias-2026-10-20.md`); piloto `death-note-fins-meios`.
  É a linha dos episódios agendados em outubro.
- **Evitar:** sobrevivência recente (fotos de agência, vira 100% ilustração gerada), true crime,
  Titanic/Hindenburg/Everest 1996 (saturados), Segunda Guerra (oceano de concorrentes).


### Estado atual (2026-10-22, era o §1)

**Vídeos técnicos — direção do dono em 2026-11-01:** todo vídeo deve explicar e representar visualmente
o impacto do conceito no **System Design da aplicação**: onde entra no fluxo, qual decisão muda e seus
benefícios, custos e limites. Priorizar conteúdo sobre **Java** nas próximas gerações da série "eu medi";
o próximo tema escolhido pelo dono é **CompletableFuture**. Planejar a explicação e os estados da animação antes da voz/render;
usar blocos conectados, setas e mudanças de estado para mostrar o mecanismo, com a linguagem explícita.
O vídeo explica o porquê com fontes; o fecho pode perguntar qual linguagem ou continuação o público quer.
Direção e critérios: `renders/serie-conceitos/direcao-editorial.md`; ordem atual em
`renders/serie-conceitos/fila.md`. O calendário original da série fica como histórico.
O quadro "Controle obrigatório em todo tema" da direção editorial deve estar preenchido na pauta
e conferido antes de voz/render e depois da montagem; uma lacuna impede avançar ou considerar a versão pronta.

**Referências da voz por cena (ADR 053, pedido do dono em 2026-11-01):** o `delivery` e o idioma
selecionam o WAV em `[chatterbox.references]` de `config/providers.toml`, para Shorts e vídeos longos,
localmente ou no Modal. Gravações em `data/voice-references/{pt-BR,en}/`, fora do Git; guia em
`docs/guia-gravacao-referencias-voz.md`. Sem mapeamento, usa a referência antiga; referência mapeada
ausente/inválida deixa a cena pendente. O cache usa a referência efetiva e os parâmetros da fala;
o manifest registra sua identidade por cena e o Short também registra arquivo/hash em `narracao.voz.json`.
O cliente não envia gravações junto da síntese: os WAVs precisam estar previamente no volume privado do Modal.
Com esse banco ativo, a geração também prepara cópias por cena em `voice/leveled/`, com alvo de −16 LUFS
e pico de −1,5 dBTP (ADR 054). A montagem usa essas cópias, preservando os WAVs brutos; mudar o volume
não exige chamar o TTS novamente. O Short registra as medições em `lines[].level`; o volume final
do vídeo continua sendo conferido depois da mistura com efeitos/trilha.

Primeiros agendamentos pelo Postiz em outubro de 2026, todos pela cadeia do §2.8 (clipes do Nabote em 17/10; o Reel
`confeitaria-erro-2-pt` em 19/10; `death-note-fins-meios`, `kira-voto-brasil`, `historia-vencedores` e
`epicteto-na-sua-mao` no Cena e Conceito, de 20 a 23/10; trilha em `data/publicacoes/registro.jsonl`). Agendado não
é publicado: conferir no YouTube Studio antes de reenviar. Métricas aos 7 e 28 dias ainda por registrar; nada de
produção em escala. Roteiro nas issues #1–#31, #41–#43, #48, #69–#82 e #164. Histórico e pendências:
`docs/ROADMAP.md` ("Etapa atual e pendências", escrita em 2026-09-30).

- **Foco (decisão do dono, 2026-10-22; cadência revista em 2026-11-14):** a cadência do Cena e Conceito, três
  ensaios longos por semana, **segunda, quarta e sexta** (no lugar do longo diário; base em
  `docs/pesquisa/frequencia-de-publicacao-2026-11-14.md`), mais os Shorts cortados deles, com pautas aprovadas em lote
  e o molde do nicho e a partitura antes de cada roteiro (ADR 031, §4). O visual segue a
  decisão de 2026-09-29: com calma, uma frente por vez, e toda mudança de template ou de motion-kit sai pelo
  vídeo-régua abaixo. Em pausa: #11 e M2–M7 do piloto documentário.
- **Vídeo-régua:** o `votorantim-dinheiro` (conteúdo congelado) ganha uma versão `vN` ao fim de cada PR que muda o
  visual (template ou motion-kit), com a sonda de CPU antes; autorização do dono só para este vídeo. Comando
  `vp evolucao` (`gerar`, `guardar`, `comparar`, `lado-a-lado`), vídeos em
  `renders/evolucao/`, registro em `data/benchmarks/evolucao-template.md`. A folha de quadros marca os planos que
  mudaram: um PR de visual deve mudar só os que pretendia.
- **Voz (ADR 016, aceita em 2026-10-12):** Kokoro nos rascunhos (`tts`), voz clonada do dono no vídeo final
  (`vp voice --voz-final`). Desde 2026-10-15 a voz final é `tts_final = "chatterbox_modal"` (ADR 024,
  aprovada pelo dono na escuta: a mesma voz numa GPU do Modal, segundos por cena). A alternativa local
  (`--voz=chatterbox`) é o Chatterbox na CPU, no ambiente próprio dele
  (`CHATTERBOX_PYTHON` e `CHATTERBOX_REFERENCE` no `.env`), uma cena por vez e ~30 vezes mais lenta que o tempo
  real. A gravação de referência é dado pessoal: fora do Git, nunca enviada a provedor, com uma exceção (ADR 024,
  2026-10-14): um volume privado da conta do dono no Modal, onde a mesma voz roda numa GPU T4
  (`--voz=chatterbox_modal`, função em `deploy/modal_chatterbox.py`; quem envia a gravação é o dono). Licença em
  `data/benchmarks/termos-chatterbox.md`. A Charon do Gemini (ADR 012) segue registrada (`--voz=gemini`; 3 chamadas
  por minuto e **10 por dia** na camada gratuita, termos em `data/benchmarks/termos-gemini-tts.md`) e é a voz do
  vídeo-régua, que não troca de voz. A voz neural pronta do Azure Speech (`pt-BR-AntonioNeural`, ADR 058) também
  está registrada (`--voz=azure_speech`; só na camada gratuita F0, 20 chamadas por minuto e 500 mil caracteres por
  mês; `AZURE_SPEECH_KEY` e `AZURE_SPEECH_REGION` no `.env`; termos em `data/benchmarks/termos-azure-speech.md`):
  proposta, ainda sem teste com a conta, e exige avisar que a voz é sintética.

### Provedores e política de escolha (era o §7)

| Função | Padrão | Candidato a teste | Critério de troca |
|---|---|---|---|
| Fichas, roteiro, cenas, checagem | Agentes do Claude Code + skills + `vp check` (ADR 009; a spec previa Ollama) | Ollama local (#27, checagem já medida em `data/benchmarks/checagem-local.md`); Groq e Gemini gratuitos; outro agente que leia as skills | Fidelidade ao texto-fonte e fatos que prendem, sem custo por chamada. |
| Narração | Kokoro local nos rascunhos; voz clonada do dono (Chatterbox local) no vídeo final (ADR 016) | Gemini TTS Charon (ADR 012, já com adapter); Azure Speech `pt-BR-AntonioNeural` na camada F0 (ADR 058, adapter pronto, sem teste com a conta) | Voz claramente melhor em escuta cega, nomes corretos, condições de dados aceitas, limite diário compatível. |
| Alinhamento de áudio | Frase: silêncios do WAV (ADR 021). Palavra: Groq Whisper gratuito com `--legenda-palavra` (ADR 023) | Whisper local (`transformers`, modelo no cache) | O áudio da cena sai da máquina só com pedido do dono na sessão; a tela mostra o texto do roteiro, não o reconhecido. |
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

### Ordem de implementação e critérios de aceite do piloto (era o §11)

Ordem: **(A)** experimento de motor da Fase 0 → **(B)** fixar `episode.json` e renderizar um episódio inteiro →
**(C)** CLI + Kokoro por bloco + timing + legendas → **(D)** adapters de busca/licença + galeria → **(E)** geração
condicional via Cloudflare + medidor de cota → **(F)** pesquisa assistida e revisão de roteiro com LLM →
**(G)** comparação pequena dos remotos, só para gargalo demonstrado. FastAPI e SQLite só quando arquivos e galeria
virarem obstáculo real, com a exceção de telemetria editorial da ADR 032.

Piloto aceito quando:

- [ ] Pauta + ≥ 2 fontes independentes para os fatos principais, em `sources.json`.
- [ ] Roteiro em inglês revisado, dividido em cenas, toda claim relevante com `source_ids`.
- [ ] Galeria com ≥ 1 opção visual por cena e direitos registrados; geração só para lacunas.
- [ ] Narração local, legendas editáveis, prévia renderizada, revisão por cena registrada.
- [ ] Export completo; **zero** custo de API paga.
- [ ] Métricas registradas: duração de cada etapa, imagens encontradas/geradas, decisões e rejeições humanas,
      horas humanas totais.

### Decisões pendentes e ajustes propostos sobre a spec v0.4 (era o §13)

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

### Agentes candidatos e modelo local (era o §15)

**Modelo local (Ollama, #27).** `prompts/local/` guarda o método das etapas em prompts curtos, uma chamada por
unidade (uma afirmação, uma cena), com o schema de saída em código. Hoje só `checagem.md` (afirmação × trecho),
medido por `scripts/bench/checagem_local.py` (resultados em `data/benchmarks/checagem-local.md`). O `vp check`
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

### Referências técnicas verificadas (23–24/09/2026)

A spec v0.4 original não está no repositório; itens verificados: WSL, Ollama, Groq, Gemini, OpenRouter, Cloudflare Workers AI, Pexels,
Wikimedia Commons, Library of Congress, Kokoro-82M, FFmpeg, Remotion e as políticas do YouTube (monetização,
divulgação de IA, retenção/CTR, YPP).

## Etapa atual e pendências (movido do `CLAUDE.md` em 2026-10-05; estado de 2026-09-30)

Roteiro completo nas issues #1–#31, #41–#43, #48 e #69–#82 (`docs/ROADMAP.md`). A #48 foi antecipada: fatia
vertical do formato explicativo antes do piloto documentário. Nenhum vídeo publicado ainda.

- [x] **M0 · Fase 0** (#1–#9): ambiente, base, contratos, arquitetura, bench, motores (ADR 001).
- [x] **#10** estado, cache por `input_hash` e aprovação imutável.
- [x] **#48, passos 1–3:** planos tipados e `episode.json` v2 em pt-BR (ADR 008); Remotion + motion-kit no
  `main` com o template "negócios moderno" (tarja sobre a foto, mapa com contornos, números na forma da ficha).
- [x] **ADR 009:** agentes das etapas criativas (§15), `facts.json`, trechos numerados, `vp excerpts`, `vp check`;
  modelo de perfil de poder (tipos `impact_today` e `rule`, perguntas neutras, controvérsia atribuída).
- [x] **Protótipo `votorantim-fatia`** (90 s, 1914–1962): gate 1 aprovado; gate 2 com mudanças pedidas
  (faltava o objetivo: impacto hoje e como virou elite), o que originou o modelo de perfil.
- [x] **Protótipo `votorantim-abertura` v1** (80 s, modelo de perfil: gancho de impacto, ponte, origem,
  promessa): gate 2 com mudanças pedidas (gancho só com cartões de número). O gate 1 voltou ao dono
  (ajuste de F38). A v1 fica em `renders/v1-final.mp4` e `v1/`.
- [x] **Abertura v2** (79 s): gancho com fotos e B-roll do Pexels (sacos de cimento, pátio de carros,
  blister, torre de transmissão), S08 sem a dedução sobre acionistas. Termos das quatro fontes
  (`data/benchmarks/termos-bancos-de-imagem.md`), contrato (ADR 007, emenda de bancos de imagem), adapters
  Pexels/Pixabay/Unsplash, gates 1 e 3 registrados, verificador aprovou, render em `renders/final.mp4` (a v1
  fica em `renders/v1-final.mp4`). **Gate 2 aprovado em 2026-09-27.** Falta o gate 3 do retrato
  `an-jose-ermirio`; Pixabay e Unsplash aguardam as chaves.
- [x] **`votorantim-completo`** (47 cenas, ~7 min 35 s, 128 planos): gates 1 e 2 aprovados em 2026-09-27; prévia
  sem imagens em `votorantim-completo-previa`; mapa de lacunas em `lacunas.md`. Roteiro anterior à ADR 011.
- [x] **Diagnóstico do visual (#69)** e sugestões #70–#82; motion-kit 0.2.0 com o kit editorial (PR #83).
- [x] **Planos editoriais (ADR 011, aceita em 2026-09-28):** contrato e `vp check` (PR #85), template com as
  peças do kit (PR #86, cobre #70–#72), skills do roteirista e do verificador (PR #87).
- [x] **Episódio de teste `votorantim-dinheiro`** (ADR 011, etapa 4): 93 s, 10 cenas, 21 planos, gates 1–3
  aprovados; prévia em `renders/preview.mp4`; métricas em `data/benchmarks/episodio-votorantim-dinheiro.md`.
- [ ] **← Agora: Remotion.** Decisão do dono em 2026-09-29: o vídeo não será publicado por enquanto; o foco
  passa a ser o template do formato explicativo (`video/`, Remotion + motion-kit), com calma, uma frente por
  vez.
  - **Evolução do template (vídeo-régua), escolhida em 2026-09-29:** em vez de conferir cada correção num render
    avulso, o `votorantim-dinheiro` (conteúdo congelado) ganha uma versão `vN` ao fim de cada PR que muda o
    visual (template ou motion-kit), com a sonda de CPU antes; autorização do dono só para este vídeo. Comando
    `vp evolucao` (`gerar`, `guardar`, `comparar` com a folha de quadros, `lado-a-lado`),
    vídeos em `renders/evolucao/` e registro em `data/benchmarks/evolucao-template.md`. A folha e o registro
    marcam os planos que mudaram em relação à versão anterior: um PR de visual deve mudar só os que pretendia.

  - **Voz (2026-09-30):** a Charon (Gemini TTS, camada gratuita) ganhou do Kokoro na escuta às cegas; ADR 012
    proposta, aceite depois da v5 do vídeo-régua com ela. Camada gratuita: 3 chamadas por minuto e **10 por dia**.
    Kokoro nos rascunhos (`tts`), Charon no vídeo final (`tts_final`, `vp render --voz-final`), várias
    cenas por chamada cortadas nas pausas. Termos, limites e resultado em `data/benchmarks/termos-gemini-tts.md`.
    Próximos: as 3 falas que faltam do vídeo-régua (S08–S10, um lote) e a v5; depois, o volume (-14 LUFS) como v6.
  - **Voz (2026-10-12 e 2026-10-15):** a voz clonada do dono virou a voz final (ADR 016, Chatterbox na CPU, ~15 min
    por cena). Em 2026-10-15, depois da escuta comparada, ela passou a rodar numa GPU do Modal (ADR 024,
    `tts_final = "chatterbox_modal"`, ~10 s por cena), com a gravação de referência num volume privado do dono.
    A Charon segue registrada (`--voz=gemini`) e a voz local também (`--voz=chatterbox`).

  Frentes candidatas, a escolher com o dono (cada uma gera uma versão nova do vídeo-régua):
  - ver e ajustar os planos no Remotion Studio (navegador em 127.0.0.1), sem render;
  - defeitos vistos no `votorantim-dinheiro`: rótulos longos cortados na linha do tempo, rótulos das setas da rede
    pequenos (prop no motion-kit);
  - resto da #69: zoom nas transições (#72), entrada 2.5D (#71), tipos novos aplicados às cenas citadas nas
    #73 e #76–#80;
  - trilha e efeitos com `MusicBed`/`SfxTrack` (#81, licença por faixa decidida pelo dono);
  - `vp render` (#13) no lugar do script provisório; o `npm run render` de `video/package.json` ainda aponta
    para a composição `Episode`, que não existe mais.
- [ ] **Quando for publicar**, na ordem (análise inicial, revisão de 2026-09-29; o documento foi removido em 2026-11-01 e está no histórico do Git):
  1. Decisões do dono, numa rodada só: (a) o `votorantim-completo` sai com o roteiro atual (32 carimbos,
     7 planos com "Fonte:" no texto, que agora duplica o rodapé, trechos de até 18 planos sem imagem) ou é
     reescrito com os planos da ADR 011, o que reabre o gate 2 e cumpre os critérios das #73 e #76–#79;
     (b) o recorte da validação de audiência (§12): perfis de poder em pt-BR ou o piloto documentário, que o §1
     ainda cita.
  2. Se reescrito: roteirista e verificador só nas cenas afetadas, e gate 2 de novo.
  3. Gate 3 do `completo`: imagem por cena (várias sem candidato no Commons; a Brasiliana Fotográfica recusou o
     acesso automatizado com 403), retratos `an-jose-ermirio` e de Getúlio Vargas.
  4. Revisão de risco antes do gate 4 (pessoas vivas, empresa ativa, fatos de fonte única ou interessada): criar o
     agente `revisor-de-risco` (§15).
  5. Voz, render, legendas e pacote: não há `captions.srt`, `credits.txt` nem `description.txt` (#17 e #18,
     ou scripts provisórios como os de voz e render). Depois, gate 4.
  6. Publicação manual e métricas aos 7 e 28 dias (§12, #31), com as horas humanas do episódio medidas.
- [ ] **Próximos passos propostos**, cada um aguardando decisão do dono:
  - decupagem da referência (#69, passo 0, feita pelo dono);
  - Hemeroteca Digital para confirmar o leilão e o rateio de 1918 (cena S08 da fatia);
  - busca por vetor (ADR 010, ainda não escrita) quando as fontes passarem do que um agente lê de uma vez;
  - árvore da família com genro;
  - scripts provisórios de fonte, voz e render virarem `vp sources` (#26), `vp voice` (#16) e `vp render` (#13);
  - `vp new` e `vp reopen` (resto da #12; `vp approve`, `vp reject` e `vp status` já existem).
- Em pausa: #11 (invalidação) e M2–M7 do piloto documentário.

## M0 · Fase 0 — Ambiente e decisão do motor

Ordem A do §11: ambiente, benchmark, experimento de motor e ADR 001.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 1 | Ambiente WSL2: .wslconfig, venv, Ollama, Kokoro e check_env | — | `scripts/check_env.sh` passa |
| 2 | Base do projeto: pyproject, ruff, pytest e `vp --help` | #1 | `vp --help` lista os comandos do §10 |
| 3 | Schemas pydantic dos manifestos + fixture pilot-example | #2 | Fixture valida contra os schemas |
| 4 | Arquitetura: interfaces (portas) e adaptadores trocáveis | #2, #3 | Trocar a implementação de uma função = mudar uma linha em `config/providers.toml` |
| 5 | `vp bench`: benchmark da máquina | #1, #2, #4 | JSON com RAM, CPU, tok/s e segundos de TTS por minuto de áudio |
| 6 | Roteiro de teste 30–60 s + ativos DP fixos | #3 | Todos os ativos com campos do §6 preenchidos |
| 7 | Protótipo de motor: ffmpeg puro | #4, #6 | MP4 16:9 H.264/AAC abre no ffprobe |
| 8 | Protótipos MoneyPrinterTurbo e Remotion + comparação | #4, #6, #7 | Os três motores renderizam o mesmo trecho |
| 9 | ADR 001: motor de render + `episode.json` congelado | #7, #8 | Decisão humana registrada |

## M1 · B — Estado, cache e render do episódio

Ordem B do §11: manifesto, estados, cache, invalidação e render a partir de episode.json.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 10 | Manifesto, máquina de estados e cache por input_hash | #3, #4 | Reexecutar com mesmo hash não refaz trabalho |
| 11 | Regras de invalidação | #10 | Um teste por regra |
| 12 | `vp new`, `vp status` e `vp approve` | #10 | Aprovação nunca edita `review_status` à mão no manifesto principal |
| 13 | `vp render [--preview]` a partir de `episode.json` | #9, #10 | `episode.json` é a única entrada do motor |
| 14 | Checks automáticos de mídia | #13 | Relatório de checks em `review.json` |

## M2 · C — Voz, timing e legendas

Ordem C do §11: Kokoro por bloco, timing pela voz real, legendas e export.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 15 | Adapter Kokoro por bloco + glossário de pronúncia | #2, #3, #4 | Trocar uma frase regenera só aquele WAV |
| 16 | `vp voice`: WAVs e timing pela duração real | #11, #15 | Nenhuma duração estimada |
| 17 | `vp subs`: legendas alinhadas | #16 | SRT sincronizado no episódio de teste |
| 18 | `vp export`: pacote final | #13, #14, #17 | `credits.txt` gerado dos metadados de ativos |

## M3 · D — Acervos, licenças e galeria

Ordem D do §11: adapters de busca com licença registrada e galeria de revisão.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 19 | Base dos acervos: cache de metadados e dedupe sha256 | #3, #4 | Busca repetida usa cache |
| 20 | Adapters Wikimedia Commons, Library of Congress e Flickr Commons | #19 | Imagem sem licença identificável → `needs_review` |
| 21 | Adapter Pexels + headers de cota | #19 | `visual_need` = `contextual_stock` |
| 22 | `vp assets`: busca em cascata | #20, #21 | Nunca preenche com imagem irrelevante |
| 23 | `vp gallery`: galeria HTML estática (gate 3) | #22, #12 | Aprovação via `vp approve --step assets` |

## M4 · E — Geração condicional

Ordem E do §11: Cloudflare Workers AI só para lacunas, com medidor de cota.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 24 | Adapter Cloudflare Workers AI (FLUX.1 Schnell) + medidor de cota | #4, #19 | `quota_exhausted` em erro de cota, sem migrar para pago |
| 25 | Geração para lacunas + fallback gráfico original | #22, #24 | Imagem gerada nunca como `historical_exact` |

## M5 · F — Pesquisa e roteiro

Ordem F do §11: fontes reais, roteiro com claims ligadas a fontes e cenas.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 26 | `vp sources`: coleta e trechos numerados (gate 1) | #10, #12 | ≥ 2 fontes independentes para fatos principais |
| 27 | Adapter Ollama + `vp script` com validador de claims (gate 2) | #4, #26 | Roteiro com ficção bem formatada não passa |
| 28 | `vp scenes`: divisão em cenas | #27 | 20–35 entradas visuais para 5–7 min |

## M6 · G — Comparação e piloto

Ordem G do §11 e piloto aceito conforme critérios do §11.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 29 | Comparação pequena de provedores remotos gratuitos → ADR 003 | #5, #27 | Registro com modelo, endpoint, data, latência, limite, custo, termos |
| 30 | Episódio piloto de ponta a ponta | #18, #23, #25, #28 | Todos os critérios de aceite do §11 marcados |

## M7 · Validação de audiência

§12: publicação manual, métricas e decisão após 4 vídeos.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 31 | Publicação manual e validação de audiência | #30 | Critério anti-conteúdo-inautêntico (YPP) checado por episódio |

## Etapas adicionais (decididas na ADR 001)

Os números seguem os das issues: #32–#40 foram usados pelos PRs das etapas 1–8.

| # | Etapa | Milestone | Depende de | Aceite principal |
|---|---|---|---|---|
| 41 | Motor ffmpeg: granulação, vinheta e movimento variado por cena (§12) | M6 (antes do piloto #30) | #9 | Render da engine-test com o novo visual e cache por cena preservado |
| 42 | Gráfico como ativo: clipes Remotion + motion-kit para cenas `map_or_graphic` | M8 (antes do piloto, se precisar de mapa) | #9 | Clipe gráfico como ativo `Original` renderizado pelo ffmpeg |
| 43 | Formato explainer: trazer Remotion + motion-kit para o `main` | M8 | #9, #42 | `render.explainer = "remotion"` funcionando pelo mapa formato → motor |

## Formato explicativo (#48 e #69–#82)

Fatia vertical e visual do formato `explainer` (ADR 008, ADR 009, ADR 011). Situação em 2026-09-29.

| # | Etapa | Situação |
|---|---|---|
| 43 | Remotion + motion-kit no `main` | Antecipada pela #48 (PR #50); falta a medição limpa com `vp bench --render`. |
| 48 | Fatia vertical Votorantim | Passos 1–3 feitos; abertura v2 com gate 2 aprovado. Faltam o gate 3 do retrato `an-jose-ermirio`, fotos de 1918, a árvore com genro e o "próximo da referência" do dono. |
| 69 | Visual mais próximo do How Money Works (guarda-chuva) | ADR 011, etapas 1–4 (PRs #83–#87 e o episódio de teste `votorantim-dinheiro`). Faltam a decupagem da referência (dono) e a prévia completa refeita. |
| 70–72 | Mídia por baixo, câmera e transições | Entregues no PR #86 (quadros aprovados em 2026-09-28; transição só com empurrão lateral, sem zoom). Falta a conferência em movimento com o dono. |
| 73 | Plano de documento | Peça pronta (PRs #85 e #86). Falta S28, S34 e S42 do `votorantim-completo` como documento. |
| 74 | Fonte no rodapé | Pronto (PRs #85 e #86). Faltam os rótulos com "Fonte:" da abertura (5) e do `completo` (7). |
| 75 | Mistura de planos | Alertas no `vp check` (PR #85) e regra na skill (PR #87): critérios cumpridos. |
| 76 | Números: hodômetro e comparação | Peça pronta. Falta S05 e S10 da abertura como `compare`. |
| 77 | Gráficos: linha, participação e destaque | Peça pronta, com o alerta de tempo. Falta S15, S19 e S40 do `completo`. |
| 78 | Diagrama de poder | Peça pronta, `claims` por aresta no `vp check`. Falta S09 e S41 do `completo`; rótulos das setas pequenos (prop no motion-kit). |
| 79 | Mapa-múndi com rotas | Peça pronta, contornos do Natural Earth registrados. Falta S18 do `completo`. |
| 80 | Texto cinético | Peça pronta. Falta em duas cenas da abertura. |
| 81 | Trilha e efeitos | Não começada; depende de decisão do dono (licença por faixa). |
| 82 | Retrato recortado | Não começada; dependência nova e direito de derivar em aberto. |
