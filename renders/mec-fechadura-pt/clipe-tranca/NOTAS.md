# Chave errada (S17) e tranca egípcia (S03 e S18), notas de 2026-11-09

Código: `video/src/previews/mec-fechadura-pt/`. S17: `linhaDoTempoErrada.ts`, `tempos-errada.json`, `check-errada.mjs`, composição `FechaduraClipeErrada` (431 frames, 14,36 s = voz). Tranca: `tranca.ts` (geometria e
linhas do tempo), `trancaVista.tsx` (desenho), `check-tranca.mjs`, composições `FechaduraTrancaS03` (197 frames) e `FechaduraTrancaS18` (191 frames). 1280×720 a 30 fps. Sem commit. **Só quadros; nenhum vídeo.**
A geometria da vista lateral (`geometria.ts`) ganhou um parâmetro opcional `fundos` (cortes de outra chave); os valores padrão e o `check.mjs` não mudaram. O `Desenho` (`index.tsx`) ganhou `fundos` e `alerta`.

Quadros: `../clipe-errada/q-0030, 0120, 0215, 0270, 0330, 0430` (a chave errada entra, os pinos param nas alturas erradas, contorno vermelho nos que cruzam a linha, seta do rotor cortada);
`s03-0015, 0060, 0120, 0196` (o esquema se desenha em traço de lápis, com os rótulos Poste, Tranca, Pinos) e `s18-0005, 0045, 0080, 0105, 0150, 0190` (a chave sobe por baixo, levanta os pinos até a altura certa e a tranca recua).

## O que os testes conferem
- **S17:** a chave errada tem cortes válidos para a lâmina; com ela inteira a coluna 1 está alinhada e as outras não, 3 pinos superiores atravessam a linha e 1 pino de chave passa dela; o rotor não fica livre; o contorno
  vermelho só aparece depois de a chave entrar; a seta cortada só depois da seta do rotor; tempo = voz.
- **Tranca:** em repouso cada pino ocupa a abertura da tranca (a prende); a tranca só corre com os três pinos fora dela (subida de 100 px); a chave **para exatamente na altura certa**, então nenhum excesso é mostrado (plano:
  "sem a sequência do excesso"); o rótulo "não confere se sobe demais" entra depois de a tranca se soltar; nada da chave aparece na S03.

## Escolhas minhas que as fontes não dão
1. **S17, valores:** quais colunas ficam fundas ou rasas demais é ilustrativo. O plano pede "ao menos um pino segue atravessando a linha"; saíram 3 superiores e 1 pino de chave. A tela não diz qual trava (F23).
2. **Tranca, mecanismo:** `source-01#E5` e `source-02#E12` dizem só: poste na porta, tranca horizontal com aberturas verticais, pinos que a prendem e uma chave que os levanta até uma altura suficiente.
   O "pente" de pegs que sobe por furos do poste e os pinos repousando nas bordas desses furos são desenho meu para mostrar a subida; as fontes não descrevem a forma da chave egípcia.
3. **Tranca, recuo para a esquerda** e o poste em corte lateral são escolhas de desenho. A madeira usa cores neutras (bege e marrom) no traço de lápis, sempre com a paleta `mao`, para separar a história do mecanismo moderno.
4. **Duração dos clipes da tranca** é estimativa: o plano V1 começa na âncora ("Os princípios básicos dela" na S03, "A fechadura de madeira do Egito" na S18), que supus em 45% da cena. O tempo exato só sai do `vp render`.
5. **Fora destes clipes:** o carimbo "c. 2000 a.C." (`stamp`), o `keyword` "o rotor fica bloqueado" e o `compare` "Gira × Não gira" da S17 (planos do template); a 1.ª parte da S03 (as cinco colunas aparecem uma a uma), a 1.ª parte da S18
   (corte alto demais na vista em corte), a S19 (dois pinos por câmara) e S20–S23.

## Para reproduzir um quadro
`cd video && TMPDIR=<pasta em data/cache/remotion-tmp> npx remotion still src/previews/mec-fechadura-pt/index.tsx FechaduraClipeErrada|FechaduraTrancaS03|FechaduraTrancaS18 <saida.png> --frame=N`
(pasta temporária de teste: `data/cache/remotion-tmp/piloto-fechadura-3`, a apagar quando quiser).
