> **Anexo de pesquisa bruta (2026-10-06).** Esta ficha foi escrita por um pesquisador antes da verificação independente e **contém itens depois corrigidos**: a taxa da Hotmart (vale 9,9% + R$ 2,49), as datas do guia do CONAR (vale 26/05/2026 e vigência em 1º de junho; 12 e 13 de maio só aparecem em terceiros), o mínimo da Cambly (US$ 30; o de US$ 50 foi refutado), o odômetro (já está dentro do plano `number`), e rótulos [F] fortes demais em paráfrases de legenda. Vale o que está em `docs/pesquisa/nichos-reels-animados.md` e em `verificacao.md`. Nenhum vídeo foi assistido.

# sysdesign: system design e entrevistas técnicas de engenharia de software (pt-BR e inglês)

Data da consulta: 2026-10-06. Janela de 90 dias: publicações desde 2026-07-08. Dados brutos: `sysdesign-evidencias.csv` (76 linhas, 24 colunas).
Marcas usadas no texto: **[F]** fato observado com URL, **[I]** inferência minha, **[H]** hipótese a testar. Códigos `[S#]` apontam para a seção 12.

## 0. Resumo e leitura provisória

O nicho tem público grande e ativo, produtos pagos com preço visível e um programa de afiliados com comissão verificada. O ponto fraco para esta pipeline hoje é que o formato central do nicho, o diagrama, não existe em retrato, e que cada seta de diagrama vira uma afirmação técnica com fonte.

| Critério do brief | Leitura | Base |
|---|---|---|
| Interesse recorrente | Alto (indireto) | Três contas de 149 mil a 559 mil seguidores e postagem quase diária no AlgoMaster [S4]; sem views, só curtidas de 5 posts. O ByteByteGo não tem item novo na grade há 26 dias [S1] |
| Problema que leva à compra | Médio a alto | Objetivo claro (passar em entrevista, subir de carreira); preços visíveis de US$ 47 a US$ 275 [S16] e R$ 152 a R$ 785 [S15]. Em pt-BR, o Dinamos (autodeclarado) chegou ao ponto de equilíbrio e virou gratuito [S21] |
| Produção simples e repetível | Médio a baixo hoje | 4 a 5 de 8 formatos cabem nos planos de retrato; o diagrama pede de 1 a 2 dias (esteira linear) a 1 a 2 semanas (diagrama completo) de engenharia, e a checagem foi o maior custo medido no projeto [S27] |
| Oferta testável com poucos recursos | Médio | Isca digital (cheat sheet em PDF) e afiliado são baratos; o gargalo é autoridade, não produto. Nada na pipeline cobre página de captura, e-mail ou PDF |

Achado de contexto [F/I]: dos 7 temas legíveis nas amostras (5 legendas lidas e 2 títulos da grade do ByteByteGo), 5 são de IA/LLM, 1 de redes e 1 de DSA [S1][S2][S3][S5][S8][S10]. O ByteByteGo anuncia "Become an AI Engineer" na home [S11] e o Full Cycle vende um "MBA em Engenharia de Software com IA" [S10][S22]. Um nicho só de system design pode estar perdendo espaço para "engenharia de IA" (amostra pequena).

Confiança: **média** para panorama de concorrentes, ofertas, preços e afiliado (leitura de site oficial); **baixa** para demanda real, retenção e conversão (nenhuma view; só 5 posts com legenda e métricas, 1 por perfil e 2 no ByteByteGo).

## 1. Método e limites

- **Instagram: 12 de 12 acessos usados**, só páginas públicas, sem login. Perfis (7 cargas): @bytebytego ×2, @trilhainfo ×2, @algomasterio, @interviewready_, @devfullcycle. Posts (5): 1 do AlgoMaster, 2 do ByteByteGo, 1 do trilhainfo, 1 do Full Cycle. Nenhum acesso extra, nenhuma tentativa de contornar bloqueio.
- **O leitor resume com modelo pequeno.** Copiei o que devolveu e marquei como `descrição lida`. Seguidores, URLs e datas da grade aparecem; legendas e métricas só nas páginas de post. Views: indisponíveis em todas.
- **Checagem independente das datas [F]:** os 60 itens da grade têm URL com código de post. Decodifiquei o carimbo de tempo embutido no código (conhecimento prévio da estrutura do ID, não confirmado pelo Instagram) e comparei com a data do leitor: **60 de 60 batem, diferença de no máximo 1 dia** (fuso). Isso valida data e URL, não legenda nem tipo. O mesmo código deu a idade dos 5 posts lidos.
- **Inconsistência registrada:** o primeiro item de duas grades (ByteByteGo e InterviewReady) tem data antiga (2024-07-31 e 2023-08-13) apesar de a lista vir "do mais recente"; provavelmente são itens fixados [I]. O Full Cycle tem um item de 2026-02-14 no topo, igualmente fixado [I].
- **Tipos de item** (`Photo`, `Clip`, `Carousel`) são do leitor. As "descrições" do tipo "May be a selfie of mirror" são texto automático do Instagram; não usei para descrever vídeo.
- **Fora do Instagram:** sites oficiais lidos no HTML bruto (preços, afiliados), API pública do TabNews e do GitHub, WebFetch e WebSearch. A busca não indexa o Instagram, e em português "system design" se mistura com "design system" (UI): a descoberta de perfis brasileiros foi fraca [I].
- **Kit:** o servidor MCP `motion-kit` estava fora do ar; li o checkout `~/projetos/motion-kit` (HEAD `a2dcca3`). Os componentes citados também existem no SHA do pin `527c708` (conferido com `git cat-file`) e o pacote instalado em `video/node_modules` (0.3.0) exporta `Pipeline`, `AnimatedGraph`, `TxTimeline`, `CodeWalkthrough` e `ComplexityChart`.
- Nenhum arquivo do repositório foi alterado. Downloads e scripts ficaram em `scratchpad/nichos-work/sysdesign/`.

## 2. Perfis observados (2026-10-06)

Amostra: os 12 itens que a grade pública de cada perfil mostrou, na ordem da página. Critério: o que o leitor listou, sem filtro. Tamanho real: 12 por perfil, 60 no total; 5 legendas lidas.

| Perfil | Mercado/idioma (evidência) | Seguidores | Porte | Grade: tipos e janela de 90 dias | Cadência | CTA e oferta | Animação/apresentador declarados |
|---|---|---|---|---|---|---|---|
| **@bytebytego** [S1] | en: bio, CTA e legendas em inglês; site em inglês; país da audiência não comprovado | 559 mil | Grande | 12 de 12 `Photo`, 0 clipes; 7 dentro de 90 dias | 11 posts de 2026-06-24 a 2026-09-10 (uns 2 por semana no início, espaçando depois); nenhum nos 26 dias antes da consulta | Bio: "free newsletter for 5x more diagrams"; legenda: PDF grátis de 368 páginas por e-mail [S2]; bundle de 8 cursos de texto ilustrado e ByteByteGo Live [S11][S12][S14] | Cursos "text-based" com ilustrações [S11]; animação no Instagram não declarada |
| **@algomasterio** [S4] | en: bio "Master DSA and System Design with visual explanations"; site em inglês; preços exibidos em R$ ao abrir desta máquina (localização provável no Brasil, não confirmada) [S15] | 394 mil (verificada) | Grande | 12 de 12 clipes; 11 dentro de 90 dias; 3 URLs sob @ashishps_1 (fundador) | 9 itens entre 2026-09-27 e 2026-10-06 | Link algomaster.io; Premium R$ 152/mês, R$ 392/ano, R$ 785 vitalício [S15] | Site: "visual animations", "Interactive Animations"; fundador "ex-Amazon, Adobe" |
| **@devfullcycle** [S9] | pt-BR: bio, legenda e site em português; preço do MBA não visível | 149 mil (verificada) | Médio a grande, adjacente | 4 clipes e 8 carrosséis; 11 dentro de 90 dias | 11 itens em 13 dias (2026-09-24 a 2026-10-06) | Legenda: "Comente MBA"; bio: fale-conosco; MBA Arquitetura (18 meses, módulo "System Design e Design Docs"), preço só sob contato [S22] | Não declarado |
| **@trilhainfo** [S7] | pt-BR: bio e legenda em português; Dinamos com receita em R$ [S21] | 21,3 mil | Pequeno | 12 de 12 clipes; 6 dentro de 90 dias | 5 itens de 2026-07-08 a 07-13, depois 1 em 2026-09-25 | Link dinamos.net; plataforma de system design em pt, hoje gratuita [S21] | Não declarado (plataforma tem "simuladores visuais") |
| **@interviewready_** [S6] | en: bio em inglês | 4.096 | Muito pequeno, parado | 1 clipe, 8 imagens, 3 carrosséis; **0** dentro de 90 dias (último 2024-07-31) | Parada | Link interviewready.io; cursos sem preço visível [S20] | Não declarado |

Candidatos encontrados e **não verificados** no Instagram (limite de acessos): Aced, ex-Exponent (@aced__io, handle lido no site oficial [S18]); Wilson Neto, canal "Engenharia de Software Além do Código" no YouTube, sem Instagram localizado [S26]. Descoberta de contas brasileiras dedicadas a system design ficou incompleta [I].

**Complemento dos perfis** (campos pedidos no brief; as URLs de cada perfil estão na seção 12):

| Perfil | Tema | Público | Problema | Gancho (só pela legenda lida) | Formato visual (só pelo que a descrição diz) | Limitações de acesso |
|---|---|---|---|---|---|---|
| @bytebytego | System design, redes, infraestrutura e IA/LLM | Engenheiros que se preparam para entrevistas (site) | Preparar entrevistas e aprender arquitetura (site e bio) | Pergunta-título em 2026-08-26; anúncio em 2026-09-10 | Imagem de 1 slide com diagrama; legenda longa em prosa | 2 de 12 legendas lidas; sem views; leitor resume a página |
| @algomasterio | DSA e system design | Candidatos a entrevistas técnicas | Preparar entrevistas com padrões e visualizações | Título curto com hashtags ("Big-O Race") | Clipes; o leitor falou em "comparação visual em formato de corrida" (inferência dele); animação só declarada na bio e no site | 1 de 12 legendas lidas; 3 URLs sob a conta do fundador |
| @devfullcycle | Arquitetura e IA aplicada | Devs que querem sistemas de grande porte | Carreira e salário (bio) | Aviso de risco ("Seu agente pode acabar seguindo instruções de um site malicioso...") | Carrosséis e clipes; o formato do clipe não é verificável | 1 de 12 legendas lidas; "Comente MBA" leva a contato comercial, sem preço público |
| @trilhainfo | Sistemas distribuídos e IA | Devs de língua portuguesa | Aprender system design em português (Dinamos) | Pergunta coloquial ("Jev faz um site aí pra mim?") | Clipes; as descrições automáticas não permitem concluir o formato | 1 de 12 legendas lidas; 2 links na bio, só 1 visível |
| @interviewready_ | Curso de system design em vídeo | Engenheiros que se preparam para entrevistas | Preparar entrevistas de system design | Nenhuma legenda lida | Imagens e carrosséis (2023 a 2024) | Conta parada; nenhuma legenda lida |

## 3. Publicações lidas (página do post)

Páginas individuais abertas: 3 Reels (AlgoMaster, trilhainfo, Full Cycle) e 2 posts de imagem (ByteByteGo); nos outros 55 itens da grade não foi possível ver legenda nem métricas dentro do limite de acessos. Idade calculada pelo código do post. Curtidas e comentários são de uma só leitura; views indisponíveis. A razão "curtidas por seguidor" é só ordem de grandeza: idades e formatos diferentes, n=1 por perfil.

| Perfil e data | Tipo | Gancho (legenda) | CTA | Curtidas / comentários | Idade | Curtidas ÷ seguidores [I] |
|---|---|---|---|---|---|---|
| ByteByteGo, 2026-08-26 [S2] | `Photo` de 1 slide; alt: diagrama da pilha de protocolos | Pergunta-título "What Keeps the Internet Running?"; legenda em prosa, sem link de fonte técnica | Newsletter semanal para receber PDF grátis de system design (368 páginas) | 1,1 mil / 12 | 41 dias | 0,20% |
| ByteByteGo, 2026-09-10 [S3] | `Photo` de 1 slide | Anúncio "ByteByteGo Live: learn AI live from real builders"; cita "~4% completion" de cursos online | Link go.bytebytego.com/live-launch-youtube | 265 / 5 | 26 dias | 0,05% |
| AlgoMaster, 2026-10-06 [S5] | Clipe | Título curto "Big-O Race" e hashtags (#dsa #interview #coding #algorithm #algomaster) | Nenhum visível | 14,1 mil / 47 | cerca de 12 a 14 h | 3,6% |
| trilhainfo, 2026-09-25 [S8] | Clipe | "Jev faz um site aí pra mim?" (tema: IA/LLM) | Nenhum visível | 218 / 5 | 11 dias | 1,0% |
| Full Cycle, 2026-10-06 [S10] | Clipe | "Seu agente pode acabar seguindo instruções de um site malicioso sem que você perceba." (aviso de risco; tema: segurança de agentes) | "Comente MBA" (palavra-chave nos comentários) | 13 / 0 | cerca de 10 h | 0,009% |

Leituras [I]:
- O único Reel de conceito técnico lido (AlgoMaster, Big-O) teve 14,1 mil curtidas em cerca de 13 h numa conta de 394 mil seguidores. A imagem estática do ByteByteGo teve 1,1 mil em 41 dias numa conta 1,4 vez maior. Com n=1 e sem views, isto é hipótese: **Reel animado de conceito pode render mais que diagrama estático [H]**.
- Os dois Reels brasileiros lidos não são de system design (IA/agentes). O CTA brasileiro é por palavra-chave nos comentários, que alimenta contato comercial (venda de MBA por "Solicitar Contato").
- A única legenda longa lida (ByteByteGo) não traz fonte oficial. Fonte por afirmação seria diferenciação real [H].
- Mecanismos para estudar, sem copiar: pergunta no título; isca digital grátis por e-mail; fundador publicando também na conta da marca (3 URLs sob @ashishps_1 na grade do AlgoMaster; colaboração provável, não verificada); CTA por palavra-chave.

## 4. Ofertas, preços e afiliados (verificados em 2026-10-06)

| Oferta | URL | Preço e moeda como a página mostrou | Observação |
|---|---|---|---|
| ByteByteGo (bundle de 8 cursos; "One Year Access" e "Lifetime") | https://bytebytego.com/pricing | **Não verificado**: preços carregados no cliente (o HTML bruto tem indicador de carregamento) | Cursos em texto ilustrado; FAQ: "Refunds are not available for the courses" [S11]. Resenha de afiliado de 2026-05-11: US$ 84,00/ano, INR 3.500, CAD 84,00, SGD 82,97 [S25]. Trechos de busca de outros blogs de afiliado citam US$ 79 a US$ 228/ano e US$ 499 vitalício em promoção; não conferi nessas páginas e os valores conflitam |
| ByteByteGo Live | https://live.bytebytego.com/ | Sem valor no texto | Associação anual com todos os cursos; reembolso integral em 7 dias se não concluiu curso [S14] |
| AlgoMaster Premium | https://algomaster.io/premium | R$ 152 (1 mês); R$ 392 (1 ano, riscado R$ 523, 25% OFF); R$ 785 (vitalício, riscado R$ 1.308, 40% OFF); pagamento único | Moeda possivelmente localizada por IP [H]; plataforma internacional que exibe preço em reais [S15] |
| Hello Interview Premium | https://www.hellointerview.com/ | $ 47 (1 mês, riscado $ 59); $ 78 (1 ano, riscado $ 119); $ 275 (vitalício, riscado $ 399) | Símbolo `$` sem nome da moeda; "Does not auto-renew"; histórias de sucesso citam ofertas de emprego [S16] |
| DesignGurus, Grokking the System Design Interview | https://www.designgurus.io/ | $ 148 ("Discounted price for Your Region"); Fundamentals $ 123 | Preço regional: o valor para o Brasil não foi verificado [S17] |
| Dinamos (pt-BR) | https://dinamos.net | R$ 0 desde 2025-12; antes "assinatura única e acesso vitalício", preço não divulgado | Autor declara cerca de R$ 30.000 em um ano com 230 pessoas ativas, "suficiente para cobrir os custos fixos" [S21] |
| Full Cycle, MBA Arquitetura | https://mba.fullcycle.com.br | Não visível ("Solicitar Contato"); nenhum preço verificado | 18 meses, 600 h, módulo "System Design e Design Docs"; início em 2026-10-05 (pré-matrícula com desconto) ou 2026-12-07 [S22] |

**Afiliado e programas de criador (condições lidas na página oficial, 2026-10-06)**

| Programa | Condições verificadas | O que falta |
|---|---|---|
| Aced (ex-Exponent), https://www.aced.io/affiliate [S18] | "earn 20% recurring commission on sales every month", incluindo renovações de assinatura; candidatura em 2 minutos, resposta em até 3 dias úteis; link de rastreio e kit de marca; "for top tech creators" | Moeda, cookie, pagamento mínimo e critério de elegibilidade não informados |
| ByteByteGo, https://bytebytego.com/be-an-affiliate [S13] | "at least 5,000 fans"; "generous revenue sharing" (percentual não informado); cookie de 30 dias; saque mensal por PayPal; inscrição por e-mail | Percentual de comissão. O critério de 5.000 "fans" deixa, a princípio, um perfil novo de fora |
| Codemia, https://codemia.io/creators [S19] | Compensação é 1 ano de Premium grátis, não comissão; exige conteúdo público de 10 minutos ou mais ("A sixty-second feature tour does not count") e divulgação | Não serve a Reels |
| Hello Interview, DesignGurus, AlgoMaster, InterviewReady | **Não verificado** (nenhuma página oficial de afiliados encontrada ou lida) | Tudo |
| Pt-BR: Alura (Full Cycle não pesquisado) | **Não verificado**: a página oficial do programa do Alura devolveu 403; agregadores de terceiros citam 8% a 12% sem fonte oficial lida | Tudo |

## 5. Cadeia: vídeo, pessoa, necessidade, produto, motivo para comprar de nós

1. **O vídeo atrai quem.** [F] Os concorrentes declaram o mesmo público: engenheiros que se preparam para entrevistas ("Ace Every Stage of Your Next Technical Interview" [S11], "Master Software Engineering Interviews" [S15]) e, no Brasil, quem quer "perfis mais bem pagos e desejados do mercado" [S9]. [I] Um Reel de 20 a 45 s de conceito atrai estudantes e devs júnior/pleno curiosos; a parcela que compra é menor e não foi medida.
2. **Essa pessoa precisa de quê.** [I] Um caminho de estudo, prática com devolutiva (simulado, feedback de IA, banco de perguntas) e confiança para explicar trade-offs em voz alta. [F] O título de um post no TabNews (autor: professor de inglês que atende devs brasileiros) afirma que a entrevista em big tech "é conversa técnica em inglês" [S26]; conteúdo em inglês e em português pode importar [H].
3. **Qual produto ajuda.** [F] Planos de acesso (US$ 47 a US$ 275; R$ 152 a R$ 785), curso de texto ilustrado, associação com cursos ao vivo, MBA por contato comercial. [F] Do lado gratuito: PDF de 368 páginas [S2], repositório com 373 mil estrelas [S23], plataforma Dinamos em pt-BR [S21], comunidade no Discord [S26].
4. **Por que compraria de nós.** Não há evidência. Hipóteses: **(H1)** referência curta em pt-BR e inglês onde cada número e seta tem fonte oficial citada na tela (a pipeline faz isso por contrato; a legenda lida do ByteByteGo não cita fonte); **(H2)** um pacote pequeno e barato, abaixo do 1 mês do Hello Interview (US$ 47), para quem ainda não quer uma plataforma; **(H3)** indicação de plataforma por afiliado, em que o canal vale pela curadoria. As três dependem de confiança, e os concorrentes vendem credencial pessoal (fundador "ex-Amazon, Adobe" [S15]; "Written by Amazon Bestselling Authors" [S11]; instrutores do Google e Meta e Kent Beck [S3]; "Engineering Manager | Sistemas Distribuídos, 18 anos em tech" [S7]).

## 6. Autoridade, concorrência, alternativas gratuitas, atendimento, manutenção, entrega

- **Autoridade necessária: alta.** [F] As marcas observadas com fundador à frente (AlgoMaster, ByteByteGo, trilhainfo, Full Cycle) apoiam-se numa pessoa com currículo declarado; o autor do trilhainfo se apresenta como Engineering Manager em sistemas distribuídos, e uma entrevista de 2024 o coloca na Workday [S29]. Um canal de avatar ilustrado com voz sintética não tem credencial [I]. Decisão do dono: quem assina e quem revisa a precisão técnica (próprio dono, revisor nomeado, ou canal sem rosto que ancora a confiança só nas fontes). O apresentador (Notionists, CC0) não é credencial.
- **Concorrência.** [F] Saturada no topo em inglês: ByteByteGo (newsletter com "Over 1,000,000 Subscribers" e "Over 5 million people", autodeclarados [S11]), AlgoMaster (1 milhão de alunos, autodeclarado [S15]), Hello Interview, DesignGurus (188 mil alunos, autodeclarado [S17]), Codemia, Aced. Em português encontrei menos oferta de Reels dedicados (um perfil parcialmente dedicado de 21 mil seguidores, um adjacente de 149 mil) [S7][S9]; a ausência de outros pode ser limite da minha busca [I].
- **Alternativas gratuitas fortes.** [F] System Design Primer (373.411 estrelas, último push 2026-09-15, licença `Other` no GitHub: conferir antes de reutilizar) [S23]; o PDF gratuito do ByteByteGo [S2]; Dinamos gratuito e em português [S21]; comunidade Craft & Code Club [S26]; documentação oficial e blogs de engenharia.
- **Atendimento.** Isca digital e afiliado: baixo (e-mail). Produto pago: dúvidas de conteúdo, pedido de reembolso, correção de erro técnico. [F] Os concorrentes tratam reembolso de modos opostos: o ByteByteGo diz que cursos não têm reembolso [S11], o Live dá 7 dias [S14]. Política própria a definir [H].
- **Manutenção.** Alta e contínua: conteúdo técnico envelhece (versões, quotas, preços de nuvem). Cada afirmação precisa de `retrieved_at` e, para este nicho, da versão da documentação. O contrato tem `Source.retrieved_at` mas nenhum campo de versão (`app/pipeline/schemas.py`, linhas 90 a 99) [S27].
- **Entrega.** PDF por e-mail e página de captura: fora da pipeline (não há export por plataforma, título, capa nem upload) [S27].

## 7. Oferta própria simples e afiliado

Ordem sugerida de teste, da mais barata para a mais cara:

1. **Lista de espera ou newsletter com isca digital.** Cheat sheet de system design (por exemplo, 20 conceitos de 1 página, cada afirmação com a fonte oficial). Modelo observado: o ByteByteGo troca um PDF de 368 páginas por e-mail na legenda [S2]. O que medir: e-mails capturados por mil views.
2. **Pacote pago pequeno** (e-book ou kit: checklist de entrevista, perguntas e rubrica de resposta). Âncoras de preço verificadas: US$ 47 por 1 mês no Hello Interview [S16], R$ 152 por 1 mês no AlgoMaster [S15]. Preço próprio: não há dado; é o que o teste precisa descobrir [H].
3. **Afiliado.** Único com comissão em dinheiro verificada: Aced, 20% recorrente [S18]. ByteByteGo convida quem tem pelo menos 5.000 "fans" e não informa o percentual [S13]. Divulgação de afiliado: o programa do Codemia cita a obrigação de divulgar (FTC) [S19]; regra brasileira: não verificada.

## 8. Produção

### 8.1 Oito formatos de Reel de 20 a 45 s e os planos de retrato de hoje

Planos aceitos em retrato (ADR 014, `PORTRAIT_SHOT_KINDS`): `photo`, `broll`, `number`, `keyword`, `stamp`, `lower_third`, `compare` (`side`, `before_after`, `scale`), `chart` (`bar`, `bar_horizontal`, `line` com rótulos de ano ou data, `share`) [S27]. Ritmo de 2 a 4 s por plano dá de 5 a 22 planos por Reel de 20 a 45 s (cerca de 10 no meio da faixa). Toda `claim` exige fonte e a tela não calcula razão nem soma que não esteja numa ficha [S27].

| # | Formato (exemplo) | Planos de hoje | O que exige adaptação | Fonte oficial exigida | Encaixe hoje |
|---|---|---|---|---|---|
| 1 | **Os noves da disponibilidade**: 99,9% vs 99,99% vs 99,999% e o tempo fora do ar por ano | `keyword` (pergunta), 3 × `number`, `compare` `before_after` | Nenhuma de contrato. As unidades da tabela vêm misturadas (horas, minutos), o que impede `scale` (exige a mesma unidade) | Tabela do SRE Book [S24] (números; licença CC BY-NC-ND) | **Alto** |
| 2 | **Limite que derruba sistema**: quota ou limite oficial de um serviço | `number`, `compare`, `keyword` | O rodapé mostra a fonte; o contrato não tem campo de versão da documentação (ver seção 6) | Documentação do fornecedor; quotas mudam | **Alto a médio** |
| 3 | **A contra B**: fila contra log, SQL contra NoSQL, REST contra gRPC | `compare` `side` com texto, `keyword`, `number` | Sem número reconhecível o `compare` mostra texto lado a lado (existe no template); falta o diagrama | Documentação de cada produto (fonte "interessada") mais uma segunda fonte independente | **Médio** |
| 4 | **Como a empresa X resolveu Y**: caso de blog de engenharia | `number`, `stamp`, `lower_third`, `chart` (`line` em anos), `keyword` | Logos de marca não entram (política do template); fonte é o próprio blog da empresa | Blog de engenharia (interessado) | **Médio** |
| 5 | **Ordens de grandeza de latência** | `compare` `scale`, `chart` `bar_horizontal` | Barras lineares escondem 1 ns ao lado de 100 ms; o template não expõe escala logarítmica e `scale` exige unidades iguais; números são aproximações datadas | Tabela de latência com fonte datada | **Baixo a médio** |
| 6 | **Caminho de uma requisição ou padrão** (cache-aside, CQRS, saga) | `keyword` por passo e `broll` de data center (ilustração) | **Diagrama**: `network` ou esteira em retrato (8.2) | Uma afirmação com fonte por nó e por seta | **Baixo** (núcleo do nicho) |
| 7 | **Conceito em 30 s** (consistent hashing, idempotência, backpressure) | `keyword`, `compare` `before_after` com texto, `broll` | Animação do conceito (grafo, esteira, linha do tempo de transações) não existe como plano | Paper, RFC ou documentação | **Baixo** |
| 8 | **Estimativa de capacidade** (QPS, armazenamento) | `number` encadeado | O contrato proíbe valor calculado que não esteja numa ficha; seria preciso um tipo de afirmação derivada com fórmula e entradas | Entradas citáveis; a conta é do roteiro | **Baixo** |

Dependências por tipo [F/I]:
- **Filmagem:** nenhuma. O apresentador é um personagem ilustrado opcional em janela (ADR 013).
- **Demonstração de produto:** impossível hoje (sem gravação de tela). Console de nuvem e interface de ferramenta não podem aparecer; trecho de código só como plano novo (`CodeBlock` e `CodeWalkthrough` existem no kit, sem plano).
- **Consistência de personagem:** resolvida pela identidade fixa do Notionists (CC0); sem outros personagens.
- **Pesquisa complexa:** alta. Ficha com citação literal por afirmação, fontes de fornecedor marcadas como interessadas (`Source.interested`: "nenhum fato só com ela"), segunda fonte independente por julgamento humano no gate 1 [S27].
- **Licença de ativos:** baixa para imagens (ícones Lucide ISC; o template exclui Simple Icons por serem marcas, `video/src/ICONS.md`; B-roll de bancos entra como ilustração). **Alta para textos-fonte:** o SRE Book é CC BY-NC-ND [S24] e o Primer aparece como `Other` [S23]. Diagramas de terceiros não podem ser copiados.

### 8.2 Diagrama em retrato: o que existe e quanto custa ligar

**O que existe [F].** O plano `network` já está no contrato e no template (`ExpandingNetwork`, canvas de 1280×720 ampliado pela altura, layout `radial` ou `layered`) mas **só em paisagem**: a ADR 014 deixa rede, mapa, linha do tempo, árvore e documento fora do retrato [S27]. Os nós só têm os tipos `person`, `family`, `company`, `bank`, `government` e `other`, com um ícone Lucide por tipo, e cada aresta exige `claims`. O demo do kit para a rede é 1920×1080 (alvo de 40 nós) [S28]. No kit, `Pipeline` ("estilo ByteByteGo em 9:16", largura padrão 920 px), `AnimatedGraph`, `TxTimeline`, `CallStack`, `CodeWalkthrough`, `ComplexityChart`, `TokenStream` e `ContextWindow` existem e **não viraram plano** [S28].

**Espaço útil em retrato [I, aritmética sobre constantes do código, sem render].** Quadro 1080×1920; área segura vertical: 288 px no topo, 500 px na base. A fonte do plano ocupa de 288 a 438 px. A legenda queimada (54 px, entrelinha 1,25) sobe de 1420 px: com 2 linhas o texto começa perto de 1285 px. Sem apresentador sobra uma faixa de cerca de 780 a 850 px de altura. Com a janela do apresentador (28% da largura = 302 px, proporção 3/4, cerca de 403 px de altura, margem de 90 px) numa quina de cima, o diagrama abaixo dela fica com cerca de 430 a 500 px (erro de cerca de 60 px: não conferi como o kit soma a margem à área segura). Diagrama de 4 a 6 nós em retrato provavelmente exige tirar o apresentador nesse plano (decisão do dono).

| Opção | Escopo | Trabalho estimado (por analogia com PRs anteriores) | Riscos |
|---|---|---|---|
| **0. Sem diagrama** | Só os planos de hoje (formatos 1 a 5) | Zero | Fica sem o formato central do nicho: concorrentes vendem "visual explanations" e "animations" [S4][S15] |
| **C. Novo plano `pipeline`** (esteira linear de 3 a 5 estágios, kit `Pipeline`) | Contrato (union, retrato, `check`, `shots`, `text_fit`, regra de cantos do apresentador), template, skills, testes, ADR curta | Cerca de 15 arquivos e 300 a 500 linhas. Analogias: ADR 014 mexeu em 18 arquivos (cerca de 444 linhas inseridas) mais 3 correções visuais em 2 dias; ADR 015, 14 arquivos e 302 linhas. Estimativa: 1 a 2 PRs, 1 a 2 dias de trabalho com agentes, mais 1 a 2 correções visuais | Só fluxo linear; sem ramificação (acerto ou falha de cache); rótulos curtos |
| **A. `network` liberado em retrato com nós de software** | Novos tipos de nó (serviço, banco, cache, fila, cliente), ícones, canvas retrato, layout vertical, ADR (emenda 011 e 014) | Contrato menor que o de C, template maior (câmera e layout em retrato). 2 a 3 PRs, 2 a 4 dias. Possível PR no motion-kit (repositório separado no GitLab) e novo pin, como em `38702a0` | `ExpandingNetwork` foi pensado para 1920×1080; rótulos de seta têm tamanho fixo no kit (já houve defeito); a câmera de afastamento não foi testada em retrato |
| **B. Plano `diagram` completo** (setas direcionais, síncrono/assíncrono, numeração, pacotes fluindo, `AnimatedGraph` com auto-layout) | Contrato novo, layout automático (o kit pede x e y), skills do roteirista e do verificador, vários testes | 4 a 6 PRs, 1 a 2 semanas de calendário (estimativa de baixa confiança) | O verificador precisa checar cada seta; o custo de checagem sobe com o número de setas |

Qualquer opção, mais a ADR: mudar o `episode.json` exige nova ADR (`CLAUDE.md` §6). Cada versão visual vira uma versão do vídeo-régua, com sonda de CPU antes. Cada seta é uma afirmação com fonte; um diagrama de 5 setas é 5 fichas com citação literal.

### 8.3 Custos por tipo (premissas e intervalos)

Base: seção 1 do brief e `data/benchmarks/episodio-votorantim-dinheiro.md` (vídeo de 93,1 s, 10 cenas, 21 planos, agentes: cerca de 1,6 milhão de tokens e 1 h 31; "Horas humanas: não medidas") [S27].

| Item | Faixa | Premissa ou base |
|---|---|---|
| **Setup: diagrama em retrato** | 0 (opção 0); 1 a 2 dias (C); 2 a 4 dias (A); 1 a 2 semanas (B) | Analogia por PRs anteriores; horas humanas do projeto não são medidas; baixa confiança |
| **Setup: biblioteca de fontes e glossário do tema** | Não medido | Cada tema novo exige baixar e fichar documentação oficial; o benchmark reaproveitou fichas e por isso não mede esse passo |
| **Setup: conta, identidade, página de captura, PDF da isca** | Fora da pipeline; não medido | Sem ferramenta no repositório; usar serviço gratuito exige conferir termos [H] |
| **Recorrente: agentes por Reel** | **0,3 a 0,8 milhão de tokens e 20 a 45 min** se as fichas já existem | Proporção de 20 a 45 s sobre os 93 s do benchmark (1,6 milhão de tokens, que o próprio registro chama de piso, e 91 min). Pode ser maior: o custo dependeu do número de rodadas de checagem (5), e a taxa de erro em tema técnico não foi medida |
| **Recorrente: voz** | Kokoro: cerca de 0,7 s por s de áudio (14 a 32 s por Reel). Gemini final: 3 chamadas/min e 10/dia na camada gratuita | Seção 1 do brief e CLAUDE.md §1; cena com pausa vai numa chamada só |
| **Render** | Prévia 720×1280: cerca de 15 a 90 s | Proporção de 40 a 110 s medidos para um curto de ~55 s (uma sessão, não benchmark formal); 1080×1920 final não medido (2,25 vezes os pixels da prévia) |
| **Revisão humana** | Não medida; **a medir** nos 3 primeiros Reels | Gates 1, 2, 3 e 4 por Reel; em tema técnico, soma a conferência da precisão |
| **Dinheiro** | US$ 0 | Regra do projeto; limites reais: 10 chamadas/dia do TTS e a cota do plano do dono (não medida) |

## 9. Precisão e risco

- **Fonte oficial por afirmação [F].** Exige fonte: número, limite, quota, versão, comportamento padrão de produto, benchmark, classificação (CAP e consistência), caso de empresa, preço, regra de processo seletivo. Em diagrama, cada nó e cada seta é uma afirmação (no contrato de `network`, `claims` por aresta).
- **Primeira passada erra bastante [F].** Na 1ª checagem do episódio de teste (tema histórico e empresarial), 5 de 20 frases (25%) e 6 de 27 planos (22%) foram reprovados; passou só na 5ª rodada [S27]. Em tema técnico a taxa não foi medida.
- **Dados prontos do kit não servem como fato [F/I].** `src/data/databases.ts` traz frases absolutas como Cassandra "Nunca fica indisponível" e a classificação PostgreSQL = CP, MongoDB = AP [S28]. Afirmações assim precisam de fonte e ressalva; usá-las no vídeo violaria a regra 2 do projeto.
- **Fonte interessada [F/I].** Documentação de fornecedor sobre o próprio produto se encaixa em `Source.interested` (fato só com ela gera alerta) [S27]. Quem decide é o gate 1.
- **Dados que envelhecem [I].** Quotas, versões e preços mudam; o contrato guarda `retrieved_at`, não a versão.
- **Licença do texto-fonte.** O SRE Book é CC BY-NC-ND 4.0 ("Copyright © 2017 Google, Inc. Published by O'Reilly Media, Inc.") [S24]; o Primer aparece como `Other` [S23]. Número e fato são citáveis; reproduzir texto ou tabela em canal comercial é risco jurídico a confirmar com quem entende [H].
- **Marcas e diagramas de terceiros.** O template não usa logos (política de ícones, ADR 011, decisão 10). Não copiar diagramas do ByteByteGo ou de outro (direito autoral; regra 8 do brief).
- **Promessa de emprego ou renda.** Concorrentes exibem "Landed ~$1M TC offer from Stripe" [S16]. O canal não deve prometer oferta, cargo ou salário. Regras de publicidade e de afiliado no Brasil: **não verificadas** nesta pesquisa; o programa do Codemia menciona a exigência de divulgação (FTC) [S19].
- **Saúde e regulação financeira:** baixo risco; o nicho não toca saúde nem investimento.
- **Plataforma [H].** Política do Instagram para voz sintética e conteúdo em série: não verificada aqui (o CLAUDE.md §12 trata a do YouTube).

## 10. Separação final

**Fatos observados (com URL):** perfis, seguidores e grades da seção 2; 5 posts lidos; preços e condições de afiliado da seção 4; Dinamos de R$ 30.000, 230 pessoas ativas e passagem a gratuito [S21]; 373 mil estrelas do Primer [S23]; 5 de 7 temas legíveis são de IA; ByteByteGo: 12 de 12 itens `Photo`.

**Inferências:** a comparação de curtidas por seguidor; que a cadência do AlgoMaster indica produção quase diária; que o nicho se desloca para IA; que o apresentador reduz o espaço do diagrama a cerca de 430 a 500 px; os intervalos de custo por proporção.

**Hipóteses a testar:** (H1) fonte oficial visível na tela como diferencial; (H2) pacote barato abaixo de US$ 47 ou R$ 152; (H3) afiliado Aced a partir de um canal novo; Reel animado de conceito rende mais que imagem estática; moeda do AlgoMaster localizada por IP; revisão humana de 30 a 90 min por Reel.

## 11. O que falta antes de investir mais

1. **Views, retenção e salvamentos por Reel** (invisíveis em páginas públicas): pedir a um criador do nicho ou rodar teste próprio de 4 vídeos, como o CLAUDE.md §12 já prevê para outros recortes.
2. **Amostra brasileira maior:** busca manual no Instagram por hashtags de system design e sistemas distribuídos, 10 a 20 contas com seguidores e cadência. Nesta rodada, o limite de acessos e a busca fraca deixaram só 2 perfis (1 adjacente).
3. **Preço e comissão do ByteByteGo:** o preço é carregado no cliente e a comissão não está publicada; só e-mail (hi@bytebytego.com) resolve, com o mínimo de 5.000 seguidores.
4. **Taxa de erro da checagem em tema técnico** e tempo humano real: produzir 1 Reel-piloto de um tema fechado (formato 1, disponibilidade) e medir rodadas, tokens e minutos.
5. **Disposição a pagar em pt-BR:** teste de isca digital (e-mails por mil views) e de 1 pacote pago; o único dado brasileiro de preço é autodeclarado e terminou em gratuidade [S21].
6. **Decisão de autoridade:** quem assina e quem revisa.
7. **Decisão de diagrama:** C, A ou B (8.2), e se o apresentador sai nos planos de diagrama.
8. **Termos legais e de plataforma:** licença dos textos-fonte, divulgação de afiliado no Brasil, política do Instagram para voz sintética.

## 12. Fontes (consultadas em 2026-10-06, salvo indicação)

- [S1] https://www.instagram.com/bytebytego/ (2 leituras) · [S2] https://www.instagram.com/bytebytego/p/Dcgk_QCm_iw/ · [S3] https://www.instagram.com/bytebytego/p/DdHNtKgG0co/
- [S4] https://www.instagram.com/algomasterio/ · [S5] https://www.instagram.com/algomasterio/reel/DeJqtP4v9mA/
- [S6] https://www.instagram.com/interviewready_/
- [S7] https://www.instagram.com/trilhainfo/ (2 leituras) · [S8] https://www.instagram.com/trilhainfo/reel/DdtUqwNI72O/
- [S9] https://www.instagram.com/devfullcycle/ · [S10] https://www.instagram.com/devfullcycle/reel/DeKAQqWgBBE/
- [S11] https://bytebytego.com/ · [S12] https://bytebytego.com/pricing · [S13] https://bytebytego.com/be-an-affiliate · [S14] https://live.bytebytego.com/ e https://live.bytebytego.com/be-an-affiliate
- [S15] https://algomaster.io/ e https://algomaster.io/premium · [S16] https://www.hellointerview.com/ · [S17] https://www.designgurus.io/
- [S18] https://www.aced.io/affiliate e https://www.aced.io/ · [S19] https://codemia.io/creators · [S20] https://www.interviewready.io
- [S21] https://www.tabnews.com.br/trilhainfo/abri-mao-de-um-saas-que-faturou-r30000-esse-ano (publicado 2025-12-17, lido pela API pública do TabNews) e https://www.tabnews.com.br/trilhainfo/pra-passar-em-provas-de-system-design (2025-12-10)
- [S22] https://mba.fullcycle.com.br e https://www.fullcycle.com.br · [S23] https://github.com/donnemartin/system-design-primer (API pública do GitHub) · [S24] https://sre.google/sre-book/availability-table/ · [S25] https://reactjava.substack.com/p/review-is-bytebytego-a-good-place (2026-05-11; post de afiliado) e https://devopscube.com/bytebytego-discount/ (2026-10-01; links de afiliado, sem preços)
- [S26] https://www.tabnews.com.br/wilsonnetodev/clube-de-estudos-se-prepare-para-entrevistas-em-bigtechs, https://www.tabnews.com.br/willybr/uma-comunidade-gratuita-pra-trocar-ideia-sobre-system-design-algoritmos-estruturas-de-dados-ai-ddd-tests-e-muito-mais (só trecho de busca), https://www.tabnews.com.br/willybr/ama-dev-brasileiro-trabalhando-pra-fora-eua-15-anos-de-carreira-microsoft-mvp-ask-me-anything, https://www.tabnews.com.br/albertosenna/entrevista-tecnica-em-faang-nao-e-teste-de-codigo-e-conversa-tecnica-em-ingles (só o título; descrição do autor pela API pública do perfil)
- [S27] Repositório (leitura, nada alterado): `CLAUDE.md`, `docs/decisions/011-planos-editoriais.md`, `docs/decisions/014-perfil-vertical.md`, `app/pipeline/schemas.py`, `video/src/Editorial.tsx`, `ShotView.tsx`, `Scene.tsx`, `HostWindow.tsx`, `icons.tsx`, `ICONS.md`, `.claude/skills/roteiro-explicativo/planos.md`, `data/benchmarks/episodio-votorantim-dinheiro.md`, histórico do git
- [S28] Kit (leitura): `~/projetos/motion-kit/src/COMPONENTS.md`, `src/components/Pipeline.tsx`, `src/graph/ExpandingNetwork.tsx`, `src/data/databases.ts`, `examples/graph/ExpandingNetworkDemo.tsx`
- [S29] https://teomewhy.substack.com/p/teo-me-who-feat-flavio-mendes (2024-09-24; perfil profissional do autor do Dinamos) e https://flaviojmendes.gumroad.com/l/trilhainfo (conteúdo não lido; só o título indexado)
