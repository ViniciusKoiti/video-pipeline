# Pauta 2: concorrência, sábado 2026-11-14, 12h

Série "eu medi" (`../serie.md`). Nada foi medido, gravado nem renderizado.

## Por que este conceito

Concorrência é o conceito em que o erro **não parece erro**: o programa roda, termina, e o número está errado.
A demonstração mostra isso em um número só, e o custo de corrigir em outro.

## Os ângulos

### A. Dois threads, um contador, o total errado (recomendado)
- **Gancho (3 s):** "Dois threads somam um milhão cada. O total deveria dar dois milhões."
- **Demonstração:** em C com `pthread`, dois threads incrementam a mesma variável um milhão de vezes cada.
  Versão A sem mutex: o total final (menor que dois milhões, e diferente a cada rodada). Versão B com mutex:
  dois milhões, e o tempo que custou. Versão C com `atomic` (opcional, se couber na duração): o total certo e o
  tempo no meio.
- **O que a medição precisa responder:** o total da versão A em 15 rodadas (mínimo, máximo, mediana), se a B
  acerta sempre, e o tempo de cada uma (mediana).
- **Risco:** com `-O2` o compilador pode otimizar o laço sem mutex para uma soma só, e o "erro" some. Mitigação:
  `volatile` ou leitura e escrita explícitas, registrado no `resultado.txt`; conferir no `objdump` que o laço
  existe. Se a máquina escalonar os threads em sequência, o total pode dar certo "por sorte" em rodadas:
  por isso 15 rodadas e a fala diz o intervalo, não um número só.
- **Por que eu escolheria:** o resultado é um número que o público pode prever errado. A surpresa está na
  previsão, não na explicação.

### B. O mutex custa quanto?
- **Gancho:** "Corrigi o bug. Olha o que aconteceu com o tempo."
- **Demonstração:** só a versão B contra a C (mutex contra atomic), tempo medido.
- **Risco:** pressupõe que o público já viu o bug; é continuação do A, não abertura.

### C. Deadlock ao vivo
- **Gancho:** "Dois threads esperando um pelo outro. Para sempre."
- **Demonstração:** dois mutexes tomados em ordem trocada; o programa trava; na tela, o `ps` mostrando os dois
  threads dormindo.
- **Risco:** "travou" não é um número; medir "tempo até travar" varia e pouco diz. Fica para um Short sem
  medição, fora da série.

## Demonstração planejada (ângulo A)

- `demo/contador.c`: `--mutex`, `--atomic`; imprime o total e o tempo (`clock_gettime`) por rodada, com a linha de
  ambiente. Compilado com a flag registrada; o laço conferido no `objdump` antes da medição.
- `demo/resultado.txt`: 15 rodadas de cada versão.
- Tela: `codigo` (o laço e a linha do mutex), `resultado` (`comparison`: total sem mutex contra com mutex, e o
  "esperado 2.000.000" no rodapé da cena), `tempo` (`categories`: ms de cada versão).

## Forma (35 a 45 s)

1. Gancho, 3 s.
2. Código, 10 s: os dois threads, a soma, a linha do mutex comentada.
3. Resultado, 12 s: o total errado (o intervalo das 15 rodadas) contra o certo.
4. Só a medida, 8 s: "sem mutex, entre X e Y; com mutex, dois milhões, em Z ms".
5. Fecho, 6 s: "Por que o total encolhe? Comenta aqui, que o código está na descrição."

## Hipótese

Um Short cujo gancho pede uma previsão ("deveria dar dois milhões") retém mais que um que entrega a resposta.
Variável: a pergunta de previsão no gancho. Medida: retenção aos 7 e 28 dias contra os Shorts 1 e 3.

## O que o dono decide

1. Ângulo (recomendo A; incluir a versão `atomic` só se couber em 45 s).
2. Título provisório: "Dois threads, um contador, e o total errado" / "Two threads, one counter, wrong total".

## O que esta pauta não diz

Nenhum número. Nada sobre escalonador, cache ou instruções atômicas na fala sem fonte; o porquê vai para a
pergunta do fecho e para o comentário fixado.
