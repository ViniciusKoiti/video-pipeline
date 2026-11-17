# Brainstorm "Como era a vida": temas e forma visual (2026-11-08)

Status: **brainstorm, sem decisão do dono, sem pauta, sem fonte, sem render.** Só leitura dos arquivos do repositório; nenhum serviço externo foi chamado.
Única fonte de números: `docs/pesquisa/vidiq-como-era-a-vida-2026-11-08.md` (citado como "§N" = seção desse arquivo). O que não está lá é **hipótese**.
Os temas abaixo são **temas, não afirmações**: nenhum fato histórico aqui está confirmado, e o recorte de cada um se fixa nas fichas ou no cuidado do roteirista.
Contexto lido: `ranking-hierarquia-vidiq-2026-11-05.md`, ADR 055 e skill `roteiro-ficcao-historica`, o piloto `idade-media-ser-rico` (pauta, plano de imagens, decisões, publicação), `estilo-desenho-a-mao`, `traco-desenho-series`, `componentes-infografico`, `video/src/types.ts` e o checkout `~/projetos/motion-kit` (o MCP do kit estava fora do ar; li `COMPONENTS.md`, `CHANGELOG.md` e `host/CAST_SCENE.md`).

## 0. Duas coisas que o piloto já ensinou (mudam a recomendação visual)

1. **O piloto foi 100% imagem de IA parada.** `idade-media-ser-rico`: 53 cenas, 81 planos `photo` (76 imagens, todas geradas pelo dono no chat) mais 13 `keyword`, só com `push_in`/panorâmica. O kit não animou nada além do movimento de câmera. Custo real: 78 arquivos entregues, 10 reprovados e refeitos no FLUX.2 Klein, conferência por 4 agentes, 76 aprovações no gate 3, o estilo do Klein "parecido, mas não idêntico", render final de 30 min (a prévia levou 2.501 s com a máquina ocupada).
2. **Quem decide o modo visual é também quem decide o roteirista.** A skill `roteiro-ficcao-historica` (ADR 055) dispensa fichas, mas **proíbe `number` e `chart`** e só aceita `keyword`/`quote` com texto dito: a tela só carrega *ilustração*. Já tudo o que o motion-kit desenha como **mecanismo** (diagrama, mapa com rota, linha do tempo, escada, comparação) é *afirmação na tela* e pede `claims` (CLAUDE.md §2.2, ADR 008), ou seja, o roteirista explicativo, com fichas e `vp check`. Logo:
   - **IA-led encaixa na "ficção histórica declarada"** (sem fichas, 2ª pessoa, reconstrução dita no começo).
   - **motion-kit-led encaixa no explicativo com fichas**, que é o diferencial do canal ("fontes verificáveis", §1 do CLAUDE.md) e o que os canais do arquivo não mostram.
   - **Híbrida** exige fichas só nas cenas em que o kit afirma algo; o resto é ilustração. O `vp check` valida só as claims que existirem.

## 1. Leitura da evidência em 10 linhas

1. O termo-guarda-chuva "como era a vida" tem 58,5 mil buscas/mês (89% BR) mas **−54,9%** (§1): não é onde entrar. A demanda está em **cabeças longas com lugar + ano**.
2. As maiores: Idade Média 13,4 mil (comp. 38) e 9,3 mil; Polônia 1985 12,2 mil (comp. **15**); ditadura 9,5 mil (+84%); Brasil 1995 8,4 mil (comp. **8**); pré-história 6,8 mil (+89%); Brasil colonial 5,8 mil; Brasil 1800, 1975 e 1900 em ~5 mil (§1). "Viver no Brasil" +92%.
3. O mercado paga por **casa, noite, comida, frio, sobrevivência + época reconhecível** (§2): castelo medieval 781 mil, casa vitoriana (1880) 434 mil com **236x** de breakout, choças que "não congelavam" 186 mil/115x, fazenda colonial 468 mil e casa colonial 364 mil.
4. Gancho recorrente: "Por que você não sobreviveria…", "Como era realmente…", "A verdade por trás…" (§2). Duração dos grandes: 17–31 min, quase diário; mas o maior breakout do arquivo (736x, 233 mil) tem 9:18, e o nosso piloto tem 8:40. **Duração não parece ser o fator** (hipótese).
5. "Pessoa famosa dentro do lugar" vende (Júlio César 545 mil, Santos Dumont 403 mil), mas **fica fora das nossas regras** (pessoa real não é personagem, skill do formato).
6. **Mau sinal 1:** "Brasil por ano" não é uniforme: 4 hits (1964 749 mil, 1975 350 mil, 1990 242 mil, Rio anos 70 75 mil) e o resto em 3–8 mil; anos sem memória coletiva (1951, 1955, 1969, 1972) não puxam (§2).
7. **Mau sinal 2:** quase todo canal pequeno tem 1–2 explosões e o resto em centenas ou poucos milhares (§2, "não replica"); há viés de sobrevivência. Vários hits pequenos são marcados IA.
8. **Espaço para o canal (o que o arquivo não mostra):** nenhum canal do arquivo usa desenho (os grandes põem "Reconstrução por/com IA" no título e usam imagem realista, §5); nenhuma escada de degraus da Idade Média em pt (nota de 05/11); "Como era ser X" (POV de uma pessoa) é raro e disperso (§3); Polônia 1985/1995 tem 5–12 mil buscas e **nenhum canal medido** (a causa da busca é desconhecida: pode ser um vídeo ou série que a puxou); acervo real em domínio público (recorte 1880–1930 do projeto) em vez de IA realista; **mecanismo explicado** em vez de panorama de cenas.
9. Nosso ponto de partida: 9 inscritos, 1.790 views, 22 vídeos; `Como era ser rico na Idade Média?` com 33 views no primeiro dia e 3,3x (§4); ensaios anteriores com 66–260 views e 24–27% assistido. **Nenhuma leitura de 7/28 dias registrada ainda**: uma amostra de um vídeo não prova nada.
10. O maior bolsão do "assim era a vida" é Bíblia/Jesus (140–750 mil; 2,2 milhões em espanhol, §2), mas é fora da marca, de fonte frágil e sensível. Escravidão e ditadura têm demanda e risco juntos.

## 2. Ideias (V01–V25)

Duas tabelas ligadas pelo id: **A** (o que e por que) e **B** (como produzir e quanto vale). Títulos ≤ 65 caracteres, sem promessa que o vídeo não cumpra.

**Chave de B.** Forma: **kit** (motion-kit leva o vídeo), **IA** (imagens geradas em desenho levam o vídeo), **híbrida** (o kit leva o mecanismo e o quadro persistente; a IA ou o acervo dão 8–12 cenas habitadas, o que cabe no teto editorial de 12 imagens do §8). Custo: **P** = poucas imagens e pouco código novo; **M** = 12–40 imagens ou uma peça nova do kit; **G** = 40+ imagens a gerar e conferir, vários componentes novos ou mais de 20 min de voz. Prioridade 1–5 pelo critério: **5** = demanda direta no arquivo + competição ≤ 31 ou hit comprovado + espaço livre + risco gerenciável; **4** = um desses fatores fraco; **3** = evidência parcial ou risco alto gerenciável; **2** = hipótese, fora da marca ou risco alto; **1** = não recomendo agora.

### Tabela A: temas e evidência

| id | Título provisório | Recorte (lugar, ano, o "você") | Evidência (arquivo de 08/11) | Quem já fez (pelo arquivo) |
|---|---|---|---|---|
| **Idade Média** | | | | |
| V01 | Como era passar o inverno numa casa de camponês medieval? | aldeia inglesa, séc. XIV (mesmo mundo do "ser rico"); você = membro de uma família camponesa | choças que não congelavam 186 mil/115x (§2); "como era viver na idade média" 9,3 mil, comp. 41; "idade média" ~28 mil +197% (§1) | Reconstrução Histórica (70,2 mil insc.) |
| V02 | Como era ser pobre na Idade Média? | mesma Inglaterra do séc. XIV; você = camponês dependente | formato POV raro, "ser rico" 543 mil (The Basic Ages, §3); o nosso "ser rico" 33 views no 1º dia (§4). Demanda do termo "pobre": **sem evidência: hipótese** | nada medido com esse título |
| V03 | Sua vida em cada degrau da Idade Média: do servo ao rei | Inglaterra, séc. XIV; você = nasce em cada degrau | formato por classe: Lobianco 161 mil/51x (§3); "your life as every rank in a medieval kingdom" 70 mil (§3); "como era viver na idade média" 9,3 mil | em pt, nada medido no arquivo (a nota de 05/11 diz que nenhum percorria os degraus); em inglês, o caso de 70 mil |
| V04 | O que se comia na Idade Média, de cima a baixo da mesa | Inglaterra, séc. XIV; você = convidado que muda de mesa | "comida medieval" ~13,5 mil (§1); taverna medieval 552 mil/18x; banquete de Elizabeth I 497 mil/11x (§2) | Reconstrução Histórica |
| V05 | Uma noite na Idade Média, devagar (para dormir) | aldeia medieval, uma noite; você = quem escuta | formato "dormir" de 2–3,5 h: 1,2–47 mil views, 1,6–6x (§2); em espanhol 1,2 milhão (Edad Media, 2h30) | Histórias para Adormecer, Relatos para Dormir, Durma em Contos |
| V06 | Como era ser mulher na Idade Média? Três vidas, três degraus | Inglaterra, séc. XIV; três mulheres; você = cada uma | **sem evidência: hipótese.** O melhor "ser X" medido é "ser gay na Idade Média" 36 mil/8,6x, engajamento 15,4% (§3), outro recorte | nada medido |
| **Brasil colonial e Império** | | | | |
| V07 | Como era um dia numa fazenda do Brasil colonial? | Brasil, c. 1800, região a fixar; você = hóspede que passa um dia (observador) | fazenda 1800 468 mil/42x; casa 1700 364 mil/52x (§2); "brasil colonial" 5,8 mil, "brasil em 1800" 5,3 mil, comp. 31–37 (§1) | Reconstrução Histórica; Reconstrução do Passado (charqueada 90 mil/38x) |
| V08 | Como era ser pobre e livre no Brasil colonial? | Brasil colonial, região a fixar; você = trabalhador livre | "como era a vida de um trabalhador no brasil colonial" 5,3 mil, comp. 31 (§1) | nada medido |
| V09 | Como funcionava um engenho de açúcar por dentro? | engenho do Brasil colonial; você = quem segue o caminho da cana | escravo em engenho 13,8 mil/17x (§2); "como era a vida dos escravos" 10,5 mil, **comp. 50** (§1); engenho citado como padrão de tema (§2) | Os Segredos da História (6,3 mil insc., IA, 24:51) |
| V10 | Sua vida em cada degrau do Brasil colonial | Brasil colonial; você = nasce em cada degrau | formato por classe (§3) + Brasil colonial 5,8 mil. Combinação: **sem evidência: hipótese** | nada medido |
| V11 | Rio de Janeiro em 1850: um dia na cidade do Império | Rio, 1850; você = morador de rua comum | "viver no rio de janeiro em 1850" 5,2 mil, comp. 26 (§1); Rio anos 70 75 mil/130x (§2) | História Clássica (15,1 mil insc.) faz Rio por ano |
| V12 | A viagem de navio dos imigrantes para o Brasil, em 1875 | Itália → Brasil, 1875; você = passageiro | imigrantes italianos 1875 283 mil/26x; caravela 1500 332 mil (§2); nota: Brasil vende menos que Europa antiga | Reconstrução do Passado |
| **Brasil por década** | | | | |
| V13 | Como era viver no Brasil antes da luz elétrica? | Brasil, fim do séc. XIX, recorte a fixar; cidade e roça | "antes da eletricidade brasil" 4,9 mil, comp. 34; "como era a vida antigamente" 5,2 mil (§1); tema "antes do papel higiênico" 47 mil/3,1x (§2) | nada medido com esse tema |
| V14 | Brasil em 1900: a cidade e o campo no mesmo ano | Brasil, 1900; dois "você" | "brasil em 1900" 5,1 mil, comp. 30 (§1). Mas ano sem memória coletiva rende 3–8 mil (§2) | História Clássica faz Brasil por ano (1900 não medido) |
| V15 | Como era viver no Brasil em 1975? | Brasil, 1975, cidade grande; você = família de classe média | 5,3 mil, comp. 27 (§1); Brasil 1975 350 mil/46x (§2) | História Clássica |
| V16 | O dia a dia sob a ditadura militar no Brasil | Brasil, 1964–1985; cotidiano e censura, não "a política" | 9,5 mil +84%, comp. 49; 5,0 mil comp. 18 (1964–1985) (§1); Brasil 1964 749 mil/176x (§2) | História Clássica |
| V17 | Como era viver no Brasil em 1995? | Brasil, 1995; você = adolescente de cidade média | 8,4 mil, **comp. 8** (§1); Brasil 1990 242 mil/19,7x; Brasil em 2000 214 mil/2,7x (§2) | História Clássica; Memória Desbloqueada |
| **Antiguidade** | | | | |
| V18 | Como era a vida na pré-história: o que se sabe e o que não | caçadores-coletores, recorte a fixar; você = quem pergunta | 6,8 mil, +89%, comp. 31 (§1); Short "homens das cavernas" 5,4 milhões em 42 s (§2, outro jogo) | nada medido em formato longo |
| V19 | Um dia em Pompeia, hora a hora | Pompeia, manhã do dia da erupção; você = morador | Pompeia 591 mil (§2); terremoto de Lisboa 230 mil/116x (§2) | Reconstrução do Passado (68,9 mil insc.) |
| V20 | Como era a casa de uma família judaica da Galileia no séc. I? | Galileia, séc. I; você = criança da casa | casas judaicas no tempo de Jesus 634 mil/62x; Maria cozinhava 747 mil/63x; "vida de maria" 5,2 mil comp. 38 (§1–2) | Reconstrução Histórica |
| **Cortina de ferro** | | | | |
| V21 | Como era viver na Polônia em 1985? | uma cidade polonesa, 1985; você = família de trabalhadores | 12,2 mil, **comp. 15** (§1). Causa da busca desconhecida | **nenhum canal medido** |
| V22 | Polônia, 1985 e 1995: a mesma rua, dez anos depois | mesma rua nos dois anos | 1995: 5,2 mil, comp. 31; 1985: 12,2 mil (§1) | nenhum canal medido |
| **Acervo real 1880–1930** | | | | |
| V23 | Como era a vida dos americanos em 1906? | uma cidade americana, 1906; você = família comum | "americanos no ano 1906" 5,1 mil, comp. 25 (§1); acervo DP até 1930 (regra do §8) | nada medido |
| V24 | Por dentro de uma casa inglesa em 1880: quem serve a quem | casa de família abastada, Inglaterra, 1880; você = quem entra pela porta de serviço | casa vitoriana 1880: **434 mil, 236x** (maior breakout de canal estabelecido no arquivo, §2) | Reconstrução Histórica |
| V25 | Como era uma cidade do interior antes da fábrica chegar? | cidade brasileira, anos 1950, genérica; você = morador | Ipatinga 1950 271 mil/14x; Tietê 76 mil; Goiânia 1960 53 mil/80x; Manaus 22 mil/17x (§2); 1951/1955 em 3–8 mil | Brasil Esquecido, Terravista, Brasil para Viver e outros |

### Tabela B: forma visual, custo, risco, prioridade

| id | Forma e o que seria mostrado | Custo | Riscos | Prio (critério) |
|---|---|---|---|---|
| V01 | **kit.** Corte lateral da casa, persistente, com setas de calor entrando e saindo (`DrawPath`/`InkStroke`); a cada bloco um estado muda (fecha a porta, acende o fogo, entra um animal). Avatar em recorte dentro. IA só para 4–6 paisagens de neve | M | factual (isolamento, combustível: fichas); baixo de direitos; saturação: 1 canal grande | **5** (hit comprovado 115x, comp. razoável, espaço: ninguém explica o *mecanismo*, risco baixo) |
| V02 | **IA.** Continua o piloto: mesmo avatar e estilo, 1 imagem por cena. Nada a animar além da câmera | G | factual (sem fichas); "pobre" generaliza; repete o título do piloto | 3 (sem evidência do termo; bom teste de modo IA) |
| V03 | **híbrida.** A escada (grafo em camadas) persiste no canto; em cada degrau a mesma ficha de 5 perguntas (casa, comida, trabalho, medo, o que se podia possuir) se preenche; setas "o que se devia ao degrau de cima". Avatar troca de roupa. 6–8 imagens IA, uma por degrau | M | estereótipo; fichas por degrau; o 1º degrau (rico) já saiu: reaproveitar sem repetir; política de conteúdo repetitivo se virar série idêntica | **5** (formato com hit 51x, espaço livre em pt, continua o piloto; esperar a leitura de 14/11) |
| V04 | **híbrida.** Mesa vista de cima como quadro: pratos entram e saem por degrau (kit); regras de jejum como calendário (`YearTimeline`). IA: 8 cenas de cozinha e salão | M | factual alto (preço, jejum, açúcar: o erro do "grama" na análise do modelo); saturação (2 canais) | 4 (demanda comprovada, mas concorrência direta e fichas pesadas) |
| V05 | **IA.** Imagens lentas, quase paradas, 2 h+ de voz; sem mecanismo | G | fora de 8–20 min; custo de voz e render; formato incerto | 2 (hipótese de formato, não de tema) |
| V06 | **IA.** Três retratos de cena e três rotinas; kit quase nada | M | generalização ("todas as mulheres"), sensível, fichas necessárias | 2 (hipótese + risco) |
| V07 | **IA** (com o kit só na abertura): planta do terreiro vista de cima (blocos: casa-grande, capela, senzala, engenho) que se preenche e serve de índice; depois 30–45 cenas em desenho. Multidão e arquitetura são o que o kit não faz | G | **sensível (escravidão)**: sem espetáculo de castigo, sem "você" no papel de escravizado; região e data a fixar; teto de 12 imagens do §8 estourado (precedente: 76 no piloto) | 4 (hit 52x, Brasil colonial é o cluster brasileiro mais evidenciado; risco e custo altos) |
| V08 | **híbrida.** Diagrama de quem depende de quem (rede com setas); 8–10 cenas IA | M | factual (classes sociais do período: fichas); sensível; sem evidência de canal | 3 (demanda parcial) |
| V09 | **kit.** Fluxo do açúcar (etapas e ordem a confirmar nas fichas) como diagrama que acende etapa a etapa, com o trabalho de cada pessoa em cada etapa; IA só no início e no fim | M | **escravidão** como processo: tratar pessoas como pessoas; factual alto; competição 50 na busca de "escravos"; monetização: hipótese | 3 (risco alto gerenciável) |
| V10 | **híbrida.** Escada em camadas como V03, com o último degrau no chão | M | **tom de "nível" inadequado para escravidão**; se feito, sem gamificar; ver §5 | 2 (hipótese + sensibilidade) |
| V11 | **IA.** O kit não tem mapa urbano (só `world` e `america-do-sul` em `geo/`); ruas, sobrados e rua cheia exigem imagem. Mapa do Brasil só de abertura | G | factual (preço, lei); concorrente por ano; pessoa real (Machado) fora | 3 (demanda 5,2 mil, mas custo G e sem mecanismo) |
| V12 | **híbrida.** `GeoMap` mundial com rota Itália → Brasil, um ponto que anda e dias que contam (`map` com `routes`, já no template); diário de bordo como `timeline`; 8–10 cenas IA de convés, porão e desembarque | M | factual (rota, duração, doença: fichas); sensível (mortes a bordo); demanda menor que "Europa antiga" | 4 (hit 26x, mecanismo repetido barato) |
| V13 | **kit.** O arco do dia (relógio de 24 h) como quadro: o sol anda, a luz vira barras que acendem e apagam; cada fonte de luz é um estado; `compare` antes/depois e `YearTimeline` para a chegada da rede; 4–6 interiores à luz de vela em IA | M | factual (fontes de luz, datas, onde chegou primeiro: fichas); recorte difícil (Brasil é grande); baixo de direitos | **4** (comp. 34, demanda direta, mecanismo claro, **sem canal medido**; recorte por fixar) |
| V14 | **híbrida.** Duas colunas (`compare`) cidade × campo, fotos de acervo DP se existirem (a verificar) e desenho | M | ano sem memória coletiva rende pouco (§2); acervo a conferir caso a caso | 3 (demanda existe, o padrão de anos é mau sinal) |
| V15 | **IA** com `YearTimeline` curta. Acervo DP de 1975 improvável (hipótese; conferir): tudo em desenho | G | **política/ditadura**; marcas, músicas e pessoas reais; fichas; já feito por canal pequeno com 350 mil | 3 |
| V16 | **kit.** "O que cabe na tela": um quadro de itens do cotidiano que vão sendo apagados (`Erase`) e restituídos, sem imagem de tortura; trechos de documento em `SourcePage`/`DocumentPage` | M | **alto**: política, pessoas vivas, vítimas, números; só com fichas e verificador; monetização: hipótese | 4 (+84%, comp. 18, ponte com os ensaios de poder/Orwell do canal; risco exige cuidado) |
| V17 | **IA** em desenho, com linha do tempo do ano; sem acervo (improvável ser DP; conferir) | G | marcas, logos, música e pessoas reais (rights); nostalgia pede a coisa real, que não podemos usar | 3 (comp. 8 é o melhor número do arquivo, mas o direito atrapalha e foge da marca) |
| V18 | **híbrida.** O quadro "o que sabemos × o que não" (`compare` com texto), linha do tempo e mapa; 8 cenas em desenho | M | **incerteza científica alta**, mito do "homem das cavernas"; fichas essenciais | 3 (+89%, sem canal em formato longo, risco factual) |
| V19 | **híbrida.** Relógio do dia como quadro e linha do tempo hora a hora (`YearTimeline`); 10 cenas de rua e casa em IA | M | mortes e luto; saturado (591 mil num canal); datas e horas: fichas | 3 (hit grande, concorrente direto) |
| V20 | **híbrida.** Planta baixa da casa que se desenha (`InkScenery`, `Shape`) e se mobilia por bloco; IA para o interior habitado | M | **sensível (religião)**; fontes frágeis; fora da marca; público diferente | 2 (maior bolsão, menor encaixe) |
| V21 | **híbrida.** Mapa da Europa com a Polônia acesa (`GeoMap`); a **prateleira/fila** como mecanismo: um quadro de prateleiras que esvazia e uma fila de silhuetas que anda (kit); 8–10 cenas IA de apartamento, fila e rua | M | **política/regime**: fichas e verificador; sem acervo DP (1985); a busca pode vir de um vídeo ou série que não conheço | **5** (comp. 15, 12,2 mil, **nenhum canal medido**, mecanismo; risco gerenciável com fichas) |
| V22 | **kit.** A mesma rua em dois anos (`compare` antes/depois, `before_after`), objetos que entram e saem; poucas IA | P | depende de V21 (reaproveita o mundo); factual | 3 (1995: comp. 31, volume menor; melhor como sequência de V21) |
| V23 | **híbrida com acervo.** Fotos reais em DP (publicadas até 1930, §8) como `historical_exact` com crédito, câmera entrando nelas (`ArchivalPhoto`, `CameraRig`); `timeline` do dia; desenho só para lacunas | M | cada foto precisa de licença registrada; pessoas reconhecíveis; não é "ficção" (é registro: fichas) | 4 (comp. 25, alinha com o recorte 1880–1930 do projeto, não precisa de divulgação de imagem sintética) |
| V24 | **híbrida, kit na frente.** Corte da casa por andares como quadro persistente; as rotas dos criados se acendem como setas; o "sino" muda o estado do quadro. Fotos DP de 1880 como inset (`SourcePage`) e 8–10 interiores em IA | M | factual (funções, horários: fichas); estereótipo de classe; evitar referência a série de TV | **5** (236x, espaço livre para um *mecanismo*, acervo DP possível, risco baixo/médio) |
| V25 | **IA.** Ruas e fábrica em desenho; antes/depois com `compare` | G | factual local (cidade real exige fichas locais); a série por ano rende pouco; sem evidência de que transfere | 2 |

### Encaixe com a marca (cluster × canal)

O canal hoje é de ensaios de filosofia, 9 inscritos, e todo o vídeo "Como era ser rico" já saiu nele.

| Cluster | Combina? | Ponte possível | Lista/canal |
|---|---|---|---|
| Acervo 1880–1930 (V23, V24) | **Alta**: é o recorte original do projeto (CLAUDE.md §1) | fontes, fotos DP, "quem serve a quem" é poder | mesmo canal |
| Cortina de ferro, ditadura (V16, V21, V22) | **Média**: ensaio de poder e autoridade (Orwell, "Não dê nem água") | "como o poder entra no cotidiano" | mesmo canal, lista "poder no cotidiano" |
| Degraus (V03, V10) | **Média**: o perfil de "dinheiro e poder" é a mesma família | hierarquia como sistema | mesmo canal |
| Idade Média, Brasil colonial/Império (V01–V02, V04–V09, V11–V12) | **Baixa**: é história cotidiana, não filosofia | nenhuma natural; a ponte seria forçada | **lista própria** e, se o teste funcionar, canal separado |
| Brasil por década (V13–V17), Antiguidade, Bíblia, "dormir" | **Baixa a nenhuma** | — | lista/canal separado, ou não fazer |

Honestidade: 9 inscritos é o melhor momento para testar no mesmo canal (pouco a estragar), mas **misturar duas audiências** tende a confundir a leitura do Studio. A recomendação é uma **lista própria "Como era"** dentro do canal para as seis primeiras e decidir a separação com os dados de 28 dias.

## 3. Os 6 melhores, em ficha

Escolha por critério da §2 (prio 4–5), com **um de cada forma** para o teste da §4 e três clusters. Reserva: V23 e V16.
"Gate 1": no formato de ficção (ADR 055) não há gate 1; vale para os que levam fichas. Onde digo "decisão do dono", é na pauta.

### V24: Por dentro de uma casa inglesa em 1880: quem serve a quem (híbrida, kit na frente)

- **Pergunta/promessa:** como uma casa de família abastada funcionava por dentro e quem fazia cada coisa para que parecesse funcionar sozinha; o espectador sai sabendo ler uma casa como um sistema de pessoas.
- **Gancho (0–30 s):** corte da casa ainda escuro; seis da manhã; a primeira luz acende no porão, não na sala. Pergunta dita: "quem já está de pé quando a família acorda?". Recorte dito em 5 s.
- **Blocos:** 1 madrugada (fogo, água quente); 2 o corte da casa como mapa de poder (andares); 3 café da manhã (a comida sobe); 4 o dia da casa (roupa, limpeza, compras); 5 o jantar (quem vê, quem não vê); 6 o sino e os corredores (circulação separada); 7 o que a casa custava a quem a fazia funcionar; 8 fecho: a porta de serviço e a pergunta.
- **Ideia visual central:** **o corte da casa que acende.** Um único quadro persistente com a casa em corte; cada tarefa acende uma sala e desenha uma seta (comida, água, roupa) pelo caminho certo; o sino faz o quadro mudar de estado (quem sobe, quem desce). Repete em todos os blocos, muda de estado e acumula.
- **Miniatura:** corte da casa em desenho, avatar na porta de serviço olhando para cima, palavra grande "QUEM SERVE?". Decisão final no gate 4.
- **Decisão do dono (gate 1):** com fichas (recomendado, o kit afirma na tela) ou sem; recorte (casa e cidade); se aceita fotos DP de 1880 como registro (licença caso a caso).
- **Hipótese (H-visual-1):** variável = o quadro-mecanismo recorrente (kit) versus cenas isoladas; medida = % médio assistido e retenção aos 2 min nos 7 dias, base 24–27% dos ensaios anteriores.

### V03: Sua vida em cada degrau da Idade Média: do servo ao rei (híbrida)

- **Pergunta/promessa:** como a mesma sociedade parecia de cada degrau, com as mesmas cinco perguntas para poder comparar (casa, comida, trabalho, medo, o que se podia possuir).
- **Gancho:** o avatar acorda no chão de terra e corta para a mesa do salão; "mesmo ano, mesma estrada, duas vidas". Pergunta e recorte (Inglaterra, séc. XIV) em 20 s.
- **Blocos:** 1 a escada; 2 servo; 3 camponês livre; 4 artesão de cidade; 5 clero; 6 cavaleiro; 7 o topo (aproveita "ser rico" sem refazer; chama o vídeo anterior); 8 fecho: quem nunca sobe e a pergunta do funil.
- **Ideia visual central:** **a escada que acende.** Grafo em camadas, persistente; o degrau atual brilha e a ficha das cinco perguntas se preenche com ícones e palavras (sem números); setas de "o que se devia ao degrau de cima" aparecem a cada degrau e mudam de grossura. O avatar troca de roupa a cada degrau.
- **Miniatura:** escada com o avatar no primeiro degrau, assustado, olhando para cima; "SERVO?" em palavra grande.
- **Decisão do dono:** qual avatar (o do piloto, em IA, ou um recorte do kit `createCutoutSkin`; misturar os dois quebra a série); quantos degraus; com fichas por degrau (recomendado) ou sem.
- **Hipótese:** variável = estrutura em degraus (lista de 6) versus um degrau só (piloto); medida = % assistido e CTR aos 7 e 28 dias, **só depois** de ler os 7 dias de `idade-media-ser-rico` (14/11).

### V21: Como era viver na Polônia em 1985? (híbrida)

- **Pergunta/promessa:** como era um dia comum de uma família numa cidade polonesa em 1985, em coisas que o brasileiro compara com a própria vida: comprar comida, morar, trabalhar, o que se podia dizer.
- **Gancho:** a sacola vazia à porta; "o que ela vai trazer de volta hoje?". Recorte (cidade polonesa, 1985, família de trabalhadores) em 10 s.
- **Blocos:** 1 a sacola e a fila; 2 o apartamento; 3 o trabalho; 4 o que se ouvia e o que se calava; 5 a rua e a igreja; 6 a noite em casa; 7 o que a família esperava do ano seguinte; 8 fecho com a ponte para 1995 (V22).
- **Ideia visual central:** **a prateleira e a fila.** Mapa da Europa abre e fecha; um quadro de prateleiras que esvazia ao longo do dia e uma fila de silhuetas que avança (kit); cada bloco troca o estado do quadro. Cenas em desenho para o resto.
- **Miniatura:** "POLÔNIA 1985" com o avatar segurando uma sacola vazia numa fila, cores de época.
- **Decisão do dono (gate 1):** fichas obrigatórias (política); quais fontes (relatos, estudos; **a verificar** o que existe baixável); se é "um dia" ou panorama; tom (nem herói, nem vilão, como no perfil de poder).
- **Hipótese:** variável = título com lugar + ano numa busca de baixa competição (15); medida = parcela das impressões vinda de "Pesquisa do YouTube" e CTR aos 28 dias.

### V01: Como era passar o inverno numa casa de camponês medieval? (kit)

- **Pergunta/promessa:** onde entrava e onde fugia o calor numa casa medieval, e o que custava manter o fogo vivo.
- **Gancho:** a casa em corte no escuro e uma pergunta: "o que impede essa casa de congelar?". Recorte (aldeia inglesa, séc. XIV) em 15 s.
- **Blocos:** 1 a casa em corte; 2 o fogo; 3 a fumaça (o preço do calor); 4 os animais; 5 roupa e cama; 6 a comida do inverno; 7 a noite longa; 8 o fim do inverno.
- **Ideia visual central:** **o balanço do calor.** Setas vermelhas (calor) e azuis (frio) numa casa em corte; cada bloco muda o estado (fecha a porta, entra um animal, apaga o fogo) e as setas se reorganizam. Sem números na tela, ou com fichas se houver.
- **Miniatura:** corte da casa com seta azul entrando e o avatar encolhido; palavra "FRIO?".
- **Decisão do dono:** fichas (recomendado); uso do mesmo avatar do piloto; se aceita um piloto de kit (peça nova: casa em corte).
- **Hipótese:** variável = kit versus IA (par com V02 e V04); medida = % assistido e retenção aos 2 min.

### V13: Como era viver no Brasil antes da luz elétrica? (kit)

- **Pergunta/promessa:** o que o escuro fazia com o dia de uma casa brasileira e o que mudou quando a luz deixou de depender do sol.
- **Gancho:** tela preta, uma vela acende, "são sete da noite". Pergunta e recorte (cidade e roça, a fixar) em 20 s.
- **Blocos:** 1 o relógio do sol; 2 luz como custo; 3 a casa à noite; 4 a rua à noite; 5 o que o escuro fazia com trabalho e estudo; 6 a chegada da luz (linha do tempo); 7 o que mudou; 8 pergunta de fecho (o que você faria com mais horas?).
- **Ideia visual central:** **o arco do dia.** Um relógio de 24 h persistente, o sol percorre o arco e as barras de luz acendem e apagam; cada fonte de luz é um estado. No fim, o mesmo arco com a luz elétrica (`compare`).
- **Miniatura:** casa escura com uma vela e "ESCURO?".
- **Decisão do dono:** recorte (um lugar e um tempo, não "o Brasil"); fichas; se aceita um vídeo sem rosto de personagem (o kit carrega).
- **Hipótese:** mecanismo temporal (relógio) versus galeria de cenas; medida = % assistido; teste do modo kit em outro cluster (Brasil).

### V07: Como era um dia numa fazenda do Brasil colonial? (IA)

- **Pergunta/promessa:** quem vivia onde na fazenda, quem mandava e quem trabalhava, num dia contado do sino à noite, sem espetáculo de violência.
- **Gancho:** o terreiro ao amanhecer, o sino; "quantas vidas cabem no mesmo terreiro?". Recorte (região e data) em 15 s.
- **Blocos:** 1 o sino; 2 a casa-grande; 3 a cozinha e a mesa; 4 a roça ou o engenho; 5 a senzala, com respeito; 6 a capela; 7 a noite; 8 fecho.
- **Ideia visual central:** **a planta que vira cena.** O terreiro visto de cima (blocos) é o índice: cada bloco acende um edifício da planta e a câmera "desce" para a cena em IA. Repetido em todos os blocos, muda de estado (de manhã a noite). O kit só faz a planta; a IA faz a cena habitada (multidão e arquitetura são o que ele não faz).
- **Miniatura:** planta do terreiro com três pontos coloridos e a pergunta "ONDE VOCÊ DORMIRIA?".
- **Decisão do dono:** quem é o "você" (sugestão: hóspede observador, **nunca** o escravizado como jogo); com fichas ou sem (recomendo fichas, por sensibilidade); se o teto de 12 imagens do §8 vale ou se o precedente de 76 do piloto se repete.
- **Hipótese:** variável = IA-led (cena habitada) versus kit (par com V13 no Brasil); medida = % assistido, custo em horas.

## 4. Plano de teste dos três modos (kit × IA × híbrida)

**O limite honesto:** o canal tem 9 inscritos e a maioria dos vídeos fica em dezenas ou centenas de views. Com esse volume, **só um efeito muito grande aparece**; o teste vale como direção, não como prova. O CTR depende de título e capa e **não mede o modo visual**: mantém-se o mesmo molde de capa (avatar + palavra) em todos e trata-se o CTR como controle.

**Desenho (6 vídeos, 2 por modo, dois clusters para não confundir tema com forma):**

| Rodada | Cluster | kit | IA | híbrida |
|---|---|---|---|---|
| 1 | Idade Média (mesmo mundo, mesma busca "idade média") | V01 | V02 | V04 |
| 2 | Brasil (mesma busca "Brasil colonial/antes") | V13 | V07 | V12 |

- **Variável única:** modo visual do corpo do vídeo. **Fixos:** voz clonada, duração (10–12 min, ±2), molde de capa, hora de postagem, estrutura da pergunta no título (a pergunta do título é dita nos primeiros ~30 s), mesma playlist.
- **Ordem:** alternar (kit, IA, híbrida, depois o contrário), um por semana, para a data e a sazonalidade não coincidirem com um modo. Cobre as 4–6 semanas do §12.
- **Medida primária (Studio, aos 7 e 28 dias):** % médio assistido e retenção aos 30 s e aos 2 min. **Controle:** CTR e impressões. **Secundária:** parcela de impressões vinda da busca (V21 e V13 testam a demanda).
- **Base:** 24–27% assistido dos ensaios anteriores (§4 do arquivo). A **margem que decide** (quantos pontos percentuais) é definida pelo dono **antes** do teste; não sai dos dados.
- **Custo, por modo (do `manifest.json` e do registro de horas):** horas humanas, imagens geradas/reprovadas, rejeições no gate 3, tempo de render, linhas de código novo no template. Isso é o que o piloto não mediu.
- **Regra de leitura:** um modo só "ganha" se os **dois** vídeos dele superam os dois de outro modo na medida primária nas duas rodadas. Empate = vence o mais barato.
- **Antes de tudo:** registrar H-visual-1 no `metrics.json` de cada vídeo e **ler os 7 dias de `idade-media-ser-rico` (14/11)** para não repetir um modo cujo piloto já falhou.

## 5. O que não fazer

- **Temas já vetados (CLAUDE.md §1):** Titanic/Hindenburg/Everest 1996, Segunda Guerra, true crime e sobrevivência recente com foto de agência. Aqui isso significa **não** fazer "como era a vida num campo de concentração/na Segunda Guerra" nem desastre recente.
- **Pessoa famosa dentro do lugar** (Júlio César, Santos Dumont, Machado, Dom Pedro): vende no arquivo, mas a skill veda pessoa real como personagem.
- **Série de títulos idênticos** ("Assim era a vida dentro de…"): é o risco do §12 (conteúdo repetitivo). A defesa é variar o corpo: por isso os modos e os mecanismos diferem entre vídeos, e o "mesmo corpo com outra data" não serve.
- **"Brasil por ano" em lote:** o arquivo mostra que só anos com memória coletiva rendem; evitar 1951, 1955, 1969, 1972.
- **Imagem realista de IA de fato histórico:** exige a divulgação de conteúdo alterado (§2.4); o piloto em desenho não obriga, mas é decisão do dono. Fotos reais só em DP e com licença registrada.
- **Dependem de rosto ou direito incerto:** V17 e V15 (marcas, músicas, pessoas, anúncios); V20 (religião); qualquer foto pós-1930 sem licença.
- **Escravidão e ditadura:** sem gamificar ("nível"), sem cena de castigo, sem tomar pessoas reais ou vítimas como personagem; só com fichas e verificador.
- **Copiar título, ordem ou roteiro de outro canal:** os canais do arquivo são pista de forma. Em particular, o "Maria cozinhava…" e os "Assim era a vida dentro de…" não se repetem com outra data.
- **Mais de 12 imagens de IA sem decidir o teto:** o §8 diz geração só para lacunas; o piloto usou 76 por decisão do dono. Cada vídeo IA-led precisa dessa decisão reafirmada.

## 6. Lacunas (só o Studio ou o dono respondem)

1. **Impressões, CTR, retenção e origem do tráfego** de `idade-media-ser-rico` (14/11 e 05/12): sem isso nada do §4 tem base. É a primeira dependência.
2. **Se o dono quer fichas** (explicativo) **ou ficção** (ADR 055) por vídeo. Isso decide o modo visual (§0).
3. **Lista própria ou canal separado** para o cluster "Como era"; e se o dono aceita misturar com os ensaios de filosofia por 6 vídeos.
4. **Avatar:** o do piloto (IA, do dono) ou um recorte do kit; e se o elenco do kit (`CastScene`, ainda "em desenvolvimento", sem vista de perfil, andar de frente "estranho" no piloto Agostinho, olhos grandes, `InkScenery` com sete peças) aguenta um vídeo longo ou só 3–4 momentos.
5. **Teto de imagens de IA** (12 do §8 ou o precedente de 76) e os termos do gerador (`termos-chatgpt-imagem.md`, pendente).
6. **Por que a Polônia 1985/1995 tem busca** (um vídeo, uma série, escola?): só o vidIQ de títulos ou comentários responde, não este arquivo.
7. **Se o formato "dormir" (2–3,5 h) vale a produção:** o arquivo só tem views e breakout, nada de retenção.
8. **Monetização de escravidão e ditadura** (adequação a anunciantes): não verificada; consultar a política do YouTube antes de V07, V09 e V16.
9. **Fontes baixáveis** para V21, V13 e V24 (o `vp sources` só conhece o que existe em fontes abertas): a pauta precisa listar o que há antes de prometer.
10. **Quanto custa de fato o kit-led:** nenhuma peça nova (casa em corte, relógio do dia, prateleira que esvazia) existe hoje no kit; cada uma é código novo, e a frente do kit segue sendo "uma por vez" (CLAUDE.md §1).
