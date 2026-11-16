# Reconstrução Histórica: duas produções lidas às cegas (V1 e V2)

Data da leitura: 2026-11-08. Leitura cega: não abri `medidas.csv`, `medidas.json` nem `*.info.json`.
Fonte: `data/cache/nicho/Como-era-a-vida/` (`.txt`, `.cortes.txt`, folhas de 32 quadros, folhas densas 00 e 50).
Método: `analise-de-formato` (medição, folha densa, decupagem simplificada).
Extras que fiz: (a) detecção de troca de plano com limiar baixo (ffmpeg, fps=4, scene>0,06, agrupada em 1,5 s), em arquivo temporário; (b) 16 quadros avulsos extraídos do MP4 local nos segundos citados no texto ("quadro @ Ns"). Nada foi baixado.

- V1 = `8sCyRH2cht0`, casa camponesa, 29:03 de fala (1760 s no cabeçalho).
- V2 = `2dqGsuQrxeM`, castelo em 1200, 21:56 de fala (1408 s no cabeçalho).
- Convenção das folhas: "folha Vn, qk" = quadro k de 32, contado da esquerda para a direita e de cima para baixo. O tempo do quadro é aproximado (a amostragem parece uniforme, mas a correspondência com a fala deriva em até ~1 min; hipótese). Onde o tempo importa, usei os quadros avulsos.

## 0. Achado de produção comum aos dois (vale ler primeiro)

| Observação | Evidência | Estatuto |
|---|---|---|
| Os planos são **vídeo gerado** (imagem para vídeo), não foto parada com zoom: pessoas mexem olhos e cabeça dentro de um plano de 4 s | V1 densa_50, 880,0–883,9 s: o homem, a mulher e o menino viram o olhar e a cabeça; V2 densa_50, 704–708 s: gado e figuras avançam, poeira no portão | observado |
| Cadência de **~8 s por plano**, nos dois | detecção própria: mediana do intervalo entre trocas = 8,0 s em V1 e em V2 (média 7,6 s e 7,0 s; 231 e 189 trocas agrupadas); nas folhas densas as trocas caem em 704,0 s e 880,0 s, com o primeiro quadro quase preto | observado (a detecção pega também movimento de câmera, então o número absoluto é incerto) |
| Clipes de 8 s colados numa grade, com fade/queda rápida de luz na emenda | quadros pretos avulsos: V1 @200 s e @560 s; V2 @560, @760, @1380 s; abertura de 704,0 e 880,0 com quadro escuro | observado; "clipes de 8 s de um gerador de vídeo" é hipótese |
| O `cortes/min` do cabeçalho (1,3 e 0,3) **não mede ritmo real**: na prática os dois trocam de plano a cada ~7-8 s | `cortes.txt`: V1 tem 37 linhas, muitas em rajada (ex. 218,233 a 221,233 s); V2 tem 6 | observado |
| Os dois seguem a **mesma fórmula**: abertura em 2ª pessoa sensorial, pergunta-tese, blocos com "contraste", pedido de comentário/like/inscrição e anúncio do próximo vídeo | V1 0:00, 1:38, 28:31, 29:02; V2 0:00, 0:44, 21:27, 21:44 | observado |
| Voz em ritmo uniforme (124-125 pal/min) e marcas de legenda automática (`[música]`, `>> [roncando]`, "Sì.") | V1 26:26; V2 21:42 e 21:56 | observado; "voz sintética" é hipótese (não ouvi o áudio) |

## 1. Roteiro

### 1.1 Gancho dos 60 s

| | V1 (casa camponesa) | V2 (castelo) |
|---|---|---|
| Dispositivo | Cold open sensorial em 2ª pessoa: acorda na palha, fumaça, família e animais no mesmo cômodo (0:00-0:45); "Bem-vindo a uma casa camponesa medieval" (0:48) | Cold open: "É o ano de 1200", frio nas frestas, cheiro de palha úmida, "Você está dentro de um castelo" (0:00-0:33); pergunta explícita (0:37-0:56); "A resposta vai te surpreender" (0:59) |
| Promessa | Corrigir a imagem "limpa" dos filmes (0:51-1:07); pergunta guia "como sobreviviam" só aparece em 1:38-2:04 | Corrigir a imagem de filme (1:00-1:13) + **relógio**: "antes que a guerra chegasse aos portões" (0:54) |
| Tensão | Baixa: a pergunta vira "eles apenas se adaptaram" (2:10-2:17) | Média: promete um evento futuro (a guerra) que organiza o vídeo |
| Demora até o primeiro conteúdo | ~3 min (a lista de paredes começa em 3:17) | ~1:15 ("Vamos começar pelo que você vê", 1:15) |
| Clichês de gancho | "vai descobrir ao longo dos próximos minutos" (2:57), "obra-prima silenciosa de engenharia" (3:07) | "preciso te fazer uma pergunta que vai mudar completamente a forma como você enxerga" (0:42), "vai te surpreender" (0:59) |

Leitura: o gancho do V2 vem com prazo narrativo ("antes da guerra") e vai ao conteúdo em 1:15; o do V1 gasta 3 min em promessas e na pergunta antes de entregar (inferência a partir das datas).

### 1.2 Estrutura em blocos

**V1** (descritivo, por componentes da casa)

| Tempo | Bloco |
|---|---|
| 0:00-0:48 | Cold open |
| 0:48-3:17 | Tese e promessas ("sistema bem pensado", 2:30-2:57) |
| 3:17-10:45 | Paredes (3:17), teto (4:37), fumaça como solução (5:30, "primeiro grande contraste" 5:43), chão (7:16), tamanho e animais (8:00), casa longa (9:37), arqueólogos (9:57) |
| 10:45-11:29 | Recap e anúncio do próximo bloco ("a verdadeira complexidade está apenas começando") |
| 11:29-16:37 | Dia a dia: 20-30 m² e sem privacidade (11:29), livre × servo ("segundo contraste", 12:07), rolos senhoriais (13:05), fogo e potage (13:42), noite (15:15) |
| 16:37-20:15 | Camas elevadas, animais como "barreira térmica" (18:20-19:10), castelo × casa ("contraste", 19:12) |
| 20:15-20:55 | Anúncio do bloco seguinte |
| 20:55-24:44 | Estoques de verão, conservação ("contraste poderoso", 22:01), cálculo de abate (23:00) |
| 23:44-26:30 | Virada de tom: "é preciso ser honesto, sem romantizar" (23:44); mortalidade infantil, fumaça e doença (24:05-25:26) |
| 26:30-29:02 | Fecho moral (inteligência não depende de laboratório, 27:26-28:30), pedido de ação (28:31), anúncio do próximo vídeo (29:02) |

**V2** (narrativo, em três atos)

| Tempo | Ato / bloco |
|---|---|
| 0:00-1:15 | Cold open, pergunta e promessa |
| 1:15-4:40 | Paz 1: salão, paredes, população de 200-500 (2:10), escada em espiral (2:26), cozinha, comida nobre × servo ("primeiro grande contraste", 3:33) |
| 4:40-9:05 | Paz 2: "organismo vivo" (5:03), pátio (5:35), poço (6:08), aviso do cerco (7:21), tribunal do senhor (7:34), crianças (8:38), mortalidade (9:23) |
| **9:05** | **Virada**: "chega aquela manhã diferente", cavaleiro entra a galope, exército a 2 dias |
| 9:05-12:28 | Ato 2a: castelo vira máquina de guerra, camponeses entram (11:38), população dobra |
| 12:28-18:36 | Ato 2b: dia 3 em silêncio, racionamento (14:15), catapulta (15:30), mulheres no comando (16:03), segunda semana (17:23) |
| 18:37-19:47 | Dia 14, bandeira branca, decisão do senhor |
| 19:47-21:27 | Coda: "depende de qual castelo", lição, olhar final nas pedras |
| 21:27-21:56 | Pedido de ação e anúncio do próximo |

### 1.3 Viradas, conflito e retenção

| | V1 | V2 |
|---|---|---|
| Viradas fortes | 1 (a "honestidade" em 23:44) | 3 (9:05 chegada do exército; 15:30 primeira catapulta; 18:37 bandeira branca) |
| Retenção por promessa interna | Âncoras de "contraste" (5:43, 12:12, 19:12, 22:01) e teasers de bloco (10:45, 20:15) a cada ~5-10 min | "ponto que ninguém te conta" (4:42), "cerco" (7:24), "mas ainda estamos em tempo de paz" (7:26) a cada ~2-3 min |
| Conflito | Quase só descrição; a ameaça é abstrata ("inverno", "fome") | Ameaça concreta (exército), escolhas (racionar, abater, negociar), personagens (senhor, senhora) |
| Resolução | Fecho moral genérico | **Não resolve**: "depende de qual castelo da história você está imaginando" (19:47). Honesto, mas é anticlímax depois de 10 min de cerco |
| Palavra-motor repetida | "sobreviver" 19 vezes, "contraste" 5, "inteligên-" 3 | "sobreviver" 8, "surpreend-" 5, "ninguém" 4 |

Hipótese: o V2 usa a estrutura de história (paz, ruptura, pressão, decisão) e o V1 usa a de aula (lista de partes). Em vídeos longos de reconstrução, a segunda estrutura tende a perder atenção na segunda metade, sobretudo porque o V1 repete a mesma tese (o que parece primitivo é inteligente) em 5 blocos.

### 1.4 Fatos, fontes e riscos de erro

| Tema | V1 | V2 |
|---|---|---|
| Cita fonte? | Nunca nomeia: "Estudos de arqueologia experimental" (4:15), "Arqueólogos... Inglaterra, Escandinávia, Alemanha" (9:57), "historiadores... manorial rows" (13:05; é *manorial rolls*, erro de transcrição ou de pronúncia), "registros paroquiais" (21:54), "Estudos sobre expectativa de vida" (24:05) | Nunca nomeia: "Pesquisadores de arquitetura militar" (2:35), "Pesquisadores que estudaram as ruínas" (6:51), "Pesquisadores que estudaram registros de cercos" (16:57) |
| Números | "20 a 30 m²" (11:31), "mais de 90%" (1:20), "quase 1000 anos" (1:04): redondos e sem origem | "200 a 500 pessoas" (2:10, com "estima-se"), "mais de 1 m" de parede (0:40), poço de "mais de 30 m" (6:38), "menos de 500 m" (12:53), "dia 14" (18:37): mais concretos, sem origem |
| Generalização | Uma "casa camponesa" para "Europa rural, ~1200" e "quase 1000 anos" (0:04, 1:04): mistura épocas e regiões | Um "castelo" genérico, e o final admite isso (19:47) |
| Erro factual provável | Camas elevadas e animais "posicionados estrategicamente contra a parede externa" como barreira térmica (17:03-19:02) têm cara de inferência apresentada como fato (hipótese; não verifiquei fonte). "Fumaça como verniz/repelente" (6:35-6:49) é plausível, mas dito sem ressalva | **Século errado três vezes**: "século XI era uma época primitiva" (5:15) e "ao longo do século XI" (19:59-20:02) para o ano 1200 (é século XIII). **Mito dado como confirmado**: escada em espiral no sentido horário para atrapalhar destros, "pesquisadores confirmam" (2:35-2:49); a tese é discutida e não é consenso. Mestres construtores "engenheiros" (6:21) e "banco de dados" (8:28) são anacronismos de linguagem |
| Anacronismo na imagem | Ver 3.3: fogão a lenha moderno, sala de estar moderna, família em roupa atual | Poucos (ver 3.3) |

Risco comum: nenhum dos dois traz fonte na tela nem nomes de obra; a promessa do V1 no título ("REAL", "de Verdade") fica descoberta (ver 3.3).

### 1.5 Fórmulas repetidas e fecho

- V1: "Aqui está o primeiro grande contraste" (5:43), "outro contraste importante" (12:09), "Se você ainda tem dúvidas... considere o seguinte contraste" (19:12), "outro contraste poderoso" (22:01); "Um detalhe raramente mencionado, mas extremamente revelador" (20:04); "outro detalhe fascinante que muitos documentários simplificados deixam passar" (19:20).
- V2: "Não porque quer, porque precisa" (0:04), "não por romantismo, mas por necessidade pura" (1:30), "Não é que os nobres sejam cruéis por design" (4:14), "não por crueldade, mas por uma lógica brutal" (14:57). A forma "não X, mas Y" se repete.
- Fechos: V1 pede comentário (28:34), like (28:43), inscrição (28:53) e anuncia "um dia inteiro de trabalho de um camponês" (29:02). V2 pede comentário com pergunta específica ("Qual parte mais te surpreendeu?", 21:35), like e inscrição, e anuncia "sobreviver a um inverno medieval" (21:48). O V2 tem a pergunta de comentário mais concreta.

## 2. Forma de comunicação

| Aspecto | V1 | V2 |
|---|---|---|
| Pessoa | "Você" 6,0/mil. Entra forte até ~3 min, depois a fala vira 3ª pessoa expositiva ("os camponeses medievais...", 5:45-9:00) e "você" volta como imperativo de câmera ("repare", "observe", "olhe", "toque": 9 ocorrências) | "Você" 13,1/mil. A 2ª pessoa carrega a ação até o fim ("Você está nas ameias", 12:45; "Você olha uma última vez", 20:55) |
| Tom | Didático, explicativo, "aula amigável"; pivô de honestidade em 23:44 | Dramático, de narrador de documentário, com sensorial (cheiro, som, "nos ossos", 15:42) |
| Ritmo | 125 pal/min, frases médias com pausas curtas | 124 pal/min, frases curtas em sequência para criar tensão ("Um exército se aproxima.", 10:30) |
| Vocabulário | Muito "sistema", "engenharia", "eficiência térmica", "sustentabilidade" (15:08), "estratégia": lente moderna sobre a casa medieval | "Organismo vivo", "máquina de guerra", "banco de dados", "manual de liderança moderno": lente moderna também |
| Promessa de surpresa | "mais fascinante do que parece" (2:20), "você vai descobrir" (2:57). Cumpre de forma moderada: a "surpresa" é a fumaça útil (5:43) e a convivência com animais (8:46), que aparecem cedo | "A resposta vai te surpreender" (0:59). Cumpre em parte (poço, escada, mulheres no comando), mas o que mais pesa é o cerco, que o gancho só sugere |
| Empatia/sensorial | Frio nos pés, fumaça, palha (0:08-0:23); depois quase some | Cheiro de gordura animal, som da catapulta, "tosse de 10 pessoas em dois dias" (17:58), crianças sem energia (17:39): sensorial o vídeo todo |
| Soa humano | A pausa honesta "sem romantizar" (23:44) e o "Sim, você não leu errado" (8:46) | O retrato da senhora do castelo (16:47) e "sobreviver muitas vezes não significa vencer" (19:25) |
| Soa gerado | Repetição de "sobreviver", "sistema", "inteligência", três fechamentos de ideia seguidos (26:30-28:30); "tentativa, erro e adaptação" 3 vezes (2:39, 6:12, 15:08) | O padrão "não X, mas Y"; "e aqui está o ponto"; fecho moral longo e abstrato (19:47-21:27) |

## 3. Entrega visual (folhas)

### 3.1 Tipo de imagem

Os dois são **IA realista em vídeo gerado** (humanos, objetos, câmera). Nenhum acervo, desenho ou mapa de fonte histórica na amostra. O V2 tem **um** plano de corte ilustrado do castelo (folha V2, linha 4 coluna 4), único momento diagramático; o V1 não tem diagrama.

### 3.2 Movimento e densidade

- Movimento: câmera lenta (empurrar ou deslizar) mais micromovimento dos personagens (V1 densa_50 880-884 s; V2 densa_50 704-708 s). Não é Ken Burns de imagem fixa.
- Densidade: ~1 plano a cada 7-8 s nos dois (item 0). O plano de abertura é estático por 4 s nos dois (V1 densa_00: telhado escuro quase sem ação; V2 densa_00: castelo na neve com luz quente na porta).
- Abertura × meio: a abertura do V2 já estabelece local e clima (castelo, neve, fogo); a do V1 mostra textura escura sem sujeito (V1 densa_00), e o primeiro quadro de pessoa só aparece depois (V1 q1, homem e mulher deitados na palha, ~0:30; quadro @20 s: pés descalços sob manta, fogo e fumaça, que bate bem com "pés descalços", 0:23). O meio do V1 (880 s) é uma família parada olhando para fora do quadro, quase sem ação; o meio do V2 (704 s) é ação com multidão.
- Faixas pretas em alguns quadros do V2 (folha V2 q3, q4, q17, q18, linha 4 colunas 1 e 2) e possível marca residual de gerador ("K" no canto de V2 q7 e q8; "8K" em V1 q30): hipótese, não ampliei os quadros.

### 3.3 Coerência com a fala

**V1: ambienta, muitas vezes não ilustra, e em alguns pontos contradiz.**

| Onde | O que vi | Relação |
|---|---|---|
| @20 s (0:20) | Pés descalços, manta, palha, fogo, fumaça | Ilustra bem |
| folha V1 q3, q4 (≈2:20-3:20) | Parede de taipa e entrançado de galhos em close | Ilustra ("watle and daub", 3:35) |
| folha V1 q5 (≈4:10) | Telhado de palha com chuva | Ilustra |
| @420 s (7:00), @790 s (13:10) | Casal e criança em cabana de **troncos horizontais** | **Contradiz** o texto sobre barro e palha (3:17-4:12) e fica sem relação com "fumaça verniz" (7:00) e "rolos senhoriais" (13:10) |
| folha V1 q11 (≈10:00) | Cômodo limpo, **janela com vidraça**, mesa, **cadeiras** e potes novos | Anacronismo, contradiz "sem janelas, abertura fechada com tábua" (8:24-8:32) |
| folha V1 q15 (≈13:30) | Pessoas de pele clara e escura em **jeans e camisa vermelha** rindo ao redor do fogo | Anacronismo gritante, risco de erro de prompt |
| folha V1 q18 (≈16:00) | **Fogão a lenha moderno** | Contradiz "lareira baixa de pedras" |
| folha V1 q28 (≈25:00) | **Sala de estar moderna**, sofá, cachorro, crianças com livros | Anacronismo; a fala diz "sobreviver ao inverno" |
| folha V1 q30 (≈27:00) | **Coelho em casinha de madeira** diante de lareira de tijolo moderna | Anacronismo |
| @1130 s (18:50) | Rajada de folhas de outono sobre casa | Ambienta; fala é "animais como barreira térmica", sem relação |
| @1500 s (25:00) | Pergaminho com letra manuscrita e vela | Ambienta; fala é "mortalidade e doenças", sem relação |
| @1700 s (28:20) | Fardos de palha e monte de argila | Ilustra o "barro e palha" do fecho (27:03) |
| folha V1 q17 (≈15:00) | Vaca, porcos e galinhas em palha | Ilustra "animais dentro de casa" (8:46) |

Conclusão: o V1 trata a fala como "tema", não como roteiro de planos. Há cerca de 6 quadros de 32 (≈19%) com anacronismo visível, um problema grave num vídeo que se vende como "REAL" e "de Verdade" no título.

**V2: ilustra com precisão, inclusive em momentos específicos.**

| Onde | O que vi | Relação |
|---|---|---|
| @300 s (5:00) | Planta circular do castelo vista de cima | Ilustra "ver o castelo de cima como um pássaro" (4:50-5:00) |
| 704-708 s (11:44) | Camponeses com sacos e gado entrando pelo portão | Ilustra "camponeses... gado, sacos de grão, crianças no colo" quase no tiro |
| @905 s (15:05) | Capela cheia, crucifixo, velas | Ilustra "As pessoas rezam na capela" (15:09) |
| @1010 s (16:50) | Homem e mulher de cabelo ruivo e vestido verde em corredor com tochas | Ilustra "A senhora do castelo, segundo comando" (16:47) |
| @1100 s (18:20) | Distribuição de comida com guardas | Ilustra |
| folha V2 q3, q4 | Corredor e escada em espiral | Ilustra "escada estreita... espiral" (2:26-2:49) |
| folha V2 q5 | Porco no espeto com fogo | Ilustra "pedaços de carne de porco giram" (3:15) |
| folha V2, linha 4 coluna 4 | Corte ilustrado do castelo com várias salas | Esquema, único plano de "explicação" |
| @1230 s (20:30) | Adega com barris e sacos | Ambienta; fala é a lição final |

### 3.4 Consistência de personagens e marcas de IA

- V1: família recorrente (homem, mulher com lenço, menino, cachorro) em @420 s, @790 s, 880 s e folha V1 q14 (homem junto ao fogo): **boa continuidade**, mas o cenário muda de tipo de parede (tronco × taipa) e há pessoas e salas atuais nos quadros q15, q28 e q30.
- V2: protagonista barbudo aparece em V2 q17 e q27 (retratos) e a mulher ruiva na linha 3 coluna 7 e em @1010 s: **continuidade de personagem clara**, usada para sustentar o "você" (a câmera mostra o rosto "dele" no momento em que o texto diz "você percebe", 12:05). Isso é o ponto visual mais forte do canal.
- Marcas de IA: rosto "derretido" não vi nos quadros que examinei; multidões do V2 (folha V2 q15 e linha 3 coluna 3) têm figuras duplicadas e de cabeça pequena, típico de IA em multidão (observado em baixa resolução; hipótese de defeito). Escala de objetos: a pedra da catapulta é grande demais no quadro de impacto (V2, linha 3 coluna 6), o que combina com a fala exagerada ("tamanho de um homem agachado", 15:45).
- Texto na tela: nenhum nas folhas (sem legenda queimada, sem título de bloco, sem número, sem mapa com rótulo).

## 4. Palpite cego sobre retenção

**V2 reteve melhor. Confiança: ~70%.**

Motivos (inferência, com apoio nas observações acima):

1. Ato de conflito com virada em 9:05 e outras duas viradas fortes (15:30, 18:37), contra um vídeo descritivo com uma única virada (23:44) no V1.
2. "Você" mais que o dobro (13,1 contra 6,0 por mil) e ação ao vivo em 2ª pessoa, que mantém o espectador dentro da cena. O V1 passa meia hora explicando.
3. Imagem coladas à fala em momentos específicos (V2 @300, 704, 905, 1010 s); o V1 usa imagem de ambiente e comete anacronismos.
4. Vídeo mais curto (21:56 contra 29:03), com tese que se repete menos.

O que pode inverter: título mais "pesquisável" (casa camponesa × castelo) e tema mais universal podem render mais views e até mais retenção se o público vier por interesse mais específico. O V2 também sofre um **desencontro entre título e conteúdo**: o título promete "antes da guerra chegar" e o vídeo gasta de 9:05 até ~19:45 (≈47% do tempo) na guerra (hipótese: quem veio pelo "como era a vida" pode abandonar; quem veio pela tensão fica).

**Ponto fraco do pior (V1, pelo palpite):** é uma lista longa de componentes com a mesma ideia repetida em 5 "contrastes" e visuais que ambientam sem acompanhar a fala, com anacronismos que desmentem o "REAL" do título. A queda provável é depois de ~11 min (recap em 10:45) e de novo perto de 20 min, onde o próprio vídeo precisa de teasers de bloco para segurar (hipótese: os teasers em 10:45 e 20:15 sinalizam onde o autor esperava perder gente).

## 5. Para um canal de DESENHO POR CÓDIGO (motion-kit, bonecos de recorte originais, diagramas, sem IA realista)

### 5.1 O que dá para aproveitar

| Do canal | Como virar desenho por código |
|---|---|
| Abertura em 2ª pessoa sensorial, com a pergunta-tese em 40-60 s e o relógio ("antes da guerra") | Mesma estrutura, texto próprio (forma, nunca fato). O relógio narrativo é o que mais segura no V2 |
| Estrutura de **ato**: paz, ruptura, pressão, decisão (V2 9:05, 15:30, 18:37) | Planejar viradas a cada 3-4 min na pauta; um quadro de estado muda a cada virada |
| Plano a cada ~8 s | Compatível com o padrão do projeto (20-35 entradas por 5-7 min, ~10-15 s cada) e dá ritmo sem cortes bruscos |
| Mecânica que o V2 só *narra* e que o desenho mostra melhor: corte do castelo (V2, linha 4 coluna 4), planta circular (V2 @300 s), poço, escada em espiral, ração por pessoa, população que dobra (11:50), calendário do cerco (dia 3, dia 14), fumaça e calor na casa (V1 5:30, 18:20) | São diagramas animados: blocos conectados, setas, contadores, mudança de estado. É a vantagem do código: exatidão e explicação, que a IA realista não dá |
| Personagem recorrente que "é você" (V2 q17, q27) | Boneco de recorte original com poucas poses e expressões, o mesmo rosto no vídeo todo |
| Pedido de comentário com pergunta concreta (V2 21:35) | Copiar a forma (pergunta específica), não a fórmula "curta, comente, inscreva-se" |

### 5.2 O que evitar

1. Lista de componentes sem conflito (V1): 29 min com a mesma tese.
2. Planos de ambiente que não acompanham a fala (V1 @1130, @1500 s): em desenho, todo plano precisa ser o assunto da frase.
3. Anacronismo (fogão a lenha, sala moderna, jeans): com desenho próprio isso some, mas o risco equivalente é o objeto "bonito" fora do período.
4. Fonte nunca nomeada ("pesquisadores", "estudos"): o projeto exige `claims` e fonte no rodapé; o canal modelo não tem nenhuma.
5. Erro de século e mito dado como confirmado (V2 5:15, 19:59, 2:35): checar cada afirmação.
6. Final sem resolução e título que promete uma coisa e entrega outra (V2 19:47 e título).
7. Fórmula idêntica em todo vídeo do canal ("contraste", "não X, mas Y", teaser, CTA): é o padrão que o YPP chama de conteúdo repetitivo (CLAUDE.md §12). Variar corpo e estrutura.
8. Fala sem pausa em 124-125 pal/min (nos dois): em vídeo de desenho, o plano de explicação precisa de silêncio para ler o diagrama.

### 5.3 Barreira de produção (estimativa; não é medida)

| Item | Estimativa |
|---|---|
| Quantos planos em ~12 min (o tamanho do nosso ensaio) | ~90-110 planos a ~7-8 s, ou ~50-70 a ~10-14 s |
| Desenho único por plano | Inviável. Precisa de **peças reutilizáveis**: cenário em camadas (casa em corte, castelo em corte, pátio), 6-10 poses do boneco, ícones (grão, lenha, flecha, pessoa), contador, linha de dias, seta de fluxo |
| Primeiro vídeo | Construir o kit de cenários (~10-15 peças) é o grosso do trabalho; hipótese: dezenas de horas na primeira vez |
| Vídeos seguintes | Reaproveitam as peças; o custo é roteiro com fonte, plano de animação e acerto de âncora |
| Maior risco | O boneco de recorte não carrega "câmera subjetiva" nem multidão como o vídeo gerado; precisa de composição planejada (planta vista de cima, silhuetas, plano de mão) para o "você" funcionar |
| O que o canal modelo tem que o nosso não terá | Volume (um vídeo de 22-29 min com ~190-230 planos de uma só vez), mas à custa de fonte, exatidão e de cuidado com anacronismo |

Recomendação, como hipótese: copiar do V2 a estrutura de ato, o "você" contínuo e a imagem presa à frase, e trocar a imagem realista por diagrama mecânico e boneco recorrente; a decisão de formato e a tese ficam com o dono (ADR 031, partitura antes do roteiro).
