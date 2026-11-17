# Fontes do Short "Consistent hashing em Java" (rotina de 2026-11-08)

**Estado: completo para o mecanismo** (as três fontes da pauta lidas em 2026-11-08, depois que o dono liberou
`WebFetch`/`curl` para os dois domínios). Nada abaixo vem de memória. PDFs baixados em
`data/episodes/short-consistent-hashing-java-pt/sources/` (`dynamo.pdf`, `karger.pdf`; fora do Git).
Os trechos foram lidos nas páginas dos PDFs; a numeração é a do artigo.

## 1. Dynamo (SOSP 2007), "Dynamo: Amazon's Highly Available Key-value Store", seção 4.2 "Partitioning Algorithm"

https://www.allthingsdistributed.com/files/amazon-dynamo-sosp2007.pdf (pp. 209–210 da revista; arquivo `dynamo.pdf`)

- **F-D1 (anel, regra da chave):** "In consistent hashing [10], the output range of a hash function is treated as a
  fixed circular space or "ring" (i.e. the largest hash value wraps around to the smallest hash value). Each node in
  the system is assigned a random value within this space which represents its "position" on the ring. Each data item
  identified by a key is assigned to a node by hashing the data item's key to yield its position on the ring, and then
  walking the ring clockwise to find the first node with a position larger than the item's position."
- **F-D2 (vantagem):** "The principle advantage of consistent hashing is that departure or arrival of a node only
  affects its immediate neighbors and other nodes remain unaffected."
- **F-D3 (limite do anel básico):** "The basic consistent hashing algorithm presents some challenges. First, the random
  position assignment of each node on the ring leads to non-uniform data and load distribution."
- **F-D4 (nós virtuais):** "instead of mapping a node to a single point in the circle, each node gets assigned to
  multiple points in the ring. To this end, Dynamo uses the concept of "virtual nodes". A virtual node looks like a
  single node in the system, but each node can be responsible for more than one virtual node."
- **F-D5 (benefício do nó novo):** "When a node becomes available again, or a new node is added to the system, the
  newly available node accepts a roughly equivalent amount of load from each of the other available nodes."
- **F-D6 (hash do Dynamo):** "It applies a MD5 hash on the key to generate a 128-bit identifier" (seção 4.1). Por isso a
  demonstração usa MD5 (4 primeiros bytes); isso é escolha da demonstração, não afirmação do artigo sobre 32 bits.

## 2. Karger et al., 1997, "Consistent Hashing and Random Trees: Distributed Caching Protocols for Relieving Hot Spots on the World Wide Web" (STOC '97)

https://www.cs.princeton.edu/courses/archive/fall09/cos518/papers/chash.pdf (arquivo `karger.pdf`, pp. 1–2)

- **F-K1 (propriedade):** "Roughly speaking, a consistent hash function is one which changes minimally as the range
  of the function changes." (resumo)
- **F-K2 (contra o hash comum):** "Unlike standard hashing schemes, a small change in the bucket set does not induce a
  total remapping of items to buckets." (seção 1.2)
- (O trecho da seção 1.2 sobre o servidor central que redistribui a tabela não foi copiado literalmente; não usar.)

## 3. Javadoc de `java.util.TreeMap`, Java SE 25 & JDK 25 (Oracle)

https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/TreeMap.html (lido em 2026-11-08, antes
desta sessão)

- **F-T1:** `ceilingEntry(K)`: "Returns a key-value mapping associated with the least key greater than or equal to
  the given key, or null if there is no such key."
- **F-T2:** "This implementation provides guaranteed log(n) time cost for the containsKey, get, put and remove
  operations."
- Uso no programa: o dono da chave é o `ceilingEntry` (primeiro ponto a partir da chave); quando é `null`, volta ao
  primeiro ponto (`firstEntry`). Nota: a frase do `ceilingEntry` foi lida na tabela de resumo.

## Medição própria (não é fonte externa)

- `renders/short-consistent-hashing-java/demo/resultado.txt` (15 rodadas, sonda de CPU antes de cada uma, JDK
  25.0.4.1, Ryzen 7 5700U).
- As frações de chaves movidas e a carga são determinísticas (100 mil ids com semente 42, MD5, 4 → 5 servidores);
  só o tempo da busca varia entre rodadas. A carga do anel depende dos nomes dos servidores, por isso o programa
  repete com 20 conjuntos de nomes e informa a média e os extremos.
- Os números são de memória (sem rede, sem cache real). Não dizem nada sobre latência de um cache distribuído.
- O tempo da busca (módulo ~11 ns; anel 97 a 179 ns) **não** vai à tela nem à fala: JIT e ruído entre rodadas
  (extremos de 44 a 606 ns); sem repetir com aquecimento não é número publicável.

---

## Fontes das empresas dos Reels (adicionadas em 2026-11-08, depois do pedido do dono)

Pedido do dono: três Reels, cada um abrindo com uma pergunta sobre uma empresa diferente (Amazon, Discord, Akamai) e
o Short citando uma só. Arquivos baixados em `data/episodes/short-consistent-hashing-java-pt/sources/`
(`akamai-maggs-sitaraman.pdf` e `.txt`, `discord-elixir.html` e `.txt`; fora do Git). Texto extraído por `pdftotext`
e por remoção de tags; as aspas abaixo foram conferidas contra esse texto. Nada vem de memória nem do resumo da busca.

## 4. Akamai: Maggs e Sitaraman, "Algorithmic Nuggets in Content Delivery", ACM SIGCOMM CCR 45(3), 2015, seção 3

https://people.cs.umass.edu/~ramesh/Site/HOME_files/CCRpaper_1.pdf (arquivo `akamai-maggs-sitaraman.pdf`)

**Fonte interessada:** os dois autores constam como "Duke and Akamai" e "UMass, Amherst and Akamai". Descreve a própria
empresa; o `vp check` pede aviso para fato só com ela, e o Reel não afirma nada fora do que o artigo diz.

- **F-A1 (onde e por quê):** "Consistent hashing [17, 22] is used by the CDN to balance the load within a single
  cluster of servers. Consistent hashing was the first algorithmic innovation in Akamai's CDN"
- **F-A2 (o círculo):** "both objects and buckets are first mapped to the unit circle. As shown in Figure 4, each
  object is then mapped to the next bucket that appears in clockwise order on the unit circle."
- **F-A3 (servidor novo):** "if a new bucket is added, e.g., the failed server comes back on-line, the only objects
  that have to be moved are those that are mapped to the new bucket."
- Escopo: o artigo diz "within a single cluster of servers"; o Reel não fala da Akamai inteira nem de hoje, só do que
  o artigo (2015) descreve. `bucket` = servidor, `object` = arquivo servido.

## 5. Discord: Stanislav Vishnevskiy, "How Discord Scaled Elixir to 5,000,000 Concurrent Users", 6 de julho de 2017

https://discord.com/blog/how-discord-scaled-elixir-to-5-000-000-concurrent-users (arquivo `discord-elixir.html`)

**Fonte interessada** (post do próprio Discord, de 2017). O Reel diz "em 2017" e não afirma nada sobre o Discord de hoje.

- **F-Di1 (o anel):** "Discord is a distributed system achieved through consistent hashing. Using this method requires
  us to create a ring data structure that can be used to lookup the node of a particular entity."
- **F-Di2 (a consulta por comunidade):** "When a session connects, it has to lookup the remote node for each guild it is
  interested in. The cost of communicating with another Erlang process using request/reply is about 12μs."
- **F-Di3 (o gargalo):** "we started to notice issues when we had bursts of users reconnecting. The Erlang process
  responsible for controlling the ring would start to get so busy that it would fail to keep up with requests to the
  ring, and the whole system would become overloaded."
- **F-Di4 (a solução):** "it puts that data into a read-only shared heap that processes can access without copying the
  data." e "Since the data is never copied, the lookup cost decreases to 0.3us, bringing the total time down to 750ms!"
- Escopo: `guild` é a comunidade do Discord (o que o app chama de servidor). Os 12μs e os 0,3μs são do Discord, de
  2017, na máquina e no software deles; **não** são medição do dono e não se misturam com a demonstração em Java.
  O post não diz quantos pontos virtuais o anel do Discord usa; o Reel não afirma isso.

## Medição própria nos Reels

Os Reels reusam a medição já feita (`demo/resultado.txt`, 15 rodadas): 80,18% (módulo) contra 20,13% (anel com 100
pontos), 251,5% / 140,2% / 111,2% de carga. Nenhum número de empresa entra como se fosse da demonstração.
