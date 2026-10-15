# 022 — Entrega da fala por cena: `delivery` no roteiro, ênfase na voz clonada

- **Status:** aceito pelo dono em 2026-10-14 ("pode fazer isso"), depois de ouvir a prévia do primeiro reel da
  série da confeitaria
- **Data:** 2026-10-14
- **Etapa do roadmap:** voz (#16) e roteiro (#28)
- **Relaciona-se com:** ADR 012 (voz Gemini, direção de fala por idioma), ADR 015 (pausas), ADR 016 (voz clonada),
  ADR 019 (objetivo), ADR 020 (conta na tela)

## Contexto

O dono achou o áudio da prévia "muito linear": a narração entra plana do começo ao fim, e um Reel costuma abrir
mais animado, com um chamado ("você sabe quanto custa um docinho?"). Duas causas somadas: o Kokoro, voz dos
rascunhos, não tem controle de ênfase; e o roteiro abriu com uma frase longa de explicação, não com um chamado.

O que o pipeline tinha: no Gemini, uma direção de fala por idioma (`speech_metadata.style`, ADR 012), igual para
todas as cenas; no Chatterbox, o processo do modelo chamava `generate` só com texto, idioma e referência, deixando
`exaggeration` (ênfase, padrão 0,5) e `cfg_weight` (quanto menor, mais vivo e rápido, padrão 0,5) no padrão em
toda cena. Nenhum lugar do roteiro dizia onde a voz deveria subir.

## Decisão

1. **A cena declara a entrega.** `Scene.delivery` no `scenes.json`, opcional: `"hook"` para a cena que chama
   (abertura, pergunta final), ausente ou `"neutral"` para o resto. Lista fechada; outro valor é erro de schema.
2. **A porta de voz carrega a entrega.** `SpeechRequest.delivery` (padrão `"neutral"`). O provedor que não souber
   ignora: o Kokoro segue igual; o Gemini continua com a direção por idioma (uma direção por cena é mudança à parte).
3. **A voz clonada obedece.** `config/providers.toml` tem `[chatterbox.delivery]` com `exaggeration` e `cfg_weight`
   por entrega (`neutral` 0,5/0,5; `hook` 0,8/0,3, valores do teste de 2026-10-14, ajustáveis). O adapter põe os
   dois no pedido e o processo do modelo os passa ao `generate`. Entrega desconhecida cai na neutra.
4. **Cache.** Na montagem, a chave do WAV inclui a entrega quando ela não é neutra e a voz é a clonada: trocar
   `delivery` regera só aquela cena; os rascunhos no Kokoro não mudam de chave.
5. **O roteirista marca.** A skill `roteiro-explicativo` pede `delivery: "hook"` na cena de abertura e na pergunta
   final, e um texto curto nessas cenas: chamado em pergunta, sem explicação longa. A ênfase é da voz; o texto
   precisa caber nela.

## Consequências

- `scenes.json` ganha um campo opcional; roteiros antigos continuam válidos.
- Os valores de `hook` são um ponto de partida: o dono ouve e ajusta no `providers.toml`, sem código.
- Rascunho no Kokoro continua plano: a prévia de revisão não mostra a entrega; a voz final, sim. Se isso atrapalhar
  o gate 4, a prévia passa a usar a voz clonada só nas cenas `hook` (proposta, não decidida).
- Fora desta ADR: trilha sonora (sem suporte no template) e direção de fala por cena no Gemini.
