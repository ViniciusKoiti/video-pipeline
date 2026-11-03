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
