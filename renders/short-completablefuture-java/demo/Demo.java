import java.util.Locale;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.atomic.AtomicLong;

// Demonstração do CompletableFuture (pauta do Short "CompletableFuture em Java").
// As duas dependências são simuladas por Thread.sleep com latência fixa, declarada no resultado.
// Modos: sequencial (uma consulta depois da outra), composto (as duas em paralelo com thenCombine),
// timeout (orTimeout cancela a espera, não a tarefa: mede quando a tarefa realmente termina).
public class Demo {
    static final long PRECO_MS = 300;
    static final long ESTOQUE_MS = 200;
    static final long ESTOQUE_LENTO_MS = 2000;
    static final long PRAZO_MS = 500;
    static final ExecutorService POOL = Executors.newFixedThreadPool(4);

    static String consulta(String nome, long ms) {
        try {
            Thread.sleep(ms);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            throw new CompletionException(e);
        }
        return nome;
    }

    static double decorrido(long t0) {
        return (System.nanoTime() - t0) / 1_000_000.0;
    }

    public static void main(String[] args) throws Exception {
        String modo = args.length > 0 ? args[0] : "sequencial";
        long t0 = System.nanoTime();
        try {
            switch (modo) {
                case "sequencial" -> {
                    String p = consulta("preco", PRECO_MS);
                    String e = consulta("estoque", ESTOQUE_MS);
                    System.out.println(String.format(Locale.ROOT, "ms=%.1f resultado=%s+%s", decorrido(t0), p, e));
                }
                case "composto" -> {
                    CompletableFuture<String> preco = CompletableFuture.supplyAsync(() -> consulta("preco", PRECO_MS), POOL);
                    CompletableFuture<String> estoque = CompletableFuture.supplyAsync(() -> consulta("estoque", ESTOQUE_MS), POOL);
                    String r = preco.thenCombine(estoque, (p, e) -> p + "+" + e).join();
                    System.out.println(String.format(Locale.ROOT, "ms=%.1f resultado=%s", decorrido(t0), r));
                }
                case "timeout" -> {
                    AtomicLong fimTarefa = new AtomicLong();
                    CompletableFuture<String> estoque = CompletableFuture.supplyAsync(() -> {
                        String r = consulta("estoque-lento", ESTOQUE_LENTO_MS);
                        fimTarefa.set(System.nanoTime());
                        return r;
                    }, POOL).orTimeout(PRAZO_MS, TimeUnit.MILLISECONDS);
                    String resposta;
                    try {
                        resposta = estoque.join();
                    } catch (CompletionException ex) {
                        resposta = "falhou:" + ex.getCause().getClass().getSimpleName();
                    }
                    double respostaMs = decorrido(t0);
                    while (fimTarefa.get() == 0) {
                        Thread.sleep(5);
                    }
                    double tarefaMs = (fimTarefa.get() - t0) / 1_000_000.0;
                    System.out.println(String.format(Locale.ROOT,
                            "ms=%.1f tarefa_terminou_em_ms=%.1f resultado=%s", respostaMs, tarefaMs, resposta));
                }
                default -> throw new IllegalArgumentException("modo desconhecido: " + modo);
            }
        } finally {
            POOL.shutdownNow();
        }
    }
}
