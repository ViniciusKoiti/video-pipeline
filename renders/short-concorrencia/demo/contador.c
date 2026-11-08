/* Concorrência ao vivo (pauta 2 da série "eu medi", 2026-11-14).
 *
 * Dois threads somam 1.000.000 vezes cada no mesmo contador (esperado: 2.000.000).
 * Três versões: sem proteção (contador volatile, para o compilador não juntar o laço numa soma só),
 * com mutex e com atomic. Imprime o total e o tempo da rodada em milissegundos.
 *
 * gcc -O2 -pthread -o contador contador.c && ./contador [--mutex|--atomic]
 */
#include <pthread.h>
#include <stdatomic.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

#define VOLTAS 1000000L

static volatile long sem_protecao = 0;
static long com_mutex = 0;
static atomic_long com_atomic = 0;
static pthread_mutex_t trava = PTHREAD_MUTEX_INITIALIZER;
static int modo = 0; /* 0 sem protecao, 1 mutex, 2 atomic */

static double agora(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1e3 + ts.tv_nsec / 1e6;
}

static void *soma(void *arg) {
    (void)arg;
    for (long i = 0; i < VOLTAS; i++) {
        if (modo == 0) {
            sem_protecao = sem_protecao + 1;
        } else if (modo == 1) {
            pthread_mutex_lock(&trava);
            com_mutex = com_mutex + 1;
            pthread_mutex_unlock(&trava);
        } else {
            atomic_fetch_add(&com_atomic, 1);
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    if (argc > 1 && strcmp(argv[1], "--mutex") == 0) modo = 1;
    if (argc > 1 && strcmp(argv[1], "--atomic") == 0) modo = 2;
    pthread_t a, b;
    double inicio = agora();
    pthread_create(&a, NULL, soma, NULL);
    pthread_create(&b, NULL, soma, NULL);
    pthread_join(a, NULL);
    pthread_join(b, NULL);
    double ms = agora() - inicio;
    long total = modo == 0 ? sem_protecao : modo == 1 ? com_mutex : atomic_load(&com_atomic);
    printf("versao=%s total=%ld esperado=%ld ms=%.1f\n", modo == 0 ? "sem" : modo == 1 ? "mutex" : "atomic", total,
           2 * VOLTAS, ms);
    return 0;
}
