# Guia de animação de texto nos Reels (referência para quem implementa e para os agentes)

- **Estado:** rascunho para aprovação do dono (2026-10-07). Desde 2026-10-14 a legenda palavra a palavra (§3) está decidida e implementada pela ADR 023; o resto segue rascunho. Em conflito, valem `CLAUDE.md`, as ADRs e o `AGENTS.md` do motion-kit. Onde diz **decisão aberta**, o agente não decide: pergunta ao dono.
- **Origem:** o Reel de referência de `@brock11johnson` (2026-10-04), lido em quadros, e um conselho de modelos. Registro, ranking e conferências em `docs/pesquisa/animacao-reel-referencia-2026-10.md`; quadros em `data/cache/referencias/DeFFzgiCQOe/` (fora do Git).
- **Prioridade do dono:** legenda palavra a palavra (a opção "c" da mensagem de 2026-10-07). O vocabulário da seção 2 vale para o resto.
- **Escopo:** Reels 9:16 do `explainer` (ADR 014). O motion-kit é quem anima; o template (`video/`) só liga as peças aos planos.
- **Rótulos:** [F] confirmado em arquivo ou quadro; [I] inferência; [H] hipótese.

## 1. Princípios

1. Estudamos o mecanismo da referência; **não copiamos** identidade (fonte, paleta, enquadramento, rosto).
2. O movimento tem vocabulário curto e nomeado. **Peça nova não escreve mola, easing nem duração em linha.**
3. A tela não calcula e não inventa tempo (ADR 011, decisão 7; ADR 015): texto sincronizado com a fala usa tempo que vem do áudio real.
4. A legenda continua na tela junto com o `keyword` (ADR 021, que emenda a decisão 5 da ADR 011).
5. Legenda, fonte, tarja, carimbo e janela ficam dentro da área segura vertical (ADR 014): 1080×1920, topo 288, base 500, direita 140, esquerda 60 px. Número, comparação e gráfico usam o quadro todo.
6. Uma frente por vez, um PR por frente. Mudou o visual: sonda de CPU antes do render e versão nova do vídeo-régua (`CLAUDE.md` §1).

## 2. Vocabulário de movimento (proposta)

| Token | Comportamento | Quadros a 30 fps | Uso | Base |
|---|---|---|---|---|
| `cut` | aparece inteiro num quadro; sem saída animada | 0 | título, item de lista, número-chave, troca de bloco de legenda | [F] na referência, título, "5X", itens e blocos de legenda surgem num quadro só |
| `pop` | escala e opacidade, ease-out, sem quique | 3 a 4 | palavra de gancho | [F] "POST" vai de ≈0,67 a ≈0,88 e a 1,0 da largura em 3 quadros (dois revisores mediram, cada um por conta própria) |
| `rise` | a entrada atual do kit (sobe e aparece) | `KineticHeadline`: mola 16/190/0,6 em 16 quadros; `CaptionText` e `useAnimateIn`: 18 | padrão editorial: **a régua não muda** | [F] `KineticHeadline.tsx`, `CaptionText.tsx`, `useAnimateIn.ts` |

- **Hoje no kit [F]:** cerca de 10 configurações de mola escritas em linha nas peças, entradas de 16 a 18 quadros nos textos e **nenhum token de movimento**: o `MotionTheme` guarda só fonte, cores e neon. O `KineticHeadline` destaca por trecho fixo, com transição de cor de 10 quadros; a referência destaca a palavra falada e troca na hora.
- **Decisões abertas:** nomes (`ENTRANCES` com `entranceStyle(preset, local, fps)` ou `MOTION` em `/theme`); nome da prop de entrada (`enter` ou `entrance`); escala inicial do `pop` (0,45 ou 0,85 propostas; ≈0,67 observada no primeiro quadro medido).

## 3. Legenda palavra a palavra (prioridade do dono)

### 3.1 O que a referência faz [F, quadros]

- Blocos de **2 a 3 palavras**, em maiúsculas, brancos com traço preto fino. A **palavra falada** fica amarela e o destaque passa de uma palavra à seguinte **sem lacuna** (cada uma fica de ≈0,13 a ≈0,5 s). O bloco inteiro troca sem transição.
- Não há legenda nos 3,9 s do gancho. A legenda fica na altura do peito.
- Medidas de **um só membro do conselho, não reproduzidas**: 157 de 162 trocas sem lacuna e cerca de 92% do vídeo coberto por legenda.

### 3.2 Especificação proposta (aprovação do dono pendente)

- **Peça:** `WordCaption` em `@viniciusk/motion-kit/editorial`, com `words: {text, from, to}[]` (quadros), `block` (padrão 3), `activeColor` (padrão `theme.accent`), `hold` (a palavra fica acesa até o início da próxima) e `swap` (`cut`) [I, proposta do conselho]. Reaproveita `layoutText` e `legibilityShadow`.
- **Destaque:** uma palavra por vez, com `cut`. A cor é a do tema (dourado `#F2B134`); o amarelo é a identidade da referência.
- **Posição:** acima da base segura, como a legenda de hoje (`Scene.tsx`, `Caption`: `paddingBottom: safe.bottom`), **não** no centro, que é onde fica o conteúdo [I].
- **Convivência:** fica visível junto com o `keyword` (ADR 021); sem `words`, a cena cai na legenda por frase.
- **Tipografia:** a de hoje (Inter, OFL; peso 600; sombra de legibilidade). Traço grosso, caixa alta e amarelo são **decisão aberta** (segunda identidade visual).

### 3.3 Dependência crítica: tempo por palavra

| Fato | Onde |
|---|---|
| Até 2026-10-14 `captions` era `null` em todos os `episode.json`. Desde a ADR 021 o SRT é por frase, com o tempo das fronteiras tirado dos silêncios do WAV: serve à legenda, não ao destaque por palavra | [F] `app/media/captions.py`, ADR 021 |
| A ADR 014 já decidiu legenda queimada no vertical, com SRT editável | [F] `docs/decisions/014-perfil-vertical.md` |
| "Tempo por palavra vindo do alinhamento (#17)" ficou **fora** da ADR 011 | [F] ADR 011, item 11 |
| Os `cues` de hoje são por frase (`Cue = {from, to, text}`, em quadros), lidos do SRT em `app/render/remotion.py` (l. 160 a 163) | [F] |
| O Kokoro 0.9.4 só devolve tempo por palavra no G2P inglês; em pt-BR sobra `pred_dur` por fonema. O adaptador do Gemini só lê áudio | [F] `kokoro/pipeline.py`, `app/providers/tts/gemini.py` |
| O candidato de alinhamento do projeto é o Groq Whisper gratuito, **provedor externo: só quando o dono pedir** | [F] `CLAUDE.md` §7 e §14 |

- **Regra: proibido fingir destaque com o modelo proporcional.** Ele já errou ~0,8 s no início de um plano (ADR 015). Sem tempo por palavra, a cena usa legenda por frase ou bloco estático, sem destaque.
- **Ordem de trabalho para a opção "c" [I]:** (1) #17: alinhar o áudio e gerar o SRT; (2) decidir onde mora o tempo por palavra; (3) `WordCaption` no kit, com demo e tempos de exemplo, o que **não depende** da #17; (4) integração no `Scene.tsx` e pin novo, que esperam a #17.
- **Decidido (ADR 023, 2026-10-14):** o tempo por palavra vem do Whisper da Groq e mora em `captions.words.json`, ao lado do SRT; o `episode.json` não muda e o adaptador converte ms em quadros.

## 4. Gancho por palavra (`keyword` com `pop`)

- Hoje o `KeywordShot` (`video/src/Editorial.tsx`, l. 353 a 360) usa `KineticHeadline` com `at={4}` e **sem** `wordFrames` [F].
- Proposta: em retrato, `enter="pop"` e, quando houver tempo por palavra, `wordFrames`. Continua um plano `keyword` por cena (o `vp check` alerta para mais de um), com até 8 palavras (`KEYWORD_MAX_WORDS`) e de 1,5 a 6 s por plano.
- Não empilhar "POST / EVERYTHING / 5X" como três planos. Tamanhos diferentes por palavra não existem no kit: fora do primeiro conjunto.

## 5. Lista que acumula (fora do primeiro conjunto)

- Título e itens entram com `cut`, na hora em que são ditos, e ficam. Na referência: 5 itens em ~6,5; 9,2; 12,9; 17,5 e 24,2 s (medição por pixel de **um** revisor), atravessando cortes de câmera.
- **Por que não agora [F]:** plano novo exige ADR e mudança de schema; o teto é de 6 s por plano (`MAX_SHOT_MS`; `LONG_KINDS` só tem `network` e `timeline`); em retrato só os dois cantos de cima são livres para a janela do apresentador (ADR 014); cada cena é um render, então os itens anteriores entram já assentados, como a janela (`at={-60}` em `HostWindow.tsx`); os intervalos são irregulares e o `useStagger` é uniforme.
- **Sobe para 1º** se os Reels virarem listas de passos (por exemplo, no recorte do MEI).

## 6. Fora de escopo

| O quê | Por quê |
|---|---|
| Texto atrás da pessoa | não há pessoa em câmera; exigiria máscara |
| Traço grosso, caixa alta, amarelo | identidade da referência; só com uma segunda identidade visual |
| Cortes de câmera com reenquadramento | não há câmera; a janela do apresentador já muda de canto |
| Texto que atravessa cenas | um render por cena |

## 7. Regras por agente (proposta)

| Quem | Faz | Não faz | Como se confere |
|---|---|---|---|
| `roteirista` | `keyword` curto (até 8 palavras), um por cena; deixa o tempo para a âncora | não escreve tempo de palavra, nem lista de itens como vários `keyword` | `vp check` |
| `verificador` | confere que o texto na tela está nas fichas | não julga o movimento | relatório |
| Quem implementa (kit e template) | usa tokens; props em px de um quadro de 1080 de altura (`useUnit`); demo em `examples/Root.tsx`; `typecheck`, build e `dist/`; quadros inicial, intermediário e final no Studio | não escreve mola em linha; não decide as decisões abertas; não muda `episode.json` sem ADR | critérios da seção 8 |
| Conselho (`/llm-council`) | decisão com trade-offs reais, só quando o dono pedir | não substitui o dono nem confere fato | `~/.claude/skills/llm-council/SKILL.md` |

## 8. Critérios de aceite

1. Nenhuma mola, easing ou duração em linha numa peça nova: tudo vem de token ou de prop com default de token.
2. `cut` = 0 quadros; `pop` = 3 a 4 quadros e sem quique; `rise` = a entrada atual (a régua não muda sem aval).
3. Animação determinística por quadro, sem `Math.random` e sem estado (`AGENTS.md` do kit).
4. Destaque por palavra só com tempo por palavra do áudio. Tolerância de sincronia: **decisão aberta**, a definir com o primeiro alinhamento real.
5. Legenda dentro da área segura, visível também durante o `keyword` (ADR 021).
6. Fonte nova só com licença registrada na lista fechada (`CLAUDE.md` §6); hoje, Inter (OFL).
7. Kit: demo registrada, `npm run typecheck`, build e `dist/` versionado. Template: pin novo, sonda de CPU, vídeo-régua vN com a folha de quadros marcando só o que se pretendia mudar.
8. Nenhum render ou clipe de teste sem pedido do dono.

## 9. Decisões abertas do dono

1. Primeira entrega: confirmar a leitura da opção "c" (legenda) e se o `pop` e o `cut` entram junto, já que não dependem da #17.
2. Nomes dos tokens e da prop de entrada; escala inicial do `pop`.
3. ~~Onde mora o tempo por palavra e quem faz o alinhamento.~~ Decidido em 2026-10-14 (ADR 023): `captions.words.json` e Whisper da Groq, com `--legenda-palavra`.
4. Haverá uma segunda identidade visual? Clara ou enérgica (contorno, caixa alta, amarelo)? **Na legenda, decidido em 2026-10-14 (ADR 023): enérgica.** O resto do template segue `editorial`. O conselho de estilos por vertical (`docs/pesquisa/estilos-por-vertical-2026-10.md`) achou que o `editorial` basta em 9 das 10 verticais e que um modo claro custa mais do que trocar cores.
5. Ligado em 2026-10-07 ao `CLAUDE.md` (§14) e à skill `roteiro-explicativo`. Falta ligar à skill `componentes-do-kit`, que é a de quem implementa no kit e no template.
