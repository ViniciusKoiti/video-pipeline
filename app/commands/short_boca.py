"""`vp short boca <pasta> <content.voz.json> <narracao.json> --saida JSON [--manifesto sprites.json]
[--texto arquivo]`: os dados de uma montagem em TSX com o kit.

As batidas (cena, quadro inicial, duração, trecho da fala), o envelope da boca por quadro do vídeo inteiro
(`app/media/envelope.py`, o mesmo do apresentador do auto-play), o manifesto da pele e, com `--texto`, as
linhas de um arquivo para a tela.
"""

from __future__ import annotations

import argparse
import json

from app.pipeline.motion_inputs import load_content
from app.pipeline.ports import Context
from app.pipeline.short_mouth import mouth_data
from app.pipeline.short_timing import voiced


def run(args: argparse.Namespace, context: Context) -> int:
    data = mouth_data(load_content(args.content), voiced(args.folder, args.narration))
    if args.manifesto:
        data["manifest"] = json.loads(args.manifesto.read_text(encoding="utf-8"))
    if args.texto:
        data["json"] = args.texto.read_text(encoding="utf-8").splitlines()
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(data, ensure_ascii=False) + "\n", encoding="utf-8")
    spoken = sum(1 for level in data["levels"] if level > 0)
    fps = data["fps"]
    print(
        f"boca: {len(data['beats'])} batida(s), {len(data['levels'])} frames, fala em {spoken} "
        f"({spoken / fps:.1f} s); escrito {args.saida}"
    )
    return 0
