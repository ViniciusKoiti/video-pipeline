# Estilos visuais × verticais: o que combina e onde dá para atuar

- **Consulta:** 2026-10-07. **Origem:** a lista de 50 estilos colada pelo dono e a pergunta "qual combina com cada produto, para ver em quais verticais atuar".
- **Método:** conselho de modelos (skill `llm-council`): 4 membros (opus, sonnet, fable e haiku) responderam sozinhos, revisaram as respostas anônimas e um presidente (opus) escreveu a resposta final. Todos são Claude, então os erros se correlacionam; o ranking mede preferência entre pares, não correção. **Nenhum vídeo de concorrente foi assistido e nenhum quadro foi renderizado**: é julgamento de design sobre fatos do kit e do projeto, não teste com público.
- **Estado:** análise. Escolha de identidade e implementação são do dono. Nada foi implementado.
- **Anexos** (`docs/pesquisa/estilos-por-vertical-anexos/`): `brief.md`, `estilos.md` (a lista, com o que o kit tem) e `verticais.md` (as 10 verticais, com a fonte de cada fato). Material bruto das respostas e revisões: `/tmp/.../scratchpad/council/estilos-por-vertical/` (temporário).

## 1. Resposta executiva

- **O estilo não é o gargalo.** Fora o documentário de arquivo (que roda no ffmpeg), as 9 verticais ficam bem servidas por **Infographic + Swiss style**, que é o que o preset `editorial` já é [I]. Quais verticais atacar se decide pelo mercado (notas comerciais da pesquisa), não pela estética.
- **Evitar nas verticais de dinheiro, saúde e imigração:** Glitch, Neon sign, Vaporwave, Pop art, Y2K chrome. Soam a golpe ou a promessa de renda, e FTC, SEC e FCA regulam alegações nessas áreas [F].
- **Acentos que valem teste:** Split-flap (prazos, pisos e rodadas; peça nova), `Marker` (tempero, 1 a 2 por vídeo; já no kit) e Neobrutalism para diferenciar a vertical saturada dos autônomos (exige tokens de forma e sombra dura).
- **Segunda identidade (um modo claro):** só após teste, e custa mais do que "trocar nove campos": os véus escuros fixos do template, a sombra preta da legenda, as cores do gráfico e um destaque novo (o dourado dá 1,6 a 1,9:1 sobre claro).
- **Decisão que falta ao dono:** uma identidade ou duas? E se duas, clara ou enérgica (traço grosso, caixa alta, amarelo)?

## 2. Resultado do conselho (resposta do presidente)

### Recomendação

Escolhas por voto [I/H]; o haiku pesa menos (números sem origem [F]).

| Vertical | Top 3 | Evitar 2 | `editorial` basta? |
|---|---|---|---|
| 1 MEI | Infographic, Swiss, Flat 2D | Glitch, Neon sign: golpe, "renda extra" | Sim; claro a testar [H] |
| 2 Placar | Infographic, Swiss, Split-flap | Pop art, Vaporwave: sensacionalizam | Sim |
| 3 Dinheiro e poder | Infographic, Swiss, Line art (`Marker`) | Art Deco, Film noir: glamoriza, criminaliza | Sim, feito para ele [F] |
| 4 Arquivo | Film noir (P&B), Topographic, Infographic ou Line art | Glitch, Cel shading: anacronismo, trivializa mortes | Não se aplica: ffmpeg, kit em clipe `Original` [F] |
| 5 Autônomos EUA | Infographic, Swiss, Neobrutalism | Y2K chrome, Skeuomorphism: hype, imita formulário do IRS | Sim |
| 6 Finanças | Infographic, Swiss, Flat 2D | Glassmorphism, Vaporwave: fintech, ironia | Sim; claro a testar [H] |
| 7 Imigração | Swiss, Split-flap, Infographic | Film noir, Aurora gradient: medo de fronteira, vende sonho | Sim |
| 8 Vendedores | Infographic, Swiss, Blueprint ou Flat 2D | Isometric, Neon sign: barra distorcida, renda fácil (FTC) | Sim |
| 9 Nutrição | Swiss, Infographic, Line art | Y2K chrome, Frutiger Aero: embalagem de suplemento | Dividido; claro a testar [H] |
| 10 IA no trabalho | Infographic, Swiss, Line art ou Bento grid | Sci-fi HUD, Glitch: afastam quem não programa | Sim |

Razão do topo: número com fonte e data pede hierarquia, não decoração [F/I].

**2. Produzível agora.** Fora a 4, todas ficam bem servidas por Infographic e Swiss style, que o `editorial` já é, sem grupo C [I]. Faltam peças [F]: Split-flap; tokens de forma e sombra dura (Neobrutalism); regra de ícone em retrato; o `Marker` no template. Limites de conteúdo e motor [F]: a 10 depende de demonstração de tela; na 8, o "quanto sobra" é derivado, e o `ShareChart` com `rest` o calcula (conferido pelo presidente), contra a ADR 011; na 4, o ffmpeg não tem grão nem filtro de cor, e o mapa do template para em 72°N, sem Antártida (piloto polar). Triagem [I]: no B, só paleta é configuração; Glassmorphism, Frutiger Aero, Neumorphism e Y2K são C no custo; Aurora paga blur 120 e Film noir, `feTurbulence`, a cada quadro [F].

**3. Conjunto mínimo.** O par Infographic + Swiss, que é o `editorial`, cobre nove de dez [I]; o `keyword`, plano mais usado em retrato (27 de 86), já é Kinetic type [F]. Acentos: Split-flap e `Marker` ("tempero, 1 a 2 por vídeo" [F]). Segundo preset, claro para 1, 6 e 9, só após teste [H]; custa mais que "nove campos" [F]: véus em grafite fixo (`Editorial.tsx`), sombra preta da legenda (`Scene.tsx`), cores do `BarChart` e destaque novo (dourado a 1,6–1,9:1 no claro). Nada escolhe o tema hoje [F].

**4. Sem quadro ou público:** legibilidade em 720×1280 após a recompressão, com legenda, fonte e janela; se o claro lê "oficial" e o grafite com dourado, "guru"; se o split-flap atrasa a leitura; se o Notionists combina com cada paleta; retenção por estilo [H].

### Onde o conselho concordou

- Infographic e Swiss no topo (na 4, Film noir e Topographic); `editorial` basta em quase todas [I].
- Evitar hype e golpe (Glitch, Vaporwave, Neon sign, Pop art, Y2K chrome): FTC, SEC e FCA regulam alegações aí [F].
- Trocar de preset não salva estrutura repetida [I].

### Onde divergiu e por quê

1. **Segundo preset.** Fable: necessário (claro para 1 e 5 a 9; grafite não combina com comida [H]); opus: opcional para 1, 6 e 9; sonnet: só após teste, claro ou enérgico (contorno, caixa alta, amarelo: decisão 4 do guia [F]); haiku: nenhum. Sem quadro, é gosto [H]. Minoria a guardar: o "não" da fable na 9. Consequência: o claro é trabalho no template, não configuração [I].
2. **Onde fica a escolha.** Sonnet: campo `theme` opcional no `episode.json`, com ADR curta (como 013 e 014); opus: fora do contrato, como prefere o brief [F]. Decidir antes do código.
3. **Terceiro estilo.** Split-flap pode sugerir vencedor onde a comparação pede ressalva [I]; Neobrutalism diferencia a 5, mas pode soar leve para imposto [H].
4. **Exceções do C** (minoria a guardar). Paper collage via `CutoutPortrait` na 3 (opus): #82 aberto [F], e rostos lado a lado insinuam relação sem ficha [I]. Woodcut por gravura em DP na 4 (fable, sonnet): licença por imagem, e gravura é interpretação, não registro [I].
5. **Rejeitadas** (haiku, sem tratar tom nem distorção): Film noir na 3, Sci-fi HUD na 10, Isometric na 8; não há peça isométrica no kit [F].
6. **YouTube.** Duas respostas leram só "mesmo canal"; o texto também veta o que "parece feito com um template" [F], e isso vale por vídeo [I].

### O que ninguém verificou

A cara real dos concorrentes; o custo de render por estilo (o final 1080×1920 nunca foi medido [F]); a licença de qualquer fonte além da Inter; se o dono quer uma identidade ou várias [F].

### Primeiro passo concreto

O template já serve nove verticais [I]. Perguntar ao dono: uma identidade ou duas e, se duas, clara (1, 6, 9) ou enérgica (decisão 4 do guia)? Se clara: PR com véus, legenda, eixo, destaque e seletor; depois, com autorização, um quadro de `number` e um de `keyword` por preset, no celular.

**Notas do coordenador sobre o texto acima:**
- Na vertical 8, o presidente diz que o `ShareChart` com `rest` calcula o "quanto sobra" "contra a ADR 011". Conferi: o `ShareChart` calcula a fatia do que sobra (`whole - sum`, `ShareChart.tsx` l. 117 a 122) e o template repassa `rest` (`Editorial.tsx` l. 216 e 217). **A própria tabela da ADR 011 lista `rest?` entre os campos do `share`**, e a decisão 7 diz que razão, variação e soma só aparecem se estiverem numa ficha. Se a fatia do que sobra conta como número derivado, é uma interpretação a decidir; não é um conflito confirmado.
- O contraste do dourado no claro: 1,89:1 sobre branco puro (cálculo meu); os revisores acharam de 1,6 a 1,9:1 sobre off-white.
- O "primeiro passo" do presidente supõe um PR de modo claro **antes** da decisão do dono; a ordem correta é a pergunta primeiro.

## 3. Ranking da revisão anônima

Mapa de rótulos (desfeito depois das revisões):

- Resposta A = opus
- Resposta B = fable
- Resposta C = sonnet
- Resposta D = haiku

Rankings dos revisores (do melhor ao pior):

- opus: A (opus) > C (sonnet) > B (fable) > D (haiku)
- sonnet: A (opus) > C (sonnet) > B (fable) > D (haiku)
- fable: C (sonnet) > A (opus) > B (fable) > D (haiku)
- haiku: C (sonnet) > A (opus) > B (fable) > D (haiku)

Posição média (menor é melhor):

- Resposta A (opus): 1.50
- Resposta C (sonnet): 1.50
- Resposta B (fable): 3.00
- Resposta D (haiku): 4.00

Posição média sem o voto do próprio autor:

- Resposta C (sonnet): 1.33 (votos [2, 1, 1])
- Resposta A (opus): 1.67 (votos [1, 2, 2])
- Resposta B (fable): 3.00 (votos [3, 3, 3])
- Resposta D (haiku): 4.00 (votos [4, 4, 4])

Posição que cada revisor deu à própria resposta: opus 1º, sonnet 2º, fable 3º, haiku 4º.

## 4. Conferências do coordenador no repositório

**Conferido por mim [F]:**
- **Aurora:** `SceneBackground` na variante `aurora` desenha círculos com `feGaussianBlur stdDeviation="120"`, recalculados a cada quadro (`motion-kit/src/fx/SceneBackground.tsx`, l. 46 a 51). `FilmGrain` usa `feTurbulence` com semente por quadro. O template usa `SceneBackground` só na variante `dots` (grade de pontos, fundo transparente, intensidade 0,25: `video/src/Scene.tsx` l. 53), **não** a `aurora`; ele não importa `FilmGrain`, `Marker`, `GlitchText` nem `NeonText`.
- **Fonte:** Inter variável carregada com `weight: "100 900"` (`video/src/theme.ts`, l. 62). O arquivo `theme.ts` tem 74 linhas; o objeto de tema, cerca de 10 campos.
- **Ninguém escolhe tema:** nenhuma ocorrência de seletor de tema em `app/render/remotion.py`, `config/providers.toml` ou `video/src/types.ts`; o template fixa o dourado `#F2B134` em `theme.ts`.
- **Modo claro custa mais do que "nove campos":** `Editorial.tsx` l. 114 (painel do número, `rgba(14, 17, 22, 0.86)`) e l. 359 (véu do `keyword`, `rgba(14, 17, 22, 0.55)`); `Scene.tsx` l. 88 (legenda com `textShadow: "0 0 6px #000, 0 0 3px #000"`); o `BarChart` do kit tem `axisColor` e `labelColor` com padrão próprio. Dois revisores contaram ainda o brilho preto de `DateStamp` e `SourceTag`.
- **Contraste do dourado `#F2B134`:** 1,89:1 sobre branco puro e 10,0:1 sobre o grafite `#0E1116` (cálculo WCAG meu); três revisores acharam de 1,6 a 1,9:1 sobre off-white. O texto `#EDEDE8` sobre o grafite dá 16,1:1.
- **Motor do documentário (ffmpeg, `app/render/ffmpeg.py`):** só `scale` e `crop`, `gblur` no fundo (sigma 8) com `eq` de brilho, `zoompan`, `fade` de entrada e saída e `subtitles`. **Não há filtro de grão nem de cor** (preto e branco, vinheta); seriam acréscimos ao motor. Os componentes do kit só entram como clipe `Original` (#42).
- **Mapa do template (`video/src/geo/regions.ts` l. 26):** `WORLD_BOX = {west: -130, south: -56, east: 150, north: 72}`. O mapa não chega ao Ártico alto nem à Antártida: um piloto polar (a expedição Greely, por exemplo) esbarra nisso (nenhum membro notou; um revisor sim).
- **Peças do kit:** `ShareChart` tem `variant 'bar100' | 'donut'`; existe `Pane` (caixa recortada com `radius`); não há nada de split-flap; os ícones Lucide (ISC, ADR 011, decisão 10) servem aos nós da rede e não há regra de ícone em retrato; `Marker` existe e o seu cabeçalho diz "tempero (1 a 2 por vídeo)".
- **Contagem:** `keyword` é o plano mais usado nos 7 episódios em retrato (27 de 86); `number` vem em segundo (19).
- **Preset do template:** `editorial` tem `neon: 0`; o neon como padrão é do tema **padrão do kit**, não do template.
- **Política do YouTube** (`plataformas-monetizacao-2026-10.md`): o texto veta conteúdo "que parece feito com um template" **e** o que "pode parecer repetitivo depois de vários vídeos seguidos do mesmo canal"; duas respostas citaram só a segunda parte.

**Erros apontados por revisores na resposta do haiku (confirmados por mim):** classificou Topographic e Film noir como B e Sci-fi HUD como C (a triagem os põe em A); citou números sem origem ("número de 56 px", "rodapé de 40 px", "grid de 8 px", "margem de 60 px" como se fosse a margem geral); ignorou que o documentário roda no ffmpeg; "FilmGrain desliga" (o template nunca o usou); citou um arquivo `[modelo].md` que não existe no repositório; passou de 800 palavras.

**Pontos que ninguém verificou:** o aspecto real dos concorrentes; a legibilidade de cada preset em 720×1280 depois da recompressão das plataformas; o custo de render por estilo (o render final 1080×1920 nunca foi medido); a licença de qualquer fonte além da Inter; qual público lê "oficial" no claro ou no grafite com dourado.

**Ainda não decidido pelo dono:** uma identidade única ou várias; se haverá uma segunda identidade (decisão aberta nº 4 do guia `docs/guia-animacao-de-texto.md`).

## 5. Os 50 estilos: triagem

Triagem do coordenador (a cobertura do kit está conferida [F]; os grupos são julgamento [I]). O conselho corrigiu: no grupo B só a paleta é configuração; Glassmorphism, Frutiger Aero, Neumorphism e Y2K chrome são B na dependência e C no custo; Aurora (blur de 120 px) e Film noir (`feTurbulence`) pagam a cada quadro; Isometric e Clay 3D não têm peça no kit.

**A. O kit já tem a peça (ou quase) [F para as peças citadas]:** Kinetic type (`KineticHeadline`, `NeonText`), Glitch (`GlitchText`), Neon sign (`NeonText`), Particles (`SceneBackground`, `SparkBurst`), Aurora gradient (`SceneBackground`), Pixel art (`pixel/`), Infographic (gráficos e peças editoriais), Film noir (parcial: `FilmGrain` mais filtro de cor), Line art (parcial: `Marker`), Sci-fi HUD (parcial: `Hud`, `Gauge`, `TerminalWindow`), Tilt-shift (parcial: `Focus` e `ParallaxLayer` já usam `blur`), Topographic (parcial: `GeoMap` tem contornos de países, sem relevo).

**B. Preset de tema e poucas peças novas, sem ativo externo [I]:** Swiss style, Bauhaus, Mid-century, Blueprint, Bento grid, Neobrutalism, Art Deco, Flat 2D, Memphis, Op art, Pop art, Risograph, Split-flap, ASCII art, Synthwave, Vaporwave, Glassmorphism, Neumorphism, Y2K chrome, Frutiger Aero, Isometric, Cross-stitch.

**C. Dependem de ilustração, de textura, de 3D pesado ou de dependência nova [I]:** Clay 3D, Low poly, Cel shading, Paper collage, Origami, Manga, Watercolor, Woodcut, Stained glass, Art Nouveau, Surrealism, Graffiti, Psychedelic, Pencil sketch, Skeuomorphism, Grunge. Pela regra do projeto, **ilustração não é desenhada à mão**: só peças com licença aberta, imagem gerada para lacunas (com escolha humana) ou ilustrador.
