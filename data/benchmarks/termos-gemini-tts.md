# Gemini TTS: termos, limites e formato (consulta de 2026-09-29)

Registro pedido no `CLAUDE.md` §7 antes de testar um provedor remoto: link oficial, data da consulta e o que a
página diz. Candidato à narração em pt-BR no lugar do Kokoro (`pm_alex`), com teste às cegas
(`scripts/provisorio/teste_voz_gemini.py`). Onde a leitura só trouxe resumo (página cortada), está marcado
**[resumo]**; o resto foi lido no texto da página.

## Modelos e idioma

- Modelos de fala: `gemini-3.8-flash-tts` e `gemini-3.8-flash-lite-tts`, "New Stable", disponíveis desde 22/09/2026;
  `gemini-3.1-flash-tts-preview` é "Legacy TTS preview model"; os modelos 2.5 ficaram restritos a quem já os usava
  ([modelos](https://ai.google.dev/gemini-api/docs/models), atualizada em 2026-09-24).
- Idioma detectado sozinho, "over 130 languages"; a página do modelo lista "Portuguese", sem variante. **Não há
  parâmetro de idioma nem de sotaque na síntese** ([gemini-3.8-flash-tts](https://ai.google.dev/gemini-api/docs/models/gemini-3.8-flash-tts)).
  A biblioteca estendida de vozes filtra por `language_code` (ex.: `pt-BR`) em `GET /v1beta/voices`.
- Chamada: `POST /v1beta/interactions`, texto em `input[].content[]`, direção de fala em
  `annotations[].speech_metadata.style`; o texto é lido "strictly as a verbatim transcript", então instrução escrita
  no texto é falada ([speech-generation](https://ai.google.dev/gemini-api/docs/speech-generation), atualizada em
  2026-09-24). Pausas e respiração por tags no texto (`<short pause>`, `<breath>`).
- **Pronúncia:** sem SSML e sem dicionário de fonemas nas páginas consultadas (o Kokoro aceita fonemas, §9).
- Vozes prontas com descrição, entre elas Charon "Informative", Rasalgethi "Informative", Sadaltager
  "Knowledgeable", Schedar "Even", Gacrux "Mature" (speech-generation).
- Saída: WAV com cabeçalho RIFF, 24 kHz, mono, 16 bits; entrada até 8.192 tokens e saída até 16.384 por chamada
  (páginas dos modelos 3.8).

## Custo e limites

- Preços ([pricing](https://ai.google.dev/gemini-api/docs/pricing), atualizada em 2026-09-24, texto lido na página;
  áudio cobrado a 25 tokens por segundo):

  | Modelo | Camada gratuita | Paga: saída de áudio por 1M tokens | Paga: por 10 s de áudio |
  |---|---|---|---|
  | `gemini-3.8-flash-lite-tts` | "Free of charge" | $6,00 até 31/12/2026; $12,00 a partir de 2027 | $0,0015; $0,003 |
  | `gemini-3.8-flash-tts` | "Free of charge" | $9,00 até 31/12/2026; $18,00 a partir de 2027 | $0,00225; $0,0045 |
  | `gemini-2.5-flash-preview-tts` | "Free of charge" (acesso restrito) | $10,00 | — |
  | `gemini-3.1-flash-tts-preview` | "Free of charge" | $20,00 | — |

  Entrada de texto: $0,50 por 1M tokens nos modelos 3.8 (até 2026). "Used to improve our products": **Yes na
  camada gratuita, No na paga**. Descrições da página: Flash TTS "engineered for studio-grade voice fidelity,
  expressive acting, and long-form stability"; Flash-Lite TTS "optimized for high-throughput, low-latency, and
  cost-efficient conversational speech".
- A camada gratuita exige só "Active project or free trial"; a paga exige conta de faturamento vinculada e
  pré-pagamento ([billing](https://ai.google.dev/gemini-api/docs/billing), atualizada em 2026-09-28).
  **Não vincular faturamento** (§2.1): uso com faturamento ativo vira serviço pago.
- Limites por minuto e por dia dos modelos TTS: não publicados; "can be viewed in Google AI Studio"
  ([rate-limits](https://ai.google.dev/gemini-api/docs/rate-limits), atualizada em 2026-09-02). Valem por projeto,
  não por chave; o limite diário zera à meia-noite do Pacífico. **Observado em 2026-09-29:** o erro 429 do
  `gemini-3.8-flash-tts` diz "limit: 3 requests per minute on Free Tier"; o limite diário não apareceu em 14
  requisições (1 lista de vozes, 13 de fala). O script espera 21 s entre chamadas.
- **Tokens de áudio observados:** 32 por segundo nos dois modelos 3.8 (12 falas, 151,5 s, campo `usage` da
  resposta), não os 25 da página de preços: o custo real por segundo, se um dia for pago, é ~28% maior que o
  "per 10s audio" publicado. O teste inteiro custaria US$ 0,043 na tabela paga; na gratuita, custou zero.

## Termos da camada gratuita

Fonte: [Gemini API Additional Terms](https://ai.google.dev/gemini-api/terms), "Effective March 23, 2026".

- O Google usa o que é enviado e gerado "to provide, improve, and develop Google products", e "human reviewers may
  read, annotate, and process your API input and output". A página pede: "Do not submit sensitive, confidential,
  or personal information to the Unpaid Services". Os roteiros são história pública (§13.2); **voz própria para
  clonagem é dado pessoal**, e a decisão é do dono.
- O Google não reivindica o conteúdo gerado; não há proibição específica de uso comercial nas páginas lidas.
- Exige 18 anos ou mais; o Brasil está nas [regiões disponíveis](https://ai.google.dev/gemini-api/docs/available-regions).
- A [política de uso](https://policies.google.com/terms/generative-ai/use-policy) proíbe apresentar conteúdo
  gerado como feito só por humano "in order to deceive": a descrição do vídeo diz que a narração é sintética.
- Marca d'água (SynthID) no áudio: não mencionada nas páginas lidas.

## Clonagem de voz

Fonte: [voice-replication](https://ai.google.dev/gemini-api/docs/voice-replication), atualizada em 2026-09-24.

- Dois áudios reais do mesmo adulto (WAV 24 kHz mono 16 bits recomendado): referência de 10–30 s de fala limpa e
  natural, e o consentimento com a frase exata em pt-BR: "Eu sou o proprietário desta voz e autorizo o Google a
  usá-la para criar um modelo de voz sintética."
- Pelo AI Studio (gravar ou enviar no navegador) ou por `POST /v1beta/voices`.
- Guarda no projeto (`store=true`, `voice_...`, 1 ano, até 200 vozes) ou sem guardar o perfil no servidor
  (`store=false`, chave `voicekey_...` válida por 7 dias, guardada por quem usa).
- A página não diz se a clonagem funciona na camada gratuita.

## Resultado do teste (2026-09-29/30)

Script `scripts/provisorio/teste_voz_gemini.py`; áudios em `data/benchmarks/voz-gemini/` (fora do Git). Endpoint
`POST /v1beta/interactions`, camada gratuita, sem faturamento. Direção de fala: "narração de documentário em
português do Brasil, com sotaque brasileiro; tom calmo, informativo e neutro; ritmo moderado".

- **Vozes pt-BR:** `GET /v1beta/voices?language_code=pt-BR` devolveu 50 vozes com `accent: "Brazilian Portuguese"`
  (primeira página). O risco de sotaque de Portugal some com elas; a Charon, voz padrão, também soou brasileira.
- **Chamadas:** 1 lista de vozes e 13 de fala, das quais 1 com erro 429 ("limit: 3 requests per minute on Free
  Tier"). Latência de 6,2 a 27,5 s por fala (a mais longa, 188 caracteres, foi a mais lenta).
- **Saída:** WAV 24 kHz mono, completo em todas as 12 falas; volume de -18 a -21 LUFS (Kokoro: -26).
- **Ritmo:** Gemini de 10,7 a 14,0 caracteres por segundo; Kokoro de 14,9 a 16,8.
- **Custo:** zero. Na tabela paga, o teste custaria US$ 0,043 (32 tokens de áudio por segundo).
- **Escuta às cegas:** 3 falas × 5 versões, mesmo volume (-16 LUFS), letras sorteadas por fala. O dono escolheu a
  **Charon** (S04-C, S05-D, S09-E) e confirmou os nomes da S05 ("Antonio Pereira Ignácio", "Marcovitch"); o
  `NOTAS.md` com notas por critério ficou em branco. Decisão proposta na ADR 012.
