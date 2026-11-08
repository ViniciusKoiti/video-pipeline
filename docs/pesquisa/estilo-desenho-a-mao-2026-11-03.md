# Estilo "desenho à mão": análise do traço e componentes para cenas

Data: 2026-11-03. Origem: duas imagens do serviço "Hand-Drawn Animation" (vendedor Kartoonics, Fiverr) que o dono
mandou como referência. Não copiamos personagens, composições nem imagens desse vendedor. Só o princípio de cada
traço entra no nosso kit, desenhado por nós em código. As imagens dele não entram no repositório.

## 1. O que as imagens mostram

| Elemento | O que se vê | Regra que dá para repetir |
|---|---|---|
| Contorno | Preto, grosso, irregular, com cantos arredondados | Um traço de espessura alta no contorno externo; detalhe mais fino |
| Hachura | Sombra e fundo escuro (a entrada da caverna) em traços curtos e direcionais | Sombra por hachura, não por degradê |
| Preenchimento | Chapado, 3 a 4 cores (verde, rosa, ocre, preto), sem degradê; brilho pequeno nos olhos | Paleta curta: uma cor de linha, uma de fundo e poucos acentos |
| Papel | Fundo creme ou ocre com grão; a cena fica dentro de uma moldura chapada de cor (verde) | Grão no fundo e uma moldura de cor como quadro |
| Tipografia | Título em caixa-alta de pincel grosso; etiquetas em caixa arredondada com contorno; selos circulares com ícone | Três níveis: título, etiqueta, selo |
| Personagem | Forma simples (gota, cérebro), olhos com pálpebra, braços e pernas finos como linha, um objeto na mão | Corpo como forma; membros como traço |
| Composição | Um personagem, um objeto e um quadro dentro do quadro (o nariz com vírus); muito espaço vazio | Uma ação por cena, com um quadro-inset para o assunto |
| Movimento (fontes) | O traço "ferve" (redesenhado a cada poucos quadros); o corpo parado enquanto o traço treme | Corpo em pausa, membros se movendo, traço vibrando |

## 2. Fontes

Fontes de vendedores e blogs, não de referência técnica. Usei como indício, não como autoridade.

- **Tremor de traço ("line boil"):** o efeito aparece quando o contorno é redesenhado a cada quadro. Fontes:
  [Squigglevision (Wikipedia)](https://en.wikipedia.org/wiki/Squigglevision),
  [FoxRenderfarm](https://www.foxrenderfarm.com/share/what-is-squigglevision/),
  [TV Tropes: Line Boil](https://TVTropes.org/pmwiki/pmwiki.php/Main/LineBoil),
  [PremiumBeat](https://www.premiumbeat.com/blog/how-to-create-line-boil-animations/),
  [ComfyUI, Line Boil](https://comfy.icu/node/LineBoilImage).
- **Animação limitada e "on twos":** reaproveitar o que não se move e redesenhar só o que se move; poucos quadros
  por segundo. Fontes: [glossário FutureLearn](https://ugc.futurelearn.com/uploads/files/26/1e/261e85c8-3b25-41eb-895e-c76b4ddc4eba/GLOSSARY.pdf),
  [fórum Lost Marble](https://lostmarble.com/forum/viewtopic.php?p=1184).
- **Variedade de traço e paleta:** traço uniforme, orgânico, hachura, tracejado e marcas de giz; uma cor de linha e
  poucos acentos. Fontes: [Golpo](https://video.golpoai.com/guide/popular-explainer-video-styles-golpo),
  [Frameo](https://frameo.ai/en/tools/video-animator).
- **Acabamento:** grão de papel, borda de pincel seco, desalinhamento de sobreposição (overprint). Fonte:
  [Topview](https://www.topview.ai/featured-cases/explainer-hand-drawn).
- **Revelação traço a traço:** o desenho aparece linha por linha antes de ganhar movimento. Fonte:
  [Pexo](https://pexo.ai/explore/hand-drawing-animation).
- **Contraste:** o estilo plano, sem textura, é outra família e não serve a este formato:
  [Atlabs, flat 2D](https://www.atlabs.ai/styles/flat-2d-modern).

**Direito autoral (não é parecer jurídico):** o comentário que encontrei diz que a Lei 9.610/98, art. 8º, I e II,
deixa estilo e técnica fora da proteção, mas protege a obra concreta feita nesse estilo. Fontes:
[Legale](https://legale.com.br/?p=2100857),
[Creative Commons](https://creativecommons.org/2023/03/23/the-complex-world-of-style-copyright-and-generative-ai/),
[UCSAL, estudo sobre imitação de estilo](https://ri.ucsal.br/bitstreams/24c02447-b43e-4a9b-9e02-1d07b1b32c90/download).
**Não conferi o texto da lei**, e as fontes são secundárias e uma com tom de marketing. Para uso comercial de algo
parecido com um personagem específico, vale uma consulta jurídica antes. A regra prática que tiro: copiar o princípio
(traço grosso, chapado, grão) é seguro; copiar o personagem, a composição ou a arte do vendedor não é.

## 3. O que o kit 0.7.1 já cobre

Confirmado nos arquivos do checkout e nos nomes exportados do tarball que o template renderiza.

| Necessidade | Peça existente | Observação |
|---|---|---|
| Traço que se desenha | `DrawPath` (`wobble`, `passes`, `boilEvery`, `dash`) | o estilo `pencil-sketch` já usa esses valores |
| Tremor e "fervura" | `DrawPath`, `StyleTexture` (`boilEvery`) | pronto |
| Hachura na sombra | token `shadow: {kind: 'hatch'}` no `pencil-sketch`; `PatternFill` | pronto |
| Grão de papel | `StyleTexture` (`grain`), `paper.ts` | pronto |
| Sobreposição desalinhada | `Overprint`, `misregister.ts` | pronto |
| Acabamento de pincel seco | `Distress` | conferir se serve |
| Animação em passos ("on twos") | `Stepped` | pronto |
| Selos, fitas, papéis | `Tape`, `PaperPiece`, `Shape` | pronto |
| Etiqueta com linha-guia | `Callout` | pronto |
| Balão de fala | `SpeechCard` | pronto |
| Apagar | `SoftMask` (frente que avança) | falta o componente `Erase` |
| Câmera sobre o papel | `CameraRig`, `CameraPath`, `ParallaxScene` | pronto |
| Números que contam | `Odometer`, `useCountUp` | pronto |

## 4. O que falta

Priorizado por dependência. A coluna "arte" diz se depende de uma decisão sobre personagens.

| Prioridade | Componente | O que faz | Esforço | Arte |
|---|---|---|---|---|
| P1 | `InkLine` | traço com espessura variável (afina nas pontas), estendendo `DrawPath` | pequeno a médio | não |
| P1 | `FrameBand` | moldura chapada de cor, borda irregular, com quadro-inset | pequeno | não |
| P1 | `Badge` | selo circular com contorno que se desenha, ícone e rótulo | pequeno | não |
| P1 | `Erase` | apagamento sobre um elemento, por `SoftMask` | pequeno | não |
| P1 | `FillLevel` | nível que sobe dentro de um contorno (pote, reserva) | médio | não |
| P1 | `Board` | camada que persiste entre planos do mesmo bloco, sem fade | médio | não |
| P2 | `StickLimbs` | braços e pernas como traço, presos a pontos de pose; o corpo fica parado (hold) | médio | sim: precisa de corpo |
| P2 | `Mascot` | corpo e rosto com expressões (pálpebra, sobrancelha, boca) | médio a grande | sim |
| P2 | props | lápis, caderno, lança, caverna | depende da fonte | sim |
| P3 | fonte de título | caixa-alta de pincel, com licença verificada | pequeno | não |

**Achado sobre a fonte:** o estilo `pencil-sketch` aponta para `fonts/patrick-hand/PatrickHand-Regular.ttf`, mas
no template (`video/src/fonts/`) só existe a Inter. Ou seja, hoje o estilo cairia numa fonte de reserva. Antes de usar,
confirmar a licença da fonte escolhida (fontes do Google Fonts costumam ser OFL, mas isso precisa ser conferido).

**Achado sobre o corpo:** as imagens mostram que o personagem é um corpo simples mais membros em traço. Membros em traço
se fazem em código (`StickLimbs`). O corpo, no entanto, é forma e precisa de uma fonte: arte ou forma geométrica
nossa. Isso é a decisão do item 6.1.

## 5. Cenas que esses componentes sustentam

Cada cena tem uma ação (um verbo), não só decoração.

1. **Abertura:** mascote apontando o título, moldura de cor, sublinhado que se desenha. Usa `Mascot`, `FrameBand`,
   `DrawPath`, fonte de título.
2. **Caso com personagem e objeto:** o personagem segura o objeto (lança, caderno) e o membro se move enquanto o
   corpo fica parado. Usa `Mascot`, `StickLimbs`, `Stepped`, `Callout`.
3. **Comparação de dois personagens com valores:** dois corpos lado a lado, renda e gasto em números que contam.
   Usa `Mascot` ×2, `Odometer`, `ValueCompare`, `FillLevel`.
4. **Conceito com quadro dentro do quadro:** o assunto (o nariz com vírus) aparece num inset com moldura, e uma seta
   liga ao personagem. Usa `FrameBand` com inset, `InkLine`, `Callout`.
5. **Chamada:** três selos (`Badge`) com ícone e rótulo, um a um, e a ação final. Usa `Badge`, `Stepped`.

## 6. Decisões do dono

1. **Corpo dos personagens.** A regra atual (memória "sem desenho à mão") diz que personagem vem de peça com licença
   aberta ou de ilustrador. Três caminhos:
   - a. **Forma geométrica nossa, feita em código** (licença Original, ADR 007). Sem arte de terceiros e sem direitos
     a acertar. Pode ficar menos rica que a referência. É o que mais se aproxima do pedido de "não dar direitos".
   - b. **Peça CC0** (Notionists ou outra) com o traço do kit. A regra aceita; o visual fica preso à peça.
   - c. **Ilustrador** com licença por escrito. É o caminho que você já escolheu, com custo e prazo.
   Recomendo testar (a) num quadro de teste antes de decidir. Esse teste não rende vídeo.
2. **Fonte de título.** Qual fonte de pincel, e com que licença.
3. **Base do estilo.** Partir do `pencil-sketch` do kit, ou criar um tema novo ("quadro explicativo") com o traço
   de tinta grossa das imagens.
4. **Originalidade.** O estilo sozinho não torna o vídeo original. A política do YouTube (CLAUDE.md §12) exige roteiro
   próprio e variação de estrutura. Isso vale mais que a arte.

## 7. Riscos

- **Cópia de personagem ou composição do vendedor:** fora. Só o princípio do traço e da paleta.
- **Imagens do vendedor no repositório:** não entram. Esta análise cita o vendedor só pelo link.
- **Custo de CPU:** tremor, hachura e grão são pesados; a máquina é limitada. Antes de qualquer render, sonda de CPU
  (`cpu_probe`, CLAUDE.md §3). Pré-renderizar estados de personagem como imagem, quando possível.
- **Frente:** a decisão de 2026-10-22 é uma frente por vez, e mudança de template ou de kit passa pelo vídeo-régua.
  Os componentes P1 podem ser construídos no template sem tocar o `votorantim-dinheiro`, mas quem decide a ordem é o
  dono.
