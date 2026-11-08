# Busca De Polimento Da Voz

Direcao do dono: buscar qualidade percebida proxima de 9/10, usando o earshot
com Gemini como segunda opiniao. Meta de qualidade, nao garantia de nota.

## Estado

- Implementado: processamento local isolado, comparacao no mesmo volume,
  registro das medidas e retentativas limitadas de indisponibilidade da API.
- Proposto abaixo: busca automatizada de tratamentos. O timer atual NAO muda
  audio, gera candidatas ou repete avaliacoes validas para tentar obter nota maior.
- Polimento de producao continua desligado. A primeira escuta humana preferiu
  a atual no par 1 e empatou no par 2. A candidata posterior de de-esser isolado
  ainda nao teve avaliacao comparativa valida: houve respostas HTTP 503.

## Fluxo Proposto

1. Fixar o audio de controle, seus hashes, os trechos, a rubrica e o modelo.
   A nota 9 nao entra no prompt do avaliador, para nao induzir a resposta.
2. Obter uma comparacao valida da candidata atual antes de criar outra.
   Retentativa de 503 so recupera disponibilidade; nao conta como nova candidata.
3. Se houver defeito especifico sustentado pela escuta, escolher uma unica
   variavel para a proxima rodada: por exemplo, intensidade do de-esser.
   Se o problema for pronuncia ou prosodia, registrar que DSP nao resolve.
4. Gerar no maximo duas candidatas por rodada, apenas de WAVs existentes,
   sem TTS, render, dependencia nova ou alteracao do episodio.
5. Conferir duracao, pico, clipping e volume igualado entre as versoes.
   Reprovar tecnicamente a candidata que violar os limites existentes.
6. Avaliar controle e candidatas com nomes neutros e a mesma rubrica. Registrar
   cada resposta valida, inclusive notas baixas e empates, sem selecionar so a maior.
7. Verificar a candidata escolhida em trechos reservados do mesmo episodio,
   nao usados para ajustar parametros, e depois na escuta cega do dono.
8. Parar com meta atingida e confirmada, ausencia de melhora, limite de rodadas,
   cota ou erro permanente. Registrar needs_review, nunca aprovar automaticamente.

## Orcamento E Paradas

- Proposta inicial: ate tres rodadas, ate duas novas candidatas por rodada.
  Novos envios de trechos e esse orcamento ainda precisam de autorizacao do dono.
- Cada avaliacao tem seu limite de retentativas; chamadas HTTP tambem contam
  no orcamento, mesmo quando nao produzem uma critica aproveitavel.
- Comparacao pendente autorizada: ate 12 chamadas totais, incluindo as seis
  anteriores, intervalo de cinco minutos e janela renovada de duas horas.
- Atualizacao de 2026-11-05: a chamada 7 terminou por timeout, sem avaliacao
  aproveitavel. O job longo permanece encerrado. A nova rodada usa os mesmos
  tratamentos na abertura de 12,92 s por versao (26,84 s com a pausa), em pasta
  separada, com ate cinco chamadas e o mesmo intervalo: sete anteriores mais
  cinco novas mantem o teto de 12. comparacao.json fixa duracao, loudness e
  limite do job; alterar a configuracao depois de iniciar interrompe o envio.
- Nao repetir uma resposta valida so porque a nota ficou abaixo de 9.
- Nota >= 9 isolada nao encerra com aprovacao: precisa de vantagem sobre o
  controle, confirmacao nos trechos reservados e ausencia de regressao na escuta.
- Se as notas oscilarem ou o modelo nao distinguir as versoes, resultado
  inconclusivo; nao aumentar automaticamente tentativas ou intensidade do filtro.
- Usar somente a camada gratuita informada pelo dono, sem ativar faturamento,
  trocar de endpoint ou modelo automaticamente. Voz so sai da maquina no escopo
  autorizado. Confirmar novamente antes de enviar outros trechos.

## Ativacao

Alcancar a meta nao liga voice_polish.enabled. Uma mudanca global continua
dependendo da decisao do dono e da emenda a ADR 054. A baseline e os arquivos
aprovados permanecem intactos. Notas de LLM nao sao MOS validado.
