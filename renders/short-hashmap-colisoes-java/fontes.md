# Fontes do Short "HashMap e colisões em Java" (produção de 2026-11-09)

Conferência feita em 2026-11-09 por leitura direta das páginas (texto em inglês citado literalmente; a marcação
do markdown foi removida). Nada aqui vem de memória.

## Fontes fichadas

1. **Javadoc de `java.util.HashMap`, Java SE 25**
   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/util/HashMap.html (HTTP 200, lida em 2026-11-09)
   - Desempenho: "This implementation provides constant-time performance for the basic operations (get and put), assuming the hash function disperses the elements properly among the buckets."
   - Capacidade e fator de carga: "The capacity is the number of buckets in the hash table, and the initial capacity is simply the capacity at the time the hash table is created." e "When the number of entries in the hash table exceeds the product of the load factor and the current capacity, the hash table is rehashed (that is, internal data structures are rebuilt) so that the hash table has approximately twice the number of buckets."
   - Aviso: "Note that using many keys with the same hashCode() is a sure way to slow down performance of any hash table."
   - Desempate: "To ameliorate impact, when keys are Comparable, this class may use comparison order among keys to help break ties."
   - Uso no Short: o `hashCode` escolhe o balde; com hash que espalha, o tempo é constante; muitas chaves com o mesmo
     `hashCode` pioram a tabela; chave `Comparable` pode ajudar. A página **não diz** quanto piora nem como o balde é
     percorrido: esse número e o comportamento vêm só da medição própria.

2. **Javadoc de `java.lang.Object`, Java SE 25, contrato de `hashCode`**
   https://docs.oracle.com/en/java/javase/25/docs/api/java.base/java/lang/Object.html (HTTP 200, lida em 2026-11-09)
   - "If two objects are equal according to the equals method, then calling the hashCode method on each of the two objects must produce the same integer result."
   - "It is not required that if two objects are unequal according to the equals method, then calling the hashCode method on each of the two objects must produce distinct integer results. However, the programmer should be aware that producing distinct integer results for unequal objects may improve the performance of hash tables."
   - Atenção na fala: o texto diz "may improve", não "improves". Um `hashCode` constante **cumpre o contrato** e
     ainda assim derruba o desempenho: é o ponto do Short.

## Fonte não lida

- **JEP 180, "Handle Frequent HashMap Collisions with Balanced Trees"** (https://openjdk.org/jeps/180): a leitura
  falhou por permissão do `WebFetch` e **não foi citada**. Sem ela, o roteiro não afirma limite de entradas por
  balde nem quando o balde vira árvore. O Javadoc acima já sustenta "chave `Comparable` pode desempatar".

## Medição própria (não é fonte externa)

- `renders/short-hashmap-colisoes-java/demo/Demo.java` (JDK 25.0.4.1). Resultado oficial **ainda não existe**: a
  rodada de 15 execuções não pôde ser iniciada em 2026-11-09 (ver `data/rotina/2026-11-09.md`).
- Rodada de teste de calibração (um processo por modo, sem sonda por rodada, **não é resultado**, não usar como
  número de tela): bom 259 ns por busca; fraco 1.046 ns; constante 89.923 ns; constante-comparable 557 ns;
  `equals` por busca 1,00 / 101,5 / 10.001,5 / 14,9 (20 mil chaves).

## Lacunas

- JEP 180 não lido (acima).
- Medição oficial (15 rodadas, `medicao.json`) pendente.
