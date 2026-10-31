// Percorre a mesma lista ligada de dois jeitos: nós encadeados na ordem da memória e em ordem embaralhada.
// Mesmos nós, mesmos valores, mesma soma; só muda a ordem em que o ponteiro `next` leva de um nó ao outro.
#include <stdio.h>
#include <stdlib.h>
#include <time.h>

typedef struct No { struct No *next; unsigned long valor; } No;

static double agora(void) {
    struct timespec t;
    clock_gettime(CLOCK_MONOTONIC, &t);
    return t.tv_sec + t.tv_nsec / 1e9;
}

static int cmp(const void *a, const void *b) {
    double x = *(const double *)a, y = *(const double *)b;
    return (x > y) - (x < y);
}

static unsigned long soma(const No *p) {
    unsigned long s = 0;
    for (; p; p = p->next) s += p->valor;
    return s;
}

static double mediana_ms(const No *cabeca, int reps, unsigned long *saida) {
    double t[64];
    for (int r = 0; r < reps; r++) {
        double ini = agora();
        *saida = soma(cabeca);
        t[r] = (agora() - ini) * 1e3;
    }
    qsort(t, reps, sizeof t[0], cmp);
    return t[reps / 2];
}

int main(void) {
    const size_t tamanhos[] = {1000, 100000, 1000000, 10000000};
    srand(42);
    for (int k = 0; k < 4; k++) {
        size_t n = tamanhos[k];
        No *pool = malloc(n * sizeof *pool);
        size_t *ordem = malloc(n * sizeof *ordem);
        for (size_t i = 0; i < n; i++) { pool[i].valor = i; ordem[i] = i; }

        // Lista 1: cada nó aponta para o vizinho na memória.
        for (size_t i = 0; i + 1 < n; i++) pool[i].next = &pool[i + 1];
        pool[n - 1].next = NULL;
        unsigned long s1;
        double seq = mediana_ms(&pool[0], 15, &s1);

        // Lista 2: os mesmos nós, encadeados numa permutação aleatória (Fisher-Yates).
        for (size_t i = n - 1; i > 0; i--) {
            size_t j = ((size_t)rand() * 65537u + (size_t)rand()) % (i + 1);
            size_t tmp = ordem[i]; ordem[i] = ordem[j]; ordem[j] = tmp;
        }
        for (size_t i = 0; i + 1 < n; i++) pool[ordem[i]].next = &pool[ordem[i + 1]];
        pool[ordem[n - 1]].next = NULL;
        unsigned long s2;
        double emb = mediana_ms(&pool[ordem[0]], 15, &s2);

        printf("n=%zu  sequencial=%.3f ms  embaralhada=%.3f ms  razao=%.1fx  soma_igual=%s\n",
               n, seq, emb, emb / seq, s1 == s2 ? "sim" : "NAO");
        free(pool); free(ordem);
    }
    return 0;
}
