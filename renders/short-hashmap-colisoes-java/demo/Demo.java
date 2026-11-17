// Demo do Short "HashMap e colisões em Java" (série "eu medi"). Só JDK, memória apenas.
// Uso: java Demo.java bom | fraco | constante | constante-comparable [N]
//
// Cache de sessões: a chave é um ChaveSessao(usuario, dispositivo), com N chaves diferentes. As quatro classes
// têm o mesmo equals; só o hashCode (e, no último modo, o compareTo) muda:
//   bom                  = Objects.hash(usuario, dispositivo)  (usa o estado todo)
//   fraco                = usuario % 100                        (usa parte do estado: no máximo 100 valores)
//   constante            = 42                                   (toda chave no mesmo balde)
//   constante-comparable = 42, mas a chave implementa Comparable (o Javadoc diz que o HashMap pode desempatar)
// Mede (1) o tempo de inserir as N chaves e de buscar as N chaves, depois de aquecer a JVM, e (2) em passada
// separada, sem cronômetro, quantas vezes equals() é chamado nas N buscas. Os grupos de hashCode são contados
// por código (determinístico).
import java.util.ArrayList;
import java.util.Collections;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;
import java.util.Random;

public class Demo {
    static final int N_PADRAO = 20_000;
    static final long SEMENTE = 42L;
    static long chamadasEquals = 0;

    static class Chave {
        final int usuario;
        final int dispositivo;
        final int modo; // 0 bom, 1 fraco, 2 constante

        Chave(int usuario, int dispositivo, int modo) {
            this.usuario = usuario;
            this.dispositivo = dispositivo;
            this.modo = modo;
        }

        @Override public boolean equals(Object o) {
            chamadasEquals++;
            return o instanceof Chave c && c.usuario == usuario && c.dispositivo == dispositivo;
        }

        @Override public int hashCode() {
            return switch (modo) {
                case 0 -> Objects.hash(usuario, dispositivo);
                case 1 -> usuario % 100;
                default -> 42;
            };
        }
    }

    static final class ChaveComparavel extends Chave implements Comparable<ChaveComparavel> {
        ChaveComparavel(int usuario, int dispositivo) { super(usuario, dispositivo, 2); }

        @Override public int compareTo(ChaveComparavel o) {
            int c = Integer.compare(usuario, o.usuario);
            return c != 0 ? c : Integer.compare(dispositivo, o.dispositivo);
        }
    }

    static List<Chave> chaves(String modo, int n) {
        List<Chave> lista = new ArrayList<>(n);
        for (int i = 0; i < n; i++) {
            int usuario = i / 4, dispositivo = i % 4;
            lista.add(switch (modo) {
                case "bom" -> new Chave(usuario, dispositivo, 0);
                case "fraco" -> new Chave(usuario, dispositivo, 1);
                case "constante" -> new Chave(usuario, dispositivo, 2);
                case "constante-comparable" -> new ChaveComparavel(usuario, dispositivo);
                default -> throw new IllegalArgumentException("modo: bom, fraco, constante ou constante-comparable");
            });
        }
        return lista;
    }

    static long ciclo(List<Chave> lista, List<Chave> busca) {
        Map<Chave, Integer> mapa = new HashMap<>();
        for (int i = 0; i < lista.size(); i++) mapa.put(lista.get(i), i);
        long soma = 0;
        for (Chave c : busca) soma += mapa.get(c);
        return soma;
    }

    public static void main(String[] args) {
        String modo = args.length > 0 ? args[0] : "bom";
        int n = args.length > 1 ? Integer.parseInt(args[1]) : N_PADRAO;

        // Aquecimento: mesmo código, mapa pequeno, várias vezes (a JVM compila put/get antes de medir).
        List<Chave> pequena = chaves(modo, 2_000);
        List<Chave> pequenaBusca = chaves(modo, 2_000);
        long sink = 0;
        for (int i = 0; i < 200; i++) sink += ciclo(pequena, pequenaBusca);

        List<Chave> lista = chaves(modo, n);
        // A busca usa instâncias novas e iguais às guardadas, como um cache recebe a chave de cada requisição
        // (com a mesma instância, o HashMap compara por == e nem chama equals).
        List<Chave> busca = chaves(modo, n);
        Collections.shuffle(busca, new Random(SEMENTE));

        Map<Chave, Integer> mapa = new HashMap<>();
        long t0 = System.nanoTime();
        for (int i = 0; i < n; i++) mapa.put(lista.get(i), i);
        long t1 = System.nanoTime();
        long soma = 0;
        for (Chave c : busca) soma += mapa.get(c);
        long t2 = System.nanoTime();

        // Contagem determinística (fora do cronômetro): hashCodes diferentes, maior grupo, equals por busca.
        Map<Integer, Integer> grupos = new HashMap<>();
        for (Chave c : lista) grupos.merge(c.hashCode(), 1, Integer::sum);
        int maiorGrupo = Collections.max(grupos.values());
        chamadasEquals = 0;
        for (Chave c : busca) mapa.get(c);
        double equalsPorBusca = (double) chamadasEquals / n;

        if (soma + sink == Long.MIN_VALUE) System.out.println("nunca");
        System.out.printf(java.util.Locale.ROOT,
            "modo=%s chaves=%d hashes_distintos=%d maior_grupo=%d equals_por_busca=%.2f ms_insercao=%.2f ms_busca=%.2f ns_por_busca=%.1f%n",
            modo, n, grupos.size(), maiorGrupo, equalsPorBusca,
            (t1 - t0) / 1e6, (t2 - t1) / 1e6, (double) (t2 - t1) / n);
    }
}
