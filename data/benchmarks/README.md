# Benchmarks

Evidência para as decisões de motor e provedores (ADRs 001 e 003). Cada arquivo é versionado.

- `machine-AAAAMMDD-HHMMSS.json` — saída do `vp bench` (etapa 5): máquina (CPU, RAM, carga no início),
  uma linha por execução de LLM (tokens/s lendo e gerando, tempo total, claims e citações inválidas)
  e de TTS (RTF = segundos de síntese por segundo de áudio). O prompt usa uma expedição **fictícia**
  (`app/pipeline/bench_data.py`), com ~1000 tokens de trechos numerados.
- `vp bench --skip-llm --skip-tts --render tests/fixtures/episodes/engine-test` mede o motor configurado
  em `config/providers.toml`: final sem cache, final com cache (só junta) e prévia. Vídeos ficam em
  `data/benchmarks/renders/<motor>/` (fora do Git).
- Rodar com a máquina ociosa **e sem jogos/apps pesados no Windows**; `warnings` registra carga alta ou
  CPU limitada (`cpu_probe_s` > 0,3 s: sha256 de 64 MB). Resultado com aviso não vale como benchmark.
- Resultados de provedores remotos (etapa 29) seguem o §7 do CLAUDE.md: link oficial, data, conta real.

## Resultados — 2026-09-25 (`machine-20260925-091013.json`)

Ryzen 7 5700U, WSL com 12 GB / 12 CPUs, 8 threads, máquina ociosa (load 1,06). Prompt de 1010 tokens,
saída limitada a 600 tokens, 2 execuções por modelo.

| Modelo | Gera (tok/s) | Lê (tok/s) | Tempo/execução | JSON válido | Citações inválidas | Memória livre depois |
|---|---|---|---|---|---|---|
| qwen3.5:4b | 4,3–4,6 | 25–27 | 130 s | 2/2 | 0 | 5,4 GB |
| qwen3.5:9b | 3,1–3,2 | 16 | 205–245 s | 2/2 | 0 | 2,4 GB |
| qwen3:4b | 5,0–5,4 | 28–30 | 135–160 s | 2/2 | 0 | 6,1 GB |

Kokoro (`am_michael`): RTF 1,52 na primeira execução (inclui carga) e **0,70** com o modelo carregado,
ou seja, ~42 s de síntese por minuto de áudio. Pico de memória do processo: 1,5 GB.

Leitura:

- Projeção para um roteiro real (~8 mil tokens de trechos, ~2 mil de saída): ~11 min (`qwen3:4b`),
  ~13 min (`qwen3.5:4b`) e ~19 min (`qwen3.5:9b`) por chamada. Viável, mas cada rodada de revisão do
  roteiro custa isso. A estimativa anterior de 20–40 min (máquina ocupada) estava pessimista.
- Narração de 6 min: ~4–5 min de síntese. TTS não é gargalo.
- `qwen3:4b` ignorou o pedido de 4–6 claims (8–9) e chegou a 599 dos 600 tokens de saída: segue
  instruções pior que o `qwen3.5`. Estrutura válida não prova fidelidade: a avaliação humana dos textos
  (campo `output`, gravado a partir da próxima execução) fica para a etapa 29.
- O `qwen3.5:9b` deixa só 2,4 GB livres; descarregar o LLM antes da etapa de voz (etapa 16).
- O Ollama usa contexto de 4096 tokens por padrão: um prompt de roteiro real seria cortado. Ver
  questão 13 da `docs/ANALISE.md`.

## Render ffmpeg — 2026-09-25 (`machine-20260925-212240.json`)

Máquina livre (sonda de CPU 0,06 s, load 0,36). Fixture `engine-test` (52,5 s, 5 cenas), motor
`app/render/ffmpeg.py` com a configuração padrão (`crf 20`, final `medium`, prévia `veryfast`).

| Render | Tempo | Velocidade | Tamanho |
|---|---|---|---|
| Final 1080p sem cache | 51,7 s | 1,0× tempo real | 30,2 MB |
| Final com cache (só junta vídeo + codifica o áudio) | 2,9 s | 18× | 30,2 MB |
| Prévia 720p sem cache | 21,3 s | 2,5× | 9,2 MB |

Pico de memória do ffmpeg: 956 MB (zoom com superamostragem 2×, fonte 3840×2160 no 1080p).
Projeção para 6 min: ~6 min o final sem cache, ~2,5 min a prévia, segundos para trocar uma cena de
imagem (só aquele segmento + junção). Com a CPU limitada (questão 15 da ANALISE) o mesmo render levou 694 s.

## Comparação dos motores — etapa 8 (2026-09-25)

Mesma entrada (`engine-test`, 52,5 s, 5 cenas), mesmas regras visuais onde o motor permite. Adapters
experimentais nos branches `experimento-mpt` e `experimento-remotion` (não estão no `main`).

- **ffmpeg** e **Remotion** medidos em sequência pelo `vp bench --render`, nas mesmas condições (CI de
  outro projeto rodando: load 3,4–6,7, por isso com aviso): `machine-20260925-222958.json` (ffmpeg) e
  `machine-20260925-224150.json` (Remotion). Valem como comparação relativa.
- **MoneyPrinterTurbo** medido com a máquina livre, um render final só, chamando o adapter direto
  (cada render leva ~40 min; o `vp bench` faria três).

| Critério | ffmpeg puro | MoneyPrinterTurbo 1.3.7 | Remotion 4.0.529 |
|---|---|---|---|
| Final 1080p, sem cache | **51,7 s** livre · 72 s com carga | 2433 s livre | 266 s com carga |
| Trocar a imagem de uma cena | refaz só a cena (~5 s) | refaz tudo (~40 min) | refaz tudo (~4,5 min) |
| Prévia 720p | 21 s livre · 35 s com carga | não tem (render completo + redução) | 177 s com carga |
| Controle por cena pelo `episode.json` | total (segmento por cena) | só entregando um clipe pré-cortado por cena; arredonda durações (~0,1 s de desvio) | total (props) |
| Imagem estreita (4:3, vertical) | inteira sobre fundo desfocado | barras pretas (`cover` cortaria) | inteira sobre fundo desfocado |
| Movimento | zoom 6% por cena | zoom 3%/s fixo: ~40% numa cena de 13 s, corta o assunto (§9) | zoom 6% por cena |
| Saída | H.264 yuv420p (tv), AAC 48 kHz, 30 MB | H.264, **AAC 44,1 kHz** (fora do contrato), 18 MB | H.264 bt709 (tv), AAC 48 kHz (+53 ms de enchimento), 46 MB |
| Maior processo | 956 MB | ~0,5 GB (observado) | 854 MB |
| Dependências | ffmpeg do sistema | app inteiro, ~1,4 GB (LiteLLM, Streamlit, Redis, SDKs de nuvem) | Node + 247 MB npm + 220 MB Chrome headless |
| Licença | ffmpeg do sistema (uso local) | MIT | Remotion License (grátis para indivíduos, inclusive comercial) |
| Auditoria | comandos ffmpeg determinísticos a partir do `episode.json` | app de terceiros com padrões aleatórios (ordem, música) | props derivadas do `episode.json` |
| Qualidade visual (avaliação humana) | pendente | pendente | pendente |

Vídeos para a avaliação humana, fora do Git: `data/benchmarks/renders/<motor>/engine-test-{final,preview}.mp4`.
