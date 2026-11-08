"""`vp short gate <mp4> <post.json> --episodio ID`: o pacote do gate 4 de um Short (ADR 050).

Põe `renders/final.mp4` e `legenda-post.txt` (título e legenda do post) na pasta `data/episodes/<id>/`, para o
dono carimbar o gate 4 com `vp approve <id> --step preview` e o `vp postiz pacote --episode <id>` conferir a
aprovação, como num episódio (CLAUDE.md §5). Um id por idioma (`-pt`, `-en`): cada MP4 tem o seu gate.
`PackagePublisher` valida o vídeo e o post antes de escrever, recusa trocar o que o gate 4 já aprovou
(`vp reopen --step preview` libera) e só marca o pacote completo depois do último arquivo.
"""

from __future__ import annotations

import argparse

from app.media.probe import duration_ms
from app.pipeline.models.package_action import PackageAction
from app.pipeline.package import PackagePublisher
from app.pipeline.ports import Context
from app.pipeline.protection import ReviewWriteGuard


def run(args: argparse.Namespace, context: Context) -> int:
    guard = ReviewWriteGuard(context.store, context.review)
    publisher = PackagePublisher(context.store, guard, lambda mp4: duration_ms(mp4) / 1000)
    episode_id = args.episodio
    action = publisher.publish(episode_id, args.video, args.post)
    final = context.store.path(episode_id, "renders/final.mp4")
    done = "já estava igual" if action is PackageAction.UNCHANGED else "pacote montado"
    print(f"gate: {final} ({duration_ms(final) / 1000:.1f} s) e legenda-post.txt ({done}); carimbe com:")
    print(f'  vp approve {episode_id} --step preview --notes "assisti"')
    print(f"  vp postiz pacote {args.post} --episode {episode_id}")
    return 0
