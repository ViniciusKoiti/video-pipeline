"""`vp short`: o Short de tecnologia montado por JSON no `motion-video` do kit (skill `shorts-tec`, RF7).

O dono aparece numa janela e fala com a voz clonada; a pasta de produção (`data/episodes/<id>/`) guarda a
narração, o JSON do kit e o que cada verbo escreve. Um verbo por etapa, cada um num módulo `short_<verbo>`:

- `vp short voz <pasta> <narracao.json> [--voz NOME]`: uma fala por linha da narração.
- `vp short gate <mp4> <post.json> --episodio ID`: o pacote do gate 4 do Short.

`narracao.json`: `{"language": "pt-BR", "lines": [{"scene": "gancho", "text": "...", "delivery": "hook"},
...]}`. `scene` é o `id` de uma cena do JSON do motion-video; `null` marca uma fala de um plano fora do JSON
(gravação de tela, troca de estilos), gerada para a montagem final e ignorada por `tempos` e `juntar`.
`delivery` é a entrega da ADR 022 (`hook`, `turn`, `calm`, `invite`; sem ela, neutra).
"""

from __future__ import annotations

import argparse
from pathlib import Path

from app.commands import short_gate, short_voz
from app.pipeline.ports import Context


def add_arguments(parser: argparse.ArgumentParser) -> None:
    verbs = parser.add_subparsers(dest="short_command", required=True)
    voz = verbs.add_parser("voz", help="uma fala por linha da narração, com a voz clonada do dono")
    voz.add_argument("folder", type=Path, metavar="pasta", help="pasta de produção do Short")
    voz.add_argument("narration", type=Path, metavar="narracao.json")
    voz.add_argument("--voz", metavar="NOME", help="voz registrada pelo nome (kokoro para um rascunho local)")
    gate = verbs.add_parser("gate", help="o pacote do gate 4: vídeo e texto do post na pasta do episódio")
    gate.add_argument("video", type=Path, metavar="video.mp4")
    gate.add_argument("post", type=Path, metavar="post.json")
    gate.add_argument("--episodio", required=True, metavar="ID", help="um id por idioma (-pt, -en)")


def run(args: argparse.Namespace, context: Context) -> int:
    if args.short_command == "voz":
        return short_voz.run(args, context)
    return short_gate.run(args, context)
