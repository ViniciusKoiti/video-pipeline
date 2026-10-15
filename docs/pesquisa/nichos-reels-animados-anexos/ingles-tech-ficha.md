> **Anexo de pesquisa bruta (2026-10-06).** Esta ficha foi escrita por um pesquisador antes da verificação independente e **contém itens depois corrigidos**: a taxa da Hotmart (vale 9,9% + R$ 2,49), as datas do guia do CONAR (vale 26/05/2026 e vigência em 1º de junho; 12 e 13 de maio só aparecem em terceiros), o mínimo da Cambly (US$ 30; o de US$ 50 foi refutado), o odômetro (já está dentro do plano `number`), e rótulos [F] fortes demais em paráfrases de legenda. Vale o que está em `docs/pesquisa/nichos-reels-animados.md` e em `verificacao.md`. Nenhum vídeo foi assistido.

# ingles-tech: inglês para entrevistas e rotina de profissionais de tecnologia (público BR, pt-BR com frases em inglês)

Consulta: **2026-10-06**. Ferramentas: WebSearch e WebFetch, que leem texto; **nenhum vídeo foi assistido** e nada abaixo descreve ritmo, cena, movimento, duração ou narração de vídeo. Tabela de evidências: `ingles-tech-evidencias.csv` (37 linhas, 24 colunas). Marcas: **(F)** fato observado, **(I)** inferência, **(H)** hipótese a testar. Emojis das bios foram omitidos nas citações.

## 0. Resumo

- **(F)** O micronicho existe e está ocupado: 4 perfis de Instagram verificados pela página (2 BR, 2 internacionais), todos com oferta paga; 3 declaram professor, engenheiro ou coaches nomeados e o quarto declara escala ("65.000+") e um time sem nomes. Há ainda plataformas grandes (DIO, Alura) e material gratuito direto (e-book da Cursa, phrasebook da Talaera, artigos da DIO, newsletter Na Gringa).
- **(F)** Os dois perfis brasileiros específicos de "inglês para devs" são pequenos ou quietos: `@devspeakacademy` (599 seguidores, 2 posts na janela de 90 dias) e `@inglespdevs` (8.011 seguidores, nenhum post visível depois de 2023-11-30). O perfil internacional ativo (`@english_for_it`, 43,4 mil) postou 9 vezes em 21 dias e seus 2 Reels abertos tinham 31 e 71 curtidas.
- **(F)** A promessa "uma situação por Reel, com frase pronta" já é usada por um concorrente brasileiro: Reel de 2026-09-30 do `@devspeakacademy` com uma pergunta de entrevista em inglês e um modelo de resposta, em série.
- **(I)** Os planos que existem hoje em retrato cobrem os 8 formatos de Reel mapeados (o #5 perde as duas vozes), mas 7 deles dependem de dois bloqueios próprios deste micronicho: narração em pt-BR **com frases em inglês** (o contrato fixa um idioma por episódio; nenhum dos dois TTS foi testado nisso; o Gemini não tem controle de pronúncia) e **autoridade** (os concorrentes verificados mostram professor, engenheiro, coaches nomeados ou escala; o canal teria voz sintética e personagem ilustrado). Só o formato #8 (dado de mercado) roda hoje sem mudança.
- **(I)** O PDF de frases disputa com material gratuito e com treino de entrevista por IA; a única evidência de preço de e-book é em USD e de um concorrente internacional (US$ 39,99 a 49,99).
- **Confiança: média** para o mapa de concorrência, ofertas e preços (páginas oficiais lidas); **baixa** para demanda, engajamento e conversão (3 Reels com curtidas, nenhuma visualização, nenhuma venda observável).
- **Leitura para decisão (I):** antes de gastar com o contrato bilíngue ou com o PDF, vale esgotar os testes baratos da seção 11: ouvir o Gemini com frases reais em inglês (uma chamada) e, se passar, publicar à mão 3 Reels-piloto dos formatos #2 ou #3 (só `keyword` e `broll`) com lista de espera, medindo o tempo humano. O dono decide; nenhum provedor externo foi chamado nesta pesquisa.

## 1. Método, limites e contagem de acessos ao Instagram

| Item | Resultado |
|---|---|
| Acessos ao domínio instagram.com (WebFetch) | **12 tentativas; 11 leituras e 1 falha** (limite do brief: 12). Perfis: `inglespdevs` x2, `devspeakacademy` x2, `speaktech.english` x2, `english_for_it` x2. Reels: 3 (um do `devspeakacademy`, dois do `english_for_it`). Falha: `rafamaiaingles` (12º acesso, "socket hang up"; não repeti) |
| Buscas com filtro instagram.com | Devolvem trechos indexados de data desconhecida; não abrem o perfil e não contam como acesso, mas dão só `trecho indexado` |
| Leitor de página | Modelo pequeno que resume o texto. **Inconsistências registradas:** `@devspeakacademy` (1ª leitura "posts de out/2024 e anteriores"; 3ª leitura listou 2026-09-30 e 2026-09-17), `@speaktech.english` (1ª leitura "datas de 2024-10 a 2026-10"; 2ª "sem datas nem legendas"), seguidores diferentes entre trecho indexado e página nos 4 perfis (ver CSV). Na dúvida, usei a leitura mais detalhada e marquei |
| Sem login, sem laço, sem contornar bloqueio | Cumprido. Nenhuma métrica foi estimada; "visualizações" não apareceu em nenhum Reel |
| Tipos de evidência no CSV | `descrição lida` (página do Instagram resumida pelo leitor), `site oficial` (página de oferta ou do programa), `trecho indexado` (resultado de busca, data desconhecida), `estatística de terceiros` (imprensa ou diretório). Nunca `vídeo assistido` |
| Colunas vazias | `duracao` é "indisponível" em todas as linhas (não assisti a vídeo); `uso_animacao_apresentador_demo` só tem valor quando uma página declarou algo |
| Fora do Instagram | Sites oficiais lidos (inglesparadevs.com.br, devspeak.com.br, english4it.online, speaktechenglish.com, cursa.app, DIO, Talaera, Cambly, Deel, EF). Bloqueados ou sem corpo: Alura (404), casado.dev (403), ComputerWeekly BR (403), italki (403/429), Preply (403), Udemy (403), Planalto (erro de conexão), central da Hotmart (corpo vazio), TecMundo/Estadão (bloqueado), YouTube "Fluência Nerd" (404) |
| Repositório | Planos e limites lidos em `docs/decisions/014-perfil-vertical.md`, `app/pipeline/schemas.py`, `app/pipeline/check.py`, `app/pipeline/text_fit.py`, `video/src/Editorial.tsx`, `app/providers/tts/*.py`, `config/providers.toml`, `data/benchmarks/termos-gemini-tts.md`. Os servidores MCP `motion-kit` e `browseros` não conectaram nesta sessão; o kit foi lido no disco (`video/node_modules/@viniciusk/motion-kit/src/COMPONENTS.md`) |

## 2. Perfis (2 brasileiros + 2 internacionais, verificados pela página em 2026-10-06)

| | **@inglespdevs** (BR) | **@devspeakacademy** (BR) | **@english_for_it** (internacional) | **@speaktech.english** (internacional) |
|---|---|---|---|---|
| URL | https://www.instagram.com/inglespdevs/ | https://www.instagram.com/devspeakacademy/ | https://www.instagram.com/english_for_it/ | https://www.instagram.com/speaktech.english/ |
| Mercado/idioma por evidência | pt-BR; preço em R$; checkout Hotmart; domínio .com.br | pt-BR; CNPJ no rodapé; Hotmart pt-br; domínio .com.br | Inglês; preço em USD; site em en, uk, es; bio "Europe - USA - LatAm - Worldwide". Audiência real não comprovada | Inglês; preço em USD; "Get hired worldwide". Audiência real não comprovada |
| Seguidores (2026-10-06) | 8.011 (148 seguindo). Trecho indexado: ~8.400 | 599 (2 seguindo). Trecho indexado: 543 | 43,4 mil (147 seguindo). Trecho indexado: 44K, 980 posts | 3.562 (1.857 seguindo). Trecho indexado: 3.615 |
| Tema e público | Inglês para programadores em carreira internacional | Inglês para desenvolvedores: entrevistas e vagas internacionais | Inglês para tecnologia, negócios e mídia digital | Inglês para entrevistas e trabalho em tecnologia, não nativos |
| CTA do perfil | "Curso Inglês Para Devs" + inglesparadevs.com.br | devspeak.com.br | "START HERE" + campsite.bio/english4it | "Subscribe + claim your FREE Interview English Starter Pack" + trythestack.co |
| Oferta e preço (página oficial) | Curso com 50h+, aulas particulares VIP 1x ou 2x por semana, correção de fala, modelos de documentos. **R$ 316/mês (1x), R$ 632/mês (2x), "12x R$ 158,08"**; duração do plano não declarada; garantia de 7 dias. https://inglesparadevs.com.br | Turmas de até 4 alunos, 2 aulas por semana, 52 módulos, comunidade; garantia de 7 dias e de 18 meses. **Preço não exibido** (formulário). https://devspeak.com.br ; Hotmart sem preço nem comissão visíveis | Teste de nível grátis; **English For Tech Lite US$ 20** (7 dias, autoestudo, sem aula ao vivo); cursos de 2 semanas a 2 meses (inclui Job Interview Crash Course); e-books (Interview Prep Workbook e outros) sem preço exibido. https://www.english4it.online/ | **E-books US$ 49,99 (Technical Interviews) e US$ 39,99 (Programmers); kit de CV US$ 9,99; curso de 50 frases US$ 14,99; flashcards US$ 4,99; bundle US$ 99,00.** https://speaktechenglish.com/courses/ |
| Autoridade declarada (não verificada) | Vitor: "professor de inglês e engenheiro de software há quase uma década"; Filipe: "professor de inglês há mais de 10 anos", "mais de 5 mil horas de aula"; bio "+800 alunos" | Victor Eloy: "Senior Software Engineer em Amsterdam na Holanda. Com mais de 13 anos de experiência na indústria de tecnologia"; "+ de 700 alunos" | "Trusted by 65,000+ tech professionals and companies worldwide" (site); destaque "Our Team" (sem nomes lidos) | "Native speakers", "British English", "10+ years ESL experience", "5+ years in tech (software & data)" (itens da lista do site, via leitor); "3000+" alunos; newsletter "45k+" |
| Atividade visível | Grade com posts de 2023-10-06 a 2023-11-30; **nenhum visível depois** | 12 posts listados; **2 nos últimos 90 dias** (2026-09-30 Reel, 2026-09-17 imagem repostada); 3 nos últimos 12 meses; lote de 8 em 2024-10-17/22 | **9 posts em 21 dias** (2026-09-16 a 2026-10-06): 6 Reels, 2 carrosséis, 1 imagem | Sem datas por post confiáveis (leituras inconsistentes) |
| Animação, apresentador, demonstração | indisponível | indisponível | indisponível nos vídeos | indisponível |
| Limitações | Legendas, curtidas, visualizações ocultas na grade | Idem; só 1 Reel aberto | Idem; 2 Reels abertos | Idem; nenhum post aberto (leitor não devolveu URLs) |

**Adjacentes só por trecho indexado, não verificados pela página:** `@rafamaiaingles` (Business English; 4.675 seguidores, 126 posts; bio "CELTA Cambridge | +1.200 alunos"; tentativa de abrir falhou) e `@inglescomtech` (8.144 seguidores; "aprenda inglês todos os dias, com tecnologia": a tecnologia parece ser o meio, não o público). Também apareceram sem abrir: `@theenglishcompany_` (inglês para mulheres de TI, em espanhol), `@_marcode_` (English for Engineers, Olivia Augustin), Talaera, SmallTalk2Me e EngVarta.

## 3. Amostras de publicações

### 3.1 `@english_for_it`: 9 posts consecutivos da grade (mais recente primeiro; o leitor devolveu 9 de até 12 pedidos)

| Data | Tipo (página) | URL | Texto alternativo automático ou legenda lida |
|---|---|---|---|
| 2026-10-06 | Reel | https://www.instagram.com/english_for_it/reel/DeJqMbNuzfZ/ | "May be a Twitter screenshot of one or more people and text" |
| 2026-10-05 | Carrossel | https://www.instagram.com/english_for_it/p/DeHgz_wDvR9/ | não lido |
| 2026-10-05 | Reel | https://www.instagram.com/english_for_it/reel/DeG5T_4ONNg/ | "May be an image of text" |
| 2026-10-02 | Reel | https://www.instagram.com/english_for_it/reel/Dd_EAnvgNtP/ | "May be a meme of dental floss and text" |
| 2026-09-30 | Carrossel | https://www.instagram.com/english_for_it/p/Dd6Mue9DpIY/ | não lido |
| 2026-09-23 | Reel | https://www.instagram.com/english_for_it/reel/DdoWNW_OVOX/ | "May be a video game screenshot" |
| 2026-09-19 | Reel (aberto) | https://www.instagram.com/english_for_it/reel/DdeEgxbOtFh/ | "The HR after hearing you don't speak English" |
| 2026-09-17 | Reel (aberto) | https://www.instagram.com/english_for_it/reel/DdYfZ72OXpt/ | "Don't make these mistakes" |
| 2026-09-16 | Imagem | https://www.instagram.com/english_for_it/p/DdWMNF0O1U1/ | não lido |

### 3.2 `@devspeakacademy`: 12 posts listados (critério: grade, mais recente primeiro)

2026-09-30 Reel (aberto, abaixo); 2026-09-17 imagem repostada de @matchoughost; 2026-03-20 imagem repostada de @victoreloy.dev; 2025-05-21 carrossel repostado de @victoreloy.dev; e 8 posts de 2024-10-17 a 2024-10-22 (3 Reels, 2 carrosséis, 3 imagens; URLs no CSV). **(F)** Cadência: lote de 8 posts em out/2024 e depois 4 posts em 23 meses (2025-05-21, 2026-03-20, 2026-09-17, 2026-09-30), 3 deles repostagens.

### 3.3 Reels individuais abertos (3 de 3 tentativas bem-sucedidas)

| Reel | Legenda lida | Data | Métricas visíveis |
|---|---|---|---|
| https://www.instagram.com/devspeakacademy/reel/Dd6tepnu8zz/ | Começa com: "'Where do you see yourself in five years?' Se essa pergunta te pega de surpresa numa entrevista em inglês, você não está sozinho..." (o leitor citou só o início e resumiu o resto: erros comuns e modelo de resposta; relata "Episode 1" de uma série com próximo episódio "Tell me about yourself"). Hashtags: #inglesparadevs #inglesparaprogramadores #entrevistaemingles #jobinterview #englishfordevs | 2026-09-30 | 5 curtidas; 0 comentários; visualizações não exibidas; áudio original |
| https://www.instagram.com/english_for_it/reel/DdYfZ72OXpt/ | "Follow @english_for_it for more English tips! Want to sound sharper in professional English? Our Business English course helps you fix mistakes like these and speak with real confidence at work. Follow the link in bio to sign up." | 2026-09-17 | 31 curtidas; 0 comentários; visualizações não exibidas; áudio original |
| https://www.instagram.com/english_for_it/reel/DdeEgxbOtFh/ | "That's what we work on in our English for Tech course. Improve your English to the level where you can build your career in English. Follow the link in bio" | 2026-09-19 | 71 curtidas; 2 comentários (1 visível: "or french" com 1 curtida); visualizações não exibidas; áudio de catálogo "Bonnie Tyler - Total Eclipse of the Heart" |

Aritmética sobre números observados (não é taxa de engajamento nem alcance): curtidas ÷ seguidores = 0,83% (`@devspeakacademy`), 0,07% e 0,16% (`@english_for_it`).

## 4. Fatos, inferências e hipóteses

**Fatos (com URL)**
1. Preços e condições: tabela da seção 2 (páginas oficiais listadas ali). E-book gratuito de 14 capítulos com STAR, vocabulário técnico, negociação salarial e e-mail de follow-up, "100% gratuito, do conteúdo ao certificado": https://cursa.app/pt/ebook-gratuito/ingles-para-entrevistas-de-emprego-respostas-storytelling-e-vocabulario-tecnico . Phrasebook gratuito de 55 frases de entrevista: https://www.talaera.com/lp/55-phrases-for-interviews-in-english/ .
2. DIO: English4Tech (A1 a B2, "entrevistas internacionais", pacote de GPTs de conversação), artigo de 2026-05-29, dentro do "DIO Global Vitalício", preço não informado: https://www.dio.me/articles/english4tech-como-funciona-o-curso-de-ingles-do-dio-global-064bca96239b . Artigo gratuito de 2024-07-15 com frases de exemplo: https://www.dio.me/articles/como-destravar-o-ingles-e-fazer-uma-entrevista-falando-o-idioma-do-inicio-ao-fim . Guia de 2025-01-21 com a alegação "salários aumentarem em até 70%" (fonte citada: Page Personnel): https://www.dio.me/articles/o-guia-definitivo-para-conquistar-sua-1a-vaga-internacional-que-paga-em-dolar-ou-euro-em-2025 .
3. Newsletter Na Gringa (2025-07-06): certificado não é exigido, clareza vale mais que gramática perfeita, simulações de entrevista de 15 minutos com IA: https://newsletter.nagringa.dev/p/ingles-pra-devs .
4. Contexto (não é demanda por Reels): EF EPI 2025, Brasil em 75º, nota 482 contra média global 488, leitura 516, escuta 468, fala 464, escrita 442 (ficha oficial, texto extraído do PDF): https://www.ef.com/assetscdn/WIBIwq6RdJvcD9bc8RMd/cefcom-epi-site/fact-sheets/2025/ef-epi-fact-sheet-brazil-english.pdf . Deel (2026-07-17): demanda global por profissionais brasileiros +53% em 2025, desenvolvedores de software o cargo mais demandado: https://www.deel.com/pt/blog/relatorio-contratar-talentos-no-brasil/ .
5. Gemini TTS: "The TTS models detect the input language automatically"; mistura de idiomas e controle de pronúncia "não mencionados"; página atualizada em 2026-10-01: https://ai.google.dev/gemini-api/docs/speech-generation . O adapter recusa glossário; limite observado de 3 chamadas por minuto e 10 por dia: `app/providers/tts/gemini.py`, `data/benchmarks/termos-gemini-tts.md`.

**Inferências**
- **(I)** Oferta madura e variada (aula ao vivo, curso, e-book, gratuito, IA) significa concorrência alta e preço de PDF pressionado para baixo.
- **(I)** Dois perfis brasileiros específicos pequenos ou quietos podem indicar espaço pouco disputado no Instagram em pt-BR **ou** pouca audiência/monetização ali; esta amostra não separa as duas leituras. A atividade dos brasileiros está em plataformas (DIO, Alura), newsletter e venda direta.
- **(I)** Autoridade é o diferencial que todos exibem; um canal sem rosto e com voz sintética começa em desvantagem para ensinar pronúncia.
- **(I)** O mecanismo "pergunta de entrevista em inglês + modelo de resposta, em série" já é usado no nicho, logo a promessa editorial é viável de produzir, mas não é diferenciada.

**Hipóteses a testar** (seção 11): H1 PDF de R$ 29 a 49 converte lista de espera; H2 formatos "diga isto / evite aquilo" geram mais salvamentos e compartilhamentos que explicação genérica; H3 o Gemini diz frases em inglês no meio de narração pt-BR de forma aceitável; H4 um revisor com credencial nomeado no canal compensa a voz sintética; H5 dá para sustentar 3 Reels por semana dentro das faixas da seção 8.

## 5. Cadeia

| Elo | Resposta | Estado da evidência |
|---|---|---|
| O vídeo atrai quem | Desenvolvedores e analistas brasileiros com leitura razoável e fala travada, perto de uma entrevista ou com reuniões em inglês | **(F)** a nota de fala do Brasil (464) é menor que a de leitura (516) no EF EPI 2025; **(F)** concorrentes miram exatamente esse público. **(H)** que o formato Reel os alcance |
| Essa pessoa precisa de quê | (1) Frase pronta para a situação do dia; (2) estrutura de resposta (STAR); (3) **prática falada com retorno**, que um PDF não entrega | **(F)** os concorrentes pagos vendem prática ao vivo (turmas de 4, aulas VIP) e a Na Gringa recomenda treino com IA |
| Qual produto ajuda | PDF de frases e modelos STAR (barato, imediato); aula particular ou prática com IA (retorno); curso | **(F)** e-book pago existe lá fora (US$ 39,99 a 49,99); **(F)** há e-book e phrasebook gratuitos |
| Por que compraria de nós | **Não estabelecido.** Candidatos: preço baixo e entrega imediata; explicação em pt-BR do "por quê" de cada frase para brasileiros; modelos para preencher (resolve a página em branco); série constante com fonte na tela | **(H)** todos. Sem credencial, o argumento de confiança é fraco |

## 6. Autoridade, concorrência, gratuitos, atendimento, manutenção, entrega

- **Autoridade necessária. (F)** 3 dos 4 perfis verificados declaram credencial pessoal (professor e engenheiro; engenheiro sênior em Amsterdam; coaches "native" com 10+ anos de ensino e 5+ em tecnologia) e o quarto declara escala e um time sem nomes (seção 2); tudo isso é alegação do vendedor, não verificada. **(I)** Para vender frases e correção de pronúncia, o público julga quem fala. Caminhos a testar: um revisor com credencial (ex.: certificação de professor) nomeado no canal; mostrar a fonte de cada afirmação na tela, o que o pipeline já faz no rodapé; posicionar como curadoria de fontes e não como professor. O custo e a aceitação de cada um são **desconhecidos**.
- **Concorrência paga. (F)** Brasil: Inglês Para Devs (R$ 316 a 632/mês), DevSpeak Academy (turmas de 4, sem preço público), DIO English4Tech, Alura Língua ("Inglês para Devs", página oficial 404, descrição só indexada), cursos da Udemy (preço do curso não lido; imprensa cita promoções "a partir de R$ 19,99" e "R$ 24,90", datas não verificadas). Fora: English For IT (Lite por US$ 20; outros cursos e e-books sem preço exibido), Speak Tech English (e-books e kits de US$ 4,99 a 49,99, bundle US$ 99), Talaera.
- **Alternativas gratuitas. (F)** E-book da Cursa; phrasebook da Talaera; artigos e eventos da DIO; newsletter Na Gringa; treino de entrevista com ChatGPT ou Claude; teste de nível grátis e "Starter Pack" grátis como isca dos concorrentes. **(I)** O piso de preço de um PDF de frases é zero; o diferencial tem de ser formato, especificidade ou confiança.
- **Atendimento. (I)** Um PDF gera perguntas do tipo "corrige minha resposta?": definir antes que não há correção individual (ou que é um serviço pago à parte). Reembolso: o Código de Defesa do Consumidor dá 7 dias para desistir de compra feita fora do estabelecimento (art. 49; texto lido em resumo de terceiros, o Planalto não respondeu); dois concorrentes verificados (inglesparadevs.com.br e devspeak.com.br) declaram garantia de 7 dias.
- **Manutenção. (I)** Frases e modelos são estáveis; revisar o PDF 1 a 2 vezes por ano e manter a biblioteca de fontes. Se houver afiliado, conferir os termos a cada mudança.
- **Entrega. (I)** Automática pela plataforma de checkout (a Hotmart cobra 9,9% + R$ 1,00 por venda aprovada e passa a R$ 2,49 fixos desde 2026-09-21, segundo https://tactus.com.br/taxas-da-hotmart-para-produtor/ , **terceiro, não conferido na página oficial**). Outras plataformas não foram pesquisadas.

## 7. Oferta própria simples e afiliado

**Oferta própria (ordem sugerida de teste, todas dependem de H1):**
1. **Lista de espera + "Starter Pack" de 5 frases** (gratuito): mede interesse antes de escrever o PDF; é o mesmo desenho de `@speaktech.english` (bio com "FREE Interview English Starter Pack" + newsletter).
2. **Templates de resposta STAR para devs** (PDF/Docs): 10 a 12 perguntas comportamentais com espaço para preencher, mais exemplos originais; contra o e-book gratuito da Cursa, vale só se for mais específico e mais curto.
3. **Banco de frases por situação** (apresentar projeto, pedir esclarecimento, discordar com educação, reportar problema, daily, code review): ~100 frases, cada uma com "diga isto / evite aquilo" e o porquê em pt-BR.
- **Faixa de preço a testar: R$ 29 a 49 (hipótese H1)**, ancorada em US$ 39,99 a 49,99 do concorrente internacional (**(F)** https://speaktechenglish.com/courses/ ) e em cursos da Udemy a partir de ~R$ 20 em promoção (**terceiro**). Não há preço de e-book brasileiro neste nicho lido.

**Afiliado (condições oficiais lidas em 2026-10-06):**
- **Cambly Ambassador:** "$30 per qualified conversion"; o indicado precisa "start a Cambly subscription and spend at least $30"; pagamento mensal por PayPal, Alipay ou conta aprovada; exige "an engaged audience"; limites por país não declarados. https://www.cambly.com/ambassador . **Divergência:** um trecho indexado dizia mínimo de US$ 50; confirmar na candidatura. Preço em USD tende a ser barreira para público brasileiro (**(H)**).
- **Alura BR:** programa na rede AWIN desde mar/2024 só em diretório de terceiros (https://www.affilitizer.com/programs/alura.com.br ); **comissão não verificada**.
- **Hotmart (produtos como o da DevSpeak):** um resumo de busca da central de ajuda diz que a comissão é definida pelo produtor e aparece na página do produto (a página da central não renderizou); a página do produto da DevSpeak não mostrou comissão; **não verificado**.
- **Preply e italki:** página oficial bloqueada (403/429); valores só em sites de terceiros; **não verificado**.
- Publicidade e afiliado exigem identificação clara: o Guia de Marketing e Publicidade por Influenciadores Digitais do CONAR é de maio de 2026 (a matéria do Meio & Mensagem é de 2026-05-13; um resumo indexado diz publicado em 12 e em vigor em 13 de maio, com efeitos desde 1º de junho; as fontes divergem em um dia) (https://www.meioemensagem.com.br/midia/conar-atualiza-guia-para-influenciadores-digitais ; o trecho sobre identificação "clara, ostensiva, imediata" e sobre afiliação e IA vem de resumo de terceiros, https://www.klalaw.com.br/conar-atualiza-guia-de-publicidade-com-influenciadores/ ; texto oficial do CONAR não lido).

## 8. Produção no pipeline de hoje (perfil retrato 9:16, ADR 014)

Planos aceitos em retrato: `photo`, `broll`, `number`, `keyword`, `stamp`, `lower_third`, `compare` (side, before_after, scale) e `chart` (bar, bar_horizontal, line, share) (`PORTRAIT_SHOT_KINDS` em `app/pipeline/schemas.py`). Limites que pesam aqui: `keyword` aceita **no máximo 8 palavras** (erro de validação acima disso) e o `vp check` alerta quando há mais de 1 por cena; `number`, `compare`, `chart`, `stamp` e `lower_third` são planos factuais e **exigem `claims` com `source_ids`**; os limites de texto do `vp check` (`text_fit.py`) foram medidos em paisagem, o `value` do `compare` (onde iria a frase) não tem limite e nenhum foi medido para o retrato; há alerta para tarja sem foto ou B-roll por baixo, para mais de 4 planos gráficos seguidos e para o mesmo tipo duas vezes seguidas; ritmo de 2 a 4 s por plano, com `compare` e `chart` em pelo menos 4 s (skill `roteiro-explicativo`).

### 8.1 Formatos de Reel de 20 a 45 s e o que cada um pede

| # | Formato | Planos que existem hoje (retrato) | Adaptação ou dependência |
|---|---|---|---|
| 1 | **Diga isto / evite aquilo** (1 situação, 30 a 40 s) | `keyword` com a situação sobre `broll` de reunião; `compare` side com o texto errado e o certo; `keyword` final com a frase pronta (`highlight`) | `compare` foi feito para números: sem número cai num ramo de texto (valor 64 px, rótulo 30 px, colunas empilhadas), **não testado com frase longa**. Dígito nas duas frases aciona o ramo numérico (contagem animada): evitar números. `compare` exige `claims` (fonte do "evite") e o ramo de texto não tem ícone de certo/errado. Narração bilíngue (seção 9) |
| 2 | **A mesma frase em 3 níveis de formalidade** (25 a 35 s) | 3 cenas, cada uma com `keyword` sobre `broll` ou `photo`, alternando para não repetir o tipo | Sem código novo. Frases de até 8 palavras. A escala de formalidade pede fonte de uso (dicionário ou guia de estilo) |
| 3 | **Resposta STAR em 4 passos** (40 a 45 s) | `number` ("4" + "passos do método STAR", com claim), 4 cenas com `keyword` e `broll` | Não existe diagrama de passos em retrato (o componente `pipeline` do kit não está ligado a plano; rede e linha do tempo fora do retrato). Fonte para o método STAR (guia de RH ou de contratação). Exemplos originais |
| 4 | **Antes e depois** (resposta fraca para forte, 30 a 40 s) | `compare` `before_after` com texto; `keyword` final | Como o #1. "Forte" e "fraca" são julgamento editorial: exige critério com fonte e revisor de inglês. Risco alto de opinião sem fonte |
| 5 | **Mini-diálogo de reunião** (daily, code review, incidente; 35 a 45 s) | `keyword` por fala (1 por cena), `lower_third` com o papel sobre `broll` | **Duas vozes não existem** (uma voz por idioma e por episódio). `lower_third` é "nome e cargo" factual (exige claims). O kit tem `CodeBlock`, `CodeWalkthrough` e `TerminalWindow` para mostrar comentário de code review, mas **não estão ligados a planos** (props vistas só na lista do `COMPONENTS.md`) |
| 6 | **Cinco termos para uma situação** (bug, incidente, deploy; 35 a 45 s) | `number` ("5" + rótulo), 5 cenas com `keyword`, `broll` | Siglas e termos (SQL, nginx, Kubernetes) dependem de pronúncia sem glossário no Gemini; o Kokoro aceita fonemas. 5 `keyword` seguidos disparam alertas de repetição: intercalar `broll` |
| 7 | **Erro comum de brasileiro** (falso cognato, tradução literal; 20 a 35 s) | `compare` `before_after` (errado para certo), `keyword`, `photo` | Como o #1. A afirmação "erro comum de falantes de português" exige fonte. Espaço saturado de professores generalistas (perfis de 2 milhões de seguidores apareceram na busca) |
| 8 | **Dado de mercado como isca** (inglês e carreira; 20 a 30 s) | `number` ("75º" e "posição do Brasil no EF EPI 2025"), `chart` `bar_horizontal` ou `compare` `scale`, `photo` | Nenhuma: é o que o pipeline já faz melhor. Fontes oficiais (EF, Deel). Não ensina frase e leva menos direto à oferta (**H**); "salário +70%" só com fonte primária |

### 8.2 Dependências

- **Filmagem:** nenhuma. **Demonstração de produto:** nenhuma; a capa do PDF entra como `photo` de ativo `Original`. **Consistência de personagem:** o apresentador Notionists (CC0, janela flutuante) é opcional; a boca acompanha o áudio, não há pessoa em câmera.
- **Pesquisa complexa:** moderada. É preciso uma **biblioteca de fontes de idioma** baixada e numerada (dicionários têm termos de uso a conferir; o guia de estilo de documentação para desenvolvedores do Google está sob CC BY 4.0, atualizado em 2026-04-27: https://developers.google.com/style ) e uma decisão de política: o pipeline exige `claims` com fonte para tudo o que a narração e a tela afirmam, e conselho de uso do idioma ("diga isto") não é fato de fonte histórica. **(I)** Os tipos de fonte aceitos (`SourceKind`: primary, secondary, newspaper, archive) parecem pensados para história.
- **Licença de ativos:** foto e B-roll de banco são ilustração (§2.4), sem pessoa reconhecível, marca, logo ou texto (§8); código na tela só original; sem música nem áudio de tendência (o Reel de 2026-09-19 do `@english_for_it` usa música de catálogo, que este pipeline não tem).

### 8.3 Custos, com premissas e intervalos

| Item | Setup (uma vez) | Recorrente (por Reel) | Premissa e origem do número |
|---|---|---|---|
| **API** | US$ 0 | US$ 0 | Camadas gratuitas, regra §2.1. Gemini TTS: 10 chamadas por dia e 3 por minuto (observado em 2026-09-30, `termos-gemini-tts.md`); texto e áudio podem ser usados pelo Google |
| **Contrato bilíngue** (idioma por cena ou marcador de trecho em inglês, com ADR, schema, adapters e testes) | ~3 a 6 dias de trabalho (**estimativa sem medição**) | 0 | `episode.json` só muda com nova ADR (CLAUDE.md §6); hoje `SpeechRequest(language=scenes.language)` vale para o episódio inteiro |
| **Skill e fontes de idioma** | Horas a 1 a 2 dias (**estimativa**) | Incluído abaixo | Skills atuais são de documentário e finanças |
| **Agentes (roteiro, checagem)** | n/a | **~0,3 a 0,8 milhão de tokens e ~20 a 45 min por Reel (estimativa)** | Escala linear a partir da medição de ~1,6 milhão de tokens e ~1 h 31 para 93 s, com 5 rodadas de checagem (`data/benchmarks/episodio-votorantim-dinheiro.md`), aplicada a 20 a 45 s. **Não medido neste nicho**; os tokens são piso. A 3 Reels por semana: ~1 a 2,4 milhões de tokens e ~1 a 2,3 h de agentes |
| **Voz** | n/a | Kokoro: ~15 a 32 s de síntese (0,7 s por segundo de áudio, brief). Gemini: 1 chamada de ~20 s por Reel de até ~1.200 caracteres | Qualidade das frases em inglês **não testada** (seção 9) |
| **Render** | n/a | ~40 a 110 s na prévia 720x1280 (medido num curto de ~55 s, uma sessão, não benchmark); final 1080x1920 **não medido** | Um render por vez; sonda de CPU antes |
| **Tempo humano** | Oferta (PDF): ~12 a 20 h de redação, revisão de inglês e diagramação (**estimativa**; não há ferramenta de diagramação no repositório) | Gates 1 a 4 + revisão de pronúncia + legendas + título, capa, hashtags e upload manuais: **não medido**; faixa de planejamento a validar nos 3 primeiros Reels: 30 a 90 min (**hipótese**) | Não existem export por plataforma, título, capa nem upload no pipeline |
| **Taxa de venda** | n/a | Hotmart: 9,9% + R$ 1,00 (terceiro, ver seção 6) | Não conferido na página oficial |

## 9. Pronúncia e TTS: o que este micronicho exige

- **(F)** O contrato fixa **um idioma por episódio** (`scenes.json` `language`, `en` ou `pt-BR`), e a voz é escolhida por idioma. Frases em inglês dentro de narração pt-BR seriam lidas pela voz pt-BR.
- **(F) Kokoro:** um `KPipeline` por idioma (`pt-BR` usa o código `p`, `en` usa `a`); aceita fonemas por termo (`[termo](/fonemas/)`); o adapter processa a cena inteira num idioma só e só concatena trechos nas pausas (ADR 015). **(I)** Misturar exigiria dividir a cena por trecho, usar duas vozes e concatenar.
- **(F) Gemini TTS:** detecta o idioma sozinho, não tem parâmetro de idioma nem de sotaque, não tem glossário de pronúncia (o adapter recusa um) e a **direção de fala configurada pede "sotaque brasileiro"** (`config/providers.toml`). **(H)** Essa direção pode valer também para as frases em inglês. **(I)** Uma chamada por Reel cabe na cota, mas um lote só aceita uma voz e um idioma; trocar de voz no meio custa chamadas (limite observado: 10 por dia).
- **(I)** O pipeline precisaria de: idioma ou voz por cena (ou marcador de trecho em inglês, como a `<short pause>`, ADR 015), um teste cego com frases reais, glossário de fonemas para termos técnicos no Kokoro e, se o Gemini ficar, uma direção de fala sem sotaque brasileiro para os trechos em inglês.
- **(H)** Revisão de pronúncia por alguém fluente em **todo** Reel antes do gate 4; sem ela, um erro de pronúncia num canal que ensina pronúncia custa a credibilidade.
- **(F)** Nota: o dono achou o Kokoro "sintético demais" em pt-BR (ADR 012), e esse é o TTS sem limite diário.

## 10. Precisão e risco

- **Exige fonte oficial:** estatísticas (EF EPI, Deel, "salário +70%"); processos de entrevista de empresas (páginas de carreira); uso do idioma (dicionário e guia de estilo, duas fontes independentes); definição do STAR; condições de afiliado; preços de concorrentes.
- **Promessa de renda e emprego:** é o risco central. Concorrentes usam "vagas em dólar", "salário até 70% maior" e "garantia de 18 meses, 100% de volta". Para o canal: não prometer vaga, salário nem prazo; o produto é material de estudo. **(I)** Isso é discurso de risco para publicidade enganosa; texto legal específico **não verificado**.
- **Regulatório:** identificação de publicidade e afiliado (CONAR 2026); direito de arrependimento de 7 dias (CDC art. 49); dados de lista de e-mail (LGPD, **não pesquisado**). Saúde: não se aplica.
- **Direitos:** não copiar os phrasebooks dos concorrentes; frases comuns são livres, compilações não; dicionários têm termos de uso; stock como ilustração; nenhum áudio de tendência; divulgar que a narração é sintética (política do Google em `termos-gemini-tts.md`).
- **Qualidade do inglês:** erro de uso numa frase "pronta" é erro de produto. Exige revisão humana fluente e a regra de duas fontes para o "evite".

## 11. Evidência que falta antes de investir mais

1. **Visualizações, salvamentos, compartilhamentos e cliques** de Reels do nicho: indisponíveis para terceiros. Piloto próprio de 6 a 8 Reels em 3 semanas, com limites de decisão definidos antes.
2. **Mais perfis brasileiros:** a amostra tem 2 verificados (1 sem posts depois de 2023, 1 esparso) e 1 tentativa falha. Coleta manual do dono, logado, em 10 a 15 perfis, sem raspagem.
3. **Disposição a pagar por PDF no Brasil:** lista de espera e pré-venda a R$ 29 a 49; medir cliques, cadastros e compras. Não há preço de e-book brasileiro neste nicho lido.
4. **Teste cego do TTS bilíngue** (Kokoro e Gemini) com 6 a 10 frases reais e 5 a 10 desenvolvedores brasileiros mais um professor de inglês; definir o limite de aceite antes. O Gemini já recebe o texto ao pé da letra e detecta o idioma, então a primeira escuta cabe numa chamada sem mudar código; o `scripts/provisorio/teste_voz_gemini.py` usa falas fixas do vídeo-régua e precisaria de ajuste, e chamar o Gemini exige pedido do dono na sessão (CLAUDE.md §14).
5. **Autoridade:** reação a canal sem rosto; custo e disponibilidade de um revisor com credencial.
6. **Afiliado:** confirmar o mínimo da Cambly (US$ 30 ou 50) e se aceita criadores do Brasil; ler Preply, italki e Alura (AWIN) logado; comissão por produto na Hotmart.
7. **Tempo humano real por Reel** (3 Reels-piloto) e render final 1080x1920.
8. **Política de claims para conteúdo de idioma:** decidir (ADR) o que conta como fonte para "diga isto / evite aquilo" antes de produzir em escala.
9. **Atualidade dos dois perfis brasileiros:** confirmar fora do Instagram (YouTube, site) se `@inglespdevs` continua ativo; a leitura de 2023 não prova inatividade.

## 12. Fontes (consulta em 2026-10-06, salvo indicação)

- Instagram: perfis e Reels citados nas seções 2 e 3.
- Sites oficiais: https://inglesparadevs.com.br ; https://devspeak.com.br ; https://hotmart.com/pt-br/marketplace/produtos/devspeak/P82274522X ; https://www.english4it.online/ ; https://www.english4it.online/english-for-tech-lite ; https://campsite.bio/english4it ; https://speaktechenglish.com/ ; https://speaktechenglish.com/courses/ ; https://trythestack.co ; https://peerpush.com/p/speak-tech-english ; https://cursa.app/pt/ebook-gratuito/ingles-para-entrevistas-de-emprego-respostas-storytelling-e-vocabulario-tecnico ; https://www.talaera.com/lp/55-phrases-for-interviews-in-english/ ; https://www.cambly.com/ambassador ; https://developers.google.com/style ; https://ai.google.dev/gemini-api/docs/speech-generation .
- DIO e newsletter: ver seção 4. Estatísticas: EF e Deel (seção 4).
- Terceiros (secundários): https://tactus.com.br/taxas-da-hotmart-para-produtor/ ; https://www.affilitizer.com/programs/alura.com.br ; https://www.meioemensagem.com.br/midia/conar-atualiza-guia-para-influenciadores-digitais ; resultados de busca para o texto do art. 49 do CDC (https://www.planalto.gov.br/ccivil_03/leis/l8078compilado.htm não abriu).
- Repositório: `docs/decisions/008`, `012`, `014`, `015`; `app/pipeline/schemas.py`; `app/pipeline/check.py`; `app/pipeline/text_fit.py`; `video/src/Editorial.tsx`; `app/providers/tts/gemini.py` e `kokoro.py`; `config/providers.toml`; `data/benchmarks/episodio-votorantim-dinheiro.md`; `data/benchmarks/termos-gemini-tts.md`.
