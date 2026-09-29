# Nicho: perfis de "dinheiro e poder" de grupos e famílias brasileiras no YouTube (2026-09-29)

Pesquisa de mercado para o formato explicativo (#48). Complementa `votorantim-viabilidade.md` (fontes e imagens
do caso) e `modelo-perfil-de-poder.md` (estrutura do roteiro). O objeto aqui é o mercado de vídeos, não os grupos
nem as pessoas.

## 1. Pergunta e data

Há espaço de nicho no YouTube em português do Brasil para vídeos explicativos de 5–7 min, no estilo How Money
Works, sobre dinheiro e poder de grupos econômicos e famílias empresariais brasileiras, com tom crítico e
documentado (nem herói, nem vilão) e fonte citada na tela? Primeiro caso: Grupo Votorantim / família Ermírio de
Moraes.

**Data da consulta: 2026-09-29.** Inscritos, visualizações, contagem de comentários e datas relativas ("há 3
meses") são desse dia.

## 2. Método e limites

### O que foi consultado

Tudo por `curl` em páginas públicas do YouTube, sem login, com cabeçalho `Accept-Language: pt-BR`, lendo os dados
que a própria página traz no HTML. Nenhuma API paga e nenhuma YouTube Data API.

| Tipo | Quantidade | O que dá |
|---|---|---|
| Página de resultados de busca | 18 | até 20 vídeos por busca: título, canal, visualizações, data relativa, duração |
| Página de vídeo | 29 | `viewCount`, `publishDate`, `lengthSeconds`, contagem de comentários, descrição completa |
| Aba "Vídeos" de canal | 20 | inscritos, total de vídeos, 30 vídeos mais recentes com visualizações e data relativa |
| Aba "Sobre" de canal | 10 | data de criação ("Inscreveu-se em") e visualizações totais |
| Storyboard do player (miniaturas de quadros) | 9 vídeos, 2 folhas cada | 18 quadros de 320×180 por vídeo (início e meio); no vídeo do Maestria, 50 quadros de 160×90 |
| Comentários (requisição de continuação que a página faz ao rolar) | 6 vídeos, 2 páginas cada | os 40 primeiros comentários na ordem "principais" |
| Sugestões de busca do YouTube (autocompletar) | 14 termos | o que o YouTube completa para cada termo |
| Busca na web | 2 | listas de canais de negócios (não trouxeram canal novo do nicho) |

Buscas feitas no YouTube (URLs completas, primeira página de resultados):

- Grupos: [história da votorantim ermírio de moraes](https://www.youtube.com/results?search_query=hist%C3%B3ria%20da%20votorantim%20erm%C3%ADrio%20de%20moraes),
  [família Ermírio de Moraes](https://www.youtube.com/results?search_query=fam%C3%ADlia%20Erm%C3%ADrio%20de%20Moraes),
  [família Safra história](https://www.youtube.com/results?search_query=fam%C3%ADlia%20Safra%20hist%C3%B3ria),
  [família Marinho Globo história](https://www.youtube.com/results?search_query=fam%C3%ADlia%20Marinho%20Globo%20hist%C3%B3ria),
  [Odebrecht história da empresa](https://www.youtube.com/results?search_query=Odebrecht%20hist%C3%B3ria%20da%20empresa),
  [Gerdau história família](https://www.youtube.com/results?search_query=Gerdau%20hist%C3%B3ria%20fam%C3%ADlia),
  [Klabin história família](https://www.youtube.com/results?search_query=Klabin%20hist%C3%B3ria%20fam%C3%ADlia),
  [Camargo Corrêa história](https://www.youtube.com/results?search_query=Camargo%20Corr%C3%AAa%20hist%C3%B3ria),
  [família Moreira Salles história](https://www.youtube.com/results?search_query=fam%C3%ADlia%20Moreira%20Salles%20hist%C3%B3ria),
  [Jorge Paulo Lemann 3G história](https://www.youtube.com/results?search_query=Jorge%20Paulo%20Lemann%203G%20hist%C3%B3ria),
  [JBS irmãos Batista história](https://www.youtube.com/results?search_query=JBS%20irm%C3%A3os%20Batista%20hist%C3%B3ria).
- Descoberta de canais: [famílias mais ricas do Brasil como ficaram ricas](https://www.youtube.com/results?search_query=fam%C3%ADlias%20mais%20ricas%20do%20Brasil%20como%20ficaram%20ricas),
  [história de empresas brasileiras documentário](https://www.youtube.com/results?search_query=hist%C3%B3ria%20de%20empresas%20brasileiras%20document%C3%A1rio),
  [bilionários brasileiros história](https://www.youtube.com/results?search_query=bilion%C3%A1rios%20brasileiros%20hist%C3%B3ria),
  [grupos econômicos que controlam o Brasil](https://www.youtube.com/results?search_query=grupos%20econ%C3%B4micos%20que%20controlam%20o%20Brasil),
  [dinastias empresariais brasileiras](https://www.youtube.com/results?search_query=dinastias%20empresariais%20brasileiras),
  [quem são os donos do Brasil família bilionária](https://www.youtube.com/results?search_query=quem%20s%C3%A3o%20os%20donos%20do%20Brasil%20fam%C3%ADlia%20bilion%C3%A1ria),
  [a família dona das empresas que você usa todo dia](https://www.youtube.com/results?search_query=a%20fam%C3%ADlia%20dona%20das%20empresas%20que%20voc%C3%AA%20usa%20todo%20dia)
  (esta última só trouxe novelas curtas; descartada).

Nenhuma fonte devolveu erro 429 ou bloqueio. Emojis dos títulos foram omitidos nas citações.

### Limites

- **Busca não é neutra.** Os resultados dependem de região, idioma e histórico; sem login, vi uma ordem que pode
  não ser a de um espectador real. Só li a primeira página de cada busca. Canais que não aparecem para esses termos
  ficaram de fora.
- **Datas.** Onde abri a página do vídeo, a data é o `publishDate` do HTML (fuso -07:00 ou -08:00, pode diferir em
  um dia da data no Brasil). Onde só vi a busca ou a lista do canal, a data é relativa ("há 1 ano") e aproximada; a
  frequência de publicação sai dessas datas relativas.
- **Não assisti aos vídeos.** Tom e estilo visual vêm de títulos, descrições e dos quadros do storyboard. Em 320×180
  não dá para ler texto pequeno: "cita fonte na tela" é **não verificado** onde não aparece nada legível, e não
  "não cita".
- **Comentários** são os 40 primeiros na ordem do YouTube, em 6 vídeos: amostra pequena e escolhida pelo algoritmo,
  não representativa.
- **Sem dados de desempenho interno** (impressões, CTR, retenção, origem do tráfego): só o dono do canal vê.
- **Não consultei** Social Blade (a aba "Sobre" já trouxe data de criação e total de visualizações), Google Trends,
  nem a página do próprio How Money Works. A duração do vídeo de referência (~21 min) vem de
  `docs/pesquisa/modelo-perfil-de-poder.md`, não desta consulta.
- Os dados brutos ficaram fora do repositório (pasta temporária da sessão).

## 3. Concorrentes

Ordenados pela proximidade com o formato proposto. Inscritos e visualizações em 2026-09-29, lidos na aba "Vídeos" e
na aba "Sobre" de cada canal. "Último mês" = vídeos com data relativa até "há 1 mês" na lista do canal.

| Canal | Inscritos | Desde · views totais | Ritmo recente | Formato observado | Cita fontes? | Vídeos recentes (views) |
|---|---|---|---|---|---|---|
| [Bastidores do Poder](https://www.youtube.com/@bastidoresdopoder) | 54 mil | jan/2024 · 3.221.659 | 5 no último mês; 9 em ~3 meses | 10–16 min. Apresentador em cena sobre fundo branco; cartões com números ("R$ 54,1 bilhões em ativos"), logos, manchetes de jornal como imagem, B-roll, legendas embutidas | Descrição: nenhuma fonte nomeada nos 3 vídeos abertos. Tela: manchetes aparecem; nenhum rótulo de fonte legível junto aos números | Esteves 343 mil (7 meses); Tanure 324 mil (7 meses); Family office do Itaú 278 mil; Maggi 177 mil; Safra 81 mil; Batistas 60 mil; Marinho 31 mil (3 sem.) |
| [Curioso Mercado](https://www.youtube.com/@curiosomercado) | 464 mil | mar/2020 · 61.215.663 | 24 no último mês (inclui as séries "Curioso Explica" e "EP.") | 19–45 min na maioria dos vídeos de grupos (Walther Moreira Salles: 1h10). No vídeo da Votorantim, quadros sem apresentador: imagem de arquivo, recorte de jornal com trecho destacado, logos, cartelas de capítulo | Às vezes, na descrição (Moreira Salles: 5 fontes; Odebrecht: "Baseado no livro 'A Organização', de Malu Gaspar"; Safra: livros com link de compra). Votorantim, Gerdau e Klabin: nenhuma nomeada. Tela: recorte de jornal visível (Votorantim) | Faria Lima 187 mil (9 dias); Coamo 267 mil (1 mês); Hering 122 mil (1 mês); Garantia EP.61 17 mil (2 sem.) |
| [InvestNews BR](https://www.youtube.com/@InvestNewsBR) | 972 mil | não consultado | 30 vídeos em ~14 dias | Portal jornalístico. Série "Spotlight"; 11–13 min nos vídeos abertos, e um de 5:46 sobre a Camargo Corrêa. Apresentador em estúdio, números grandes ao fundo ("R$ 4,7 bilhões"), tarjas de nome, B-roll | Descrição: nenhuma nomeada nos 3 vídeos abertos. Tela: não verificado | Votorantim 319 mil (abr/2026); família da Gol 42 mil (7 dias); família Constantino 2,2 mil (2 sem.) |
| [Spotniks](https://www.youtube.com/@spotniks) | 2,18 mi | jul/2014 · 178.556.761 | ~12 no último mês | 25–59 min. Apresentadora em sofá, legendas embutidas, ilustrações animadas, manchetes de jornal destacadas | Descrição do vídeo da JBS: nenhuma nomeada. Tela: manchetes com trecho destacado | JBS 1,32 mi (abr/2026); "As famílias que governam o Brasil" 2,89 mi (clãs políticos, não grupos econômicos). Um vídeo recente se chama "Lançamos a nossa campanha para deputado federal" (757 mil) |
| [Maestria nos Negócios](https://www.youtube.com/@maestrianosnegocios) | 637 mil | mar/2021 · 96.912.137 | 6 no último mês; 15 em ~3 meses | "Mini-documentários investigativos" (descrição do canal). Moreira Salles: 12 min, arquivo, B-roll, cartões de manchete | Descrição: nenhuma nomeada. **Tela: cartão de manchete com veículo e ano legíveis ("O GLOBO (2025)")** | Moreira Salles 166 mil (mai/2025); Brás 142 mil; Uber 125 mil |
| [Era uma vez Hoje](https://www.youtube.com/@eraumavezhoje) | 65 mil | nov/2024 · 5.301.807 | 9 no último mês; 18 em ~3 meses | Temporadas. Episódios numerados de 1 a pelo menos 14 sobre a Globo e a família Marinho (o ep. 3 se diz da temporada "Clãs que Moldaram o Brasil"; os mais recentes são marcados "T02"). 10–16 min. Apresentadora em cena diante de estante; fotos de arquivo com legenda | Descrição do ep. 3: não lista fontes; oferece "acesso aos documentos originais" num clube pago | T02 Ep14 106 mil; T02 Ep13 80 mil; ep. 3 184 mil |
| [Imperio S.A](https://www.youtube.com/@ImpérioS.A-r2h) | 40,7 mil | jan/2026 · 6.822.476 | 30 vídeos em ~21 dias | 22–57 min. Nos quadros vistos, sem apresentador; cenas fotorrealistas, algumas com texto deformado em placas e telas. Mistura grupos econômicos, marcas antigas e política do dia | Votorantim: "tudo baseado em fontes históricas e documentos oficiais", sem nomear. Camargo Corrêa: nada | Will Bank 224 mil (6 dias); Master 193 mil (8 dias); Votorantim 303 mil (fev/2026); Camargo Corrêa 31 mil (set/2026) |
| [Lado B da Elite](https://www.youtube.com/@LadoBdaElite) | 38,5 mil | jul/2025 · 4.904.787 | 14 no último mês; 29 em ~3 meses | 23–36 min. Cartão de abertura: "Este vídeo não é uma homenagem nem uma biografia romântica. O foco é a análise crítica de gestão e os bastidores do poder." Cenas ilustradas em estilo 3D | **Descrição da Odebrecht com lista detalhada** (processos, inquéritos, livros, periódicos). Rodapé na tela: "Todo o conteúdo é fundamentado em investigações, processos e fontes jornalísticas disponíveis na descrição." | Nenê Constantino 70 mil; Thor Batista 68 mil; Odebrecht 102 mil (mai/2026); Klabin/Ibama 11 mil; JBS 2,9 mil |
| [Grandes Dinastias](https://www.youtube.com/@grandesdinastias) | 23,9 mil | out/2025 · 947.430 | 9 no último mês (o canal tem 10 vídeos) | 22–53 min. Famílias históricas (Prado, Matarazzo, café). Cenas em P&B e sépia de época, várias com composição repetida e pequenas variações | Descrição do vídeo dos Prado: "Fontes principais: USP/FEA Pioneiros & Empreendedores, Câmara Municipal de São Paulo, Assembleia Legislativa de São Paulo, FGV/CPDOC, Revista de História da USP, Unicamp e Prefeitura de São Paulo" | Prado 505 mil (ago/2026); Matarazzo 138 mil; café 104 mil |
| [Passo a Passo Empreendedor](https://www.youtube.com/@passoapassoempreendedoroficial) | 676 mil | não consultado | 22 no último mês | 5–15 min (Klabin 14:43; J&F 10:11; lista Forbes 7:44). Visual não verificado | Klabin: nenhuma nomeada (só links de livros de negócios) | Forbes 2026 307 mil (3 sem.); mais ricos por estado 217 mil; "O que aconteceu com a JBS?" 85 mil |
| [Conhecimento Disruptivo](https://www.youtube.com/@conhecimentodisruptivo) | 374 mil | não consultado | ~2–3 por semana, cada um também publicado como "[SEM ANÚNCIO]" | 20–24 min. "O que aconteceu com" marcas e empresas. Visual não verificado | Não verificado | Magalu 154 mil; Casas Bahia 118 mil; Bradesco 109 mil; Odebrecht/Lava Jato 98 mil (7 meses) |
| [Histórias Empreendedoras](https://www.youtube.com/@historiasempreendedoras) | 17,5 mil | não consultado | Parado: vídeo mais recente há 1 ano | 11–15 min, "A história da X". Visual não verificado | Não verificado | JBS 55 mil, Gerdau 30 mil, Klabin 21 mil (todos há 3 anos) |
| [Legado Capital](https://www.youtube.com/@legadocapitals) | 392 | abr/2026 · 88.189 | 971 vídeos desde abr/2026; descrição: "Novos vídeos todos os dias às 9h e 19h" | 10–11 min. Visual não verificado | Não verificado | Votorantim 532; Gerdau 22; Camargo Corrêa 208; Moreira Salles 125; Lemann 10 |
| [Reis do Capital](https://www.youtube.com/@ArquitetosdoPoderYT) | 1,27 mil | set/2025 · 56.318 | Nenhum vídeo nos últimos ~8 meses (os 30 listados são de "há 8 meses") | 13–16 min. Descrição: "Conteúdo educativo sobre história empresarial usando narração/imagens de IA" | "Baseado em fontes documentadas", sem nomear | Setúbal 5,5 mil; Ermírio de Moraes 840; Safra 522 |

Notas:

- O ritmo de Imperio S.A e Legado Capital (mais de um vídeo por dia) é observado. Produção assistida por IA nesses
  dois é **inferência** (no Imperio S.A, cenas com texto deformado; no Legado Capital, só o volume). O Reis do Capital
  a declara na descrição. O InvestNews se descreve como "portal de notícias multiplataforma", e o ritmo dele não indica isso.
- Canais grandes que também aparecem nas buscas mas são generalistas: [Planeta Novo](https://www.youtube.com/@PlanetaNovo)
  (3,82 mi; "Contando e fazendo História desde 2016"; Marinho 347 mil em 2021, Joseph Safra 287 mil há 5 anos; hoje
  publica sobre política, crime e geopolítica) e [NORMOSE](https://www.youtube.com/@Normose_) (500 mil; "BILIONÁRIOS DA
  CARNE | Quem são os donos do Brasil?", 27 mil há 2 meses; os outros vídeos da lista publicados nos últimos 2 meses
  têm de 95 mil a 212 mil, exceto um publicado há 5 horas).
- Canais pequenos que já usam o rótulo de poder: [Mapa Do Poder](https://www.youtube.com/@mapadopoderes) (381 inscritos,
  8 vídeos, parado há 5 meses; Safra 1,1 mil), [Biografias de Poder](https://www.youtube.com/@BiografiasdePoder)
  (3,25 mil; um vídeo com 319 mil, ver §5), [Bastidores do Capital](https://www.youtube.com/@BastidoresdoCapital)
  (2,71 mil; 5 vídeos; Safra 47,8 mil) e "Impérios de Sucesso & Grandes Mentes de Negócios" (vídeos de 5–6 min
  sobre as "dinastias" Ermírio de Moraes e Gerdau com 144 e 4 visualizações).
- A busca na web devolveu listas de canais de empreendedorismo e de finanças pessoais (ex.: "12 canais para
  empreendedores no YouTube", [sebraemg.com.br](https://sebraemg.com.br/canais-empreendedores/); "Finanças Pessoais: Os
  12 Melhores Canais do Youtube", [clubedovalor.com.br](https://clubedovalor.com.br/blog/canais-financas-e-investimentos-youtube/)).
  Não abri essas páginas e não usei nada delas; nenhum canal novo do nicho saiu daí.

## 4. Vídeos sobre os grupos

Colunas: visualizações; data (exata quando abri a página do vídeo, relativa quando só vi a busca ou a lista do canal);
duração. Seleção: perfis, documentários e explicativos; deixei de fora cortes de telejornal e entrevistas, salvo
quando indicados.

### Votorantim / Ermírio de Moraes

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [Antônio Ermírio de Moraes: A Vida do Capitão da Votorantim](https://www.youtube.com/watch?v=GczRkWwPxMk) | Curioso Mercado | 363.459 | 2025-07-19 | 35:32 |
| [Votorantim pós-Antônio Ermírio: como o grupo quer investir um caixa de R$ 7,7 bilhões](https://www.youtube.com/watch?v=pKcJjVLLtpc) | InvestNews BR | 319.328 | 2026-04-13 | 12:19 |
| [Por Dentro da VOTORANTIM: O Que Aconteceu Com Esse Império do Cimento?](https://www.youtube.com/watch?v=lhCIR4NCQ58) | Imperio S.A | 302.891 | 2026-02-16 | 34:53 |
| [Como Antônio Ermírio de Moraes transformou a Votorantim num símbolo de sucesso no Brasil](https://www.youtube.com/watch?v=MHM0Xk3Vq1U) | InvestNews BR | 55.217 | 2025-05-14 | 11:13 |
| [Roda Viva — Antônio Ermírio de Moraes — 1991](https://www.youtube.com/watch?v=nFAjgf0vLbw) (entrevista de arquivo) | Roda Viva | 43.207 | há 11 anos | 1:27:29 |
| [Votorantim: o negócio que atravessa gerações — Histórias Centenárias Ep. 07](https://www.youtube.com/watch?v=HXR7oukEOE0) | Folha de S.Paulo | 40.192 | 2021-09-26 | 8:01 |
| [CONHEÇA A HISTÓRIA DA VOTORANTIM](https://www.youtube.com/watch?v=YBAgIuLWznU) | Luciano Hang Oficial | 15.686 | há 4 anos | 3:09 |
| [A HISTÓRIA DE JOSÉ ERMÍRIO DE MORAES - CRIADOR DO GRUPO VOTORANTIM](https://www.youtube.com/watch?v=yRm5FHiP8N4) | Mazukim | 7.123 | há 3 anos | 6:01 |
| [Votorantim — O Império Que Não Quebra](https://www.youtube.com/watch?v=AKOkz-5carQ) | DOSSIE EMPRESARIAL | 3.954 | 2026-05-06 | 16:02 |
| [Como a "Natural One" Saiu do Cimento ao Suco de Laranja — A Invenção da Votorantim...](https://www.youtube.com/watch?v=j_vJQo2Clmo) | Imperio S.A | 1,6 mil | há 2 sem. | não verificado |
| [O Império Ermírio de Moraes – A Dinastia Oculta Por Trás dos 100 Anos de Poder da Votorantim](https://www.youtube.com/watch?v=DLjPqM4E7SM) | Reis do Capital | 840 | 2025-12-30 | 13:16 |
| [Antônio Ermírio: Construiu o IMPÉRIO Votorantim do Zero](https://www.youtube.com/watch?v=wBoW51t5Qq0) | Legado Capital | 532 | há 1 mês | 11:08 |
| [A Guerra Secreta na Dinastia Ermírio de Moraes e o Voto de R$ 30 Bi](https://www.youtube.com/watch?v=5Z2qxHVdG3o) | Impérios de Sucesso & Grandes Mentes | 144 | há 8 dias | 5:19 |
| [1918: José Ermírio de Moraes Transformou a Vila em um Império Bilionário](https://www.youtube.com/watch?v=fVmGPssmQ7g) | Lado b do brasil | 101 | há 1 mês | 8:08 |

Também aparecem entrevistas de arquivo publicadas pelo canal Pedro Barros (Jô Soares 1988, 4.091; Roda Viva 1998,
parte 1, 1.897; Provocações, 312) e uma biografia antiga ([ARTE & CULTURA](https://www.youtube.com/watch?v=tQXXvBhNRfI), 8.712, há 8
anos, 15:10). Três vídeos passaram de 300 mil visualizações em ~14 meses (jul/2025 a abr/2026).

Observação sobre precisão: a descrição do vídeo do Reis do Capital diz "De imigrante português analfabeto a
fundador de um império industrial [...]. Antonio Ermírio de Moraes construiu a Votorantim"; a do Imperio S.A diz
"Como Antonio Pereira Ignacio chegou analfabeto ao Brasil em 1884"; a do DOSSIE EMPRESARIAL diz que "um imigrante
português" comprou a fábrica em 1918 e que "o verdadeiro arquiteto do império seria seu genro: José Ermírio de
Moraes". As descrições não concordam entre si; a conferência é trabalho do `sources.json`, não deste documento.

### Safra

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [Como EDMOND SAFRA construiu um IMPÉRIO FINANCEIRO global](https://www.youtube.com/watch?v=KV7RGSqps2o) | Curioso Mercado | 678.957 | 2023-10-27 | 29:01 |
| [JOSEPH SAFRA, o banqueiro mais rico de todos](https://www.youtube.com/watch?v=zXN7ylBh1NI) | Planeta Novo | 287.468 | há 5 anos | 15:51 |
| [A HISTÓRIA DE JOSEPH SAFRA - O HOMEM MAIS RICO DO BRASIL](https://www.youtube.com/watch?v=kSfkwL3IP0M) | Passo a Passo Empreendedor | 189.843 | há 7 anos | 11:41 |
| [O que os Safra compraram em Londres, Nova York e Boston](https://www.youtube.com/watch?v=gmFj6NK0TYc) | Bastidores do Poder | 81.584 | 2026-05-06 | 11:44 |
| [The $23 Billion Lebanese Family That Owns Brazil: The Safra Dynasty](https://www.youtube.com/watch?v=_zGJ_VYeRWk) | Old Money Luxury | 64.495 | 2025-06-10 | 17:02 |
| [A Guerra Bilionária da Família Safra](https://www.youtube.com/watch?v=gRmTNI0vuBU) | Bastidores do Capital | 47.801 | há 1 ano | 13:12 |
| [Safra: Os Banqueiros dos Bilionários](https://www.youtube.com/watch?v=AYSjZ_ts1Yc) | Bastidores do Poder | 33.427 | há 2 anos | 12:57 |
| [Edmond Safra: A Mente Mais Brilhante do Mundo Bancário](https://www.youtube.com/watch?v=j7YKuDzlCRc) | Aura por Lucas Abreu | 25.281 | há 10 meses | 1:01:21 |
| [A DINASTIA SAFRA: Segredos do Maior Império Bancário do Mundo](https://www.youtube.com/watch?v=07VHmamtC34) | Papo de Milionário | 7.404 | há 2 anos | 10:01 |
| [Banco Safra: O Império Bilionário da Família que lucra com os Juros no Brasil](https://www.youtube.com/watch?v=2LATMGmZIzY) | Mapa Do Poder | 1.110 | há 5 meses | 23:37 |

O vídeo do Old Money Luxury é em inglês: na busca aparece com título traduzido para o português ("A família libanesa
de US$ 23 bilhões que é dona do Brasil..."); na página do vídeo, o título é o original em inglês. Outros cinco vídeos
de canais pequenos (35 a 2.380 visualizações) aparecem na mesma busca.

### Marinho / Globo

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [FAMÍLIA MARINHO](https://www.youtube.com/watch?v=gSUMFOiH2ts) | Planeta Novo | 347.040 | 2021-10-13 | 28:34 |
| [Os Três Casamentos de Roberto Marinho: O Lado Obscuro do Império — Ep 03](https://www.youtube.com/watch?v=ktQNsU4zJdc) | Era uma vez Hoje | 183.870 | 2026-05-03 | 10:52 |
| [A maior traição da TV brasileira: Como os Marinho descartaram os criadores da Globo — Ep. 9](https://www.youtube.com/watch?v=HzEzH-AgURA) | Era uma vez Hoje | 124.420 | há 3 meses | 16:05 |
| [QUEM FOI ROBERTO MARINHO](https://www.youtube.com/watch?v=FyCekOD4eUc) | Meteoro Brasil | 121.038 | há 5 anos | 18:07 |
| [A Globo avisou que não ia pagar a conta — T02 Ep14](https://www.youtube.com/watch?v=aLkqwn-_R00) | Era uma vez Hoje | 106 mil | há 2 sem. | não verificado |
| [A Globo nasceu ilegal e o Governo Ditatorial pagou a conta — Ep 02](https://www.youtube.com/watch?v=lRR-PiQz7o0) | Era uma vez Hoje | 89.282 | há 5 meses | 15:48 |
| [Do rádio ao streaming, como a família Marinho reinventa o grupo Globo para se manter no topo](https://www.youtube.com/watch?v=m8Pv6alTPOc) | InvestNews BR | 83.584 | 2025-11-26 | 12:23 |
| [Como os Marinho estão dividindo o comando da Globo entre os filhos e um ex-Cosan](https://www.youtube.com/watch?v=LNn-9snYZ10) | Bastidores do Poder | 31 mil | há 3 sem. | não verificado |
| [Como a Família Marinho Construiu um Império BILIONÁRIO?](https://www.youtube.com/watch?v=0f3LtnG6vv0) | Sabe Tudo | 29.830 | há 4 meses | 12:09 |
| [Roberto Marinho: o homem que construiu o Império Globo](https://www.youtube.com/watch?v=RJVBNXwQVRo) | Aura por Lucas Abreu | 17.296 | há 11 meses | 1:39:07 |
| [Como Roberto Marinho Transformou a Globo em um Império](https://www.youtube.com/watch?v=XIsa5G2oC8U) | Lásaro Do Carmo Júnior | 12.359 | há 1 mês | 6:55 |

O Era uma vez Hoje tem uma série inteira sobre o tema (episódios numerados até pelo menos 14, alguns citados acima).

### Odebrecht

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [A Ascensão e Queda da Odebrecht — Documentário](https://www.youtube.com/watch?v=mFg7BZx9Bm4) | Curioso Mercado | 984.157 | 2025-06-28 | 45:37 |
| [Como a ODEBRECHT voltou ao topo depois de dever R$ 98 BILHÕES](https://www.youtube.com/watch?v=AnGy9U_5vZI) | Fernando Miranda | 740.396 | há 1 mês | 2:36 |
| [ODEBRECHT — Como uma Empresa Brasileira Comprou Governos Inteiros](https://www.youtube.com/watch?v=Tcftydy01DQ) | Lado B da Elite | 101.521 | 2026-05-15 | 36:17 |
| [COMO O MAIOR ESQUEMA DE CORRUPÇÃO DO BRASIL CAIU?](https://www.youtube.com/watch?v=wjJjYKys0Wg) | Conhecimento Disruptivo | 97.721 | há 7 meses | 23:59 |
| [ODEBRECHT POR DENTRO: A CAIXA-PRETA ABERTA](https://www.youtube.com/watch?v=OXfRvJLLgP8) | AUVP Capital | 25.036 | há 10 meses | 22:03 |
| [O Império Que Comprava Países – A Queda da Odebrecht](https://www.youtube.com/watch?v=bnz-dCZ29G8) | Imperio S.A | 5.405 | há 6 meses | 26:36 |

Na mesma busca: um esquete de humor ("ODEBRECHT", Porta dos Fundos, 6.933.753, há 9 anos) e um vídeo em espanhol
(Emprende Aprendiendo, 2.389.745, há 5 anos).

### Gerdau

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [Moldados como Aço - O Filme](https://www.youtube.com/watch?v=elQHkflHfYs) (canal da empresa) | Gerdau | 447.411 | há 1 ano | 57:18 |
| [A Trajetória Centenária da Brasileira Gerdau](https://www.youtube.com/watch?v=tAWb6EMZWf8) | Curioso Mercado | 359.249 | 2023-06-23 | 20:39 |
| [AÇO DO BRASIL PARA O MUNDO - A HISTÓRIA DE JORGE GERDAU](https://www.youtube.com/watch?v=oinwhLPBmW0) | Passo a Passo Empreendedor | 98.008 | há 3 anos | 8:15 |
| [A GIGANTE DO AÇO BRASILEIRO - A HISTÓRIA DA GERDAU](https://www.youtube.com/watch?v=tLnWkFQOI5Q) | Histórias Empreendedoras | 30.134 | há 3 anos | 11:02 |
| [A Hístoria da Centenária Brasileira Gerdau](https://www.youtube.com/watch?v=v7qTyfTLSew) | Imperio S.A | 1.682 | há 2 meses | 22:12 |
| [Gerdau: O SEGREDO da Única Dinastia com 5 Gerações](https://www.youtube.com/watch?v=foDd6GT6toc) | Legado Capital | 22 | há 1 mês | 10:48 |
| [A Guerra Secreta na Dinastia Gerdau pelo Trono de Aço](https://www.youtube.com/watch?v=Hk1gCAc8U6A) | Impérios de Sucesso & Grandes Mentes | 4 | há 1 dia | 6:04 |

O YouTube não completa "família gerdau" (a única sugestão foi "família guimarães"). Os perfis com audiência são de
2023 ou antes; os de 2026 vêm de canais de alto volume e têm até 1,7 mil visualizações. Fora dos perfis, um vídeo
sobre uma fábrica do grupo teve audiência em 2026 ([A Mega Fábrica da Gerdau que Transforma Sucata de Metal em Aço de
Alto Valor](https://www.youtube.com/watch?v=HncNCDDxwW8), Construções e Mega Obras, 74.736, há 2 meses, 11:31).

### Klabin

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [A HISTÓRIA DA KLABIN - UM COLOSSO BRASILEIRO](https://www.youtube.com/watch?v=Ohq4VbhpWlE) | Passo a Passo Empreendedor | 530.008 | 2020-12-04 | 14:43 |
| [Klabin: a história centenária da maior produtora de papel do Brasil](https://www.youtube.com/watch?v=3cmoC71sJ-c) | Curioso Mercado | 59.149 | 2024-05-17 | 19:11 |
| [A MAIOR PRODUTORA DE PAPÉIS DO BRASIL - A HISTÓRIA DA KLABIN](https://www.youtube.com/watch?v=YJhR7ycmUpc) | Histórias Empreendedoras | 21.304 | há 3 anos | 11:25 |
| [MAURÍCIO KLABIN: A HISTÓRIA DO IMIGRANTE QUE INDUSTRIALIZOU SÃO PAULO](https://www.youtube.com/watch?v=BPrCGMFNCg4) | Gregorio Martins | 12.679 | há 10 dias | 21:05 |
| [IBAMA é Proibido de Fiscalizar Terras da KLABIN](https://www.youtube.com/watch?v=DAmqV8gLA-I) | Lado B da Elite | 11 mil | há 1 mês | não verificado |
| [Como A Klabin Ficou Bilionária Sem Que Quase Ninguém Percebesse](https://www.youtube.com/watch?v=BfSaOUpq-eg) | The Final Quarter | 404 | há 1 mês | 46:21 |

As sugestões de busca para "klabin" são todas de investidor ("klabin dividendos", "klabin 4 ou klbn11", "klabin
barsi"...). Sobre pessoas da família, o mesmo canal Gregorio Martins tem [EVA KLABIN E A CASA NA LAGOA](https://www.youtube.com/watch?v=xigcguvynsM)
(33.881, há 1 mês, 20:33).

### Camargo Corrêa

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [EXCLUSIVO: Camargo Corrêa ocultou bens bilionários?](https://www.youtube.com/watch?v=jDQqnz0ERdI) (jornalístico) | Times Brasil (licenciado CNBC) | 45.018 | 2025-05-29 | 10:18 |
| [De Itaipu e Havaianas à Lava Jato: O Que Aconteceu com a Camargo Corrêa?](https://www.youtube.com/watch?v=G2SEgB6dRBE) | Imperio S.A | 31.476 | 2026-09-02 | 57:15 |
| [A HISTÓRIA DE SEBASTIÃO CAMARGO - CRIADOR DO GRUPO CAMARGO CORRÊA](https://www.youtube.com/watch?v=csV3saxRct8) | Mazukim | 9.872 | há 3 anos | 6:10 |
| ['Querida, encolhi a Camargo Corrêa'](https://www.youtube.com/watch?v=13xYYPbIMKM) | InvestNews BR | 1.662 | há 3 sem. | 5:46 |
| [Sebastião Camargo: o Preço OCULTO da Camargo Corrêa](https://www.youtube.com/watch?v=8HBRwtjf5vQ) | Legado Capital | 208 | há 1 mês | 11:21 |

Nenhum vídeo sobre o grupo passou de 50 mil visualizações na busca. O resto dos resultados são telejornais
(licitações, disputa entre herdeiros) e vídeos institucionais. O YouTube completa "camargo corrêa" com só duas
sugestões ("camargo correa", "camargo correa construtora").

### Moreira Salles

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [O Family Office de R$54 bilhões dos donos do Itaú](https://www.youtube.com/watch?v=AgF9R3xeBoY) | Bastidores do Poder | 278.490 | 2026-01-17 | 15:54 |
| [A família Moreira Salles e o Unibanco — Parte 1](https://www.youtube.com/watch?v=2PyELsBod4c) | Curioso Mercado | 244.039 | 2024-06-30 | 27:17 |
| [A OBSCURA família que ENRIQUECE enquanto o Brasil ENFRAQUECE..](https://www.youtube.com/watch?v=tO926mL58CQ) | Maestria nos Negócios | 166.150 | 2025-05-02 | 12:13 |
| [A família Setubal e o Itaú — Parte 2](https://www.youtube.com/watch?v=_tBsO6mVy94) | Curioso Mercado | 100.062 | há 2 anos | 18:39 |
| [Nióbio: O Segredo da Família Moreira Salles](https://www.youtube.com/watch?v=vnyo_7XKcAI) | Bastidores do Poder | 35.410 | há 2 anos | 10:30 |
| [Por Que a Família Moreira Salles Vendeu Seu Palácio do Unibanco Por Migalhas](https://www.youtube.com/watch?v=Uj31rAlVjQY) | Grandes Mansões | 13.326 | há 6 meses | 34:42 |
| [Walther Moreira Salles: A História de um dos Maiores Banqueiros do Brasil](https://www.youtube.com/watch?v=bjK7CjtiHdw) | Curioso Mercado | 9.996 | há 8 meses | 1:10:27 |

Também: "Vida de Titãs" (252 e 201) e Legado Capital (125).

### Lemann / 3G

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [A INCRÍVEL VIDA DE JORGE PAULO LEMANN — Histórias de Sucesso #2](https://www.youtube.com/watch?v=obyjR_zO_z4) | Breno Perrucho - Jovens de Negócios | 1.878.088 | 2019-07-24 | 27:13 |
| [A emocionante vida e trajetória de Jorge Paulo Lemann](https://www.youtube.com/watch?v=FQk10UTl6zg) | Fatos Desconhecidos | 253.293 | 2021-02-10 | 18:58 |
| [O SEGREDO OBSCURO DE JORGE PAULO LEMANN! (PREJUÍZOS E ERROS BILIONÁRIOS)](https://www.youtube.com/watch?v=pDYhRGUifCI) | Eu Quero Investir | 164.458 | há 3 anos | 20:57 |
| [SONHO GRANDE DEMAIS? - POR QUE JORGE PAULO LEMANN DEIXOU A KRAFT HEINZ?](https://www.youtube.com/watch?v=fie9MKkslOk) | Passo a Passo Empreendedor | 147.933 | há 2 anos | 9:43 |
| [O BANCO DE JORGE PAULO LEMANN QUE DEIXOU DE EXISTIR](https://www.youtube.com/watch?v=ia97YUztnFw) | Passo a Passo Empreendedor | 64.832 | há 3 anos | 11:55 |
| [6 PILARES DE GESTÃO DE JORGE PAULO LEMANN QUE VOCÊ PODE APLICAR EM SEU NEGÓCIO](https://www.youtube.com/watch?v=3ByB7AIjlSw) | Passo a Passo Empreendedor | 53.934 | há 6 anos | 21:08 |
| [O Método Brutal de Jorge Paulo Lemann Para Criar Impérios](https://www.youtube.com/watch?v=xatTJvkU7Yg) | Lado B da Elite e Pororoca Financeira | 10.964 | há 3 meses | 23:15 |
| [COMO O DONO DA AMBEV COMPROU GRANDES EMPRESAS AMERICANAS](https://www.youtube.com/watch?v=TsFH0CHf3dw) | Desvendando Negócios | 8.430 | há 4 anos | 5:42 |

O vídeo "Garantia: O Banco que Moldou a Cultura do Mercado Financeiro no Brasil | EP. 61" do Curioso Mercado (17 mil,
há 2 semanas) está na lista do canal; não abri a página para ver se trata de Lemann.

### JBS / Batista

| Título | Canal | Views | Data | Duração |
|---|---|---|---|---|
| [A história não contada da JBS](https://www.youtube.com/watch?v=pgc9UcsUeOo) | Spotniks | 1.319.241 | 2026-04-07 | 25:07 |
| [Veja quem é Joesley Batista e como o Grupo JBS cresceu nos últimos anos](https://www.youtube.com/watch?v=jEB7Rij7SMY) (telejornal) | Fala Brasil | 1.306.743 | há 9 anos | 14:46 |
| [JBS Joesley Batista: O Inicio do Império e a Ascensão dos Irmãos Batista](https://www.youtube.com/watch?v=5PHoegTlDsA) | Ph Suburbano | 210.930 | há 9 anos | 11:38 |
| [O QUE ACONTECEU COM A JBS?](https://www.youtube.com/watch?v=qS_gtXnwhdo) | Passo a Passo Empreendedor | 85 mil | há 3 sem. | não verificado |
| [R$434 BILHÕES/ANO - COMO A J&F SE TORNOU O MAIOR CONGLOMERADO DO PAÍS](https://www.youtube.com/watch?v=vQuuV-Y4fRU) | Passo a Passo Empreendedor | 83.391 | há 10 meses | 10:11 |
| [Quem são os novos Batistas que estão comprando o Brasil?](https://www.youtube.com/watch?v=JJ5Eq16GmsA) | Bastidores do Poder | 60.042 | 2026-06-09 | 10:35 |
| [COMO UM PEQUENO AÇOUGUEIRO DOMINOU O MUNDO - A HISTÓRIA DA JBS - FRIBOI](https://www.youtube.com/watch?v=7blU0pKdCTU) | Histórias Empreendedoras | 54.655 | há 3 anos | 15:05 |
| [Da prisão ao poder: A volta por cima dos irmãos Batista na J&F](https://www.youtube.com/watch?v=yeTHgru0Db0) | InvestNews BR | 36.320 | há 1 ano | 12:23 |
| [BILIONÁRIOS DA CARNE — Quem são os donos do Brasil?](https://www.youtube.com/watch?v=fVt-tUd43rM) | NORMOSE | 27.409 | há 2 meses | 24:47 |
| [A Saga dos Irmãos Batista e JBS — Curioso Entrevista: Consuelo Dieguez](https://www.youtube.com/watch?v=hPQ83dYhZhg) (entrevista) | Curioso Mercado | 5.061 | há 1 mês | 1:01:06 |

### Onde não achei nada

Nenhum grupo da lista ficou sem vídeo. As ausências observadas são mais estreitas:

- Nas buscas feitas, **nenhum vídeo sobre Marinho/Globo nem sobre Camargo Corrêa do Curioso Mercado**, que cobre os
  outros sete grupos da lista (Votorantim, Safra, Moreira Salles, Odebrecht, Gerdau, Klabin e, por entrevista, JBS).
- **Nenhum perfil ou história de 2026 sobre Gerdau, Klabin ou Camargo Corrêa passou de 50 mil visualizações**; os
  que têm audiência são de 2020 a 2024. Em 2026, o maior perfil é o do Imperio S.A sobre a Camargo Corrêa (31 mil,
  57 min); fora dos perfis, o vídeo da fábrica da Gerdau (74.736) e o de Eva Klabin (33.881).
- **Nenhum vídeo sobre a "dinastia" Ermírio de Moraes (várias gerações) passou de mil visualizações**; os de
  audiência são biografia de Antônio Ermírio, notícia do caixa do grupo ou história corporativa longa.

## 5. Sinais de demanda

### Observado

1. **Audiência por vídeo.** Nas 11 buscas por grupo (200 vídeos distintos), 52 vídeos têm 50 mil visualizações ou
   mais. Entre os publicados desde 2025, com data exata: JBS/Spotniks 1.319.241, Odebrecht/Curioso 984.157,
   Votorantim/Curioso 363.459, Votorantim/InvestNews 319.328, Votorantim/Imperio S.A 302.891, Moreira Salles/Bastidores
   278.490, Marinho/Era uma vez Hoje 183.870, Moreira Salles/Maestria 166.150, Odebrecht/Lado B 101.521.
2. **Canais novos crescendo no tema** (aba "Sobre"): Imperio S.A, criado em jan/2026, com 6.822.476 visualizações e
   40,7 mil inscritos; Lado B da Elite, jul/2025, 4.904.787 e 38,5 mil; Era uma vez Hoje, nov/2024, 5.301.807 e 65 mil;
   Bastidores do Poder, jan/2024, 3.221.659 e 54 mil; Grandes Dinastias, out/2025, 947.430 e 23,9 mil com 10 vídeos.
3. **Tema vizinho com audiência alta.** "[As famílias que governam o Brasil](https://www.youtube.com/watch?v=MRG6d9bQC8Q)"
   (Spotniks, 2.894.825, 2026-05-19, 58:46, 20 mil comentários) trata de famílias na política, não de grupos
   econômicos. "[Os Verdadeiros Donos do Brasil: 5 Marcas que Controlam a Sua Vida (E Você Não Sabe)](https://www.youtube.com/watch?v=in22bPX_4rE)"
   (Biografias de Poder, 319.443, há 9 meses, 14:38) é o único dos 25 vídeos listados no canal acima de 16 mil
   visualizações.
4. **Pedidos nos comentários** (40 principais de cada vídeo):
   - No vídeo do family office do Itaú ([AgF9R3xeBoY](https://www.youtube.com/watch?v=AgF9R3xeBoY), Bastidores do Poder),
     com 142 curtidas: "Algumas ideias para seus proximos videos > Familias do Agro - Ermirio de Moraes, Fischer,
     Maggi, Cutrale, Batista, Ometto > Familias da epoca do Imperio - Como os 'quatrocentões' > Fortunas que se
     tornaram ruinas - Familia Matarazzo". O mesmo comentário pede, no fim do vídeo, "o patrimônio e os principais
     ativos dessas famílias hoje em dia". Outros: "Já tô esperando sentado a WEG" (59 curtidas), "Seria legal um
     vídeo sobre os quatrocentoes" (7).
   - No vídeo da Odebrecht do Lado B da Elite: pedidos de Americanas, Puma, Vorcaro e família real de Mônaco (0 a 4
     curtidas cada).
5. **O que o público elogia.** "Pesquisa, conteúdo e edição original de qualidade" (39 curtidas, Curioso/Votorantim);
   "Como que esse canal tem tão poucos inscritos? É de uma qualidade pouco vista para esse tema aqui no Youtube"
   (Bastidores); "Trabalho jornalístico de primeira", "Praticamente um mini documentário" (Spotniks/JBS). **Nenhum dos
   240 comentários lidos pede fontes ou fala de fontes.** Dois corrigem ou completam o vídeo (um diz que o vídeo do
   family office "está confuso" ao tratar os Moreira Salles como "a família do Itaú"; outro acrescenta um fato que
   "faltou falar" no vídeo do Maestria).
6. **Enquadramento crítico ressoa nos comentários de alguns vídeos.** "Essas são as capitanias hereditárias modernas.
   Sempre as mesmas famílias os mesmos sobrenomes..." (360 curtidas, Bastidores/Itaú); "Como sempre digo, o Brasil tem
   dono e não são os brasileiros" (1,9 mil curtidas) e "Um vídeo como esse deveria passar em rede nacional, no horário
   nobre" (2,5 mil curtidas), ambos em Spotniks/JBS.
7. **Público da Votorantim tem vínculo pessoal com o grupo.** No vídeo do Imperio S.A ([lhCIR4NCQ58](https://www.youtube.com/watch?v=lhCIR4NCQ58)),
   cerca de metade dos 40 principais comentários é de quem trabalhou, ou tem parente que trabalhou, em empresas do
   grupo, com tom de gratidão. No do Curioso Mercado ([GczRkWwPxMk](https://www.youtube.com/watch?v=GczRkWwPxMk)), a
   maioria elogia Antônio Ermírio como pessoa; um comentário com 30 curtidas contesta o trecho de controvérsia do vídeo
   ("Não tem nada de controverso...").
8. **Sugestões de busca do YouTube** (autocompletar, 2026-09-29):
   - "ermírio de moraes" → inclui "familia ermirio de moraes", "biografia antonio ermirio de moraes", "jose ermirio de
     moraes" e entrevistas (Jô Soares, Roda Viva).
   - "família safra" → inclui "familia safra historia", "heranca familia safra", "mansão familia safra".
   - "irmãos batista" → inclui "historia dos irmaos batista", "empresas dos irmaos batista", "irmãos batista jbs".
   - "jorge paulo lemann" → inclui "jorge paulo lemann historia", "... americanas".
   - "moreira salles" → inclui "familia moreira salles", "pedro moreira salles", "walter moreira salles".
   - "famílias mais ricas do brasil" → "as 5 familias mais ricas do brasil", "as 10 famílias mais ricas do brasil".
   - "história da família" → inclui "matarazzo", "abravanel", "rockefeller", "rothschild".
   - "família gerdau" → nenhuma sugestão sobre Gerdau. "klabin" → só termos de investidor. "camargo corrêa" → 2
     sugestões. "família marinho" → nenhuma sobre a Globo. "votorantim" → a cidade e a Votorantim Cimentos.

### Inferência

- A demanda existe e é recente: vídeos sobre esses grupos passam de 100 mil visualizações com regularidade, e canais
  criados em 2024–2026 cresceram rápido só com esse tipo de tema.
- A demanda é maior quando o título promete bastidor ou conflito ("história não contada", "o que compraram", "ascensão
  e queda") do que quando promete trajetória. Não medi isso; é leitura dos títulos com mais visualizações.
- Os pedidos nos comentários indicam interesse por famílias pouco cobertas (agro, "quatrocentões") e por um número
  final de patrimônio e ativos, que é o bloco "escala" do modelo de perfil.
- No caso Votorantim, parte relevante do público chega por vínculo afetivo (ex-funcionários, moradores). Um tom
  crítico, mesmo documentado, tende a gerar resistência nesses comentários; o contrário também é possível (atrair
  gente que quer o outro lado). Só a publicação mostra.

## 6. Lacunas

### Observado

1. **Duração.** Dos 52 vídeos com 50 mil visualizações ou mais nas buscas por grupo: 5 têm menos de 5 min (esquete de
   humor, peça publicitária, cortes curtos), **1 tem entre 5 e 8 min** (uma lista, "AS FAMÍLIAS MAIS RICAS DO
   BRASIL", 5:19, não um perfil de grupo), 19 têm 8–15 min, 21 têm 15–30 min e 6 passam de 30 min. Os perfis de 5–7 min
   encontrados têm pouca audiência: Mazukim 6:01 (7.123) e 6:10 (9.872), Lásaro do Carmo Júnior 6:55 (12.359),
   InvestNews 5:46 (1.662), Impérios de Sucesso 5:19 (144) e 6:04 (4).
2. **Fontes na descrição.** Das 29 descrições lidas: 4 nomeiam fontes como fontes (Curioso/Moreira Salles, Curioso/
   Odebrecht, Lado B/Odebrecht, Grandes Dinastias/Prado); 2 listam livros com link de compra sem chamá-los de fonte
   (Curioso/Safra, Jovens de Negócios/Lemann); 2 dizem que o vídeo se baseia em fontes sem nomear nenhuma (Imperio
   S.A/Votorantim, Reis do Capital/Votorantim); 1 cita um autor no resumo (Spotniks/famílias); **20 não falam de
   fonte**, incluindo as 3 do InvestNews, as 3 do Bastidores do Poder e a do Spotniks/JBS.
3. **Fontes na tela.** Nos 9 vídeos com storyboard, manchetes de jornal ou site aparecem como imagem em 4 (Curioso/
   Votorantim, Bastidores/Itaú, Spotniks/JBS, Maestria/Moreira Salles). Só no Maestria o veículo e o ano aparecem como
   rótulo legível ("O GLOBO (2025)"). Em nenhum quadro visto um número na tela ("R$ 54,1 bilhões em ativos", "R$ 4,7
   bilhões") tinha rótulo de fonte legível; a resolução não permite descartar texto pequeno. O Lado B remete à
   descrição num rodapé.
4. **Tom nos títulos.** Há títulos de exaltação ("A emocionante vida e trajetória de Jorge Paulo Lemann", "A INCRÍVEL
   VIDA DE JORGE PAULO LEMANN", "Antônio Ermírio: Construiu o IMPÉRIO Votorantim do Zero", "Como Antônio Ermírio de
   Moraes transformou a Votorantim num símbolo de sucesso no Brasil", "6 PILARES DE GESTÃO DE JORGE PAULO LEMANN QUE
   VOCÊ PODE APLICAR EM SEU NEGÓCIO"), de acusação ("A OBSCURA família que ENRIQUECE enquanto o Brasil ENFRAQUECE..",
   "Como uma Empresa Brasileira Comprou Governos Inteiros", "JBS • No Brasil o Crime Compensa?", "Banco Safra: O Império
   Bilionário da Família que lucra com os Juros no Brasil", "O SEGREDO OBSCURO DE JORGE PAULO LEMANN!") e de mecanismo
   ("O que os Safra compraram em Londres, Nova York e Boston", "O Family Office de R$54 bilhões dos donos do Itaú",
   "Votorantim pós-Antônio Ermírio: como o grupo quer investir um caixa de R$ 7,7 bilhões"). A descrição do vídeo
   dos novos Batistas (Bastidores) termina numa pergunta: "isso é eficiência ou concentração perigosa?". O Lado B abre
   com um cartão que recusa a homenagem.
5. **Recorte.** Nos vídeos sobre a Votorantim, a maioria dos títulos nomeia Antônio Ermírio; os que falam de
   "dinastia" (Reis do Capital, Impérios de Sucesso) ou de 1918 (Lado b do brasil) têm de 101 a 840 visualizações.
6. **Visual.** Três estilos convivem: apresentador em cena (Bastidores do Poder, InvestNews, Spotniks, Era uma vez
   Hoje); arquivo, recortes e logos sem apresentador (Curioso Mercado, Maestria); cenas fotorrealistas ou ilustradas
   (Imperio S.A, com texto deformado em placas; Lado B, em estilo 3D; Grandes Dinastias, em P&B e sépia). Gráficos de dados com eixo e mapas não
   apareceram nos quadros vistos; aparecem cartões de número, logos, uma linha do tempo simples (Bastidores), uma curva
   ilustrativa ("A reta agora é curva", Maestria) e telas de bolsa como B-roll.
7. **Produção em massa.** Legado Capital (971 vídeos desde abr/2026, 88.189 visualizações totais, 392 inscritos, dois
   vídeos por dia) e Reis do Capital (63 vídeos, 56.318 visualizações, narração e imagens de IA declaradas) cobrem
   quase todos os grupos da lista com audiência de dezenas a centenas de visualizações por vídeo.

### Inferência

- **A lacuna de formato é real, mas pode ser lacuna por um motivo.** Quase ninguém faz perfil de grupo em 5–7 min,
  e os poucos que fazem têm pouca audiência. Pode ser espaço vazio ou sinal de que o tema pede mais tempo (o próprio
  vídeo de referência do How Money Works tem ~21 min, segundo `modelo-perfil-de-poder.md`). Os dados daqui não
  separam as duas hipóteses.
- **Fonte na tela por número é rara.** Não achei nenhum concorrente que rotule cada número com a fonte; o mais perto é
  o cartão de manchete com veículo e ano do Maestria. É diferencial de credibilidade e de defesa (política de conteúdo
  inautêntico, risco jurídico com pessoas vivas), mas **nada indica que o público procure isso**: ninguém pediu fonte
  nos comentários. O que o público elogia é "pesquisa" e "qualidade", que é como a fonte chega a ele.
- **O tom documentado, sem herói nem vilão, é minoria nos títulos**, e os dois extremos têm audiência (exaltação:
  Lemann 1,9 mi em 2019; acusação: Maestria 166 mil). O Bastidores do Poder é o concorrente mais próximo em ângulo
  (mecanismo, ativos, família), mas não nomeia fontes nas descrições lidas.
- **Gráficos de dados e mapas** parecem subusados pelos concorrentes vistos, e são o ponto forte do template do
  projeto (`video/`, motion-kit). Com 9 vídeos no storyboard, é indício, não conclusão.
- **Canais de alto volume já ocupam os nomes dos grupos nas buscas.** Diferenciar por pesquisa e fonte não é só
  escolha editorial; é o que separa o projeto do tipo de canal que a política do YouTube descreve (§12 do
  `CLAUDE.md`), e esses canais têm pouca audiência por vídeo.

## 7. Conclusão

**Há espaço, mas estreito, e a incerteza é alta.**

- **Demanda: confirmada (observado).** Vídeos sobre esses grupos passam de 100 mil visualizações com frequência, a
  Votorantim teve três vídeos acima de 300 mil em ~14 meses, e canais novos no tema cresceram rápido em 2024–2026.
- **Oferta: grande e crescendo (observado).** Todos os dez grupos já têm pelo menos um vídeo; Curioso Mercado cobre
  sete; Safra, Marinho/Globo, Odebrecht e JBS estão cheios; canais de produção em massa ocupam os nomes nas buscas.
- **O que não achei (observado, com o limite das buscas feitas):** a combinação proposta, com 5–7 min, número com
  fonte na tela, tom documentado e o eixo "impacto hoje + como virou elite". Os concorrentes fazem um ou dois desses
  itens, não todos.
- **Risco principal (inferência):** a duração. O mercado observado premia 10–30 min; 5–7 min pode reter melhor em
  porcentagem e somar menos tempo de exibição. Isso só a publicação responde.

O que só a publicação real (§12: 4 vídeos, métricas aos 7 e 28 dias) pode responder:

1. Se o YouTube entrega impressões orgânicas a um vídeo de 5–7 min nesse tema, contra concorrentes de 15–45 min.
2. CTR de títulos neutros ("como", "o que", pergunta) contra os títulos polarizados que dominam as buscas.
3. Retenção nos 30 s iniciais com o gancho de impacto, e duração média de visualização.
4. Se a fonte na tela é notada (comentários espontâneos sobre pesquisa ou fonte) ou passa despercebida.
5. Como o público da Votorantim reage a um tom crítico e documentado, dado o vínculo afetivo observado.
6. Se aparecem pedidos espontâneos de novos temas, como nos comentários do Bastidores do Poder.

Sugestão para o registro das métricas: anotar a duração de cada vídeo e comparar com os números de referência
desta pesquisa, para separar "tema" de "formato" na decisão das 4 semanas. Decisão do dono.

## 8. Sugestões de pauta

Com base só no que foi observado aqui, ordenadas por demanda visível com pouca oferta no ângulo proposto:

| Grupo | Demanda observada | Oferta observada | Leitura |
|---|---|---|---|
| **Votorantim / Ermírio de Moraes** (piloto) | 3 vídeos acima de 300 mil em ~14 meses; autocompletar "familia ermirio de moraes"; pedido nominal em comentário com 142 curtidas | Biografia de Antônio Ermírio (35 min), notícia de caixa (12 min), história corporativa (35 min); ângulo de dinastia só em canais sem audiência | Manter. Diferencial: várias gerações, mecanismo e impacto hoje, curto e com fonte. Cuidado com o público afetivo (§5, item 7) |
| **Klabin** | 530 mil num vídeo de 2020; 59 mil em 2024; busca de investidor | Perfis de 2026 com até 12,7 mil (Gregorio Martins sobre Maurício Klabin, Lado B, The Final Quarter); fora dos perfis, Eva Klabin 33,9 mil | Boa candidata: demanda antiga, oferta recente de perfis fraca |
| **Gerdau** | 359 mil (2023) e 98 mil (2023) | Perfis de 2026 só de canais de alto volume (até 1,7 mil); vídeo de fábrica com 74,7 mil | Boa candidata pela empresa; o ângulo "família" não aparece no autocompletar |
| **Moreira Salles** | 278 mil, 244 mil e 166 mil desde 2024 | Recente e forte (Bastidores fez family office e nióbio; Maestria, versão acusatória; Curioso, histórica) | Possível, com concorrência direta do Bastidores |
| **Camargo Corrêa** | Baixa: máximo 45 mil (jornalístico) | Baixa: Imperio S.A 31 mil (57 min), resto pequeno | Incerta. Pouca oferta e pouca demanda visível; há disputa judicial entre herdeiros nos títulos de telejornal, o que pede revisão de risco |
| Safra, Marinho/Globo, Odebrecht, JBS/Batista, Lemann/3G | Alta | Alta e recente (Curioso, Spotniks, Era uma vez Hoje com temporada inteira, Bastidores, Lado B, Passo a Passo) | Evitar como primeiros episódios; entrar só com ângulo que os concorrentes não cobriram |

Pedidos vistos em comentários e **não pesquisados** nesta rodada: Fischer, Cutrale, Ometto, Maggi (o Bastidores já
fez Maggi, 177 mil, e Cosan, 64 mil), WEG, os "quatrocentões" e Matarazzo (o Grandes Dinastias já fez, 138 mil). Se
algum entrar na pauta, repetir esta checagem para ele.
