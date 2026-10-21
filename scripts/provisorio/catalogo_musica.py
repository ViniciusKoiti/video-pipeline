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
- `usar`: copia o ativo e o arquivo da faixa para `assets/` do episódio, onde o gate 3 aprova a faixa como
  qualquer outro ativo (`vp approve <id> --step assets --asset <asset-id>`).
"""

from __future__ import annotations

import argparse
import hashlib
import re
import shutil
import sys
import unicodedata
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.media.loudness import integrated_lufs, intensity  # noqa: E402
from app.media.probe import duration_ms  # noqa: E402
from app.pipeline.music import load_music_catalog  # noqa: E402
from app.pipeline.schemas import (  # noqa: E402
    ATTRIBUTION_LICENSES,
    AUDIO_LIBRARY_LICENSE,
    MUSIC_CATALOG_FILE,
    MUSIC_DIR,
    Asset,
    MusicCatalog,
    MusicTrack,
    Provider,
)

LIBRARY_URL = "https://www.youtube.com/audiolibrary"
AUDIO_SUFFIXES = (".mp3", ".m4a", ".wav", ".ogg")


def slug(text: str) -> str:
    plain = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", plain.lower()).strip("-")


def add(args: argparse.Namespace, music_dir: Path) -> int:
    source = Path(args.arquivo)
    if source.suffix.lower() not in AUDIO_SUFFIXES:
        raise SystemExit(f"formato {source.suffix} fora de {', '.join(AUDIO_SUFFIXES)}")
    if args.licenca in ATTRIBUTION_LICENSES and not args.atribuicao:
        raise SystemExit("faixa CC exige --atribuicao (o texto do botão Copy da coluna License type)")
    asset_id = f"ytal-{slug(args.titulo)}"
    catalog = load_music_catalog(music_dir.parent) or MusicCatalog()
    if asset_id in catalog.by_id():
        raise SystemExit(f"{asset_id} já está no catálogo")
    target = music_dir / f"{asset_id}{source.suffix.lower()}"
    music_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    digest = hashlib.sha256(target.read_bytes()).hexdigest()
    lufs = integrated_lufs(target)
    vocals = args.voz_cantada == "sim"
    now = datetime.now(UTC)
    asset = Asset(
        id=asset_id,
        provider=Provider.YOUTUBE_AUDIO_LIBRARY,
        provider_id=args.titulo,
        page_url=LIBRARY_URL,
        author=args.artista,
        license_id=args.licenca,
        attribution_text=args.atribuicao or "",
        usage_notes=(
            f"Faixa \"{args.titulo}\"{f' de {args.artista}' if args.artista else ''}, baixada pelo dono na "
            f"YouTube Audio Library (Studio) em {now:%Y-%m-%d}; licença conforme a coluna License type "
            f"({args.licenca}). Só em vídeo publicado no YouTube (data/benchmarks/termos-musica.md, "
            f"ADR 030). Voz cantada: {'sim' if vocals else 'não'} (escuta do dono)."
        ),
        retrieved_at=now,
        sha256=digest,
    )
    (music_dir / f"{asset_id}.json").write_text(asset.model_dump_json(indent=2) + "\n")
    track = MusicTrack(
        asset_id=asset_id,
        title=args.titulo,
        artist=args.artista,
        file=target.name,
        duration_ms=duration_ms(target),
        moods=[m.strip() for m in args.clima.split(",") if m.strip()],
        intensity=intensity(lufs),
        bpm=args.bpm,
        vocals=vocals,
        loops=args.loop,
    )
    catalog = MusicCatalog(tracks=[*catalog.tracks, track])
    (music_dir / MUSIC_CATALOG_FILE).write_text(catalog.model_dump_json(indent=2) + "\n")
    print(f"{asset_id}: {track.duration_ms / 1000:.0f} s, {lufs:.1f} LUFS, intensidade {track.intensity}")
    return 0


def use(args: argparse.Namespace, music_dir: Path, data_dir: Path) -> int:
    catalog = load_music_catalog(data_dir)
    track = (catalog.by_id() if catalog else {}).get(args.asset_id)
    if track is None:
        raise SystemExit(f"{args.asset_id} fora do catálogo")
    assets = data_dir / "episodes" / args.episode_id / "assets"
    if not assets.parent.is_dir():
        raise SystemExit(f"episódio {args.episode_id} não existe")
    assets.mkdir(exist_ok=True)
    for name in (f"{track.asset_id}.json", track.file):
        if (assets / name).exists():
            print(f"{name}: já está no episódio")
            continue
        shutil.copy2(music_dir / name, assets / name)
        print(f"{name} -> {assets / name}")
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
    licenses = sorted({AUDIO_LIBRARY_LICENSE} | ATTRIBUTION_LICENSES)
    add_p.add_argument("--licenca", choices=licenses, default=AUDIO_LIBRARY_LICENSE)
    add_p.add_argument("--atribuicao", help="texto de crédito, para faixa CC")
    use_p = sub.add_parser("usar", help="copia a faixa para assets/ do episódio (gate 3)")
    use_p.add_argument("episode_id")
    use_p.add_argument("asset_id")
    sub.add_parser("listar")
    args = parser.parse_args(argv)
    data_dir = ROOT / "data"
    music_dir = data_dir / MUSIC_DIR
    if args.comando == "adicionar":
        return add(args, music_dir)
    if args.comando == "usar":
        return use(args, music_dir, data_dir)
    return list_tracks(data_dir)


if __name__ == "__main__":
    raise SystemExit(main())
