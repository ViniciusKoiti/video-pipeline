// Soma os quadrados de 1 a n. Pequeno de propósito: cabe numa tela de Short.
unsigned long soma_quadrados(unsigned int n) {
    unsigned long total = 0;
    for (unsigned int i = 1; i <= n; i++) {
        total += (unsigned long)i * i;
    }
    return total;
}
