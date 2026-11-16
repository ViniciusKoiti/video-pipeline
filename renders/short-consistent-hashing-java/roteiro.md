# Consistent hashing em Java: roteiro (rotina de 2026-11-08)

**Pauta:** `data/episodes/short-consistent-hashing-java-pt/pauta.md` (aprovada em 2026-11-03).
**Título provisório:** "Adicionei 1 servidor e o cache inteiro mudou de lugar: consistent hashing em Java" /
"I added one server and the whole cache moved: consistent hashing in Java".
**Publicação prevista:** seg 16/11 (plano de novembro). Nada agendado.

**Empresa citada (pedido do dono, 2026-11-08):** só a **Amazon** (Dynamo, F-D1 a F-D5); o `TreeMap` fica na tela, não na fala. As
empresas Discord e Akamai ficam nos três Reels (`reels-por-empresa.md`). `content.pt.json`/`content.en.json` ainda têm o
texto antigo da cena `anel`: refazer depois de o dono aprovar o texto e antes da primeira voz.

## A lição em uma frase

> **`hash % N` troca o dono de quase toda chave quando N muda; no anel só as chaves do arco do servidor novo trocam,
> e muitos pontos por servidor deixam a carga parelha.**

Cada cena de explicação diz na fala uma parte da regra (módulo, anel, consequência medida, limite e solução da carga).
A tela repete a lição e mostra o mecanismo; não a substitui.

## Aplicação e decisão de System Design

- **Aplicação:** cache distribuído de sessões em N servidores; a equipe adiciona um servidor para aguentar mais carga.
  Quem escolhe o servidor de uma sessão é a aplicação (o cliente do cache), antes de falar com ele.
- **Decisão:** como a chave vira servidor: **módulo** (`hash(chave) % N`) ou **anel** (servidor ocupa pontos num
  círculo; a chave vai ao primeiro ponto no sentido horário), e **quantos pontos virtuais por servidor**.
- **Benefício (medido):** ao passar de 4 para 5 servidores, 80,18% das sessões trocam de servidor no módulo contra
  20,13% no anel com 100 pontos por servidor (ideal 1/5 = 20%); no anel, nenhuma das que trocaram foi para um
  servidor antigo.
- **Limite (medido):** com 1 ponto por servidor o mais cheio recebe 251,5% da carga ideal; com 10, 140,2%; com 100,
  111,2%. O módulo é mais parelho (100,7%) e sua busca é uma conta, não uma árvore.
- **Cuidado de escopo:** 5 servidores, MD5, 100 mil ids; o desvio com 100 pontos não vale para outros N nem outros
  hashes. A carga é de memória, sem rede nem cache real; o tempo de busca não é número do vídeo (ver `fontes.md`).

## Origem de cada número ou afirmação (ver `fontes.md`)

| O que o vídeo diz ou mostra | Origem |
| --- | --- |
| "quase toda chave muda de resto" quando N muda; 80,18% das sessões trocam (módulo) | Medição `demo/resultado.txt` (mediana de 15 rodadas, determinístico) |
| Exemplo didático das chaves 0 a 19 (resto por 4 e por 5): 16 de 20 mudam | Conta do próprio exemplo, não é medição (rótulo "exemplo didático") |
| Anel: a chave vai para o primeiro servidor no sentido horário | Dynamo §4.2 (F-D1); Karger (F-K1) |
| Só o vizinho é afetado quando um servidor entra | Dynamo §4.2 (F-D2); Karger (F-K2) |
| `TreeMap` acha o primeiro ponto a partir da chave | Javadoc `ceilingEntry` (F-T1) |
| 20,13% mudam no anel com 100 pontos; 0 vão para outro servidor que não o novo | Medição (`movidas_pct`, `fora_do_novo`) |
| 1 ponto por servidor: carga desigual; pontos virtuais corrigem | Dynamo §4.2 (F-D3, F-D4); medição 251,5% / 140,2% / 111,2% |

## Cenas (nome, tipo, fala em pt-BR) e entrega

| Cena | Tipo | Fala | Entrega |
| --- | --- | --- | --- |
| `situacao` | animação (abertura em 3 quadros) | Entrou o quinto servidor do cache. | hook |
| `pergunta` | hook (pergunta escrita) | Por que quase toda sessão mudou de lugar? | neutral |
| `modulo` | animação | O servidor é o resto do hash por N, e mudando o N, quase toda chave muda de resto. | neutral |
| `medicao-modulo` | number | Em cem mil sessões simuladas, oitenta por cento trocaram de servidor. | neutral |
| `anel` | animação | No Dynamo, da Amazon, o anel acha o servidor no sentido horário, e o novo toma só o seu arco. | turn |
| `comparacao` | versus | Com cem pontos por servidor, só vinte por cento mudaram, e todas foram para o servidor novo. | neutral |
| `pontos` | categories | Mas com um ponto por servidor a carga fica torta, e cem pontos virtuais deixam parelha. | neutral |
| `fecho` | end_card | Quantos pontos virtuais você usaria por servidor? | invite |

Fecho: pergunta de decisão (quantos pontos), sem resposta do vídeo.
