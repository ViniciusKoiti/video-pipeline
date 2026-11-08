import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicInteger;

/**
 * Short "eu medi": 10 mil requisicoes que esperam I/O (simulado por Thread.sleep).
 * Uso: java Demo.java plataforma | virtual | virtual-com-pool
 *  - plataforma:       Executors.newFixedThreadPool(200)
 *  - virtual:          Executors.newVirtualThreadPerTaskExecutor()
 *  - virtual-com-pool: as mesmas virtuais, cada uma pegando 1 de 50 "conexoes" (Semaphore) durante a espera
 * Imprime uma linha: modo=... total_ms=... concluidas=... (os numeros da tela saem so do resultado.txt).
 */
public class Demo {
    static final int TAREFAS = 10_000;
    static final int ESPERA_MS = 100;
    static final int THREADS = 200;
    static final int CONEXOES = 50;

    public static void main(String[] args) throws Exception {
        String modo = args.length > 0 ? args[0] : "virtual";
        AtomicInteger concluidas = new AtomicInteger();
        Semaphore conexoes = new Semaphore(CONEXOES);
        Runnable requisicao = switch (modo) {
            case "plataforma", "virtual" -> () -> {
                dormir();
                concluidas.incrementAndGet();
            };
            case "virtual-com-pool" -> () -> {
                try {
                    conexoes.acquire();
                    try {
                        dormir();
                    } finally {
                        conexoes.release();
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                    return;
                }
                concluidas.incrementAndGet();
            };
            default -> throw new IllegalArgumentException("modo: plataforma | virtual | virtual-com-pool");
        };
        long inicio = System.nanoTime();
        try (ExecutorService executor = modo.equals("plataforma")
                ? Executors.newFixedThreadPool(THREADS)
                : Executors.newVirtualThreadPerTaskExecutor()) {
            for (int i = 0; i < TAREFAS; i++) {
                executor.submit(requisicao);
            }
        } // close() espera todas as tarefas terminarem
        double ms = (System.nanoTime() - inicio) / 1_000_000.0;
        System.out.printf(java.util.Locale.ROOT, "modo=%s total_ms=%.1f concluidas=%d%n", modo, ms, concluidas.get());
    }

    static void dormir() {
        try {
            Thread.sleep(ESPERA_MS);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    }
}
