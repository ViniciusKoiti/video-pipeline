import java.util.concurrent.atomic.AtomicLong;

/** Interleavings controlados por chamadas aninhadas; sem sleep ou relogio real. */
public class BreakerTest {
    static void falha(Demo.Breaker breaker) throws Exception {
        try {
            breaker.chama(() -> { throw new Exception("falha simulada"); });
            throw new AssertionError("deveria falhar");
        } catch (Demo.CircuitoAberto e) {
            throw new AssertionError("deveria chamar a dependencia", e);
        } catch (Exception expected) {
            if (!expected.getMessage().equals("falha simulada")) throw expected;
        }
    }

    static void abre(Demo.Breaker breaker) throws Exception {
        for (int i = 0; i < Demo.FALHAS_PARA_ABRIR; i++) falha(breaker);
    }

    static void recusa(Demo.Breaker breaker) throws Exception {
        try {
            breaker.chama(() -> { throw new AssertionError("dependencia nao deveria executar"); });
            throw new AssertionError("deveria recusar");
        } catch (Demo.CircuitoAberto expected) {
            // Recusa antes da dependencia.
        }
    }

    public static void main(String[] args) throws Exception {
        AtomicLong tempo = new AtomicLong();
        Demo.Breaker b = new Demo.Breaker(tempo::get);
        abre(b);
        tempo.set(1999);
        recusa(b);
        tempo.set(2000);
        b.chama(() -> recusa(b)); // Uma unica sonda; sucesso fecha.
        b.chama(() -> {});
        System.out.println("PASS limiar, fronteira 1999/2000, sonda unica e fechamento");

        tempo.set(0);
        Demo.Breaker antigaFalha = new Demo.Breaker(tempo::get);
        try {
            antigaFalha.chama(() -> {
                abre(antigaFalha);
                tempo.set(1000);
                throw new Exception("antiga");
            });
        } catch (Exception expected) {
            if (!expected.getMessage().equals("antiga")) throw expected;
        }
        tempo.set(2000);
        antigaFalha.chama(() -> {});
        System.out.println("PASS falha antiga nao reinicia janela aberta");

        tempo.set(0);
        Demo.Breaker antigoSucesso = new Demo.Breaker(tempo::get);
        antigoSucesso.chama(() -> abre(antigoSucesso));
        recusa(antigoSucesso);
        System.out.println("PASS sucesso antigo nao fecha circuito aberto");

        tempo.set(2000);
        falha(antigoSucesso); // Falha da sonda abre nova janela integral.
        tempo.set(3999);
        recusa(antigoSucesso);
        tempo.set(4000);
        antigoSucesso.chama(() -> {});
        System.out.println("PASS falha da sonda reabre por 2000 ms");

        tempo.set(0);
        Demo.Breaker entreGeracoes = new Demo.Breaker(tempo::get);
        entreGeracoes.chama(() -> {
            abre(entreGeracoes);
            tempo.set(2000);
            entreGeracoes.chama(() -> {});
            for (int i = 0; i < 4; i++) falha(entreGeracoes);
        }); // Sucesso antigo nao zera as quatro falhas da nova geracao.
        falha(entreGeracoes);
        recusa(entreGeracoes);
        System.out.println("PASS sucesso antigo nao zera falhas da nova geracao");

        Demo.Breaker reset = new Demo.Breaker(tempo::get);
        for (int i = 0; i < 4; i++) falha(reset);
        reset.chama(() -> {});
        for (int i = 0; i < 4; i++) falha(reset);
        reset.chama(() -> {});
        System.out.println("PASS sucesso atual zera falhas consecutivas");
        System.out.println("testes=6 status=PASS relogio=controlado sleep=0");
    }
}
