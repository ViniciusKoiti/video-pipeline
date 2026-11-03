# Alternativas fora de filosofia para canais narrados

Consulta: 01/11/2026. Pergunta: quais linhas populares em pt-BR podem ser produzidas como vídeo longo narrado, sem apresentador, aproveitando o pipeline existente?
Estas notas tratam de viabilidade editorial e de ativos. Não medem demanda nem autorizam produção.

## Conclusão

As quatro linhas abaixo cabem como propostas de pesquisa. Eu avaliaria primeiro **como funciona o cotidiano**
e **histórias de marcas conhecidas**, porque permitem uma pergunta simples e uma explicação visual própria.
A ordem é inferência editorial; cabe ao panorama por MCP avaliar interesse do público.
“Dark” descreve a ausência de apresentador, não uma licença nem um nicho.

## Fatos locais e fontes conferidas

- [CLAUDE.md](../../../../CLAUDE.md), §§1–2, consultado em 01/11/2026: o projeto já tem documentário
  histórico e explicativo; a linha de “dinheiro e poder” foi ensaiada no caso Votorantim.
- [Modelo de perfil de poder](../../modelo-perfil-de-poder.md), consultado em 01/11/2026:
  a ligação com produtos e serviços usados pelo espectador vem cedo; mecanismo e causa organizam a narrativa;
  controvérsia tem autor, data e desfecho, e fonte empresarial é interessada.
- [ADR 007](../../../../docs/decisions/007-contratos-de-dados.md), consultada em 01/11/2026:
  permite acervo com domínio público ou licenças aceitas, bancos registrados e gráficos originais.
  Não permite presumir licença de uma foto só porque está em página pública.
- [CVM](https://www.gov.br/cvm/pt-br), página inicial aberta em 01/11/2026:
  oferece entradas para dados abertos, regulados, documentos enviados e processos.
  O portal não comprova sozinho um fato sobre a história de uma empresa.
- [ONS](https://www.ons.org.br/), página inicial aberta em 01/11/2026:
  há entradas para carga/geração, balanço de energia e reservatórios.
  Parte da página depende de scripts; nenhum dado de um evento foi extraído.
- A abertura de https://www.ibge.gov.br/ e
  https://bndigital.bn.gov.br/hemeroteca-digital/ recebeu HTTP 403 nesta ferramenta.
  São pistas de pesquisa, não documentos conferidos nesta rodada.

## Quatro linhas propostas

| Linha | Pergunta de vídeo proposta | Fontes primárias necessárias | Visual viável no pipeline | Esforço e limite editorial |
|---|---|---|---|---|
| Consumo do dia a dia | “Por que a embalagem diminui e o preço não?” | Registros datados da mesma embalagem antes/depois, documentos ou resposta do fabricante e órgãos de defesa do consumidor; séries do IBGE apenas para o contexto que elas realmente medirem. | Embalagens genéricas desenhadas, comparação de quantidade/preço e conta por unidade; registro real só com origem e direitos conferidos. | Médio: escolher um produto/caso documentado. Não afirmar que todas as marcas fazem a mesma coisa nem usar inflação como prova de redução de quantidade. |
| Marcas que todo mundo conhece | “O que aconteceu com a Mesbla?” ou outra marca com documentação suficiente | Registros societários, documentos de recuperação/falência quando existirem e forem públicos, balanços de companhia aberta quando aplicáveis, anúncios e jornais contemporâneos; confrontar material da própria empresa. | Linha do tempo, mapa de expansão, números e fotos de acervo autorizadas. Pode seguir o mecanismo já usado no perfil de poder. | Médio/alto: a pesquisa precisa separar causas documentadas de explicações retrospectivas. Não presumir que a CVM tenha documentação de toda empresa fechada. |
| Como o cotidiano funciona | “Como uma falha consegue deixar tanta gente sem luz?” | Relatório técnico de um evento escolhido, explicações do operador e regulador, dados ou diagramas públicos cuja reutilização seja verificada. | Diagrama original de geração, transmissão, distribuição e falha em cascata; estados e mapas, com stock apenas como ambiente. | Médio: precisa verificar o mecanismo e suas exceções. Um relatório de evento não autoriza copiar suas imagens nem generalizar a causa para todo apagão. |
| História real com suspense | “Como uma expedição ficou presa no gelo?” | Diário ou memória de participante, documentos e jornais de época, pesquisa histórica independente; escolher caso com acervo utilizável. | Fotos em domínio público conferidas por ativo, mapa da rota, calendário e trechos documentais breves. | Médio/alto: é o recorte histórico já previsto no projeto. A hipótese de ser mais barato de ilustrar depende da licença de cada foto. |

Os exemplos são perguntas de pesquisa, não afirmações verificadas para roteiro. Esforço é julgamento comparativo,
sem medição de horas. Nenhuma linha exige criar motor, serviço ou dependência nova.

## Inferências

1. Começar por situações reconhecíveis — mercado, conta de luz, uma marca que sumiu — amplia a possibilidade
   de compreensão imediata, mesmo sem repertório prévio. Isso é uma hipótese de clareza, não previsão de alcance.
2. “Como funciona o cotidiano” permite sustentar a imagem com diagramas próprios, reduzindo a dependência
   de clipes de TV e cenas de terceiros.
3. História empresarial aproveita mais diretamente o modelo já escrito para Votorantim; a escolha do caso deve
   depender dos documentos e dos ativos, além das views dos concorrentes.
4. Fotografias e jornais antigos podem favorecer a linha histórica, mas antiguidade e disponibilidade online
   não substituem a verificação de licença exigida no projeto.

## Lacunas

- Demanda, concorrentes, frequência e audiência serão avaliados separadamente pelo MCP; não foram pesquisados aqui.
- Nenhum caso tem ficha, fontes baixadas, licenças aprovadas ou plano de imagens pronto nesta rodada.
- Acesso público a um documento não significa permissão automática para reutilizar o documento como imagem.
- Não foram calculados custo por episódio, RPM ou prazo de produção.
- A escolha de uma nova série/canal e do primeiro caso continua com o dono.

