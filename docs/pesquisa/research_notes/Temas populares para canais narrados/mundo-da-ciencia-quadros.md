# Mundo da Ciência: quadros, números e o que falta para fazermos igual (2026-11-02)

Pedido do dono: baixar um vídeo do canal novo de referência, analisar quadro a quadro e mapear o que ainda falta.
Material em `data/cache/nicho/Mundo-da-Ciencia/` (fora do Git), baixado pela skill `analise-de-formato` com os cookies
do dono (autorizados na sessão). Vídeos: "Como Funciona um Laser?" (`wbzXHYyP9dE`, 64,6 mil views, 21 min) e "A
Revolução de Kepler" (`gbkPqIhqeCM`, 1,1 mil views, 27 min). Quadros a cada 10 s (laser) e 20 s (Kepler). A leitura
dos quadros é minha, sobre miniaturas de 480×270.

## Números do canal (vidIQ, 50 vídeos longos de 11/04 a 29/10/2026)

- Criado em 16/03/2026; 11,6 mil inscritos; **nenhum Short**; vídeos de 15 a 31 min.
- Cadência: 2 por semana até julho, 1 por semana desde agosto.
- Views por vídeo: **mediana 5.562**, média 21,7 mil. **42 dos 50 vídeos passam de 1.350** (a nossa meta por vídeo).
- Concentração: os 5 maiores (IA 317 mil, painéis solares 174 mil, microchip 76 mil, laser 65 mil, hidrogênio 63 mil)
  somam 64% das views.

## O formato, visto nos quadros

| | Laser (64,6 mil) | Kepler (1,1 mil) |
|---|---|---|
| Imagem | infográfico técnico em fundo azul-escuro, um por plano, rotulado em português | o mesmo estilo; mais cenas históricas ilustradas (Kepler, Tycho) |
| Tempo por imagem | ~30 a 50 s (a mesma imagem em 3 a 5 quadros seguidos de 10 s) | ~20 a 40 s |
| Movimento | troca por fusão; sem animação interna | idem |
| Cortes secos (`medir.py`) | 0 por minuto | 0 por minuto |
| Narração | impessoal: "você" 0,7 e "eu" 0 por mil palavras; 135 pal./min | "você" 0,3 e "eu" 0; 142 pal./min |
| Apresentador, legenda queimada | nenhum | nenhum |

- **Os infográficos parecem gerados por IA:** há rótulos com palavras quebradas ou trocadas ("PLATA DE STÉO", "READI",
  "AMPLIFIDIR OPTICAL", "INTERNA CADO") e restos em inglês ("displaced center", "Sun"). O vidIQ marca o canal como
  "AI-labeled". É inferência pelo erro de texto, não verificação de origem.
- **Mesmo formato, resultados 60 vezes diferentes:** laser e Kepler têm o mesmo estilo, ritmo e narração. O que muda é o
  assunto (tecnologia do dia a dia × história da astronomia) e, presumivelmente, título e capa. O formato sozinho não
  explica o resultado.
- **Densidade:** um infográfico rico (5 a 15 elementos rotulados), mas **parado** e trocado a cada ~40 s. É o oposto do
  Epifania (muitos elementos em movimento): aqui a densidade está dentro da imagem, não no tempo.

## O que falta para fazermos algo parecido

### Dados que não temos

1. Retenção, CTR, origem de tráfego e se o canal já é monetizado: nada disso é público.
2. Se a narração é voz sintética: não ouvi o áudio. Dá para medir com o earshot, só com pedido do dono.
3. Por que os 5 maiores estouraram (título, capa, busca ou recomendação): falta comparar títulos e capas.

### Lacunas de produção (pipeline)

| # | Lacuna | Situação hoje | Caminho | Peso |
|---|---|---|---|---|
| A | **30 a 50 diagramas por vídeo de 25 min** | teto editorial de 12 imagens geradas por episódio | diagramas em código no motion-kit (`network`, `compare`, `chart`, `map`, `DrawPath`), com rótulos exatos | Alto |
| B | **Plano do tipo "diagrama rotulado"** (peças com nomes e setas) | não existe no schema; `network` cobre só parte | plano novo, com ADR e vídeo-régua | Médio |
| C | **Roteiro de ~25 min** (~3.400 palavras) | molde de ~12 min; fichas para ~7 min no episódio atual | mais fichas por vídeo; fontes abertas de ciência (OpenStax CC-BY, NASA em domínio público) | Médio |
| D | **Cadência semanal de vídeo longo** | cada vídeo passa por 4 gates humanos | gates mais leves num formato sem pessoa viva nem política; decisão do dono | Alto |
| E | **Escolha de tema** | pauta manual | pesquisa de palavras e outliers por vídeo (vidIQ), no padrão "Como funciona X?" | Baixo |
| F | **Texto na imagem com erro** | nosso `vp check` exige fonte em tudo que aparece na tela | diagramas em código evitam o erro; vira diferencial | — |

### Lacunas de decisão (do dono)

1. **Mudar o canal de nicho?** O Cena e Conceito é de ensaio de filosofia. Ciência e tecnologia explicada seria nicho
   novo no mesmo canal (único canal a monetizar) ou pivô.
2. **Risco de conteúdo produzido em massa:** o canal de referência usa imagem gerada e estrutura repetida. A política do
   YouTube mira esse padrão. Nossa defesa seria fonte por afirmação e diagramas próprios e corretos.
3. **Duração:** 20 a 30 min dá mais horas de exibição por view, mas pede o triplo de roteiro e fontes.

## Conta para a meta, com este formato

Com 25 min e a retenção do nosso Montaigne (28%), cada view vale ~7 min de exibição. As 4.000 horas pedem ~34 mil views
no ano, ~650 por vídeo se for um por semana. A mediana do Mundo da Ciência é 5.562. **Mesmo com um terço da mediana
deles, a meta de horas fecha**; o limite real passa a ser a cadência e os 1.000 inscritos.

## Por que os maiores estouraram (capas e temas, 2026-11-02)

**Capa não explica.** Comparadas as capas dos 5 maiores (IA, painéis solares, microchip, laser, hidrogênio) com as dos
5 menores (velocidade da luz, multiverso, GPS, química, Kepler): o mesmo estilo nos dois grupos (render chamativo, fundo
escuro com brilho azul e laranja, duas ou três palavras grandes). Miniaturas baixadas das URLs públicas do YouTube.

**O tema explica.** Os 50 vídeos separados por tipo de tema (classificação minha pelos títulos):

| Tipo de tema | Vídeos | Mediana de views | Acima de 1.350 | Acima de 20 mil |
|---|---|---|---|---|
| Como funciona um objeto ou tecnologia do dia a dia | 9 | 36.937 | 8 de 9 | 6 |
| Elemento químico | 12 | 9.824 | 12 de 12 | 3 |
| Conceito abstrato ou história da ciência | 29 | 2.929 | 22 de 29 | 3 |

- "Como funciona" tem mediana **12,6 vezes** maior que conceito abstrato. O GPS (814 views) é a exceção do grupo.
- O canal fez 29 vídeos de conceito abstrato e só 9 de "como funciona": usa pouco a linha que mais rende.
- Mesmo o pior grupo passa da nossa meta de 1.350 em 22 de 29 vídeos.
- Limite: a classificação é minha; não há dado de busca × recomendação nem de CTR para separar o efeito do título.

**Para nós:** a linha "como funciona" pede fontes técnicas (documentação de fabricante, órgãos técnicos, livros abertos)
e diagramas de mecanismo, que é onde o motion-kit é mais forte (fluxo, esteira, rede, comparação).

## Voz e mixagem, medidas com o earshot (2026-11-02)

Trechos de 40 s, mono, 48 kHz; sonda de CPU 0,154 s. Comparação com a nossa voz clonada (Short do CompletableFuture,
pt) e com o Epifania (narrador presumido humano, não conferido). Os vídeos de referência vieram da cópia de 360p do
YouTube, então banda e ruído deles têm a perda da compressão.

| Trecho | AudioSet "Speech synthesizer" | Música | LUFS integrado | Pico real | Piso de ruído | Banda |
|---|---|---|---|---|---|---|
| Mundo da Ciência, laser | 0,86 | 0,70 | −20,5 | −5,0 dBTP | −57,9 dBFS | 16,3 kHz |
| Mundo da Ciência, Kepler | 0,89 | 0,42 | −20,6 | −4,1 dBTP | −60,2 dBFS | 16,3 kHz |
| Nossa voz clonada (Short pt) | 0,81 | — | −14,5 | −1,4 dBTP | −68,8 dBFS | 12,9 kHz |
| Epifania (controle) | não aparece | 0,58 | −15,0 | −0,2 dBTP | −34,3 dBFS | 20,5 kHz |

- **Voz:** o classificador marca "speech synthesizer" no Mundo da Ciência (0,86–0,89) no mesmo nível da nossa voz
  clonada e não marca no Epifania. É indício de voz sintética, não prova (a classe de síntese do AudioSet é evidência
  fraca, e o `realness` do earshot não separa voz neural de humana). Somado aos infográficos com texto quebrado e ao
  rótulo de IA do vidIQ, a produção parece toda automatizada.
- **Volume:** o Mundo da Ciência está em −20,5 LUFS, uns 6 dB abaixo da referência de −14 do YouTube, que não aumenta
  o volume de quem está baixo. Mesmo assim tem mediana de 5,5 mil views: volume não é o que segura o canal.
- **Trilha:** há música de fundo nos dois vídeos deles; nos nossos Shorts, não.
- **Nossa voz:** banda até 12,9 kHz, contra 20,5 kHz no Epifania, mesmo medindo o nosso MP4 local sem perda do YouTube.
  Provável limite da taxa de saída do Chatterbox (não conferido). Pode deixar a voz menos "aberta" em fone; vale uma
  escuta comparada antes de decidir.
- **Leitura:** se a voz deles é sintética e o volume é baixo, o que carrega as views é o tema ("como funciona"),
  não a qualidade da voz.
