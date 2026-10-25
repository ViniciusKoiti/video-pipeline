# Crescimento no YouTube: embalagem e hipóteses

**Consulta:** 23/10/2026. **Recorte:** vídeos longos explicativos e ensaios em pt-BR do mesmo canal e série.
**Pergunta:** quais recomendações externas ajudam a escolher a ordem do trabalho e o próximo teste neste pipeline?

A proposta é adequada: pesquisar afirmações, planejar a embalagem na pauta e ligar cada teste a uma publicação.
A mudança mais defensável para experimentar primeiro é antecipar **o título provisório e o conceito da capa**.
A produção da arte continua dependendo dos ativos e direitos; o gate 4 continua sendo a revisão final do dono.
Essa é uma hipótese de processo, com possível redução de retrabalho. Seu efeito na audiência ainda é desconhecido.

Este documento verifica uma seleção de afirmações de Paddy Galloway, Ed Lawrence/Film Booth, da equipe do YouTube
e da vidIQ. Não é uma medição de demanda nem uma análise completa dos canais pelo método do molde. Não foram
baixados vídeos, medidos cortes ou consultados painéis privados. Os relatos dos criadores foram conferidos em
entrevistas e transcrições publicadas pelo próprio entrevistador; os minutos abaixo são localizadores publicados,
sem conferência audiovisual segundo a segundo.

**Rodada 2 (23/10, 22h):** as seções 8 a 14, no fim do documento, ampliam a pesquisa com o vídeo indicado pelo dono, uma segunda leva de criadores em inglês, os criadores brasileiros, o YouTube oficial além das três páginas acima, as contradições entre as fontes, o cruzamento com os dois moldes medidos do nicho e as hipóteses H05 a H07. As seções 1 a 7 e o adendo ficaram como estavam.

## 1. O que foi confirmado na aplicação

| Ponto a conferir | Verificação em 23/10 | Consequência |
|---|---|---|
| O contrato já aceita hipótese por publicação | `PublicationMetrics.hypothesis` é `str \| None`; `readings` aceita `d7` e `d28`. | Usar uma hipótese principal por publicação em texto; não criar lista, schema ou serviço novo. |
| Momento de criar o `metrics.json` | `published_at`, `channel`, `platform` e `format` são obrigatórios. O script `iniciar` usa flags ou dados do registro de agendamento. | Preparar a hipótese na pauta; criar o registro quando os metadados reais estiverem disponíveis. Não inventar data de publicação. |
| Momento de executar a miniatura | A skill `miniatura` e o §15 situam sua execução entre os gates 3 e 4. | Antecipar o conceito, sem exigir a imagem final antes de pesquisar ou aprovar ativos. |
| Embalagem já era um gap | O relatório de 12/10 registra título, capa e primeiro quadro fora do fluxo principal. Já há skill de miniatura e análise de referência de 20/10. | O diagnóstico histórico precisa dessa atualização: há execução da capa; o problema verificado agora é seu planejamento tardio. |
| Disponibilidade de resultados para a comparação | Os quatro registros de vídeos longos de 20–23/10 têm `hypothesis: null` e `readings: {}`. | Não atribuir retrospectivamente a eles uma hipótese escolhida nesta pesquisa. |
| Alcance da regra dos quatro vídeos | O §12 pede quatro vídeos no mesmo recorte em 4–6 semanas. | É um lote editorial mínimo do projeto, não cálculo de poder estatístico nem prova causal. |

Fontes locais: [contrato](../../app/pipeline/schemas.py), [leitura e gravação das métricas](../../app/pipeline/metrics.py),
[script de métricas](../../scripts/provisorio/metricas.py), [testes do contrato](../../tests/test_metrics.py),
[pauta](../../.agents/skills/vp-pauta/SKILL.md), [miniatura](../../.claude/skills/miniatura/SKILL.md),
[contexto, §§4, 12 e 15](../../CLAUDE.md), [gaps de 12/10, §3.2](../RELATORIO-GAPS-AUDIENCIA-ENGAJAMENTO.md) e
[análise de miniaturas de 20/10](miniaturas-filosofatos-2026-10-20.md).

O grafo estava pronto, mas sua geração era de 15/10. A consulta não encontrou os símbolos novos de métricas;
a cobertura indicou arquivos alterados ou ainda não rastreados. As conclusões acima vêm da leitura da fonte atual,
não de uma inferência de ausência no índice. Na rodada inicial de pesquisa, nenhum arquivo de produção foi alterado.

## 2. Referências e qualidade da evidência

| Referência | Material conferido | Base declarada e limite |
|---|---|---|
| **Paddy Galloway** | [Entrevista publicada pelo Creator Science, 13/06/2023, com transcrição](https://creatorscience.com/podcast/paddy-galloway/) e [vídeo](https://www.youtube.com/watch?v=UHhTKwclHCs). | Experiência de consultoria e exemplos. Nesta entrevista, não há amostra auditável nem teste controlado que sustente uma regra universal. |
| **Ed Lawrence / Film Booth** | [Entrevista publicada pelo Creator Science, 04/07/2023, com transcrição e capítulos](https://creatorscience.com/podcast/ed-lawrence/) e [vídeo](https://www.youtube.com/watch?v=MRz5QwkAJqw). | Relato do próprio fluxo e de feedback da comunidade. Não há base bruta ou grupo de controle apresentado nesse material. |
| **Equipe do YouTube** | [Creator Insider: algoritmo, 25/05/2023](https://www.youtube.com/watch?v=67TkpHKv9tE), capítulos públicos; documentação atual de recomendações, retenção e A/B. | Creator Insider se apresenta como canal informal da equipe técnica. Os capítulos localizam assuntos; as afirmações operacionais foram conferidas na documentação atual da plataforma. |
| **vidIQ** | [Estudo de miniaturas, versão de 08/07/2026](https://vidiq.com/research/youtube-thumbnail-study/) e [guia comercial de miniaturas, 14/07/2026](https://vidiq.com/blog/post/youtube-thumbnail-design-tips/). | Declara 500 vídeos de destaque, 30 nichos, junho/2026; canais com pelo menos 10 mil inscritos, vídeos com pelo menos 50 mil views e limite de dois por canal. Publica agregados, sem registros individuais. Seleção de sucessos e interesse comercial limitam a inferência. |

São quatro referências, **não quatro canais medidos com bases independentes e replicadas**. As duas entrevistas
compartilham o mesmo editor. Ter muitos clientes ou inscritos não substitui declarar amostra, seleção e método.
Não foi confirmado um vídeo com minutagem para o estudo da vidIQ: sua fonte nesta rodada é escrita.
YouTube Creators continua candidato para uma rodada audiovisual específica; não foi contado como canal analisado.
Não foram selecionados canais em pt-BR sem conferência.

## 3. Tabela de afirmações

**Oficial** identifica informação atribuída à plataforma e conferida em fonte própria; não garante um ganho local.
**Ofício** identifica prática profissional ou observação descritiva com alcance limitado.
**Folclore** identifica uma generalização causal sem sustentação apresentada ou que contraria a fonte oficial.
Ausência de confirmação oficial, sozinha, não torna uma observação falsa.

A coluna de medida indica o que pode corroborar ou contrariar uma hipótese. Uma taxa isolada não confirma uma
explicação causal. Onde a fonte é escrita, a seção substitui o minuto; não se inventa um timestamp.

| ID | Afirmação delimitada | Tipo | Fonte e localizador | Medida ou verificação | Entrada na pipeline |
|---|---|---|---|---|---|
| A01 | Paddy recomenda trabalhar ideia, título e capa antes da produção. | Ofício | [Vídeo, bloco 01:04–04:22](https://www.youtube.com/watch?v=UHhTKwclHCs&t=64s); transcrição da entrevista. | Minutos de retrabalho e mudanças de conceito tardias; audiência é resultado secundário. | C1: pauta. |
| A02 | Paddy considera o uso de texto na capa dependente do contexto. | Ofício | [Vídeo, 15:37](https://www.youtube.com/watch?v=UHhTKwclHCs&t=937s); transcrição. | Entendimento em tamanho reduzido; teste nativo entre variantes quando disponível. | C1/C4: conceito e capa. |
| A03 | Ed relata resolver a embalagem antes de escrever o roteiro. | Ofício | [Vídeo, capítulo 07:19](https://www.youtube.com/watch?v=MRz5QwkAJqw&t=439s), “Packaging Comes First”; transcrição. | Reaberturas de roteiro por mudança de promessa e tempo de revisão. | C1 → C3. |
| A04 | Ed propõe histórias curtas e metáforas para explicar conceitos. | Ofício | [Vídeo, capítulos 13:48](https://www.youtube.com/watch?v=MRz5QwkAJqw&t=828s) e [17:34](https://www.youtube.com/watch?v=MRz5QwkAJqw&t=1054s); transcrição. | Resposta a pergunta de compreensão; observar a curva real se fornecida. | C3/C4: escrita e storyboard. |
| A05 | O sistema busca relevância por espectador e satisfação de longo prazo. | Oficial | [Creator Insider, capítulo 01:51](https://www.youtube.com/watch?v=67TkpHKv9tE&t=111s), assunto; confirmação na [documentação de recomendações](https://support.google.com/youtube/answer/16533387?hl=en). | Não existe uma taxa local única que valide o sistema; observar consumo e feedback em contexto. | C1/C8: público e aprendizado. |
| A06 | O relatório de introdução mede a permanência após 30 s e orienta conferir a expectativa criada por título e capa. | Oficial | [Retenção, seção “Intros”](https://support.google.com/youtube/answer/9314415?hl=en); fonte escrita. | `retention_30s_percent`, com amostra e tráfego; conferir a promessa no texto. | C1/C3/C8. |
| A07 | O A/B nativo compara até três variantes de título, capa ou combinação e escolhe por tempo de exibição. | Oficial | [A/B, seções de funcionamento e critério do vencedor](https://support.google.com/youtube/answer/16391400?hl=en); fonte escrita. | Resultado do próprio teste, inclusive “inconclusivo”; CTR serve de diagnóstico adicional. | C8: leitura no Studio. |
| A08 | Um teste nativo pode levar até duas semanas; poucas impressões podem impedir um vencedor. | Oficial | [A/B, seções de prazo e ausência de vencedor](https://support.google.com/youtube/answer/16391400?hl=en). | Estado e período efetivos do teste nas notas de D7/D28; não encerrar por pressa de ler D7. | C8. |
| A09 | A vidIQ declara rosto humano em 69% de 500 miniaturas de destaque. | Ofício — observação declarada | [Estudo, tabela e metodologia](https://vidiq.com/research/youtube-thumbnail-study/); fonte escrita. | Agregado do autor; efeito local exige comparação própria. Não extrapolar rosto humano para avatar 2D. | C4/C5: candidato de capa, adiado. |
| A10 | A vidIQ recomenda conferir a capa em tamanho pequeno. | Ofício | [Guia, seção “Design for mobile first”](https://vidiq.com/blog/post/youtube-thumbnail-design-tips/). | Pessoas do público identificam assunto e promessa na prévia; registrar acertos e total. | C1/C4: revisão antes do roteiro. |
| F01 | “Toda capa precisa de rosto ou de um número fixo de palavras.” | Folclore — extrapolação a rejeitar | Generalização avaliada aqui, não citação atribuída a um canal; confrontar A02 e o [estudo descritivo](https://vidiq.com/research/youtube-thumbnail-study/). | A frequência de um traço entre sucessos não estabelece necessidade nem causalidade. | Não virar regra de schema ou gate. |
| F02 | “Existe horário mágico que determina o alcance de longo prazo.” | Folclore — contrariado pela orientação oficial | Formulação avaliada aqui, não fala atribuída aos entrevistados; [YouTube, seção sobre horário](https://support.google.com/youtube/answer/16533387?hl=en). | Separar resposta imediata de desempenho posterior; não priorizar um agendador para resolver essa hipótese. | C8: prioridade baixa. |

Os capítulos de Ed e os relógios dos blocos da transcrição publicada não coincidem em todos os pontos.
Os links de A03/A04 usam os **capítulos publicados**, como localizadores aproximados. A leitura da transcrição
confirma o conselho, mas uma citação audiovisual exata exigirá conferir o vídeo. A05 usa o capítulo apenas para
localizar o tema: a confirmação textual está no Help Center.

## 4. Como experimentar a embalagem cedo

Proposta para a próxima pauta ainda não aprovada, aproveitando os mesmos artefatos e gates:

1. **Na pauta:** escrever a pergunta, a promessa provisória, duas opções de título e um esboço textual da capa
   por opção. Relacionar cada proposta às evidências que ainda precisamos obter. Título pode mudar se as fontes
   não sustentarem a promessa. Registrar uma hipótese principal, a variável e a medida.
2. **Antes do roteiro:** escolher uma proposta com o dono. Fazer uma leitura de compreensão do conjunto
   título/capa/abertura; anotar o que a pessoa espera aprender. Isso avalia clareza, sem prever CTR.
3. **No roteiro e gate 2:** conferir se as fichas sustentam o prometido e se a abertura prepara sua entrega.
   Conselhos de crescimento orientam forma; a fala e as afirmações factuais continuam saindo das fichas.
4. **Entre gates 3 e 4:** produzir a arte com ativos registrados, reutilizando a skill de miniatura. O esboço
   antecipado não autoriza usar uma imagem nem aprova direitos.
5. **No gate 4:** o dono confere coerência entre título, arte, primeiro quadro, fala e conclusão. Corrigir uma
   divergência assim que descoberta; “confirmar no gate 4” não significa acumular problemas até esse momento.
6. **Na publicação autorizada e nas leituras:** transportar a hipótese previamente registrada para `metrics.json`,
   registrar dados reais e observar D7/D28. Se houver A/B autorizado, registrar variante, início, fim e resultado
   nas notas. Não trocar título, roteiro e animação ao mesmo tempo para tentar explicar um único efeito.

O esforço antecipado deve ser pequeno: conceito e esboço, sem produzir várias artes finais antes de conhecer as
fontes. A hipótese é economizar mudanças tardias de direção; não há economia medida ainda. Esta pesquisa não
alterou as skills nem tornou esse processo uma obrigação nos episódios existentes. A aplicação posterior autorizada
está registrada no adendo ao fim deste documento.

## 5. Hipóteses prontas para as próximas pautas

Ordem de planejamento; não é agenda de publicação nem decisão de aplicar todas. O dono ainda não indicou neste
pedido um próximo episódio para o teste. Não foram inventados tema, tese, data, resultado ou aprovação.

| Hipótese | Mudança e principal medida | Acompanhamento | Quando usar |
|---|---|---|---|
| **H01 — Embalagem antecipada** | Definir conceito de título/capa na pauta. Medir revisões de conceito após gate 2 e minutos de retrabalho por episódio. | D7/D28: CTR, impressões, origem do tráfego e retenção de 30 s como contexto; não atribuir sua variação apenas à ordem do trabalho. | Primeira candidata; planejar agora e decidir a execução à luz das primeiras leituras. |
| **H02 — Coerência da abertura** | Antecipar um exemplo fichado ligado à promessa nos primeiros 30 s. Principal: `retention_30s_percent`. | `avg_view_duration_s`, tráfego, duração e entendimento; comparar vídeos do mesmo recorte. | Ciclo posterior, mantendo o procedimento de embalagem e sem alterar simultaneamente os recursos visuais. |
| **H03 — Uma diferença na capa** | Comparar duas capas do mesmo vídeo, com título fixo, no A/B nativo se disponível e autorizado. Principal: resultado do teste por tempo de exibição. | Registrar resultado e intervalo em `readings.*.notes`; CTR geral não revela o CTR de cada variante. | Quando houver impressões e acesso ao recurso; inconclusivo é resultado válido. |
| **H04 — Metáfora visual simples** | Trocar uma explicação abstrata por uma metáfora ilustrativa que preserve os fatos. Principal: pergunta de compreensão antes da publicação. | Tempo de produção; curva de retenção apenas se fornecida e localizada na cena. | Depois da base editorial; usar componentes existentes antes de desenvolver atuação 2D nova. |

H01 mede eficiência. H02/H03 observam comportamento de audiência. H04 começa com compreensão.
Não usar CTR como prova de economia de trabalho, nem usar mais animação como sinônimo de maior retenção.
Pares de episódios diferem em tema, tráfego e público; a comparação pequena é indicativa.

### Registro no contrato existente

`hypothesis` aceita uma string, sem campos tipados para variável, métrica ou referência. Esses elementos podem
estar na própria string e no registro de pauta. Exemplo de **fragmento**, não de `PublicationMetrics` completo:

```json
{
  "hypothesis": "H01: definir título e conceito de capa na pauta reduzirá revisões de conceito após gate 2 e minutos de retrabalho, em comparação com o lote anterior do mesmo recorte. Registrar esforço na pauta e nas notas; acompanhar CTR, tráfego e retenção de 30 s em D7/D28. Referência: docs/pesquisa/crescimento-youtube-embalagem-hipoteses-2026-10-23.md, A01/A03."
}
```

Para uma publicação nova com episódio, canal, formato e data reais conhecidos, o caminho já existente é
`scripts/provisorio/metricas.py iniciar <id> --platform youtube --format longo`, completando os metadados e
`--hypothesis` com o texto escolhido. `iniciar` recusa arquivo existente. Não usar `ler` para editar hipótese.
Uma eventual correção de registro existente exige preservar as leituras e validar o objeto completo.

**Limite concreto do contrato:** não há campo numérico de tempo de produção, revisões, resultado A/B, CTR por
origem ou curva de retenção. Não confundir `duration_s` (duração do vídeo) com horas de trabalho. Registrar
esforço na pauta e resumir em `readings.d7.notes`/`readings.d28.notes`; uma leitura também precisa conter dado
numérico real ou origem de tráfego. Não preencher zeros para conseguir gravar uma nota.

Antes da publicação, conservar a hipótese na pauta e neste documento; `metrics.json` exige `published_at` com
fuso. Se o script preencher uma data pelo agendamento, conferir depois se corresponde à publicação efetiva.
Sem histórico de esforço, H01 começa estabelecendo a base; não será possível afirmar redução já no primeiro caso.

## 6. Calendário das leituras existentes

Snapshot dos registros locais de YouTube longo, validado pelo modelo `PublicationMetrics`. As datas abaixo
são as gravadas nos arquivos, não uma conferência de publicação no YouTube. Todas as hipóteses estão `null` e
todas as leituras estão vazias em 23/10. Ajustar vencimentos se a data efetiva for corrigida.

| Episódio | Data registrada | D7 | D28 |
|---|---|---|---|
| `death-note-fins-meios` | 20/10/2026 | 27/10/2026 | 17/11/2026 |
| `kira-voto-brasil` | 21/10/2026 | 28/10/2026 | 18/11/2026 |
| `historia-vencedores` | 22/10/2026 | 29/10/2026 | 19/11/2026 |
| `epicteto-na-sua-mao` | 23/10/2026 | 30/10/2026 | 20/11/2026 |

As primeiras leituras caem na semana de 26/10 a 01/11. Isso permite planejar a próxima hipótese antes de produzir,
sem declarar vencedora uma técnica por um vídeo. O lote de quatro do §12 não é uma meta de quatro vídeos na
próxima semana. Reels de confeitaria e clipes musicais ficam fora desta comparação.

## 7. Encaminhamento e limites

- Planejar H01; registrar o próximo episódio e a hipótese antes de começar o teste. Fazer as leituras reais na
  janela correspondente, sem preencher retrospectivamente os vídeos anteriores como se fossem ensaios planejados.
- Usar os resultados para detalhar as issues existentes: [#124, promessa e embalagem](https://github.com/ViniciusKoiti/video-pipeline/issues/124),
  [#118, adaptação de métodos](https://github.com/ViniciusKoiti/video-pipeline/issues/118),
  [#121, revisão de compreensão](https://github.com/ViniciusKoiti/video-pipeline/issues/121) e
  [#31, resultados e próximo experimento](https://github.com/ViniciusKoiti/video-pipeline/issues/31).
- Conferir no Studio a elegibilidade do A/B antes de planejá-lo. A documentação atual permite títulos e capas,
  exige recursos avançados e não disponibiliza esse teste para Shorts. Não foi acessada a conta para confirmar acesso.
- O estudo da vidIQ informa uma associação em uma seleção de sucessos; não prova que um rosto, personagem,
  ferramenta paga ou estilo de texto causa crescimento. A afirmação comercial de prever potencial de clique não
  foi validada. Não contratar ferramenta com base nesta rodada.
- Revisar fontes oficiais quando houver mudança de plataforma. A fonte de 2023 situa uma prática; não define a
  interface de 2026. Nenhum limiar universal de CTR, retenção ou frequência foi estabelecido aqui.

**Entrega da pesquisa inicial:** pesquisa e proposta de teste, sem etapa, skill, dependência ou integração nova.
Nenhum roteiro, gate, publicação ou `metrics.json` existente foi editado. Naquela rodada faltava identificar um
episódio para preparar o teste. Não há ganho de audiência demonstrado.

**Verificações:** `tests/test_metrics.py`: 13 testes passaram; datas da tabela calculadas pelo contrato atual.
Links locais e o fragmento de hipótese também foram conferidos. Isso verifica o uso do contrato, não a eficácia
das recomendações externas.

## Adendo — aplicação autorizada em 23/10/2026

Após o pedido do dono para aplicar a proposta, as orientações compartilhadas em `AGENT.MD` e `CLAUDE.md` passaram
a explicitar o planejamento de título/conceito na pauta e a passagem da hipótese ao registro de métricas. A skill
existente `miniatura` passou a consultar esse plano antes de compor. Não foi criada uma skill nem uma etapa nova.

A pauta [eren-liberdade-destino](../../data/episodes/eren-liberdade-destino/pauta.md) foi preparada como **candidata**:
era um rascunho só com perguntas, sem fontes, roteiro, manifesto de render ou registro de métricas. Recebeu duas
opções de título/conceito, H01, definição das medidas e espaço para registrar esforço. A candidata não fixa a
ordem de produção; a escolha editorial continua pendente. Os demais episódios foram preservados.

O `metrics.json` dessa candidata continua ausente porque não há data real de publicação. O texto para seu campo
`hypothesis` já está na pauta. Com os metadados conhecidos, o script existente pode criar o registro sem mudar
o contrato. Não foram inventados calendário, leituras, decisões humanas ou benefícios medidos.

---

## Rodada 2 — ampliação de 23/10/2026, 22h

**Pedido do dono:** analisar os canais que ensinam a crescer no YouTube e dizer o que serve ao fluxo. **O que esta
rodada acrescenta** às seções 1–7: o vídeo que o dono indicou (seção 8), uma segunda leva de criadores e analistas em
inglês (seção 9), os criadores brasileiros e o YouTube oficial em pt-BR (seção 10), o oficial em inglês além das três
páginas já lidas (seção 11), as contradições entre as fontes (seção 12), o cruzamento com os dois moldes medidos do
nicho (seção 13) e hipóteses novas, uma variável por vez (seção 14).

**Método e limites.** Três agentes de pesquisa leram as páginas em texto e devolveram tabelas com URL, citação e base
declarada; eu abri por amostragem as páginas mais citadas (lista no fim da rodada) e corrigi o que não batia. O vídeo
indicado pelo dono foi lido pela legenda automática em inglês, baixada com `yt-dlp` numa pasta descartável; os minutos
são aproximados (blocos de 30 s) e os capítulos vêm da descrição oficial. Nenhum painel privado, nenhum vídeo baixado,
nenhuma medição de cortes nesta rodada. Os prefixos dos IDs separam as origens: `AA` (vídeo indicado), `EN` (criadores em
inglês), `BR` (pt-BR), `OF` (oficial, rodada 2). Os tipos são os da seção 3: **oficial**, **ofício**, **folclore**. Como
na seção 3, forma nunca vira fato: nada daqui entra na narração; só muda onde e como o trabalho é feito e o que se mede.

## 8. O vídeo indicado pelo dono: Aprilynne Alter, "how to make an EVEN MORE killer youtube intro"

| Campo | Valor |
|---|---|
| Canal | Aprilynne Alter (`@AprilynneAlter`), ~180 mil inscritos |
| Vídeo | https://www.youtube.com/watch?v=eRWyf-oDdCI, publicado em 04/08/2025, 25:02, ~455 mil views em 23/10/2026 |
| Capítulos (descrição) | 00:00 Intro · 00:33 Step 1: The Plot Promise · 02:56 Step 2: The First 5 Seconds · 05:56 Step 3: The Rest of Your Intro · 21:09 Step 4: The Viewer Experience |
| O que vende | "90 Day Breakthrough" (acelerador de 12 semanas, lista de espera para 2027); afiliado da 1of10 (ferramenta de outliers); guia gratuito no Gumroad; equipamentos por afiliado Amazon. O vídeo tem patrocínio da Spotter Studio (11:45–13:17), ferramenta que a própria descrição diz ter fechado ao público. |
| Base declarada | Experiência própria ("over 4 years") e exemplos de vídeos de terceiros (Mark Rober, MKBHD, Ali Abdaal, Ryan Trahan). Nenhuma amostra, nenhum painel. |

| ID | Afirmação delimitada | Tipo | Minuto | Medida ou verificação | Entrada na pipeline |
|---|---|---|---|---|---|
| AA01 | A abertura é "onde a maioria dos criadores perde até 50% dos espectadores". | Folclore (número sem fonte) | ~00:00 | A curva de retenção dos nossos vídeos, no Studio, aos 30 e 60 s. Não assumir o número. | Leitura D7. |
| AA02 | Título e miniatura fazem uma **promessa de enredo**; definir primeiro a versão mais clicável dos dois e só então escrever a abertura para cumpri-la. | Ofício | 00:33–02:56 | Mesma coisa que A01/A03 (seção 3). | Pauta (H01, já planejada). |
| AA03 | Os primeiros 5 segundos têm um trabalho só: **dizer o assunto do título e mostrar o assunto da miniatura**. | Ofício | 02:56–04:38 | `retention_30s_percent` ("Intro" do Studio, A06). No roteiro: segundos até a primeira menção do assunto do título (medida nova para o molde, seção 13). | Partitura e primeira cena. |
| AA04 | Mostrar vale mais que dizer, porque a prévia que toca ao passar o mouse é muda. "Cada vez mais gente" decide por ela. | Ofício; a frequência é folclore | 04:38–05:40 | A prévia em linha existe; quantos a usam, ninguém mediu aqui. Conferir o nosso primeiro quadro e os primeiros 5 s sem som. | Primeiro plano do vídeo (no Reel, ADR 028, o primeiro quadro já é a capa; no longo, não há regra). |
| AA05 | O resto da abertura tem três ingredientes, em qualquer ordem: contexto mínimo, ao menos uma lacuna de curiosidade e a "proposta única" (USP). Métrica própria: **tempo até o primeiro valor**. | Ofício | 05:56–07:44 | Curva de retenção no primeiro minuto; no roteiro, segundos até a primeira ideia útil. | Partitura. |
| AA06 | "As aberturas mais eficazes têm 45 segundos ou menos"; o segmento todo tem "20 a 45 segundos". | Folclore (número sem fonte) | ~07:44 e ~22:57 | **Conflita com o nicho medido:** abertura de 93 s no topo reproduzível e 167 s no Filosofatos (seção 13). Vale o molde. | Nenhuma, até dado nosso. |
| AA07 | Lacuna de curiosidade se abre por **contradição**, por **dizer a pergunta em voz alta**, por **interrupção** de uma resposta e por **promessa de mais itens**. | Ofício | 08:14–11:15 | No roteiro: segundos até a primeira pergunta (o nicho faz aos 26–29 s) e número de ganchos pagos depois. | Partitura e `vp check` (gancho pago já é traço do molde). |
| AA08 | Se não há lacuna de curiosidade para abrir, "a ideia do vídeo talvez não seja interessante"; lacunas nascem de conflito, tensão e transformação. | Ofício (critério editorial) | ~11:15 | Sem métrica; é uma pergunta à pauta. | Pauta: a pergunta neutra às fontes já cumpre esse papel. |
| AA09 | Quatro formas de USP: **expertise**, **esforço** (viés de insumo: "quantos livros li"), **personalidade** e **prova** (mostrar o resultado cedo; "Jenga storytelling"). | Ofício | 13:17–20:54 | Não mede sozinha. No nicho, a "personalidade" aparece como confissão do narrador (85% no Filosofatos, 0% no topo; seção 13). | Partitura; a nota dos livros lidos já existe (`livros.json`) e pode ser dita na abertura. |
| AA10 | **Antecipar a qualidade:** a abertura é a amostra pela qual o espectador julga o resto; o que de melhor o vídeo tem no visual deve aparecer nela. Anotar o roteiro linha a linha com o que se vê (T-sheet). | Ofício | 21:09–22:57 | Curva de retenção nos primeiros 60 s. | Já é como a pipeline escreve: os planos ancorados na narração (ADR 008) são um T-sheet. Falta só a regra editorial de pôr o melhor plano na abertura. |

**Leitura.** O vídeo é bem construído e vende pouco dentro do próprio conteúdo, mas não traz um número verificável: as
duas quantidades que ele afirma (50% de perda na abertura, abertura de até 45 s) não têm fonte, e a segunda contraria o
que medimos no nicho. O que sobra de útil é método (AA02, AA03, AA07, AA10), e três dessas quatro coisas a pipeline já
faz ou já mede. A novidade aproveitável é AA03: dizer o assunto do título nos primeiros segundos, que hoje não é medido
nem na partitura nem no `vp check`.

## 9. Criadores e analistas em inglês, segunda leva

Fora o que a seção 2 já cobriu (as duas entrevistas do Creator Science e o estudo de miniaturas da vidIQ). Marcação
**(conferido)** = página aberta por mim nesta rodada; o resto foi lido pelo agente de pesquisa e está com a URL.

| ID | Afirmação delimitada | Tipo | Quem, e o que vende | Fonte | Base declarada | Medida |
|---|---|---|---|---|---|---|
| EN01 | A quem pergunta como "agradar o algoritmo", trocar a palavra por **público**. | Oficial (fala de funcionário, não documento) | Todd Beaupré, diretor de descoberta do YouTube; nada vende | [TechCrunch, 24/06/2022](https://techcrunch.com/2022/06/24/mrbeast-explain-algorithm-youtube-vidcon/), VidCon **(conferido)** | Posição do YouTube | Origem do tráfego e espectadores recorrentes. |
| EN02 | Duração: "as long as it needs to be" (Beaupré); "nunca vi nada que diga que vídeos precisam ser mais longos" (MrBeast). | Oficial / ofício | idem; MrBeast com dados do próprio canal | idem **(conferido)** | Posição do YouTube; experiência | Duração média e porcentagem assistida por duração. |
| EN03 | Trocar a miniatura de um vídeo já publicado "costuma ajudar bastante, dá um leve salto". | Ofício | MrBeast | idem **(conferido)** | Dados do canal, sem número | CTR e views por dia antes e depois da troca. |
| EN04 | Só três métricas importam: CTR, duração média (AVD) e porcentagem assistida (AVP). O título e a miniatura "fixam a expectativa"; "quanto mais extremo, melhor". | Ofício (canal de um só) | Memorando interno da produção do MrBeast, vazado em 2024; autenticidade não confirmada por nenhuma das fontes | [Reprodução do memorando](https://www.alexanderjarvis.com/memo-how-to-succeed-in-mrbeast-production/) **(conferido)**; [Creator Handbook, 18/09/2024](https://www.creatorhandbook.net/leaked-document-allegedly-reveals-mrbeasts-secrets-to-youtube-success-the-key-takeaways/) | Dados do canal ("5 anos estudando viralidade") | CTR, AVD, AVP. O "mais extremo" conflita com OF05: clickbait tende a AVD baixa e menos recomendação. |
| EN05 | Num vídeo, 21 milhões de 60 milhões saíram no primeiro minuto; daí o cuidado com a abertura. "Re-engajamento aos 3 minutos": algo novo para quem enjoaria. Vídeo médio do canal: 818 s (13:37). | Ofício; o "3 minutos" é sem gráfico | Memorando MrBeast | idem **(conferido)** | Gráfico de retenção de um vídeo; média dos últimos 100 | Retenção aos 60 s e entre 2 e 6 min. A média de duração é dado do canal dele, não regra. |
| EN06 | "A diferença entre 1 milhão e 28 milhões de views é a embalagem"; o jogo é "ganhar o clique". Grandes gastam ~30% do tempo em ideia e embalagem; pequenos ~5%. | Ofício; os percentuais são folclore (número do resumidor) | Paddy Galloway, consultor (MrBeast, Sidemen); vende consultoria e um "accelerator". Página de Colin and Samir, que vendem programa e patrocínio | [Colin and Samir, "The New Rules of YouTube From Paddy Galloway"](https://www.colinandsamir.com/resources/the-new-rules-of-youtube-from-paddy-galloway), 2024 | Casos de clientes (n=2 citados) | CTR e impressões por vídeo. Horas em embalagem: só registro próprio. |
| EN07 | Miniatura tem de passar no "teste da olhada" (milissegundos); título e miniatura são uma peça só; um vídeo por semana sem falhar; miniatura clara porque "60–70% usam modo escuro". | Ofício; a frequência e o modo escuro são folclore | Paddy Galloway, via posts no X e via newsletter Marketing Examined | Posts no X **não verificados** (HTTP 402); [Marketing Examined, 14/11/2023](https://www.marketingexamined.com/blog/paddy-galloway-youtube-guide) é síntese de terceiro | Nenhuma | CTR em A/B nativo. |
| EN08 | "Se você faz o vídeo primeiro, provavelmente vai falhar"; "retenção está na escrita", não na edição; a primeira frase também é gancho. | Ofício | Ed Lawrence (Film Booth); vende curso, coorte por aplicação e ingressos | [Creators on Air, 02/07/2024](https://www.passionfroot.me/creators-on-air/mastering-youtube-strategies-with-ed-lawrence), 07:00, 14:00, 17:22 | Experiência | Duração média e curva de retenção. |
| EN09 | Revisar vídeos com duração média **alta** e CTR **baixo**, trocando título e miniatura. | Ofício (regra de diagnóstico) | Ed Lawrence, via 1of10 e StarterStory (ambos vendem algo) | [1of10, 23/01/2025](https://1of10.com/blog/film-booths-strategy-gaining-millions-views/); [StarterStory, 22/12/2024](https://www.starterstory.com/film-booth-breakdown) | Experiência | CTR antes e depois com AVD estável. É a regra mais útil desta leva para ler o D7 (seção 14). |
| EN10 | CTR cai quando o vídeo chega a público frio: é sinal de alcance, não de falha. Faixas por tamanho de canal e por origem. "As primeiras 24–48 h decidem", **embora o YouTube não confirme** (a própria página diz). | Ofício (observação); o "24–48 h" é folclore | vidIQ; vende extensão e planos | [vidIQ, "What Is a Good YouTube CTR?", atual. 27/05/2026](https://vidiq.com/blog/post/6-tips-good-CTR-youtube) | Faixa de 2–10% vem do YouTube (OF05); o resto, "observações" sem amostra | CTR × impressões ao longo do tempo. |
| EN11 | "O YouTube afirma que o horário de publicação não afeta o desempenho de longo prazo." | Atribuído ao YouTube por terceiro | vidIQ (suporte da ferramenta "Best Time to Post") | [vidIQ, 14/01/2026](https://support.vidiq.com/en/articles/108673-the-best-time-to-post-youtube-videos-for-maximum-viewership) | Nenhuma página oficial com essa frase foi encontrada (OF09) | Ver OF09. |
| EN12 | Renomear "Strange Applications of the Magnus Effect" para "Backspin Basketball Flies Off Dam" levou a 16,3 milhões de views em uma semana, quase tudo de fora do YouTube. Dois tipos de clickbait: o que entrega ("legitbait") e o que engana. | Ofício com dados do canal (sem CTR) | Veritasium (Derek Muller); nada vende sobre o tema | Vídeo ["Clickbait is Unreasonably Effective"](https://www.youtube.com/watch?v=S2xHZPH5Sng), **17/08/2021**, 19:25 (metadados conferidos por `yt-dlp`; o agente citara uma reupload de 83 s, corrigido aqui); texto via [Gigazine, 30/08/2021](https://gigazine.net/gsc_news/en/20210830-clickbait-effective) | Views e origem de tráfego do canal | Origem externa × YouTube; CTR após renomear. |
| EN13 | Estudo de **323 mil vídeos** (50 mil canais, 62,6 bi de views) por mediana de views: título de ~30 caracteres +60%; "desaba" após 60–70; números no título −11%; texto na miniatura −19%; rosto ≈ 0 no geral; enquadramento negativo +20%; **15–25 min** é a melhor faixa de duração, 30–60 a pior. | Ofício (correlação; marketing de ferramenta) | 1of10; vende extensão de outliers (é a ferramenta que Aprilynne indica por afiliado) | [Quasa, 23/03/2026, atual. 14/08/2026](https://quasa.io/media/youtube-s-biggest-thumbnail-title-study-ever-323-000-videos-62-6-billion-views-and-the-brutal-truth-about-what-actually-gets-clicks) **(conferido)**; relatório original em 1of10.com **não localizado**; período não informado | Correlação com mediana de views; sem controle de nicho na página | Views ÷ mediana do canal × comprimento do título. |
| EN14 | **18.080 canais** em inglês, 11 nichos: título de 30–50 caracteres é o "ponto doce"; acima de 90 rende menos; **interrogação ajuda em Educação e Ciência**; CAIXA ALTA prejudica em Educação. A página diz "this is correlational data". | Ofício (correlação; marketing de auditoria) | AIR Media-Tech; vende auditoria de canal | [AIR, atual. 12/06/2026](https://air.io/en/audience-growth/how-to-write-a-youtube-title-that-gets-clicked-research-across-11-niches) | Engajamento mediano = (likes + comentários) ÷ views; p75 de views | Engajamento e views × forma do título. Interessa porque os nossos quatro títulos são perguntas. |
| EN15 | Melhor horário para vídeo longo: domingo 10h (Buffer, 1,8 M de vídeos) × quarta a sexta 14–16h (SocialPilot, ~301 mil) × 10–16h (Metricool, ~800 mil). | Ofício (correlação); **marketing de agendadores**, métricas não definidas, só clientes das ferramentas | Buffer, SocialPilot, Metricool | [Buffer, 24/07/2026](https://buffer.com/resources/best-time-to-post-on-youtube/); [SocialPilot](https://www.socialpilot.co/insights/best-time-to-post-on-youtube); [Metricool, 29/07/2026](https://metricool.com/best-time-to-post-on-youtube/) | Amostras grandes, método não exposto | Views em 48 h por horário. **Não testar** (seção 14). |
| EN16 | Títulos com menos de 54 caracteres recebem ~30% mais views (261 mil títulos); rostos expressivos elevam CTR em 20–30%. | Não verificado na origem; o segundo é folclore | Zelios (agência), citando Charles Weill e vidIQ | [Zelios, atual. 21/08/2026](https://zelios.agency/titles-and-thumbnails-statistics/) | Agregador; originais não abertos | — |

**Não encontrado nesta leva:** estudo de Paddy Galloway com amostra declarada em texto; episódio de Colin and Samir com
funcionário do YouTube (a fala do Beaupré é da VidCon 2022); a "regra dos 3 segundos" do Film Booth; números de CTR
do Veritasium; o PDF original do memorando do MrBeast (404); estudo de TubeBuddy, Social Blade ou Hootsuite com método.

## 10. Criadores brasileiros e o YouTube oficial em pt-BR

Os vídeos foram lidos por espelhos de transcrição (resumo automático com minutagem) e, onde só havia a descrição, a
citação é da descrição e está marcada. Canal e handle de cada vídeo foram confirmados pelo oEmbed oficial do YouTube.
Inscritos: números declarados pelo próprio criador ou "não verificado" (o Social Blade recusou o robô).

| ID | Afirmação delimitada | Tipo | Quem, e o que vende | Fonte | Base declarada | Medida |
|---|---|---|---|---|---|---|
| BR01 | A recomendação se baseia no que o público assiste ou deixa de assistir, tempo de exibição, curtidas e descurtidas, "não tenho interesse" e pesquisas de satisfação. Título, descrição e miniatura "devem refletir exatamente o conteúdo". Em Shorts, "os primeiros 2 segundos" decidem. | Oficial | YouTube Creators (site oficial em pt-BR) | ["Perguntas mais frequentes de YouTubers"](https://www.youtube.com/intl/pt-BR_ALL/creators/top-questions/), sem data | Documentação | Origem "Sugeridos/Início" × duração média; CTR alto com Intro baixa = desalinhamento. |
| BR02 | Made on YouTube 2026: o Studio vai gerar miniaturas no estilo do canal; **teste A/B com até três cortes**; Shorts organizados em temporadas e episódios. | Oficial (anúncio) | YouTube (blog oficial pt-BR, Neal Mohan) | [Blog pt-BR, 23/09/2026](https://blog.youtube/intl/pt-br/news-and-events/inovacao-youtube-era-made-on-publico-criadores/) | Anúncio | Resultado do A/B no Studio. |
| BR03 | A marcação de produtos da Amazon (Shopping) chega ao Brasil; tags de Shopping geram "mais que o dobro de cliques" em relação ao link na descrição. | Oficial (dado agregado sem método) | YouTube (blog oficial pt-BR) | [Blog pt-BR, 23/09/2026](https://blog.youtube/intl/pt-br/news-and-events/made-on-youtube-monetizacao-de-criadores-shopping/) | Agregado do YouTube | Cliques em produtos no Studio. Interessa ao link de afiliado dos livros (`livros.json`): hoje ele vai só na descrição. |
| BR04 | "Pergunte ao Studio" (IA do Studio) em português para criadores brasileiros. Mais de 45 mil canais brasileiros com mais de 100 mil inscritos (Oxford Economics, encomendado). | Oficial (anúncio) | YouTube Brasil | [Blog pt-BR, 11/06/2026](https://blog.youtube/intl/pt-br/news-and-events/google-for-brasil-pergunte-ao-studio-chega-para-criadores-em-portugues-e-dados-da-oxford-economics-reforcam-o-impacto-do-youtube-na-creator-economy-no-pais/) | Estudo encomendado, método não exposto | — |
| BR05 | Tendência BR 2025: os canais que mais cresceram "gamificam" a vida e criam universos compartilhados entre canais. | Oficial (tendência, não mecânica) | YouTube Culture & Trends, edição pt-BR | [Relatório 2025 (PDF)](https://services.google.com/fh/files/blogs/yt-cats-report-edicao-final-de-ano-2025.pdf) | Análise da equipe de tendências | — |
| BR06 | Canal pequeno tem poucos dados, "o algoritmo não vai recomendar"; capa e título devem gerar curiosidade e o roteiro entregar o prometido; constância e paciência. Em 2026: "não temos mais motivos para publicar Shorts", "a pior mudança da história do YouTube". | Ofício sem dado; a parte dos Shorts é opinião | Marcos Lemos (`@MarcosLemosExpert`, 336 mil declarados); vende auditoria (R$ 97 e R$ 297), comunidade e e-book | [Vídeo sobre canal pequeno](https://www.youtube.com/watch?v=zBIalP4j2hw); [vídeo sobre Shorts](https://www.youtube.com/watch?v=16cJn1LcZco) (só descrição); [página de venda](https://formulayoutuber.expert/) | Nenhuma declarada | Impressões e % de "Sugeridos" nas primeiras 48 h, por tamanho de canal. |
| BR07 | Escolher nicho onde a demanda supera a oferta (Google Trends com filtro YouTube); estudar outliers e 3 a 5 canais de referência antes de produzir; conteúdo repetitivo tira a elegibilidade de monetização; RPM varia muito por nicho. | Ofício (experiência) / oficial (política citada) | Nerds de Negócios (Peter Jordan; `@nerdsdenegocios`; inscritos não verificados); vende curso de "canal dark" e outros | ["Como criar um canal dark do zero em 2026"](https://www.youtube.com/watch?v=kIIfOJ5uM_o), 01:52–15:13 | Experiência (diz operar canais com equipe) | Views ÷ mediana do canal; RPM por nicho. O método de referência é o que a skill `analise-de-formato` já faz. |
| BR08 | Canal "dark" com IA pode render "até R$ 5.200 por mês sem aparecer". | Folclore (promessa de venda) | Hotmart com Peter Jordan | [Hotmart Tips](https://www.youtube.com/watch?v=YerSlC5aGGE) (descrição) | Nenhuma | Extrato do AdSense de 12 meses numa amostra. |
| BR09 | No Brasil o AdSense não sustenta o criador, salvo com milhões de views por mês. Afiliado: ~1% clicam e ~13% dos que clicam compram; vídeos antigos seguem trazendo público. | Ofício (números próprios ditos, não mostrados) | Joba (`@Joba`; não verificado); vende curso "Mapa do YouTube", consultoria, afiliados | [Vídeo, resumo externo de 02/12/2025](https://www.youtube.com/watch?v=Qk--k_hrQPc), 10:53–13:54 | Experiência; vendas "não exibidas por privacidade" | Cliques por UTM e conversões por mil views. |
| BR10 | Shorts valem para crescer em 2025 ("abro meus números"); RPM dos Shorts é baixo; há uma duração ideal "testada na prática". | Não verificado: os números prometidos não aparecem nas páginas | Pat Machadu (`@patmachadu`; não verificado); vende e-book e afiliados | [Shorts 2025](https://www.youtube.com/watch?v=9Awl9PtFxuk); [RPM](https://www.youtube.com/watch?v=NI2TCZ2xzuI); [duração](https://www.youtube.com/watch?v=Y4PMcZyV-VI) (só descrições) | Promete painel; não visto | Inscritos originados de Shorts; RPM por formato. |
| BR11 | "Mapa de calor exclusivo" de horários que funciona "mesmo sem dados no Studio"; "a chave para 10x mais views". | Folclore | Gabriel Zago (`@gabrielbzago`; não verificado); vende ferramenta de SEO e afiliados | [Vídeo](https://www.youtube.com/watch?v=31qUXyv63i4) (só descrição) | "dados atualizados", sem fonte | Compare com OF09. |
| BR12 | Teve oito canais "dark" simultâneos, "os oito banidos por conteúdo repetitivo"; "hoje é impossível produzir um vídeo por dia de um canal dark"; marcas não patrocinam quem não aparece; vive disso no Brasil quem "conta nos dedos". | Experiência; a política é oficial (OF14) | Lucas, Youtube Sem MIMIMI (`@Youtubesemmimimi`; não verificado); clube de membros | ["Minha experiência com 11 canais dark"](https://www.youtube.com/watch?v=sSHls4JcsFM), 15/10/2023, ~03:13, ~06:43, ~16:25 | Relato próprio | Avisos de conteúdo repetitivo no Studio. **É o relato mais próximo do risco do §12** para uma cadência de um longo por dia com imagens paradas. |
| BR13 | "Aproximadamente 80% do sucesso de um canal dark vem de título e thumbnail"; primeiros US$ 100 em 2 a 4 semanas; método "100% legal, sem strikes". | Folclore (declara conflito de interesse) | Agência Roque; vende curso (R$ 297) e apps | [Blog, 06/07/2026, atual. 17/09/2026](https://www.agenciaroque.com.br/blog/curso-de-canal-dark-qual-vale-a-pena-em-2026-analise) | "Testes internos", sem método | — |
| BR14 | "Grande atualização" favorece canais pequenos; Shorts "priorizados no feed"; frequência previsível "sinaliza compromisso". | Folclore (nada oficial corresponde) | Canal Engajado (blog; e-book; rodapé com link de apostas) | [Blog, sem data](https://canalengajado.com.br/o-youtube-agora-esta-no-modo-facil-qualquer-um-pode-estourar-em-2025/) | Nenhuma | — |

**O que não existe em pt-BR, até onde a busca alcançou:** criador que mostre o painel do Studio na página; alguém que
trate de "vídeos para ouvir" ou áudio em segundo plano como estratégia; dado sobre os primeiros 30 segundos; dado de
Shorts puxando o longo; horário ou frequência com número. O canal oficial `@YouTubeCriadores` existe (anúncio de
27/02/2023), mas a lista de vídeos de 2025–2026 não renderizou para o robô. Resultado prático: o material brasileiro
desta busca serve para saber **o que o mercado vende**, não para decidir forma; para forma, o molde medido continua
sendo a única base em pt-BR.

## 11. O que o YouTube diz oficialmente, além das três páginas da seção 3

Páginas do suporte não exibem data (só "©2026 Google"). **(conferido)** = aberto por mim nesta rodada; "via" = fala de
funcionário lida em cobertura de terceiro, com o vídeo original não transcrito.

| ID | Afirmação delimitada | Fonte | Métrica que toca | Leitura para o canal |
|---|---|---|---|---|
| OF01 | Os sinais de satisfação são cliques, tempo de exibição, respostas a pesquisas, compartilhamentos, likes e dislikes; "em 2011 aprendemos que clicar não significa assistir"; conta como tempo valioso o que o espectador avaliou com 4–5 estrelas, e o sistema prevê a resposta de quem não respondeu. | [Cristos Goodrow, blog oficial, 15/09/2021](https://blog.youtube/inside-youtube/on-youtubes-recommendation-system/) | CTR, duração média, tempo de exibição | Nenhuma métrica isolada é o alvo; a pesquisa de satisfação pesa e não aparece no Studio por vídeo. |
| OF02 | A Ajuda lista histórico de exibição e de pesquisa, inscrições, likes e dislikes, "não tenho interesse", "não recomendar o canal" e pesquisas de satisfação ("não só tempo de exibição"). Início depende sobretudo do histórico; "Próximo" depende do vídeo em curso. **Não cita frequência nem tamanho do canal.** | [Ajuda, "How YouTube recommendations work"](https://support.google.com/youtube/answer/16089387?hl=en) | Origens de tráfego | Desmente BR06 e BR14 sobre favorecer ou punir canal pequeno: a página não fala disso. |
| OF03 | Cada espectador recebe um ranking diferente; é normal o inscrito não querer todo upload ("CTR por volta de 10% ou menos" entre inscritos); nenhuma métrica isolada indica valor; "não é o YouTube que empurra vídeos longos, é o público na TV que os quer". | Todd Beaupré, [Creator Insider, 01/09/2026](https://www.youtube.com/watch?v=rHLjxrbXmmY) (39:31; capítulos 9:57 e 28:34), via [ppc.land, 02/09/2026](https://ppc.land/subscribers-skip-90-of-uploads-in-their-feed-youtube-director-says/) | CTR, inscritos, dispositivo | A declaração oficial mais recente sobre duração: o motivo é TV, não algoritmo. |
| OF04 | "O algoritmo segue o público, então agrade o público"; olhar a aba Público para ver quais vídeos crescem a audiência. | Rene Ritchie (Creator Liaison), Short de ago/2024, via [Tubefilter, 26/08/2024](https://www.tubefilter.com/2024/08/26/rene-ritchie-shorts-creator-faqs/); **primário não localizado** | Aba Público | Confirma EN01 em 2024. |
| OF05 | "Metade dos canais e vídeos tem CTR de impressões entre 2% e 10%"; muitas impressões (Início) baixam o CTR naturalmente; "vídeos clickbait tendem a ter duração média baixa e por isso são menos recomendados"; poucas impressões costumam dar CTR alto (público pequeno e fiel); **vídeos ou canais novos (menos de uma semana) e vídeos com menos de 100 views têm faixa ainda maior.** | [Ajuda, "Impressions and click-through rate FAQ"](https://support.google.com/youtube/answer/7628154?hl=en) **(conferido)** | CTR, duração média | A faixa serve de contexto para o D7, não de meta; nos nossos primeiros vídeos ela não diz quase nada. É a resposta oficial a EN04 ("mais extremo"). |
| OF06 | Impressão só conta com a miniatura visível por mais de 1 s e pelo menos 50% na tela; não conta em sites externos, cards, telas finais, notificações, YouTube Kids ou Music. | [Ajuda, "thumbnail impressions and watch time"](https://support.google.com/youtube/answer/9314486?hl=en) | Impressões, CTR | Tráfego externo (BR, grupos) aparece em views, não em impressões: o CTR sobe artificialmente. |
| OF07 | Duração média = minutos assistidos "entre quem ficou para assistir"; uma visualização conta "no instante em que o vídeo começa a tocar", em todos os formatos (mudança de 24/08/2026). | [Ajuda, "engagement"](https://support.google.com/youtube/answer/9313698?hl=en); [Ajuda, "content performance"](https://support.google.com/youtube/answer/12220281?hl=en) | Duração média, views | Views de 2026 não são comparáveis às faixas antigas dos gurus. |
| OF08 | Navegação = Início, inscrições, Assistir mais tarde, Explorar; Sugeridos = ao lado ou depois de outros vídeos e links em descrições; Pesquisa; Playlists; Shorts. | [Ajuda, "video reach"](https://support.google.com/youtube/answer/1714921?hl=en) | Origens de tráfego | Definições para `traffic_sources` no `metrics.json`. |
| OF09 | Horário: o relatório "quando seus espectadores estão no YouTube" é indicado para comunidade, Premiere e live; **outra página** diz que o relatório de formatos ajuda a "decidir o melhor dia e hora para publicar". As duas não se alinham. Em 2020 o Creator Insider disse: "não temos confiança para dizer que você deva ajustar o horário de upload a isso". | [Ajuda, aba Público](https://support.google.com/youtube/answer/9314416?hl=en); [Ajuda, dicas de formatos](https://support.google.com/youtube/answer/13616337?hl=en); Creator Insider abr/2020 via [SEJ, 17/04/2020](https://www.searchenginejournal.com/youtube-to-show-creators-what-time-of-day-their-audience-in-online/362624/) | Aba Público | **Refina F02:** nenhuma página oficial diz "horário não importa"; a posição oficial é "sem confiança para recomendar". O que EN11 atribui ao YouTube não foi achado em página oficial. |
| OF10 | Frequência: "um cronograma de lançamentos consistente **e sustentável**"; a página pergunta quantas vezes por semana ou mês e se é sustentável; **não dá número**. | [Ajuda, "Upload schedule tips"](https://support.google.com/youtube/answer/13616979?hl=en) | — | "Um por semana sem falhar" (EN07) e "um por dia" (BR12) são dos criadores, não do YouTube. |
| OF11 | Shorts e longo têm históricos de exibição separados; "quem assiste Shorts nem sempre é quem assiste longo"; canais com Shorts "pareciam crescer mais rápido" (2022). O "vídeo relacionado" de um Short leva a qualquer longo do canal; "se você não faz Shorts, é invisível para bolsões enormes de fãs em potencial" (2026, sem dado de conversão). | Creator Insider, 28/07/2022, via [SEJ](https://www.searchenginejournal.com/youtube-shorts-algorithm/543939/); [blog oficial, 14/07/2026](https://blog.youtube/creator-and-artist-stories/youtube-related-videos-traffic-guide/) | Origens de tráfego (Shorts), inscritos | Os Reels que o canal já faz podem apontar para o longo pelo "vídeo relacionado"; medir no `traffic_sources`. |
| OF12 | Capítulos (regras: 1º em 00:00, ao menos 3, mínimo 10 s), telas finais (últimos 5–20 s, vídeo ≥ 25 s, até 4 elementos, métrica própria de cliques), cards, comentário fixado e playlists: **nenhuma página afirma efeito** em views, retenção ou recomendação. | [Capítulos](https://support.google.com/youtube/answer/9884579?hl=en); [telas finais](https://support.google.com/youtube/answer/6388789?hl=en); [cards](https://support.google.com/youtube/answer/6140493?hl=en); [fixar comentário](https://support.google.com/youtube/answer/9482367?hl=en); [playlists](https://support.google.com/youtube/answer/57792?hl=en) | Taxa de cliques da tela final | O nicho usa capítulos (100% no Filosofatos, 56% no topo): é hábito do nicho, não regra do YouTube. |
| OF13 | Duração: **nenhuma orientação oficial.** O único limiar documentado é de monetização: anúncios no meio só em vídeos monetizados de 8 minutos ou mais. A retenção é comparada com "vídeos de duração parecida". | [Ajuda, mid-roll](https://support.google.com/youtube/answer/6175006?hl=en) | Receita; retenção comparada | Os ~12 min atuais passam do limiar; 15–25 min (EN13) é correlação de ferramenta, não regra. |
| OF14 | **Política do YPP, 15/07/2025:** "conteúdo repetitivo" vira "conteúdo inautêntico" (em pt-BR, **"conteúdo não original"**) e passa a dizer que inclui conteúdo "repetitivo ou produzido em massa"; sempre foi inelegível. Exemplos literais: "conteúdo repetitivo ou similar com baixo valor educativo, analítico, narrativo ou com pouca variação entre os vídeos"; "personagens na mesma situação várias vezes com o mesmo resultado (modelo de enredo altamente semelhante)"; "apresentações de slides com imagens, histórias com modelos ou texto com pouco ou nenhum valor narrativo, analítico ou educativo"; "IA com modelos genéricos que dão a impressão de produção em massa". Permitido: mesma abertura e fecho se o corpo varia; série com personagens recorrentes e enredo distinto. | [Ajuda, políticas de monetização](https://support.google.com/youtube/answer/1311392?hl=en) e [em pt-BR](https://support.google.com/youtube/answer/1311392?hl=pt-BR) **(conferido no HTML baixado)** | Status de monetização | **Correção ao §12 do CLAUDE.md:** as frases "histórias narradas com variações mínimas" e "slideshows com narração idêntica" não estão no texto oficial em nenhuma das duas línguas; os trechos acima são os literais, e o nome em pt-BR é "conteúdo não original". A substância do risco continua a mesma. |
| OF15 | Divulgação de conteúdo alterado ou sintético: obrigatória quando realista (pessoa real fazendo ou dizendo o que não fez; evento real alterado; cena realista que não aconteceu); dispensada para IA em roteiro, outline, miniatura, título ou legendas; rótulo na descrição expandida ou, em temas sensíveis, no player; omissão repetida pode gerar rótulo manual ou penalidade. | [Ajuda, "altered or synthetic content"](https://support.google.com/youtube/answer/14328491?hl=en); [blog, 18/03/2024](https://blog.youtube/news-and-events/disclosing-ai-generated-content/) | — | A voz clonada do dono dizendo o texto do dono não é "pessoa dizendo o que não disse"; o `publicacao.md` já deixa o rótulo como decisão do dono por vídeo. Cena sintética realista de fato histórico continua exigindo o rótulo (§2.4). |
| OF16 | TV ultrapassou o celular como principal dispositivo nos EUA por tempo de exibição (carta de 2025); "#1 em tempo de streaming nos EUA" por quase três anos (Nielsen, carta de 2026); o YouTube é o serviço mais usado para **ouvir** podcasts nos EUA; 700 milhões de horas de podcasts em TVs em out/2025; "se o vídeo é o novo jeito de ouvir". Reprodução em segundo plano é recurso Premium. **Não há declaração oficial sobre "vídeos para ouvir" como categoria.** A carta de 2026 reconhece a preocupação com "AI slop" e promete reforço contra "conteúdo repetitivo de baixa qualidade". | [Carta do CEO, 11/02/2025](https://blog.youtube/inside-youtube/our-big-bets-for-2025/); [carta do CEO, 21/01/2026](https://blog.youtube/inside-youtube/the-future-of-youtube-2026/); [podcasts na sala, 18/12/2025](https://blog.youtube/news-and-events/podcasts-living-room-in-2025/) | Dispositivo (TV) na aba Público | O "(pra ouvir enquanto faz outra coisa)" do Filosofatos encaixa no enquadramento de podcast do YouTube; medir a fatia de TV e de áudio em segundo plano no D28 é barato e diz se o nicho é mesmo "de ouvir". |

**Procurado e não encontrado como declaração oficial:** duração ideal; frequência numérica; "horário importa pouco"
(só o "sem confiança" de 2020); efeito de capítulos, telas finais, cards, comentário fixado ou playlists; pesos dos
sinais; públicos de Shorts e longo em 2025–2026 (a declaração é de 2022); limiar de inscritos para o teste A/B (só
"recursos avançados" e Studio no computador).

## 12. Onde as fontes se contradizem

| Tema | Lado A | Lado B | O que fazer aqui |
|---|---|---|---|
| Horário de publicação | Buffer (domingo 10h), SocialPilot (quarta a sexta 14–16h), Metricool (10–16h), Zago ("mapa de calor"), Canal Engajado | YouTube: duas páginas que não se alinham e "sem confiança" (OF09); vidIQ atribui ao YouTube uma negação que não existe em página (EN11) | Não testar horário; manter o horário que o dono já usa e anotar. |
| Comprimento do título | 1of10 ~30 caracteres (EN13); AIR 30–50 (EN14); Weill < 54 (EN16) | Direção igual, limiares diferentes; todos correlacionais; nenhum em pt-BR | Hipótese H06 (seção 14), com os nossos quatro títulos (29–70 caracteres) como base. |
| Pergunta e números no título | AIR: interrogação ajuda em Educação e Ciência; números ajudam em alguns nichos | 1of10: números −11% no geral | Os nossos títulos são perguntas; só mudar uma coisa por vez. |
| Rosto na miniatura | vidIQ: 69% dos 500 de destaque (A09); Zelios +20–30% sem amostra | 1of10: rosto "quase zero" no geral | Não se aplica: a miniatura do canal é personagem de anime (skill `miniatura`). |
| Texto na miniatura | vidIQ: 72% têm texto, mediana 5 palavras (A09); Filosofatos: uma palavra larga (análise de 20/10) | 1of10: texto −19% | Hipótese H07, no A/B nativo, quando houver impressões. |
| Tamanho da abertura | Aprilynne: até 45 s (AA06) | Molde: 93 s no topo, 167 s no Filosofatos (seção 13) | Vale o molde; é medido no nicho em pt-BR. |
| Duração do vídeo | 1of10: 15–25 min melhor, 30–60 pior | Beaupré e MrBeast: "o que precisar"; YouTube: nenhuma orientação (OF13); Filosofatos: 22,8 min; topo: 13,9 | Decisão do dono (já registrada como pendente no doc de 20/10). |
| CTR como alvo | Memorando MrBeast: "quanto mais extremo, melhor" (EN04) | YouTube: clickbait → duração média baixa → menos recomendado (OF05); Veritasium: "legitbait" × "clicktrap" (EN12) | Título promete só o que as fichas sustentam (já é regra do gate 4). |
| Shorts | Canal Engajado e Pat Machadu: priorizados, valem em 2025 | Marcos Lemos: "sem motivo para publicar Shorts" em 2026 | YouTube (OF11) segue investindo e liga Short a longo pelo "vídeo relacionado"; medir no `traffic_sources`. |
| Canal pequeno e algoritmo | Canal Engajado: "atenção especial aos menores" | Marcos Lemos: "poucos dados, não recomenda" | A Ajuda não fala de tamanho de canal (OF02). Ignorar os dois. |
| "Algoritmo" | Spotter: favorece engajamento rápido; vidIQ: 24–48 h decidem | Beaupré e Ritchie: "troque algoritmo por público" (EN01, OF04); Goodrow: satisfação, não clique (OF01) | Vale o oficial. |

## 13. O que os dois moldes medidos já respondem

Os dois moldes do nicho (ADR 031; `moldes-lado-a-lado.md` em `data/cache/`) medem em pt-BR o que os gurus afirmam
em inglês. A = Filosofatos (13 vídeos, canal de referência escolhido pelo dono); B = topo reproduzível do nicho (9
vídeos de 7 canais). "Nossos" = os quatro longos de 20–23/10, medidos pelo `episode.json` e pelo `post.json`.

| Conselho | Quem diz | A: Filosofatos | B: topo | Nossos quatro | Leitura |
|---|---|---|---|---|---|
| Abertura curta (≤ 45 s) | AA06 | 167 s (57–199) | 93 s (72–117) | não medido nesta rodada | O nicho abre longo. Vale o molde. |
| Pergunta cedo | AA07 | primeira pergunta aos 29 s | aos 26 s | não medido | Já é padrão do nicho e da partitura. |
| Falar com quem assiste | molde Filosofatos (ADR 031) | primeiro "você" aos 11 s; 7,9 por mil palavras | aos 15 s; 6,3 por mil | medido pelo `vp check` | Igual nos dois moldes. |
| Promessa explícita na abertura | AA02, AA05 | 38% dos vídeos | 11% | não medido | O nicho promete pouco de forma explícita; a promessa está no título e na pergunta. |
| Gancho pago (prometer e entregar depois) | AA07 | 54% | 33% | traço já no `vp check` | Indício, não padrão. |
| Narrador confessa (USP de personalidade) | AA09 | 85% (padrão) | 0% | decisão do dono (doc de 20/10) | É a maior diferença entre os dois moldes. |
| Capítulos | OF12 | 100% (padrão), 6 por vídeo | 56%, 6 por vídeo | sem capítulos na descrição | Hábito do nicho sem efeito afirmado pelo YouTube. Barato de adotar; medir cliques é impossível, então é só coerência com o nicho. |
| Duração | EN13, OF13 | 22,8 min (20,9–29,4) | 13,9 min (9,7–18,2) | 6,3 · 11,5 · 12,7 · 12,8 min | Três dos quatro estão no quartil de baixo do topo; o `kira-voto-brasil` está fora dos dois moldes. |
| Variedade visual na abertura | AA10 | 1,5 cortes/min (0,8–46) | 0,1 cortes/min | render do template, não medido | O topo quase não corta: "antecipar a qualidade" no nicho é imagem em movimento, não corte. |
| Fala com "segundo fulano" | doc de 20/10 | 0,8 por mil | 1,3 por mil | `kira-voto-brasil` tinha 15 por mil | Já tratado em 20/10. |
| Comprimento do título do vídeo | EN13, EN14, EN16 | 71 caracteres (62–81), 13 palavras; pergunta em 1 de 13 (o sufixo "(pra ouvir enquanto faz outra coisa)" entra na conta) | 60 caracteres (40–70), 10 palavras; pergunta em 8 de 40 | 29 · 57 · 70 · 70 caracteres; 6 · 12 · 13 · 15 palavras | Medido em 23/10 (`titulo_video_chars`, `titulo_video_palavras`, `titulo_video_pergunta`). **O nicho em pt-BR usa títulos longos**: os "~30 caracteres" da 1of10 ficam abaixo do q1 dos dois moldes. Três dos nossos quatro estão dentro dos quartis; o de 29 está fora, por baixo. |
| Assunto do título dito cedo | AA03 | dito em 13 de 13 (padrão), mas aos **77 s** (4–137); o terço mais visto diz aos 42 s, o menos visto aos 80 s | dito em 36 de 40 (padrão), aos **40 s** (9–82); o terço mais visto diz aos 42 s, o menos visto aos 13 s | não medido | Medido em 23/10 (`titulo_video_dito_s`, `titulo_video_dito`). O nicho diz o assunto do título, mas **não nos primeiros 5 s**: H05 é aposta nossa, não padrão do nicho; os terços dos dois moldes discordam entre si (n pequeno), então nem a direção está clara. |

**Duas medidas novas na skill `analise-de-formato`** (implementadas em 23/10/2026 a pedido do dono; emenda da ADR 031):
(1) `titulo_video_chars`, `titulo_video_palavras` e o traço `titulo_video_pergunta`, da coluna `titulo` da amostra;
(2) `titulo_video_dito_s` e o traço `titulo_video_dito`: o segundo em que a fala já disse metade das palavras de
conteúdo do título (4 letras ou mais, fora das palavras de função; "navio" vale por "navios"). A partitura mostra os
dois na seção "Título do vídeo" e na linha do tempo. Os números da tabela acima vieram de rodar o molde nas duas
amostras (saída em pasta descartável; os `molde.json` do cache e dos episódios não foram regravados). Na mesma
noite, a pedido do dono, o `scenes.json` ganhou o campo opcional `title` (o título provisório da pauta) e o
`vp check` passou a avisar quando o tamanho do título sai dos quartis do molde e quando a narração demora a dizer
o assunto do título além do q3 do nicho, ou nunca o diz.

## 14. Hipóteses adicionais e a leitura do D7

Compatíveis com H01–H04 (seção 5); uma variável por vez; nenhuma começa antes de o dono escolher o episódio.

| Hipótese | Variável e medida principal | Base | Quando |
|---|---|---|---|
| **H05 — Assunto do título nos primeiros 5 s** | A primeira frase da narração nomeia o assunto do título e o primeiro plano mostra o da miniatura. Principal: `retention_30s_percent` (a "Intro" do Studio, A06), comparado com os quatro de outubro. No roteiro: segundos até a primeira menção (`titulo_video_dito_s`, seção 13). | AA03 (ofício); A06 (oficial: a Intro mede exatamente isso). **Contra o nicho:** o Filosofatos diz o assunto aos 77 s e o topo aos 40 s; é aposta nossa, não padrão. | Depois de H01 estar em curso; não junto com H02, que também mexe na abertura. Só se o dono quiser testar contra o nicho. |
| **H06 — Título curto** | Título com até 50 caracteres, ainda em forma de pergunta, com o pensador ou a ideia (regra do canal). Principal: `ctr_percent` em D7 e D28 contra os três títulos de 57–70 caracteres. | EN13, EN14 e EN16 (correlação, três fontes na mesma direção, nenhuma em pt-BR). **Contra o nicho:** títulos de 60 a 71 caracteres (seção 13); 50 caracteres fica no q1 do topo e abaixo do q1 do Filosofatos. O `historia-vencedores` (29 caracteres, "E se o Light tivesse ganhado?") já é o ponto natural de comparação quando o D7 chegar em 29/10, com os confundidores anotados: tema, dia, 12h em vez de 18h ou 19h. | Primeira leitura: D7 dos quatro. Teste só se a diferença aparecer; a correlação em inglês e o nicho em pt-BR apontam para lados diferentes. |
| **H07 — Capa sem texto × uma palavra** (refina H03) | Duas capas do mesmo vídeo, título fixo: uma só com o personagem, outra com a palavra larga do padrão Filosofatos. Principal: resultado do A/B nativo (vencedor por **tempo de exibição**, até 3 variantes, até 2 semanas; "inconclusivo" é resultado). | A09 e vidIQ (72% com texto) × EN13 (texto −19%) × análise de miniaturas de 20/10. | Quando o Studio mostrar o recurso ativo e houver impressões; registrar variante, início, fim e resultado em `readings.*.notes`. |
| **Não testar agora** | Horário (OF09, EN15); frequência numérica (OF10); "re-engajamento aos 3 min" (EN05, sem gráfico); rosto humano (não se aplica); duração (decisão editorial do dono, não teste). | | |

**Leitura do D7 (27 a 30/10), com o que esta rodada acrescenta à tabela 9.2 do relatório de gaps:**

1. **Impressões e origem.** Separar Navegação, Sugeridos, Pesquisa e Externo (OF08). Views de link compartilhado não
   geram impressão (OF06) e inflam o CTR.
2. **CTR com contexto.** A faixa oficial é 2–10%, e canais novos variam mais (OF05): o número sozinho não decide nada.
3. **Diagnóstico pelo par CTR × duração média** (EN09, OF05): duração média alta e CTR baixo apontam para embalagem
   (H06, H07); CTR alto e Intro baixa apontam para promessa não cumprida nos primeiros segundos (H05); os dois baixos
   apontam para tema ou público, não para forma.
4. **Intro (30 s) e curva.** Anotar em que cena cai o primeiro vale (as cenas têm `start_ms` no `episode.json`).
5. **Dispositivo.** Fatia de TV (OF03, OF16): diz se o "vídeo para ouvir" do nicho é o que acontece aqui.
6. **Risco do §12 (OF14, BR12).** Um longo por dia, mesma estrutura e imagens paradas é o perfil que a política
   descreve. A defesa do CLAUDE.md (pesquisa própria, roteiro por episódio, variação de estrutura e imagem) vale se for
   registrada por vídeo: o `outline.md` já tem a seção "Formato"; basta ela dizer o que **variou** em relação ao anterior.

## Verificação desta rodada

Abertas por mim em 23/10/2026, entre 21h30 e 22h30, e batendo com o que o doc afirma: Ajuda do YouTube
[16391400](https://support.google.com/youtube/answer/16391400?hl=en) (A/B), [9314415](https://support.google.com/youtube/answer/9314415?hl=en)
(retenção e Intro), [7628154](https://support.google.com/youtube/answer/7628154?hl=en) (CTR); o
[estudo da vidIQ](https://vidiq.com/research/youtube-thumbnail-study/); [TechCrunch sobre a VidCon 2022](https://techcrunch.com/2022/06/24/mrbeast-explain-algorithm-youtube-vidcon/);
a [reprodução do memorando do MrBeast](https://www.alexanderjarvis.com/memo-how-to-succeed-in-mrbeast-production/);
o [artigo da Quasa sobre o estudo da 1of10](https://quasa.io/media/youtube-s-biggest-thumbnail-title-study-ever-323-000-videos-62-6-billion-views-and-the-brutal-truth-about-what-actually-gets-clicks);
o HTML das [políticas de monetização](https://support.google.com/youtube/answer/1311392?hl=en) em inglês e em pt-BR; os
metadados dos vídeos `eRWyf-oDdCI`, `S2xHZPH5Sng` e `k3ZqB07QLnU` por `yt-dlp`. O resto da rodada foi lido pelos agentes
de pesquisa e está com URL e data; o que eles não conseguiram abrir está marcado "não verificado". Nenhum arquivo de
episódio, skill, `metrics.json` ou `CLAUDE.md` foi alterado nesta rodada; a correção do §12 (OF14) foi aplicada ao CLAUDE.md às 22h50, a pedido do dono, só naquele parágrafo.
