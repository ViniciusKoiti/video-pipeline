# Plano de 30 atividades: audiência, motion e componentes

**Data:** 13/10/2026. **Estado:** proposta de execução. Este plano divide os três diagnósticos em
10 atividades por frente. Os relatórios preservam a análise original e detalham objetivo, escopo,
entrega, aceite e dependências de cada atividade.

| Frente | Documento com as 10 atividades | Responsabilidade |
|---|---|---|
| MC — Skills do GitHub, motion e cenas | [Relatório de motion e cenas](../RELATORIO-SKILLS-GITHUB-MOTION-CENAS.md) | Adaptar métodos, dirigir movimento e definir receitas de cenas |
| AE — Gaps de audiência e engajamento | [Relatório de audiência](../RELATORIO-GAPS-AUDIENCIA-ENGAJAMENTO.md) | Definir jornada editorial, concluir legendas, revisar gates e medir resultados |
| CP — Componentes e integração | [Mapa do workspace e componentes](../WORKSPACE-ATUAL-E-COMPONENTES.md) | Reutilizar ou criar peças e integrá-las aos contratos e ao render |

Os IDs identificam as entregas; a sequência recomendada aparece abaixo. Esforço S/M/L é relativo,
sem estimativa de dias. Prioridade técnica não representa ganho de audiência medido.

## As 10 atividades de skills, motion e cenas

| ID | Atividade | Resultado esperado |
|---|---|---|
| MC-01 | Matriz de disponibilidade e compatibilidade | Saber o que existe no pin, no pacote instalado e no checkout |
| MC-02 | Guia de adaptação das skills externas | Usar somente instruções compatíveis com tempo por frame, fontes e arquitetura |
| MC-03 | Vocabulário de movimento e transições | Escolher movimento pela função da cena, com foco e pausa de leitura |
| MC-04 | Receitas de headline e legenda | Distinguir entrada de texto de legenda sincronizada e definir sua convivência |
| MC-05 | Receitas de lista, processo e ilustração | Escolher entre enumeração, mecanismo e desenho explicativo |
| MC-06 | Receita de evidência documental | Mostrar trecho e atribuição sem alterar o sentido da evidência |
| MC-07 | Receitas de comparação, gráfico e detalhe | Manter escala, unidade, contexto e foco na informação narrada |
| MC-08 | Composição vertical, localização e cronologia | Recompor a cena para 9:16, com áreas seguras e rótulos legíveis |
| MC-09 | Cortes motivados e continuidade de áudio | Relacionar cortes à fala e especificar quando a montagem precisa mudar |
| MC-10 | Revisão visual e temporal por cena | Conferir entrada, movimento, leitura e saída com critérios reproduzíveis |

## As 10 atividades de audiência e engajamento

| ID | Atividade | Resultado esperado |
|---|---|---|
| AE-01 | Recorte de série e pauta | Dono define público, idioma, pergunta, formato e promessa do lote |
| AE-02 | Promessa, progressão e resposta final | Revisor reconhece a pergunta e encontra a resposta nas cenas |
| AE-03 | Gancho e embalagem coerentes | Abertura, título, capa/primeiro quadro e legenda prometem a mesma entrega |
| AE-04 | CTA, comentários e continuidade | Próxima ação útil e critério para avaliar respostas do público |
| AE-05 | SRT e tempos reais no fluxo de montagem | Legenda revisada vinculada ao manifesto; tempos por palavra só quando confiáveis |
| AE-06 | Preflight editorial e gates humanos | Pendências de conteúdo e direitos aparecem antes da produção final |
| AE-07 | Ritmo, leitura e convivência de camadas | Vídeo compreensível com e sem áudio, sem perda de fala nos destaques |
| AE-08 | Radar copiado como hipótese de forma | Uma associação datada vira hipótese, mantendo evidências do vídeo separadas |
| AE-09 | Registro de métricas e próximo experimento | Dados próprios comparáveis em janelas fixas orientam a próxima mudança |
| AE-10 | Capacidade, tempo por etapa e redução de retrabalho | Gargalo escolhido por esforço registrado e capacidade disponível |

## As 10 atividades de componentes

| ID | Atividade | Resultado esperado |
|---|---|---|
| CP-01 | WordCaption | Palavra ativa com tempos fornecidos, sem inventar sincronização |
| CP-02 | RevealList | Lista acumulativa com destaque e espaço reservado |
| CP-03 | Process com Pipeline | Mecanismo curto em etapas e relações sustentadas pelas claims |
| CP-04 | ValueTable | Comparação de vários itens preservando unidades e notas |
| CP-05 | LimitMeter | Limiar linear com escala, marcador e zonas documentadas |
| CP-06 | Documento/quote vertical | Trecho documental legível em retrato e corretamente atribuído |
| CP-07 | Detalhe com Callout e anotação de gráfico | Alvo e explicação ligados às evidências, com leitura e posições conferidas |
| CP-08 | Mapa/timeline em retrato | Localização ou sequência temporal recomposta para 9:16 |
| CP-09 | Proporção e cascata sob demanda | Variante escolhida pela pergunta e denominador; números derivados explícitos |
| CP-10 | Áudio licenciado na montagem final | Trilha/efeitos preservados no arquivo final e subordinados à voz |

## Dependências entre as frentes

- **MC-01 → CP:** conferir API/export/build consumidos antes de decidir se precisa alterar o kit.
- **AE-01/AE-02 → receitas MC:** a pergunta e a promessa determinam qual cena precisa existir.
- **AE-05 → CP-01 → MC-04:** uso real de WordCaption depende de tempos por palavra; SRT por frase
  não fornece automaticamente esses tempos. O componente pode ser desenvolvido com fixture neutra.
- **CP-02/CP-03 → MC-05:** as receitas de lista/processo ganham exemplos executáveis após a integração.
- **CP-06 → MC-06:** a receita documental usa o layout vertical quando ele estiver integrado.
- **CP-04/CP-07 → MC-07:** tabela e anotação destravam os exemplos correspondentes; barras atuais
  podem servir ao primeiro exemplo homogêneo. CP-05/CP-09 só entram quando a pergunta os exigir.
- **CP-08 → MC-08:** mapa e timeline precisam de adaptação antes de entrar nos exemplos verticais.
- **CP-10 → MC-09:** cortes na fala já podem ser revistos; exemplos com trilha dependem da mixagem final.
- **MC-10/AE-07:** protocolo temporal e compreensão sem áudio validam cada entrega, em conjunto.
  Definir o protocolo pode acontecer antes dos componentes; aplicar a revisão acontece após cada integração.
- **AE-09/AE-10:** registro de resultados e esforço acompanha o lote inteiro e alimenta a próxima pauta.

Uma receita pode ter seu desenho documentado antes de um componente existir; seu uso em roteiro e
render fica condicionado à integração. Essas etapas da mesma atividade não criam tarefas adicionais.

## Por onde começar

1. **Definir o caso:** AE-01 e AE-02, com o dono; preparar AE-08 e o registro de AE-09/AE-10.
2. **Concluir a base:** AE-05, AE-06 e AE-07; fazer MC-01/MC-02, definir MC-03 e o protocolo MC-10.
3. **Primeira entrega visual:** escolher entre CP-03 (mecanismo), CP-02 (enumeração) e CP-06
   (evidência) conforme o caso. Aplicar a receita MC correspondente e conferir com MC-10/AE-07.
4. **Fechar a peça piloto:** AE-03 e AE-04. Usar o registro AE-09 quando houver publicação decidida
   pelo dono; ajustar a próxima entrega a partir de resultado e esforço reais.
5. **Expandir conforme a pergunta:** legenda por palavra, tabela, anotação, mapa, limite, variantes
   de gráfico e áudio entram quando o lote mostrar necessidade. A ordem dos IDs não obriga fabricar todos.

Este trabalho entrega o planejamento. Implementação, atualização de pin, validação visual e publicação
continuam como atividades futuras; nenhum componente ou resultado de audiência foi produzido aqui.
