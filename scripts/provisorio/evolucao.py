"""Evolução do template: versões do mesmo vídeo-régua, para comparar (provisório, #69).

Uso: `.venv/bin/python scripts/provisorio/evolucao.py <comando> <episode-id> ...`

  gerar <id> --nota "..."              prévia pelo `montar_episodio.py --preview` e guarda como nova versão
  guardar <id> --nota "..." [--commit REF] [--tempo-s N] [--sonda S]
                                       guarda a prévia que já existe (`renders/preview.mp4`)
  comparar <id> [--versoes v1,v3]      folha de quadros: o mesmo instante de cada plano, uma coluna por
                                       versão, com borda no quadro que mudou em relação à coluna anterior
  lado-a-lado <id> <vA> <vB>           vídeo com as duas versões lado a lado, com o áudio da segunda

- As versões ficam em `data/episodes/<id>/renders/evolucao/` (fora do Git), cada uma com um `vN.json`: commit,
  hash do template, sha do motion-kit, tempo, sonda de CPU, o instante de cada plano e os planos que mudaram
  em relação à versão anterior (um quadro por plano).
- Cada versão acrescenta uma linha em `data/benchmarks/evolucao-template.md` (no Git).
- `gerar` recusa rodar com a CPU limitada (sonda acima de 0,3 s, CLAUDE.md §3), porque o tempo entra no
  registro.
- `--commit REF` é para um render antigo: o hash do template e o motion-kit saem daquele commit, não do
  diretório de trabalho.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.media import evolution  # noqa: E402
from app.pipeline.bench import CPU_PROBE_SLOW_S, cpu_probe  # noqa: E402
from app.pipeline.schemas import EpisodeManifest  # noqa: E402
from app.render.remotion import PROJECT, template_hash  # noqa: E402
from app.settings import load_settings  # noqa: E402

REGISTRY = ROOT / "data" / "benchmarks" / "evolucao-template.md"


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout.strip()


def template_info(ref: str | None) -> tuple[str, str, str]:
    """Commit, hash do template e sha do motion-kit: do diretório de trabalho ou de um commit."""
    if ref is None:
        commit = git("rev-parse", "--short", "HEAD")
        if git("status", "--porcelain", "--", "video"):
            commit += " + alterações locais em video/"
        return commit, *project_info(PROJECT)
    commit = git("rev-parse", "--short", ref)
    with tempfile.TemporaryDirectory() as tmp:
        archive = subprocess.run(["git", "archive", ref, "video"], cwd=ROOT, capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", tmp], input=archive.stdout, check=True)
        return commit, *project_info(Path(tmp) / "video")


def project_info(project: Path) -> tuple[str, str]:
    return template_hash(project), evolution.motion_kit_sha((project / "package.json").read_text())


def save(episode_dir: Path, note: str, ref: str | None, render_s: float | None, probe: float | None) -> None:
    episode = EpisodeManifest.model_validate_json((episode_dir / "episode.json").read_text())
    commit, template, kit = template_info(ref)
    version = evolution.store(
        episode_dir / "renders" / "preview.mp4", episode, episode_dir / "renders" / "evolucao",
        commit=commit, template_hash=template, motion_kit=kit, note=note,
        render_s=render_s, cpu_probe_s=probe,
    )
    evolution.append_registry(REGISTRY, version)
    print(f"{version.name}: {len(version.samples)} planos, commit {commit}, template {template[:12]}")
    if version.changed is not None:
        print(f"planos que mudaram desde a versão anterior: {', '.join(version.changed) or 'nenhum'}")
    print(f"registro: {REGISTRY.relative_to(ROOT)}")


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("gerar")
    generate.add_argument("episode_id")
    generate.add_argument("--nota", required=True)
    keep = commands.add_parser("guardar")
    keep.add_argument("episode_id")
    keep.add_argument("--nota", required=True)
    keep.add_argument("--commit")
    keep.add_argument("--tempo-s", type=float)
    keep.add_argument("--sonda", type=float)
    compare = commands.add_parser("comparar")
    compare.add_argument("episode_id")
    compare.add_argument("--versoes", help="lista separada por vírgula; padrão: todas")
    side = commands.add_parser("lado-a-lado")
    side.add_argument("episode_id")
    side.add_argument("antes")
    side.add_argument("depois")
    args = parser.parse_args()

    episode_dir = load_settings(ROOT).data_dir / "episodes" / args.episode_id
    folder = episode_dir / "renders" / "evolucao"
    try:
        if args.command == "gerar":
            probe = cpu_probe()
            if probe > CPU_PROBE_SLOW_S:
                raise SystemExit(f"CPU limitada (sonda {probe:.2f} s, limite {CPU_PROBE_SLOW_S} s): "
                                 "feche os apps pesados e tente de novo")
            started = time.monotonic()
            script = ROOT / "scripts" / "provisorio" / "montar_episodio.py"
            # O vídeo-régua fica com a voz com que foi gravado (Charon, ADR 012), já guardada: só o
            # template muda. A voz final de hoje é outra (ADR 016) e mudaria o tempo de todos os planos.
            command = [sys.executable, str(script), args.episode_id, "--preview", "--voz=gemini"]
            subprocess.run(command, cwd=ROOT, check=True)
            save(episode_dir, args.nota, None, round(time.monotonic() - started, 1), probe)
        elif args.command == "guardar":
            save(episode_dir, args.nota, args.commit, args.tempo_s, args.sonda)
        elif args.command == "comparar":
            names = args.versoes.split(",") if args.versoes else evolution.versions(folder)
            suffix = "" if not args.versoes else "-" + "-".join(names)
            out = folder / f"folha{suffix}.jpg"
            changes = evolution.contact_sheet(folder, names, out)
            print(f"folha: {out} ({len(names)} versões; borda nos quadros que mudaram)")
            for name, changed in changes.items():
                print(f"  {name}: {', '.join(changed) or 'nenhum plano mudou'}")
        else:
            out = folder / f"{args.antes}-{args.depois}.mp4"
            evolution.side_by_side(folder, args.antes, args.depois, out)
            print(f"lado a lado: {out}")
    except evolution.EvolutionError as error:
        raise SystemExit(str(error)) from error


if __name__ == "__main__":
    main()
