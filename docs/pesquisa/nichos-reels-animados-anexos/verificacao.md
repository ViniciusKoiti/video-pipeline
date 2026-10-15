# Verificação independente da pesquisa de nichos

Consulta original: 2026-10-06. Verificação: 2026-10-06. Papel: verificador independente; **não aprovo nada, o dono decide**. Nenhum arquivo do repositório nem das fichas foi alterado. Este é o único arquivo gravado em `nichos/`; rascunhos, HTML bruto e scripts ficaram em `scratchpad/verif/`.

## 1. Método e limites

- **Páginas oficiais:** WebFetch (o leitor resume com modelo pequeno) e, nos itens de maior peso, conferência independente no HTML bruto com `curl` (GET simples, sem login, sem contornar bloqueio), lendo texto visível e JSON embutido. Onde escrevo "HTML bruto", o texto citado está na resposta do servidor. **PDFs:** texto extraído com `pdftotext` dos arquivos que o WebFetch salvou (EF EPI, manual DASN, Anexo XI, Resolução CVM 20, e-book do Sebrae).
- **Repositório:** só leitura (Read, Grep, `git`, `ffprobe` no preview existente). Nenhum código do projeto foi executado e nada foi alterado. Estado: `d1757d6`, com `Editorial.tsx` e `baixar_fonte.py` modificados e não commitados pelo dono (a mudança em `Editorial.tsx` é só l. 152).
- **Instagram: 10 de 10 acessos usados**, só páginas públicas, sem login, sem laço, 1 tentativa por URL: `/algomasterio/`, `/english_for_it/`, `/paulogala/`, `/imlucena/`, `/visualcap/`, `/minhas_financas_organizadas/`, `/garotadasplanilhas/`, `/peqart.app/`, `/reel/Dcy-WrMO8MH/` e, com o 10º, `/bytebytego/` (bônus, por pesar no argumento "o formato do nicho é imagem estática"). Nenhum bloqueio. Registro o que o leitor devolveu (respostas literais em `scratchpad/verif/instagram-leituras.md`); **nenhuma diferença de seguidores acima de 10%** (todas iguais ao valor da ficha).
- **O que não consegui reverificar por falta de acessos ao Instagram:** os demais perfis e Reels das fichas (por exemplo @the.freelance.coach e seu Reel, @howtogofreelance, @dicasmei, @freelasemcrise, @devspeakacademy e seu Reel, @inglespdevs, @speaktech.english, @trilhainfo, @devfullcycle, @interviewready_, @planetmoney, @comidaeconomia, @econotimebr, @seudinheiro, @visualeconomik, @economicsexplained, e as curtidas do Reel Big-O do AlgoMaster). Isso é limite de acessos, não bloqueio.
- **Convenções:** "l." é número de linha do arquivo citado; "L" seguido de número é a linha do CSV (cabeçalho = linha 1). WebSearch foi usada uma vez (Hotmart) e não sustenta nenhum veredito.
- **Datas dos CSVs:** o carimbo de tempo embutido no shortcode dos posts bate com as datas das fichas (X47), o que valida as contagens de janela de 90 dias.
- **Páginas que não consegui ler por inteiro:** FAQ do Aced (acordeão, X04); preço mensal e por faixa do beehiiv (cliente, A6); central de ajuda da Hotmart (só cabeçalho; usei a página de taxas e um terceiro, X35); `bytebytego.com/pricing` (a ficha já dizia que carrega no cliente; não tentei de novo).

## 2. Contagem de vereditos

| Bloco | CONFIRMADO | DIVERGENTE | NÃO VERIFICÁVEL | REFUTADO | Total |
|---|---|---|---|---|---|
| Itens 1 a 21 (A, B, C; o item 16 conta duas linhas, 16a e 16b) | 21 | 1 | 0 | 0 | 22 |
| D. Instagram (8 perfis, 1 Reel, 1 bônus) | 10 | 0 | 0 | 0 | 10 |
| E. Repositório (item iv dividido em a, b, c) | 7 | 1 | 0 | 0 | 8 |
| **Subtotal do pedido** | 38 | 2 | 0 | 0 | 40 |
| Verificações adicionais fora da lista (X01 a X53) | 41 | 5 | 7 | 1 | 54 |
| **Total** | 79 | 7 | 7 | 1 | 94 |

F (honestidade) e G (contradições) não têm veredito por linha; resultados nas seções 6 e 7.

## 3. Resumo para decisão

1. **Nenhuma afirmação central das fichas sobre preço, comissão ou número oficial foi refutada.** A única linha REFUTADO é um valor de trecho indexado que a própria ficha já tratava como divergente (Cambly US$ 50, X05b). Os problemas achados são de data, de atualização, de formulação e de premissa.
2. **Datas e vigência do guia do CONAR:** a página oficial sustenta notícia de 26/05/2026 e vigência em 1º de junho de 2026. As datas 12-13 de maio só existem em terceiros que discordam entre si (C16b). A frase "comissão de afiliado precisa ser divulgada" (economia) não está na página do CONAR (G1).
3. **Taxa da Hotmart:** a ficha MEI cita R$ 1 fixo (já marcado "não verificado"); a página oficial da Hotmart mostra "9,9% + R$ 2,49", e a ficha ingles-tech já traz a mudança de 21/09/2026 (via terceiro). Nenhuma ficha calcula margem com a Hotmart, então o erro está só no valor citado (X35). As contas de Kiwify (8,99% + R$ 2,49) estão certas.
4. **Odômetro:** o brief e duas fichas dizem que o odômetro do kit não tem plano; ele já está dentro do plano `number` (`Editorial.tsx` l. 3 e 92). Pipeline, Gauge e CodeWalkthrough realmente não têm (E4c).
5. **Ressalvas que afetam orçamento:** beehiiv Lite US$ 49 é cobrança anual na faixa de 1.000 inscritos (A6); Aced tem FAQ de pagamento e atribuição que não consegui ler (X04); Bling paga até 30 dias após nota fiscal (A1); preços da Speak Tech são promocionais (B9); curso How To Go Freelance é "Early Bird" (B12).
6. **Honestidade (F):** nenhuma frase descreve ritmo, corte, movimento, qualidade ou duração de vídeo como se assistido; há 2 casos limítrofes (S1, S2) e o resto é leitura de legenda, bio ou texto alternativo, sempre rotulada.
7. **Premissas de custo por Reel diferem entre fichas** e o 0,7 s/s do Kokoro (Fase 0, inglês) não é o medido em pt-BR (~0,9); o tempo de render de 40-110 s não tem registro no repositório (G3, X48, X49).

## 4. Registro por item

### A. Afiliado e plataformas

#### A1. Bling: 10% no 1º ano, CNPJ, resgate R$ 100
- **Afirmação:** mei-ficha.md §7 (l. 148): "Receba 10% do valor da mensalidade paga pelo seu indicado durante o primeiro ano de contrato"; resgate mínimo R$ 100,00, pedido do dia 01 ao 05; exige CNPJ ativo (CPF excluído); perfis-alvo incluem influenciadores.
- **URL:** https://www.bling.com.br/programa-de-parceiros
- **O que li:** WebFetch e HTML bruto (curl) coincidem. "Receba 10% do valor da mensalidade paga pelo seu indicado durante o primeiro ano de contrato"; "O resgate ... deve ser solicitado entre o dia 01 a 05 de cada mês, desde que o parceiro tenha atingido um montante de, no mínimo, R$ 100,00"; "Posso me cadastrar como pessoa física (CPF)? Não. O Programa de Afiliados do Bling é voltado exclusivamente para empresas"; "é necessário realizar o cadastro utilizando um CNPJ ativo"; perfis: influenciadores, consultores de vendas, agências de marketing, contadores. Consta também, e a ficha não registrou: "O prazo para pagamento é de até 30 dias corridos após a emissão da nota fiscal" (pode implicar nota fiscal do parceiro; termos completos não lidos).
- **Veredito: CONFIRMADO.** A ficha não registrou a menção à nota fiscal; como os termos completos não foram lidos, não dá para dizer se o parceiro precisa emitir nota.

#### A2. Aced: 20% de comissão recorrente
- **Afirmação:** sysdesign-ficha.md §4 (l. 90): "earn 20% recurring commission on sales every month", inclui renovações; candidatura em 2 minutos, resposta em até 3 dias úteis; link de rastreio e kit de marca; "for top tech creators"; moeda, cookie, pagamento mínimo e elegibilidade "não informados".
- **URL:** https://www.aced.io/affiliate
- **O que li:** WebFetch e HTML bruto: "The affiliate program for top tech creators. Share Aced with your audience and earn 20% recurring commission on sales every month"; "Apply in 2 minutes ... hear back within 3 business days"; "Get a custom tracking link and brand assets you can use"; "Get commission every month, including subscription renewals"; "Trusted by 100+ partners on top platforms: YouTube TikTok LinkedIn Medium". Sem moeda, cookie nem mínimo no texto visível. O FAQ tem 8 perguntas ("How much can I earn?", "When do payouts happen?", "How does attribution work?", ...) e as respostas não estão no HTML (acordeão recolhido, `aria-controls="faq-answer-..."`).
- **Veredito: CONFIRMADO.** Subafirmação "não informados": ver X04 (não lido, porque o FAQ não carrega no HTML; não é o mesmo que não existir).

#### A3. Cambly: US$ 30 por conversão; mínimo de gasto US$ 30 ou 50
- **Afirmação:** ingles-tech-ficha.md §7 (l. 119): "$30 per qualified conversion"; indicado precisa "start a Cambly subscription and spend at least $30"; pagamento mensal por PayPal, Alipay ou conta aprovada; "an engaged audience"; um trecho indexado dizia mínimo de US$ 50.
- **URL:** https://www.cambly.com/ambassador
- **O que li:** WebFetch e HTML bruto: "We'll pay you every time one of your referrals starts a Cambly subscription and spends at least $30 learning English with Cambly. The more people you send, the more you make, starting at $30 per qualified conversion!"; "Every month, we'll deposit your earnings into your electronic payment account (e.g. PayPal, Alipay, or other approved payment account)"; "An engaged audience: You are a charismatic leader with a large presence in social media or your local community." A busca por "$50" no texto e no HTML dá zero ocorrências. Sem restrição de país na página.
- **Veredito: CONFIRMADO.** O mínimo é US$ 30. "starting at $30" é piso (a ficha omitiu "starting at"). O "US$ 50" do trecho indexado é REFUTADO pela página oficial (ver X05b).

#### A4. Amazon Associados BR: livros 10%
- **Afirmação:** economia-ficha.md §5 (l. 138): "livros e livros digitais, comissão fixa padrão de 10%"; pagamento cerca de 60 dias após o fim do mês, mínimo R$ 30,00, janela de 24 h, divulgação conforme o código publicitário brasileiro; e-mail e mensagens só quando solicitados.
- **URL:** https://associados.amazon.com.br/help/node/topic/GRXPHT8U84RAYDXZ ; https://associados.amazon.com.br/help/operating/policies/
- **O que li:** HTML bruto. Título da página: "Regulamento de Comissões Padrão do Programa de Associados"; linha "Livros | Livros Digitais 10%"; "Outros 7%"; outras faixas na mesma tabela: 13% (bebês, beleza, alimentos, audiolivros), 11% (roupas, pet shop), 9,5% (dispositivos Amazon), 8% (eletrônicos, informática, casa, esportes e outras), 7% (várias e "Outros"), 0% (Coach). Políticas: "aproximadamente 60 dias após o final de cada mês"; "Quadro de Pagamento Mínimo: Opção 1 (Depósito) R$30,00; Opção 2 (Vale-presente) Indisponível; Opção 3 (Cheque) Indisponível"; sessão encerrada "24 horas decorridas após o referido clique" (ou quando o cliente faz pedido de outro produto que não seja item digital); cita "Código Brasileiro de Autorregulamentação Publicitária" e "Guia de Publicidade por Influenciadores Digitais"; links especiais em e-mails/SMS/mensagens diretas só se solicitados.
- **Veredito: CONFIRMADO.** "Padrão" é o nome da tabela do programa; o 10% é da categoria Livros (as demais vão de 7% a 13%, com Coach a 0%). O mínimo de R$ 30 vale só para depósito direto.

#### A5. Kiwify: 8,99% + R$ 2,49 por venda
- **Afirmação:** mei-ficha.md §6 (l. 138) e economia-ficha.md §5 (l. 137): "8,99% + R$2,49" por venda; "Você só paga se vender"; R$ 3,67 por saque; sem mensalidade; "Pix e transferência em 2 dias, cartão em 15 dias".
- **URL:** https://kiwify.com.br/ ; https://ajuda.kiwify.com.br/pt-br/article/quais-sao-as-taxas-da-plataforma-1ems3wq/
- **O que li:** HTML bruto. Home: "Quanto custa? Você só paga se vender 8,99% + R$2,49. Receba em cartão em 15 dias, boletos e Pix em 2 dias. Possibilidade de receber cartões em 2 dias"; FAQ: "15 dias para cartão de crédito, 2 dias para boleto bancário e PIX". Ajuda: "A nossa taxa é de 8.99% + R$2,49 por venda aprovada"; "R$3,67 por solicitação de saque, seja via TED ou pix"; "Na Kiwify não há taxa de adesão e nem mensalidade"; "você não paga nenhum valor de taxa nos pedidos reembolsados". A palavra "transferência" não aparece nos prazos.
- **Veredito: CONFIRMADO.** Taxas confirmadas. Detalhe menor: o prazo de 2 dias vale para boleto e Pix, não "Pix e transferência" (X06).

#### A6. beehiiv: gratuito até 2.500; Lite US$ 49/mês
- **Afirmação:** economia-ficha.md §5 (l. 135-136): Free US$ 0, até 2.500 inscritos, sem assinaturas pagas; Lite US$ 49/mês ("há cobrança anual"), 0% de taxa da plataforma, Stripe 2,9% + US$ 0,30.
- **URL:** https://www.beehiiv.com/pricing
- **O que li:** WebFetch e HTML bruto: "Subscribers, Free, Up to 2,500"; "Lite ... $49 /mo Yearly billing ... Paid subscriptions 0% take rate"; "Pro ... $95 /mo Yearly billing"; assinaturas pagas listadas só a partir do Lite; "beehiiv takes 0% of your paid subscription and digital product revenue. You keep what you earn, minus Stripe's standard processing fee of 2.9% + $0.30 per transaction". A página tem o alternador "Yearly (and save) / Monthly" e, junto dele, "Pricing for 250,000+ subscribers / Pricing for 1,000 subscribers" (leio como seletor de faixa de inscritos; não testei a interação, que é do lado do cliente).
- **Veredito: CONFIRMADO.** Ressalva: US$ 49 é o preço mensal com cobrança anual, na faixa exibida (1.000 inscritos, pelo texto do seletor). Preço com cobrança mensal e preço em outras faixas não aparecem no HTML.

### B. Preços

#### B7. AlgoMaster Premium: R$ 152 / 392 / 785
- **Afirmação:** sysdesign-ficha.md §4 (l. 80): R$ 152 (1 mês), R$ 392 (1 ano, riscado R$ 523, 25% OFF), R$ 785 (vitalício, riscado R$ 1.308, 40% OFF), pagamento único; "moeda possivelmente localizada por IP [H]".
- **URL:** https://algomaster.io/premium
- **O que li:** HTML bruto: "Monthly 1 month access R$152"; "Annual 1 year access R$392 R$523 25 % OFF"; "Lifetime Forever access R$785 R$1,308 40 % OFF"; "One-time payment (no auto-renewal)". O HTML embute `currencyConfig:{"code":"BRL","symbol":"R$","name":"Brazilian Real","prices":{"monthly":15200,"annual":39200,"lifetime":78500}...}`, montado no servidor para esta requisição; não há USD nem outra moeda no HTML. Isso é compatível com moeda por visitante, mas não o prova (nenhum texto fala em localização).
- **Veredito: CONFIRMADO.** Valores e moeda (R$) confirmados nesta leitura. A hipótese de moeda por IP segue NÃO VERIFICÁVEL (X07).

#### B8. Hello Interview Premium: US$ 47 / 78 / 275
- **Afirmação:** sysdesign-ficha.md §4 (l. 81): $ 47 (1 mês, riscado $ 59), $ 78 (1 ano, riscado $ 119), $ 275 (vitalício, riscado $ 399); "Does not auto-renew"; símbolo $ sem nome da moeda.
- **URL:** https://www.hellointerview.com/
- **O que li:** HTML bruto: "1 Month Access $ 47 $ 59"; "1 Year Access $ 78 $ 119"; "Lifetime Access $ 275 $ 399"; "Does not auto-renew". Nenhum código de moeda (USD) no texto da página.
- **Veredito: CONFIRMADO.**

#### B9. Speak Tech English: e-books US$ 49,99 e 39,99; bundle US$ 99
- **Afirmação:** ingles-tech-ficha.md §2 (l. 37): e-books US$ 49,99 (Technical Interviews) e US$ 39,99 (Programmers); kit de CV US$ 9,99; curso de 50 frases US$ 14,99; flashcards US$ 4,99; bundle US$ 99,00.
- **URL:** https://speaktechenglish.com/courses/
- **O que li:** HTML bruto: "English for Technical Interviews $ 69.99 Original price was: $69.99. $ 49.99 Current price is: $49.99"; "English For Programmers $ 59.99 ... $ 39.99"; "English for Developers Bundle $ 160.00 ... $ 99.00"; "English Tech CV Upgrade Kit ... $ 9.99"; curso de 50 frases $14.99 e flashcards $4.99 (leitor); carrinho com `"currency":"USD"`; faixa "SAVE UP TO 30%".
- **Veredito: CONFIRMADO.** Os preços da ficha são os promocionais (descontos de 29% a 38%); os de lista são 40% a 62% maiores (US$ 69,99, 59,99 e 160,00). Âncora de preço da hipótese H1 deve dizer isso.

#### B10. Inglês para Devs: R$ 316 e R$ 632 por mês
- **Afirmação:** ingles-tech-ficha.md §2 (l. 37): R$ 316/mês (1x), R$ 632/mês (2x), "12x R$ 158,08"; duração do plano não declarada; garantia de 7 dias; curso com 50 h+.
- **URL:** https://inglesparadevs.com.br
- **O que li:** HTML bruto: "Inglês Para Devs 1x por semana R$ 316 por mês"; "2x por semana R$ 632 por mês"; "Curso Inglês Para Devs 12x R$158,08"; "7 dias de garantia incondicional"; "A carga horária do curso é de 50 horas, contando com mais de 45h em videoaulas, 900 exercícios e mais de 250 áudios"; "Vitor é professor de inglês e engenheiro de software há quase uma década"; "Filipe é professor de inglês há mais de 10 anos e já deu mais de 5 mil horas de aula".
- **Veredito: CONFIRMADO.**

#### B11. PeqArt (App Store BR): assinatura anual R$ 129,90
- **Afirmação:** mei-ficha.md §4.1 (l. 52): "Grátis com compras no app; Assinatura Anual R$ 129,90; nota 4,8 (405 avaliações)".
- **URL:** https://apps.apple.com/br/app/id1594656704
- **O que li:** WebFetch (a página da App Store não foi relida em HTML bruto): "Peqart - Gestão Artesanal"; "Assinatura Peqart Anual R$ 129,90"; "Plano Anual R$ 129,90"; "4.8 out of 5 stars with 405 ratings"; "Free (with in-app purchases)".
- **Veredito: CONFIRMADO.**

#### B12. How To Go Freelance: US$ 29 (templates) e US$ 149 (curso)
- **Afirmação:** mei-ficha.md §4.2 (l. 66): US$ 29,00 (8 templates, inclui Rate Sheet e Living Expenses Calculator) e US$ 149 (curso); URL citada: página da template library.
- **URL:** https://www.howtogofreelance.com/store/p/freelance-template-library ; https://www.howtogofreelance.com/ ; https://www.howtogofreelance.com/sign-up
- **O que li:** HTML bruto. Template library: "The Freelance Starter Kit: 8 Templates $29.00 ... Includes: 10 Copy-Paste Cold + Client Email Templates, Scope of Work Template, Rate Sheet Template, Client Services Agreement, Client Outreach Tracker, Living Expenses Calculator, Business Expense Tracker, and Invoice Template"; `product:price:currency` = USD. O US$ 149 não está nessa página: home "BUY THE COURSE + TEMPLATES $149 JUST THE TEMPLATES $29"; /sign-up: "Early Bird Pricing! Digital Course How to Go Freelance $149.00 One time. 13 written and audio lessons plus a full template library".
- **Veredito: CONFIRMADO.** O preço de US$ 149 está certo, mas em outra URL que a citada; é preço "Early Bird" e já inclui os templates.

#### B13. Visual Capitalist: VC+ US$ 7,49/mês anual; relatório US$ 80
- **Afirmação:** economia-ficha.md §0 (l. 26) e §2.1 (l. 61): VC+ "US$ 7,49/mês cobrado anualmente"; relatório avulso US$ 80 (moeda não explícita).
- **URL:** https://www.visualcapitalist.com/get-more-vc/
- **O que li:** HTML bruto: "VC+ Membership ... $7.49 /month, billed annually" (alternador "Monthly / Annual SAVE 25%"); "Global Forecast Report Only $80 /one time payment. 2026 Global Forecast Report delivered via email". Só o símbolo $.
- **Veredito: CONFIRMADO.** Há também cobrança mensal (mais cara), não lida.

### C. Números oficiais e regras

#### C14. DAS-MEI 2026 (INSS R$ 81,05; somas)
- **Afirmação:** mei-ficha.md §3 (l. 30): R$ 81,05 de INSS (5% de R$ 1.621,00, Decreto 12.797/2025) + R$ 5,00 de ISS e/ou R$ 1,00 de ICMS; "somas R$ 82,05 / 86,05 / 87,05 são aritmética minha".
- **URL:** https://www8.receita.fazenda.gov.br/simplesnacional/noticias/NoticiaCompleta.aspx?id=c3b2044c-ff97-432a-b33c-ecf2a3df6dc3 ; https://www.gov.br/empresas-e-negocios/pt-br/empreendedor/perguntas-frequentes
- **O que li:** HTML bruto (Receita, publicado 02/01/2026): "Decreto nº 12.797, de 23 de dezembro de 2025. Para este período, o valor a ser pago em DAS corresponderá a: R$ 81,05 de INSS (5% do valor do salário-mínimo, de R$ 1.621,00); R$ 5,00 de ISS, caso seja contribuinte deste imposto; e R$ 1,00 de ICMS, caso seja contribuinte deste imposto". O texto não traz totais (82,05, 86,05 e 87,05 ausentes). Conferi a aritmética: 5% de 1.621,00 = 81,05; 81,05+1,00 = 82,05; 81,05+5,00 = 86,05; 81,05+6,00 = 87,05. FAQ gov.br (121 mil caracteres, li 100 mil): "Comércio e Industria - ICMS 81,05 1,00 82,05" e "Comércio e Serviços - ICMS e ISS 81,05 6,00 87,05".
- **Veredito: CONFIRMADO.** A ficha foi conservadora: o FAQ traz as somas 82,05 e 87,05 literalmente (o 86,05 não apareceu no trecho lido).

#### C15. Teto do MEI, proporcional, PLP 186/2026, dois funcionários
- **Afirmação:** mei-ficha.md §3 (l. 32-36): limite R$ 81 mil; R$ 6.750 por mês no ano de abertura; PLP 186/2026: R$ 110 mil em 2027 e R$ 140 mil em 2028 ("não estão em vigor", "poderá sofrer alterações ... ou não ser aprovado"); "agora tem permissão legal para contratar até dois funcionários"; "20% de R$ 81.000 = R$ 97.200 é conta minha; não li esse valor literal"; publicado 2026-06-29, modificado 2026-09-16; PLP 186 "(Executivo)".
- **URL:** https://www.gov.br/memp/pt-br/teto-do-mei
- **O que li:** HTML bruto: "Atualmente, o limite de faturamento anual do Microempreendedor Individual (MEI) é de R$ 81 mil"; "o valor proporcional corresponde a R$ 6.750 por mês de atividade"; "PLP nº 186/2026 ... 2027: R$ 110 mil por ano; 2028: R$ 140 mil por ano. Esses valores são propostos pelo PLP nº 186/2026 e ainda não estão em vigor"; "O texto poderá sofrer alterações durante a tramitação ou não ser aprovado"; "O limite de contratação dobrou. O microempreendedor individual agora tem permissão legal para contratar até dois funcionários registrados simultaneamente"; "Publicado em 29/06/2026 16:08 Modificado em 16/09/2026 14:54". O valor R$ 97.200 ESTÁ literal: "Até 20% acima do teto (até R$ 97.200): Você deve recolher um DAS complementar ... passará a pagar o imposto como Microempresa (ME) no ano seguinte". A palavra "Executivo" não aparece na página.
- **Veredito: CONFIRMADO.** Dois pontos menores contra a ficha: o R$ 97.200 é literal (a ficha dizia que não); a atribuição do PLP 186 ao Executivo não está nesta página (não verificada).

#### C16a. CONAR (versão economia): publicado 2026-05-26, em vigor desde 2026-06-01
- **Afirmação:** economia-ficha.md §7 (l. 194): Guia "publicado em 2026-05-26, em vigor desde 2026-06-01: identificação clara da publicidade, segmentos restritos, uso de IA".
- **URL:** https://www.conar.org.br/noticias/guia-de-marketing-e-publicidade-por-influenciadores-digitais
- **O que li:** HTML bruto: título "Guia de Marketing e Publicidade por Influenciadores Digitais 26 MAIO 2026"; "Atualização do Guia ... ganha versão diagramada, que pode ser baixada em formato PDF"; tópicos: "Transparência e identificação publicitária", "Segmentos de produtos e serviços restritos", "Uso de Inteligência artificial na publicidade"; "As diretrizes foram aprovadas pelo Conselho do Conteúdo do CONAR e entram em vigor em 1º de junho". "12 de maio" e "13 de maio" não aparecem.
- **Veredito: CONFIRMADO.** 26/05/2026 é a data da notícia do CONAR (sobre a versão diagramada); "em vigor em 1º de junho" é literal. A ficha escreveu "publicado" para a data da notícia.

#### C16b. CONAR (versão ingles-tech): 12-13 de maio, efeitos desde 1º de junho
- **Afirmação:** ingles-tech-ficha.md §7 (l. 123): guia "de maio de 2026"; matéria do Meio & Mensagem de 2026-05-13; "um resumo indexado diz publicado em 12 e em vigor em 13 de maio, com efeitos desde 1º de junho; as fontes divergem em um dia".
- **URL:** https://www.meioemensagem.com.br/midia/conar-atualiza-guia-para-influenciadores-digitais ; https://www.klalaw.com.br/conar-atualiza-guia-de-publicidade-com-influenciadores/ ; página oficial acima
- **O que li:** HTML bruto. Meio & Mensagem: "13 de maio de 2026 - 12h25"; "O Conar publica, nesta quarta-feira, 13, a nova edição"; "O novo texto entra em vigor também nesta quarta-feira" (sem menção a 1º de junho). KLA (escritório): "publicou, em 12 de maio de 2026, uma nova edição ..., que entrou em vigor em 13 de maio de 2026 e produzirá efeitos a partir de 1º de junho de 2026". Página oficial do CONAR: notícia de 26/05 e "entram em vigor em 1º de junho"; nenhuma menção a 12 ou 13 de maio.
- **Veredito: DIVERGENTE.** Resolução: a única data de vigência que a página oficial sustenta é 1º de junho de 2026. As datas de 12 e 13 de maio vêm só de terceiros que discordam entre si (M&M: publica e vigora em 13/05; KLA: publica em 12/05, vigora em 13/05, efeitos em 1º/06). Não usar 12-13/05 como fato.

#### C17. CVM 2020-11-11: caráter profissional e "não é recomendação"
- **Afirmação:** economia-ficha.md §7 (l. 193) e coordenador: caráter profissional = constância e remuneração, ainda que indireta (assinatura, mensalidade); "não é recomendação" não descaracteriza; a página não separa educação de recomendação.
- **URL:** https://www.gov.br/cvm/pt-br/assuntos/noticias/area-tecnica-da-cvm-esclarece-duvidas-sobre-atuacao-de-influenciadores-que-recomendam-investimentos-dddc1973876d4cc78c734b8ceeaaa740 (redireciona para .../noticias/2020/...)
- **O que li:** HTML bruto: "Publicado em 11/11/2020 11h00 Atualizado em 09/04/2025 14h21"; "O caráter profissional fica caracterizado, por exemplo, quando há uma constância na divulgação das análises e recebimento de remuneração, ainda que indireta" (Daniel Maeda, SIN/CVM); padrões listados: "cobrança de taxa de assinatura ou adesão", "Cobrança de mensalidades e anuidades do público", "Receitas indiretas recebidas em função do acesso de terceiros", "Habitualidade"; "Muitos influenciadores digitais usam avisos como 'não se trata de recomendação de investimento' ... Mesmo assim, a área técnica da CVM enfatiza que ...". Sem separação entre conteúdo educativo e recomendação.
- **Veredito: CONFIRMADO.** O texto diz "por exemplo": constância e remuneração são exemplos, não definição fechada.

#### C18. EF EPI 2025 Brasil: 75º, nota 482
- **Afirmação:** ingles-tech-ficha.md §4 (l. 81): Brasil em 75º, nota 482 contra média global 488; leitura 516, escuta 468, fala 464, escrita 442; usado em §5 como indício de "fala travada".
- **URL:** https://www.ef.com/assetscdn/WIBIwq6RdJvcD9bc8RMd/cefcom-epi-site/fact-sheets/2025/ef-epi-fact-sheet-brazil-english.pdf
- **O que li:** O WebFetch devolveu o PDF binário; extraí o texto com `pdftotext` do arquivo salvo: "Global ranking: #75"; "EF EPI score: 482"; "Global average score: 488"; "Reading score: 516; Listening score: 468; Writing score: 442; Speaking score: 464"; tendência "2011 - 2025".
- **Veredito: CONFIRMADO.** Contraevidência na mesma folha, não citada na ficha: "Scores by job function ... IT: 551" (acima da nota nacional 482 e da média global 488). O elo "dev brasileiro com fala travada" usa médias nacionais; a nota de TI da própria fonte é alta.

#### C19. Dinamos: R$ 30 mil em um ano, 230 pessoas ativas, passou a gratuito
- **Afirmação:** sysdesign-ficha.md §0 (l. 13) e §4 (l. 83): ~R$ 30.000 em um ano, 230 pessoas ativas, "suficiente para cobrir os custos fixos", "chegou ao ponto de equilíbrio e virou gratuito"; R$ 0 desde 2025-12.
- **URL:** https://www.tabnews.com.br/api/v1/contents/trilhainfo/abri-mao-de-um-saas-que-faturou-r30000-esse-ano
- **O que li:** JSON bruto (curl): published_at 2025-12-17T18:23:02Z; "lancei o Dinamos.net como um produto pago (com assinatura única e acesso vitalício). Graças ao apoio de 230 pessoas ativas na plataforma e um faturamento total de cerca de R$ 30.000 ao longo de um ano, rastreado via Stripe/Trust MRR, conseguimos cobrir os custos fixos de manutenção (como hospedagem, banco de dados e acesso à API da LLM). Agora, estou anunciando que o Dinamos.net é 100% gratuito e será grátis para sempre!"; "Apesar do projeto ter tido boas vendas ...".
- **Veredito: CONFIRMADO.** Números conferem. Ressalvas de leitura: 230 são "pessoas ativas" (não se diz que são pagantes); "ponto de equilíbrio" é paráfrase (o texto diz que cobriu os custos fixos de manutenção, sem contar o tempo do autor); receita autodeclarada.

#### C20. Remotion: grátis até 3 pessoas; uso comercial; Company License acima
- **Afirmação:** Pedido do coordenador, item 20 (as quatro fichas não citam a licença do Remotion): grátis para pessoas e empresas com fins lucrativos de até 3 funcionários; uso comercial permitido; Company License acima disso.
- **URL:** https://github.com/remotion-dev/remotion/blob/main/LICENSE.md ; https://www.remotion.pro/license ; https://www.remotion.dev/docs/license/faq
- **O que li:** LICENSE.md (curl): "a for-profit organization with up to 3 employees"; "to use the software non-commercially or commercially for the purpose of creating videos and images"; Company License exigida de quem não é elegível ao Free. remotion.pro/license: "For individuals and companies of up to 3 people. Free License. Create and automate. Commercial use allowed. Unlimited use. Must upgrade when your team grows"; "For collaborations and companies of 4+ people. Company License"; Creators US$ 25/mês por pessoa; Automators US$ 0,01 por render, mínimo US$ 100/mês. FAQ oficial: "Can I run an automation under the Free License? Yes ... If you are eligible for the Free License, you can also run an automation"; "Can single-person companies use the Free License? Yes ... as long as your total headcount is 3 or less"; "If you bring in another studio, freelancers, or a consulting agency ..., their headcount aggregates with yours for the 4-person threshold".
- **Veredito: CONFIRMADO.** O texto diz "employees" (LICENSE.md), "people" (página de preços) e "headcount" (FAQ), e a contagem inclui freelancers e agências no mesmo projeto. Automação sob a licença gratuita é permitida pelo FAQ.

#### C21. Loja Kurzgesagt: só físicos, US$ 15,90 a 59,90
- **Afirmação:** Pedido do coordenador, item 21 (nenhuma das quatro fichas cita a loja): só produtos físicos, preços em USD de US$ 15,90 a US$ 59,90.
- **URL:** https://shop-us.kurzgesagt.org/
- **O que li:** HTML bruto da página inicial: preços visíveis no texto de US$ 15,90 a US$ 59,90 (15.9, 18.9, 22.9, 23.9, 27.9, 29.9, 32.9, 35.9, 59.9); linhas "Books & Stationery", cadernos, calendário, artbooks; zero ocorrências de "digital", "download", "PDF" e "course" ("ebook" só aparece dentro de "Notebooks"); o rodapé tem link "Gift Cards" (não aberto).
- **Veredito: CONFIRMADO.** Vale para a página inicial; não percorri as coleções nem os cartões-presente.

### D. Instagram (10 acessos; o que o leitor devolveu)

Cada leitura pediu: seguidores, seguindo, posts, bio, verificado e os 12 primeiros itens da grade (tipo, data, caminho), sem inferir. "Posts count" veio "not shown" em todas. Divergência acima de 10% em seguidores: **nenhuma**.

| ID | Perfil | Ficha | Resposta do leitor | Itens recentes (tipo e data como a página mostrou) | Veredito |
|---|---|---|---|---|---|
| D1 | @minhas_financas_organizadas | 85,5 mil (seguindo 6) | Followers 85.5K; Following 6; Verified Yes; bio "Transforme sua vida financeira com uma planilha simples e eficiente! ... Pessoal • Empresarial • Precificação • Est..."; link planilhaspremium.online/link-bio | 12 itens: 3 fotos de 2024-10-12 (prováveis fixadas); Clip 2026-09-02 (/reel/Dcy-WrMO8MH/), Clip 2026-06-18, Carousel 2026-03-25, Photo 2025-11-25, Carousel 2025-10-18, Photo 2025-10-10, Clip 2025-07-30, Carousel 2025-07-26, Photo 2025-07-25. Idêntico ao CSV (3 Reels, 3 carrosséis, 3 imagens; 1 item na janela). | CONFIRMADO |
| D2 | @garotadasplanilhas | 81,2 mil (seguindo 67) | Followers 81.2K; Following 67; Verified Yes; link linkin.bio/garotadasplanilhas | 12 itens: Carousel 2026-05-04, Clip 2026-02-03, Clip 2024-10-09 (prováveis fixados) e 9 de 2026-08-30 a 2026-10-01 (6 Clips, 3 Carousels; ordem não cronológica). Idêntico ao CSV. | CONFIRMADO |
| D3 | @peqart.app | 12,4 mil (seguindo 5) | Follower count 12.4K; Following 5; link linktr.ee/peqart and 1 more | 12 Carousels de 2026-10-06 a 2026-09-24. Idêntico. Desta vez o leitor devolveu a data de cada item (a ficha dizia "datas individuais não exibidas"). | CONFIRMADO |
| D4 | @algomasterio | 394 mil (seguindo 1) | Followers 394K; Following 1; Verified Yes; bio "Master DSA and System Design with visual explanations. Learn more below." | 12 Clips: 2026-07-13, 07-23, 05-07, 10-06, 10-05, 10-04 (/ashishps_1/), 10-04, 10-02 (/ashishps_1/), 10-01 (/ashishps_1/), 09-29, 09-28, 09-27. Idêntico ao CSV (11 de 12 na janela; 3 sob a conta do fundador). | CONFIRMADO |
| D5 | @english_for_it | 43,4 mil (seguindo 147) | Follower Count 43.4K; Following 147; bio "English For Tech, Business & Digital ... Europe - USA - LatAm - Worldwide ... START HERE"; Verified: Not shown | 12 itens de 2026-10-06 a 2026-09-16: 6 Clips (10-06, 10-05, 10-02, 09-23, 09-19, 09-17), carrosséis 10-05 e 09-30 (/english_for_it/), 10-01 (/evotalents.school/), 09-22 (/staya.agency/), Post 09-17 (/evotalents.school/), Photo 09-16. A ficha listou 9 (os 6 Reels, 2 carrosséis e 1 imagem); os 3 itens sob URLs de outras contas ficaram de fora. Reels idênticos. | CONFIRMADO |
| D6 | @paulogala | 78 mil | Followers 78K; Following 3,085; Verified Yes; bio "Paulo Gala / Economista · Professor FGV, Te explico por que o Brasil não cresce ..." | 12 itens de 2026-10-06 a 10-02: 10 Photos, 1 Carousel (10-06), 1 Clip (10-04). Idêntico ao CSV. | CONFIRMADO |
| D7 | @imlucena | 30,1 mil | Follower Count 30.1K; Following 3,625; Verified Yes; bio "Economista PhD R.I Ex-Presidente do CORECON - 8ª Região. Apresentador do 'Lucena Explica'. Fundador do @sana_fcnb" | 12 itens: Clip 2026-03-02, Photo 2025-11-28, Clips 10-06, 10-05, 10-02, 09-29; Photo 10-01 e 09-22; Carousels 09-30 (/giftitconsultoria/), 09-25, 09-24, 09-23. Idêntico (5 Reels, 4 carrosséis, 3 fotos). | CONFIRMADO |
| D8 | @visualcap | 413 mil | Followers 413K; Following 69; Verified: Not shown; bio "Data-driven visual content that explains the trends shaping our world ... Creator on @voronoiapp" | 12 itens de 2026-10-04 a 09-24: 9 Photos, 2 Carousels (10-04, 09-27), 1 Clip (10-02). Textos alternativos automáticos ("May be a graphic of poster and text", etc.). Idêntico ao CSV. | CONFIRMADO |
| D9 | Reel /reel/Dcy-WrMO8MH/ (@minhas_financas_organizadas) | 31 curtidas, 33 comentários, legenda "Comenta Precificação..." | Account minhas_financas_organizadas; Likes 31; Comments 33; Views/Plays "Not shown"; "Original audio"; "4 weeks ago (September 2, 2026)"; hashtags #precificacao #empreendedorismo #pequenosnegocios #planilhadeprecificação #planilha | Legenda literal: "Um detalhe na Precificação que muita gente esquece: o percentual de perda dos ingredientes. No fim, isso pode mudar bastante o custo real do produto. Comenta Precificação que eu te envio o link no direct". Comentários visíveis: "Multiple users commented solely with 'Precificação,' along with one comment reading 'Olá' and another saying 'precificação'" (isto é, boa parte dos 33 comentários é a palavra-chave do CTA, não interesse espontâneo). | CONFIRMADO |
| D10 | Bônus: @bytebytego | 559 mil | Follower count 559K; Following 1; Verified not shown; bio "ByteByteGo / Learn System Design" (a ficha registra "Sign up to our free newsletter for 5x more diagrams": o meu leitor não devolveu essa frase); link bit.ly/bytebytegoInst | 12 itens: Photo 2024-07-31 (provável fixado) e 11 "Image" de 2026-09-10 a 2026-06-24; nenhum Clip. Idêntico (12 de 12 estáticos; 7 na janela; último em 2026-09-10, 26 dias antes). | CONFIRMADO |

Observações: (1) em D5 a grade tem 12 itens e a ficha usa 9; a contagem "9 posts em 21 dias" subestima a grade, mas os 6 Reels batem. (2) Em D9 os 33 comentários são, em boa parte, a palavra-chave pedida pelo CTA; a ficha já lia assim (I), e a leitura direta reforça. (3) Em D10 a bio devolvida difere da registrada na ficha (X50).

### E. Coerência técnica no repositório (somente leitura)

#### E1. Retrato aceita só photo, broll, number, keyword, stamp, lower_third, compare, chart
- **Afirmação:** Coordenador (i); sysdesign-ficha.md §8.1 (l. 124); mei/ingles/economia idem.
- **Arquivo:** /home/viniciusk/projetos/auto-play/app/pipeline/schemas.py
- **O que li:** l. 506-508: `PORTRAIT_SHOT_KINDS = frozenset({"photo", "broll", "number", "keyword", "stamp", "lower_third", "compare", "chart"})`; `portrait_problems` (l. 511-518) manda erro por plano fora do conjunto. `chart` aceita bar, bar_horizontal, line, share (l. 211); `compare` aceita side, before_after, scale (l. 373).
- **Veredito: CONFIRMADO.**

#### E2. keyword: no máximo KEYWORD_MAX_WORDS palavras
- **Afirmação:** Coordenador (ii); ingles-tech-ficha.md §8 (l. 127) e economia-ficha.md §6 (l. 145): "no máximo 8 palavras".
- **Arquivo:** /home/viniciusk/projetos/auto-play/app/pipeline/schemas.py
- **O que li:** l. 454: `KEYWORD_MAX_WORDS = 8`; l. 472-473: erro "frase na tela com mais de 8 palavras". `check.py` l. 245-246 alerta para mais de 1 keyword por cena.
- **Veredito: CONFIRMADO.** Valor: 8.

#### E3. ADR 014 deixa rede, mapa, linha do tempo, árvore e documento fora do retrato
- **Afirmação:** Coordenador (iii); sysdesign-ficha.md §8.2 (l. 146).
- **Arquivo:** /home/viniciusk/projetos/auto-play/docs/decisions/014-perfil-vertical.md
- **O que li:** l. 23-25 (opção escolhida: só os 8 planos) e l. 53-54: "Fora desta ADR: rede, mapa, linha do tempo, árvore e cartão de documento em retrato; música; export para plataforma; título e capa." `quote` também está fora do conjunto do retrato (schemas.py l. 506-508).
- **Veredito: CONFIRMADO.**

#### E4a. compare ganha ramo de texto no retrato
- **Afirmação:** Coordenador (iv); ingles-tech-ficha.md §8.1 (l. 133): ramo de texto com valor 64 px e rótulo 30 px, colunas empilhadas.
- **Arquivo:** /home/viniciusk/projetos/auto-play/video/src/Editorial.tsx
- **O que li:** l. 137-182 (HEAD d1757d6 e árvore de trabalho): comentário "sem número reconhecível, lado a lado em texto (a tela não converte nem calcula)"; em retrato `flexDirection: "column"`, valor `u(portrait ? 64 : 110)`, rótulo `u(portrait ? 30 : 36)`, `top: u(COMPARE_TOP)`. O ramo numérico só roda se os DOIS valores passam em `screenNumber` (l. 143-145); `numbers.ts` l. 5: `/^(\D*?)([\d.,]*\d)(.*)$/` aceita qualquer texto com dígito (a ficha ingles-tech acertou: dígito nas duas frases aciona o ramo numérico). A árvore de trabalho tem mudança não commitada só em l. 152 (valueSize 120 para 150, labelSize 34 para 38, ramo numérico).
- **Veredito: CONFIRMADO.**

#### E4b. Pipeline, Gauge, CodeWalkthrough existem no kit e não têm plano
- **Afirmação:** Coordenador (iv); brief-comum.md §1 (l. 7); mei-ficha.md l. 167; sysdesign-ficha.md §8.2.
- **Arquivo:** ~/projetos/motion-kit/src/COMPONENTS.md ; /home/viniciusk/projetos/auto-play/video/src/ShotView.tsx
- **O que li:** COMPONENTS.md: `<CodeWalkthrough code steps>` (l. 80), `<Pipeline stages itemColor>` "estilo ByteByteGo em 9:16" (l. 86), `<Gauge max to zones>` (l. 93). Existem no SHA do pin 527c708 (`git cat-file -e 527c708:src/components/{Pipeline,Gauge,CodeWalkthrough,Odometer}.tsx`) e o pacote instalado em `video/node_modules` é 0.3.0. `ShotView.tsx` l. 123-158: `switch` com photo, broll, number, quote, stamp, lower_third, chart, timeline, family_tree, map, compare, network, keyword; nenhum desses componentes aparece em `video/src` (grep).
- **Veredito: CONFIRMADO.**

#### E4c. Odometer existe no kit e não tem plano no template
- **Afirmação:** Coordenador (iv) e brief-comum.md §1 (l. 7) ("odômetro ... ainda não foram ligados a planos"); economia-ficha.md §6.2 (l. 166): "odômetro (número que sobe)"; mei-ficha.md l. 167.
- **Arquivo:** /home/viniciusk/projetos/auto-play/video/src/Editorial.tsx
- **O que li:** l. 3: `import {Odometer} from "@viniciusk/motion-kit"`; l. 88-97: `Digits` renderiza `<Odometer to={parsed.value} ... />` e é usado por `NumberShot` (l. 117, 128). Ou seja, o "número que sobe" já é o plano `number`. O que não existe é um plano próprio de odômetro. É o único componente da lista que está ligado.
- **Veredito: DIVERGENTE.** Valor lido: Odometer está em uso dentro do plano number. Pipeline, Gauge, CodeWalkthrough, CodeBlock, ContextWindow, AnimatedGraph e Highlighter não aparecem em video/src.

#### E5. Gemini TTS: 10 chamadas/dia e 3/min; adapter sem glossário
- **Afirmação:** Coordenador (v); ingles-tech-ficha.md §4 (l. 82) e §9.
- **Arquivo:** /home/viniciusk/projetos/auto-play/data/benchmarks/termos-gemini-tts.md ; /home/viniciusk/projetos/auto-play/app/providers/tts/gemini.py
- **O que li:** termos-gemini-tts.md l. 45: limites por minuto e por dia "não publicados"; l. 47-48: observado em 2026-09-29, erro 429 "limit: 3 requests per minute on Free Tier"; l. 50-51: observado em 2026-09-30, "limit: 10 requests per day on Free Tier". gemini.py l. 4-5 repete os dois valores; l. 10: "Sem dicionário de fonemas: um glossário no pedido é erro"; l. 101-102: `if request.lexicon: raise ProviderError(... "glossário de fonemas não é aceito pelo Gemini TTS (ADR 012)")`. `config/providers.toml` l. 31: estilo "com sotaque brasileiro".
- **Veredito: CONFIRMADO.** Os dois limites são OBSERVADOS (um 429 em cada dia), não publicados pelo Google.

#### E6. Votorantim: ~1,6 M tokens e ~1 h 31 para 93 s
- **Afirmação:** Coordenador (vi); as quatro fichas.
- **Arquivo:** /home/viniciusk/projetos/auto-play/data/benchmarks/episodio-votorantim-dinheiro.md
- **O que li:** l. 10: "93,1 s (voz real), 10 cenas, 21 planos"; l. 22-27: roteirista ~409 mil tokens e 32,8 min; verificador ~944 mil e 45,6 min (5 checagens); pesquisador ~264 mil e 12,3 min; total "~1,6 milhão" e "~1 h 31 min"; l. 29: "Os tokens são um piso"; l. 45-51: rodada 1 reprovou 5 de 20 frases e 6 de 27 planos, passou na 5ª; l. 73: "Horas humanas: não medidas". Conferi as escalas lineares das fichas (20/93 e 45/93 de 1,6 M e 91 min dão 0,34 a 0,77 M e 20 a 44 min).
- **Veredito: CONFIRMADO.**

## 5. Verificações adicionais (fora da lista, afirmações que também pesam)

| ID | Onde a ficha afirma | Afirmação | Fonte | O que li | Veredito |
|---|---|---|---|---|---|
| X01 | sysdesign §4 | ByteByteGo afiliado: 5.000 "fans", "generous revenue sharing" sem %, cookie 30 dias, saque por PayPal | https://bytebytego.com/be-an-affiliate | "at least 5,000 fans"; "generous revenue sharing on any enrollment attributed to you"; "30-day cookie period"; "cash-out via PayPal"; "Send us an email at hi@bytebytego.com". Sem percentual nem mínimo de saque. | CONFIRMADO |
| X02 | sysdesign §4 | Codemia: 1 ano de Premium em vez de comissão; conteúdo de 10 minutos ou mais; divulgação | https://codemia.io/creators | "A full year of Codemia Premium"; "Ten minutes or longer ... A sixty-second feature tour does not count"; "disclose it in the video itself and in the description. The FTC requires it". | CONFIRMADO |
| X03 | sysdesign §2 | Aced é ex-Exponent; handle @aced__io | https://www.aced.io/ | "formerly Exponent"; Instagram @aced__io. | CONFIRMADO |
| X04 | sysdesign §4 | Aced: moeda, cookie, pagamento mínimo e elegibilidade "não informados" | https://www.aced.io/affiliate | FAQ com perguntas sobre ganhos, pagamentos, ativos de marketing e atribuição; respostas não estão no HTML nem no leitor (acordeão). A frase correta é "não lido". | NÃO VERIFICÁVEL |
| X05a | ingles-tech §7 | Cambly: pagamento mensal por PayPal/Alipay; exige "an engaged audience"; sem limite de país declarado | https://www.cambly.com/ambassador | HTML bruto confere (ver A3). | CONFIRMADO |
| X05b | ingles-tech §7 | Trecho indexado: Cambly exigiria gasto mínimo de US$ 50 | https://www.cambly.com/ambassador | Zero ocorrências de "$50"; só "$30" (duas vezes). | REFUTADO |
| X06 | mei §6 | Kiwify: "Pix e transferência em 2 dias" | https://kiwify.com.br/ | A página diz "boleto bancário e PIX" em 2 dias; "transferência" ausente. Cartão pode ser antecipado para 2 dias. | DIVERGENTE |
| X07 | sysdesign §4 | AlgoMaster: moeda localizada por IP [H] | https://algomaster.io/premium | O servidor injeta um `currencyConfig` (BRL) por requisição; nada diz como a moeda é escolhida. Não confirmei com outra origem de IP. | NÃO VERIFICÁVEL |
| X08 | sysdesign §4 | DesignGurus: US$ 148 e US$ 123 "Discounted price for Your Region"; 188 mil alunos | https://www.designgurus.io/ | "Discounted price for Your Region $148"; "$123"; "188,183 learners"; "91,732 learners" (Fundamentals). | CONFIRMADO |
| X09 | economia §2.2 | VisualEconomik: EUR 2.000 (3 x 766 ou 6 x 433), 12 meses, +285 h; sem aviso de risco | https://www.visualbusiness.com/inversio-multimercado/suscripcion-directo | "€2,000"; "3 months at €766/month or 6 months at €433/month"; "12 meses"; "+285 Horas"; "Universidad de las Hespérides"; sem aviso de risco visível (leitor). | CONFIRMADO |
| X10 | ingles-tech §2 | DevSpeak: turmas de até 4, 2 aulas/semana, 52 módulos, garantias de 7 dias e 18 meses, preço só por formulário, fundador "Senior Software Engineer em Amsterdam" | https://devspeak.com.br | "no máximo 4 alunos"; duas aulas ao vivo por semana; 52 módulos; garantia de 7 dias; garantia de 18 meses ("100% do seu investimento de volta" se cumprir módulos e desafios); preço não exibido; "Senior Software Engineer em Amsterdam na Holanda", "13 anos", "700 alunos". | CONFIRMADO |
| X11 | ingles-tech §2 | English4IT: "Trusted by 65,000+"; Lite US$ 20, 7 dias, sem aula ao vivo, feedback humano de fala | https://www.english4it.online/ ; .../english-for-tech-lite | HTML bruto: "Trusted by 65,000+ tech professionals and companies worldwide"; "English For Tech Lite course for $20"; Lite: "7 lessons in 7 days", "No live lessons", "Real human feedback on speaking & pronunciation". | CONFIRMADO |
| X12 | ingles-tech §2 | Speak Tech: "3000+" alunos e newsletter "45k+" | https://speaktechenglish.com/ | "Join 3000+ preparing for global tech roles"; "Trusted by 45k+ engineers". O mesmo site também diz "5000+ STUDENTS" no bloco "Expert led" (inconsistência do próprio vendedor). | CONFIRMADO |
| X13 | ingles-tech §4 | Deel: +53% em 2025; desenvolvedores de software o cargo mais demandado; 2026-07-17 | https://www.deel.com/pt/blog/relatorio-contratar-talentos-no-brasil/ | "em 2025, a demanda global por profissionais brasileiros cresceu 53%"; "Desenvolvedores de software" em primeiro entre os mais contratados; "Last updated July 17, 2026". | CONFIRMADO |
| X14 | ingles-tech §4/§9 | Gemini TTS: "detect the input language automatically"; docs sem menção a mistura de idiomas nem controle de pronúncia; atualizada em 2026-10-01 | https://ai.google.dev/gemini-api/docs/speech-generation | "The TTS models detect the input language automatically."; sem SSML, guia de pronúncia nem mistura de idiomas; Português listado; "Last updated 2026-10-01 UTC". | CONFIRMADO |
| X15 | sysdesign §6 | System Design Primer: 373.411 estrelas, push 2026-09-15, licença Other | https://api.github.com/repos/donnemartin/system-design-primer | stargazers_count 373.414 (mesmo dia); pushed_at 2026-09-15T01:10:09Z; license key "other", SPDX NOASSERTION. | CONFIRMADO |
| X16 | sysdesign §8.1/§9 | SRE Book: CC BY-NC-ND 4.0; tabela 99,9 / 99,99 / 99,999 | https://sre.google/sre-book/availability-table/ | "Copyright © 2017 Google, Inc. Published by O'Reilly Media, Inc. Licensed under CC BY-NC-ND 4.0"; 8,76 h; 52,6 min; 5,26 min por ano. | CONFIRMADO |
| X17 | economia §7 | Resolução CVM 20: art. 1º caput, §1º, §2º ("vídeos"), art. 2º, art. 3º | https://conteudo.cvm.gov.br/export/sites/cvm/legislacao/resolucoes/anexos/001/resol020consolid.pdf | Texto extraído com pdftotext: "em caráter profissional, elabora relatórios de análise destinados à publicação, divulgação ou distribuição a terceiros"; §1º "valores mobiliários específicos ou sobre emissores de valores mobiliários determinados"; §2º "vídeos ... cujo conteúdo seja típico de relatório de análise, são equiparadas"; art. 2º "privativa de analistas ... credenciados"; art. 3º "É obrigatório o credenciamento". As citações da ficha conferem. | CONFIRMADO |
| X18 | economia §7 | CVM 2023-04-19: ~75% começaram por YouTube e influenciadores; foco em transparência do vínculo pago | https://www.gov.br/cvm/pt-br/assuntos/noticias/2023/cvm-divulga-estudo-sobre-possivel-regulamentacao-envolvendo-influenciadores-digitais-e-o-mercado-de-capitais | "Publicado em 19/04/2023 10h02"; "cerca de 75% das pessoas iniciaram seus investimentos com base em informações de canais do YouTube e influenciadores"; "o influenciador contratado por um regulado da CVM divulgue esse vínculo contratual quando oferecer conteúdo patrocinado". | CONFIRMADO |
| X19 | mei §3 | PLP 108/2021: R$ 144,9 mil (Câmara 2026-03-17) e R$ 130 mil (2026-04-29); até dois empregados | https://www.camara.leg.br/noticias/1254645-... ; https://www.camara.leg.br/noticias/1267536-... | Março: "eleva para R$ 144,9 mil" (PLP 108/21). Abril (atualizada em 30/04): "eleva para R$ 130 mil"; "autoriza a contratação de até dois empregados, o dobro do permitido hoje". A divergência entre as duas notícias oficiais existe. | CONFIRMADO |
| X20 | mei §3 | E-book Sebrae/MS: ©2025, imposto R$ 80,90, "O valor do DAS pode mudar todo ano", Contrata+Brasil até R$ 12.545,11 | https://sebrae.com.br/content/dam/portal-sebrae/na/midias/documentos/pdfs/ebook_precificacao-mei-contrata-brasil.pdf | pdftotext: "©2025. Serviço de Apoio às Micro e Pequenas Empresas ... Sebrae/MS"; "Imposto: R$ 80,90"; "O valor do DAS pode mudar todo ano e depende da sua ..."; "máximo de R$ 12.545,11". | CONFIRMADO |
| X21 | mei §3 | Manual DASN-SIMEI (set/2024): DAS de excesso 1,66%, 3,02%, 4,61%; "o caso de ICMS e ISS juntos não consta na página lida" | https://www8.receita.fazenda.gov.br/simplesnacional/arquivos/manual/manual_dasn-simei.pdf | pdftotext: "Atualizado em setembro de 2024"; 1,66% (sem ICMS e ISS), 3,02% (só ICMS), 4,61% (só ISS) e, na página seguinte, o caso conjunto: "3,02% ... sobre 50% do excesso e 4,61% ... sobre o restante do excesso". Também: comunicação até o último dia útil do mês seguinte; efeito no 1º de janeiro seguinte (até 20%) ou retroativo (mais de 20%); DASN até o último dia de maio; multa por atraso da DASN (MAED) de 2% ao mês, máximo 20%; limite do caminhoneiro R$ 251.600,00. | DIVERGENTE |
| X22 | mei §3 | Anexo XI: nenhum de designer, programador, consultor, marketing, social, assessor, tradutor, redator; nem "produtor de conteúdo" | https://www8.receita.fazenda.gov.br/SimplesNacional/Arquivos/manual/Anexo_XI.pdf | pdftotext do arquivo (criado em 2025-10-16): zero ocorrências de design, programad, consultor, marketing, social, assessor, tradutor, redator, conteúdo, software, web. Mas a lista contém "EDITOR(A) DE VÍDEO INDEPENDENTE", "INSTRUTOR(A) DE INFORMÁTICA", "INSTRUTOR(A) DE IDIOMAS", "INSTRUTOR(A) DE CURSOS GERENCIAIS", "INSTRUTOR(A) DE CURSOS PREPARATÓRIOS", "PROFESSOR(A) PARTICULAR", "FOTÓGRAFO(A)". As buscas da ficha estão certas; a conclusão (I) de que o freelancer de conhecimento fica de fora é exagerada para essas ocupações. | CONFIRMADO |
| X23 | mei §3 | DAS 2025: R$ 75,90 (5% de R$ 1.518,00) | https://www8.receita.fazenda.gov.br/simplesnacional/noticias/NoticiaCompleta.aspx?id=f8fd8ebc-76b2-46ce-8bd6-2379f9988501 | "02/01/2025"; "R$ 75,90 de INSS (5% do valor do salário-mínimo, de R$ 1.518,00)"; ISS R$ 5,00 e ICMS R$ 1,00. | CONFIRMADO |
| X24 | economia §2.2 | Anbima/B3: 515 finfluencers, 176,3 milhões de seguidores, 1º semestre de 2023, Economista Sincero em 1º | https://borainvestir.b3.com.br/noticias/economista-sincero-carol-dias-e-primo-rico-conheca-os-finfluencers-mais-relevantes-segundo-a-anbima/ | Números e ranking conferem. O artigo da B3 é de 08/12/2023; o CSV (economia L109) diz "divulgada em out/2023" sem citar fonte para essa data. | DIVERGENTE |
| X25 | economia §4 | BCB Copom (dados abertos): ODbL, atualização a cada 45 dias, JSON e PDF | https://dadosabertos.bcb.gov.br/dataset/atas-comunicados-copom | "Open Data Commons Open Database License (ODbL)"; "a cada 45 dias"; JSON pela API; atas em "formato texto, com tags html, e em formato PDF". | CONFIRMADO |
| X26 | economia §4 | Calculadora do Cidadão (BCB): IPCA, INPC, IGP-M, Selic, CDI etc. | https://www3.bcb.gov.br/CALCIDADAO/publico/exibirFormCorrecaoValores.do?method=exibirFormCorrecaoValores | Índices: IGP-M, IGP-DI, INPC, IPCA, IPCA-E, IPC-BRASIL, IPC-SP; abas TR, poupança, Selic, CDI, Taxa Legal. | CONFIRMADO |
| X27 | economia §2.2 | Seu Dinheiro: "Conteúdo Empiricus" e "Parceria com Empiricus"; newsletter gratuita | https://www.seudinheiro.com/ | Seções marcadas "Conteúdo Empiricus"/"Parceria com Empiricus"; "newsletter ... 100% gratuita"; sem preço. | CONFIRMADO |
| X28 | economia §0 | NPR+ "a partir de US$ 8/mês" | https://plus.npr.org/ | "GIVE $8/MONTH OR MORE" (texto de contribuição); sem preço do Planet Money+ na página. | CONFIRMADO |
| X29 | mei §6 | Contabilizei: planos R$ 195, R$ 225 e R$ 395; calculadora gratuita | https://www.contabilizei.com.br/ | "Padrão R$ 195/mês"; "Multibenefícios De: R$ 299 Por: R$ 225/mês"; "Experts R$ 395/mês"; CTAs "Abra sua empresa"/"Abrir CNPJ grátis". A "Calculadora Freelancer" não está na home (só "Calculadora de RPA online"); o CTA com "ABRA SUA EMPRESA GRÁTIS" não aparece literal. | CONFIRMADO |
| X30 | sysdesign §4 | Full Cycle MBA: 18 meses, 600 h, módulo System Design e Design Docs, início 2026-10-05 ou 2026-12-07, sem preço | https://mba.fullcycle.com.br | "18 months", "600 hours", duas turmas (5 de outubro e 7 de dezembro de 2026), sem preço ("Solicitar Contato"). | CONFIRMADO |
| X31 | sysdesign §0/§6 | ByteByteGo (home): "Become an AI Engineer"; 5 milhões; 1.000.000 inscritos; cursos de texto ilustrado; sem reembolso | https://bytebytego.com/ | "NEW Become an AI Engineer"; "Join over 5 million people"; "Over 1,000,000 Subscribers"; "The courses are text-based and include detailed illustrations"; "Refunds are not available for the courses". | CONFIRMADO |
| X32 | economia §0 | Paulo Gala: cursos EAD, mentoria, livros; sem preço nas páginas lidas | https://www.paulogala.com.br | 7 cursos nomeados mais outros (a ficha diz 6), mentoria, livros, palestras; nenhum preço; li 100 mil dos 111 mil caracteres. | CONFIRMADO |
| X33 | mei §4.2 | Freela Sem Crise: calculadoras gratuitas (preço, "quanto sobra", MEI x Simples x PF) e newsletter | https://www.freelasemcrise.com.br/calculadoras | 8 calculadoras; "Ferramentas gratuitas com impostos 2026 atualizados"; "Assinar newsletter". | CONFIRMADO |
| X34 | economia §2.1 | Lucena: Linktree sem produto com preço | https://linktr.ee/igormlucena | 7 links (artigos FGV IBRE, podcast, palestra, LinkedIn, assessoria de imprensa); nenhum preço. | CONFIRMADO |
| X35 | mei §6 e ingles-tech §6/§8 | Taxa da Hotmart: mei "9,9% + R$ 1"; ingles-tech "R$ 1,00 e, desde 2026-09-21, R$ 2,49" (terceiro) | https://hotmart.com/pt-br/taxa-hotmart ; https://tactus.com.br/taxas-da-hotmart-para-produtor/ | Hotmart (oficial, sem data na página): "9,9% + R$ 2,49 por venda aprovada" (percentual menor para faturamento anual maior; fixo R$ 2,49). Tactus (terceiro, "Atualizado em: agosto 31, 2026"): "R$ 1,00 até 20/09/2026; R$ 2,49 a partir de 21/09/2026". A página de ajuda da Hotmart não carregou (só o cabeçalho). | DIVERGENTE |
| X36 | economia §0/§6.1 | Armênia × Brasil: 6 cenas, 4 compare, 6 keyword, 2 stamp, 2 photo | data/episodes/armenia-brasil/scenes.json | Contagem idêntica (orientation portrait, pt-BR). O preview.mp4 tem 51,5 s (ffprobe) e 720x1280. | CONFIRMADO |
| X37 | economia §6.1/§7 | pares.md: de 9 pares só 2 comparáveis e 2 com ressalva | data/episodes/armenia-brasil/pares.md l. 5 | "comparar: P1, P2. Comparar com ressalva: P3, P4. Não comparar diretamente: P5, P6, P7, P8, P9." | CONFIRMADO |
| X38 | economia §6.2 | Gate 1 aprovou fichas de fonte única; FMI e OCDE recusam o robô; fecho "sem confirmação independente" | data/episodes/armenia-brasil/review.json ; outline.md l. 13 | "Todas as fichas são de fonte única; o lado armênio só tem o banco central (FMI e OCDE não baixados; servidores recusam o robô)"; outline: "sem confirmação independente neste vídeo (os dois lados)". | CONFIRMADO |
| X39 | economia §6.1 | ADR 011, decisão 7: a tela não calcula nem converte moeda | docs/decisions/011-planos-editoriais.md l. 94-95 | "A tela não calcula. Razão, variação percentual e soma só aparecem se estiverem numa ficha ... o template nunca converte moeda nem corrige valor." | CONFIRMADO |
| X40 | ingles/mei §8 | Ritmo 2-4 s por plano, gráfico e comparação com pelo menos 4 s; alertas do vp check | .claude/skills/roteiro-explicativo/SKILL.md l. 94, 146-147; app/pipeline/check.py l. 41, 217-246 | "Um plano a cada 2 a 4 s"; "gráfico, comparação, rede, cronologia e documento com pelo menos 4 s"; MAX_GRAPHIC_RUN = 4; alerta de mesmo tipo duas vezes seguidas; mais de 1 keyword por cena; tarja sem foto; barra com 2 pontos manda usar compare. | CONFIRMADO |
| X41 | ingles-tech §8 | text_fit: limites medidos em paisagem; value do compare sem limite | app/pipeline/text_fit.py l. 18, 58-60 | `COMPARE_LABEL = (44, 2)` "metade de 1600 px ... letra 36 (ValueCompare)"; só `side.label` passa por `fit`; `value` não. | CONFIRMADO |
| X42 | sysdesign §8.2 | Source.retrieved_at sem campo de versão; SourceKind; tipos de nó da rede | app/pipeline/schemas.py l. 83-99, 398 | Source: id, title, url, kind, retrieved_at, local_path, notes, interested, authors (sem versão); SourceKind primary/secondary/newspaper/archive; nós person/family/company/bank/government/other. | CONFIRMADO |
| X43 | sysdesign §8.2 | Custo por analogia: ADR 014 com 18 arquivos e ~444 linhas; ADR 015 com 14 arquivos e 302 linhas | git log do repositório | Implementação do ADR 014 (`289d8ac^..4c29bab`, PR #105): 15 arquivos únicos, 441 inserções, 118 remoções; com os commits de ADR (`9fd5df7^..0124c95`): 16 arquivos, 496 inserções. PR #107 (ADR 015): 14 arquivos, 302 inserções, 27 remoções. ADR 015 confere; no ADR 014 as linhas conferem (441 contra ~444) e os 18 arquivos da ficha provavelmente somam toques por commit. É estimativa por analogia, e a ficha a rotula assim. | CONFIRMADO |
| X44 | sysdesign §8.2 | Legenda queimada 54 px, entrelinha 1,25; área segura 288/500; janela do apresentador 28% | video/src/Scene.tsx l. 88; docs/decisions/014-perfil-vertical.md l. 41-47 | `fontSize: u(portrait ? 54 : 44), lineHeight: 1.25`; área segura "topo 288, base 500, direita 140, esquerda 60"; largura do apresentador 0,28 em retrato. | CONFIRMADO |
| X45 | ingles-tech §9 | ADR 012: o dono achou o Kokoro "sintético demais" | docs/decisions/012-voz-gemini-tts.md l. 10 | "O dono achou a voz sintética ..." (status da ADR: proposto). | CONFIRMADO |
| X46 | todos os CSVs | Estrutura e contagens (24 colunas; mei 42 publicações na janela; economia 108 = 9+1+84+14, 70 na janela; sysdesign 76; janelas por perfil) | os quatro *-evidencias.csv | Todas as linhas têm 24 campos; contagens e janelas de 90 dias recalculadas e iguais às das fichas. | CONFIRMADO |
| X47 | todos os CSVs | Datas das publicações (janela de 90 dias) | os quatro *-evidencias.csv | Decodifiquei o carimbo de tempo do shortcode do Instagram (método do sysdesign, validado por mim em 3 datas conhecidas) e comparei com `data_publicacao`: 168 linhas com URL e data; 162 iguais, 6 com 1 dia de diferença (fuso), nenhuma acima de 1 dia. | CONFIRMADO |
| X48 | brief e fichas | Kokoro "~0,7 s de síntese por segundo de áudio" | data/benchmarks/README.md l. 29; data/benchmarks/episodio-votorantim-dinheiro.md l. 40 | O 0,70 é o RTF da Fase 0 com a voz `am_michael` (inglês) e o modelo já carregado (1,52 na primeira execução). No vídeo-régua em pt-BR (`pm_alex`), 84 s de Kokoro para 10 WAVs de um vídeo de 93,1 s dão ~0,9 s por segundo. | DIVERGENTE |
| X49 | brief e fichas | Prévia 720x1280 de um curto de ~55 s: 40 a 110 s | repositório (data/benchmarks, docs) | Sem registro: nenhuma ocorrência em data/benchmarks/*.md nem no ROADMAP. O curto Armênia × Brasil tem 51,5 s. Só o 180 s de render em 720p paisagem do Votorantim (93 s) está documentado. | NÃO VERIFICÁVEL |
| X50 | sysdesign §2 | @bytebytego: bio "Sign up to our free newsletter for 5x more diagrams" | https://www.instagram.com/bytebytego/ | O meu leitor devolveu a bio "ByteByteGo / Learn System Design" e o link bit.ly/bytebytegoInst (o link coincide com o do CSV). A frase da newsletter não veio nesta leitura. | NÃO VERIFICÁVEL |
| X51 | sysdesign §0 (l. 16-17) | "Reel animado de conceito" e "o formato central do nicho, o diagrama" | ver seção F | É inferência sobre formato (ver F, S1 e S3); nenhuma página lida mostra o Reel "Big-O Race". | NÃO VERIFICÁVEL |
| X52 | mei §4.4 e ingles-tech §3.3 | Reels com métrica: @the.freelance.coach (10 curtidas, 18 comentários) e @devspeakacademy (5 curtidas) | instagram.com/the.freelance.coach/reel/Dax-nR7hzWw/ ; instagram.com/devspeakacademy/reel/Dd6tepnu8zz/ | Não reabertos: os 10 acessos permitidos já tinham sido usados. Não verificado por limite de acessos, não por bloqueio. | NÃO VERIFICÁVEL |
| X53 | mei §4.1 | @freelasemcrise com "3 seguidores" (incoerente com 12 Reels) | https://www.instagram.com/freelasemcrise/ | Não reaberto (limite de acessos). A própria ficha marca como não confirmado. | NÃO VERIFICÁVEL |

## 6. F. Varredura de honestidade (nada de vídeo descrito como assistido)

**Método.** Varredura por expressão regular em todas as 24 colunas dos quatro CSVs e nas quatro fichas, com termos de ritmo, corte, movimento, dinamismo, qualidade, edição, animação, narração, voz, cena, câmera, música, áudio, duração, estilo e verbos de assistir; mais a lista de valores distintos de `duracao`, `uso_animacao_apresentador_demo`, `formato_visual` e `tipo_evidencia`.

**Resultado.**
- `duracao` = "indisponível" em 100% das linhas dos quatro CSVs (mei 80, sysdesign 76, ingles-tech 37, economia 108).
- `tipo_evidencia`: zero ocorrências de "vídeo assistido"; só `descrição lida`, `site oficial`, `trecho indexado` e `estatística de terceiros`.
- Declaração explícita de que nenhum vídeo foi assistido: mei (l. 21, 77), ingles-tech (l. 3, 23-24) e economia (l. 5, 208). A sysdesign não traz declaração geral equivalente; diz só que não usou o texto alternativo para descrever vídeo (l. 27) e o CSV L19 registra "o vídeo não foi visto". Não é violação, mas a declaração falta.
- Não achei frase que descreva ritmo, cortes, movimento, qualidade ou duração de um vídeo concorrente como assistido. As ocorrências de "ritmo" são cadência de postagem (mei CSV L2, L6) ou ritmo de 2-4 s por plano da pipeline (ingles-tech l. 127; sysdesign l. 124).

**Ocorrências suspeitas ou limítrofes (arquivo e linha).**

| # | Onde | Trecho | Classificação |
|---|---|---|---|
| S1 | sysdesign-ficha.md l. 69 e l. 193; l. 51; sysdesign CSV L19 | "**Reel animado de conceito** pode render mais que diagrama estático [H]"; "o leitor falou em 'comparação visual em formato de corrida' (inferência dele)" | **Inferência sobre o vídeo sem base textual.** O Reel "Big-O Race" só tem título, hashtags e a inferência do leitor; "animação" só é declarada na bio ("visual explanations") e no site, não para esse Reel. Marcado [H], mas a premissa "animado" não foi lida. A ficha rotula a citação do leitor como inferência. |
| S2 | ingles-tech-ficha.md l. 9 (marcado (F)); l. 69; ingles-tech CSV L15 | "Reel de 2026-09-30 do @devspeakacademy com uma pergunta de entrevista em inglês **e um modelo de resposta, em série**" | **Leitura de legenda parafraseada pelo leitor**, não de vídeo. O CSV L15 admite "paráfrase do leitor, não citação literal" (inclusive o "Episode 1" e o próximo episódio). O rótulo (F) é forte demais para uma paráfrase de modelo pequeno. |
| S3 | sysdesign-ficha.md l. 8 e l. 152 | "o formato central do nicho, o diagrama" | Generalização a partir de 2 textos alternativos automáticos do ByteByteGo ("network protocol stack diagram"), da bio e do site; é sobre imagem estática, não sobre vídeo. Fica como inferência, escrita como fato no resumo. |
| S4 | ingles-tech-ficha.md l. 71 e l. 146; CSV L12 | "o Reel de 2026-09-19 ... usa música de catálogo" ("Bonnie Tyler - Total Eclipse of the Heart") | **Metadado de áudio exibido pela página**, não escuta. Aceitável, mas é a única menção a som de um vídeo concorrente. |
| S5 | texto alternativo automático do Instagram, sempre rotulado | sysdesign CSV L2, L4, L5, L41, L42, L46, L54, L56; ingles-tech CSV L6, L8, L9, L11 ("May be a ..."); economia CSV L2, L4, L7, L13, L17, L20, L37-L47, L62-L70 ("descrição da página ... não verificada") | **Só texto alternativo automático.** Os rótulos dizem que não permitem concluir o formato; sysdesign L46 e L54 acrescentam que "selfie" e "microphone" não provam pessoa em câmera. |
| S6 | economia CSV L3 e L28 | "Apresentador do Lucena Explica" (bio); "neste vídeo, compartilho três revistas" (legenda) | **Leitura de bio e de legenda**, com "presença em câmera ... não verificada". |
| S7 | mei CSV L2 | "Tema regulatório/educativo, formato estático" (@dicasmei) | Derivado do tipo de item indicado pela página (10 imagens, 1 carrossel). Aceitável. |

Separação pedida: **só leitura de legenda ou de texto alternativo automático** = S2, S4, S5, S6, S7. **Inferência sobre o vídeo sem base textual** = S1 (e S3, que é sobre imagem estática).

## 7. G. Contradições entre fichas

Nenhum perfil e nenhum produto aparece em duas fichas (interseção de handles: vazia; domínios compartilhados: só instagram.com, hotmart.com e gov.br). Os fatos repetidos são CONAR, Hotmart, Kiwify, o benchmark do Votorantim e as regras do retrato.

- **G1. CONAR (economia l. 194 x ingles-tech l. 123).** Economia: publicado 2026-05-26, em vigor desde 2026-06-01. Ingles-tech: matéria do Meio & Mensagem de 2026-05-13; resumo indexado com publicação em 12 e vigência em 13 de maio, efeitos desde 1º de junho. **Resolução pela página oficial:** notícia de "26 MAIO 2026" e "entram em vigor em 1º de junho"; 12 e 13 de maio não constam. Em terceiros: M&M diz publica e vigora em 13/05 (sem 1º de junho); KLA diz publica em 12/05, vigora em 13/05, efeitos em 1º/06. Economia está certa quanto ao que a página oficial diz; mas "publicado em 26/05" é a data da notícia do CONAR, que trata da versão diagramada em PDF de uma atualização que terceiros já noticiavam em 12-13/05 (mesmos temas: crianças e adolescentes, IA, transparência; que seja o mesmo texto é inferência minha). Ingles-tech cita só terceiros e eles divergem entre si. **Além disso:** "Comissão de afiliado precisa ser divulgada" (economia l. 194) não está na página do CONAR ("afiliad" e "comiss" ausentes da notícia); a política da Amazon cita o Código e o Guia, e o escritório KLA fala em "influenciadores, criadores e afiliados" no capítulo de governança. Como afirmação do CONAR, **não verificável** na fonte oficial.
- **G2. Taxa da Hotmart (mei l. 138 x ingles-tech l. 108 e 159).** Mei: "9,9% + R$ 1" (blog, não verificado). Ingles-tech: R$ 1,00 até 2026-09-20 e R$ 2,49 desde 2026-09-21 (Tactus, terceiro). **Resolução:** a página oficial `hotmart.com/pt-br/taxa-hotmart` mostra "9,9% + R$ 2,49 por venda aprovada". O R$ 1 da ficha MEI está desatualizado em 2026-10-06. Coincidência a não confundir: a taxa fixa da Kiwify também é R$ 2,49.
- **G3. Premissas de custo por Reel (hipóteses, mesma base de benchmark, premissas diferentes).** Agentes: mei 0,15 a 0,5 M tokens e 10 a 30 min (Reel de 30 s, fichas reaproveitadas, 2 rodadas); sysdesign e ingles-tech 0,3 a 0,8 M e 20 a 45 min; economia 0,34 a 0,77 M e 20 a 44 min. Render da prévia: mei 22 a 60 s; sysdesign e economia 15 a 90 s; **ingles-tech 40 a 110 s sem reescalar** (valor medido para ~55 s aplicado a Reels de 20 a 45 s). Tempo humano por Reel: **mei 20 a 45 min; sysdesign, ingles-tech e economia 30 a 90 min**. Não comparar custos entre nichos sem normalizar.
- **G4. Odômetro (brief l. 7 e economia l. 166 x mei l. 167 x código).** As três dizem que o odômetro não tem plano; o código o usa no plano `number` (E4c).
- **G5. Kokoro 0,7 s/s (brief; mei, ingles, economia, sysdesign) x Votorantim.** O 0,70 é do Fase 0 em inglês com modelo carregado; no vídeo-régua pt-BR são 84 s para ~93 s (X48).
- **G6. Conflitos já declarados pelas próprias fichas, sem resolução:** preço do ByteByteGo (US$ 84/ano numa resenha de afiliado; US$ 79 a 228 e US$ 499 vitalício em trechos de busca; página carrega no cliente); preço do Planet Money+ (US$ 3,99; 5,99/59,99; 6,99/69,99; NPR+ "8/mês ou mais"); PLP 108/2021 com R$ 144,9 mil (Câmara, 17/03) e R$ 130 mil (Câmara, 29/04), conferido em X19.
- **G7. Sem contradição:** Kiwify (mei x economia), Votorantim (todas), planos do retrato (todas), limites do Gemini (ingles, mei, economia), máximo de 8 palavras no keyword (ingles x economia).

## 8. Tabela final de vereditos

| ID | Item | Veredito |
|---|---|---|
| A1 | Bling: 10% no 1º ano, CNPJ, resgate R$ 100 | CONFIRMADO |
| A2 | Aced: 20% de comissão recorrente | CONFIRMADO |
| A3 | Cambly: US$ 30 por conversão; mínimo de gasto US$ 30 ou 50 | CONFIRMADO |
| A4 | Amazon Associados BR: livros 10% | CONFIRMADO |
| A5 | Kiwify: 8,99% + R$ 2,49 por venda | CONFIRMADO |
| A6 | beehiiv: gratuito até 2.500; Lite US$ 49/mês | CONFIRMADO |
| B7 | AlgoMaster Premium: R$ 152 / 392 / 785 | CONFIRMADO |
| B8 | Hello Interview Premium: US$ 47 / 78 / 275 | CONFIRMADO |
| B9 | Speak Tech English: e-books US$ 49,99 e 39,99; bundle US$ 99 | CONFIRMADO |
| B10 | Inglês para Devs: R$ 316 e R$ 632 por mês | CONFIRMADO |
| B11 | PeqArt (App Store BR): assinatura anual R$ 129,90 | CONFIRMADO |
| B12 | How To Go Freelance: US$ 29 (templates) e US$ 149 (curso) | CONFIRMADO |
| B13 | Visual Capitalist: VC+ US$ 7,49/mês anual; relatório US$ 80 | CONFIRMADO |
| C14 | DAS-MEI 2026 (INSS R$ 81,05; somas) | CONFIRMADO |
| C15 | Teto do MEI, proporcional, PLP 186/2026, dois funcionários | CONFIRMADO |
| C16a | CONAR (versão economia): publicado 2026-05-26, em vigor desde 2026-06-01 | CONFIRMADO |
| C16b | CONAR (versão ingles-tech): 12-13 de maio, efeitos desde 1º de junho | DIVERGENTE |
| C17 | CVM 2020-11-11: caráter profissional e "não é recomendação" | CONFIRMADO |
| C18 | EF EPI 2025 Brasil: 75º, nota 482 | CONFIRMADO |
| C19 | Dinamos: R$ 30 mil em um ano, 230 pessoas ativas, passou a gratuito | CONFIRMADO |
| C20 | Remotion: grátis até 3 pessoas; uso comercial; Company License acima | CONFIRMADO |
| C21 | Loja Kurzgesagt: só físicos, US$ 15,90 a 59,90 | CONFIRMADO |
| D1 | Instagram: @minhas_financas_organizadas (85,5 mil) | CONFIRMADO |
| D2 | Instagram: @garotadasplanilhas (81,2 mil) | CONFIRMADO |
| D3 | Instagram: @peqart.app (12,4 mil) | CONFIRMADO |
| D4 | Instagram: @algomasterio (394 mil) | CONFIRMADO |
| D5 | Instagram: @english_for_it (43,4 mil) | CONFIRMADO |
| D6 | Instagram: @paulogala (78 mil) | CONFIRMADO |
| D7 | Instagram: @imlucena (30,1 mil) | CONFIRMADO |
| D8 | Instagram: @visualcap (413 mil) | CONFIRMADO |
| D9 | Instagram: Reel /reel/Dcy-WrMO8MH/ (@minhas_financas_organizadas) (31 curtidas, 33 comentários, legenda "Comenta Precificação...") | CONFIRMADO |
| D10 | Instagram: Bônus: @bytebytego (559 mil) | CONFIRMADO |
| E1 | Retrato aceita só photo, broll, number, keyword, stamp, lower_third, compare, chart | CONFIRMADO |
| E2 | keyword: no máximo KEYWORD_MAX_WORDS palavras | CONFIRMADO |
| E3 | ADR 014 deixa rede, mapa, linha do tempo, árvore e documento fora do retrato | CONFIRMADO |
| E4a | compare ganha ramo de texto no retrato | CONFIRMADO |
| E4b | Pipeline, Gauge, CodeWalkthrough existem no kit e não têm plano | CONFIRMADO |
| E4c | Odometer existe no kit e não tem plano no template | DIVERGENTE |
| E5 | Gemini TTS: 10 chamadas/dia e 3/min; adapter sem glossário | CONFIRMADO |
| E6 | Votorantim: ~1,6 M tokens e ~1 h 31 para 93 s | CONFIRMADO |
| F | Varredura de honestidade | Sem violação clara; 2 casos limítrofes (S1, S2) |
| G | Contradições entre fichas | 2 resolvidas com fonte oficial (CONAR, Hotmart); 1 de premissas (G3); 1 de código (G4) |
| X01 | ByteByteGo afiliado: 5.000 "fans", "generous revenue sharing" sem %, cookie 30 dias, saque por PayPal | CONFIRMADO |
| X02 | Codemia: 1 ano de Premium em vez de comissão; conteúdo de 10 minutos ou mais; divulgação | CONFIRMADO |
| X03 | Aced é ex-Exponent; handle @aced__io | CONFIRMADO |
| X04 | Aced: moeda, cookie, pagamento mínimo e elegibilidade "não informados" | NÃO VERIFICÁVEL |
| X05a | Cambly: pagamento mensal por PayPal/Alipay; exige "an engaged audience"; sem limite de país declarado | CONFIRMADO |
| X05b | Trecho indexado: Cambly exigiria gasto mínimo de US$ 50 | REFUTADO |
| X06 | Kiwify: "Pix e transferência em 2 dias" | DIVERGENTE |
| X07 | AlgoMaster: moeda localizada por IP [H] | NÃO VERIFICÁVEL |
| X08 | DesignGurus: US$ 148 e US$ 123 "Discounted price for Your Region"; 188 mil alunos | CONFIRMADO |
| X09 | VisualEconomik: EUR 2.000 (3 x 766 ou 6 x 433), 12 meses, +285 h; sem aviso de risco | CONFIRMADO |
| X10 | DevSpeak: turmas de até 4, 2 aulas/semana, 52 módulos, garantias de 7 dias e 18 meses, preço só por formulário, fundador "Senior Software Engineer em Amsterdam" | CONFIRMADO |
| X11 | English4IT: "Trusted by 65,000+"; Lite US$ 20, 7 dias, sem aula ao vivo, feedback humano de fala | CONFIRMADO |
| X12 | Speak Tech: "3000+" alunos e newsletter "45k+" | CONFIRMADO |
| X13 | Deel: +53% em 2025; desenvolvedores de software o cargo mais demandado; 2026-07-17 | CONFIRMADO |
| X14 | Gemini TTS: "detect the input language automatically"; docs sem menção a mistura de idiomas nem controle de pronúncia; atualizada em 2026-10-01 | CONFIRMADO |
| X15 | System Design Primer: 373.411 estrelas, push 2026-09-15, licença Other | CONFIRMADO |
| X16 | SRE Book: CC BY-NC-ND 4.0; tabela 99,9 / 99,99 / 99,999 | CONFIRMADO |
| X17 | Resolução CVM 20: art. 1º caput, §1º, §2º ("vídeos"), art. 2º, art. 3º | CONFIRMADO |
| X18 | CVM 2023-04-19: ~75% começaram por YouTube e influenciadores; foco em transparência do vínculo pago | CONFIRMADO |
| X19 | PLP 108/2021: R$ 144,9 mil (Câmara 2026-03-17) e R$ 130 mil (2026-04-29); até dois empregados | CONFIRMADO |
| X20 | E-book Sebrae/MS: ©2025, imposto R$ 80,90, "O valor do DAS pode mudar todo ano", Contrata+Brasil até R$ 12.545,11 | CONFIRMADO |
| X21 | Manual DASN-SIMEI (set/2024): DAS de excesso 1,66%, 3,02%, 4,61%; "o caso de ICMS e ISS juntos não consta na página lida" | DIVERGENTE |
| X22 | Anexo XI: nenhum de designer, programador, consultor, marketing, social, assessor, tradutor, redator; nem "produtor de conteúdo" | CONFIRMADO |
| X23 | DAS 2025: R$ 75,90 (5% de R$ 1.518,00) | CONFIRMADO |
| X24 | Anbima/B3: 515 finfluencers, 176,3 milhões de seguidores, 1º semestre de 2023, Economista Sincero em 1º | DIVERGENTE |
| X25 | BCB Copom (dados abertos): ODbL, atualização a cada 45 dias, JSON e PDF | CONFIRMADO |
| X26 | Calculadora do Cidadão (BCB): IPCA, INPC, IGP-M, Selic, CDI etc. | CONFIRMADO |
| X27 | Seu Dinheiro: "Conteúdo Empiricus" e "Parceria com Empiricus"; newsletter gratuita | CONFIRMADO |
| X28 | NPR+ "a partir de US$ 8/mês" | CONFIRMADO |
| X29 | Contabilizei: planos R$ 195, R$ 225 e R$ 395; calculadora gratuita | CONFIRMADO |
| X30 | Full Cycle MBA: 18 meses, 600 h, módulo System Design e Design Docs, início 2026-10-05 ou 2026-12-07, sem preço | CONFIRMADO |
| X31 | ByteByteGo (home): "Become an AI Engineer"; 5 milhões; 1.000.000 inscritos; cursos de texto ilustrado; sem reembolso | CONFIRMADO |
| X32 | Paulo Gala: cursos EAD, mentoria, livros; sem preço nas páginas lidas | CONFIRMADO |
| X33 | Freela Sem Crise: calculadoras gratuitas (preço, "quanto sobra", MEI x Simples x PF) e newsletter | CONFIRMADO |
| X34 | Lucena: Linktree sem produto com preço | CONFIRMADO |
| X35 | Taxa da Hotmart: mei "9,9% + R$ 1"; ingles-tech "R$ 1,00 e, desde 2026-09-21, R$ 2,49" (terceiro) | DIVERGENTE |
| X36 | Armênia × Brasil: 6 cenas, 4 compare, 6 keyword, 2 stamp, 2 photo | CONFIRMADO |
| X37 | pares.md: de 9 pares só 2 comparáveis e 2 com ressalva | CONFIRMADO |
| X38 | Gate 1 aprovou fichas de fonte única; FMI e OCDE recusam o robô; fecho "sem confirmação independente" | CONFIRMADO |
| X39 | ADR 011, decisão 7: a tela não calcula nem converte moeda | CONFIRMADO |
| X40 | Ritmo 2-4 s por plano, gráfico e comparação com pelo menos 4 s; alertas do vp check | CONFIRMADO |
| X41 | text_fit: limites medidos em paisagem; value do compare sem limite | CONFIRMADO |
| X42 | Source.retrieved_at sem campo de versão; SourceKind; tipos de nó da rede | CONFIRMADO |
| X43 | Custo por analogia: ADR 014 com 18 arquivos e ~444 linhas; ADR 015 com 14 arquivos e 302 linhas | CONFIRMADO |
| X44 | Legenda queimada 54 px, entrelinha 1,25; área segura 288/500; janela do apresentador 28% | CONFIRMADO |
| X45 | ADR 012: o dono achou o Kokoro "sintético demais" | CONFIRMADO |
| X46 | Estrutura e contagens (24 colunas; mei 42 publicações na janela; economia 108 = 9+1+84+14, 70 na janela; sysdesign 76; janelas por perfil) | CONFIRMADO |
| X47 | Datas das publicações (janela de 90 dias) | CONFIRMADO |
| X48 | Kokoro "~0,7 s de síntese por segundo de áudio" | DIVERGENTE |
| X49 | Prévia 720x1280 de um curto de ~55 s: 40 a 110 s | NÃO VERIFICÁVEL |
| X50 | @bytebytego: bio "Sign up to our free newsletter for 5x more diagrams" | NÃO VERIFICÁVEL |
| X51 | "Reel animado de conceito" e "o formato central do nicho, o diagrama" | NÃO VERIFICÁVEL |
| X52 | Reels com métrica: @the.freelance.coach (10 curtidas, 18 comentários) e @devspeakacademy (5 curtidas) | NÃO VERIFICÁVEL |
| X53 | @freelasemcrise com "3 seguidores" (incoerente com 12 Reels) | NÃO VERIFICÁVEL |

## 9. O que a decisão não deve usar

1. **"Cambly exige gasto mínimo de US$ 50"** (trecho indexado): REFUTADO pela página oficial (US$ 30; "starting at $30").
2. **Taxa da Hotmart "9,9% + R$ 1"** (ficha MEI): desatualizada; a página oficial mostra R$ 2,49 fixos.
3. **"Guia do CONAR publicado e em vigor em 12-13 de maio"** e **"comissão de afiliado precisa ser divulgada" como se fosse do CONAR**: a página oficial só sustenta a notícia de 26/05 e a vigência em 1º de junho; a segunda frase não está nela (a política da Amazon e um escritório de advocacia a tangenciam). Confirmar com advogado antes de publicar.
4. **"Odômetro do kit sem plano"**: já está dentro do plano `number`. Sem plano: Pipeline, Gauge, CodeWalkthrough, CodeBlock, ContextWindow, AnimatedGraph, Highlighter.
5. **"Newsletter paga custa US$ 49/mês" (beehiiv)** e **"Aced não informa pagamento"**: o US$ 49 é cobrança anual na faixa de 1.000 inscritos; os termos de pagamento do Aced estão num FAQ que não consegui ler.
6. **"Reel animado de conceito rende mais" e "o formato central do nicho é o diagrama"** (sysdesign): sem leitura de vídeo; só hipótese.
7. **"Dinamos chegou ao ponto de equilíbrio" e "230 clientes"**: o texto diz que cobriu custos fixos de manutenção e fala em 230 pessoas ativas; receita autodeclarada.
8. **"O MEI de serviço é o prestador manual; o freelancer de conhecimento fica fora"** sem ressalva: o Anexo XI traz editor de vídeo, instrutor de idiomas e de informática, professor particular e fotógrafo; só designer, programador, consultor e afins estão ausentes.
9. **Custos por Reel comparados entre nichos, "Kokoro 0,7 s/s" e "render 40-110 s"**: premissas diferentes ou sem registro em pt-BR (G3, X48, X49). Os únicos dados medidos são os do Votorantim (180 s de render em 720p paisagem; 84 s de Kokoro).
10. **Preços de concorrentes como âncora:** os e-books da Speak Tech são promocionais (lista 40% a 62% maior); o AlgoMaster em R$ pode ser moeda localizada por IP; o curso de US$ 149 é "Early Bird".
11. **Métricas de demanda por Reel** (curtidas de 1 Reel por perfil, comentários de CTA, "9 posts em 21 dias"): visualizações não existem nas páginas públicas; os 33 comentários do Reel D9 são em boa parte a palavra-chave do CTA.
