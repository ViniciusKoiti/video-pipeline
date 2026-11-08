// Demo do Short "Idempotência em Java" (série "eu medi"). Só JDK, sem rede e sem banco: memória apenas.
// Uso: java Demo.java sem-chave | java Demo.java com-chave
//
// Um cliente manda 10 mil pagamentos. Cada resposta do servidor se perde na volta com probabilidade PERDA
// (sorteio com semente fixa). Quando se perde, o cliente tenta de novo. Sem chave, cada tentativa vira uma
// cobrança nova. Com chave, o servidor guarda o resultado da primeira execução e o devolve nas repetições.
// O sorteio consome um número por tentativa nos dois modos, então as tentativas são iguais nos dois casos.
import java.util.HashMap;
import java.util.Map;
import java.util.Random;

public class Demo {
    static final int PAGAMENTOS = 10_000;
    static final double PERDA = 0.30;     // parâmetro da simulação (não é medida da rede)
    static final int MAX_TENTATIVAS = 10;
    static final long SEMENTE = 42L;

    record Resposta(long cobrancaId) {}

    static final class Banco {
        long cobrancas = 0;
        final Map<String, Resposta> chaves = new HashMap<>();

        Resposta cobrar(String chave) {
            if (chave == null) {                      // sem chave: toda tentativa é uma cobrança nova
                return new Resposta(++cobrancas);
            }
            Resposta guardada = chaves.get(chave);    // com chave: repetição devolve o resultado guardado
            if (guardada != null) {
                return guardada;
            }
            Resposta nova = new Resposta(++cobrancas);
            chaves.put(chave, nova);
            return nova;
        }
    }

    public static void main(String[] args) {
        String modo = args.length > 0 ? args[0] : "sem-chave";
        boolean comChave = switch (modo) {
            case "sem-chave" -> false;
            case "com-chave" -> true;
            default -> throw new IllegalArgumentException("modo: sem-chave ou com-chave");
        };

        Random sorteio = new Random(SEMENTE);
        Banco banco = new Banco();
        long pedidos = 0;
        long inicio = System.nanoTime();
        for (int i = 0; i < PAGAMENTOS; i++) {
            String chave = comChave ? "pag-" + i : null;
            boolean recebido = false;
            int tentativas = 0;
            while (!recebido && tentativas < MAX_TENTATIVAS) {
                tentativas++;
                pedidos++;
                banco.cobrar(chave);
                recebido = sorteio.nextDouble() >= PERDA;   // a resposta chegou ou se perdeu na volta
            }
        }
        long fim = System.nanoTime();

        long duplicadas = banco.cobrancas - PAGAMENTOS;
        double usPorPedido = (fim - inicio) / 1_000.0 / pedidos;
        System.out.printf(
            "modo=%s pagamentos=%d pedidos=%d cobrancas=%d duplicadas=%d chaves_guardadas=%d us_por_pedido=%.4f%n",
            modo, PAGAMENTOS, pedidos, banco.cobrancas, duplicadas, banco.chaves.size(), usPorPedido);
    }
}
