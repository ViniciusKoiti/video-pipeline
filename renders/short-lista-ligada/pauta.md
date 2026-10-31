# Pauta: Short de lista ligada para @baixo.nivel.dev.s, 2026-10-30

Pedido do dono (2026-10-30): um Short próprio sobre lista ligada, no formato de ~40 s. Pauta para validar antes de
qualquer medição, voz ou render. Nada foi medido, gravado nem renderizado.

**Referência de forma (só o id, para o dono assistir):** `GYr8zSisd7o` (canal de terceiro, 42 s, uma estrutura de
dados animada, link para o vídeo completo na descrição). Não se copia título, roteiro nem imagem dele. Ele é
referência de duração e ritmo; o nosso tem demonstração própria.

## Por que um ângulo, e não "lista ligada em 40 s"

A forma `shorts-tec` é "eu construí/medi", nunca "eu achei" (CLAUDE.md §12, conteúdo original). Um resumo de lista
ligada não tem nada do dono. Cada ângulo abaixo gira em torno de **uma demonstração que o dono roda** em
`baixo-nivel-demos` (mesmo desenho do `short-compiladores`: código pequeno, saída real na tela, versão do
compilador na legenda). Todo número da tela vem da execução dele; sem execução, fica fora.

## Os ângulos

### A. Medi a mesma soma em lista ligada e em array
- **Gancho (3 s):** "Somei 1 milhão de números de duas formas. Olha a diferença."
- **Demonstração:** dois programas em C, um com array e um com lista ligada, mesma soma, mesmo N; tempo medido
  com repetições e a mediana na tela, mais a máquina e a versão do gcc.
- **O que a medição precisa responder:** quanto uma estrutura leva a mais que a outra, e se a razão se mantém ao
  variar N (por exemplo 1 mil, 100 mil e 1 milhão).
- **Risco:** o resultado depende de como os nós foram alocados (ver B). Sem dizer isso, o Short generaliza demais.

### B. A mesma lista ligada, nós em outra ordem na memória (recomendado)
- **Gancho (3 s):** "A mesma lista. O mesmo código. Só mudei onde os nós ficam na memória."
- **Demonstração:** um programa só, duas listas com os mesmos valores: nós criados em sequência e nós embaralhados
  na memória; tempo de percorrer cada uma, com a mediana e o ambiente na tela.
- **O que a medição precisa responder:** se a ordem na memória muda o tempo de percorrer a lista e por quanto,
  e se a diferença cresce com N.
- **Por que eu escolheria:** é o ângulo que mais usa o que o canal tem de próprio (baixo nível, medido na máquina
  do dono) e o que o público de iniciante dificilmente vê. Dá um gancho de pergunta sem prometer o resultado.
- **Risco:** se a diferença medida for pequena, o Short vira "quase não muda" e o gancho precisa mudar para isso.
  Decide-se depois da medição, não antes.

### C. O que `p = p->next` vira no objdump
- **Gancho (3 s):** "Isto é percorrer uma lista ligada. Isto é o que a CPU recebe."
- **Demonstração:** a função de percorrer a lista compilada com `-O2`, lida no `objdump`, ao lado do código C;
  continuação direta do `short-compiladores`.
- **O que a listagem precisa responder:** quantas instruções tem o laço e quais delas dependem do resultado da
  anterior.
- **Risco:** é o mais seco e o menos "visual"; renderiza bem, mas retém menos sem um número forte na abertura.

## Forma (60 s ou menos, vertical, molde do `short-compiladores`)

1. Gancho, 3 s: a frase do ângulo escolhido, com os números só quando existirem.
2. Código, 12 s: as poucas linhas do programa na tela.
3. Resultado, 20 s: a medição (ou a listagem) com a versão do gcc e a máquina na legenda.
4. Por quê, 15 s: uma frase, só com o que a medição mostra. Nada que ela não cubra.
5. Fecho, 8 s: link do repositório na descrição; só entra quando o repositório estiver aberto com a pasta nova.

## Hipótese a registrar (CLAUDE.md §4)

- **Hipótese:** um Short com demonstração própria e medida na tela retém mais do que um Short de explicação
  genérica do mesmo tema.
- **Variável:** presença de número medido pelo dono na abertura.
- **Medida:** views e retenção aos 7 e 28 dias, comparadas com o `short-compiladores` quando ele tiver os 7 dias.
  Um Short não decide nada: a decisão é depois de 4 no mesmo recorte.

## O que o dono decide

1. **Ângulo:** A, B ou C (ou B + A num só Short de até 60 s). Recomendo B.
2. **Canais (decisão do dono, 2026-10-30):** os dois, um por idioma: `@baixo.nivel.dev.s` e `@viniciusnakahara`,
   com a mesma demonstração e a narração em pt e em en. **Inglês em `@baixo.nivel.dev.s` e português em
   `@viniciusnakahara`** (correção do dono, 2026-10-30; a minha sugestão era o contrário).
3. **Idioma e voz:** a voz em inglês (clonada do dono ou dublagem automática do YouTube) segue pendente de escuta
   cega (skill `shorts-tec`), e se o dono aparece na janela.
4. **Funil e chamada final (ADR 026):** topo (seguir) ou meio (comentar o resultado)? A chamada é do dono.
5. **Medição:** posso escrever e rodar os programas em C com `cpu_probe()` antes (máquina livre; medida em máquina
   limitada é inválida). Roda local, sem rede nem custo. Faço só depois do ok.

## Concorrência observada (vidIQ, 2026-10-30, só contagens públicas)

- O canal `@bytada` (pt-BR, criado em 2026-09-25) tem um Short sobre cache da CPU e a ordem do loop (id `b7JqSk55jw0`,
  ~36 mil views). O ângulo B toca o mesmo assunto de fundo (memória e cache). Para não virar versão do dele: a
  demonstração é a nossa (medida na máquina do dono, lista ligada, código na tela) e nada do roteiro, título ou
  imagem dele é reaproveitado. O dono assiste a ele antes de escolher o ângulo.

## Trilha sonora (decisão do dono, 2026-10-30)

Música em Short técnico é válida, mas **fica fora deste primeiro Short**, para a hipótese medir só a demonstração.
Entra a partir do segundo, o que pede estender o `juntar` da `shorts-tec` com ducking e escolher faixa do catálogo
(licença da YouTube Audio Library, só vale no YouTube; não serve para Reels do Instagram).

## O que esta pauta não diz

- Nenhum resultado de desempenho: não há medição ainda, e a intuição de que "array ganha" não entra no roteiro
  como fato.
- Nada sobre o canal de referência além da forma. Demanda de busca para "linked list" não foi medida (o vidIQ
  só devolveu uma pergunta em espanhol para "death note light"; para este tema não rodei a pesquisa).
- Títulos: ainda sem candidatos pontuados. Pontuo no vidIQ depois que o ângulo for escolhido (5 créditos por
  título).
