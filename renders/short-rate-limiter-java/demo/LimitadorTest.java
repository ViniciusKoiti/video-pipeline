/**
 * Teste deterministico do token bucket do Demo, com relogio falso (sem sleep).
 * Uso: java -cp classes LimitadorTest
 */
public class LimitadorTest {
    static long agoraNs = 0;

    static void confere(boolean condicao, String mensagem) {
        if (!condicao) {
            throw new AssertionError(mensagem);
        }
        System.out.println("ok: " + mensagem);
    }

    public static void main(String[] args) {
        Demo.TokenBucket balde = new Demo.TokenBucket(100, 20.0, () -> agoraNs);
        int passaram = 0;
        for (int i = 0; i < 100; i++) {
            if (balde.tentaGastar()) passaram++;
        }
        confere(passaram == 100, "as primeiras 100 requisicoes seguidas passam (balde cheio)");
        confere(!balde.tentaGastar(), "a 101a requisicao seguida e recusada");

        agoraNs += 49_000_000L;
        confere(!balde.tentaGastar(), "49 ms depois (0,98 ficha) ainda recusa");
        agoraNs += 1_000_000L;
        confere(balde.tentaGastar(), "50 ms depois (1 ficha a 20 por segundo) uma passa");
        confere(!balde.tentaGastar(), "e a seguinte, sem ficha, recusa");

        agoraNs += 60_000_000_000L;
        int depoisDeParado = 0;
        for (int i = 0; i < 150; i++) {
            if (balde.tentaGastar()) depoisDeParado++;
        }
        confere(depoisDeParado == 100, "apos 60 s parado o balde enche so ate a capacidade: 100, nao 1200");

        Demo.Limitador limitador = new Demo.Limitador();
        int robo = 0;
        for (int i = 0; i < 150; i++) {
            if (limitador.permite("robo")) robo++;
        }
        confere(robo >= 100 && robo <= 101, "o robo esgota o proprio balde (100, no maximo 101 com o relogio real)");
        confere(limitador.permite("cliente-0"), "o balde de outro cliente nao e afetado");
        System.out.println("LimitadorTest COMPLETO");
    }
}
