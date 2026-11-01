# Pauta 3: árvores, sábado 2026-11-21, 12h

Série "eu medi" (`../serie.md`). Nada foi medido, gravado nem renderizado.

## Por que este conceito

Árvore é o conceito que todo curso ensina e que o iniciante nunca vê **ganhar** de nada. A demonstração põe a
árvore contra a lista ligada do Short de 31/10 (continuidade da série) e mostra o ganho em comparações, que é um
número que não depende da máquina, e em tempo, que depende.

## Os ângulos

### A. A mesma busca, lista contra árvore (recomendado)
- **Gancho (3 s):** "Procurei o mesmo número em dois lugares. Um precisou de um milhão de passos. O outro, vinte."
- **Demonstração:** um milhão de inteiros; a lista ligada da série anterior e uma árvore binária de busca
  montada com os valores embaralhados. Buscar os mesmos mil valores em cada uma; contar comparações por busca
  (mediana) e o tempo total (mediana de 15 rodadas).
- **O que a medição precisa responder:** comparações por busca em cada estrutura, o tempo total, e a altura da
  árvore montada com valores embaralhados.
- **Risco:** se a árvore for montada com valores **ordenados**, ela degenera numa lista (altura um milhão) e a
  busca fica tão lenta quanto a lista. Isso é o ângulo B, e precisa aparecer no `resultado.txt` como contraste.
- **Por que eu escolheria:** o número de passos é concreto e não precisa de explicação; a ordem de grandeza
  (um milhão contra ~20) é a história.

### B. A árvore que virou lista
- **Gancho:** "Inseri os números em ordem. A árvore virou uma fila."
- **Demonstração:** a mesma árvore montada com valores ordenados contra embaralhados; altura e comparações.
- **Risco:** com um milhão de inserções ordenadas a recursão pode estourar a pilha; inserir iterativamente. Vale
  como segunda metade do A (uma cena a mais) se couber em 45 s; senão, é o Short seguinte sobre o tema.

### C. Árvore balanceada contra não balanceada
- **Gancho:** "Mesma árvore, mesmos números. Só balanceei."
- **Demonstração:** AVL ou rubro-negra contra a BST simples. Exige mais código próprio (ou uma biblioteca com
  licença conferida); mais risco de erro de implementação no vídeo.
- **Risco:** o balanceamento é difícil de mostrar em 40 s; fica para depois.

## Demonstração planejada (ângulo A, com a altura degenerada do B como contraste)

- `demo/arvore.c`: monta lista e BST com os mesmos valores (embaralhados; `--ordenado` para o contraste),
  busca mil valores em cada, imprime comparações por busca (mediana), tempo total e a altura da árvore.
- `demo/resultado.txt`: 15 rodadas; a linha `ordenado` com a altura degenerada.
- Tela: `codigo` (a busca na lista e na árvore, lado a lado), `resultado` (`comparison`: comparações por busca),
  `altura` (`categories`: embaralhada contra ordenada), tempo no rodapé da cena.

## Forma (35 a 45 s)

1. Gancho, 3 s.
2. Código, 10 s: as duas buscas.
3. Resultado, 12 s: passos por busca, lista contra árvore; o tempo.
4. Só a medida, 8 s: "e se eu inserir em ordem, a altura vai a X e a árvore perde a vantagem".
5. Fecho, 6 s: "Por que vinte passos bastam? Comenta aqui, que o código está na descrição."

## Hipótese

A continuidade explícita com o Short 1 da série anterior ("a lista do vídeo passado") faz o público voltar.
Variável: a referência ao Short anterior no gancho ou no comentário fixado. Medida: views do `short-lista-ligada`
nos 7 dias após este Short sair, e retenção deste aos 7 e 28 dias.

## O que o dono decide

1. Ângulo (recomendo A com o contraste do B numa cena).
2. Título provisório: "Um milhão de passos contra vinte" / "A million steps versus twenty" (os números finais
   vêm da medição; o título só depois dela).

## O que esta pauta não diz

Nenhum número além do que a pauta prevê como hipótese de ordem de grandeza (um milhão contra ~20), que **não entra
no roteiro** antes de medido. Nada de complexidade assintótica na fala ("O de log n") sem fonte; a pergunta do
fecho e o comentário fixado levam isso.
