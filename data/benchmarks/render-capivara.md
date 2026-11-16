# Render dos clipes da capivara (motion-video do kit)

| Data | Episódio | Conteúdo | Saída | Tempo | Memória (pico do processo node) | Sonda de CPU antes |
|---|---|---|---|---|---|---|
| 2026-11-13 | academia-dinheiro-pt | 138 cenas `cast`, kit 0.13.0, motion-video 0.6.0 | 1280×720, 30 fps, H.264, 442,2 s, 134 MB | 1 h 12 min 41 s | 615 MB | 0,075–0,132 s |

Observação: a duração saiu 0,17 s maior que a soma dos planos (442,03 s), pelo arredondamento de cada cena a quadros
inteiros (1/30 s). O processo do Chrome headless não entra na medida de memória.
| 2026-11-13 | academia-dinheiro-pt | 138 cenas `cast`, durações = mídia na tela (ajustar_duracoes.py) | 1280×720, 30 fps, H.264, 705,2 s, 154 MB | 18 min 54 s | 581 MB | 0,11 s |

O primeiro render (442 s em 1 h 12 min) foi bem mais lento por segundo de vídeo que o segundo (705 s em 19 min):
provavelmente a máquina ficou carregada durante o primeiro, apesar da sonda livre no início.
