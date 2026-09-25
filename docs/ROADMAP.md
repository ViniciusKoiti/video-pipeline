# Roadmap — 30 etapas entregáveis

Cada etapa é uma issue no GitHub com o mesmo número (etapa N = issue #N) e pertence a um milestone
que segue a ordem de implementação do §11 do `CLAUDE.md`. Gerado a partir de uma fonte única;
detalhes e critérios de aceite completos estão nas issues.

## M0 · Fase 0 — Ambiente e decisão do motor

Ordem A do §11: ambiente, benchmark, experimento de motor e ADR 001.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 1 | Ambiente WSL2: .wslconfig, venv, Ollama, Kokoro e check_env | — | `scripts/check_env.sh` passa |
| 2 | Base do projeto: pyproject, ruff, pytest e `vp --help` | #1 | `vp --help` lista os comandos do §10 |
| 3 | Schemas pydantic dos manifestos + fixture pilot-example | #2 | Fixture valida contra os schemas |
| 4 | `vp bench`: benchmark da máquina | #1, #2 | JSON com RAM, CPU, tok/s e segundos de TTS por minuto de áudio |
| 5 | Roteiro de teste 30–60 s + ativos DP fixos | #3 | Todos os ativos com campos do §6 preenchidos |
| 6 | Protótipo de motor: ffmpeg puro | #5 | MP4 16:9 H.264/AAC abre no ffprobe |
| 7 | Protótipos MoneyPrinterTurbo e Remotion + comparação | #5, #6 | Os três motores renderizam o mesmo trecho |
| 8 | ADR 001: motor de render + `episode.json` congelado | #6, #7 | Decisão humana registrada |

## M1 · B — Estado, cache e render do episódio

Ordem B do §11: manifesto, estados, cache, invalidação e render a partir de episode.json.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 9 | Manifesto, máquina de estados e cache por input_hash | #3 | Reexecutar com mesmo hash não refaz trabalho |
| 10 | Regras de invalidação | #9 | Um teste por regra |
| 11 | `vp new`, `vp status` e `vp approve` | #9 | Aprovação nunca edita `review_status` à mão no manifesto principal |
| 12 | `vp render [--preview]` a partir de `episode.json` | #8, #9 | `episode.json` é a única entrada do motor |
| 13 | Checks automáticos de mídia | #12 | Relatório de checks em `review.json` |

## M2 · C — Voz, timing e legendas

Ordem C do §11: Kokoro por bloco, timing pela voz real, legendas e export.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 14 | Protocol TTS + adapter Kokoro por bloco + glossário | #2, #3 | Trocar uma frase regenera só aquele WAV |
| 15 | `vp voice`: WAVs e timing pela duração real | #10, #14 | Nenhuma duração estimada |
| 16 | `vp subs`: legendas alinhadas | #15 | SRT sincronizado no episódio de teste |
| 17 | `vp export`: pacote final | #12, #13, #16 | `credits.txt` gerado dos metadados de ativos |

## M3 · D — Acervos, licenças e galeria

Ordem D do §11: adapters de busca com licença registrada e galeria de revisão.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 18 | Protocol de acervos + cache e dedupe sha256 | #3 | Busca repetida usa cache |
| 19 | Adapters Wikimedia Commons, Library of Congress e Flickr Commons | #18 | Imagem sem licença identificável → `needs_review` |
| 20 | Adapter Pexels + headers de cota | #18 | `visual_need` = `contextual_stock` |
| 21 | `vp assets`: busca em cascata | #19, #20 | Nunca preenche com imagem irrelevante |
| 22 | `vp gallery`: galeria HTML estática (gate 3) | #21, #11 | Aprovação via `vp approve --step assets` |

## M4 · E — Geração condicional

Ordem E do §11: Cloudflare Workers AI só para lacunas, com medidor de cota.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 23 | Adapter Cloudflare Workers AI (FLUX.1 Schnell) + medidor de cota | #18 | `quota_exhausted` em erro de cota, sem migrar para pago |
| 24 | Geração para lacunas + fallback gráfico original | #21, #23 | Imagem gerada nunca como `historical_exact` |

## M5 · F — Pesquisa e roteiro

Ordem F do §11: fontes reais, roteiro com claims ligadas a fontes e cenas.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 25 | `vp sources`: coleta e trechos numerados (gate 1) | #9, #11 | ≥ 2 fontes independentes para fatos principais |
| 26 | Protocol de texto + Ollama + `vp script` com validador de claims (gate 2) | #25 | Roteiro com ficção bem formatada não passa |
| 27 | `vp scenes`: divisão em cenas | #26 | 20–35 entradas visuais para 5–7 min |

## M6 · G — Comparação e piloto

Ordem G do §11 e piloto aceito conforme critérios do §11.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 28 | Comparação pequena de provedores remotos gratuitos → ADR 003 | #4, #26 | Registro com modelo, endpoint, data, latência, limite, custo, termos |
| 29 | Episódio piloto de ponta a ponta | #17, #22, #24, #27 | Todos os critérios de aceite do §11 marcados |

## M7 · Validação de audiência

§12: publicação manual, métricas e decisão após 4 vídeos.

| # | Etapa | Depende de | Aceite principal |
|---|---|---|---|
| 30 | Publicação manual e validação de audiência | #29 | Critério anti-conteúdo-inautêntico (YPP) checado por episódio |
