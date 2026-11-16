# Montagem: a espinha antes das cenas

Ramo da skill `edicao-de-roteiro` para quando o roteirista entregou só o `outline.md` (pergunta central,
gancho, espinha com os ids das fichas e a abertura escrita) e ainda não há `scenes.json`. Mudar a ordem aqui
custa uma linha; depois das cenas, custa âncoras, claims e voz. Tudo o que o `SKILL.md` diz sobre nota,
primeiros 30 s, atribuições, fronteiras e segunda passada vale igual; aqui muda o que você lê e o que propõe.

## Passos

1. **Fichas a frio.** Leia `facts.json` inteiro antes do outline e anote, sem olhar a escolha do roteirista:
   as três fichas com que você abriria o vídeo e a pergunta que elas levantam. Pronto quando as três têm id
   e uma linha de motivo. Se, ao ler o outline, uma decisão do dono barrar alguma delas (spoiler, por
   exemplo), mantenha-a anotada como reserva e escolha outra.
2. **Primeiros 30 s.** Passe a abertura escrita no outline pelos quatro testes. Se o outline só descreve as
   batidas da abertura, sem o texto, diga isso na primeira linha da seção, teste as batidas e peça o texto
   ao roteirista em "Para o dono e o roteirista". O título do teste 1 é o provisório da `pauta.md`. Se os
   testes passam mas há nota dentro da abertura, escreva a abertura inteira com as notas aplicadas, para
   comparação. O teste de atribuições e datas fica para a edição: na montagem, vale só para a abertura
   escrita. Compare o gancho do
   roteirista com as suas três fichas: se outra abre melhor, a abertura proposta usa essa. Pronto como no
   `SKILL.md`: cada teste com `passa` ou `falha` e o trecho, e toda falha com a abertura proposta inteira.
3. **Espinha.** Para cada bloco do outline, responda: que parte da resposta ele acrescenta, que pergunta ele
   deixa aberta para o próximo, e que ficha é o seu ponto mais forte. Bloco sem uma das três respostas vira
   nota, de qualquer tipo da tabela do `SKILL.md`. Pronto quando todo bloco tem as três respostas ou
   uma nota.
4. **Fichas fora.** Liste as fichas aprovadas que o outline não usa e que serviriam à promessa, com o bloco
   onde entrariam; e as usadas que não servem a ela. Pronto quando toda ficha de `facts.json` está no
   outline, nesta lista ou marcada como dispensada.
5. **Arquivo e relatório.** Grave a seção "Montagem" no `edicao.md` e devolva só isto, no lugar do relatório
   do `SKILL.md`: o resultado dos quatro testes, a ordem proposta em uma linha, as três notas que mais pesam
   e o que pede ficha.

## Arquivo

No `edicao.md`, antes de qualquer seção de edição:

```markdown
# Edição do roteiro: <id>

## Montagem — <data>

### Fichas a frio
As três fichas com que você abriria, a pergunta que levantam e as reservas barradas por decisão do dono.

### Primeiros 30 s
(a tabela dos quatro testes e a abertura proposta, como no SKILL.md)

### Espinha
| Bloco | Acrescenta à resposta | Deixa aberto | Ficha mais forte |
|---|---|---|---|
| 1. Origem | de onde veio o primeiro dinheiro | por que só eles tinham acesso | F04 |

**Ordem proposta:** gancho (F11) → 2 → 1 → 3 → fecho (F02). Motivo em uma frase.

### Notas
(o mesmo formato; "Trecho" é a linha ou o fragmento do outline, "Proposta" é a batida com os ids das fichas, "Custo" é o
que sai ou muda de lugar)

### Fichas
- **Entrariam:** F09, no bloco 3, como o caso antes do conceito.
- **Usadas que pouco servem à promessa:** F21 (bloco 2).
- **Dispensadas:** F30–F41.

### Para o dono e o roteirista
### Limites desta leitura
```

"O que não mexer" e "Referências para a descrição" ficam para a edição.

Teto: 8 notas. A proposta de montagem é em batidas e fichas; frase pronta só na abertura e onde a nota é uma
pergunta ou uma ponte.
