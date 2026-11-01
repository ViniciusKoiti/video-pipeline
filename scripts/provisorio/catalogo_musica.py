"""Catálogo de música de fundo (ADR 030), provisório até um comando `vp`.

Uso:
  .venv/bin/python scripts/provisorio/catalogo_musica.py adicionar <arquivo> --titulo "<título>"
      --clima <c1,c2> --voz-cantada sim|nao [--artista "<artista>"] [--loop] [--bpm N]
      [--licenca YouTube-Audio-Library | --licenca CC-BY-4.0 --atribuicao "<texto do botão Copy>"]
  .venv/bin/python scripts/provisorio/catalogo_musica.py usar <episode-id> <asset-id>
  .venv/bin/python scripts/provisorio/catalogo_musica.py listar

- `adicionar`: a faixa que o dono baixou da YouTube Audio Library (Studio, sem API) vai para `data/music/`
  com o ativo `<id>.json` (licença, `sha256`, `usage_notes`) e uma linha no `catalog.json`. A duração vem do
  ffprobe e a intensidade (1 a 5), da loudness integrada. O clima e a voz cantada são do dono, que ouviu.
  Nunca substitui uma faixa do catálogo.
- `usar`: copia o ativo e o arquivo da faixa para `assets/` do episódio, onde o gate 3 aprova a faixa como
  qualquer outro ativo (`vp approve <id> --step assets --asset <asset-id>`). Confere o arquivo contra o
  `sha256` do ativo e nunca troca o que o episódio já tem (`app.pipeline.music_library`, ADR 047).
"""

from __future__ import annotations

import argparse
import sys
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.commands.errors import run  # noqa: E402
from app.media.loudness import integrated_lufs, intensity  # noqa: E402
from app.media.probe import duration_ms  # noqa: E402
from app.pipeline.constants.schemas_constants import SchemasConstants  # noqa: E402
from app.pipeline.models.audio_probe import AudioProbe  # noqa: E402
from app.pipeline.models.track_draft import TrackDraft  # noqa: E402
from app.pipeline.models.track_install_action import TrackInstallAction  # noqa: E402
from app.pipeline.music import load_music_catalog  # noqa: E402
from app.pipeline.music_library import add_track, install_track  # noqa: E402
from app.pipeline.protection import ReviewWriteGuard  # noqa: E402
from app.settings import load_settings  # noqa: E402
from app.storage.json_files import JsonFileStore, JsonReviewGate  # noqa: E402

ACTIONS = {
    TrackInstallAction.INSTALLED: "faixa e ativo copiados para assets/ do episódio",
    TrackInstallAction.UNCHANGED: "já está no episódio",
    TrackInstallAction.REPAIRED: "o ativo já estava no episódio; a mídia foi refeita",
}


def add(args: argparse.Namespace, music_dir: Path) -> int:
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
    seconds = track.duration_ms / 1000
    print(f"{track.asset_id}: {seconds:.0f} s, {lufs:.1f} LUFS, intensidade {track.intensity}")
    return 0


def use(args: argparse.Namespace, music_dir: Path, data_dir: Path) -> int:
    store = JsonFileStore(data_dir / "episodes")
    guard = ReviewWriteGuard(store, JsonReviewGate(store))
    action = install_track(store, guard, music_dir, args.episode_id, args.asset_id)
    print(f"{args.asset_id}: {ACTIONS[action]}")
    return 0


def list_tracks(data_dir: Path) -> int:
    catalog = load_music_catalog(data_dir)
    for t in catalog.tracks if catalog else []:
        print(
            f"{t.asset_id}: {t.duration_ms / 1000:.0f} s, intensidade {t.intensity}, {', '.join(t.moods)}"
            f"{', voz cantada' if t.vocals else ''}{', loop' if t.loops else ''}"
        )
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="catalogo_musica.py")
    sub = parser.add_subparsers(dest="comando", required=True)
    add_p = sub.add_parser("adicionar", help="faixa baixada da Audio Library para o catálogo")
    add_p.add_argument("arquivo")
    add_p.add_argument("--titulo", required=True)
    add_p.add_argument("--artista")
    add_p.add_argument("--clima", required=True, help="climas separados por vírgula (escuta do dono)")
    add_p.add_argument("--voz-cantada", choices=("sim", "nao"), required=True)
    add_p.add_argument("--loop", action="store_true", help="o fim emenda no começo sem corte audível")
    add_p.add_argument("--bpm", type=int)
    licenses = sorted({SchemasConstants.AUDIO_LIBRARY_LICENSE} | SchemasConstants.ATTRIBUTION_LICENSES)
    add_p.add_argument("--licenca", choices=licenses, default=SchemasConstants.AUDIO_LIBRARY_LICENSE)
    add_p.add_argument("--atribuicao", help="texto de crédito, para faixa CC")
    use_p = sub.add_parser("usar", help="copia a faixa para assets/ do episódio (gate 3)")
    use_p.add_argument("episode_id")
    use_p.add_argument("asset_id")
    sub.add_parser("listar")
    args = parser.parse_args(argv)
    data_dir = load_settings(ROOT).data_dir
    music_dir = data_dir / SchemasConstants.MUSIC_DIR
    if args.comando == "adicionar":
        return add(args, music_dir)
    if args.comando == "usar":
        return use(args, music_dir, data_dir)
    return list_tracks(data_dir)


if __name__ == "__main__":
    raise SystemExit(run("catalogo_musica", main))
