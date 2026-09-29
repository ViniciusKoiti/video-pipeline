# Evolução do template (vídeo-régua)

Uma versão por mudança no visual do formato explicativo, sempre do mesmo vídeo com o conteúdo congelado
(roteiro, imagens e voz aprovados): só o template muda entre as versões. Os vídeos ficam fora do Git, em
`data/episodes/<id>/renders/evolucao/` (`vN.mp4` e `vN.json`); a folha de quadros e o vídeo lado a lado saem
de `scripts/provisorio/evolucao.py`. "Tempo" é o do `montar_episodio.py --preview` (voz em cache + render);
a sonda de CPU acima de 0,3 s indica máquina limitada (CLAUDE.md §3). "Planos que mudaram" compara um quadro
por plano com a versão anterior; um PR de visual deve mudar só os planos que pretendia.

| Versão | Vídeo-régua | Render em | Commit | motion-kit | Template | Tempo | Sonda de CPU | Planos que mudaram | O que mudou |
|---|---|---|---|---|---|---|---|---|---|
| v1 | `votorantim-dinheiro` | 2026-09-28 16:09 | `831c96d` | `2af5a7e` | `5fe6e0bd7401` | 180 s | 0,05 s | — | Primeira versão com os planos da ADR 011 (motion-kit 0.2, tema editorial). Tempo e sonda das métricas de 2026-09-28 (só o render; a voz foi gerada no mesmo script). |
| v2 | `votorantim-dinheiro` | 2026-09-29 14:51 | `8cd30ba` | `2af5a7e` | `951451d34a41` | 206 s | 0,10 s | S01 plano 2, S07 plano 3, S09 plano 3 | #88: fonte sobre foto ou B-roll sempre embaixo à direita, fora do painel do número. |
| v3 | `votorantim-dinheiro` | 2026-09-29 15:39 | `d34c6d7` | `2af5a7e` | `db42c99790ba` | 192 s | 0,05 s | S09 plano 2 | #92: rede em camadas com as setas descendo (S09: valor e texto da seta não ficam mais sob o nome da CBA); rede desenhada em 1280×720 e ampliada, prévia igual ao final. |
