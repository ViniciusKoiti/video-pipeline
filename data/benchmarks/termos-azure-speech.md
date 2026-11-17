# Azure Speech (voz neural pronta): termos, limites e formato (consulta de 2026-11-11)

Registro pedido no `CLAUDE.md` §7 antes de testar um provedor remoto: link oficial, data da consulta e o que a
página diz. Tudo abaixo foi lido no texto das páginas, sem conta e **sem nenhuma chamada à API**; o teste com a
conta real ainda não foi feito. Decisão e detalhes na ADR 058.

| Assunto | O que a página diz | Página (data da página) |
|---|---|---|
| Endpoint | `POST https://<região>.tts.speech.microsoft.com/cognitiveservices/v1`, corpo SSML | [rest-text-to-speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech) (2026-05-21) |
| Cabeçalhos | `Ocp-Apim-Subscription-Key` ou `Authorization: Bearer`; `Content-Type: application/ssml+xml`; `X-Microsoft-OutputFormat`; `User-Agent` (< 255 caracteres) | idem |
| Formato usado | `riff-24khz-16bit-mono-pcm` (lista "NonStreaming"); também 48 kHz e 44,1 kHz | idem |
| Erros | 400, 401, 415, 429 (cota ou taxa), 502, 503 | idem |
| Áudio por chamada | até 10 minutos; o resto é cortado | idem |
| Taxa na F0 | 20 chamadas por 60 s, sem ajuste | [quotas and limits](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits) (2026-10-02) |
| Franquia da F0 | "0.5 million characters free per month" (voz neural) | [preços](https://azure.microsoft.com/en-us/pricing/details/speech/) (lida em 2026-11-11) |
| O que conta | texto e marcação do SSML, menos `<speak>` e `<voice>` | [text-to-speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech) (2026-01-30) |
| Pausa | `<break time="…ms"/>`, 0 a 20.000 ms | [SSML, estrutura](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-structure) (2026-02-25) |
| Velocidade | `<prosody rate>` de 0,5 a 2 | [SSML, voz](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice) (2026-01-30) |
| Voz | `pt-BR-AntonioNeural` (Male), "Standard", sem marca de prévia | [language-support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts) |
| Uso | voz pronta liberada para casos de uso escolhidos pelo cliente, dentro da política de uso aceitável e do código de conduta, sem registro | [nota de transparência](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/speech-service/text-to-speech/transparency-note) (2026-03-31) |
| Aviso de voz sintética | obrigatório: "Microsoft requires its customers to disclose the synthetic nature of text to speech voices to its users" | idem; [código de conduta](https://learn.microsoft.com/en-us/legal/ai-code-of-conduct) (v4.0, 2026-05-01) |

## A confirmar

- Frase explícita sobre uso comercial do áudio gerado, e se vale na F0: os Microsoft Product Terms
  (`microsoft.com/licensing/terms`) não foram lidos.
- O que a F0 responde quando os 500 mil caracteres do mês acabam (a página de preços não diz).
- O preço da camada paga não apareceu na página de preços lida; a página de cotas usa US$ 15 por milhão de
  caracteres num exemplo.
- Teste com a conta real: latência, tamanho do WAV, ritmo da voz (caracteres por segundo), se o cabeçalho do WAV
  vem com o tamanho certo, 429 observado.
