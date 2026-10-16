# 020 — Conta feita na tela a partir de fichas

- **Status:** aceito pelo dono em 2026-10-14 (proposta do agente no outline de `confeitaria-ingrediente-pt`)
- **Data:** 2026-10-14
- **Etapa do roadmap:** roteiro (#28) e checagem (#31)
- **Relaciona-se com:** ADR 008 (planos), ADR 011 (decisão 7: a tela não calcula), ADR 019 (objetivo `explicar`)

## Contexto

A série da confeitaria por encomenda explica contas: o custo de um ingrediente é o preço da embalagem dividido
pela quantidade da embalagem, vezes a quantidade que a receita usa. O resultado (R$ 9,10 no primeiro reel) não
está em nenhuma fonte: os três números e a regra estão em fichas, o resultado sai da aritmética.

A ADR 011 (decisão 7) e o CLAUDE.md §6 dizem que a tela não calcula razão, variação nem soma que não esteja numa
ficha. A regra existe para o roteiro não derivar fato novo ("cresceu 40%") a partir de números soltos. Numa
peça cujo objetivo é a conta, o resultado é o conteúdo, e proibir a conta mata a peça.

## Decisão

1. **Um número calculado pode ir para a tela** (`number`, `compare`) quando, ao mesmo tempo:
   - cada insumo está numa ficha com citação literal (preço, peso, quantidade da receita);
   - a regra da conta está numa ficha com fonte (o método), ou é aritmética elementar;
   - a narração diz a conta inteira antes do resultado ("dezoito e quarenta e quatro, dividido por trezentos e
     noventa e cinco, vezes cento e noventa e cinco");
   - as `claims` do plano apontam para as fichas de cada insumo e da regra, e o `text` da claim escreve a conta
     com o resultado ("18,44 ÷ 395 × 195 = R$ 9,10");
   - o resultado é arredondado como se fala, na convenção do idioma, e o rótulo diz o que ele mede.
2. **O que não muda.** Razão, variação percentual ou soma que a narração não diz inteira continuam fora da tela.
   O template continua sem calcular (`showRatio` desligado, nenhuma conversão): o número calculado é escrito pelo
   roteirista e refeito pelo verificador a partir das fichas, como qualquer afirmação.
3. **Só em `explicar`.** Num vídeo que noticia ou opina, a conta não entra.
4. **`vp check` segue como está.** Candidato (#31): claim que começa com "conta:" e traz a expressão, para o
   check refazer a aritmética e recusar resultado errado.

## Consequências

- CLAUDE.md §6 e ADR 011 (decisão 7) ganham a ressalva com a data; as skills `roteiro-explicativo` e `checagem`
  ganham uma linha cada.
- O primeiro reel da série (`confeitaria-ingrediente-pt`) usa a regra nas cenas S04 e S05.

## Emenda (2026-10-16, ADR 028)

- **O item 4 saiu do papel:** a conta ganhou plano próprio (`calculation`), e o `vp check` refaz a aritmética dele
  e recusa o resultado que não bate nas casas escritas.
- **Total da nota:** no plano `receipt`, a soma das linhas vai à tela sem a narração dizer cada parcela, desde que
  a claim escreva a soma inteira, o `vp check` a refaça e a narração diga o total.
