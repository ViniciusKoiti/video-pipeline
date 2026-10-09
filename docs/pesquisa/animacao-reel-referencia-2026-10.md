# Animações de texto de um Reel de referência e como padronizá-las no motion-kit

- **Consulta:** 2026-10-07. **Referência:** Reel de `@brock11johnson` (publicado em 2026-10-04), arquivo fornecido pelo dono em `docs/post-everything-five-times-DeFFzgiCQOe.mp4` (o `.gitignore` ignora `*.mp4`; não vai para o Git). Quadros extraídos com ffmpeg em `data/cache/referencias/DeFFzgiCQOe/` (pasta fora do Git).
- **Método:** conselho de modelos (skill `llm-council`, em `~/.claude/skills/llm-council/`): 4 membros (opus, sonnet, fable, haiku) responderam sozinhos, revisaram as respostas anônimas e um presidente (opus) escreveu a resposta final. Todos são Claude, então os erros se correlacionam; o ranking mede preferência entre pares, não correção.
- **Estado:** análise. **Nada foi implementado; o dono ainda não disse o que quer levar da referência.** O vídeo foi usado só para estudar mecanismo, sem copiar identidade visual.
- **Material bruto** (brief, respostas, revisões): `/tmp/.../scratchpad/council/animacao-reel-referencia/` (temporário). O que vale está abaixo.

## 1. Resultado do conselho (resposta do presidente)

### Recomendação

1. **Entrada curta por palavra** (POST, EVERYTHING): escala e opacidade em 3 a 4 quadros, sem quique [F], mais o **corte seco** do 5X, do título e dos itens [F]. Cabe no `keyword`, o plano mais usado em retrato (27 de 86) [F].
2. **Lista que acumula**: útil em Reels de lista [I], mas plano novo exige ADR [F].
3. **Legenda palavra a palavra**: falta tempo por palavra; a #17 não começou, o Kokoro só o dá em inglês e o Gemini só devolve áudio [F].

Fora: texto atrás da pessoa (não há pessoa) [F], traço grosso e maiúsculas amarelas (acabamento) e cortes com reenquadramento (a janela já muda de canto) [I].

**Menor conjunto**, sem tocar o `episode.json` [I]:
- **Kit:** tokens de entrada `rise` (a atual, 16 quadros no `KineticHeadline`), `pop` e `cut` (0 quadros). Nome em aberto: `ENTRANCES` + `entranceStyle(preset, local, fps)` (opus) ou `MOTION` em `/theme` (sonnet).
- **`KineticHeadline`:** prop de entrada (`enter`; o opus diz `entrance`), padrão `rise`, para a régua não mudar.
- **Template:** `KeywordShot` em retrato com `enter="pop"`; hoje passa só `at={4}`, sem `wordFrames` [F].

Os `wordFrames` no tempo da fala esperam decidir onde mora o tempo por palavra [I].

### Onde o conselho concordou

- O kit não tem vocabulário de movimento: ~10 molas escritas em linha, sem token; entradas de texto de 16 a 18 quadros [F].
- A lista esbarra no teto de 6 s por plano; na janela, presa aos cantos de cima em retrato [F], onde a lista ficaria [I]; e no render por cena: só repondo itens em quadro negativo, como a janela [F]. `useStagger` só faz intervalos uniformes [F]; os da referência são irregulares [I].
- Na referência, a legenda some no gancho, como a nossa com `keyword` [F].

### Onde divergiu e por quê

- **Legenda primeiro** (sonnet; haiku, com erros confirmados). Minoria a guardar: a ADR 014 já decidiu legenda queimada no vertical, e os 11 `episode.json` têm `captions: null` [F]. Mas, até a #17, ela só entrega tokens [I], e o modelo proporcional já errou ~0,8 s no início de um plano (ADR 015) [F]; pelo critério do próprio sonnet, com a #17 parada, lista e pop sobem [I]. O gancho mostra algo já, com a lacuna aberta [I].
- **Onde mora o tempo por palavra.** Três propostas o derivam no adaptador, como os `levels` da boca [F]; mas todo tempo por âncora (`start_ms`, `steps_ms`) está no `episode.json`, e o adaptador só o converte em quadros [F]. Derivar dispensa ADR e tira o tempo do contrato [I]; gravar segue o padrão e exige ADR [F].
- **Escala inicial do `pop`:** 0,45 (opus) ou 0,85 (fable). POST surge menor e translúcido, depois ~0,67 e ~0,88 da largura final [F]; dois revisores acham 0,85 mais contido que a referência. Serve se o `pop` destoar do `editorial` sóbrio [H].
- **Lista primeiro** se os Reels virarem séries em lista (opus: `votorantim-5-jeitos` [I]; fable: nicho MEI).

### O que ninguém verificou

O áudio (logo, a sincronia com a fala); o erro proporcional por palavra no `keyword` em pt-BR (os 100 a 300 ms do opus são [H]; o fable voltaria ao stagger acima de ~0,25 s); texto atrás da pessoa; custo de render; se o `pop` combina com o `editorial` ou treme após compressão [H]; o que o dono quer levar e se haverá segunda identidade (sonnet: contorno, maiúsculas e `pop` virariam preset de tema). Medidas de um membro só: "157 de 162 trocas", "~92% com legenda", "0 de 16 quadros" e os instantes 6,53/9,17/12,93/17,53/24,23 s.

### Primeiro passo concreto

Com o aval do dono (pendente [F]): PR no `~/projetos/motion-kit` com os tokens e a prop de entrada (padrão `rise`), demo em `examples/Root.tsx`, typecheck, build e `dist/` (AGENTS.md). No `video/`: pin novo, `KeywordShot` em retrato com `enter="pop"`, sonda de CPU e versão nova da régua, cuja folha de quadros deve mudar só onde se pretendia.

## 2. Ranking da revisão anônima


Mapa de rótulos (desfeito depois das revisões):

- Resposta A = fable
- Resposta B = opus
- Resposta C = haiku
- Resposta D = sonnet

Rankings dos revisores (do melhor ao pior):

- opus: B (opus) > D (sonnet) > A (fable) > C (haiku)
- sonnet: D (sonnet) > B (opus) > A (fable) > C (haiku)
- fable: D (sonnet) > B (opus) > A (fable) > C (haiku)
- haiku: C (haiku) > B (opus) > A (fable) > D (sonnet)

Posição média (menor é melhor):

- Resposta B (opus): 1.75
- Resposta D (sonnet): 2.00
- Resposta A (fable): 3.00
- Resposta C (haiku): 3.25

Posição média sem o voto do próprio autor:

- Resposta B (opus): 2.00 (votos [2, 2, 2])
- Resposta D (sonnet): 2.33 (votos [2, 1, 4])
- Resposta A (fable): 3.00 (votos [3, 3, 3])
- Resposta C (haiku): 4.00 (votos [4, 4, 4])

Observação: 3 de 4 revisores colocaram a própria resposta em 1º (o haiku foi o único a pôr a sua em 1º contra 3 votos de 4º lugar). A ordem B > D > A > C se mantém sem os votos próprios.

## 3. Conferências do coordenador no repositório


**Conferido por mim [F]:**
- `captions` é `null` nos 11 `episode.json` em `data/episodes/*/` (nenhum Reel tem legenda queimada hoje). `docs/ROADMAP.md` (l. 22 e 90): #17 (legendas) "não começada" e não existe `captions.srt`. A ADR 014 (seção "Legendas", l. 50 a 52) já decidiu que o vertical sai com legenda queimada e SRT editável: a decisão existe, a capacidade não.
- ADR 011, item 11: "tempo por palavra vindo do alinhamento (#17)" está **fora** daquela ADR.
- Kokoro 0.9.4 instalado (`.venv/lib/python3.12/site-packages/kokoro/pipeline.py`): `join_timestamps` preenche `start_ts` e `end_ts` por `MToken` a partir de `pred_dur`; os `MToken` vêm do G2P inglês (`lang_code` `a` e `b`, l. 106); em `pt-br` (`p`) só resta `pred_dur` por fonema. O Gemini TTS só devolve áudio.
- `video/src/Editorial.tsx` l. 353 a 360: `KeywordShot` usa `KineticHeadline` com `at={4}` e **sem** `wordFrames`.
- `app/render/remotion.py` l. 73 e 74 converte `shot.steps_ms` em `stepFrames` (precedente: tempo por âncora vira quadros no adaptador); l. 196 deriva `levels` do envelope da boca.
- `app/pipeline/check.py`: `MAX_SHOT_MS = 6000` (l. 39), `LONG_KINDS = {"network", "timeline"}` (l. 46), alerta para mais de um `keyword` por cena (l. 245 e 246); `app/pipeline/shots.py` l. 28: `MIN_SHOT_MS = 1500`.
- ADR 014 (l. 44 a 47): em retrato só os dois cantos de cima ficam livres para a janela do apresentador.
- `video/src/HostWindow.tsx` l. 39: `at={fromCorner ? -60 : undefined}` (peça já assentada ao começar a cena).
- Contagem de planos nos `scenes.json` em retrato: nos 4 episódios armenia-brasil, armenia-capital-humano, armenia-servicos e votorantim-5-jeitos, `keyword` é 17 de 53 planos (o mais usado); nos 7 episódios em retrato é 27 de 86 (31%), também o mais usado.
- Springs do kit: ~10 configurações diferentes escritas em linha (3 revisores contaram 9 em 11 usos); entradas de 16 quadros (`KineticHeadline`) e 18 (`useAnimateIn`, `CaptionText`); `useInOut` 14 e 10; `useSpringIn` 40.
- Medida do "pop" de "POST": dois revisores mediram, cada um por conta própria, a largura 0,66 a 0,68 → 0,88 a 0,89 → 1,0 em 3 quadros (0,233 a 0,333 s), sem quique.

**Medido por um só membro e não reproduzido pelos outros (tratar como não confirmado):** "157 de 162 trocas de destaque" e "~92% da referência coberta por legenda"; "0 de 16 quadros com legenda" nos Reels do projeto; os instantes dos itens da lista (6,53; 9,17; 12,93; 17,53; 24,23 s) vêm de uma medição por pixel de um revisor; dois outros revisores só viram os itens a 1 quadro por segundo.

**Erros apontados por 3 ou mais revisores na resposta do haiku (confirmados por mim):** a decisão 7 da ADR 011 é "a tela não calcula" (não "não duplica"); `t25.0-topo-lista-cabeca.png` mostra a lista e a cabeça, sem legenda; os itens da lista não entram "a cada ~2 s"; `shots.py` não calcula `wordFrames` (só existe no kit); uma entrada de 18 quadros não é a da referência (3 quadros).

**Ainda não decidido pelo dono:** o que, na referência, ele quer levar para o kit; se o projeto terá uma segunda identidade visual além do `editorial`.

## 4. O que a referência faz (leitura do coordenador a partir dos quadros)

**Leitura do coordenador (confira nos quadros; se discordar, diga):**
- "POST" entra pequeno e semitransparente em 0,23 s e chega ao tamanho final em cerca de 3 quadros; "EVERYTHING" (menor, abaixo) entra do mesmo jeito em 0,93 s; "5X" aparece já inteiro num quadro só em 2,03 s, mais embaixo. Os três saem juntos no corte de 3,1 s. Texto branco, traço preto grosso, sem painel, sem fundo.
- O título "For every Reel:" (3,97 s) e os itens da lista (1 a 5, em 7 s, 9 s, 12,93 s, cerca de 18 s e cerca de 24 s) aparecem **inteiros num quadro só**, sem transição visível a 30 quadros por segundo, e se acumulam: a lista cresce até o item 5, fica até o corte de 29,1 s e atravessa o corte de 13,47 s. O ritmo parece acompanhar a fala (áudio não conferido).
- Em 25 s o item 5 fica parcialmente coberto pela cabeça do apresentador, e em 1,6 s o topo da cabeça encosta na base de "EVERYTHING": o texto parece estar **atrás** da pessoa.
- Legenda: 2 a 3 palavras por vez, em maiúsculas, brancas com traço preto fino, na altura do peito; a palavra falada fica **amarela** e o amarelo avança palavra a palavra (cada uma de cerca de 0,13 a 0,5 s); o bloco inteiro troca sem transição.
- A câmera tem cortes secos com mudança de enquadramento (3,1 s, 13,47 s, 29,1 s); os textos ficam no lugar durante os cortes de 13,47 s.
- Posição: título e lista no terço superior (o título a cerca de 12% do topo, ou seja, ~240 px num quadro de 1920 px), legenda no centro.

