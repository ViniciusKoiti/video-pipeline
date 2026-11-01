"""`vp short tempos <pasta> <content.json> <narracao.json>`: o tempo de cada cena pela fala dela.

Escreve `<content>.voz.json` com a duração de cada cena esticada até a fala caber (`max(duração do JSON,
fala + folga)`), sem encurtar nenhuma, e, nas cenas com a janela do apresentador, `host.speaking` com o trecho
da fala, para a boca parar quando a voz para. O `render` do kit sai desse arquivo.
"""

from __future__ import annotations

import argparse

from app.pipeline.motion_inputs import load_content
from app.pipeline.ports import Context
from app.pipeline.short_timing import fit_timing, fitted_path, voiced


def run(args: argparse.Namespace, context: Context) -> int:
    content = load_content(args.content)
    fitted, rows = fit_timing(content, voiced(args.folder, args.narration))
    out = fitted_path(args.content)
    out.write_text(fitted.dumps(), encoding="utf-8")
    for row in rows:
        spoken = f"fala {row.spoken:.2f} s" if row.spoken is not None else "sem fala"
        mark = " ←" if row.after != row.before else ""
        print(f"{row.scene:16s} {row.before:4.1f} → {row.after:4.1f} s  ({spoken}){mark}")
    print(
        f"tempos: {sum(r.after for r in rows):.1f} s no JSON ({sum(r.before for r in rows):.1f} s antes); "
        f"escrito {out.name}"
    )
    return 0
