# Posts do Short "o cofre" (engenharia reversa com o Claude Code), 2026-10-25

Rascunhos no formato do Postiz para o YouTube @baixo.nivel.dev.s (`cmr030qdh000glw83on440hxi`), pt e en, cadeia da ADR 025. Lacunas
de propósito: `date`, `image` e `[LINK]` (onde o dono publicar `cofre.c`, `vault.c` e os binários: um snippet
público do GitLab ou uma pasta num repositório aberto; os fontes estão em `../cofre.c` e `../vault.c`).

Títulos pontuados pelo vidIQ no canal (20 créditos): pt "Engenharia reversa com o Claude: a senha estava no
binário" **89** e "Pedi ao Claude Code para abrir um cofre sem a senha" 85; en "I asked Claude Code to open a
vault without the password" **88** e "Reverse engineering with Claude Code: the password was in the binary" 86.

Antes de agendar: a gravação de tela do Claude Code fazendo a análise (hoje, espaço marcado), a escuta do dono,
o link do código, a pele do apresentador fora de `needs_review`, e a marcação de conteúdo sintético no Studio.

## Agendamento pedido pelo dono (2026-10-25, 17h19): "coloque uma postagem"

Decisão registrada: o Short do cofre **em inglês** no YouTube @baixo.nivel.dev.s (o canal publica em inglês e o
dono pediu antes a versão em inglês lá), em `baixo-nivel/post-shorts-en.json`, para **25/10/2026 às 19h30 de
Brasília** (duas horas de folga para desfazer). Mídia já no Postiz: id `c4315948-691f-4cba-8782-c45d72a4ab53`,
`renders/short-engenharia-reversa/cofre-en-voz.mp4` (57,0 s, −15,2 LUFS). A versão em português vai depois,
no mesmo canal ou no pessoal, à escolha do dono.

O que falta para o `pacote` e a dúvida cega passarem:

1. **O link do código.** A tela e a fala dizem "code and binary in the description". A tentativa de publicar
   `vault.c` como snippet público do GitLab foi barrada pela permissão desta sessão (upload público). O dono cria
   com um comando, na pasta `renders/short-engenharia-reversa/`:

   ```
   glab snippet create vault.c --personal --visibility public --title "vault.c: the toy vault opened without the password" --filename vault.c --description "Build: gcc -O1 -fno-inline -no-pie -o vault vault.c. Only reverse binaries you own or CTF ones. MIT."
   ```

   e cola a URL no lugar de `[LINK]` no JSON. Ou abre o repositório e aponta para a pasta.
2. **A escuta do dono** da versão em inglês (o gate 4 deste vídeo; a dúvida cega procura o registro).
3. **A pele do apresentador** fora de `needs_review`: o gerador que fez a folha a partir das fotos.

Com o link no JSON, a cadeia segue em um comando de cada: `pacote`, dúvida cega, `duvida`, `schedule` (que pede
a confirmação do dono). O pacote do teaser no mesmo canal continua com parecer "não segue" pelos mesmos motivos.

**Link resolvido (2026-10-25, 17h40):** o dono pediu que eu criasse o repositório; `gh` logado como ViniciusKoiti
criou e publicou `https://github.com/ViniciusKoiti/baixo-nivel-demos` (público, MIT) com `cofre.c`, `vault.c`,
`Makefile`, os dois binários do vídeo e `SHA256SUMS`. A descrição aponta para `https://github.com/ViniciusKoiti/baixo-nivel-demos/tree/main/cofre`. Lacunas que ficam para o
dono: a escuta da versão em inglês e o gerador da pele do apresentador.

## Gates no auto-play (2026-10-25, 18h)

O dono pediu que as decisões ficassem documentadas no auto-play, como nos episódios. `shorts_tec.py gate` montou
`data/episodes/short-engenharia-reversa-en/` com `renders/final.mp4` (o `cofre-en-voz.mp4`, 57,0 s) e
`legenda-post.txt` (título e legenda do post). `vp status short-engenharia-reversa-en` mostra o gate 4 (`preview`)
sem decisão. O carimbo é do dono, depois de assistir:

```
.venv/bin/vp approve short-engenharia-reversa-en --step preview --notes "assisti ao cofre-en-voz.mp4"
```

Isso grava a aprovação em `data/episodes/short-engenharia-reversa-en/review.json` com o hash do MP4 e da legenda.
Depois, o pacote é refeito com `--episode short-engenharia-reversa-en`, que passa a dizer "gate 4: aprovado", e a
dúvida cega lê isso em vez de um README. A pele do apresentador segue em `needs_review` até o dono informar o
gerador da folha (vai no `origem.json` da pele, em `data/episodes/teaser-motion-kit/public/sprites/dono/`).
