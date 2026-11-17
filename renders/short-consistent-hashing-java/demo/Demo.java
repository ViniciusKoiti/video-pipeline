// Demo do Short "Consistent hashing em Java" (série "eu medi"). Só JDK, sem rede: memória apenas.
// Uso: java Demo.java modulo | java Demo.java anel 1 | java Demo.java anel 10 | java Demo.java anel 100
//
// Um cache de sessões roda em N servidores. 100 mil ids de sessão (semente fixa) vão para um servidor, e a equipe
// adiciona um servidor (4 -> 5). Mede-se:
//   - quantas chaves trocam de servidor (cada uma é uma sessão que some do cache: miss);
//   - quantas das que trocaram foram para um servidor que NÃO é o novo;
//   - a carga por servidor com 5 servidores (desvio padrão / média, e o servidor mais cheio / carga ideal).
// Módulo: servidor = hash(chave) % N.
// Anel: cada servidor ocupa PONTOS posições no círculo de 2^32 (hash de "<cluster>-srv-<i>#<v>"); a chave vai para
//       o primeiro ponto a partir de hash(chave), no sentido crescente, voltando ao início no fim (TreeMap).
// A carga do anel depende de onde os nomes caem no círculo; por isso o programa repete tudo com CLUSTERS conjuntos
// diferentes de nomes de servidor e informa a média e os extremos. O módulo não depende dos nomes.
// Hash de 32 bits: os 4 primeiros bytes do MD5 (o artigo do Dynamo usa MD5 para posicionar chaves e nós).
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Map;
import java.util.Random;
import java.util.TreeMap;

public class Demo {
    static final int CHAVES = 100_000;
    static final int ANTES = 4;
    static final int DEPOIS = 5;
    static final int CLUSTERS = 20;
    static final long SEMENTE = 42L;
    static final int PASSADAS_TEMPO = 5;

    static long hash32(String texto) {
        try {
            byte[] d = MessageDigest.getInstance("MD5").digest(texto.getBytes(StandardCharsets.UTF_8));
            return ((d[0] & 0xFFL) << 24) | ((d[1] & 0xFFL) << 16) | ((d[2] & 0xFFL) << 8) | (d[3] & 0xFFL);
        } catch (Exception e) {
            throw new IllegalStateException(e);
        }
    }

    static TreeMap<Long, Integer> anel(int cluster, int servidores, int pontos) {
        TreeMap<Long, Integer> t = new TreeMap<>();
        for (int s = 0; s < servidores; s++) {
            for (int v = 0; v < pontos; v++) {
                t.put(hash32("c" + cluster + "-srv-" + s + "#" + v), s);
            }
        }
        return t;
    }

    static int donoNoAnel(TreeMap<Long, Integer> t, long h) {
        Map.Entry<Long, Integer> e = t.ceilingEntry(h);     // primeiro ponto a partir da chave
        return (e != null ? e : t.firstEntry()).getValue(); // passou do fim: volta ao começo do círculo
    }

    public static void main(String[] args) {
        String modo = args.length > 0 ? args[0] : "modulo";
        boolean usaAnel = switch (modo) {
            case "modulo" -> false;
            case "anel" -> true;
            default -> throw new IllegalArgumentException("modo: modulo ou anel <pontos>");
        };
        int pontos = usaAnel ? Integer.parseInt(args[1]) : 0;

        Random sorteio = new Random(SEMENTE);
        long[] h = new long[CHAVES];
        for (int i = 0; i < CHAVES; i++) {
            h[i] = hash32("sess-" + Long.toHexString(sorteio.nextLong()));
        }

        int clusters = usaAnel ? CLUSTERS : 1;
        double somaMovidas = 0, minMovidas = 1e9, maxMovidas = 0;
        double somaDesvio = 0, maxDesvio = 0, somaMaxCarga = 0, somaMinCarga = 0;
        long foraDoNovo = 0;
        double nsPorBusca = 0;
        for (int c = 0; c < clusters; c++) {
            TreeMap<Long, Integer> a4 = usaAnel ? anel(c, ANTES, pontos) : null;
            TreeMap<Long, Integer> a5 = usaAnel ? anel(c, DEPOIS, pontos) : null;
            long movidas = 0;
            long[] carga = new long[DEPOIS];
            for (int i = 0; i < CHAVES; i++) {
                int antes = usaAnel ? donoNoAnel(a4, h[i]) : (int) (h[i] % ANTES);
                int depois = usaAnel ? donoNoAnel(a5, h[i]) : (int) (h[i] % DEPOIS);
                carga[depois]++;
                if (antes != depois) {
                    movidas++;
                    if (depois != DEPOIS - 1) {
                        foraDoNovo++;
                    }
                }
            }
            double ideal = (double) CHAVES / DEPOIS, media = ideal, var = 0, max = 0, min = Double.MAX_VALUE;
            for (long k : carga) {
                var += (k - media) * (k - media);
                max = Math.max(max, k);
                min = Math.min(min, k);
            }
            double desvio = Math.sqrt(var / DEPOIS) / media * 100;
            double pct = 100.0 * movidas / CHAVES;
            somaMovidas += pct; minMovidas = Math.min(minMovidas, pct); maxMovidas = Math.max(maxMovidas, pct);
            somaDesvio += desvio; maxDesvio = Math.max(maxDesvio, desvio);
            somaMaxCarga += 100.0 * max / ideal; somaMinCarga += 100.0 * min / ideal;

            if (c == 0) {   // tempo da busca do dono, com os hashes já calculados; a última passada é a medida
                long sink = 0;
                for (int p = 0; p < PASSADAS_TEMPO; p++) {
                    long t0 = System.nanoTime();
                    for (int i = 0; i < CHAVES; i++) {
                        sink += usaAnel ? donoNoAnel(a5, h[i]) : (int) (h[i] % DEPOIS);
                    }
                    nsPorBusca = (System.nanoTime() - t0) / (double) CHAVES;
                }
                if (sink < 0) {
                    System.out.println(sink);
                }
            }
        }
        System.out.printf(java.util.Locale.ROOT,
            "modo=%s pontos=%d chaves=%d clusters=%d movidas_pct=%.2f movidas_pct_min=%.2f movidas_pct_max=%.2f "
                + "fora_do_novo=%d desvio_pct=%.2f desvio_pct_max=%.2f carga_max_pct_do_ideal=%.1f "
                + "carga_min_pct_do_ideal=%.1f ns_por_busca=%.1f%n",
            modo, pontos, CHAVES, clusters, somaMovidas / clusters, minMovidas, maxMovidas, foraDoNovo,
            somaDesvio / clusters, maxDesvio, somaMaxCarga / clusters, somaMinCarga / clusters, nsPorBusca);
    }
}
