# Pauta: "Engenharia reversa, visualmente" (Short para @baixo.nivel.dev.s), 2026-10-25

Pedido do dono: mostrar visualmente como é feita a engenharia reversa. Pauta para validação antes de qualquer
voz ou render (skill `shorts-tec`, passo 1). Nada renderizado.

## O que o público busca (vidIQ, 10 créditos; ficam 1.086)

| Pergunta buscada | Buscas/mês est. | Competição | Crescimento |
| --- | --- | --- | --- |
| como fazer engenharia reversa com ia | 74.828 | 40 | **+1.951%** |
| como fazer engenharia reversa | 20.646 | 41 | — |
| como fazer engenharia reversa em jogos | 9.630 | 25 | — |
| como fazer engenharia reversa com o claude | 6.594 | 25 | — |
| como fazer engenharia reversa em um .exe | 5.227 | **13** | — |

O termo "engenharia reversa" tem 94% das buscas no Brasil (+1.076% no mês). Em português, o único vídeo que
estourou no tema no último semestre é "REA: a ferramenta que está mudando a engenharia reversa" (Leonardo
Bissoli, 2,8 mil inscritos, 97 mil views, 99x), sobre uma ferramenta de IA. O público quer ver a IA fazendo.
Não há Short em pt que mostre o processo num binário de verdade: é a lacuna.

## O ângulo proposto

**"Pedi ao Claude Code para abrir um cofre sem a senha."** O cofre é um programa de 16 KB que eu escrevi
(`cofre.c`, ao lado), compilado sem símbolos de depuração; a senha não está em texto no binário. O vídeo mostra,
passo a passo e de verdade, como se chega a ela sem o código-fonte: o que o binário entrega de graça, onde ele
decide, a tabela escondida, e o XOR desfeito. Termina com o cofre aberto e a regra: só em binário seu ou de CTF.

Por que esse ângulo: casa o termo que mais cresce ("com IA", "com o Claude") com a identidade do canal ("baixo
nível"), e é honesto: o Claude Code faz isso de fato com `file`, `strings` e `objdump`, que estão na máquina.

## A demonstração, já feita e conferida (todas as saídas abaixo são reais)

- Fonte: `cofre.c`. Compilação: `gcc -O1 -fno-inline -no-pie -o cofre cofre.c` (16.232 bytes). A senha é
  `paladino20`, guardada como 10 bytes já passados por XOR com `0x4b`.
- `./cofre` com "123": `Senha: Senha errada.` Com `paladino20`: `Senha: Cofre aberto.`
- `file cofre`: `ELF 64-bit LSB executable, x86-64, dynamically linked`.
- `strings -n 6 cofre`: `Senha: `, `Cofre aberto.`, `Senha errada.`; nenhuma senha legível.
- `objdump -d -M intel cofre`, função `confere` (25 linhas, em `demo/confere.asm`); as que decidem:

```
  401208:  call   4010a0 <strlen@plt>
  401215:  cmp    rdx,0xa              ; o tamanho tem de ser 10
  401220:  lea    rsi,[rip+0xe09]      ; # 402030 <guardada>
  401244:  xor    edx,0x4b             ; cada byte da tentativa passa por XOR 0x4b
  40124b:  cmp    edx,ecx              ; e é comparado com a tabela
  40124d:  jne    401260               ; um erro e acabou
```

- `objdump -s -j .rodata cofre`, a tabela em `402030`: `3b 2a 27 2a 2f 22 25 24 79 7b` (em texto: `;*'*/"%$y{`).
- XOR desfeito com o mesmo `0x4b`: `3b→p 2a→a 27→l 2a→a 2f→d 22→i 25→n 24→o 79→2 7b→0` = `paladino20`.

Ferramentas na máquina: gcc, objdump, readelf, strings, nm, xxd. Não há gdb, radare2 nem Ghidra. O Short não
precisa deles: `strings` e `objdump` abrem este cofre.

## Plano visual, cena a cena (vertical, ~55 s, molde do Short 2: resultado → passos numerados → resultado)

| # | Batida | Painel de cima (gravação de tela) | Painel de baixo (o kit desenha, com dado real) | Fala (rascunho) |
| --- | --- | --- | --- | --- |
| 0 | capa, 3 s | — | o terminal: `Senha: ` → `Senha errada.`, e o cartão "A senha está no binário. Sem o código-fonte." | Este programa tem uma senha escondida. Eu não tenho a senha nem o código. |
| 1 | o que ele entrega, 8 s | Claude Code rodando `file` e `strings` | as três frases de `strings` entrando uma a uma; o rótulo "nenhuma senha" | Primeiro, o que o binário entrega de graça: é um executável de 64 bits, e as únicas frases dentro dele são as que ele imprime. Nenhuma senha. |
| 2 | onde ele decide, 12 s | Claude Code com o `objdump` | a listagem de `confere` como documento (`DocumentPage`): a câmera desce até `cmp rdx,0xa`, depois `xor edx,0x4b`, depois `cmp edx,ecx`, cada linha marcada | Então eu desmonto a função que confere. Ela mede o tamanho: tem de ser dez. Depois pega cada letra, faz um XOR com quatro-B, e compara com uma tabela. |
| 3 | a tabela, 8 s | o `objdump -s` | os dez bytes aparecendo em cartões: `3b 2a 27 2a 2f 22 25 24 79 7b` | A tabela está guardada no binário: dez bytes. Não são a senha. São a senha depois do XOR. |
| 4 | desfazer, 10 s | o Claude calculando | os dez cartões virando letras, um a um: `3b→p`, `2a→a`… até `paladino20` | XOR se desfaz com o mesmo XOR. Cada byte com quatro-B vira uma letra. P, a, l, a, d, i, n, o, dois, zero. |
| 5 | abrir, 5 s | o terminal: `paladino20` → `Cofre aberto.` | o mesmo terminal grande, com o resultado | Paladino vinte. Cofre aberto. |
| 6 | fecho, 6 s | — | o dono grande, falando; cartão final | Engenharia reversa é ler o que o compilador deixou. Só em binário seu, ou de CTF. Código e binário na descrição. |

O dono fica na janela flutuante das batidas 1 a 5, com a boca no envelope da voz. Peças do kit: `HookCard`,
`DocumentPage` (listagem com câmera e trecho marcado), `TerminalText`, cartões de byte (os mesmos `Chips` e
cartões do Short 2), `FloatingWindow` + `Host` com a pele do dono, `EndCta`. Tudo que aparece na tela é saída
real dos comandos acima; o painel de cima é gravação de tela real do Claude Code fazendo a análise (o dono
grava; até lá, espaço marcado como no Short 2).

## O que é real e o que falta

Real: o binário, as saídas, a senha. Falta: a gravação de tela do Claude Code (o dono pede ao agente, numa sessão
nova na pasta `demo/`, "abra este cofre sem a senha", e grava); a voz; os renders. Divulgação: voz clonada e
apresentador desenhado, como nos outros. Ética: o binário é do dono e o vídeo diz "só em binário seu ou de CTF".

## Títulos para pontuar no vidIQ depois da validação

- Pedi ao Claude Code para abrir um cofre sem a senha
- Engenharia reversa com o Claude: a senha estava no binário
- Como achar uma senha escondida num binário, sem o código-fonte

Hipótese (H01 do canal): o molde "resultado → passos numerados → resultado", no termo "engenharia reversa com
IA", retém mais de 60% e traz os primeiros inscritos do canal (hoje 0). Medida: retenção média e inscritos aos
7 e 28 dias no Studio.

## Decisões do dono (2026-10-25) e produção

Ângulo: o Claude Code fazendo. Idiomas: os dois. Sem gdb. E, no lugar da gravação de tela, o painel de cima mostra
um **terminal com os comandos e as saídas reais sendo digitados** ("tela dividida; tranquilo nesse caso"): o
vídeo fica completo sem gravação, e nada na tela é inventado. Se o dono gravar a sessão do Claude Code depois,
o nome do arquivo entra em `recordings` e o painel passa a ser a gravação.

| Versão | Arquivo | Duração | Volume | Título (vidIQ) |
| --- | --- | --- | --- | --- |
| pt-BR | `cofre-pt-voz.mp4` | 55,6 s | −15,3 LUFS | Engenharia reversa com o Claude: a senha estava no binário (89) |
| en | `cofre-en-voz.mp4` | 57,0 s | −15,2 LUFS | I asked Claude Code to open a vault without the password (88) |

Composição `Cofre` no kit (`examples/divulgacao/CofreDemo.tsx`, MR !37), com as peças compartilhadas em
`pieces.tsx`; dados em `data/episodes/short-engenharia-reversa/` (`cofre.pt.json`, `cofre.en.json`, voz em
`voice/`, binários e saídas em `demo/`). Os fontes `cofre.c` e `vault.c` estão nesta pasta para o link da
descrição; posts em `posts/`. Bug corrigido no caminho: o nome do WAV não tinha o idioma, e gerar a voz em inglês
apagava as falas em português da mesma cena; o nome agora é `<cena>-<provedor>-<idioma>-<hash>.wav`.

## Pendências antes de publicar

A escuta e a leitura do dono nas duas línguas; o link público do código e do binário; a pele do apresentador fora
de `needs_review`; a marcação de conteúdo sintético no Studio. Variante `.exe` (competição 13) com o mesmo cofre
pelo MinGW: um segundo Short.

## As três decisões, como foram feitas

1. **Ângulo:** o Claude Code fazendo (o termo que cresce 1.951%) ou você fazendo à mão (a identidade "baixo nível")?
   Recomendo o Claude Code, com você narrando o que ele faz.
2. **Idioma:** pt-BR primeiro (94% das buscas), inglês depois com a mesma voz? Recomendo sim.
3. **Profundidade:** fica em `strings` e `objdump` (abrem o cofre em 55 s) ou entra o gdb com um breakpoint
   (precisa de `sudo apt install gdb` e mais 10 s)? Recomendo sem gdb nesta versão; o `.exe` do Windows, que tem
   competição 13, fica para um segundo Short com o mesmo cofre compilado pelo MinGW.
