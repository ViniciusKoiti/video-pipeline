# Fontes: virtual threads em Java

Baixadas em 2026-11-04 (curl, só leitura; texto extraído em `fontes/*.txt`). Frases literais conferidas no texto extraído.

| Id | Fonte | Arquivo | sha256 (html) |
| --- | --- | --- | --- |
| JEP444 | JEP 444: Virtual Threads (OpenJDK, Closed / Delivered, JDK 21), https://openjdk.org/jeps/444 | `fontes/jep444.html` | e8a0b9ba02cd12f154a191b40a308fb84845f6779b0439f0e53182c8a2bdf0aa |
| JEP491 | JEP 491: Synchronize Virtual Threads without Pinning (Closed / Delivered, JDK 24), https://openjdk.org/jeps/491 | `fontes/jep491.html` | f8b83e0135eca102da5fe74e425ec2cd8ce14e3fdf68c950224bec87bb17344e |
| EXEC | Javadoc `java.util.concurrent.Executors`, JDK 25 | `fontes/executors.html` | f38600719cd071edf7cfc4b70ca495fd7388ddedc46a57c1b13513ea6d538a33 |
| THR | Javadoc `java.lang.Thread`, JDK 25 | `fontes/thread.html` | 5e6778961fb01408a9ffa9c5233fb4e3d8e3f4a6c54a69b3d6b1b3c249fa4601 |

## Frases literais

- **T1** (JEP444, "Why virtual threads?"): "The thread is Java's unit of concurrency: a piece of sequential code that runs concurrently with — and largely independently of — other such units." e "Each thread provides a stack to store local variables and coordinate method calls".
- **T2** (JEP444): "the JDK implements threads as wrappers around operating system (OS) threads. OS threads are costly, so we cannot have too many of them".
- **T3** (JEP444, "Virtual threads"): "A virtual thread is an instance of java.lang.Thread that is not tied to a particular OS thread. A platform thread, by contrast, is an instance of java.lang.Thread implemented in the traditional way, as a thin wrapper around an OS thread."
- **T4** (JEP444): "While a platform thread monopolizes a precious OS thread, a virtual thread does not."
- **T5** (JEP444, "Scheduling and mounting"): "the JDK's virtual thread scheduler assigns the virtual thread for execution on a platform thread by mounting the virtual thread on a platform thread. This makes the platform thread become the carrier of the virtual thread." (a virtual thread só ocupa uma thread do SO enquanto roda; V3 e V4 dizem o resto).
- **V1** (JEP444, "Why virtual threads?"): "If each request consumes a thread, and thus an OS thread, for its duration, then the number of threads often becomes the limiting factor long before other resources, such as CPU or network connections, are exhausted."
- **V2** (JEP444): "This happens even when threads are pooled, since pooling helps avoid the high cost of starting a new thread but does not increase the total number of threads."
- **V3** (JEP444): "Application code in the thread-per-request style can run in a virtual thread for the entire duration of a request, but the virtual thread consumes an OS thread only while it performs calculations on the CPU."
- **V4** (JEP444, "Scheduling and mounting"): "Typically, a virtual thread will unmount when it blocks on I/O or some other blocking operation in the JDK, such as BlockingQueue.take()."
- **V5** (JEP444): "Virtual threads are cheap and plentiful, and thus should never be pooled: A new virtual thread should be created for every application task."
- **V6** (JEP444, "Do not pool virtual threads"): "Developers sometimes use thread pools to limit concurrent access to limited resources." e "do not be tempted to pool virtual threads in order to limit concurrency. Instead use constructs specifically designed for that purpose, such as semaphores."
- **V7** (JEP444): "For this program, a pool with 200 platform threads can only achieve a throughput of 200 tasks-per-second, whereas virtual threads achieve a throughput of about 10,000 tasks-per-second (after sufficient warmup)." (o exemplo do JEP dorme 1 s por tarefa; o nosso dorme 100 ms: **não reusar esse número**, só o mecanismo.)
- **V8** (JEP444): "A server application like this, with straightforward blocking code, scales well because it can employ a large number of virtual threads."
- **P1** (JEP444, pinning): "Pinning does not make an application incorrect, but it might hinder its scalability." (fora do Short.)
- **P2** (JEP491, objetivo): "Improve the scalability of Java code that uses synchronized methods and statements by arranging for virtual threads that block in such constructs to release their underlying platform threads for use by other virtual threads." (entregue no JDK 24; o ambiente é o JDK 25. Fora do Short.)
- **E1** (Executors): "Creates an Executor that starts a new virtual Thread for each task." (`newVirtualThreadPerTaskExecutor()`)
- **E2** (Executors): "Creates a thread pool that reuses a fixed number of threads operating off a shared unbounded queue." (`newFixedThreadPool(int nThreads)`)

## O que cada fonte sustenta no Short

- O que é uma thread, plataforma × virtual: T1, T2, T3, T4, T5.
- Plataforma × virtual com I/O: V1, V2, V3, V4, E1, E2.
- A virtual thread não é pooled; limite de recurso com semáforo: V5, V6. É o que o `virtual-com-pool` faz (`Semaphore(50)`).
- A fila reaparece em outro lugar: **inferência da medição** (`demo/resultado.txt`), não afirmação das fontes. As fontes dizem que o limite de threads some (V1, V2) e que o limite de recurso se faz com semáforo (V6); o tempo medido mostra o resultado.
- Limite do exemplo: a espera é `Thread.sleep(100)` (I/O simulado), não rede nem banco reais.
