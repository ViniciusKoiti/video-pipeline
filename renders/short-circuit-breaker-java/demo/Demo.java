import java.util.ArrayList;
import java.util.Collections;
import java.util.List;
import java.util.Locale;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.function.LongSupplier;

/**
 * Short "eu medi": circuit breaker em Java. Uma API de pedidos chama o servico de pagamento (simulado).
 * Uso: java Demo.java sem-breaker | com-breaker
 *
 * Cenario (tudo simulado com Thread.sleep, sem rede):
 *  - 300 requisicoes chegam a cada 20 ms (50 por segundo) e sao atendidas por um pool de 20 threads;
 *  - o pagamento FALHA de 0 a 3000 ms: cada chamada espera 1000 ms (tempo limite) e termina em erro;
 *  - depois de 3000 ms o pagamento volta e responde em 50 ms.
 *  - com-breaker: o breaker abaixo (escrito aqui, sem biblioteca) abre apos 5 falhas seguidas, fica aberto por
 *    2000 ms, depois deixa passar UMA chamada de teste (meio-aberto): sucesso fecha, falha abre de novo.
 * Imprime uma linha com as metricas; os numeros da tela saem so do resultado.txt.
 */
public class Demo {
    static final int REQUISICOES = 300;
    static final int INTERVALO_MS = 20;
    static final int THREADS = 20;
    static final long FALHA_ATE_MS = 3000;
    static final int TIMEOUT_MS = 1000;
    static final int NORMAL_MS = 50;
    static final int FALHAS_PARA_ABRIR = 5;
    static final long ABERTO_MS = 2000;
    static final long NORMAL_LIMITE_MS = 200;

    static long t0;

    static long agoraMs() {
        return (System.nanoTime() - t0) / 1_000_000;
    }

    /** O pagamento simulado: ate FALHA_ATE_MS cada chamada espera o tempo limite e falha. */
    static void pagamento(AtomicInteger chamadasNaFalha) throws Exception {
        boolean falhando = agoraMs() < FALHA_ATE_MS;
        if (falhando) {
            chamadasNaFalha.incrementAndGet();
            Thread.sleep(TIMEOUT_MS);
            throw new Exception("tempo limite do pagamento");
        }
        Thread.sleep(NORMAL_MS);
    }

    static class CircuitoAberto extends RuntimeException {
        CircuitoAberto() {
            super("circuito aberto", null, false, false);
        }
    }

    /** Circuit breaker minimo: FECHADO -> ABERTO -> MEIO_ABERTO -> FECHADO. */
    static class Breaker {
        enum Estado { FECHADO, ABERTO, MEIO_ABERTO }

        private Estado estado = Estado.FECHADO;
        private int falhasSeguidas = 0;
        private long abertoEm = 0;
        private boolean testeEmCurso = false;
        private long geracao = 0;
        private final LongSupplier relogio;

        Breaker() {
            this(Demo::agoraMs);
        }

        Breaker(LongSupplier relogio) {
            this.relogio = relogio;
        }

        interface Chamada { void executa() throws Exception; }

        void chama(Chamada c) throws Exception {
            boolean eraTeste = false;
            long geracaoDaChamada;
            synchronized (this) {
                if (estado == Estado.ABERTO && relogio.getAsLong() - abertoEm >= ABERTO_MS) {
                    estado = Estado.MEIO_ABERTO;
                    geracao++;
                    testeEmCurso = false;
                }
                if (estado == Estado.ABERTO) {
                    throw new CircuitoAberto();
                }
                if (estado == Estado.MEIO_ABERTO) {
                    if (testeEmCurso) {
                        throw new CircuitoAberto();
                    }
                    testeEmCurso = true;
                    eraTeste = true;
                }
                geracaoDaChamada = geracao;
            }
            try {
                c.executa();
            } catch (Exception e) {
                synchronized (this) {
                    // Resultados em voo de uma geracao anterior nao mudam o circuito atual.
                    if (geracaoDaChamada == geracao) {
                        falhasSeguidas++;
                        if (eraTeste || falhasSeguidas >= FALHAS_PARA_ABRIR) {
                            estado = Estado.ABERTO;
                            geracao++;
                            abertoEm = relogio.getAsLong();
                            testeEmCurso = false;
                        }
                    }
                }
                throw e;
            }
            synchronized (this) {
                if (geracaoDaChamada == geracao) {
                    falhasSeguidas = 0;
                    if (eraTeste) {
                        estado = Estado.FECHADO;
                        geracao++;
                        testeEmCurso = false;
                    }
                }
            }
        }
    }

    record Pedido(int id, long chegadaMs) {}

    record Resultado(long chegadaMs, long latenciaMs, boolean ok, boolean recusada) {}

    public static void main(String[] args) throws Exception {
        String modo = args.length > 0 ? args[0] : "com-breaker";
        if (!modo.equals("sem-breaker") && !modo.equals("com-breaker")) {
            throw new IllegalArgumentException("modo: sem-breaker | com-breaker");
        }
        Breaker breaker = new Breaker();
        AtomicInteger chamadasNaFalha = new AtomicInteger();
        LinkedBlockingQueue<Pedido> fila = new LinkedBlockingQueue<>();
        List<Resultado> resultados = Collections.synchronizedList(new ArrayList<>());
        Pedido fim = new Pedido(-1, 0);

        t0 = System.nanoTime();
        List<Thread> workers = new ArrayList<>();
        for (int i = 0; i < THREADS; i++) {
            Thread w = new Thread(() -> {
                try {
                    for (Pedido p = fila.take(); p.id() >= 0; p = fila.take()) {
                        boolean ok = true;
                        boolean recusada = false;
                        try {
                            if (modo.equals("com-breaker")) {
                                breaker.chama(() -> pagamento(chamadasNaFalha));
                            } else {
                                pagamento(chamadasNaFalha);
                            }
                        } catch (CircuitoAberto e) {
                            ok = false;
                            recusada = true;
                        } catch (Exception e) {
                            ok = false;
                        }
                        resultados.add(new Resultado(p.chegadaMs(), agoraMs() - p.chegadaMs(), ok, recusada));
                    }
                } catch (InterruptedException e) {
                    Thread.currentThread().interrupt();
                }
            });
            w.start();
            workers.add(w);
        }
        for (int i = 0; i < REQUISICOES; i++) {
            long alvo = (long) i * INTERVALO_MS;
            long espera = alvo - agoraMs();
            if (espera > 0) {
                Thread.sleep(espera);
            }
            fila.add(new Pedido(i, alvo));
        }
        for (int i = 0; i < THREADS; i++) {
            fila.add(fim);
        }
        for (Thread w : workers) {
            w.join();
        }
        long totalMs = agoraMs();

        List<Long> lat = new ArrayList<>();
        int erros = 0, recusadas = 0, recusadasPosFalha = 0;
        long voltaMs = -1;
        long voltaRespostaMs = -1;
        List<Resultado> ordenados = new ArrayList<>(resultados);
        ordenados.sort((a, b) -> Long.compare(a.chegadaMs(), b.chegadaMs()));
        for (Resultado r : ordenados) {
            lat.add(r.latenciaMs());
            if (!r.ok()) erros++;
            if (r.recusada()) {
                recusadas++;
                if (r.chegadaMs() >= FALHA_ATE_MS) recusadasPosFalha++;
            }
            if (voltaMs < 0 && r.chegadaMs() >= FALHA_ATE_MS && r.ok() && r.latenciaMs() <= NORMAL_LIMITE_MS) {
                voltaMs = r.chegadaMs() - FALHA_ATE_MS;
                voltaRespostaMs = voltaMs + r.latenciaMs();
            }
        }
        Collections.sort(lat);
        long mediana = lat.get(lat.size() / 2);
        long p99 = lat.get((int) Math.ceil(lat.size() * 0.99) - 1);
        System.out.printf(Locale.ROOT,
                "modo=%s mediana_ms=%d p99_ms=%d chamadas_na_falha=%d erros=%d recusadas=%d recusadas_pos_falha=%d volta_ms=%d volta_resposta_ms=%d total_ms=%d%n",
                modo, mediana, p99, chamadasNaFalha.get(), erros, recusadas, recusadasPosFalha, voltaMs, voltaRespostaMs, totalMs);
    }
}
