"""`vp music`: o catálogo de música de fundo (ADR 030, ADR 047).

- `vp music adicionar <arquivo> --titulo ... --clima c1,c2 --voz-cantada sim|nao [--artista] [--loop]
  [--bpm N] [--licenca YouTube-Audio-Library | --licenca CC-BY-4.0 --atribuicao "<texto do Copy>"]`: a
  faixa que o dono baixou da YouTube Audio Library (Studio, sem API) vai para `data/music/` com o ativo
  `<id>.json` (licença, `sha256`, `usage_notes`) e uma linha no `catalog.json`. A duração vem do ffprobe e
  a intensidade (1 a 5), da loudness integrada. O clima e a voz cantada são do dono, que ouviu. Nunca
  substitui uma faixa do catálogo.
- `vp music usar <id> <asset-id>`: copia o ativo e o arquivo da faixa para `assets/` do episódio, onde o
  gate 3 aprova a faixa como qualquer outro ativo (`vp approve <id> --step assets --asset <asset-id>`).
  Confere o arquivo contra o `sha256` do ativo e nunca troca o que o episódio já tem.
- `vp music listar`: as faixas do catálogo. Sem rede.
"""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
from pathlib import Path

from app.commands.constants.music_command_constants import MusicCommandConstants as Constants
from app.media.loudness import integrated_lufs, intensity
from app.media.probe import duration_ms
from app.pipeline.constants.schemas_constants import SchemasConstants
from app.pipeline.models.audio_probe import AudioProbe
from app.pipeline.models.track_draft import TrackDraft
from app.pipeline.music import load_music_catalog
from app.pipeline.music_library import add_track, install_track
from app.pipeline.ports import Context
from app.pipeline.protection import ReviewWriteGuard


def add_arguments(parser: argparse.ArgumentParser) -> None:
    commands = parser.add_subparsers(dest="music_command", required=True)
    add = commands.add_parser("adicionar", help="faixa baixada da Audio Library para o catálogo")
    add.add_argument("arquivo")
    add.add_argument("--titulo", required=True)
    add.add_argument("--artista")
    add.add_argument("--clima", required=True, help="climas separados por vírgula (escuta do dono)")
    add.add_argument("--voz-cantada", choices=("sim", "nao"), required=True)
    add.add_argument("--loop", action="store_true", help="o fim emenda no começo sem corte audível")
    add.add_argument("--bpm", type=int)
    licenses = sorted({SchemasConstants.AUDIO_LIBRARY_LICENSE} | SchemasConstants.ATTRIBUTION_LICENSES)
    add.add_argument("--licenca", choices=licenses, default=SchemasConstants.AUDIO_LIBRARY_LICENSE)
    add.add_argument("--atribuicao", help="texto de crédito, para faixa CC")
    use = commands.add_parser("usar", help="copia a faixa para assets/ do episódio (gate 3)")
    use.add_argument("episode_id", metavar="id")
    use.add_argument("asset_id")
    commands.add_parser("listar", help="as faixas do catálogo")


def run(args: argparse.Namespace, context: Context) -> int:
    data_dir = context.settings.data_dir
    if args.music_command == "adicionar":
        return _add(args, data_dir / SchemasConstants.MUSIC_DIR)
    if args.music_command == "usar":
        return _use(args, context, data_dir / SchemasConstants.MUSIC_DIR)
    return _list(data_dir)


def _add(args: argparse.Namespace, music_dir: Path) -> int:
    draft = TrackDraft(
        title=args.titulo,
        moods=tuple(m.strip() for m in args.clima.split(",") if m.strip()),
        vocals=args.voz_cantada == "sim",
        license_id=args.licenca,
        artist=args.artista,
        attribution=args.atribuicao or "",
        bpm=args.bpm,
        loops=args.loop,
    )
    probe = AudioProbe(duration_ms=duration_ms, lufs=integrated_lufs, intensity=intensity)
    track, lufs = add_track(music_dir, Path(args.arquivo), draft, probe, datetime.now(UTC))
    print(
        f"{track.asset_id}: {track.duration_ms / 1000:.0f} s, {lufs:.1f} LUFS, intensidade {track.intensity}"
    )
    return 0


def _use(args: argparse.Namespace, context: Context, music_dir: Path) -> int:
    store = context.store
    action = install_track(
        store, ReviewWriteGuard(store, context.review), music_dir, args.episode_id, args.asset_id
    )
    print(f"{args.asset_id}: {Constants.ACTIONS[action]}")
    return 0


def _list(data_dir: Path) -> int:
    catalog = load_music_catalog(data_dir)
    for t in catalog.tracks if catalog else []:
        print(
            f"{t.asset_id}: {t.duration_ms / 1000:.0f} s, intensidade {t.intensity}, {', '.join(t.moods)}"
            f"{', voz cantada' if t.vocals else ''}{', loop' if t.loops else ''}"
        )
    return 0
