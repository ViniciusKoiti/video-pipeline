# Render dos clipes do mec-fechadura-pt (2026-11-09)

Autorização do dono na sessão ("C e B"): render em vídeo dos clipes do estudo `video/src/previews/mec-fechadura-pt/` e corte nas âncoras reais.

- **Máquina:** sonda de CPU antes do lote 0,044 s e antes do 1.º render 0,046 s (limite 0,3 s: livre). 12 threads; WSL com 11 GB.
- **Comando por clipe** (um por vez): `remotion render src/previews/mec-fechadura-pt/index.tsx <Composição> <saída>.mp4 --scale=1.5 --codec=h264 --concurrency=4 --muted --frames=A-B`, `TMPDIR` em `data/cache/remotion-tmp/clipes-fechadura/`.
- **Resultado:** 37 clipes, 7353 quadros (245.1 s de vídeo), 739 s de render (10.0 quadros/s), memória máxima 847 MB, 12,2 MB no total. Nenhuma falha.
- **Conferência:** `ffprobe` nos 37 (1920×1080, H.264, 30 fps, número de quadros igual ao do manifesto, diferença máxima de 1) e quadros extraídos dos vídeos da S21 (trecho repetido) e da S24.
- **Cortes:** pelas âncoras que o pipeline calcula (`shot_bounds`, `app/pipeline/shots.py`, sobre os WAV de `voice/leveled/`), com a regra de `video/src/Scene.tsx`: o `broll` segue por baixo dos planos seguintes até a **próxima mídia**
  ou o fim da cena (carimbo, número e frase entram por cima; `network` e `compare` cobrem). O manifesto está em `data/episodes/mec-fechadura-pt/clipes-manifesto.json`.
- **Só a S21 (V2.16)** precisa de trecho repetido: a composição tem 88 quadros e o plano dura 432 (o `network` o cobre a partir de 2.945 ms); o último quadro é repetido por 344 quadros (`ffmpeg tpad`, re-encode H.264).

| Ativo | Composição | Quadros | Render (s) | Memória máx. (MB) |
|---|---|---|---|---|
| mec-s01-v0 | FechaduraPortaS01 | 336 | 27.0 | 839 |
| mec-s02-v2.0 | FechaduraS02 | 128 | 13.9 | 811 |
| mec-s02-v2.0b | FechaduraS02 | 77 | 14.8 | 830 |
| mec-s03-v2.1 | FechaduraS03Colunas | 161 | 17.3 | 844 |
| mec-s03-v1 | FechaduraTrancaS03 | 197 | 27.2 | 819 |
| mec-s04-v2.2 | FechaduraClipe | 203 | 17.2 | 847 |
| mec-s05-v2.3 | FechaduraClipe | 283 | 21.5 | 839 |
| mec-s06-v2.4 | FechaduraClipe | 268 | 20.3 | 820 |
| mec-s07-v2.5 | FechaduraClipe | 218 | 17.2 | 824 |
| mec-s08-v2.6 | FechaduraClipe | 174 | 14.4 | 829 |
| mec-s08-v2.7 | FechaduraClipe | 134 | 13.7 | 821 |
| mec-s09-v2.8 | FechaduraClipe | 122 | 13.4 | 823 |
| mec-s09-v2.9 | FechaduraClipe | 248 | 24.2 | 822 |
| mec-s10-v2.10 | FechaduraClipe | 181 | 18.8 | 838 |
| mec-s11-v2.11 | FechaduraClipe | 150 | 16.8 | 841 |
| mec-s11-v2.12 | FechaduraClipe | 186 | 19.6 | 822 |
| mec-s12-v2.13 | FechaduraClipeFrente | 270 | 28.5 | 844 |
| mec-s13-v2.14 | FechaduraClipeFrente | 211 | 24.9 | 841 |
| mec-s14-v2.15 | FechaduraClipeCame | 222 | 31.8 | 840 |
| mec-s15-v4.0 | FechaduraClipeCadeado | 201 | 19.6 | 840 |
| mec-s15-v4.1 | FechaduraClipeCadeado | 121 | 14.5 | 821 |
| mec-s16-v4.2 | FechaduraClipeCadeado | 171 | 16.9 | 841 |
| mec-s16-v4.3 | FechaduraClipeCadeado | 136 | 14.2 | 839 |
| mec-s17-v3.0 | FechaduraClipeErrada | 431 | 36.6 | 846 |
| mec-s18-v3.1 | FechaduraS18Alta | 101 | 13.8 | 823 |
| mec-s18-v1-reprise | FechaduraTrancaS18 | 247 | 27.3 | 842 |
| mec-s19-v3.2 | FechaduraS19 | 199 | 24.0 | 825 |
| mec-s20-v3.3 | FechaduraS20 | 212 | 22.0 | 840 |
| mec-s21-v2.16 | FechaduraS21A | 432 | 14.4 | 835 |
| mec-s22-v5.0 | FechaduraS22 | 102 | 13.0 | 833 |
| mec-s22-v5.1 | FechaduraS22 | 71 | 10.8 | 812 |
| mec-s22-v5.2 | FechaduraS22 | 104 | 12.9 | 818 |
| mec-s23-v6.0 | FechaduraS23 | 349 | 44.0 | 824 |
| mec-s23-v6.1 | FechaduraS23 | 138 | 21.6 | 835 |
| mec-s24-v0-reprise | FechaduraPortaS24 | 219 | 16.5 | 842 |
| mec-s24-v2.17 | FechaduraS24B | 116 | 16.8 | 820 |
| mec-s25-v2.18 | FechaduraS25 | 234 | 17.5 | 839 |

Correção feita antes do render: o corte da S18 estava em 45% da cena e o da S24 em 55%; as âncoras reais são 28,9% (3.356 ms) e 65,4% (7.295 ms). S03 (45,1%) e S21 (20,5%) já estavam certos.

## Render v2 dos clipes e prévia do episódio (2026-11-09, noite)
- **Clipes v2 (sem o rodapé "Estudo visual"):** 37 clipes em `renders/mec-fechadura-pt/clipes-v2/`, `scale 1.5`, `concurrency 4`, mudos; sonda de CPU antes 0,044 s; lote de ~12 min, 12 MB; ffprobe: 37/37 com os quadros do manifesto, 1920×1080, sem áudio. Mídia dos ativos substituída antes do gate 3; os 37 foram aprovados depois.
- **Prévia 720p do episódio:** `vp render mec-fechadura-pt --preview --voz-final`, sonda de CPU 0,053 s; voz reaproveitada do cache em 4 s (sem chamar o Modal); render **1.964 s (~33 min)**, memória máxima **2,4 GB**; `preview.mp4` 245,13 s, 1280×720, H.264 + AAC estéreo, 13 MB; volume medido pelo `vp render` **−14,3 LUFS**; sem silêncio ≥ 2 s abaixo de −45 dB; `episode.json` com 4 trechos de música e 2 faixas (todos `gain_db −24`, nível `low`).
- Avisos do `vp render`: 1 plano com menos de 1,5 s na S01 e 1 na S05; média de 4,8 s por plano fora da faixa de 2–4 s do `explainer`; 12 blocos de legenda para revisar (números e "Egito").
