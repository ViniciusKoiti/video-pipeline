# Render do explainer: onde está o tempo (2026-10-30)

Medição do fluxo `montar_episodio.py` → `RemotionEngine.render()` → `assemble()` no `votorantim-dinheiro`
(10 cenas, 109,4 s, 1080p de saída, **prévia** em 720p), numa cópia do episódio fora de `data/episodes/`.
Máquina livre (carga abaixo de 3 no início de cada série; sonda de CPU de 0,045 a 0,095 s, abaixo dos
0,3 s do CLAUDE.md §3). WSL2, 12 threads, ffmpeg 8.0.1, Remotion do `video/package-lock.json`.
Cada cenário foi repetido duas vezes; render intercalado quando a comparação é entre configurações.

## Fases do render (antes das mudanças; concurrency 8)

| Cenário | Total | bundle | selectComposition | renderMedia | assemble |
|---|---|---|---|---|---|
| Cache vazio (2 rodadas) | 242,5 / 237,4 s | 19,9 / 3,9 s | 6,4 / 6,5 s | 206 / 218 s | 8,2 / 7,9 s |
| Cache cheio | 8,2 / 8,0 s | 0 | 0 | 0 | 7,5 / 7,3 s |
| Uma cena invalidada (S03) | 25,1 / 24,9 s | 3,6 / 3,6 s | 0,7 s | 12 s | 7,7 / 7,6 s |

O bundle de 19,9 s é o Webpack sem cache (primeira rodada). O `renderMedia` é ~88% do render completo.

## `assemble`: o AAC era 6,3 s dos 7,5 s

Vídeo `-c:v copy` 0,25 s; decodificar e reamostrar 24 kHz mono → 48 kHz estéreo 0,3 s; os 10 `ffprobe` 0,7 s;
**encoder `aac` nativo 6,3 s** para 109 s de áudio (~17x o tempo real; não escala com threads;
`-aac_coder fast` 4,5 s). O áudio agora fica em cache (`.audio-<saída>-<chave>.m4a`, commit `c84cfea`):

| Cenário (prévia) | Antes | Depois |
|---|---|---|
| `assemble` com cache | 7,3 a 7,6 s | 0,47 s |
| Render com cache cheio | 8,0 a 8,2 s | 1,1 s |
| Uma cena invalidada | 25,0 s | 17,9 a 18,1 s |

## `concurrency` e `jpegQuality` no `renderMedia`

Por cena (node direto, 2 repetições): S03 (`keyword`, `stamp`; 303 quadros) e S02 (`photo`, `compare`,
`keyword`; 440 quadros; JPEG de 5 MB).

| concurrency | S03 | S02 |
|---|---|---|
| 2 | n/m | 23,5 a 24,9 s |
| 3 | n/m | 20,8 a 21,7 s |
| 4 | 12,5 a 13,5 s | 18,9 a 21,8 s |
| 6 | n/m | 21,3 a 23,2 s |
| 8 | 10,1 a 11,1 s | 31 a 39 s |
| 12 | 11,4 a 12,0 s | 96 a 107 s |

`jpegQuality` 90, 75 e 60 não mudou o tempo de forma distinguível do ruído; abaixo de 90 o MP4 da S02
ficou maior (2,75 MB → 5,3 e 6,1 MB), porque o ruído do JPEG pesa no x264. Mantido em 90.

Render completo, cache vazio. A série não intercalada (4, 6, 4, 6) deu 249,6 / 224,8 / 194,2 / 190,6 s e
**não vale**: a mesma configuração variou mais (250 contra 194 s) do que as configurações entre si, e a
máquina variou 25% entre sessões (base de 8 abas: 237 a 242 s antes, 187 a 192 s depois). A série
intercalada (8, 4, 6, 8, 4, 6):

| concurrency | Rodada 1 | Rodada 2 | Média |
|---|---|---|---|
| 8 | 191,9 s | 186,6 s | 189,3 s |
| 4 | 181,0 s | 182,3 s | 181,7 s |
| 6 | 177,5 s | 181,9 s | 179,7 s |

6 abas ganha ~5% (perto do ruído de 4 a 5 s). O padrão passou de 8 para 6 (commit `623dabf`), sobretudo
pela margem com mídia pesada (8 abas já estourou o tempo de espera em 2026-10-24).

## Não medido

- Render final em 1080p (só a prévia).
- Episódio com apresentador (`mouth_levels`) e com trilha no `assemble`.
- A S01 (B-roll de 14 MB) e a S07 (mapa de 6 MB) isoladas.
- O custo do quadro em si (componentes, Chrome, x264): a S03, sem mídia, leva 10 a 11 s para 303 quadros.
- Reaproveitar o bundle (3,6 s por edição) e o Chrome entre cenas (`selectComposition` 0,7 s por cena).
