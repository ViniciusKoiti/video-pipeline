# Prompt: loop de melhoria da voz até nota 8–10 no earshot (padrão de qualidade)

Prompt para o agente que conduzir o loop. Escrito em 2026-11-05 a pedido do dono. Estende `busca-polimento-voz.md` (fluxo e
orçamento) e `prompt-polimento-de-voz.md` (cadeia de DSP). Não é decisão: cada parada abaixo é do dono, e nada vira padrão sem a
emenda à ADR 054 e a escuta dele.

## Pedido

Melhorar a voz final (Chatterbox clonado do dono, hoje no Modal) com um **loop de rodadas curtas e medidas**, até que a nota do
earshot fique entre **8 e 10** de forma repetível, e então propor essa régua como padrão de aceite para qualquer vídeo.
"Padronizar" quer dizer: critério escrito, medido da mesma forma em todo episódio, com o que passa e o que reprova.

## O que "nota" significa (ler antes de começar)

- A **única nota de 0 a 10** do earshot é a do `llm_critique` (Gemini): `critique.overall.score`, mais `scores.realism`,
  `mix_balance` e `loudness`. Hoje, num trecho de 45,6 s do `ayanokoji-provocacao-epicteto`: overall 7,0; realism 7,0;
  mix_balance 7,0; loudness 8,0 (`data/benchmarks/ayanokoji-voz-earshot-llm-2026-11-04.json`).
- O `critique` local compara com filmes de lançamento e devolve veredito (launch-grade, close, needs work, not launch-grade) e
  métricas ok/low/high. **Não dá nota 0–10**, e a referência é filme, não narração. Use-o como diagnóstico e calibre antes de usar como porta.
- O `measure` é exato (LUFS, pico real, ruído de fundo, clipping): é a porta técnica, sem opinião.
- A nota do Gemini é **opinião, não MOS**, e varia entre chamadas. Se `synth_intended=true` (voz clonada de propósito), a síntese
  não conta como defeito: fixe esse valor em todas as chamadas do loop e **declare no relatório** que a nota não mede
  "parece humano", mede "está bem feita como voz clonada".

## Regras que não mudam (do `busca-polimento-voz.md` e do CLAUDE.md)

- **Nenhum áudio sai da máquina sem autorização do dono naquela sessão** (`llm_critique` envia o trecho ao Google; `consent=true` só
  depois de ele autorizar, trechos e número de chamadas ditos). Camada gratuita, sem faturamento (§2.1); sem trocar de modelo
  ou endpoint sozinho.
- **Nenhuma síntese nova (Modal) sem pedido do dono.** O loop começa só com WAVs brutos que já existem (`voice/` e a baseline
  `renders/baseline-voz-2026-11-04/`), como a Fase 1b. Mudar texto, glossário, entrega ou referência exige regerar: peça antes.
- Um render ou processamento pesado por vez, com a sonda `cpu_probe()` antes (acima de 0,3 s = máquina limitada, medida inválida).
- Não apagar baseline, WAVs brutos nem arquivos de gate aprovado (§2.6). Saídas do loop em pasta nova com data.
- `voice_polish.enabled` fica `false`. Atingir a meta **não** liga nada: ligar é decisão do dono e emenda à ADR 054.
- Nota alta isolada não aprova. Uma resposta válida baixa não se descarta nem se repete só para subir a nota.
- Sem dependência nova sem licença (§2.9). Testes sem rede (§2.10).

## Fase 0 — calibrar o avaliador (antes de qualquer candidata)

1. Congelar o **controle**: os trechos, os arquivos, os hashes, o modelo do avaliador e o texto da rubrica. A meta (8) **não entra**
   no prompt do avaliador.
2. Montar dois conjuntos de trechos de 20–45 s: **ajuste** (3 ou mais, onde se mexe nos parâmetros) e **reservado** (3 ou mais, de
   pelo menos dois episódios diferentes, que nunca guiam um ajuste). Incluir muitos "s/ch/x", nomes próprios difíceis, pergunta,
   número e uma pausa longa.
3. Medir o **ruído do avaliador**: o mesmo trecho de controle avaliado N vezes (N a combinar com o dono; proposta: 3). Registrar a
   dispersão da nota. **Uma melhora menor que essa dispersão não é melhora.**
4. Registrar a nota do controle em cada trecho e o `critique` local do controle (veredito e métricas fora da faixa), para saber
   quais métricas do filme não se aplicam a fala.
5. Se o controle já estiver em 8 ou mais com dispersão pequena, **pare e relate**: o padrão já existe e o loop não é necessário.

Saída da fase: `rubrica.md`, `controle.json` (hashes, trechos, modelo, dispersão) e a tabela das notas do controle. Parada: o dono
vê a dispersão e autoriza as chamadas das rodadas.

## O loop (uma rodada)

1. **Ler os defeitos** da última avaliação (`issues`, `top_fixes`, `synthetic_or_cheap`) e classificar cada um pela alavanca que o resolve:

   | Defeito apontado | Alavanca | Precisa de |
   |---|---|---|
   | sibilância, aspereza, brilho excessivo | de-esser, EQ, `highpass` (`[voice_polish]`) | só WAVs existentes |
   | nome mal pronunciado | glossário `voice/glossary.json` | regerar a cena (pedir) |
   | entonação linear, final de frase caído | `delivery` e parâmetros do Chatterbox | regerar (pedir) |
   | timbre ou "som de síntese" | outra referência de voz (ADR 053) | gravação nova do dono |
   | pausa, ritmo | `<short pause>` e texto | regerar (pedir) |
   | volume irregular | nivelamento (ADR 054) | só WAVs existentes |

   Se o defeito não tem alavanca em DSP, **registre que DSP não resolve** e não gaste candidata com ele.
2. **Uma variável por rodada** (por exemplo, só a intensidade do de-esser). No máximo **2 candidatas** por rodada, só de WAVs existentes.
3. **Porta técnica** em cada candidata, com o `measure`: mesma duração (±20 ms), volume igualado ao do controle (−16 LUFS ± tolerância), pico
   dentro do teto, sem clipping. Reprovou? Registrar e descartar, sem avaliar.
4. **Avaliar às cegas**: nomes neutros, mesma rubrica, mesma duração de trecho, `synth_intended` igual. Cada resposta válida
   é registrada, inclusive nota baixa e empate. Erro 429/503/timeout é indisponibilidade e **não conta como candidata**; segue
   a regra de retentativas e o teto de chamadas já autorizados em `busca-polimento-voz.md`.
5. **Comparar com a dispersão da Fase 0.** Candidata só "melhora" se superar o controle por mais que o ruído, em mais de um trecho.
6. **Verificar no conjunto reservado** (nunca usado para ajustar) e só então propor ao dono a **escuta cega** (`polimento_voz_ab.py`).
7. Registrar a rodada em `rodadas.jsonl` (variável, valor, hashes, notas, decisão) e atualizar a tabela. Parada para o dono se a
   candidata passou nos passos 3–6.

## Régua proposta para "padrão" (a calibrar na Fase 0, não vale antes)

Uma versão da voz só é proposta como padrão se, no conjunto **reservado**:

- mediana do `overall` ≥ 8 (do número de avaliações válidas autorizado por trecho: proposta 3, mínimo 2, e com 2 vale a média) e nenhum trecho abaixo de 7;
- `realism`, `mix_balance` e `loudness` ≥ 7 em todos os trechos e ≥ 8 na mediana;
- nenhum `issue` de severidade média ou alta que se repita em mais de um trecho;
- porta técnica limpa (`measure`): −16 LUFS ± tolerância, pico real ≤ teto, sem clipping, ruído de fundo registrado;
- escuta cega do dono: prefere a nova ou não nota diferença, **sem notar artefato**, em pelo menos 4 de 5 pares.

Nota 9 ou 10 é bem-vinda e não é exigida. Se a nota ficar presa em 7 porque o avaliador reprova a própria natureza sintética, relate o teto
em vez de piorar o áudio para subir a nota.

## Paradas

- Meta atingida **e** confirmada no reservado e na escuta: parar e propor o padrão.
- Três rodadas sem melhora acima do ruído, orçamento de chamadas gasto, cota ou erro permanente: parar com `needs_review` e relatar.
- Resultado inconclusivo (o avaliador não distingue as versões): não aumentar intensidade nem tentativas por conta própria.
- Qualquer pedido que exija regerar voz, enviar outros trechos ou ampliar chamadas: parar e perguntar uma vez, com opções.

## Entrega

Pasta `data/benchmarks/voz-loop-<data>/` com `rubrica.md`, `controle.json`, `rodadas.jsonl`, os WAVs das candidatas e um `index.html` de escuta
(como em `ayanokoji-polimento-ab-2026-11-04/`). Relatório curto no fim: notas do controle e das candidatas lado a lado, dispersão do
avaliador, o que foi tentado e descartado, o que o DSP não resolve, e a proposta de régua (ou a razão de não haver).
Rodar `uv run pytest` e `uv run ruff check .` se mexer em código.

## Como começar

> Leia `docs/specs/prompt-loop-voz-earshot.md`, `busca-polimento-voz.md` e `prompt-polimento-de-voz.md`. Faça só a **Fase 0**: me mostre os
> trechos de ajuste e reservados que você propõe, a rubrica e o plano de chamadas ao Gemini (quantas, em quais trechos). Não envie áudio nem
> gere voz até eu autorizar.
