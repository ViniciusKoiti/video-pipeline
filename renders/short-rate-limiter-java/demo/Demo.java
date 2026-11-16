import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.Semaphore;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongSupplier;

/**
 * Short "eu medi": rate limiter (token bucket) em Java. Uma API de busca recebe clientes normais e um robo em rajada.
 * Uso: java -cp classes Demo sem-limite | com-limite
 *
 * Cenario (tudo simulado com Thread.sleep, sem rede):
 *  - o servico de tras atende ate 10 requisicoes ao mesmo tempo, cada uma leva 50 ms (fila FIFO quando lota);
 *  - 5 clientes normais chegam em ritmo constante: cada um 10 por segundo (50 por segundo no total),
 *    por 6000 ms (300 requisicoes);
 *  - o robo dispara 1000 requisicoes de uma vez, em 1000 ms;
 *  - com-limite: um balde de fichas POR CLIENTE (escrito aqui, sem biblioteca): capacidade 100, enche 20 fichas por
 *    segundo, cada requisicao gasta uma ficha; sem ficha, a API responde 429 sem chamar o servico de tras.
 * Imprime uma linha com as metricas; os numeros da tela saem so do resultado.txt.
 */
public class Demo {
    static final int SLOTS = 10;
    static final int SERVICO_MS = 50;
    static final int CLIENTES_NORMAIS = 5;
    static final int INTERVALO_CLIENTE_MS = 100;
    static final int DURACAO_NORMAL_MS = 6000;
    static final int ROBO_REQUISICOES = 1000;
    static final long ROBO_CHEGADA_MS = 1000;
    static final int BALDE_CAPACIDADE = 100;
    static final double BALDE_FICHAS_POR_S = 20.0;

    static long t0;

    static long agoraMs() {
        return (System.nanoTime() - t0) / 1_000_000;
    }

    /** Token bucket minimo: enche a uma taxa fixa ate a capacidade; cada requisicao gasta uma ficha. */
    static class TokenBucket {
        private final long capacidade;
        private final double fichasPorNs;
        private final LongSupplier relogioNs;
        private double fichas;
        private long ultimoNs;

        TokenBucket(long capacidade, double fichasPorSegundo, LongSupplier relogioNs) {
            this.capacidade = capacidade;
            this.fichasPorNs = fichasPorSegundo / 1_000_000_000.0;
            this.relogioNs = relogioNs;
            this.fichas = capacidade;
            this.ultimoNs = relogioNs.getAsLong();
        }

        synchronized boolean tentaGastar() {
            long agora = relogioNs.getAsLong();
            fichas = Math.min(capacidade, fichas + (agora - ultimoNs) * fichasPorNs);
            ultimoNs = agora;
            if (fichas >= 1.0) {
                fichas -= 1.0;
                return true;
            }
            return false;
        }
    }

    /** Um balde por cliente: o robo esvaziar o dele nao mexe no dos outros. */
    static class Limitador {
        private final java.util.Map<String, TokenBucket> baldes = new java.util.concurrent.ConcurrentHashMap<>();

        boolean permite(String cliente) {
            return baldes.computeIfAbsent(cliente,
                    c -> new TokenBucket(BALDE_CAPACIDADE, BALDE_FICHAS_POR_S, System::nanoTime)).tentaGastar();
        }
    }

    record Chegada(String cliente, boolean robo, long chegadaMs) {}

    record Resultado(boolean robo, boolean recusada, long latenciaMs) {}

    public static void main(String[] args) throws Exception {
        String modo = args.length > 0 ? args[0] : "com-limite";
        if (!modo.equals("sem-limite") && !modo.equals("com-limite")) {
            throw new IllegalArgumentException("modo: sem-limite | com-limite");
        }
        Limitador limitador = new Limitador();
        Semaphore servico = new Semaphore(SLOTS, true);
        AtomicInteger emEspera = new AtomicInteger();
        AtomicInteger filaMax = new AtomicInteger();
        AtomicInteger atendidas = new AtomicInteger();
        List<Resultado> resultados = Collections.synchronizedList(new ArrayList<>());

        List<Chegada> chegadas = new ArrayList<>();
        for (int c = 0; c < CLIENTES_NORMAIS; c++) {
            for (long t = c * (INTERVALO_CLIENTE_MS / CLIENTES_NORMAIS); t < DURACAO_NORMAL_MS; t += INTERVALO_CLIENTE_MS) {
                chegadas.add(new Chegada("cliente-" + c, false, t));
            }
        }
        for (int i = 0; i < ROBO_REQUISICOES; i++) {
            chegadas.add(new Chegada("robo", true, ROBO_CHEGADA_MS));
        }
        chegadas.sort((a, b) -> Long.compare(a.chegadaMs(), b.chegadaMs()));

        t0 = System.nanoTime();
        List<Thread> requisicoes = new ArrayList<>();
        for (Chegada ch : chegadas) {
            long espera = ch.chegadaMs() - agoraMs();
            if (espera > 0) {
                Thread.sleep(espera);
            }
            requisicoes.add(Thread.ofVirtual().start(() -> {
                if (modo.equals("com-limite") && !limitador.permite(ch.cliente())) {
                    resultados.add(new Resultado(ch.robo(), true, agoraMs() - ch.chegadaMs()));
                    return;
                }
                int fila = emEspera.incrementAndGet();
                filaMax.accumulateAndGet(fila, Math::max);
                try {
                    servico.acquire();
                    emEspera.decrementAndGet();
                    try {
                        Thread.sleep(SERVICO_MS);
                        atendidas.incrementAndGet();
                    } finally {
                        servico.release();
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
                resultados.add(new Resultado(ch.robo(), false, agoraMs() - ch.chegadaMs()));
            }));
        }
        for (Thread r : requisicoes) {
            r.join();
        }
        long totalMs = agoraMs();

        List<Long> latNormais = new ArrayList<>();
        int normaisRecusadas = 0, roboAceitas = 0, roboRecusadas = 0;
        for (Resultado r : resultados) {
            if (r.robo()) {
                if (r.recusada()) roboRecusadas++; else roboAceitas++;
            } else {
                latNormais.add(r.latenciaMs());
                if (r.recusada()) normaisRecusadas++;
            }
        }
        Collections.sort(latNormais);
        long mediana = latNormais.get(latNormais.size() / 2);
        long p99 = latNormais.get((int) Math.ceil(latNormais.size() * 0.99) - 1);
        long maximo = latNormais.get(latNormais.size() - 1);
        System.out.printf(Locale.ROOT,
                "modo=%s normais=%d normais_mediana_ms=%d normais_p99_ms=%d normais_max_ms=%d normais_recusadas=%d robo_aceitas=%d robo_recusadas=%d servico_atendidas=%d fila_max=%d total_ms=%d%n",
                modo, latNormais.size(), mediana, p99, maximo, normaisRecusadas, roboAceitas, roboRecusadas,
                atendidas.get(), filaMax.get(), totalMs);
    }
}
