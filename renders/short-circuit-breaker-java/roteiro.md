# Circuit breaker em Java: texto fechado antes da voz

## Atualização após voz

Em 2026-11-05, somente a fala inglesa `medido` foi reescrita e sintetizada com cache das demais cenas,
após falha determinística de nivelamento da versão anterior. Texto definitivo abaixo, também nas cópias
en/ig: "In this simulation, the breaker cut calls during the outage from sixty to twenty-four."
Afirmação, fontes e números preservados; humanizer reconferido antes da nova síntese. PT permanece com
81 palavras e EN passa a 87 (contagem por espaços). Nenhuma outra fala foi alterada.

As quatorze falas niveladas passaram no silencedetect a -50 dB, duração mínima 0,5 s, contra speech bounds
com margem de 0,05 s nas extremidades, sem pausas internas. Não houve síntese extra para alterar ritmo.
Tempos finais vêm dos WAVs: PT 29,283 s de fala / 35,3 s de timeline; EN 36,488 s / 39,2 s.
Render-ready em `pronto/content.pt.voz.json` e `pronto/content.en.voz.json`; os 43,4 s citados no
planejamento abaixo são históricos, preservados nos JSONs autorais, não as saídas para renderizar.
Sem render/review de imagens ou aprovação. Detalhes e comandos em `validacoes.md`.

## Lição em uma frase

O circuit breaker interrompe chamadas com falhas para evitar novas esperas, mas pode recusar pedidos mesmo depois de a dependência voltar.

Aplicação: pedidos Java chamando pagamento simulado. Decisão: envolver essa chamada com um breaker,
aceitando erros de recusa enquanto o circuito está aberto. A recuperação do pagamento é externa ao breaker.
Objetivo: explicar. Sete cenas, uma abertura hook e seis neutral, sem turn, CTA ou música.
Idioma original pt-BR; inglês e Instagram derivam dele. Planejamento inicial: 43,4 s por versão.

## Narração pt-BR

1. O pagamento cai na aplicação Java e as threads ficam esperando.
2. O circuit breaker fechado passa chamadas, mas cinco falhas seguidas abrem o circuito.
3. Aberto, devolve erro sem chamar o pagamento e evita esperar.
4. Após dois segundos, fica meio-aberto e libera um teste.
5. Se funcionar, fecha e retoma chamadas; se falhar, reabre.
6. Na simulação, as chamadas durante a falha caíram de sessenta para vinte e quatro.
7. Mas ainda recusou sete pedidos depois da volta do pagamento: proteger recursos também custa recusas.

## Narration en

1. Payments fail in a Java application and its threads are left waiting.
2. A closed circuit breaker lets calls through, but five consecutive failures open it.
3. While open, it returns an error without calling payments, avoiding the wait.
4. After two seconds, it becomes half-open and allows a test call.
5. Success closes it and resumes calls; failure opens it again.
6. In this simulation, the breaker cut calls during the outage from sixty to twenty-four.
7. But it still rejected seven requests after payments recovered: protecting resources also means rejecting requests.

## Rastreio e recorte

F1a/F2b sustentam fechado e aberto; F1b/F1c sustentam meio-aberto e retorno condicionado ao teste;
F1d/F2a sustentam espera e recursos; F2c sustenta o custo após a recuperação. D1 sustenta o cenário e os números.
Cinco falhas consecutivas e dois segundos são escolhas desta demo. Uma sonda por vez, não liberação geral.
O ramo de falha do teste é condicional, coberto pelo teste controlado, não resultado observado na mediana.

Na tela, 60 e 24 são chamadas à dependência durante a falha; 7 são recusas com chegada programada após
o fim da falha; 133 são recusas totais. Todos são medianas por rodada. Extremos: 60–60, 24–24, 6–7 e 132–133.
`medicao.json` rastreia também o teste único, o limiar, o intervalo, o JDK e o número de rodadas.
O rodapé identifica simulação, JDK 25 e 15 rodadas: versão é ambiente, não resultado.

A pauta existente foi preservada, inclusive seus trechos históricos pendentes. O escopo atual usa a demo já
concluída: três segundos de falha, não a proposta de dois segundos de lentidão da pauta; dois segundos são
o tempo aberto. Sem comparação de latência e sem alegar throughput, disponibilidade ou pagamentos recuperados.

## Humanizer revisado antes da voz

Revisão textual inicial concluída em 2026-11-05, com a skill `humanizer-narracao`: fatos e números preservados,
orações conectadas, sem anúncio antes do ponto, fecho de efeito vazio, trios ou promessa de código público.
Na preparação inicial não houve síntese ou escuta; a síntese autorizada posterior está registrada acima.
Glossários por idioma preparados.
Entregas: hook apenas na abertura, neutral no restante (seis de sete). Não há pausas artificiais.

Tempos são provisórios: parent ajusta pelos WAVs, preservando a leitura e o fim de todos os eventos.
Ainda faltam voz, escuta, quadros antes/durante/depois, render e gates humanos de tradução/prévia.
Nenhum gate foi aprovado nesta preparação.
