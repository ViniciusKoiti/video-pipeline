# 016 — Voz clonada do dono no explicativo em pt-BR (Chatterbox local)

- **Status:** proposto (aceite depende da escuta às cegas contra a Charon e da medição de tempo com a máquina
  ociosa)
- **Data:** 2026-10-11
- **Etapa do roadmap:** #15 (voz por bloco), #29 (comparação de vozes)
- **Relaciona-se com:** ADR 006 (portas e adaptadores), ADR 012 (Gemini Charon; a opção 4 de lá, clonar a voz do
  dono, ficou adiada), ADR 013 (apresentador), ADR 015 (pausas), ADR 017 (apresentador do dono, proposta)

## Contexto

A ADR 012 adiou a voz clonada porque o caminho era remoto (Gemini) e a amostra de voz é dado pessoal. Em
2026-10-11 o dono testou a clonagem **local**, fora deste repositório (`~/projetos/lab-voz`, Python 3.11), com o
Chatterbox Multilingual V3 da Resemble AI, e aprovou o resultado de ouvido ("ficou muito bom"). A motivação veio do
projeto reels-radar: nos Reels de privacidade lidos, os mais compartilhados abrem com pessoa falando para a câmera
(ver ADR 017). Aqueles dados **não medem voz**; a troca de voz é uma aposta do dono, a testar.

O que foi conferido na fonte (2026-10-11):

- **Licença:** MIT no repositório `resemble-ai/chatterbox` e no cartão do modelo
  `ResembleAI/Chatterbox-Multilingual-pt-br` (`license: mit`). Falta conferir o cartão do modelo geral
  (`ResembleAI/chatterbox`) antes do aceite.
- **Idiomas:** 23 no modelo geral, com português (`pt`); existe um ajuste só de português do Brasil, não testado.
- **Marca d'água:** todo áudio sai com a marca inaudível Perth da Resemble, que identifica áudio sintético.
- **Dependências fixadas** no `pyproject.toml` deles: `torch==2.6.0`, `transformers==5.2.0`, `numpy<2`,
  `gradio==6.8.0`, entre outras; testado por eles em Python 3.11.

O que foi medido no laboratório (CPU, 12 threads, modelo geral V3, idioma `pt`, três falas de teste):

| Voz | Fala 1 | Fala 2 | Fala 3 |
|---|---|---|---|
| Padrão do modelo | 3,8 s em 108 s | 6,1 s em 128 s | 5,0 s em 99 s |
| Clonada (referência de 13 s) | 4,6 s em 130 s | 6,7 s em 522 s | 6,4 s em 456 s |

Carregar o modelo levou de 54 a 166 s. A rodada da voz clonada correu com a máquina carregada (carga média 15 em
12 núcleos), então as duas últimas medidas **não valem** como tempo de referência (regra da máquina limitada, §3).
A referência saiu de uma gravação de 45 s em Opus de baixa taxa (áudio de mensagem).

## Opções consideradas

1. **Manter a ADR 012** (Kokoro nos rascunhos, Charon no final). Nada muda; a voz continua genérica.
2. **Chatterbox local com a voz do dono** (proposta). Sem custo, sem cota diária, sem envio de dados; lento em CPU
   e com dependências que podem conflitar com as do extra `tts`.
3. **Clonagem remota** (Gemini `POST /v1beta/voices` ou outro serviço). Mais rápida; manda a voz do dono para
   terceiros e os termos da camada gratuita pedem para não enviar dado pessoal. Continua adiada.
4. **XTTS-v2 e F5-TTS.** Descartados por licença: Coqui Public Model License (não lida; a página do modelo não diz
   se permite uso comercial) e pesos em CC-BY-NC. **OpenVoice V2** (MIT) não tem português nativo.

## Decisão

Proposta: **voz clonada do dono com o Chatterbox, local, como terceira opção de voz**, sem tirar Kokoro nem
Charon. Qual delas vai no vídeo final continua sendo uma linha em `config/providers.toml`.

- **Adapter** `app/providers/tts/chatterbox.py` na porta `TTSProvider` (ADR 006), `ProviderInfo(remote=False,
  usd_per_call=0)`. Cache pela fala, pelo modelo, pelo idioma e pelo **hash do arquivo de referência**.
- **Ambiente separado.** As dependências fixadas do Chatterbox não entram no `uv.lock` deste projeto enquanto a
  compatibilidade com o extra `tts` (Kokoro, PyTorch) não for conferida. Até lá o adapter chama um ambiente próprio
  por subprocesso, como o motor Remotion já faz com o Node.
- **Amostra de voz é dado pessoal do dono:** fica fora do Git (o `.gitignore` já recusa `*.wav`), em caminho
  indicado no `.env`, e nunca é enviada a provedor remoto.
- **Divulgação:** voz clonada continua sendo voz sintética. O passo de divulgação no upload (§12) não muda, e a
  marca d'água do modelo permanece.
- **Uma cena por chamada**, em fila, com retomada: pelo tempo medido, um vídeo de 80 s leva dezenas de minutos.

## Consequências

- `app/providers/tts/chatterbox.py`, bloco `[chatterbox]` em `config/providers.toml` (modelo, idioma, caminho da
  referência por variável do `.env`), teste do adapter com fixture e sem rede, teste `slow` com o modelo real.
- `chars_per_second` da voz clonada precisa ser medido: o `vp check` estima a duração da cena com ele (ADR 012).
- A marca `<short pause>` (ADR 015) precisa de tratamento próprio neste adapter; não foi testada.
- Sem dicionário de fonemas: nome próprio errado pede a mesma lista "nome → como falar" da ADR 012.
- `CLAUDE.md` §1, §7 e §9 mudam quando esta ADR for aceita.

## Pendente antes do aceite

1. **Escuta às cegas** do dono, no molde da ADR 012: as mesmas falas do vídeo-régua em Charon, Kokoro e voz
   clonada, com o mesmo volume e letras sorteadas.
2. **Tempo com a máquina ociosa** (sonda `cpu_probe()` antes), por fala e por vídeo-régua inteiro.
3. **Ajuste de português do Brasil** (`Chatterbox-Multilingual-pt-br`) contra o modelo geral, na mesma escuta.
4. **Referência melhor:** gravação em WAV ou em taxa alta, no lugar do áudio de mensagem.
5. **Compatibilidade de dependências** com o extra `tts`, para decidir entre ambiente separado e extra novo.
6. **Licença do modelo geral** conferida no cartão do Hugging Face e registrada em `data/benchmarks/`.

## Implementado como experimento (2026-10-12)

A pedido do dono, o adapter entrou antes do aceite, sem mudar a voz padrão (ADR 012 segue valendo):

- `app/providers/tts/chatterbox.py` e `chatterbox_worker.py`: o modelo roda no ambiente próprio, num processo que
  carrega uma vez e atende uma cena por pedido; `<short pause>` vira silêncio (`pause_ms`), sem chegar ao modelo.
- `CHATTERBOX_PYTHON` e `CHATTERBOX_REFERENCE` no `.env`; bloco `[chatterbox]` em `config/providers.toml`.
- Uso: `montar_episodio.py <id> --voz=chatterbox`. A chave de cache da fala inclui o hash da gravação.
- Medido com a máquina ociosa (sonda 0,05 s): 3,4 s de áudio em 180 s (primeira fala, com aquecimento) e 6,8 s em
  194 s. `chars_per_second = 14.0` é provisório (duas falas: 12,9 e 14,4).

Os seis itens de "Pendente antes do aceite" continuam pendentes.
