# 058 — Voz neural pronta do Azure Speech (`pt-BR-AntonioNeural`), só na camada gratuita

- **Status:** proposta (2026-11-11). Adapter e testes prontos. **Primeiro uso real em 2026-11-12**, a pedido do dono,
  no piloto `academia-dinheiro-pt`: 70 cenas sem falha na F0, em velocidade 1,0 (12:20) e depois 1,05 (11:45;
  `rate` em `config/providers.toml`). Falta a escuta do dono e a comparação do §7 do `CLAUDE.md`.
- **Data:** 2026-11-11
- **Etapa do roadmap:** #15 (voz por bloco), #29 (comparação pequena de remotos gratuitos, §7)
- **Relaciona-se com:** ADR 006 (portas e adaptadores), ADR 012 (Gemini TTS), ADR 015 (pausas), ADR 016 e 024
  (voz clonada, que segue sendo a final), ADR 022 (entrega por cena), ADR 041 (identidade do cache de voz),
  ADR 049 (`VoiceKey` e nomes dos WAVs)

## Contexto

O dono quer poder narrar com a voz neural `pt-BR-AntonioNeural` do Azure Speech, o serviço oficial da Microsoft.
As regras do §2 continuam: custo zero, segredo só no `.env`, cota esgotada para a cena e nunca o episódio, nenhuma
dependência nova, testes sem rede. A voz não vira padrão nem final: é mais uma voz registrada pelo nome.

## O que a documentação diz (consulta de 2026-11-11)

Lido no texto das páginas; resumo com links e datas em `data/benchmarks/termos-azure-speech.md`.

- **Endpoint e chamada** ([rest-text-to-speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/rest-text-to-speech),
  página de 2026-05-21): `POST https://<região>.tts.speech.microsoft.com/cognitiveservices/v1`, corpo SSML,
  `Content-Type: application/ssml+xml`, `X-Microsoft-OutputFormat` com o formato e `User-Agent` obrigatório
  (menos de 255 caracteres). Autenticação por `Ocp-Apim-Subscription-Key` (a chave do recurso) ou por
  `Authorization: Bearer`. A tabela de cabeçalhos da síntese só lista `Authorization`, mas a seção de
  autenticação da mesma página diz que a chave no `Ocp-Apim-Subscription-Key` vale para texto em fala e "works
  with all endpoint formats"; o adapter usa a chave direto, sem a troca por token de 10 minutos.
- **Formato:** `riff-24khz-16bit-mono-pcm` está na lista dos formatos não contínuos (WAV com cabeçalho RIFF); há
  também 48 kHz e 44,1 kHz. Cada voz padrão existe em 24 kHz e 48 kHz.
- **Erros:** 400 (parâmetro inválido), 401 (chave ou região erradas), 415 (`Content-Type` errado), 429 ("You
  exceeded the quota or rate of requests allowed for your resource"), 502 e 503 (problema do serviço).
- **Limite por fala:** o áudio de uma chamada não passa de 10 minutos; o que passar é **cortado**, sem erro.
- **Camada gratuita F0** ([quotas and limits](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-services-quotas-and-limits),
  página de 2026-10-02): 20 chamadas por 60 segundos, sem ajuste; 10 minutos de áudio por chamada; no máximo 50
  tags `<voice>` e `<audio>` por SSML. A página pede nova tentativa no 429 e avisa que a maioria dos 429 das
  vozes padrão é falta de capacidade daquela voz na região ("use the voice in its native region").
  A franquia mensal está na [página de preços](https://azure.microsoft.com/en-us/pricing/details/speech/) (fora
  do learn.microsoft.com): "0.5 million characters free per month" para a voz neural.
- **Caracteres contados** ([text-to-speech](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/text-to-speech),
  página de 2026-01-30): todo o texto e a marcação do SSML, menos as tags `<speak>` e `<voice>`; espaços e
  pontuação contam. Um `<break time="500ms"/>` gasta 23 caracteres da franquia.
- **SSML** ([estrutura](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-structure),
  página de 2026-02-25; [voz e prosódia](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-voice),
  página de 2026-01-30): `<speak version="1.0" xmlns="http://www.w3.org/2001/10/synthesis" xml:lang="…">` com pelo
  menos um `<voice name="…">`; `&`, `<` e `>` têm de ir como entidades, e aspas e apóstrofos escapados;
  `<break time="…ms"/>` de 0 a 20.000 ms em qualquer ponto do texto; `<prosody rate="…">` de 0,5 a 2 vezes.
- **A voz** ([language-support](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/language-support?tabs=tts)):
  `pt-BR-AntonioNeural` (Male), linha "Standard" de `pt-BR`, sem marca de prévia.

**Termos que importam para vídeo monetizado:**

- **Confirmado.** A [nota de transparência](https://learn.microsoft.com/en-us/azure/ai-foundry/responsible-ai/speech-service/text-to-speech/transparency-note)
  (página de 2026-03-31) diz que a voz neural pronta pode ser usada nos casos de uso listados e em "additional use
  cases selected by customers", desde que dentro da política de uso aceitável do Azure e do código de conduta, e
  que "No registration or pre-approval is required". Entre os casos listados estão narração e mídia de marketing.
- **Confirmado: é obrigatório avisar que a voz é sintética.** A mesma nota: "Microsoft requires its customers to
  disclose the synthetic nature of text to speech voices to its users", com o exemplo de um aviso falado no começo
  de uma transmissão. O [código de conduta dos serviços de IA](https://learn.microsoft.com/en-us/legal/ai-code-of-conduct)
  (versão 4.0, 2026-05-01) repete: divulgar "the synthetic nature of generated voices" para ninguém crer que ouve
  uma pessoa real. Ele também proíbe gerar ou **monetizar** conteúdo que o próprio código proíbe (engano,
  desinformação, personificação sem consentimento, conteúdo sexual ou violento explícito) e exige que o conteúdo
  publicado seja do autor ou licenciado. Não há, nesses dois textos, proibição de monetizar conteúdo permitido.
- **A confirmar** (não está nas páginas lidas): (1) uma frase que diga com todas as letras que o áudio gerado pode
  ser usado comercialmente, e se isso vale também na camada F0; os termos que mandam são os Microsoft Product
  Terms (`microsoft.com/licensing/terms`), que não foram lidos; (2) o que a F0 responde quando a franquia mensal
  acaba (a página de preços não diz; o adapter trata 429, e um 401 ou 403 vira erro com a mensagem do caso);
  (3) como o YouTube classifica essa voz na regra de conteúdo alterado ou sintético (§12 do `CLAUDE.md`).
  Enquanto (1) não for lido pelo dono, a voz não entra em vídeo publicado (§14: em dúvida sobre termos, parar e
  perguntar).

## Opções consideradas

1. **SDK de fala da Microsoft** (`azure-cognitiveservices-speech`). Dá eventos e marcações de tempo. Recusada: é
   dependência nova com binário nativo (§2.9), e a duração já vem do `ffprobe`.
2. **REST com a biblioteca padrão** (`urllib`, como os outros adapters). Uma função nova no transporte comum
   (`post_bytes`: corpo pronto, resposta binária), porque as que existiam só liam JSON. **Escolhida.**
3. **Várias cenas por chamada**, como no Gemini. Desnecessário: 20 chamadas por minuto dão conta de um episódio,
   e cortar o lote nas pausas é o ponto frágil do Gemini.
4. **Síntese em lote do Azure** (batch synthesis). Não existe na F0.

## Decisão

Um adapter `azure_speech` atrás da porta de voz, registrado pelo nome: `vp voice <id> --voz azure_speech`.
`tts` e `tts_final` em `config/providers.toml` não mudam.

- **Custo zero.** A chave não diz a camada do recurso, então a camada é declarada em `[azure_speech] tier`
  (`"F0"`). Com outro valor o adapter declara custo por chamada e o `ensure_free` o recusa sem
  `ALLOW_PAID_API=true` e teto de gasto (§2.1), como qualquer provedor pago. O que garante de fato o custo zero é o
  recurso ter sido criado na F0 no portal: é o dono quem confere isso.
- **Segredos.** `AZURE_SPEECH_KEY` (em `SecretStr`) e `AZURE_SPEECH_REGION` só no `.env`. Sem um deles, o erro
  diz qual falta. A região só aceita letras minúsculas e números, porque entra no nome do host. A chave vai só no
  cabeçalho; erro e log não levam chave, cabeçalho nem URL.
- **Fala.** Uma cena por chamada, SSML com o texto escapado. Cada `<short pause>` vira
  `<break time="<pause_ms>ms"/>` (500 ms por padrão, a ajustar na escuta). `rate` (0,5 a 2) só gera
  `<prosody>` quando não é 1. Saída `riff-24khz-16bit-mono-pcm`, gravada como veio, por `atomic_wav`.
- **Identidade (ADR 041).** `identity = "azure_speech"`; `fingerprint` =
  `azure_speech|<voz>|<formato>`, mais `|rate<v>` quando a velocidade não é 1 e `|pausa<ms>` quando o texto tem
  pausa. Os nomes dos WAVs das outras vozes não mudam (ADR 049).
- **Limites.** As chamadas são espaçadas em 60/20 s mais folga. 429, 500, 502, 503, tempo esgotado ou rede: espera
  o intervalo e tenta uma vez; o segundo 429 vira `QuotaExhausted` (as chamadas param, as falas prontas ficam e a
  próxima execução continua). 401 e 403 viram erro que manda conferir a chave e a região. Fala com mais de 5.000
  caracteres é recusada, para o corte de 10 minutos nunca acontecer calado.
- **Entrega por cena (ADR 022): não se aplica.** `delivery` é ignorado, como no Kokoro e no Gemini; a voz lê
  tudo no tom neutro. A `pt-BR-AntonioNeural` não tem estilos na tabela de vozes, então não há o que mapear.
- **Pronúncia.** O glossário por grafia (`voice/glossary.json`, §9) vale, porque troca o texto antes da voz. Um
  glossário de fonemas no pedido é erro, e não ignorado em silêncio. O `<phoneme>` do SSML fica para quando
  houver um caso.

## Consequências

- Código: `app/providers/tts/azure_speech.py`, constantes e settings próprios, `post_bytes` em
  `app/providers/http.py`, registro em `app/bootstrap/__init__.py` (fábrica em `app/bootstrap/azure_speech.py`), bloco `[azure_speech]` no `providers.toml`,
  variáveis no `.env.example`, testes em `tests/test_azure_speech_tts.py` e no contrato da porta.
- O texto da narração e o áudio passam a sair da máquina quando o dono usa esta voz (como no Gemini). Chamar o
  provedor continua sendo só a pedido do dono na sessão (§14).
- `chars_per_second = 15.0` é provisório, sem medida; só é usado se esta voz virar `tts_final`.
- Antes de usar num vídeo publicado: teste com a conta real e registro em `data/benchmarks/` (§7), escuta do
  dono, leitura dos Product Terms e a decisão sobre o aviso de voz sintética na descrição ou no vídeo.

## Emenda de 2026-11-15: fonemas IPA pelo glossário e pausa de 250 ms

- **Pedido do dono (2026-11-15):** a crítica da voz do `academia-dinheiro-pt` apontou o "TotalPass" mudando de
  pronúncia ao longo do vídeo e um corte antes dos números; o dono pediu os ajustes ("faça 1, 2, 3, 4").
- **O caso chegou.** O glossário por grafia ("Tótal Pás") estava aplicado em todas as cenas (o `glossary.json` é
  anterior a todos os WAVs), e mesmo assim a voz adivinhava a leitura pelo contexto. Um termo do glossário pode
  trazer agora `ipa` (fonemas da tabela do pt-BR); o Azure declara `phoneme_alphabet = "ipa"` (`PhonemeTTS`),
  a produção da voz longa deixa a grafia do roteiro no texto e manda o termo no `lexicon` do pedido, e o adapter o
  envolve em `<phoneme alphabet="ipa" ph="…">`. As outras vozes continuam lendo a `fala`. Só os termos presentes
  no texto entram na identidade (`|ipa<hash>`): os WAVs sem o termo mantêm o nome. O Short ainda não usa (o nome
  do WAV do Short não leva o glossário de fonemas; fica para quando houver um Short com marca).
- **Documentação (consulta de 2026-11-15):** `<phoneme alphabet="ipa" ph="…">` com `ipa`, `sapi`, `ups` ou
  `x-sampa` ([pronunciation](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-synthesis-markup-pronunciation),
  atualizada em 2026-06-05); a tabela do pt-BR existe em
  [phonetic sets](https://learn.microsoft.com/en-us/azure/ai-services/speech-service/speech-ssml-phonetic-sets)
  (vogais `i ĩ a ɔ u ũ o e ɐ̃ ə ɛ ẽ õ`, semivogais `w j`); acento `ˈ` exige marcar as sílabas com `.`; fonema
  fora da tabela volta HTTP 400 (a cena fica pendente).
- **Teste com a conta (2026-11-15):** `ˌtɔ.taw.ˈpas` aceito em três frases (S32, S38, S42), arquivos em
  `data/cache/teste-voz-academia-2026-11-15/`; falta a escuta do dono.
- **Pausa:** `pause_ms` do `[azure_speech]` passou de 500 para 250. Na S30 a pausa antes de "dois bilhões e
  trezentos milhões" media 0,54 s, mais que o dobro de uma vírgula (0,27 s), e soava como corte; com 250 ms mede
  0,29 s.

## Emenda de 2026-11-16: velocidade pela entrega da cena

- **Pedido do dono (2026-11-16):** sobre a voz do `banco-digital-dinheiro-pt`, "variar o ritmo, com calma". Num teste
  A/B do trecho do rotativo, as pausas entre frases mediam quase todas ~0,9 s (a cadência da ADR 060 já as varia);
  faltava a velocidade. Das opções (por frase, por regra; por cena, pela entrega; por marca no roteiro), o dono
  escolheu **por cena, pela entrega**, com o roteirista marcando mais cenas.
- **Decisão:** o Azure passa a obedecer à `delivery` da cena (ADR 022) só na velocidade. `[azure_speech.delivery]`
  no `providers.toml` dá um fator por entrega (de 0,7 a 1,3), que multiplica `rate`; a entrega sem fator fala em
  `rate`. A velocidade efetiva vai no `<prosody rate>` e na identidade (`|rate<v>`), então a cena neutra guarda o
  nome do WAV de antes e só as cenas com fator geram de novo. Velocidade efetiva fora de 0,5 a 2 deixa a cena
  pendente. Entonação e estilo continuam os da voz: o Antonio não tem estilos de fala no SSML.
- **Valores de partida:** `hook` 1,06, `turn` 0,94, `calm` 0,90, `invite` 0,92 (sobre `rate` 1,05). A escuta do
  dono decide os valores.

