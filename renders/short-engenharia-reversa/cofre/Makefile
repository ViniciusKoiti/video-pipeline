# Os dois cofres do Short "Engenharia reversa com o Claude: a senha estava no binário".
CFLAGS = -O1 -fno-inline -no-pie

all: cofre vault

cofre: cofre.c
	gcc $(CFLAGS) -o $@ $<

vault: vault.c
	gcc $(CFLAGS) -o $@ $<

clean:
	rm -f cofre vault
