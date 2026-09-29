# Evolução do template (vídeo-régua)

Uma versão por mudança no visual do formato explicativo, sempre do mesmo vídeo com o conteúdo congelado
(roteiro, imagens e voz aprovados): só o template muda entre as versões. Os vídeos ficam fora do Git, em
`data/episodes/<id>/renders/evolucao/` (`vN.mp4` e `vN.json`); a folha de quadros e o vídeo lado a lado saem
de `scripts/provisorio/evolucao.py`. "Tempo" é o do `montar_episodio.py --preview` (voz em cache + render);
a sonda de CPU acima de 0,3 s indica máquina limitada (CLAUDE.md §3).

| Versão | Vídeo-régua | Render em | Commit | motion-kit | Template | Tempo | Sonda de CPU | O que mudou |
|---|---|---|---|---|---|---|---|---|
| v1 | `votorantim-dinheiro` | 2026-09-28 16:09 | `831c96d` | `2af5a7e` | `5fe6e0bd7401` | 180 s | 0,05 s | Primeira versão com os planos da ADR 011 (motion-kit 0.2, tema editorial). Tempo e sonda das métricas de 2026-09-28 (só o render; a voz foi gerada no mesmo script). |
