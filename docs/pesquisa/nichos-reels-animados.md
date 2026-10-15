# Nichos para Reels animados e venda de produtos: pesquisa e plano de teste

- **Consulta:** 2026-10-06. **Janela de demanda atual:** publicações de 2026-07-08 a 2026-10-06 (90 dias). O que é mais antigo só mostra linguagem visual e não prova demanda.
- **Repositório lido em:** `d1757d6` (branch `retrato-comparacao-abaixo-da-janela`), com `video/src/Editorial.tsx` e `scripts/provisorio/baixar_fonte.py` modificados e não commitados.
- **Quem fez:** o coordenador (Claude Code), quatro pesquisadores (um por finalista) e um verificador independente, todos agentes do plano do dono (ADR 009). Não houve conta criada, publicação, provedor pago nem raspagem.
- **Estado:** análise e plano. **Aprovação, escolha do nicho e publicação são do dono.**
- **Arquivos:** este relatório; `docs/pesquisa/evidencias-nichos-reels.csv` (301 linhas, 25 colunas, a última com o resultado da verificação independente); anexos em `docs/pesquisa/nichos-reels-animados-anexos/` (quatro fichas de pesquisa e o relatório do verificador).

## 0. Como ler, e o que esta pesquisa não é

- **[F]** fato observado, com URL; **[I]** inferência; **[H]** hipótese a testar. As notas de 1 a 5 são julgamentos comparativos, não probabilidades de sucesso.
- **Nenhum vídeo foi assistido.** Nada aqui descreve ritmo, cena, movimento, duração ou qualidade de um vídeo concorrente. A evidência é bio, legenda, texto alternativo automático do Instagram, páginas de oferta e sites oficiais.
- **Instagram:** só páginas públicas, lidas por um leitor que resume a página com um modelo pequeno (12 acessos por pesquisador e 10 do verificador, 58 no total, sem login e sem contornar bloqueio). Aparecem seguidores, bio, tipo e data dos itens da grade; **visualizações, retenção e salvamentos por Reel não aparecem**. Foram abertas 10 páginas de Reel e 2 de post de imagem, com curtidas e comentários. Métrica oculta é "indisponível"; nada foi estimado.
- **Busca:** o orçamento de 200 buscas da sessão, compartilhado entre os agentes, esgotou durante a pesquisa. A descoberta de perfis brasileiros de system design e de criadores brasileiros que usam animação ficou incompleta.
- **A amostra é exploratória e não representa o mercado:** 16 perfis principais (4 por finalista, 2 brasileiros e 2 internacionais) e cerca de 24 de contexto. "Existe oferta" não é "vende": uma página de checkout não revela faturamento, conversão nem rentabilidade.
- **Datas:** a data da consulta (2026-10-06) vem separada da data de publicação. Conferi as datas de 168 posts pelo código do endereço do post: 162 batem e 6 diferem 1 dia (fuso).
- **Custos de agentes e de tempo humano são extrapolações** (seção 2.4). Só o episódio Votorantim e algumas rodadas desta sessão foram medidos.

## 1. Resposta executiva

| Pergunta | Resposta |
|---|---|
| **Qual nicho começar** | **MEI e pequenos prestadores: preço, caixa e limite** ("quanto cobrar e quanto sobra, com número oficial e data"). **Reserva:** system design e entrevistas técnicas, sob duas condições (seção 6.B). Ficam de fora desta rodada: inglês para tecnologia e economia do cotidiano. |
| **Para qual público** | Brasileiros que vendem produto ou serviço por conta própria, MEI ou a caminho de abrir. O recorte ainda precisa de calibragem: o Anexo XI do Simples Nacional mistura ocupações manuais (cabeleireiro, eletricista, confeiteiro) com editor de vídeo independente, instrutor de idiomas, instrutor de informática, professor particular e fotógrafo; não achei designer, programador nem consultor na lista [F]. |
| **Em qual mercado** | Brasil, pt-BR. O inglês fica para depois: nenhuma evidência desta rodada mostra audiência fora do Brasil (um perfil em inglês não comprova público nos EUA). |
| **Com qual formato animado** | Reel vertical de 25 a 40 s, um número ou uma regra oficial por vídeo, com fonte e data na tela. Planos que já existem no retrato: `keyword`, `number` (com odômetro), `compare`, `chart` e `stamp`; apresentador ilustrado opcional. Sem filmagem e sem demonstração de produto. |
| **Vendendo o quê** | Em degraus: (1) isca gratuita por comentário-chave, uma calculadora de hora técnica em planilha; (2) lista de espera da planilha "preço, caixa e limite (2026)" com mini e-book; (3) só depois, afiliado (o Bling paga 10% no primeiro ano, mas exige CNPJ). Faixa de preço de teste: R$ 27, R$ 47 e R$ 67 (hipótese, seção 7.4). |
| **Que evidência falta antes de investir mais** | Alcance e retenção reais por Reel; disposição a pagar por algo que existe grátis; qual público responde (prestador manual ou quem presta serviço de conhecimento); regras tributárias e a fronteira com consultoria contábil, conferidas por um profissional (IR do MEI, estrutura fiscal de quem vende); condições de afiliado para criador; horas humanas e tokens reais por Reel (seção 10). |
| **Confiança** | **Média** nos fatos oficiais e no mapa de concorrentes; **baixa** em demanda, conversão e preço. O ranking é provisório. |

**Por que esta decisão, e o que a sustenta**

1. **Produz hoje.** Os 8 formatos de Reel mapeados para o MEI cabem nos 8 planos do retrato, sem engenharia nova (ADR 014; seção 6.A). O melhor concorrente em evidência de mercado (system design) depende de um diagrama que não existe em retrato.
2. **O elo vídeo → produto é direto e testável sem custo.** O Reel mostra a conta ("quanto cobrar") e a planilha faz a mesma conta; a isca gratuita e a lista de espera custam quase zero.
3. **Menor barreira de autoridade e de regulação entre os finalistas.** O conteúdo é número oficial com fonte e data, não conselho individual nem recomendação de investimento (o ponto sensível da CVM não entra; a fronteira com consultoria contábil precisa ser confirmada por um contador).
4. **Empate técnico no topo.** Com os pesos pedidos, MEI soma 3,35 e system design 3,25. A diferença é menor do que a incerteza: uma mudança de ±1 numa única nota troca a ordem. O que é estável é a distância para os dois últimos (0,7 ponto). Escolho o MEI por produzir hoje e por exigir menos autoridade; se o dono tiver credencial técnica verificável, o system design pode passar à frente (seção 4.4).
5. **O MEI tem fraquezas reais [F]:** existe grátis (Sebrae, InfinitePay, Contabilizei, Freela Sem Crise, MEiSHOP); nenhuma venda foi observável; os números oficiais mudam (DAS em janeiro, projetos de lei de limite em tramitação, quatro valores diferentes em fontes oficiais).

## 2. Capacidades da pipeline hoje (etapa 1; lido no repositório)

### 2.1 O que existe

| Item | Estado | Onde conferir |
|---|---|---|
| Motor do formato `explainer` | Remotion + `@viniciusk/motion-kit` (pin `527c708`) | `video/package.json`, ADR 001 e 008 |
| Tipos de plano no template | 13: photo, broll, number, quote, stamp, lower_third, chart, timeline, family_tree, map, compare, network, keyword | `video/src/ShotView.tsx` l. 123-158 |
| **Perfil vertical 9:16** | Só 8 planos: **photo, broll, number, keyword, stamp, lower_third, compare, chart** | `app/pipeline/schemas.py` l. 506-508; ADR 014 |
| Fora do retrato | rede, mapa, linha do tempo, árvore, cartão de documento (e `quote`); também música, export por plataforma, título e capa | ADR 014 l. 53 |
| Peças do kit já ligadas ao template | Odômetro (dentro do plano `number`), BarChart, LineChart, ShareChart, ValueCompare, YearTimeline, DateStamp, LowerThird, SourceTag, KineticHeadline, DocumentPage, ArchivalPhoto, GeoMap, ExpandingNetwork, FloatingWindow e Host, FootageBackground e ImageBackground, CameraRig | `video/src/Editorial.tsx`, `HostWindow.tsx`, `Scene.tsx` (imports) |
| Peças do kit **sem plano** | Pipeline (esteira "estilo ByteByteGo em 9:16"), Gauge, CodeWalkthrough, CodeBlock, ContextWindow, AnimatedGraph, Highlighter | `~/projetos/motion-kit/src/COMPONENTS.md`; ausentes em `video/src` |
| Limites de texto | `keyword` com no máximo 8 palavras (`KEYWORD_MAX_WORDS = 8`) e alerta para mais de 1 por cena; gráfico e comparação com pelo menos 4 s; 2 a 4 s por plano; alerta para mais de 4 planos gráficos seguidos e para o mesmo tipo duas vezes | `schemas.py` l. 454; `app/pipeline/check.py`; skill `roteiro-explicativo` |
| Fatos e fontes | Planos factuais exigem `claims` com fonte; a tela **não calcula** razão, soma nem converte moeda que não esteja numa ficha | ADR 011 decisão 7 |
| Apresentador | Personagem ilustrado (Notionists, CC0) em janela flutuante; não é pessoa em câmera | ADR 013; `HostWindow.tsx` |
| Retrato final | Legenda queimada; área segura (topo 288, base 500) | ADR 014; `Scene.tsx` |
| Voz | Kokoro nos rascunhos; Gemini TTS Charon no vídeo final (ADR 012 ainda **proposta**); um idioma por episódio; o adapter do Gemini recusa glossário de pronúncia | ADR 012; `app/providers/tts/gemini.py` |
| Cota do Gemini (camada gratuita) | 3 chamadas por minuto e 10 por dia (observadas); na camada gratuita o Google pode usar o conteúdo para melhorar produtos | `data/benchmarks/termos-gemini-tts.md` |
| Etapas criativas | Agentes `pesquisador`, `roteirista`, `verificador` + `vp check` + gates por comando (`vp approve`, `vp status`) | `.claude/agents/`, ADR 009 |
| Licença do Remotion | Grátis para pessoas e empresas com fins lucrativos de até 3 pessoas, **contando freelancers e agências no mesmo projeto**; uso comercial e automação permitidos; acima disso, Company License paga | https://github.com/remotion-dev/remotion/blob/main/LICENSE.md ; https://www.remotion.pro/license (conferidas pelo verificador) |

### 2.2 O que não existe (e pesa em Reels)

- **Comandos `vp`:** `new`, `reopen`, `sources`, `script`, `scenes`, `assets`, `gallery`, `voice`, `subs`, `render` e `export` ainda não respondem (CLAUDE.md §10); scripts em `scripts/provisorio/` cobrem fonte, voz e render.
- **Pacote de publicação:** nada gera `captions.srt`, `credits.txt`, `description.txt`, título, capa, legenda de postagem, hashtags, export por plataforma nem upload (`docs/ANALISE.md`, item 23). A publicação é sempre manual, depois da revisão humana (CLAUDE.md §1).
- **Validade de ficha:** o contrato guarda `retrieved_at`, mas não data de revisão nem versão da fonte. Para números que mudam (DAS, quotas, limite do MEI), a retirada de um Reel velho é manual.
- **Número hipotético:** não há "ficha de exemplo" para uma conta de exemplo na tela; ela exigiria uma decisão (ADR).
- **Idioma por trecho:** o contrato fixa um idioma por episódio. Narração em pt-BR com frases em inglês exigiria mudança de contrato.
- **Gravação de tela e demonstração de produto:** não existem; uma planilha, um app ou um template só entram como imagem estática (ativo `Original`).
- **Ferramentas de venda:** página de captura, lista de e-mail, entrega de PDF e planilha, analytics por Reel e checkout ficam fora do repositório (serviços gratuitos a conferir).

### 2.3 Divergências entre os documentos (resolvidas pelo código e pelas ADRs)

- **`AGENTS.md` não existe** na raiz; `CLAUDE.md` é a referência.
- **`docs/spec-v0.4.md` é um marcador "PENDENTE"** (8 linhas), embora o `CLAUDE.md` o declare fonte de verdade. Usei o código e as ADRs.
- `CLAUDE.md` §1 ainda cita o recorte de expedições e perfis de poder; `docs/ANALISE.md` item 18 pede uma ADR do recorte quando o dono decidir. **Esta pesquisa não muda o recorte**; se o dono adotar o MEI, registrar numa ADR.

### 2.4 Custos medidos e o que é extrapolação

| Dado | Valor | Origem |
|---|---|---|
| Episódio `votorantim-dinheiro` (93,1 s, 10 cenas, 21 planos) | ~1,6 milhão de tokens e ~1 h 31 de agentes, com 5 rodadas de checagem (o verificador foi ~944 mil tokens); a 1ª rodada reprovou 5 de 20 frases e 6 de 27 planos; **horas humanas não medidas** | `data/benchmarks/episodio-votorantim-dinheiro.md` [F] |
| Voz Kokoro | ~0,70 s de síntese por segundo de áudio no benchmark da Fase 0 (inglês); ~0,9 no vídeo-régua em pt-BR (84 s para um vídeo de 93 s) | `data/benchmarks/README.md`; verificador [F] |
| Render do vídeo-régua | 180 s (prévia 720p, paisagem) | `data/benchmarks/episodio-votorantim-dinheiro.md` [F] |
| Prévia 720×1280 de curtos de ~50 a 64 s, **medida nesta sessão em 2026-10-06** (máquina livre, sonda de CPU 0,04 a 0,06 s; não registrada em `data/benchmarks`) | 41 s (cache parcial), 79 a 122 s (cache frio, Kokoro) e 351 s (cache frio depois de trocar para a voz do Gemini); a causa da diferença não foi investigada | logs desta sessão [F, não reproduzido] |
| Voz final Gemini nesta sessão | 424 s para 6 cenas (uma chamada por cena, porque o lote foi recusado com pausas internas) | log desta sessão [F]; na prática **1 a 2 Reels por dia** na cota gratuita |
| Render final 1080×1920 | **não medido** | — |
| Custo por Reel de 25 a 40 s | 0,15 a 0,8 milhão de tokens e 10 a 45 min de agentes; 20 a 90 min humanos; render da prévia de ~20 s a ~3 min | **[H]** escala linear sobre o Votorantim e sobre as medições desta sessão; as fichas dos pesquisadores usaram premissas diferentes e não são comparáveis entre si |

### 2.5 Trabalho necessário para Reels (por prioridade)

| # | Item | Por quê | Esforço [I, por analogia com PRs anteriores] | Bloqueia o ciclo de 14 dias? |
|---|---|---|---|---|
| 1 | Título, capa, legenda de postagem e hashtags por Reel | não existem no pipeline | 10 a 20 min por Reel, manual | Não (manual) |
| 2 | Política de ficha de exemplo hipotético | para "quanto sobra no mês" com conta de exemplo | 1 ADR + skill + check, 1 a 2 dias | Não (o ciclo evita exemplos hipotéticos) |
| 3 | Validade e revisão de ficha | DAS muda em janeiro; PLP em tramitação | pequeno a médio | Não, mas necessário antes de escalar |
| 4 | Legenda de ilustração sem claim | o ano da foto não aparece na tela | pequeno | Não |
| 5 | Esteira (`pipeline`) ou rede em retrato | só para system design | esteira 1 a 2 dias; rede com nós de software 2 a 4 dias; diagrama completo 1 a 2 semanas (baixa confiança) | Não (o ciclo usa os formatos sem diagrama) |
| 6 | Contrato bilíngue | só para inglês para tecnologia | 3 a 6 dias | n/a |
| 7 | Importador de séries oficiais (SGS, SIDRA) | só para economia | médio | n/a |
| 8 | Serviços externos: lista de e-mail, isca, rastreio de cliques por Reel | setup do ciclo | 5 a 16 h, manual | Sim (setup) |
| 9 | Estrutura fiscal de quem vende | não verificada | consulta a contador | Só antes da primeira venda real |

## 3. Triagem de micronichos (12 candidatos)

Cada candidato é definido por **público + problema + promessa editorial + possível oferta**. Nível de evidência: **A** pesquisa a fundo por agente (perfis, ofertas, fontes oficiais); **B** busca exploratória e páginas oficiais lidas; **C** só julgamento e leitura do repositório, sem busca temática.

| # | Micronicho | Evidência | Produção no retrato | Decisão |
|---|---|---|---|---|
| 1 | **MEI e pequenos prestadores: preço, caixa e limite.** Público: MEI e autônomo iniciante. Problema: não sabe quanto cobrar nem quanto sobra. Promessa: um número oficial datado por Reel. Oferta: planilha preço/caixa/limite + mini e-book; afiliado de gestão | A | 8 de 8 formatos, sem filmagem | **Finalista, principal** |
| 2 | **System design e entrevistas técnicas.** Público: devs júnior e pleno. Problema: sabe programar e trava ao explicar arquitetura. Promessa: um conceito com número e fonte por Reel. Oferta: cheat sheet, e-book, kit; afiliado Aced | A | 4 a 5 de 8; o diagrama não existe no retrato | **Finalista, reserva (condicional)** |
| 3 | **Inglês instrumental para devs.** Público: devs e analistas brasileiros. Problema: trava em entrevista e reunião. Promessa: a frase certa por situação. Oferta: banco de frases e templates STAR; afiliado Cambly | A | 1 de 8 sem mudança; precisa de narração bilíngue | Finalista, descartado (TTS bilíngue, autoridade, gratuitos) |
| 4 | **Economia do cotidiano com dados oficiais** (o tema atual da pipeline). Público: adultos que leem manchete de economia. Problema: número sem contexto. Promessa: "o que dá para comparar". Oferta: newsletter e e-book informativo | A | 4 de 8 sem adaptação | Finalista como comparação, fora do experimento (monetização fraca) |
| 5 | **Produtividade e organização com templates (Notion, planner).** Público: estudantes e profissionais. Oferta: template pago | B: várias ofertas em Gumroad e Payhip; uma página sem preço legível; nenhum perfil verificado | médio, mas o template precisa de demonstração em tela, que o pipeline não faz | Descartado: produto de preço baixo e substituível; sem demonstração |
| 6 | **Histórias de empresas (ascensão e queda).** Oferta: newsletter | B: buscas não acharam perfis nem ofertas. Repositório: no Votorantim, 5 de 10 planos de imagem ficaram sem ativo | linha do tempo e mapa fora do retrato; direitos de imagem | Descartado: direitos de imagem e elo fraco com produto |
| 7 | **Materiais para pais e professores (imprimíveis).** Oferta: PDFs de atividades | B: a Hotmart lista "+800 Atividades Educativas Para Crianças em PDF" (a página não mostra preço, comissão nem vendas) | exige ilustração infantil; o projeto só usa peças de licença aberta | Descartado: ilustração, licença e produto sem relação com dado |
| 8 | **Ciência, história e mitologia animadas (referência: Kurzgesagt).** Oferta: produtos físicos | B: perfil com 1,6 milhão de seguidores (leitura do coordenador, não reaberta pelo verificador); a loja oficial só vende produto físico (US$ 15,90 a 59,90) [F, conferida pelo verificador] | ilustração animada artesanal, fora do conjunto de planos | Descartado: produção e monetização |
| 9 | **Imposto de renda da pessoa física.** Sazonal | C | dados oficiais cabem | Não testado: o ciclo cairia fora da época declarada de entrega (não verificada nesta rodada) e há risco de aconselhamento tributário |
| 10 | **IA aplicada ao trabalho (tutoriais).** | C: sinal indireto, 5 de 7 temas legíveis de system design são de IA | exige gravação de tela, que o pipeline não faz | Não testado; adjacente ao #2 |
| 11 | **Direitos do consumidor (CDC) explicados.** Oferta: modelos de carta | C | planos cabem | Não testado: fronteira com consultoria jurídica não verificada |
| 12 | **Nutrição e treino em "mito ou verdade".** | A parte da conversa anterior (`docs/pesquisa/instagram-fitness-nutricao-2026-10.md`) | planos cabem | Fora desta rodada: regulação alta (CFN, Anvisa, CONAR) e estudo pago |

**Alternativas encontradas durante a pesquisa (sem estudo):** (a) extensão em inglês do #1 para freelancers de conhecimento: a How To Go Freelance vende templates a US$ 29 e curso a US$ 149 (preço "Early Bird") [F]; (b) engenharia de IA como deriva do #2: 5 de 7 temas legíveis e a home do ByteByteGo ("Become an AI Engineer") apontam nessa direção [F/I].

## 4. Comparação dos finalistas

### 4.1 Tabela comparativa

| | **MEI: preço, caixa e limite** | **System design** | **Inglês para tecnologia** | **Economia do cotidiano** |
|---|---|---|---|---|
| **Público/mercado** | MEI e autônomos, Brasil, pt-BR | Devs júnior e pleno; inglês global é o mercado forte, pt-BR menor | Devs e analistas brasileiros, pt-BR com frases em inglês | Adultos brasileiros, pt-BR; comparação internacional |
| **Formato** | Um número ou regra oficial datado, 25 a 40 s | Um conceito ou número com fonte; o diagrama é o núcleo do nicho e não existe em retrato | "Diga isto, evite aquilo" e resposta modelo | Placar ou número com ressalva (formato já testado) |
| **Oferta** | Planilha preço/caixa/limite + mini e-book; isca gratuita; afiliado Bling 10% no 1º ano, exige CNPJ | Cheat sheet, e-book, kit; afiliado Aced 20% recorrente (FAQ de pagamento não lido); ByteByteGo ≥ 5.000 "fans", % não publicado | Banco de frases e templates STAR; afiliado Cambly US$ 30 por conversão (piso) | Lista e newsletter gratuita; e-book informativo; afiliado Amazon livros 10%; produto financeiro regulado (não verificado) |
| **Produção** | **Alta:** 8 de 8 formatos mapeados no retrato; números voláteis | **Média a baixa:** 4 a 5 de 8 formatos hoje; diagrama 1 a 2 dias a 1 a 2 semanas; checagem técnica cara | **Baixa:** 1 de 8 sem mudança; contrato bilíngue; TTS sem controle de pronúncia | **Alta:** 4 de 8 sem adaptação, 3 com ajuste, 1 exige ADR |
| **Engajamento** | Incerto: 2 Reels com métrica (31 curtidas e 33 comentários, em boa parte a palavra-chave do CTA; 10 e 18); perfis de planilha de 81 a 85 mil | **Indício mais forte, n=1:** AlgoMaster (394 mil) com um Reel de 14,1 mil curtidas em ~13 h; ByteByteGo (559 mil) só com imagens estáticas e 26 dias sem postar | Baixo: perfis brasileiros pequenos ou parados; @english_for_it (43,4 mil) com 31 e 71 curtidas | Médio a baixo: perfis de dados dominados por imagem estática; Reels de 53 e 258 curtidas |
| **Compra** | Média a baixa: ofertas pagas existem (PeqArt R$ 129,90/ano; kits e e-books de US$ 9,75 a 149) e concorrentes gratuitos oficiais são fortes; nenhuma venda observável | **Alta no mercado em inglês** (US$ 47/78/275; R$ 152/392/785); em pt-BR o Dinamos (autodeclarado) fez ~R$ 30 mil em um ano e virou gratuito | Média: R$ 316 a 632/mês, e-books de US$ 39,99 a 49,99 (promocionais); gratuitos diretos fortes | Baixa: nenhum perfil brasileiro lido expõe produto simples com preço |
| **Concorrência** | Alta: Sebrae, InfinitePay, Contabilizei, Freela Sem Crise, MEiSHOP e planilheiras | Muito alta em inglês; menor em pt-BR (busca fraca) | Alta (cursos, e-books, DIO, Alura, gratuitos) | Muito alta (mídia, marcas, IBGE no mesmo canal) |
| **Evidências** | 9 perfis abertos (5 BR, 4 INT), 42 publicações datadas, 5 legendas, 2 Reels | 5 perfis abertos, 60 itens de grade, 5 posts com legenda | 4 perfis abertos, 3 Reels, 9 + 12 itens listados | 10 perfis abertos, 84 itens de grade, 2 Reels |
| **Confiança** | Média (oficial e concorrência); baixa (demanda e preço) | Média (panorama e preços); baixa (demanda) | Média (concorrência); baixa (demanda) | Média (produção, risco); baixa (pagamento) |
| **Principal obstáculo** | Provar que alguém paga pelo que existe grátis; estrutura fiscal do vendedor; números que mudam | Autoridade (quem assina e revisa) e diagrama em retrato | Narração bilíngue e autoridade | O elo conteúdo → compra sem marca nem credencial; CVM |

**Produtos físicos e SaaS (comparados, não escolhidos).** A loja da Kurzgesagt vende só produtos físicos [F], o que depende de marca grande; para os finalistas, um planner impresso (MEI) ou um pôster de diagramas (system design) tem ligação plausível com o conteúdo, mas custa estoque e logística sem nenhuma evidência de venda. Serviço de consultoria contábil é atividade regulada (texto legal não lido, [H]). SaaS exige desenvolvimento e atendimento: o Dinamos (system design em pt-BR) autodeclarou ~R$ 30 mil em um ano com 230 pessoas ativas e passou a gratuito [F].

### 4.2 Três rankings

| Posição | Facilidade de produção | Potencial de engajamento (provisório) | Viabilidade comercial |
|---|---|---|---|
| 1º | Economia (4), pelo formato já testado | System design (4), por um Reel de 14,1 mil curtidas e contas de 149 a 559 mil seguidores (n=1) | **MEI (3)** |
| 2º | **MEI (4)** | Economia e MEI (3, empatados) | System design (3), empatado em nota; mercado pago mais bem provado, mas exige autoridade e diagrama |
| 3º | System design (3) | — | Economia (2) |
| 4º | Inglês para tecnologia (2) | Inglês para tecnologia (2) | Inglês para tecnologia (2), empatado com Economia |

**Cobertura insuficiente:** não há visualizações nem retenção para nenhum Reel; o ranking de engajamento é o menos confiável. Dados ausentes não foram tratados como zero: a nota 3 do MEI e da economia em interesse reflete incerteza, não pouca demanda.

### 4.3 Pontuação ponderada, com justificativa

Pesos: viabilidade comercial 30%, facilidade de produção 25%, ligação conteúdo-produto 20%, interesse pelo conteúdo 15%, espaço competitivo 10%.

| Critério (peso) | MEI | System design | Inglês p/ tecnologia | Economia |
|---|---|---|---|---|
| **Viabilidade comercial (30%)** | **3.** Ofertas pagas existem (app R$ 129,90/ano; kits US$ 9,75 a 149) e a entrega custa 8,99% + R$ 2,49 por venda na Kiwify; risco regulatório baixo a médio. Pesam contra: alternativas gratuitas oficiais, nenhuma venda observável, afiliado exige CNPJ, preços das planilhas brasileiras ilegíveis | **3.** Mercado pago provado e afiliado verificado (Aced 20% recorrente). Pesam contra: autoridade alta; em pt-BR o único dado (Dinamos) terminou em gratuidade; preço do ByteByteGo não verificável | **2.** Há ofertas pagas, mas o piso de preço de um PDF de frases é zero (Cursa, Talaera, DIO, Na Gringa); afiliado só Cambly; a própria folha da EF mostra nota de TI 551, acima da média nacional 482 | **2.** Nenhum perfil brasileiro expõe produto simples com preço; o dinheiro vem de marca, credencial ou investimento regulado; substituto oficial gratuito (Calculadora do Cidadão) |
| **Facilidade de produção (25%)** | **4.** 8 de 8 formatos; fichas reaproveitáveis. Desconto: números voláteis, sem validade de ficha, exemplos hipotéticos exigem política nova | **3.** 4 a 5 de 8 formatos hoje; diagrama ausente; checagem técnica cara | **2.** Narração bilíngue não existe; só 1 de 8 formatos sem mudança; revisão fluente por Reel | **4.** Formato testado; o custo é pesquisa e checagem, e falta importador de séries |
| **Ligação conteúdo-produto (20%)** | **4.** "Quanto cobrar" leva a uma planilha com a mesma conta. Desconto: calculadoras gratuitas cobrem a conta | **4.** Conceito leva a cheat sheet, kit ou afiliado | **4.** Situação leva a banco de frases | **2.** O produto simples tem substituto oficial; o pago exige credencial |
| **Interesse pelo conteúdo (15%)** | **3.** Tema perene; perfis de planilha de 81 e 85 mil. Só 2 Reels com métrica, e os comentários são em boa parte a palavra-chave do CTA | **4.** Contas de 149 a 559 mil, Reels quase diários, um Reel de 14,1 mil curtidas (n=1). Desconto: tendência para IA | **2.** Perfis brasileiros de 599 seguidores e de 8.011 sem post desde 2023-11-30; internacional de 43,4 mil com 31 e 71 curtidas | **3.** Pauta por calendário oficial; audiência para economia explicada, mas Reels de dado são minoria |
| **Espaço competitivo (10%)** | **2.** Gratuitos oficiais e planilheiras grandes | **2.** Topo saturado em inglês; pt-BR menos ocupado (busca fraca) | **2.** Cursos, e-books e plataformas grandes | **1.** Mídia, marcas e fontes oficiais no mesmo canal |
| **Total ponderado** | **3,35** | **3,25** | **2,40** | **2,55** |

### 4.4 Sensibilidade

- **MEI e system design empatam tecnicamente.** Baixar em 1 ponto qualquer uma das quatro primeiras notas do MEI (comercial, produção, ligação conteúdo-produto ou interesse) faz o system design passar à frente; baixar a de espaço competitivo só empata (3,25 a 3,25); subir qualquer uma mantém o MEI na frente.
- Em 20.000 sorteios com os pesos variando ±10 pontos percentuais, os **dois primeiros são sempre MEI e system design** (100%), e o MEI fica em primeiro em 87%.
- Se o dono tiver **credencial técnica verificável** (nota de viabilidade comercial do system design de 3 para 4), o system design sobe a 3,55 e passa o MEI.
- A distância do 2º para o 3º colocado (economia) é de 0,70, estável; economia e inglês ficam atrás em qualquer variação razoável.

## 5. Evidências verificáveis

O registro linha a linha está em `docs/pesquisa/evidencias-nichos-reels.csv` (301 linhas). Tabela dos 16 perfis principais (seguidores lidos em 2026-10-06):

| Nicho | Perfil | Mercado e idioma (evidência) | Seguidores | Atividade na janela | Oferta observada (preço, moeda) | Limitação |
|---|---|---|---|---|---|---|
| MEI | [@minhas_financas_organizadas](https://www.instagram.com/minhas_financas_organizadas/) | Brasil, pt-BR (bio, legenda e hashtags) | 85,5 mil | 1 item (Reel de 2026-09-02) | Planilhas pessoal, empresarial e precificação; preços só em imagens | Preços ilegíveis; 9 itens em ~13 meses |
| MEI | [@peqart.app](https://www.instagram.com/peqart.app/) | Brasil, pt-BR (App Store BR em R$) | 12,4 mil | 12 carrosséis de 2026-09-24 a 10-06 | App com assinatura anual R$ 129,90; nota 4,8 (405 avaliações) | Sem Reels; métricas ocultas |
| MEI | [@howtogofreelance](https://www.instagram.com/howtogofreelance/) | Inglês; EUA não comprovado | 19,6 mil | 10 itens (4 Reels, 2 reposts) | Templates US$ 29; curso US$ 149 ("Early Bird") | Legendas e métricas ocultas |
| MEI | [@the.freelance.coach](https://www.instagram.com/the.freelance.coach/) | Inglês; EUA não comprovado | 51,6 mil | 3 itens, último 2026-07-14 | Oferta não exibida; promessa de renda autodeclarada | Link da bio não lido |
| System design | [@trilhainfo](https://www.instagram.com/trilhainfo/) | Brasil, pt-BR | 21,3 mil | 6 itens (5 em julho, 1 em 2026-09-25) | Dinamos, system design em pt-BR, gratuito desde 2025-12 | 1 legenda lida |
| System design | [@devfullcycle](https://www.instagram.com/devfullcycle/) (adjacente) | Brasil, pt-BR | 149 mil | 11 itens em 13 dias | MBA Arquitetura (18 meses, 600 h), preço só por contato | Os dois Reels lidos não são de system design |
| System design | [@bytebytego](https://www.instagram.com/bytebytego/) | Inglês; audiência não comprovada | 559 mil | 7 itens; 12 de 12 imagens estáticas; sem item novo há 26 dias | Bundle de cursos em texto ilustrado; **preço não verificável** | Preço carrega no cliente |
| System design | [@algomasterio](https://www.instagram.com/algomasterio/) | Inglês (preço lido em R$; moeda por IP não verificável) | 394 mil | 11 de 12 clipes | Premium R$ 152 / 392 / 785 | 3 itens sob a conta do fundador |
| Inglês | [@inglespdevs](https://www.instagram.com/inglespdevs/) | Brasil, pt-BR | 8.011 | Nenhum post visível depois de 2023-11-30 | R$ 316 (1x) e R$ 632 (2x) por mês | Pode estar ativo fora do Instagram |
| Inglês | [@devspeakacademy](https://www.instagram.com/devspeakacademy/) | Brasil, pt-BR | 599 | 2 posts (Reel de 2026-09-30, 5 curtidas) | Turmas de até 4; preço só por formulário | Legenda é paráfrase do leitor |
| Inglês | [@english_for_it](https://www.instagram.com/english_for_it/) | Inglês; "Worldwide" na bio | 43,4 mil | 6 Reels em 21 dias | Lite US$ 20; cursos e e-books sem preço | 2 Reels abertos |
| Inglês | [@speaktech.english](https://www.instagram.com/speaktech.english/) | Inglês | 3.562 | Datas por post inconsistentes | E-books US$ 39,99 e 49,99 (promocionais); bundle US$ 99 | Nenhum post aberto |
| Economia | [@paulogala](https://www.instagram.com/paulogala/) | Brasil, pt-BR | 78 mil | 12 de 12 (10 fotos, 1 carrossel, 1 clipe) | Cursos EAD e mentoria; **sem preço nas páginas lidas** | Legendas e métricas ocultas |
| Economia | [@imlucena](https://www.instagram.com/imlucena/) | Brasil, pt-BR | 30,1 mil | 5 Reels, 4 carrosséis, 3 fotos | Sem produto; palestra e assessoria | Só 1 Reel aberto |
| Economia | [@visualcap](https://www.instagram.com/visualcap/) | Global, inglês | 413 mil | Ao menos 1 item por dia; 1 clipe | VC+ US$ 7,49/mês cobrado anualmente; relatório US$ 80 | O handle certo é `@visualcap` (`@visualcapitalist` é outra página) |
| Economia | [@planetmoney](https://www.instagram.com/planetmoney/) | Inglês; EUA inferido (NPR, preços em dólar) | 248 mil | 11 Reels em 12 itens | Assinatura Planet Money+; preço diverge entre fontes | Preço não resolvido |

### 5.1 Reels abertos (únicos com legenda e métrica)

| Reel | Data | O que a página mostra | Métricas públicas | Observação |
|---|---|---|---|---|
| [@minhas_financas_organizadas](https://www.instagram.com/reel/Dcy-WrMO8MH/) | 2026-09-02 | Legenda sobre "um detalhe da precificação que muita gente esquece" e o CTA "Comenta Precificação que eu te envio o link no direct" | 31 curtidas, 33 comentários | Reaberto pelo verificador: boa parte dos comentários é só a palavra-chave |
| @the.freelance.coach | 2026-07-14 | "Curious about freelancing... Comment WORKSHOP" | 10 curtidas, 18 comentários | Não reaberto |
| @algomasterio | 2026-10-06 | Título curto "Big-O Race" e hashtags | 14,1 mil curtidas, 47 comentários em ~13 h | Não reaberto; a página **não permite concluir** que o Reel é animado |
| @trilhainfo | 2026-09-25 | "Jev faz um site aí pra mim?" (tema de IA) | 218 curtidas, 5 comentários | Não é de system design |
| @devfullcycle | 2026-10-06 | Aviso de risco sobre agentes de IA; "Comente MBA" | 13 curtidas em ~10 h | CTA leva a contato comercial |
| @devspeakacademy | 2026-09-30 | Pergunta de entrevista em inglês com modelo de resposta, em série (paráfrase do leitor) | 5 curtidas | |
| @english_for_it | 2026-09-17 e 2026-09-19 | "Don't make these mistakes" e "The HR after hearing you don't speak English", ambos com CTA para o link da bio | 31 e 71 curtidas | O de 09-19 usa música de catálogo (metadado da página) |
| @imlucena | 2026-10-02 | "Como me mantenho atualizado sobre os principais acontecimentos da economia mundial?" | 53 curtidas | |
| @planetmoney | 2026-10-02 | Legenda sem tema econômico explícito | 258 curtidas, 3 comentários | |

**Análise limitada de um Reel típico e de um que se destaca.** Como nenhum vídeo foi assistido, só dá para afirmar o que a legenda e os números dizem. **Típico (MEI):** gancho de omissão ("o detalhe que muita gente esquece"), tema de custo real, CTA de comentário-chave que dispara o envio de um link; 31 curtidas num perfil de 85,5 mil. **Destaque (system design):** título de duas palavras, sem CTA visível, 14,1 mil curtidas em um dia num perfil de 394 mil; a página mostra que o perfil se descreve como "visual explanations", e isso não permite descrever o vídeo. O que se pode **estudar sem copiar** é o mecanismo: pergunta no título; isca digital grátis por e-mail (o ByteByteGo troca um PDF de 368 páginas por cadastro); funil gratuito → template → curso; CTA de comentário-chave.

## 6. Fichas dos dois escolhidos

### 6.A Ficha do principal: MEI, preço, caixa e limite

**Definição.** Público: MEI e autônomo iniciante, no Brasil. Problema: não sabe quanto cobrar nem quanto sobra. Promessa editorial: um número ou uma regra oficial, com fonte e data, por Reel. Oferta: planilha de preço, caixa e limite + mini e-book; afiliado de gestão depois.

**Cadeia.**

| Elo | Leitura | Base |
|---|---|---|
| O vídeo atrai quem | MEI e autônomo que quer saber "quanto é o DAS", "qual o limite", "quanto cobrar" | [F] fontes oficiais existem e mudam; [H] que responda mais a número oficial do que a método |
| Precisa de quê | Um número confiável e datado; uma conta de preço (custos + imposto + margem + hora); um controle simples de entradas e saídas; acompanhar o limite | [F] o método gratuito do Sebrae/MS cobre a conta |
| Qual produto ajuda | Planilha de 3 abas (parâmetros oficiais datados, preço, caixa e termômetro do limite) e mini e-book de 10 a 15 páginas | [H]; concorrentes vendem versões (Kit Finanças MEI 2026 na Hotmart; app PeqArt) |
| Por que compraria de nós | Cada número com fonte e data (contra material com ano trocado); a conta do Reel é a mesma da planilha; preço baixo e atualização anual | **[H] nada disso foi testado.** O cálculo em si existe grátis; o diferencial teria de ser conveniência e atualização |

**Fatos oficiais que o conteúdo usaria (conferidos pelo verificador em 2026-10-06).**
- **DAS-MEI 2026:** R$ 81,05 de INSS (5% do salário mínimo de R$ 1.621,00, Decreto 12.797/2025) + R$ 5,00 de ISS e/ou R$ 1,00 de ICMS; as somas são R$ 82,05 (comércio e indústria), R$ 86,05 (serviços) e R$ 87,05 (comércio e serviços). Fonte: Receita Federal, 2026-01-02.
- **Limite:** R$ 81 mil por ano; **R$ 6.750 por mês de atividade** no ano de abertura; até 20% acima (R$ 97.200) paga-se DAS complementar e vira ME no ano seguinte (gov.br/memp, atualizado em 2026-09-16).
- **Em tramitação:** o PLP 186/2026 propõe R$ 110 mil em 2027 e R$ 140 mil em 2028 e "ainda não está em vigor"; o PLP 108/2021 aparece com R$ 144,9 mil (Câmara, 2026-03-17) e R$ 130 mil (2026-04-29). **Reel com "novo limite" envelhece em semanas.**
- **DASN-SIMEI** até o último dia de maio; **ocupações permitidas:** Anexo XI da Resolução CGSN 140/2018 (PDF sem data visível, confirmar a versão vigente).

**Oferta própria e afiliado.**

| Opção | Condições (página oficial, 2026-10-06) | Observação |
|---|---|---|
| Isca gratuita: calculadora de hora técnica (Google Sheets), entregue por palavra-chave nos comentários | — | Padrão visto em 2 de 2 Reels com legenda lida [F]; **[H]** que converta cadastros |
| Planilha "preço, caixa e limite (2026)" + mini e-book | Kiwify: 8,99% + R$ 2,49 por venda, R$ 3,67 por saque, sem mensalidade. Líquido (conta minha): R$ 22,08 em R$ 27; R$ 40,28 em R$ 47; R$ 58,49 em R$ 67 | Hotmart cobra 9,9% + R$ 2,49 por venda (a ficha antiga citava R$ 1 e está desatualizada) |
| Afiliado Bling | 10% da mensalidade no primeiro ano; resgate mínimo R$ 100; **só CNPJ ativo (CPF excluído)**; pagamento em até 30 dias após nota fiscal; termos completos não lidos | Serve a quem vende produto; aderência a prestador de serviço **não verificada** |
| Outros afiliados (Agilize, Contabilizei, Cora, Conta Azul) | Sem comissão publicada para criador | **Não verificado** |

**Produção: 8 formatos de 20 a 45 s e os planos de hoje.**

| # | Formato | Planos | Adaptação |
|---|---|---|---|
| 1 | O número do ano (DAS 2026) | keyword, number, compare (comércio, serviços, ambos), stamp | Nenhuma; ficha por número |
| 2 | Quanto sobra de um mês (exemplo) | number, chart share, compare, lower_third | Exige ficha de exemplo (item 2 da seção 2.5); o IR do MEI não foi verificado |
| 3 | Preço em quatro partes (método do Sebrae) | keyword, number, compare | Nenhuma; atribuir ao Sebrae; não copiar o exemplo |
| 4 | Termômetro do limite (R$ 81 mil; R$ 6.750 no 1º ano) | chart bar_horizontal, number, compare, stamp | O medidor do kit não tem plano |
| 5 | Notícia: o limite vai mudar? | stamp, compare, number | Linha do tempo fora do retrato; notícia envelhece rápido |
| 6 | Faturamento não é dinheiro no bolso | compare, number, keyword | Exemplo hipotético exige ficha |
| 7 | Prazos (DASN, comunicação do excesso) | keyword, number, stamp | Calendário ausente; texto de lei não lido |
| 8 | Sua ocupação está na lista? | keyword, stamp, broll | Risco de individualizar; só apontar a lista oficial |

**Riscos e fronteira regulatória.** [F] A lista de ocupações e os valores têm fonte oficial. [H, texto de lei não lido porque o Planalto não respondeu] A contabilidade e a consultoria jurídica têm atividades privativas; regra editorial: informar número e regra geral com fonte e data; nunca "você deve", "você pode" nem "no seu caso"; exemplo sempre rotulado; dúvida individual vai para o Portal do Empreendedor ou para um contador. **Não afirmar** isenção de IR sobre o lucro do MEI (não verificada) e **não prometer** renda, economia de imposto nem resultado.

**Autoridade, concorrência e alternativas gratuitas.** Para informação geral com fonte, não parece exigir ser contador [I], mas o canal sem rosto depende de transparência de fonte e data como substituto (nada prova que converta). Gratuitas: e-book do Sebrae/MS (©2025, já com DAS defasado), planilha da InfinitePay (em troca de nome e e-mail), calculadoras do Freela Sem Crise, gestão do CNPJ do MEiSHOP, portal e app oficiais. Pagas: planilheiras de 81 a 85 mil seguidores, o app PeqArt, e-books e kits de US$ 9,75 a 149.

**Atendimento, manutenção e entrega.** Dúvidas previsíveis ("meu DAS não bate", "posso ser MEI?", "devo virar ME?"): as duas últimas são consultoria individual e devem ser recusadas com remissão oficial. **Manutenção:** todo Reel com "2026" envelhece em janeiro; uma mudança de limite deixa Reels errados do dia para a noite. Entrega: plataforma de venda; direito de arrependimento e garantia não verificados.

### 6.B Ficha da reserva: system design e entrevistas técnicas (condicional)

**Definição.** Público: devs júnior e pleno que se preparam para entrevistas. Problema: sabe programar e trava ao explicar escalabilidade, filas, cache, consistência. Promessa editorial: um conceito ou número por Reel, com a fonte oficial citada na tela. Oferta: cheat sheet gratuito por e-mail, depois pacote pago pequeno; afiliado.

**Por que é reserva e não principal.** Tem as melhores evidências de mercado pago (preços visíveis de US$ 47 a US$ 275 e de R$ 152 a R$ 785; afiliado Aced com 20% de comissão recorrente) e de engajamento (n=1). Perde por duas dependências do dono, que viram **condições para ativá-la**:
1. **Autoridade:** quem assina e quem revisa a precisão técnica (o dono, um revisor nomeado ou um canal sem rosto ancorado só nas fontes). Todos os concorrentes lidos exibem credencial pessoal; o apresentador ilustrado não é credencial. Se ninguém assinar, o lugar da reserva no ciclo vai para a **economia do cotidiano** (seção 7.9).
2. **Diagrama:** o formato central do nicho (a esteira, a rede) não existe em retrato. No ciclo de 14 dias a reserva usa só os formatos que existem (4 a 5 de 8); **um resultado fraco aqui não refuta o nicho de diagramas**, só o de números e comparações.

**Formatos (8) e encaixe hoje.** Noves da disponibilidade (alto); limite documentado que derruba sistema (alto a médio); A contra B (médio); caso real de uma empresa (médio); ordens de grandeza de latência (baixo a médio); caminho de uma requisição, conceito em 30 s e estimativa de capacidade (baixo: dependem de diagrama, de animação de conceito ou de cálculo que a tela não faz).

**Afiliado.** Aced: "20% recurring commission on sales every month", inclusive renovações; candidatura em 2 minutos; é "for top tech creators"; **o FAQ de pagamento e atribuição não carrega e não foi lido**. ByteByteGo: exige pelo menos 5.000 "fans", comissão não publicada, cookie de 30 dias. Codemia paga 1 ano de Premium em vez de comissão e exige conteúdo de 10 minutos ou mais: não serve a Reels. Divulgação de afiliado: o programa do Codemia cita a exigência (FTC); a regra brasileira para afiliado **não foi verificada no CONAR**.

**Riscos.** Alta precisão técnica: cada número, quota e seta é uma afirmação com fonte; na 1ª checagem do episódio de teste do projeto, 25% das frases foram reprovadas (tema não técnico; em tema técnico, não medido). Fontes de fornecedor são "interessadas" e exigem segunda fonte independente no gate 1. Licença: o SRE Book do Google (tabela de disponibilidade) é **CC BY-NC-ND 4.0**; citar o número é diferente de reproduzir a tabela num canal comercial: confirmar com quem entende [H]. Não copiar diagramas de terceiros.

## 7. Plano de teste de 14 dias

### 7.1 Organização

- **Duas contas novas, uma por micronicho** (MEI e system design), criadas, administradas e publicadas **pelo dono, à mão**. O pipeline não cria conta nem publica. Motivo: os públicos são incompatíveis (prestadores de serviço e desenvolvedores), e misturar os dois num perfil contaminaria quem vê, quem segue e a leitura de cada Reel.
- **Mesmas condições:** 5 Reels por conta em 14 dias (um a cada 2 a 3 dias, mesmos dias e horários nas duas contas), duração de 25 a 40 s, mesma estrutura (gancho com número, fonte e data na tela, CTA de comentário-chave com resposta manual), uma isca gratuita por conta, sem anúncio pago (CLAUDE.md §12), sem divulgar uma conta na outra e **sem contar amigos e família** nas métricas.
- **Leituras:** 7 e 14 dias depois de cada post (a medição vai até ~D+28; a leitura de 28 dias é a que o CLAUDE.md §12 pede para o registro).
- **Humano e agentes:** cada Reel passa pelos gates 1 a 4. Gate 1 em pacote por conta (as fichas oficiais do MEI servem a vários Reels). Horas humanas cronometradas por gate.

### 7.2 Calendário (D0 = dia escolhido pelo dono)

| Antes de D1 | D1 | D3 | D6 | D9 | D12 | D14 a D28 |
|---|---|---|---|---|---|---|
| Contas, isca, página de lista, planilha de registro, gate 1 | M1 e T1 | M2 e T2 | M3 e T3 | M4 e T4 | M5 e T5 | Leituras de 7 e 14 dias de cada post; decisão |

### 7.3 Reels do principal (MEI, pt-BR)

**M1. DAS 2026, por atividade.**
- *Problema:* o MEI não sabe quanto vai pagar de boleto. *Gancho autoral:* "O boleto do MEI não é igual para todo mundo." *Ideia:* mostrar os três valores oficiais de 2026 por tipo de atividade e a data da fonte.
- *Sequência:* keyword → compare (comércio × serviços) → number (ambos) → stamp (fonte e data). *Componentes:* KineticHeadline, ValueCompare, odômetro do `number`, DateStamp e SourceTag.
- *CTA:* "Comenta DAS" → isca (calculadora de hora técnica). *Oferta relacionada:* lista de espera da planilha. *Fontes:* Receita Federal 2026-01-02; FAQ gov.br. *Esforço:* baixo (3 a 4 fichas).

**M2. Limite e proporcional do ano de abertura.**
- *Problema:* quem abriu no meio do ano não sabe o limite. *Gancho:* "R$ 81 mil por ano. Mas, no ano em que abre, o limite é outro." *Ideia:* teto anual e R$ 6.750 por mês de atividade, **sem calcular o caso do espectador** e sem números de PLP em tramitação.
- *Sequência:* keyword → number (R$ 81 mil) → number (R$ 6.750 por mês) → compare (ano inteiro × ano de abertura) → stamp. *CTA:* "Comenta LIMITE" → planilha-termômetro gratuita. *Fontes:* gov.br/memp (modificado em 2026-09-16); manual DASN. *Esforço:* baixo a médio.

**M3. Preço em quatro partes (método do Sebrae).**
- *Problema:* "preço de cabeça". *Gancho:* "Preço não é chute: tem quatro partes." *Ideia:* custos fixos, custos variáveis, imposto e margem, e que a hora de trabalho entra; atribuir ao Sebrae/MS; **não usar o exemplo numérico do e-book** (DAS de 2025).
- *Sequência:* keyword × 4 intercalados com broll de prestador (ilustração, conferência de pessoas, marcas e texto da ADR 007) → compare em texto. *CTA:* "Comenta PREÇO" → calculadora de hora técnica. *Fontes:* e-book do Sebrae/MS (fonte única: marcar). *Esforço:* médio.

**M4. A lista oficial de ocupações.**
- *Problema:* "minha atividade pode ser MEI?". *Gancho:* "Existe uma lista oficial de ocupações do MEI. A sua está nela?" *Ideia:* mostrar onde a lista está (Anexo XI, Portal do Empreendedor) e como conferir, sem dizer "pode" nem "não pode" no caso do espectador. Serve também para **descobrir qual público responde** (comentários sobre a ocupação).
- *Sequência:* keyword → broll → keyword → stamp. *CTA:* "Comenta a sua atividade". *Fontes:* Anexo XI (confirmar versão vigente). *Esforço:* baixo.

**M5. Para onde vai o DAS.**
- *Problema:* "o que eu estou pagando?". *Gancho:* "Quase todo o DAS é INSS." *(Frase a confirmar: só vale se a ficha mostrar que R$ 81,05 de R$ 82,05 a R$ 87,05 é INSS; senão reescrever.)* *Ideia:* INSS (5% do salário mínimo) + ISS ou ICMS, com os valores de 2026.
- *Sequência:* keyword → chart share ou number × 3 → stamp. *CTA:* "Comenta DAS". *Fontes:* Receita Federal 2026-01-02. *Esforço:* baixo.
- *Fica para depois, até um profissional revisar:* a regra do excesso de faturamento, o IR do MEI e qualquer "quanto sobra" com conta de exemplo.

### 7.4 Reels da reserva (system design, pt-BR, só com formatos que existem hoje)

**T1. Noves da disponibilidade.** *Gancho:* "99,9% parece quase perfeito. Por ano, são 8,76 horas fora do ar." *Ideia:* comparar 99,9%, 99,99% e 99,999% em tempo fora do ar por ano (8,76 h; 52,6 min; 5,26 min). *Sequência:* keyword → number × 3 → compare before_after → stamp. *Fonte:* tabela de disponibilidade do SRE Book (CC BY-NC-ND 4.0; citar o número, **não reproduzir a tabela**). *CTA:* "Comenta NOVES" → starter pack de 1 página com fonte. *Esforço:* médio (unidades mistas impedem a escala `scale`).

**T2. O limite que derruba o sistema.** *Gancho:* "Todo serviço tem um número na documentação que o seu sistema não pode passar." *Ideia:* um limite documentado de um serviço (a escolher no gate 1). *Sequência:* keyword → number → compare → stamp com a versão da documentação. *Fonte:* documentação oficial do fornecedor (fonte interessada: segunda fonte independente). *Esforço:* médio a alto (cota muda; o contrato não guarda versão).

**T3. Fila ou log?** *Gancho:* "Fila e log parecem iguais até a mensagem ser lida." *Ideia:* a diferença conceitual, com a documentação de cada produto (a escolher) e uma fonte neutra. *Sequência:* keyword → compare em texto → number. *Esforço:* alto (pesquisa e checagem).

**T4. Como uma empresa resolveu um problema.** *Ideia:* um caso de blog de engenharia com uma métrica antes e depois. *Sequência:* stamp → number → compare before_after → chart line (anos). *Fonte:* o blog da empresa (interessada; sem logo). *Esforço:* médio.

**T5. Ordens de grandeza de latência.** *Ideia:* pares de mesma unidade em `compare scale`, não barras lineares. *Fonte:* tabela de latência com data (a escolher; são aproximações). *Esforço:* médio. *Encaixe:* baixo a médio.

Fontes de T2 a T5 são **a escolher no gate 1 e ainda não existem**: por isso o esforço é incerto e a reserva só entra se o dono resolver a condição 1.

### 7.5 Oferta mínima e medição de interesse (preços são de teste)

| Conta | Gratuito | Lista de espera | Preço de teste e premissas |
|---|---|---|---|
| MEI | Calculadora de hora técnica (Google Sheets), entregue por palavra-chave | Planilha "preço, caixa e limite (2026)" + mini e-book | **R$ 27, R$ 47 e R$ 67 [H].** Faixa tirada de um relato de blog sem fonte (R$ 47) e de preços internacionais de US$ 9,75 a US$ 39 (páginas oficiais, em dólar); líquido na Kiwify: R$ 22,08, R$ 40,28 e R$ 58,49. Pergunta de preço na lista (3 opções), **não um botão de compra falso**; a pré-venda real só depois de resolver a estrutura fiscal do vendedor |
| System design | Starter pack de 1 página: 10 números de confiabilidade, cada um com a fonte | Kit com checklist de entrevista e rubrica de resposta | **Sem preço neste ciclo [H]:** âncoras são 1 mês de plataforma a US$ 47 (Hello Interview) e R$ 152 (AlgoMaster); um preço próprio só depois de a lista existir |

Cada conta precisa de um texto de consentimento de e-mail e da pergunta única de qualificação (por exemplo, "qual é a sua atividade?"). **LGPD não foi pesquisada**; usar só o necessário.

### 7.6 O que medir, com denominadores

| Métrica | Denominador | Fonte | Quando |
|---|---|---|---|
| Alcance e visualizações | por Reel | Insights da conta profissional | 7 e 14 dias |
| Retenção | tempo médio de exibição ÷ duração; queda nos primeiros segundos, se o painel mostrar | Insights do Reel | 7 e 14 dias |
| Salvamentos e compartilhamentos | por 1.000 visualizações | Insights | 7 e 14 dias |
| Comentários do CTA | comentários com a palavra-chave ÷ comentários totais; respostas espontâneas à parte | contagem manual | 7 dias |
| Visitas ao perfil e cliques no link | por 1.000 visualizações; cliques ÷ visitas | Insights e rastreio do link com um parâmetro por Reel | 7 e 14 dias |
| Cadastros | cadastros ÷ cliques, por Reel | ferramenta de lista (beehiiv Free vai até 2.500 inscritos, sem assinaturas pagas) | 7 e 14 dias |
| Leads qualificados | respostas qualificadas ÷ cadastros | formulário de 1 pergunta | 14 dias |
| Pré-vendas e vendas | compras ÷ leads qualificados | plataforma de venda | só depois da estrutura fiscal |
| **Horas humanas** | minutos por gate (1 a 4), título e capa, legenda, publicação e atendimento | planilha de tempo | por Reel |
| Custo por Reel | tokens dos agentes + segundos de render + minutos humanos + R$ | logs dos agentes e scripts | por Reel |

Para comparar hipóteses, manter duração, formato e CTA semelhantes. **Dez vídeos dão sinais iniciais; não validam nem preveem receita.**

### 7.7 Como distinguir o que deu errado

| Sintoma | Leitura | Ajuste |
|---|---|---|
| Alcance baixo em todos os Reels, retenção boa | Distribuição (conta nova, horário, tema) | Mais Reels e colaboração antes de concluir que o tema não interessa |
| Alcance razoável, queda nos primeiros segundos e tempo médio curto | Perda de atenção (gancho, ritmo) | Reescrever o gancho, encurtar, mostrar o número primeiro |
| Boa retenção e salvamentos, pouco comentário e clique | CTA fraco | Trocar a palavra-chave, mover o CTA, tornar a isca mais concreta |
| Cliques e visitas, poucos cadastros | Oferta ou página inadequada (promessa diferente da do Reel) | Reescrever a página; trocar a isca |
| Cadastros e respostas qualificadas, nenhuma compra | Interesse sem compra (preço, confiança, produto, substituto gratuito) | Entrevistas curtas; outro preço; verificar se o gratuito basta |

### 7.8 Critérios para continuar, ajustar ou abandonar

**Defina os limiares antes de publicar e registre a decisão.** Não há um percentual universal de sucesso.
- **Continuar** (mais 10 a 12 Reels e construir o produto): sinais convergentes: um formato com retenção e salvamentos claramente acima do resto do próprio ciclo, repetido em pelo menos 2 Reels; cadastros que não vieram só de amigos; ao menos um sinal de compra (pergunta de preço respondida, ou pré-venda). Escolher o limiar relativo à mediana dos 10 Reels do ciclo e à outra conta.
- **Ajustar** (mudar uma variável por vez por 5 Reels): alcance ou retenção boas sem cadastro, ou cadastro sem compra.
- **Abandonar:** nenhum dos cinco diagnósticos mostra sinal depois de ajustar uma variável, ou o custo humano por Reel passa do que o dono aceita sem sinal em troca.

### 7.9 Plano alternativo se a reserva não puder ser ativada

Se ninguém puder assinar nem revisar o conteúdo técnico, a segunda conta testa **economia do cotidiano**, cujos formatos já existem: número do mês (IPCA), placar Brasil × outro país, dentro ou fora da meta, "o que o número não diz" e termo em 20 s. **Os dois vídeos prontos usam dados de 2025 e não servem para postar hoje sem nova rodada de fichas**; o custo dominante é pesquisa e checagem, com download manual de PDFs do IBGE (o servidor recusa o robô).

### 7.10 Custos do ciclo (premissas explícitas)

| Item | Setup (uma vez) | Recorrente | Premissa |
|---|---|---|---|
| Contas, página de lista, 2 iscas, planilha de registro | 5 a 16 h humanas **[H]** | — | calculadora de hora técnica 2 a 4 h; starter pack 2 a 4 h; páginas e contas 2 a 4 h; planilhas de registro 1 a 4 h |
| Gate 1 e fichas | 2 a 6 h humanas por conta **[H]** | — | as fichas oficiais do MEI se reaproveitam entre Reels |
| Agentes por Reel | — | 0,15 a 0,8 milhão de tokens; 10 a 45 min | escala linear do Votorantim; a reserva custa mais por Reel (fontes novas, checagem técnica) |
| Voz | — | Kokoro ~0,9 s por segundo de áudio; Gemini final 1 a 6 chamadas por Reel, **1 a 2 Reels por dia** na cota gratuita | medições desta sessão e ADR 012 |
| Render | — | prévia ~20 s a ~3 min por Reel de 30 s; final 1080×1920 não medido | extrapolado das medições de 41 a 351 s |
| Humano por Reel | — | 20 a 90 min (gates, título, capa, legenda, publicação) **[H]**, a cronometrar | o Votorantim não mediu horas humanas |
| Dinheiro | US$ 0 | US$ 0 | ferramentas gratuitas; **conferir os termos de cada uma** |
| Total do ciclo (10 Reels) | — | 1,5 a 8 milhões de tokens; 3 a 8 h de agentes; 3 a 15 h humanas, além do setup | capacidade do plano do dono para 2 a 8 milhões de tokens: **não medida** |

## 8. O que poderia mudar a decisão, e o que perdeu

**Pode mudar a recomendação:**
1. O dono tem credencial técnica verificável e quer assinar → system design passa a principal (3,55).
2. Os Reels do MEI mostram retenção e cadastros claramente piores que os de system design no mesmo ciclo.
3. Um contador ou advogado limita o que se pode dizer de tributos → reduzir o escopo ou trocar de nicho.
4. Os preços reais das planilhas brasileiras (ilegíveis nesta rodada) ficam bem abaixo de R$ 27, ou a lista só converte para a isca gratuita.
5. O custo humano por Reel medido fica acima do que o dono aceita.
6. A lei muda (PLP do limite aprovado) e a manutenção passa a custar mais do que rende.
7. O público que responde é outro (por exemplo, quem presta serviço de conhecimento): o ângulo muda, não necessariamente o nicho.

**Candidatos atraentes que perderam:**
- **Inglês para tecnologia:** perdeu em produção (narração bilíngue; o Gemini detecta o idioma sozinho, sem controle de pronúncia, e a direção configurada pede "sotaque brasileiro"), em autoridade (todos os concorrentes exibem credencial) e em monetização (materiais gratuitos diretos); a folha da EF mostra nota de TI 551, acima dos 482 do Brasil.
- **Ciência e mitologia animadas:** produção artesanal e produto físico.
- **Histórias de empresas:** direitos de imagem e elo fraco com produto.
- **Produtividade com templates e materiais para pais e professores:** produto de preço baixo, substituível e sem demonstração possível.
- **Economia do cotidiano:** perdeu em monetização e regulação, mas **continua útil como conteúdo gratuito de credibilidade** e confirma, com evidência, a suspeita do dono de que é difícil vender com ela.

## 9. Verificação independente

Um verificador separado releu as páginas, os arquivos e o código sem depender das fichas (relatório completo no anexo). **94 verificações: 79 confirmadas, 7 divergentes, 7 não verificáveis e 1 refutada.** Nenhum preço, comissão ou número oficial central foi refutado. Datas das publicações conferidas pelo código do post (168 linhas: 162 iguais, 6 com 1 dia). Todos os 10 acessos ao Instagram do verificador bateram com as fichas (seguidores sem diferença acima de 10%).

**O que a decisão não deve usar, e o que corrigi neste relatório:**
1. "Cambly exige gasto mínimo de US$ 50" foi **refutado**: a página oficial diz US$ 30 ("starting at $30").
2. Hotmart: a taxa vigente é 9,9% + R$ 2,49; a ficha do MEI citava R$ 1.
3. CONAR: a página oficial sustenta a notícia de 26/05/2026 e a vigência em 1º de junho; as datas 12 e 13 de maio só vêm de terceiros que discordam entre si; "comissão de afiliado precisa ser divulgada" **não está** na página do CONAR (vale a prática de divulgar, mas o texto do CONAR sobre afiliados não foi verificado).
4. **Odômetro:** ele já está dentro do plano `number` (`Editorial.tsx` l. 3 e 92). Também já estão ligados o `DocumentPage` (plano `quote`) e outros itens. Isto corrige uma afirmação minha feita durante a sessão, em que listei odômetro e página de documento entre as peças fora do template. Seguem sem plano: Pipeline, Gauge, CodeWalkthrough, CodeBlock, ContextWindow, AnimatedGraph e Highlighter.
5. A conclusão de que "o freelancer de conhecimento fica fora do MEI" é exagerada: o Anexo XI traz editor de vídeo, instrutor de idiomas e de informática, professor particular e fotógrafo; só designer, programador e consultor não aparecem.
6. "Reel animado de conceito rende mais": **sem base de leitura de vídeo**; só hipótese.
7. "Dinamos chegou ao ponto de equilíbrio" é paráfrase: o texto do autor diz que cobriu os custos fixos de manutenção, e "230" são pessoas ativas, não pagantes; receita autodeclarada.
8. Preços de concorrentes são âncoras frágeis: os e-books da Speak Tech são promocionais (lista 40% a 62% maior); a moeda do AlgoMaster pode ser localizada por IP; o curso de US$ 149 é "Early Bird"; o beehiiv Lite de US$ 49 é cobrança anual na faixa de 1.000 inscritos.
9. Custos por Reel das fichas não são comparáveis entre nichos (premissas diferentes), o 0,7 s por segundo do Kokoro é de inglês (em pt-BR ~0,9) e o render de 40 a 110 s não estava registrado no repositório: usei as medições desta sessão e marquei a origem.
10. Métricas de demanda por Reel (curtidas de um Reel por perfil, comentários de CTA) **não são demanda**: visualizações não existem em páginas públicas.

**Não verificáveis que pesam:** FAQ de pagamento do Aced; moeda do AlgoMaster por IP; métricas dos Reels não reabertos (por limite de acessos, não por bloqueio); o preço oficial do ByteByteGo; o tempo de render do final 1080×1920.

## 10. Lacunas e decisões do dono

**Decisões que só o dono toma:**
1. Adotar o MEI como o primeiro recorte (e registrar numa ADR, conforme o item 18 da `docs/ANALISE.md`)?
2. Quem assina e quem revisa o conteúdo técnico: ativa o system design como reserva (condição 1)?
3. Aceita investir de 1 a 2 dias em uma esteira (`pipeline`) em retrato para o system design, depois do ciclo, se ele mostrar sinal?
4. Quem resolve a estrutura fiscal de quem vende e a fronteira com consultoria contábil (um contador, antes da pré-venda real)?
5. Aceita as duas contas novas e a publicação manual, com cronometragem das horas humanas?

**Evidência que ainda falta, por prioridade:**
1. Visualizações, retenção, salvamentos e cliques por Reel (só o ciclo próprio ou capturas de tela de contas do nicho).
2. Preços e vendas das planilhas brasileiras (Hotmart e links de bio renderizam por script ou imagem).
3. Qual público responde (prestador manual ou de conhecimento).
4. IR do MEI, vencimento e multa do DAS, estado do limite de dois empregados e o texto de lei (o site do Planalto não respondeu), conferidos por profissional.
5. Condições de afiliado para criador (Bling: termos completos e nota fiscal do parceiro; Aced: FAQ).
6. Horas humanas e tokens reais por Reel de 25 a 40 s.
7. LGPD e regras do Instagram para voz sintética e personagem ilustrado (**não pesquisadas**); conferir também os termos de cada ferramenta gratuita.
8. Amostra brasileira maior de system design e de criadores brasileiros que usam animação, por coleta manual (hashtags e perfis), sem raspagem.

## 11. Fontes e arquivos

- **Evidências linha a linha:** `docs/pesquisa/evidencias-nichos-reels.csv`.
- **Anexos (fichas brutas dos pesquisadores e verificação):** `docs/pesquisa/nichos-reels-animados-anexos/` (`mei-ficha.md`, `sysdesign-ficha.md`, `ingles-tech-ficha.md`, `economia-ficha.md`, `verificacao.md`). **As fichas são material de pesquisa e contêm os itens corrigidos na seção 9; vale o que está neste relatório.**
- **Repositório:** `CLAUDE.md`; `docs/decisions/011`, `012`, `013`, `014`, `015`; `app/pipeline/schemas.py`; `app/pipeline/check.py`; `video/src/Editorial.tsx`, `ShotView.tsx`, `Scene.tsx`, `HostWindow.tsx`; `data/benchmarks/episodio-votorantim-dinheiro.md`, `termos-gemini-tts.md`, `README.md`; `docs/ANALISE.md`; `docs/ROADMAP.md`.
- **Páginas oficiais conferidas pelo verificador (2026-10-06):** https://www.bling.com.br/programa-de-parceiros ; https://www.aced.io/affiliate ; https://www.cambly.com/ambassador ; https://associados.amazon.com.br/help/node/topic/GRXPHT8U84RAYDXZ ; https://kiwify.com.br/ ; https://hotmart.com/pt-br/taxa-hotmart ; https://www.beehiiv.com/pricing ; https://algomaster.io/premium ; https://www.hellointerview.com/ ; https://speaktechenglish.com/courses/ ; https://inglesparadevs.com.br ; https://apps.apple.com/br/app/id1594656704 ; https://www.howtogofreelance.com/ ; https://www.visualcapitalist.com/get-more-vc/ ; https://www8.receita.fazenda.gov.br/simplesnacional/noticias/NoticiaCompleta.aspx?id=c3b2044c-ff97-432a-b33c-ecf2a3df6dc3 ; https://www.gov.br/memp/pt-br/teto-do-mei ; https://www.conar.org.br/noticias/guia-de-marketing-e-publicidade-por-influenciadores-digitais ; https://www.gov.br/cvm/pt-br/assuntos/noticias/area-tecnica-da-cvm-esclarece-duvidas-sobre-atuacao-de-influenciadores-que-recomendam-investimentos-dddc1973876d4cc78c734b8ceeaaa740 ; https://github.com/remotion-dev/remotion/blob/main/LICENSE.md ; https://www.remotion.pro/license ; https://shop-us.kurzgesagt.org/ ; https://www.tabnews.com.br/trilhainfo/abri-mao-de-um-saas-que-faturou-r30000-esse-ano ; https://sre.google/sre-book/availability-table/.
