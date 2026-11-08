# Roteiro: virtual threads em Java (série "eu medi")

Pauta: `data/episodes/short-virtual-threads-java-pt/pauta.md` (aprovada pelo dono em 2026-11-03). Funil `topo` (padrão da
série, a confirmar). Sem música. Título provisório: **"10 mil requisições em Java: threads ou virtual threads?"**.
Em 2026-11-04 o dono pediu que o vídeo **explique o que são threads**, não só mostre resultados: ver a cena `threads`.

Pergunta central: **o que muda num servidor que espera I/O quando cada requisição ganha uma virtual thread, e onde o
gargalo vai parar?**

## A lição em uma frase

**Uma thread comum segura uma thread do sistema operacional, que é cara, até quando só espera; a virtual thread não
segura, e tirar esse limite não tira o próximo: o gargalo passa a ser o pool de conexões.**
Por isso a decisão de System Design é dimensionar as conexões, não as threads.

| Cena | Regra ou consequência dita na fala |
| --- | --- |
| `gancho` | a pergunta: onde vai parar o gargalo |
| `threads` | uma thread executa uma requisição e, em Java, segura uma thread do sistema, cara, mesmo esperando |
| `plataforma` | por isso o pool tem limite (200) e o resto das requisições espera na fila |
| `codigo` | trocar o pool por virtual threads é uma linha |
| `virtual` | a virtual thread é da JVM e não segura a thread do sistema enquanto espera: as dez mil esperam juntas |
| `conexoes` | com 50 conexões no banco, a fila reaparece nelas |
| `medido` | os três tempos medidos |
| `fecho` | o gargalo saiu das threads e foi para as conexões; qual limite dimensionar |

## Origem de cada número

Medição própria: `demo/resultado.txt` (`Demo.java` + `medir.sh`, OpenJDK 25.0.4.1, Ryzen 7 5700U, 15 rodadas, JVM nova por
modo e por rodada, sonda de CPU entre 0,043 e 0,082 s antes de cada rodada; as 10 mil tarefas concluíram em todas).
A espera é `Thread.sleep(100)`: **simulação de I/O**, dita no vídeo; não é rede nem banco reais.

| Cena | Fala / tela | Origem |
| --- | --- | --- |
| `gancho`, `plataforma`, `virtual`, `conexoes` | dez mil requisições | constante `TAREFAS` do `Demo.java` |
| `threads`, `plataforma`, `virtual`, `conexoes` | espera de 100 ms | constante `ESPERA_MS`, simulada |
| `plataforma`, `codigo`, `medido` | pool de 200 threads | constante `THREADS` |
| `conexoes`, `medido` | 50 conexões | constante `CONEXOES` (`Semaphore`) |
| `medido` | "cinco segundos" / 5.089 ms | mediana `plataforma_ms` 5088,6 (mín. 5077,6; máx. 5221,4) |
| `medido` | "cento e setenta e nove milissegundos" / 179 ms | mediana `virtual_ms` 179,4 (mín. 167,9; máx. 318,0) |
| `medido` | "vinte segundos" / 20.139 ms | mediana `virtual_com_pool_ms` 20139,0 (mín. 20120,7; máx. 20203,1) |

Razões derivadas (não ditas): plataforma/virtual = 28,4; virtual com pool/plataforma = 3,96. Esperado pela conta
(10.000 ÷ 200 × 100 ms = 5.000 ms; 10.000 ÷ 50 × 100 ms = 20.000 ms): a medição ficou perto nos dois.

## Fontes do mecanismo

`fontes.md`: T1–T5 (o que é uma thread, plataforma × virtual), V1–V8, E1–E2. "A fila reaparece nas conexões" é
**inferência da medição**, não afirmação das fontes (as fontes dizem só que se limita recurso com semáforo, V6).

## Regras seguidas

- Nenhum tempo sem medição; a fala não generaliza os tempos para outros servidores, bancos ou cargas reais.
- Java e JDK 25 explícitos no gancho e no rodapé; espera simulada dita no rodapé.
- System Design: serviço de pedidos (requisições → threads → banco); a decisão é dimensionar as conexões.
- O modo `cpu` da pauta ficou de fora (o vídeo ficaria acima de 55 s com a explicação de threads).
- A comparação "virtual com 50 conexões × pool de 200" (3,96×) não é dita: os dois limites são diferentes (50 e 200)
  e a fala não deve sugerir que as virtuais são "piores".

## Fora deste Short

- *Pinning* (`synchronized`): resolvido no JDK 24 pelo JEP 491 (P1, P2 em `fontes.md`).
- Tarefas de CPU, reativo/assíncrono, `StructuredTaskScope`, memória por virtual thread.
