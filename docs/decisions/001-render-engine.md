# 001 — Motor de render por formato de episódio; `episode.json` congelado (v1)

- **Status:** aceito
- **Data:** 2026-09-26
- **Etapa do roadmap:** #9 (evidência: #7 e #8)
- **Decisão humana:** Vinicius Koiti, após assistir aos vídeos dos quatro protótipos

## Contexto

A Fase 0 comparou os motores com a mesma entrada (`tests/fixtures/episodes/engine-test`, 52,5 s, 5 cenas
com fotos de arquivo). Tabela completa em `data/benchmarks/README.md`; vídeos em `data/benchmarks/renders/`.

| | ffmpeg puro | MoneyPrinterTurbo 1.3.7 | Remotion 4.0.529 | Remotion + motion-kit |
|---|---|---|---|---|
| Final 1080p sem cache | 51,7 s (72 s com carga) | 2433 s | 266 s com carga | sem medição limpa |
| Trocar uma cena | só a cena (~5 s) | tudo (~40 min) | tudo | só a cena (4,3 s com cache) |
| Imagem estreita | inteira + fundo desfocado | barras pretas | inteira + fundo desfocado | inteira + fundo desfocado |
| Movimento | zoom 6% | 3%/s, corta o assunto | zoom 6% | push-in + deriva + granulação |
| Controle por cena | total | parcial, arredonda durações | total | total |
| Dependências | ffmpeg do sistema | app inteiro (LiteLLM, Redis…) | Node + Chrome | Node + Chrome + motion-kit |

O dono do projeto avaliou que, para foto + narração + legenda, os vídeos do ffmpeg e do Remotion + motion-kit
ficam "extremamente próximos". A vantagem do motion-kit aparece em visual **gerado a partir de dados**
(código, diagramas, mapas animados, linhas do tempo), que o ffmpeg faz mal.

## Decisão

1. **O motor é escolhido pelo formato do episódio**, não uma vez para sempre, e o formato vem de um
   **tomador de decisão** (`app/pipeline/format_decision.py`) que recomenda e um humano confirma (§2.5):
   - **pelo tema**, no `vp new`: o LLM local classifica o tema (`TopicAssessment`: evento histórico,
     conceito ou ambíguo, e o ano) e regras pontuam — evento até 1930 favorece o documentário (fotos em
     domínio público, §8); depois de 1930 perde força (risco de 100% ilustração, §1); conceito vira
     explicativo; ambíguo fica no formato do MVP com aviso;
   - **pelas cenas**, depois do `vp scenes`: regras sobre os `visual_need` — ≥ 60% de cenas
     `map_or_graphic` recomendam explicativo; poucas cenas gráficas mantêm o documentário e são marcadas
     para o caminho "gráfico como ativo" (item 5).
   A recomendação traz pontuação por formato, motivos e `input_hash`. O humano aprova ou troca no
   `review.json` (`step: format`, `choice` quando troca); se a entrada mudar, a confirmação cai.
   `vp new --format` fica como troca explícita. O formato confirmado vai para `EpisodeManifest.format`
   (`archival_documentary` | `explainer`), que o `config/providers.toml` mapeia para o motor:
   `render = { archival_documentary = "ffmpeg", explainer = "remotion" }`.
2. **`archival_documentary` → ffmpeg puro** (`app/render/ffmpeg.py`): mais rápido, cache por cena, sem Node,
   comandos determinísticos a partir do `episode.json`. É o único formato do MVP.
3. **`explainer` → Remotion + @viniciusk/motion-kit**, que entra no `main` só quando o primeiro vídeo
   explicativo começar (etapa #43). Até lá o adapter vive no branch `experimento-remotion`
   (tag `arquivo/experimento-remotion`), e pedir esse motor dá erro claro apontando a etapa.
4. **MoneyPrinterTurbo reprovado**: não segue a linha do tempo por cena, zoom fixo corta o assunto (§9),
   áudio fora do contrato (44,1 kHz), ~47× mais lento, e só funciona instalando o app inteiro com LiteLLM
   (§2.8). Adapter arquivado no branch `experimento-mpt` (tag `arquivo/experimento-mpt`).
5. **Mistura sem segundo motor — "gráfico como ativo"** (etapa #42): quando um documentário precisar de
   uma cena gráfica animada (rota sobre mapa, linha do tempo), o Remotion + motion-kit gera um **clipe**
   com a duração da cena, registrado como ativo `Original` (sha256, componente e props) e revisado no
   gate 3 como uma foto; o motor ffmpeg o monta como visual da cena. Node só é exigido ao gerar o clipe.
   Um motor composto por cena foi rejeitado por ora: exigiria segmentos idênticos entre motores, duas
   implementações do mesmo visual e Node em todo episódio com uma cena gráfica.
6. **Regra §2.8 alterada**: de "não existe segundo motor de render" para "um motor por formato; o MVP
   produz só `archival_documentary`".
7. **Contrato `episode.json` congelado na versão 1** (`schema_version: 1`): `episode_id`, `title`,
   `language`, `format`, `video` (1920×1080, 30 fps, 48 kHz, 16:9), `scenes` (`id`, `start_ms`,
   `duration_ms`, `narration`, `asset_id`, `image`, `audio`), `captions`. Mudar campos exige nova ADR e
   nova versão. A saída do ffmpeg passa a converter e marcar cor em bt709 (faixa limitada), como o Remotion.

## Consequências

- `Context.renderer(format)` substitui `Context.render`; a raiz de composição monta o motor do formato
  sob demanda.
- Ligações pendentes do tomador de decisão: classificador de tema no adapter de texto (etapa #27), `vp new`
  gravando a recomendação e o gate de formato (#12), revisão pelas cenas no `vp scenes` (#28).
- Etapa #41 leva ao ffmpeg granulação, vinheta e movimento variado por cena (defesa do §12) antes do piloto.
- Etapas #42 e #43 (milestone M8) guardam o caminho para visual mais rico sem pesar o MVP.
- Instalações locais do experimento podem ser apagadas e reinstaladas pelos locks dos branches arquivados.
