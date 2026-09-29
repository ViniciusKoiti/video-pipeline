# Roadmap — etapas entregáveis (#1–#31, #41–#43, #48, #69–#82)

Cada etapa é uma issue no GitHub com o mesmo número (etapa N = issue #N) e pertence a um milestone
que segue a ordem de implementação do §11 do `CLAUDE.md`. Gerado a partir de uma fonte única;
detalhes e critérios de aceite completos estão nas issues.

## Situação em 2026-09-29

O formato explicativo (#48, #69–#82, no fim deste arquivo) passou na frente do piloto documentário. As
pendências em ordem estão no "Etapa atual" do `CLAUDE.md`.

| Issues | Situação |
|---|---|
| #1–#10 | Fechadas. |
| #11 | Em pausa até o modelo de planos estabilizar. |
| #12 | Parcial: `vp approve`, `vp reject` e `vp status` (PR #67); faltam `vp new` e `vp reopen`. |
| #13, #16 | Script provisório `scripts/provisorio/montar_episodio.py` faz voz e render; os comandos `vp` não existem. |
| #15 | Adapter Kokoro existe (usado no `vp bench` e no script de voz); falta o glossário de pronúncia. |
| #19–#22 | Adapters Pexels, Pixabay e Unsplash feitos na #48 (PRs #61–#63); Commons e Arquivo Nacional só pelos scripts provisórios de busca e download; `vp assets` não existe. |
| #26 | Parcial: script provisório `baixar_fonte.py` (PR #68) e `vp excerpts`. |
| #27, #28 | Adapter Ollama existe; `vp script` e `vp scenes` não. Desde a ADR 009, fichas, roteiro e cenas saem dos agentes (pesquisador, roteirista, verificador) validados pelo `vp check`; o Ollama ficou como candidato (§7). |
| #14, #17, #18, #23–#25, #29–#31, #41, #42 | Não começadas. #17 (legendas) e #18 (pacote) são necessárias antes de publicar. |
| M2–M7 do piloto documentário | Em pausa. |

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
