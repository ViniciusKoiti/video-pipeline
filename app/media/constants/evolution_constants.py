"""Constantes de evolution; dados fixos sem I/O."""

from __future__ import annotations

import re
from typing import Final


class EvolutionConstants:
    # fração do plano: depois da entrada, antes da transição
    SAMPLE_AT: Final[float] = 0.7
    CELL_W: Final[int] = 480
    CELL_H: Final[int] = 270
    LABEL_W: Final[int] = 300
    HEADER_H: Final[int] = 56
    SIDE_W: Final[int] = 960
    SIDE_H: Final[int] = 540
    DURATION_TOLERANCE_MS: Final[int] = 500
    BACKGROUND: Final[str] = "0x16181d"
    EMPTY: Final[str] = "0x2a2d33"
    # borda do quadro que mudou (a cor de destaque do template)
    MARK: Final[str] = "0xF2B134"
    # borda do quadro que mudou (a cor de destaque do template)
    MARK_PX: Final[int] = 6
    CHANGE_PSNR_DB: Final[float] = 50.0
    VERSION: Final = re.compile("^v(\\d+)$")
    MOTION_KIT_SHA: Final = re.compile('motion-kit[^\\"]*\\"\\s*:\\s*\\"[^\\"]*sha=([0-9a-f]{7,40})')
    MOTION_KIT_TARBALL: Final = re.compile(
        'motion-kit\\"\\s*:\\s*\\"file:[^\\"]*motion-kit-(\\d+\\.\\d+\\.\\d+[^\\"]*)\\.tgz\\"'
    )
    REGISTRY_COLUMNS: Final = (
        "Versão",
        "Vídeo-régua",
        "Render em",
        "Commit",
        "motion-kit",
        "Template",
        "Tempo",
        "Sonda de CPU",
        "Planos que mudaram",
        "O que mudou",
    )
    REGISTRY_HEADER: Final = (
        "# Evolução do template (vídeo-régua)\n\nUma versão por mudança no visual do "
        "formato explicativo, sempre do mesmo vídeo com o conteúdo "
        "congelado\n(roteiro, imagens e voz aprovados): só o template muda entre as "
        "versões. Os vídeos ficam fora do Git, em\n`data/episodes/<id>/renders/evoluc"
        "ao/` (`vN.mp4` e `vN.json`); a folha de quadros e o vídeo lado a lado "
        'saem\nde `scripts/provisorio/evolucao.py`. "Tempo" é o do '
        "`vp render --preview` (voz em cache + render);\na sonda de CPU "
        'acima de 0,3 s indica máquina limitada (CLAUDE.md §3). "Planos que '
        'mudaram" compara um quadro\npor plano com a versão anterior; um PR de '
        "visual deve mudar só os planos que pretendia.\n\n"
    ) + ("| " + " | ".join(REGISTRY_COLUMNS) + " |\n" + "|---" * len(REGISTRY_COLUMNS) + "|\n")
