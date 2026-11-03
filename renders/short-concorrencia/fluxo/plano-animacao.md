# Concorrência em C: plano do fluxo animado

Pedido do dono: mostrar os acontecimentos com caixas conectadas e dizer que este
exemplo é em C; terminar perguntando sobre outras linguagens. Esta versão não
faz afirmações sobre o comportamento em Java ou em outra linguagem.

Fontes e fichas: `../explicacao/fontes.md`. Mesma medição e mesmo código C das
versões anteriores. As três animações são originais; licença e hash em `licencas.json`.

| Cena / trecho da fala | Estado inicial | Blocos e conexões | Ação | Estado final | Fonte |
| --- | --- | --- | --- | --- | --- |
| gancho / "Em C, dois threads..." | Pergunta sobre o total | C, threads e contador na capa | Nomear a linguagem e o total esperado | Expectativa explícita | DEMO, MEDIDA |
| resultado / "abaixo do esperado" | Esperado de 2.000.000 | Comparação das medianas | Mostrar 1.130.174 contra 2.000.000 | Diferença que pede explicação | MEDIDA |
| codigo / "Imagine os dois lendo dez..." | Contador didático em 10 | Duas colunas, cada uma com LER → SOMAR → GRAVAR, conectadas ao mesmo contador | Dois pontos coloridos levam 10 às leituras locais; ambos calculam 11 e o gravam; o segundo não chega a 12 | Contador em 11, uma soma perdida; aviso de comportamento indefinido em C | F01, DEMO, C11 |
| mutex / "um thread por vez" | A e B diante da mesma trava | Threads → trecho protegido → destrava | A entra; B fica esperando; A destrava e B entra | Exclusão mútua do trecho | F02, MUTEX |
| atomic / "operação indivisível" | Contador didático em 10 | A e B → caixa envolvendo LER, SOMAR e GRAVAR → contador | A caixa inteira destaca uma soma por vez; cada operação atualiza o contador | 10 → 11 → 12 | F03, F04, C11 |
| tempo / "onze... noventa e dois... 21" | Mecanismos já explicados | Barras com rótulos e unidade | Retomar os tempos do teste local | Custos medidos, com a versão errada identificada | F05, MEDIDA |
| fecho / "E em outras linguagens...?" | Exemplo de C explicado | Pergunta final | Convidar o público a escolher a próxima linguagem | Pedido de continuação, sem transferir conclusões de C | Pedido editorial do dono |

## Tempos locais das ações

- `codigo`: A recebe 10 entre 3,3–3,75 s; B recebe 10 entre 3,9–4,35 s.
  A devolve 11 entre 5,0–5,8 s; B devolve o mesmo 11 entre 6,1–6,9 s.
  A conclusão visual aparece em 6,9 s, e o aviso de C em 9,2 s.
- `mutex`: A entra em 0,4 s, destrava em 2,0 s; B entra em 2,3 s.
- `atomic`: o contador recebe 11 em 2,4 s e 12 em 4,9 s.

Esses tempos são marcações da ilustração sincronizada à fala, não tempos da medição
do programa. Os valores 10, 11 e 12 são didáticos, com entradas próprias de nota no
`medicao.json`; a animação não representa um trace capturado da execução em C.

## Revisão

Abrir os quadros de leitura e as faixas de movimento das três animações; verificar
também leitura/retorno do valor nos momentos intermediários, manutenção do valor local
de B após a gravação de A, troca de thread dentro do mutex e contador atômico em 10/11/12.
As fontes locais Noto Sans e as cores editoriais são fixadas no Lottie; revisar os
avisos `LOTTIE_TEXT` e `SAFE_AREA_UNCHECKED` pelas imagens, não só pelo validador.
