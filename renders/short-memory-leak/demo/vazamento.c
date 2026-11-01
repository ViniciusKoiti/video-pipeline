/* Memory leak ao vivo (pauta 1 da série "eu medi", 2026-11-07).
 *
 * A cada milissegundo aloca um bloco de 64 KB e escreve nele (sem a escrita a página nem é mapeada).
 * Sem --libera, o bloco nunca é devolvido: a memória residente (RSS) só sobe. Com --libera, o mesmo
 * bloco é devolvido logo depois, e o RSS fica parado. A cada segundo imprime o RSS lido de
 * /proc/self/statm, por 10 segundos. Nada aqui depende de otimização: a escrita no bloco é observável.
 *
 * gcc -O2 -o vazamento vazamento.c && ./vazamento [--libera]
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <unistd.h>

#define BLOCO (64 * 1024)
#define SEGUNDOS 10

static double agora(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec + ts.tv_nsec / 1e9;
}

static double rss_mb(void) {
    long paginas = 0, residentes = 0;
    FILE *f = fopen("/proc/self/statm", "r");
    if (!f || fscanf(f, "%ld %ld", &paginas, &residentes) != 2) {
        if (f) fclose(f);
        return -1;
    }
    fclose(f);
    return residentes * (double)sysconf(_SC_PAGESIZE) / (1024.0 * 1024.0);
}

int main(int argc, char **argv) {
    int libera = argc > 1 && strcmp(argv[1], "--libera") == 0;
    double inicio = agora();
    int proximo = 1;
    long iteracoes = 0;
    printf("versao=%s bloco_kb=%d rss_inicial_mb=%.1f\n", libera ? "libera" : "vaza", BLOCO / 1024, rss_mb());
    while (1) {
        double t = agora() - inicio;
        if (t >= SEGUNDOS) break;
        char *p = malloc(BLOCO);
        if (!p) {
            printf("malloc falhou em t=%.1fs\n", t);
            return 1;
        }
        memset(p, (int)(iteracoes & 0xff), BLOCO);
        if (libera) free(p);
        iteracoes++;
        if (t >= proximo) {
            printf("t=%ds rss_mb=%.1f iteracoes=%ld\n", proximo, rss_mb(), iteracoes);
            proximo++;
        }
        struct timespec pausa = {0, 1000000L};
        nanosleep(&pausa, NULL);
    }
    printf("t=%ds rss_mb=%.1f iteracoes=%ld fim\n", SEGUNDOS, rss_mb(), iteracoes);
    return 0;
}
