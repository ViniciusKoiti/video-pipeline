# S03 (colunas), S18 (corte alto), S19, S20 e a porta com as duas chaves (S01 e S24), notas de 2026-11-09

Código: `video/src/previews/mec-fechadura-pt/`. Linhas do tempo em `linhaDoTempoResto.ts` e `entrada.ts` (entrada da chave, compartilhada com a S17); desenhos novos em `colunaVista.tsx` (S19) e `portaVista.tsx` (porta);
`tempos-resto.json`; conferência em `check-resto.mjs`. Composições em `index.tsx`: `FechaduraS03Colunas` (161 frames), `FechaduraS18Alta` (157), `FechaduraS19` (199 = 6,64 s), `FechaduraS20` (212 = 7,08 s),
`FechaduraPortaS01` (336 = 11,20 s) e `FechaduraPortaS24` (184). 1280×720 a 30 fps. Sem commit. **Só quadros; nenhum vídeo.**

Quadros (`s03-`, `s18a-`, `s19-`, `s20-`, `porta01-`, `porta24-` + número do frame): S03 20, 70, 120, 160; S18 30, 90, 156; S19 25, 65, 100, 125, 198; S20 20, 90, 130, 160, 211; porta S01 30, 120, 150, 215, 260, 335;
porta S24 60, 110, 150, 183.

## O que o `check-resto.mjs` confere
- **S03:** em repouso, sem chave e sem rótulos; os pinos superiores atravessam a linha nas cinco colunas.
- **S18:** a chave de cortes rasos tem colunas 3 e 5 passando da linha e as outras alinhadas; o rotor não está livre; **a tela não destaca nenhum pino** (nenhum contorno vermelho); a seta do rotor aparece cortada no fim.
- **S19:** com o corte certo o topo do pino de chave fica na linha; com o raso passa 34 px dela; o segundo pino entra antes de a chave subir demais; o "X" só existe com a chave alta; ao fim a linha fica livre.
- **S20:** a chave só sai (nunca volta), as setas de força só aparecem depois de ela sair, e ao fim os pinos superiores voltam a atravessar a linha.
- **Porta:** a chave só gira com a ponta na fechadura; o trinco só recolhe com a chave certa girada; a errada balança no máximo 7° e para; as duas nunca estão na fechadura juntas; na S01 a errada vem depois, na reprise
  da S24 a errada entra antes da certa; a S01 termina com as duas chaves lado a lado e a porta trancada; a reprise termina com a certa girada e o trinco recolhido.
- Tempo = voz (S19, S20, S01) e frações da cena pela âncora (S03 e S18: 0,45; S24: 0,55; estimativas pela posição das palavras).

## Mudança que atingiu clipes anteriores
A ponta da chave agora começa e termina em x = −40 (antes 0): deixava um traço branco na borda do quadro. Mudou em `linhaDoTempo.ts` (S04 em diante), `entrada.ts` (S17, S18) e na saída da S20. `check.mjs` e `check-errada.mjs`
foram ajustados e passam; os quadros `clipe/q-0060`, `clipe-errada/q-0030` foram renderizados de novo (os demais quadros antigos têm o traço de 1 px na borda e só serão refeitos no render final).

## Escolhas minhas que as fontes ou o plano não dão
1. **S18, 1.ª parte:** o plano diz "um corte alto demais"; usei dois (colunas 3 e 5) para o efeito ficar legível. Nenhum pino é destacado, como o plano manda.
2. **S19, abstração:** em vez de a chave subir, o corte sob a coluna fica raso (a lâmina sem corte), que é o que "chave alta demais" faz no desenho da S18. A tranca egípcia entra como quadro à esquerda ("Egito: um pino por posição").
3. **Porta, pictograma:** a chave gira em torno da própria ponta; chave certa amarela, errada em cinza-azulado, cortes diferentes; o trinco da porta é um bloco que sai da borda e recolhe 36 px. Sem rótulos e sem pessoa, como o plano.
   Forma da chave e posição da fechadura são ilustrativas.
4. **S20:** reaproveita o `Desenho` com a chave certa saindo (a chave errada ou nenhuma chave dão o mesmo estado final); pulsos nos furos do rotor e nos pinos superiores.
5. **Fora destes clipes:** `keyword` e `number` da S01/S17 (planos do template), a S21 (`network` do template), S22 (tubular e dimple), S23 (espaçador e duas chaves), V2.17 da S24 (pode reaproveitar o clipe da S14 com os rótulos
   Rotor, Came e Mecanismo da trava) e a explosão da S25.

## Para reproduzir um quadro
`cd video && TMPDIR=<pasta em data/cache/remotion-tmp> npx remotion still src/previews/mec-fechadura-pt/index.tsx <Composição> <saida.png> --frame=N`
(pasta temporária de teste: `data/cache/remotion-tmp/piloto-fechadura-3`, a apagar quando quiser).

---

# Segunda rodada, 2026-11-09: S22, S23, S24 (V2.17) e S25

Composições em `index.tsx`: `FechaduraS22` (277 frames = 9,24 s), `FechaduraS23` (487 = 16,24 s), `FechaduraS24B` (151, 2.ª parte da S24, pela âncora 0,55) e `FechaduraS25` (234 = 7,80 s). Desenhos novos:
`variasVista.tsx` (S22); `colunaVista.tsx` ganhou o espaçador (S23); `Desenho` ganhou `explodir` e `semLinha` (S25); linhas do tempo em `linhaDoTempoResto.ts`; testes em `check-resto.mjs`.
Quadros: `s22-` 10, 60, 100, 150, 215, 276; `s23-` 30, 100, 160, 215, 330, 420, 486; `s24b-` 30, 80, 120, 150; `s25-` 0, 60, 110, 160, 233.

## O que os testes conferem
- **S22:** a vista principal encolhe antes de os painéis abrirem; a chave tubular só entra com o painel aberto; os pinos da dimple só avançam depois da chave; "Tubular" vem antes de "Dimple", como na fala.
- **S23:** com a 1.ª chave a junção pino de chave/espaçador fica na linha de corte; com a 2.ª (corte mais fundo, 450) a junção espaçador/pino superior é que fica; a mola nunca some; ordem: espaçador, segunda linha, troca de chave;
  o pulso de junção só ocorre com a coluna alinhada.
- **S24 (V2.17):** a ponta da alavanca a 90° toca o bloco; o bloco só acende depois (≥ 87°); rótulos Rotor, Came e Mecanismo da trava (sem Carcaça nem Chave).
- **S25:** as peças começam no lugar; nenhuma passa do deslocamento previsto; com a redução de 0,72 em torno de (640, 395) tudo cabe no quadro em todos os instantes; a chave fica bem fora (x = −600), porque x = −40 voltava ao quadro com a redução.

## Escolhas minhas que as fontes ou o plano não dão
1. **S22, tubular:** só afirmo o canal redondo e a chave tubular (anel com entalhes na borda); não há contagem de pinos. As posições dos entalhes são ilustrativas. **Dimple:** corte transversal da lâmina com entalhes nas duas laterais e pinos
   entrando por cada lado; quantidade e posição dos entalhes são ilustrativas (F31 só diz que os cortes ficam na lateral).
2. **S23, "duas linhas de corte":** na coluna, as duas junções (pino de chave/espaçador e espaçador/pino superior) aparecem tracejadas; uma delas coincide com a linha de corte real (a borda do rotor) conforme a chave. As duas chaves são
   mostradas pelo corte da lâmina que muda de profundidade sob a coluna (410 e 450), não por duas chaves inteiras entrando na fechadura de cinco colunas. Só uma coluna é mostrada ("algumas câmaras", como o plano).
3. **S24 (V2.17):** reaproveita o desenho do came da S14, sem a volta de vista; é a mesma animação, com rótulos diferentes.
4. **S25:** a vista explodida usa os grupos de peças do desenho (carcaça de cima, rotor, carcaça de baixo, molas, pinos superiores, pinos de chave); a chave não aparece; sem a linha de corte; as peças balançam de leve depois de se afastar.

## O que falta animar
Nada do plano de animação: os 37 planos `broll` do `scenes.json` têm composição (ver `data/episodes/mec-fechadura-pt/plano-de-clipes.md`). Os planos `keyword`, `number`, `stamp`, `compare`, `network` e os rodapés de fonte são do template.
Falta registrar os clipes como ativos (decisão A do plano de clipes), a trilha (decisão do dono) e o render em vídeo, que depende da autorização do dono.

---

# Terceira rodada, 2026-11-09: S02 (V2.0 e V2.0b) e S21 (V2.16)

- **S02, `FechaduraS02` (205 frames = 6,84 s):** o contorno de uma fechadura (carcaça, entrada da chave, eixo) se desenha só em traço; em "a gente corta uma ao meio" (62% da fala) uma linha de corte tracejada o percorre da esquerda
  para a direita e, atrás dela, aparece a vista em corte em repouso, sem rótulos e sem linha de corte. Quadros `s02-0040, 0100, 0140, 0165, 0204`. O contorno exterior é desenho meu (nenhuma ficha o descreve).
- **S21, `FechaduraS21A` (86 frames = 0–20% da S21):** a vista em corte de volta, em repouso, com a chave inteira; pinos, molas e câmaras esmaecem e a chave ganha contorno branco. Quadros `s21a-0000, 0030, 0055, 0085`.
- **Correção:** na rodada anterior escrevi que só faltava a V2.16; faltavam também a V2.0 e a V2.0b da S02. O cruzamento dos 37 planos `broll` com as composições, feito para o plano de clipes, achou a lacuna.
- Testes: `check-resto.mjs` cobre as duas (a S02 só corta depois de o contorno terminar, a linha só aparece na fala certa, a S21 não leva rótulos e a chave está inteira com o rotor livre).
