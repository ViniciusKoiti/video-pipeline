# Pauta: "O que o compilador faz com o seu código" (Short para @baixo.nivel.dev.s), 2026-10-25

Pedido do dono: explicar tecnicamente como o compilador transforma o código em binário. Pauta para validar antes
de voz e render. Nada gravado nem renderizado.

## A demonstração (já feita, saídas reais de gcc 15.2 e objdump)

Função de 7 linhas, `soma_quadrados(n)`, soma `i*i` de 1 a n (`demo/soma.c`), compilada em três níveis:

| Nível | Linhas de instrução | Tamanho do .o | O que muda |
| --- | --- | --- | --- |
| -O0 | 18 | 1272 bytes | cada variável vive na pilha (`[rbp-0x8]`, `[rbp-0xc]`); o laço é um `jmp` e um `cmp` com memória a cada volta |
| -O1 | 17 | 1264 bytes | variáveis passam para registradores; o laço fica mais curto |
| -O2 | 18 | 1248 bytes | o compilador reescreve o laço: `test edi,edi` cuida do caso n=0 antes, e a conta vai direto em `rax`/`rcx` |

Em -O0 a função tem a cara do código-fonte: a pilha guarda `total` e `i` como no C. Em -O2 quase não sobra
variável com nome, e a leitura exige entender a conta. Esse é o ponto do Short: o compilador apaga os nomes
e reorganiza o laço, mas o resultado continua fazendo a mesma soma.

## Ângulo e roteiro (60 s, vertical, molde do Short 2)

1. Gancho, 3 s: "O mesmo código, três binários. O compilador decide quase tudo."
2. -O0, 12 s: o código-fonte em cima, a listagem com as variáveis na pilha em baixo; a câmera marca `[rbp-0x8]` e `[rbp-0xc]`.
3. -O1 e -O2, 20 s: as mesmas linhas, agora com registradores; a contagem de linhas aparece como cartão (18, 17, 18).
4. Por que: 12 s, uma frase sobre o que o compilador faz (analisa, transforma, gera código de máquina) e sobre o
   otimizador, sem jargão.
5. Fecho, 8 s: "é por isso que engenharia reversa é ler o que o compilador deixou." e a descrição com o repositório.

## Pontos a validar antes da voz

- Os números (18, 17, 18 linhas; 1272, 1264, 1248 bytes) são da máquina de hoje (gcc 15.2, x86-64). Versões
  diferentes do gcc mudam o código; a legenda diz a versão.
- Não há afirmação sobre desempenho: só o que a listagem mostra. Medir tempo seria outro Short.
- O repositório público de demos (`github.com/ViniciusKoiti/baixo-nivel-demos`) pode receber `soma.c` em uma pasta nova.

## Títulos (para pontuar no vidIQ depois da validação)

- O mesmo código, três binários: o que o compilador muda
- What the compiler does to your code: -O0 vs -O2
