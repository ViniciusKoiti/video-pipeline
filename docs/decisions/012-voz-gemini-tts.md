# 012 — Voz do explicativo em pt-BR: Gemini TTS (Charon)

- **Status:** proposto; desde 2026-10-12 a voz do vídeo final é a clonada do dono (ADR 016). A Charon segue
  registrada (`montar_episodio.py --voz=gemini`) e continua sendo a voz do vídeo-régua
- **Data:** 2026-09-30
- **Etapa do roadmap:** #15 (voz por bloco), #29 (comparação pequena de remotos gratuitos, §7)
- **Relaciona-se com:** ADR 006 (portas e adaptadores), ADR 008 (pt-BR, voz Kokoro `pm_alex`), ADR 011

## Contexto

A narração do formato explicativo em pt-BR sai do Kokoro local (`pm_alex`, ADR 008). O dono achou a voz sintética
demais e quis melhorá-la antes de avançar no visual. O §7 do `CLAUDE.md` já listava o Gemini TTS gratuito como
candidato, com três critérios de troca: voz claramente melhor em escuta cega, nomes corretos e condições de dados
aceitas. As regras do §2 continuam: custo zero, segredo só no `.env`, cota esgotada para a cena e nunca o episódio.

## Opções consideradas

1. **Manter o Kokoro (`pm_alex`).** Local, sem limite nem envio de dados, com dicionário de fonemas para nomes.
   Soa mais sintético, na escuta do dono.
2. **Gemini TTS na camada gratuita.** `gemini-3.8-flash-tts`, estável desde 22/09/2026, com vozes com sotaque
   brasileiro e direção de fala por texto (`speech_metadata.style`). Limite de 3 chamadas por minuto; o texto e o
   áudio podem ser usados pelo Google para melhorar os produtos, com revisão humana; sem dicionário de pronúncia.
   Termos, preços e limites em `data/benchmarks/termos-gemini-tts.md`.
3. **Gemini Flash-Lite TTS.** Mais barato na camada paga (US$ 6 contra US$ 9 por milhão de tokens de áudio até
   2026); de graça na gratuita, como o Flash. A página o descreve para fala conversacional; entrou no teste com uma
   voz.
4. **Clonar a voz do dono** (Gemini, `POST /v1beta/voices`). Adiada: é dado pessoal, e os termos da camada gratuita
   pedem para não enviar dados pessoais.
5. **Hedra** (apresentador sintético). Descartada: é paga e a política de uso proíbe mídia de pessoas mortas há
   menos de cem anos, que são as dos episódios.

## Decisão

Proposta: **Gemini TTS `gemini-3.8-flash-tts` com a voz Charon, na camada gratuita**, como voz do vídeo final do
explicativo em pt-BR, e **Kokoro nos rascunhos** (escolha do dono em 2026-09-30, depois do limite de 10 chamadas
por dia):

- `config/providers.toml`: `tts = "kokoro"` (rascunhos e prévias de revisão, sem limite) e `tts_final = "gemini"`
  (vídeo final e vídeo-régua). `montar_episodio.py --voz-final` usa a voz final; o vídeo-régua usa sempre ela.
- **Várias cenas por chamada:** as cenas que faltam vão em lotes de até ~1.200 caracteres (~90 s de fala),
  separadas por `<long pause>` (marca da documentação, em inglês mesmo com texto em português); o áudio é cortado
  nas pausas mais longas (`app/media/pauses.py`), e o corte é recusado quando elas não se destacam das pausas de
  respiração. Lote recusado é gerado cena a cena. Um episódio completo (~6.600 caracteres) cabe em ~6 chamadas.

- **Escuta às cegas (2026-09-29/30):** três falas do vídeo-régua (S04 datas e valores; S05 nomes difíceis; S09
  banco e valor por extenso) em cinco versões com o mesmo volume e letras sorteadas por fala: Kokoro `pm_alex`,
  Gemini Charon, `pt-br-advisor-9` e `pt-br-assistant-9` (Flash) e `pt-br-assistant-9` (Flash-Lite). O dono
  escolheu a Charon (no gabarito: S04-C, S05-D, S09-E) e confirmou os nomes na S05.
- **Direção de fala fixa**, a do teste: "narração de documentário em português do Brasil, com sotaque brasileiro;
  tom calmo, informativo e neutro; ritmo moderado".
- **Adapter** `app/providers/tts/gemini.py` na porta `TTSProvider` (ADR 006): `ProviderInfo(remote=True,
  usd_per_call=0)`, chave só no cabeçalho, no máximo 3 chamadas por minuto, e erro de cota vira `ProviderError`
  (cena pendente, §2.1). Cache da voz pela fala, pelo provedor, pelo modelo, pela voz e pela direção.
- **Ritmo:** a Charon fala ~12–14 caracteres por segundo, contra 15–17 do Kokoro; a estimativa do `vp check` passa a
  depender da voz configurada.

## Consequências

- O vídeo fica ~20–30% mais longo com o mesmo roteiro: o vídeo-régua passa de 93 s para ~2 min, e o completo de
  ~7,5 para ~9,5 min.
- **Limite diário de 10 chamadas** (observado em 2026-09-30, "limit: 10 requests per day on Free Tier"): o
  vídeo-régua (10 cenas) gasta um dia de cota; o completo (47 cenas), cinco; cada reescrita de cena gasta mais.
  Com 3 por minuto, cada fala leva ~20 s. Cenas que passam do limite ficam pendentes para o dia seguinte (a cota
  zera à meia-noite do Pacífico). Serviço sobrecarregado ("503 high demand") e tempo esgotado também aconteceram
  no primeiro dia de uso. **Este limite pode mudar a decisão** (alternativas na conversa de 2026-09-30: várias
  cenas por chamada, Kokoro nos rascunhos e Charon só na versão final, ou gasto pequeno com teto).
- O roteiro narrado (história pública, §13.2) vai para o Google, como aceito pelo dono. A descrição do vídeo diz
  que a narração é sintética (política de uso do Google e divulgação do YouTube, §12).
- Nomes sem dicionário de fonemas: se a voz errar um nome, uma lista "nome → como falar" entra só na síntese, sem
  mudar o roteiro nem as legendas.
- Se o modelo sair de linha, a cota mudar ou a camada gratuita acabar, a volta ao Kokoro é uma linha em
  `config/providers.toml`; pagar exige nova decisão (§2.1).
- `CLAUDE.md` §1, §7 e §9 mudam quando esta ADR for aceita.
