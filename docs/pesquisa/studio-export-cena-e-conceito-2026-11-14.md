# Cena e Conceito: leitura das exportações do Studio (2026-11-14)

Fontes: duas exportações do dono, do Modo avançado, aba Conteúdo, período **17/10 a 13/11**:
`data/benchmarks/Conteúdo 2026-10-17_2026-11-14 Cena e Conceito.zip` (views, tempo de exibição, inscritos,
impressões, CTR) e `… (1).zip` (as mesmas colunas e mais a duração média da visualização). O período é o mesmo para
todos os vídeos, mas cada vídeo teve um tempo de exposição diferente: estes números **não** entram como D7 nem como D28
no `metrics.json`. "Calculado aqui" = conta minha sobre os números do arquivo.

**Correção (14/11):** a primeira versão deste documento calculou a duração média como tempo de exibição ÷ views
(64 s no Montaigne) e disse que o 28,4% registrado estava errado. O Studio mostra 3:10 (27%): o 28,4% estava certo, e a
conta errada era a minha. O Studio não divide o tempo de exibição por todas as views (ver item 3).

## Longos

- **Views das impressões** ≈ impressões × CTR (é a definição de CTR do Studio).
- **Views com tempo** = tempo de exibição ÷ duração média: quantas views a média do Studio considera.
- **Views quase sem tempo** = views − views com tempo.

As três são calculadas aqui.

| Vídeo | Publ. | Impressões | CTR | Duração média (Studio) | % do vídeo | Views | Views das impressões | Views com tempo | Views quase sem tempo |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Kira teria voto no Brasil? | 21/10 | 4.202 | 1,12% | 1:04 | 16,9% | 67 | ≈47 | ≈59 | ≈8 |
| Porquê Montaigne não era bonzinho? | 27/10 | 4.079 | 1,62% | 3:10 | 27,0% | 262 | ≈66 | ≈88 | ≈174 |
| A pausa: o guia estoico… | 04/11 | 2.273 | 1,58% | 2:11 | 17,9% | 101 | ≈36 | ≈49 | ≈52 |
| Cansada de carregar tudo?… | 31/10 | 1.229 | 0,90% | 2:16 | 13,3% | 43 | ≈11 | ≈22 | ≈21 |
| Como se parecer mais com o Ayanokoji… | 01/11 | 1.113 | 1,98% | 2:14 | 17,7% | 156 | ≈22 | ≈46 | ≈110 |
| **Como era ser rico na Idade Média?** | 07/11 | 1.079 | **4,17%** | **2:50** | **32,7%** | 158 | ≈45 | ≈58 | ≈100 |
| A manipulação que não precisa de mentira \| Orwell | 29/10 | 998 | 1,30% | 0:54 | 7,7% | 75 | ≈13 | ≈26 | ≈49 |
| O Que Não Está na Sua Mão \| Epicteto… | 23/10 | 635 | 2,20% | 1:45 | 15,2% | 88 | ≈14 | ≈23 | ≈65 |
| Como não explodir quando alguém te provoca… | 05/11 | 365 | 1,64% | 2:08 | 21,3% | 20 | ≈6 | ≈10 | ≈10 |
| E se o Light tivesse ganhado? | 22/10 | 182 | 3,30% | 3:22 | 26,6% | 15 | ≈6 | ≈10 | ≈5 |
| Por que torcemos pelo Light?… | 20/10 | 88 | 4,55% | 2:48 | 21,8% | 8 | ≈4 | ≈8 | 0 |
| "Não dê nem água"… | 03/11 | 76 | 3,95% | 1:46 | 23,0% | 16 | ≈3 | ≈6 | ≈10 |

Os dois de Solo Leveling (10/11 e 12/11) têm 24 e 12 impressões: ficam fora, por serem novos demais.
O canal todo teve 17.386 impressões, CTR de 1,67%, 2.944 views e 12 inscritos no período.

## O que as exportações mostram

1. **Os longos foram mostrados; o que faltou foi o clique.** Oito longos passaram de 600 impressões. Entre os oito com
   500 ou mais, a mediana do CTR é 1,6% (calculado aqui). O YouTube diz que metade dos canais e vídeos fica entre 2% e
   10% e que muitas impressões baixam o CTR naturalmente (OF05 em
   `crescimento-youtube-embalagem-hipoteses-2026-10-23.md`). Isso enfraquece a H1 da análise de 08/11 ("quase nenhum
   vídeo foi mostrado") e fortalece a H4/H6: a embalagem ou o tema não fazem o público frio clicar.
2. **A Idade Média é a exceção nas duas medidas:** 4,17% de CTR sobre 1.079 impressões em seis dias (cerca de 2,6
   vezes a mediana) e 32,7% do vídeo assistido, a maior porcentagem entre os longos com público. Também é o longo com
   mais inscritos (3). É um vídeo só: é indício, não prova.
3. **Boa parte das views quase não tem tempo de exibição.** No Montaigne, ≈174 das 262 views ficam fora da média do
   Studio; no Ayanokoji, ≈110 de 156; na Idade Média, ≈100 de 158. Nos dois Light e no Kira, quase não há essa
   diferença. As views com tempo ficam perto das views vindas das impressões. A origem do tráfego (seção abaixo)
   descarta o link compartilhado (Externa = 7 views) e aponta para a **Navegação** sem clique em miniatura. O
   Montaigne teve 253 das 262 views entre 27 e 30/10 e quase nenhuma depois disso.
4. **Retenção (Studio):** de 7,7% (Orwell) a 32,7% (Idade Média) do vídeo. Os pensadores com pergunta pessoal
   (Montaigne 27%) e a Idade Média ficam no topo; Orwell e Kira, embaixo.
5. **Shorts:** o maior conteúdo do canal é o Short "O que os ricos comiam na Idade Média?" (839 views, 624 no primeiro
   dia). Os três Shorts feitos fora do pipeline ("invejosa" 546, "hábito noturno" 170, "manipuladores" 160) seguem o
   mesmo desenho: um pico de um dia e quase nada depois.

## A Idade Média na régua da própria pauta

- **CTR acima da mediana dos longos:** passa (4,17% contra 1,6%).
- **% assistido ≥ 28,4%:** passa (32,7%).
- **Views acima do D7 do Montaigne:** provavelmente não passa. Foram 158 views em seis dias, contra 259 do Montaigne
  em 26/10–02/11 pelo gráfico diário. Mas ≈174 das views do Montaigne são das quase sem tempo; contando só as views com
  tempo, a comparação fica bem mais próxima (≈58 contra ≈88 no período todo; calculado aqui, sem recorte de sete dias).
- A leitura formal do D7 (07/11–14/11) fica para 16/11.

## Origem do tráfego (canal inteiro, longos e Shorts juntos)

Fonte: `data/benchmarks/Origem do tráfego 2026-10-17_2026-11-14 Cena e Conceito.zip`. Tempo por view e views de
miniatura (impressões × CTR) são calculados aqui.

| Origem | Views | % das views | Tempo por view | Impressões | CTR | Views de miniatura |
|---|---:|---:|---:|---:|---:|---:|
| Feed do Shorts | 1.799 | 61,1% | 11 s | — | — | — |
| Navegação (Início, Inscrições) | 684 | 23,2% | 25 s | 2.835 | 3,07% | ≈87 |
| Vídeos sugeridos | 239 | 8,1% | 119 s | 12.851 | 1,32% | ≈170 |
| Pesquisa do YouTube | 118 | 4,0% | 15 s | 905 | 1,88% | ≈17 |
| Páginas do canal | 33 | 1,1% | 85 s | 748 | 2,01% | ≈15 |
| Outros recursos do YouTube | 32 | 1,1% | 40 s | — | — | — |
| Direto ou desconhecido | 21 | 0,7% | 34 s | — | — | — |
| Externa | 7 | 0,2% | 69 s | — | — | — |
| Playlists | 6 | 0,2% | 431 s | 47 | 6,38% | ≈3 |
| Notificações | 5 | 0,2% | 298 s | — | — | — |

O que se lê:

1. **Os longos vivem de "Vídeos sugeridos":** 74% das impressões do canal (12.851 de 17.386), CTR de 1,32% e o maior
   tempo por view (119 s, 37% do tempo de exibição do canal). O YouTube põe os ensaios ao lado de outros vídeos; quem
   clica assiste, mas poucos clicam. A pergunta de embalagem é: o título e a miniatura ganham o clique **ao lado de
   quais vídeos**?
2. **Navegação sem clique em miniatura:** 684 views, mas só ≈87 de clique em miniatura, com 25 s por view. Antes de
   02/11 o canal não tinha Shorts no ar (Feed do Shorts = 0), e em 29/10 a Navegação deu 128 views, quase todas do
   Montaigne (126 views nesse dia). São as views quase sem tempo do item 3. **Explicação provável:** a descrição da
   ferramenta de Analytics do MCP do vidIQ (lida em 14/11) diz que, desde 27/08/2026, o YouTube conta a view a partir
   do primeiro quadro, o que deixa as views dos longos cerca de 1,7 a 1,9 vez maiores do que antes, e que as *engaged
   views* não mudaram. Isso bate com o Montaigne (262 views; 84 *engaged views* em 01/11; ≈88 views com tempo).
   A frase é do vidIQ, não de uma página oficial do YouTube; a conferir na Ajuda.
3. **Ninguém compartilha e não há base:** Externa 7, Direto 21, Notificações 5. Cada vídeo começa do zero.
4. **Shorts:** 61% das views, 11 s por view, um pico de um dia por Short (02–03/11, 07/11, 10–11/11). O canal ganhou 12
   inscritos no período todo.
5. **Pesquisa quase não traz público** (118 views, 15 s por view): os temas não respondem a buscas.

Consequência para comparar vídeos: a coluna **Views** do Studio infla os longos que tiveram Navegação sem clique.
Para comparar, usar **tempo de exibição, duração média, CTR e views com tempo**.

## O que falta

1. **Ao lado de quais vídeos os ensaios aparecem:** no Modo avançado, aba Origem do tráfego, clicar na linha "Vídeos
   sugeridos" abre a lista dos vídeos que levaram aos nossos. Isso mostra a vizinhança onde a embalagem precisa
   ganhar o clique, e é a entrada mais útil para escolher temas.
2. **Termos de pesquisa:** a linha "Pesquisa do YouTube", do mesmo jeito.
3. As leituras D7/D28 por vídeo (`data/publicacoes/leitura-studio-2026-11-14.md`) continuam valendo para o
   `metrics.json`, mas não são necessárias para esta decisão.
