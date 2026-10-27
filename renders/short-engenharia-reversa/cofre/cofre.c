// Um "cofre" de brinquedo: pede uma senha e compara com uma senha guardada com XOR.
// Feito para ser invertido no vídeo: a senha não aparece em texto no binário.
#include <stdio.h>
#include <string.h>

static const unsigned char guardada[] = {0x3b, 0x2a, 0x27, 0x2a, 0x2f, 0x22, 0x25, 0x24, 0x79, 0x7b};
static const unsigned char chave = 0x4b;

int confere(const char *tentativa) {
    if (strlen(tentativa) != sizeof guardada) return 0;
    for (size_t i = 0; i < sizeof guardada; i++) {
        if ((tentativa[i] ^ chave) != guardada[i]) return 0;
    }
    return 1;
}

int main(void) {
    char tentativa[64];
    printf("Senha: ");
    if (!fgets(tentativa, sizeof tentativa, stdin)) return 1;
    tentativa[strcspn(tentativa, "\n")] = '\0';
    if (confere(tentativa)) {
        puts("Cofre aberto.");
        return 0;
    }
    puts("Senha errada.");
    return 1;
}
