// A toy "vault": asks for a password and compares it with one stored under XOR.
// Built to be reversed on video: the password is not stored as text.
#include <stdio.h>
#include <string.h>

static const unsigned char stored[] = {0x3b, 0x2a, 0x27, 0x2a, 0x2f, 0x22, 0x25, 0x24, 0x79, 0x7b};
static const unsigned char key = 0x4b;

int check(const char *attempt) {
    if (strlen(attempt) != sizeof stored) return 0;
    for (size_t i = 0; i < sizeof stored; i++) {
        if ((attempt[i] ^ key) != stored[i]) return 0;
    }
    return 1;
}

int main(void) {
    char attempt[64];
    printf("Password: ");
    if (!fgets(attempt, sizeof attempt, stdin)) return 1;
    attempt[strcspn(attempt, "\n")] = '\0';
    if (check(attempt)) {
        puts("Vault open.");
        return 0;
    }
    puts("Wrong password.");
    return 1;
}
