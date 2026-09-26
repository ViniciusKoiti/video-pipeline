# Modelo de perfil de poder (2026-09-26)

Origem: o dono pediu a um agente próprio uma análise do roteiro do vídeo sobre Peter Thiel do canal How Money
Works, para extrair como o vídeo liga a pessoa à vida do espectador e explica a ascensão à elite. Motivo: na
fatia Votorantim, o dono sentiu falta de um objetivo na apresentação da família ("o que ele fez, como impacta
o nosso dia a dia, como se tornou elite"). Este documento guarda o que adotamos, o que não adotamos e por quê.
O método operacional está nas skills `fichamento`, `roteiro-explicativo` e `checagem` (ADR 009).

## Como o vídeo de referência se organiza (resumo da análise)

| Bloco | Tempo | Fatia | Função |
|---|---|---|---|
| Gancho e mistério | 00:00–02:32 | ~12% | quem é e por que importa; lista de empresas conhecidas no 1º minuto |
| Origem e capital inicial | 02:32–04:04 | ~7% | de onde veio o primeiro dinheiro (rede de família e amigos) |
| Primeira grande vitória | 04:04–05:32 | ~7% | o negócio que o deixou rico |
| Mecanismo de multiplicação | 05:32–08:44 | ~15% | como a riqueza de um negócio virou influência e o próximo negócio |
| Escala e regras | 09:52–11:46 | ~9% | uso de regras do sistema (veículo com vantagem fiscal), contraste com a classe média |
| Custo do poder e ideologia | 11:46–15:18 | ~16% | o que faz com o dinheiro |
| Controvérsia | 15:18–17:34 | ~11% | quem perdeu; acusações atribuídas a veículos de imprensa |
| Fecho | 17:34–21:06 | ~17% | por que age assim hoje e o efeito no mundo real |

## O que adotamos

- **Ponte com o espectador no 1º minuto:** o que ele usa ou paga, dito cedo e retomado ao longo do vídeo.
- **Causa no lugar de cronologia:** cada elo da ascensão diz o tipo de vantagem (capital, rede, informação,
  regra, timing, risco, escala) e se liga ao anterior por "por isso", "graças a", "mas".
- **Controvérsia atribuída:** "segundo o órgão X, em tal ano"; nunca afirmar crime ou intenção.
- **Contraste de escala:** comparar números do personagem com referências do dia a dia, com fonte.
- **Fonte interessada só para escala física**, confrontada com fonte independente.
- Dois tipos de fato novos: `impact_today` e `rule` (ver `FactKind`).

## O que não adotamos, e por quê

- **Enquadramento de vilão** ("vantagem injusta", "quem ele destruiu", "táticas brutais"): com pessoas vivas e
  empresa ativa, rotular antes de pesquisar é julgamento prévio. Tom do canal: crítico e documentado, com os
  mesmos blocos em nomes neutros.
- **Tipos de fato `network_effect` e `collateral_damage`:** já cabem em `mechanism` e `conflict`.
- **Perguntas com a resposta embutida** (ver abaixo): levariam o pesquisador a procurar confirmação em vez do fato.
- **Gírias e ironia de cultura pop** ("villain origin story", "finance bro"); a própria análise recomenda evitar.
- **"Vamos ser justos" a cada 2 minutos como fórmula:** contraponto só quando houver fato documentado.

## Perguntas de pesquisa genéricas (neutras)

Servem para qualquer personagem de "dinheiro e poder". São perguntas; a resposta só vem de fonte baixada.

- **Gancho de impacto:** O que o público usa ou paga hoje que vem de empresas do personagem, com que participação
  e em que ano? Que número de escala as fontes dão, e com o que dá para comparar?
- **Origem e vantagem:** Qual era a posição social e econômica dos fundadores antes do primeiro negócio? De quem
  veio o primeiro capital, e qual a relação com eles? Que acesso (educação, crédito, rede, informação) eles tinham
  e os concorrentes não, segundo as fontes?
- **Virada:** Quando o grupo passou a controlar mais de uma etapa da cadeia? Houve crise, guerra ou falência de
  terceiros em que o grupo comprou ativos, por quanto? Trouxe tecnologia ou modelo de negócio antes dos
  concorrentes locais, se trouxe?
- **Mecanismo:** Como o dinheiro de um negócio financiou o seguinte (lucro reinvestido, crédito, venda de
  ativos)? Quais bancos, fundos ou sócios financiaram as expansões?
- **Regras e Estado:** Que leis, tarifas, crédito público, concessões ou decisões de Estado afetaram o grupo, a
  favor ou contra? Como o grupo está organizado hoje, segundo documentos públicos?
- **Custo e controvérsia:** O grupo foi parte em processos, investigações, greves ou acidentes documentados?
  Quem decidiu, o quê, quando, e qual o desfecho? Quem perdeu com as decisões do grupo, segundo as fontes?
- **Presente:** Em que setores o grupo atua e investe hoje? Como a família participa da gestão?

## Aplicação ao caso Votorantim (perguntas reescritas)

A análise original trazia nomes, setores e acusações dentro das perguntas, e nada disso está nas fontes
baixadas. Reescritas como neutras, com o tipo de fonte que responderia:

| Bloco | Pergunta | Onde procurar |
|---|---|---|
| Gancho | Que produtos e serviços do dia a dia vêm hoje de empresas do grupo, e com que participação? | Relatório anual e RI (interessada), confirmado por dado público ou imprensa independente |
| Gancho | Em quais negócios o grupo divide o controle com outros sócios, inclusive estatais? | CVM, relatórios, imprensa |
| Origem | Que papel o Estado ou relações políticas tiveram na compra de 1918, se tiveram? (as fontes atuais descrevem um leilão de falência) | Hemeroteca Digital, acadêmica |
| Origem | De onde veio o dinheiro de Pereira Ignácio para o leilão e para comprar a parte de Scarpa? (já em `open_questions`) | Acadêmica, Hemeroteca |
| Virada | Quando e como o grupo entrou em setores além dos tecidos? | Acadêmica (source-03 cobre até 1980) |
| Virada | O grupo comprou concorrentes ou ativos em crises? Quais, quando, por quanto? | Atos de concentração do CADE, imprensa |
| Mecanismo | Como as expansões foram financiadas: lucro, crédito público, mercado? | Dados abertos do BNDES, CVM, acadêmica |
| Regras e Estado | Que tarifas, créditos ou concessões públicas afetaram o grupo? | Acadêmica, dados públicos |
| Custo | O grupo foi parte em processos no CADE? Quais, com que decisão, ano e desfecho? | Decisões públicas do CADE |
| Custo | Há registros de greves, acidentes ou processos ambientais em unidades do grupo? | Imprensa independente, órgãos ambientais |
| Presente | Como o grupo está organizado hoje, e como a família participa da gestão? | Documentos societários públicos, RI (interessada) |

## Riscos

- **Pessoas vivas e empresa ativa:** só ações documentadas de negócio; nada de personalidade ou vida privada.
- **Difamação:** toda acusação com quem acusou ou decidiu, o quê, quando e o desfecho (recurso, acordo).
- **Fonte interessada:** material da própria empresa só para escala física, e sempre confrontado.
