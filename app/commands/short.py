"""`vp short`: o Short de tecnologia montado por JSON no `motion-video` do kit (skill `shorts-tec`, RF7).

O dono aparece numa janela e fala com a voz clonada; a pasta de produção (`data/episodes/<id>/`) guarda a
narração, o JSON do kit e o que cada verbo escreve. Um verbo por etapa, cada um num módulo `short_<verbo>`:

- `vp short voz <pasta> <narracao.json> [--voz NOME]`: uma fala por linha da narração.
- `vp short tempos <pasta> <content.json> <narracao.json>`: o tempo de cada cena pela fala dela.
- `vp short sfx <pasta> <content.voz.json> <narracao.json> <sfx.json>`: confere o plano de efeitos.
- `vp short juntar <pasta> <video.mp4> <content.voz.json> <narracao.json> --saida MP4 [--sfx sfx.json]`:
  a voz e os efeitos sobre o MP4 silencioso do kit.
- `vp short boca <pasta> <content.voz.json> <narracao.json> --saida JSON [--manifesto] [--texto]`: os dados
  de uma montagem em TSX.
- `vp short gate <mp4> <post.json> --episodio ID`: o pacote do gate 4 do Short.

`narracao.json`: `{"language": "pt-BR", "lines": [{"scene": "gancho", "text": "...", "delivery": "hook"},
...]}`. `scene` é o `id` de uma cena do JSON do motion-video; `null` marca uma fala de um plano fora do JSON
(gravação de tela, troca de estilos), gerada para a montagem final e ignorada por `tempos` e `juntar`.
`delivery` é a entrega da ADR 022 (`hook`, `turn`, `calm`, `invite`; sem ela, neutra).
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

from app.commands import short_boca, short_gate, short_juntar, short_sfx, short_tempos, short_voz
from app.pipeline.ports import Context


def add_arguments(parser: argparse.ArgumentParser) -> None:
    verbs = parser.add_subparsers(dest="short_command", required=True)
    voz = verbs.add_parser("voz", help="uma fala por linha da narração, com a voz clonada do dono")
    voz.add_argument("folder", type=Path, metavar="pasta", help="pasta de produção do Short")
    voz.add_argument("narration", type=Path, metavar="narracao.json")
    voz.add_argument("--voz", metavar="NOME", help="voz registrada pelo nome (kokoro para um rascunho local)")
    _montage_arguments(verbs)
    gate = verbs.add_parser("gate", help="o pacote do gate 4: vídeo e texto do post na pasta do episódio")
    gate.add_argument("video", type=Path, metavar="video.mp4")
    gate.add_argument("post", type=Path, metavar="post.json")
    gate.add_argument("--episodio", required=True, metavar="ID", help="um id por idioma (-pt, -en)")


def _montage_arguments(verbs: Any) -> None:
    """Os verbos que leem a pasta de produção, o conteúdo do kit e a narração."""
    tempos = verbs.add_parser("tempos", help="estica cada cena até a fala dela caber")
    _inputs(tempos, "content.json")
    sfx = verbs.add_parser("sfx", help="confere o plano de efeitos e lista onde cada som cai")
    _inputs(sfx, "content.voz.json")
    sfx.add_argument("plan", type=Path, metavar="sfx.json")
    juntar = verbs.add_parser("juntar", help="a voz e os efeitos sobre o MP4 silencioso do kit")
    juntar.add_argument("folder", type=Path, metavar="pasta")
    juntar.add_argument("video", type=Path, metavar="video.mp4")
    juntar.add_argument("content", type=Path, metavar="content.voz.json")
    juntar.add_argument("narration", type=Path, metavar="narracao.json")
    juntar.add_argument("--saida", type=Path, required=True, metavar="MP4")
    juntar.add_argument("--sfx", type=Path, metavar="sfx.json", help="plano de efeitos (ADR 035)")
    boca = verbs.add_parser("boca", help="batidas e envelope da boca para uma montagem em TSX")
    _inputs(boca, "content.voz.json")
    boca.add_argument("--saida", type=Path, required=True, metavar="JSON")
    boca.add_argument("--manifesto", type=Path, metavar="sprites.json", help="manifesto da pele")
    boca.add_argument("--texto", type=Path, metavar="arquivo", help="linhas para a tela")


def _inputs(parser: argparse.ArgumentParser, content_name: str) -> None:
    parser.add_argument("folder", type=Path, metavar="pasta", help="pasta de produção do Short")
    parser.add_argument("content", type=Path, metavar=content_name)
    parser.add_argument("narration", type=Path, metavar="narracao.json")


def run(args: argparse.Namespace, context: Context) -> int:
    match args.short_command:
        case "voz":
            return short_voz.run(args, context)
        case "tempos":
            return short_tempos.run(args, context)
        case "sfx":
            return short_sfx.run(args, context)
        case "juntar":
            return short_juntar.run(args, context)
        case "boca":
            return short_boca.run(args, context)
    return short_gate.run(args, context)
