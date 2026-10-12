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
| v4 | `votorantim-dinheiro` | 2026-09-29 17:14 | `6d856cf` | `2af5a7e` | `b7e0402eb5e6` | 205 s | 0,05 s | S09 plano 1, S09 plano 3 | Crédito da foto de arquivo acima da foto, alinhado à direita: o painel do número e a tarja não o cobrem mais (S09); a foto fica um pouco maior. |
| v5 | `votorantim-dinheiro` | 2026-10-12 17:44 | `bb7f96b + alterações locais em video/` | `527c708` | `328eedc7de4d` | 637 s | 0,16 s | S01 plano 1, S01 plano 2, S02 plano 1, S02 plano 2, S02 plano 3, S03 plano 1, S03 plano 2, S04 plano 1, S04 plano 2, S05 plano 1, S05 plano 2, S06 plano 1, S07 plano 1, S07 plano 2, S07 plano 3, S08 plano 1, S09 plano 1, S09 plano 3, S10 plano 1, S10 plano 2 | Linha de base antes de atualizar o motion-kit: template do main (bb7f96b) com o kit 527c708, depois dos PRs de apresentador (ADR 013), 9:16 (ADR 014), pausas (ADR 015) e números por idioma, que não tinham versão da régua. Árvore de trabalho com alterações não commitadas só na composição Clipe. |
| v6 | `votorantim-dinheiro` | 2026-10-12 17:52 | `bb7f96b + alterações locais em video/` | `b393012` | `c03630fbbdc9` | 344 s | 0,07 s | nenhum | motion-kit 0.2.0 (527c708) -> 0.3.0 (b393012, main publicado em 2026-10-09): só o pin do kit muda em relação à v5. Árvore de trabalho com alterações não commitadas só na composição Clipe. |
