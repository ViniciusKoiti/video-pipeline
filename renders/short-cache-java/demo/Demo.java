import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.CountDownLatch;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Short "eu medi": cache na frente de um banco lento e o que acontece quando a chave mais pedida expira.
 * Uso: java Demo.java sem-cache | com-cache | expira-sem-protecao | expira-com-protecao
 *  - sem-cache:            1.000 requisicoes simultaneas da mesma pagina, todas vao ao banco
 *  - com-cache:            o mesmo, com a pagina no cache dentro da validade
 *  - expira-sem-protecao:  o mesmo, no instante em que a validade acabou; cada requisicao que erra recarrega por conta propria
 *  - expira-com-protecao:  o mesmo, mas so uma requisicao recarrega e as outras esperam o mesmo resultado
 * O banco e simulado: 50 conexoes (Semaphore) e 50 ms por consulta (Thread.sleep); nao e rede nem banco real.
 * Imprime uma linha: modo=... consultas_banco=... mediana_ms=... p99_ms=... maximo_ms=... total_ms=...
 * (os numeros da tela saem so do resultado.txt).
 */
public class Demo {
    static final int REQUISICOES = 1_000;
    static final int CONEXOES = 50;
    static final int CONSULTA_MS = 50;
    static final long VALIDADE_MS = 300;
    static final String CHAVE = "produto-42";

    static final Semaphore conexoes = new Semaphore(CONEXOES);
    static final AtomicInteger consultas = new AtomicInteger();

    record Entrada(String valor, long expiraNs) {
        boolean valida() {
            return System.nanoTime() < expiraNs;
        }
    }

    // O banco: pega uma das 50 conexoes, "consulta" por 50 ms e devolve a pagina.
    static Entrada consultarBanco(String chave) {
        try {
            conexoes.acquire();
            try {
                consultas.incrementAndGet();
                Thread.sleep(CONSULTA_MS);
            } finally {
                conexoes.release();
            }
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return new Entrada("pagina de " + chave, System.nanoTime() + VALIDADE_MS * 1_000_000);
    }

    // Cache simples: acerto devolve da memoria; erro (ausente ou expirado) vai ao banco e guarda.
    static final ConcurrentHashMap<String, Entrada> cache = new ConcurrentHashMap<>();

    static String obterSemProtecao(String chave) {
        Entrada e = cache.get(chave);
        if (e != null && e.valida()) {
            return e.valor();
        }
        Entrada nova = consultarBanco(chave);
        cache.put(chave, nova);
        return nova.valor();
    }

    // Cache com recarga unica: o mapa guarda o CompletableFuture da carga; quem chega durante a recarga espera o mesmo.
    static final ConcurrentHashMap<String, CompletableFuture<Entrada>> cacheUnico = new ConcurrentHashMap<>();

    static String obterComProtecao(String chave) {
        CompletableFuture<Entrada> f = cacheUnico.compute(chave, (k, atual) ->
                atual != null && (!atual.isDone() || atual.join().valida())
                        ? atual
                        : CompletableFuture.supplyAsync(() -> consultarBanco(k), Executors.newVirtualThreadPerTaskExecutor()));
        return f.join().valor();
    }

    public static void main(String[] args) throws Exception {
        String modo = args.length > 0 ? args[0] : "expira-com-protecao";
        boolean protegido = modo.equals("expira-com-protecao");
        boolean comCache = !modo.equals("sem-cache");
        switch (modo) {
            case "sem-cache", "com-cache", "expira-sem-protecao", "expira-com-protecao" -> { }
            default -> throw new IllegalArgumentException("modo: sem-cache | com-cache | expira-sem-protecao | expira-com-protecao");
        }

        // Preparacao (fora da medicao): com cache, a pagina ja foi carregada; nos modos de expiracao, espera a validade acabar.
        if (modo.equals("com-cache")) {
            obterSemProtecao(CHAVE);
        } else if (modo.startsWith("expira")) {
            if (protegido) {
                obterComProtecao(CHAVE);
            } else {
                obterSemProtecao(CHAVE);
            }
            Thread.sleep(VALIDADE_MS + 100);
        }
        consultas.set(0);

        List<Double> latencias = Collections.synchronizedList(new ArrayList<>());
        CountDownLatch largada = new CountDownLatch(1);
        long inicio;
        try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
            for (int i = 0; i < REQUISICOES; i++) {
                executor.submit(() -> {
                    try {
                        largada.await();
                    } catch (InterruptedException e) {
                        Thread.currentThread().interrupt();
                        return;
                    }
                    long t0 = System.nanoTime();
                    if (!comCache) {
                        consultarBanco(CHAVE);
                    } else if (protegido) {
                        obterComProtecao(CHAVE);
                    } else {
                        obterSemProtecao(CHAVE);
                    }
                    latencias.add((System.nanoTime() - t0) / 1_000_000.0);
                });
            }
            Thread.sleep(200); // todas as virtuais criadas e esperando a largada
            inicio = System.nanoTime();
            largada.countDown();
        } // close() espera todas as requisicoes terminarem
        double totalMs = (System.nanoTime() - inicio) / 1_000_000.0;

        List<Double> ordenadas = new ArrayList<>(latencias);
        Collections.sort(ordenadas);
        int n = ordenadas.size();
        double mediana = (n % 2 == 1) ? ordenadas.get(n / 2) : (ordenadas.get(n / 2 - 1) + ordenadas.get(n / 2)) / 2;
        double p99 = ordenadas.get((int) Math.ceil(n * 0.99) - 1);
        System.out.printf(java.util.Locale.ROOT,
                "modo=%s requisicoes=%d consultas_banco=%d mediana_ms=%.1f p99_ms=%.1f maximo_ms=%.1f total_ms=%.1f%n",
                modo, n, consultas.get(), mediana, p99, ordenadas.get(n - 1), totalMs);
    }
}
