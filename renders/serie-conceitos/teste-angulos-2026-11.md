# Teste de ângulos nos Shorts técnicos (novembro de 2026)

**Estado:** proposta, aguarda confirmação do dono. Nada foi alterado em pauta, agendamento ou CLAUDE.md.
**Andamento (2026-11-07):** o primeiro vídeo do bloco, idempotência no ângulo A, está em produção em
`renders/short-idempotencia-java/` (medição de 15 rodadas e roteiro prontos; render do MP4 silencioso em
andamento). Não agendado.
**Origem:** conversa de 2026-11-07. O dono quer seguir por duas linhas (medição própria e explicação de como
a tecnologia funciona), variar os vídeos e colocar um vídeo em cada ângulo para testar.

## 1. Duas linhas

- **Linha "eu medi":** conceito explicado com um número medido no computador do dono, na tela.
- **Linha "como funciona":** mecanismo explicado com animação e analogia do dia a dia, sem medição nova.
  Cada fato pede duas fontes independentes (CLAUDE.md, §2.2).

## 2. Os quatro ângulos

Cada ângulo é uma forma de abertura e de prova. Só a abertura muda entre os vídeos do bloco.

| Ângulo | Abertura | Prova | Referência no histórico |
|---|---|---|---|
| **A** | Pergunta sobre o que a pessoa vive, sem termo técnico nos 5 primeiros segundos | Medição própria antes de 20 s | Pergunta sobre espera, sem número |
| **B** | Pergunta sobre o efeito, com analogia do dia a dia | Explicação com fontes, sem medição nova | Pauta "como funciona" do garbage collector |
| **C** | Afirmação com número e custo, medidos | Medição própria, mostrada na tela | Índices com SQLite: 124 visualizações, a maior do grupo recente |
| **D** | Pergunta de dilema, com duas opções concretas ("X ou Y?") | Medição ou explicação, conforme o tema | CompletableFuture: 115 visualizações |

## 3. Atribuição proposta

Cada vídeo usa uma pauta já aprovada pelo dono e mantém a data do plano de novembro.

| Publicação (12h de Brasília) | Tema (pauta aprovada) | Produção prevista | Ângulo |
|---|---|---|---|
| qua 18/11 | Idempotência em Java | 08/11 | A |
| sáb 21/11 | HashMap e colisões em Java | 09/11 | C |
| seg 23/11 | Cache e cache stampede em Java | 10/11 | D |
| qua 25/11 | Como funciona o garbage collector | 06/11 na fila (confirmar o estado) | B |

Para o garbage collector, a abertura precisa ser reescrita no ângulo B antes da produção.

## 4. Regras comuns do bloco

- Mesmos canais (YouTube pt e en), mesmo horário, duração de 35 a 45 segundos.
- A pergunta ou a afirmação de abertura aparece também no título e escrita na tela no primeiro segundo.
- Hipótese registrada em `metrics.json` (campo `hypothesis`) antes de publicar.
- Temas diferentes entre os vídeos. Por isso o resultado confunde tema com ângulo, e a leitura precisa dizer isso.

## 5. Leitura e decisão

- Leituras de visualizações em 2 horas, 24 horas, 7 dias e 28 dias. Retenção nos primeiros 30 segundos e
  retenção média, no YouTube Studio.
- A decisão só vale depois dos quatro vídeos do bloco, como já registrado em `metrics.json`.
- Com quatro vídeos e quatro temas, o resultado indica onde olhar, não prova nada.
- Se um ângulo se destacar, o bloco seguinte repete esse ângulo em três temas diferentes para confirmar.

## 6. Limites

- Amostra pequena. A hipótese é exploratória.
- O canal em português tem poucos inscritos, então o alcance depende de busca e recomendação.
- O vidIQ mostra visualizações dos canais autorizados (@viniciusnakahara), mas não mostra retenção.

## 7. Decisões pendentes do dono

1. Confirmar os quatro ângulos e a atribuição da tabela 3.
2. Escolher o tamanho do teste: uma rodada de quatro vídeos (exploratória) ou três por ângulo, com doze vídeos
   (cerca de quatro semanas).
3. Autorizar a mudança de direção no CLAUDE.md (§1) e em `direcao-editorial.md`. Depois da confirmação, a
   atualização entra no mesmo commit.

## 8. Próxima rodada: abertura em quadros

Decisão do dono em 2026-11-07: a abertura passa a ser em quadros (3 a 4 quadros de formas geométricas nos primeiros 3 a 5 segundos, com a pergunta no último). Ela não entra nos vídeos de 08/11, que seguem como estão. Entra numa rodada seguinte, comparada com o ângulo que se destacar, para não misturar variáveis.
