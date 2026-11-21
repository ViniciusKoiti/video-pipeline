"""`vp evolucao`: versões do mesmo vídeo-régua, para comparar a evolução do template (#69; CLAUDE.md §8).

  gerar <id> --nota "..."              prévia pelo `vp render --preview` e guarda como nova versão
  guardar <id> --nota "..." [--commit REF] [--tempo-s N] [--sonda S]
                                       guarda a prévia que já existe (`renders/preview.mp4`)
  comparar <id> [--versoes v1,v3]      folha de quadros: o mesmo instante de cada plano, uma coluna por
                                       versão, com borda no quadro que mudou em relação à coluna anterior
  lado-a-lado <id> <vA> <vB>           vídeo com as duas versões lado a lado, com o áudio da segunda

- As versões ficam em `data/episodes/<id>/renders/evolucao/` (fora do Git), cada uma com um `vN.json`: commit,
  hash do template, sha do motion-kit, tempo, sonda de CPU, o instante de cada plano e os planos que mudaram.
- Cada versão acrescenta uma linha em `data/benchmarks/evolucao-template.md` (no Git).
- `gerar` renderiza (exceção do vídeo-régua, CLAUDE.md §8) e recusa rodar com a CPU limitada (sonda acima de
  0,3 s, §3), porque o tempo entra no registro. A voz fica a do vídeo-régua (Charon, ADR 012), já guardada.
- `--commit REF` é para um render antigo: o hash do template e o motion-kit saem daquele commit.

Era `scripts/provisorio/evolucao.py`. O hash do template vem da composição (`app/cli.py`), que conhece o
Remotion.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import time
from collections.abc import Callable
from pathlib import Path

from app.commands.project_root import project_root
from app.media import evolution
from app.media.constants.evolution_constants import EvolutionConstants
from app.pipeline.bench.runner import cpu_probe
from app.pipeline.constants.bench_constants import BenchConstants
from app.pipeline.ports import Context
from app.pipeline.schemas import EpisodeManifest
from app.render.constants.remotion_constants import RemotionConstants

TemplateHash = Callable[[Path], str]


def add_arguments(parser: argparse.ArgumentParser) -> None:
    verbs = parser.add_subparsers(dest="evolucao_command", required=True)
    generate = verbs.add_parser("gerar", help="renderiza a prévia e guarda como nova versão")
    generate.add_argument("episode_id")
    generate.add_argument("--nota", required=True)
    keep = verbs.add_parser("guardar", help="guarda a prévia que já existe como nova versão")
    keep.add_argument("episode_id")
    keep.add_argument("--nota", required=True)
    keep.add_argument("--commit")
    keep.add_argument("--tempo-s", type=float)
    keep.add_argument("--sonda", type=float)
    compare = verbs.add_parser("comparar", help="folha de quadros das versões")
    compare.add_argument("episode_id")
    compare.add_argument("--versoes", help="lista separada por vírgula; padrão: todas")
    side = verbs.add_parser("lado-a-lado", help="vídeo com duas versões lado a lado")
    side.add_argument("episode_id")
    side.add_argument("antes")
    side.add_argument("depois")


def run(args: argparse.Namespace, context: Context, *, template_hash: TemplateHash) -> int:
    root = project_root(Path.cwd())
    episode_dir = context.store.path(args.episode_id, "")
    folder = episode_dir / "renders" / "evolucao"
    if args.evolucao_command == "gerar":
        _generate(root, args.episode_id, episode_dir, args.nota, template_hash)
    elif args.evolucao_command == "guardar":
        _save(root, episode_dir, args.nota, args.commit, args.tempo_s, args.sonda, template_hash)
    elif args.evolucao_command == "comparar":
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
    return 0


def _generate(root: Path, episode_id: str, episode_dir: Path, note: str, template_hash: TemplateHash) -> None:
    probe = cpu_probe()
    if probe > BenchConstants.CPU_PROBE_SLOW_S:
        raise evolution.EvolutionError(
            f"CPU limitada (sonda {probe:.2f} s, limite {BenchConstants.CPU_PROBE_SLOW_S} s): "
            "feche os apps pesados e tente de novo"
        )
    started = time.monotonic()
    # O vídeo-régua fica com a voz com que foi gravado (Charon, ADR 012), já guardada: só o template muda.
    command = [sys.executable, "-m", "app", "render", episode_id, "--preview", "--voz", "gemini"]
    subprocess.run(command, cwd=root, check=True)
    _save(root, episode_dir, note, None, round(time.monotonic() - started, 1), probe, template_hash)


def _save(
    root: Path, episode_dir: Path, note: str, ref: str | None, render_s: float | None, probe: float | None,
    template_hash: TemplateHash,
) -> None:
    episode = EpisodeManifest.model_validate_json((episode_dir / "episode.json").read_text())
    commit, template, kit = template_info(root, ref, template_hash)
    version = evolution.store(
        episode_dir / "renders" / "preview.mp4", episode, episode_dir / "renders" / "evolucao",
        commit=commit, template_hash=template, motion_kit=kit, note=note,
        render_s=render_s, cpu_probe_s=probe,
    )
    registry = root / EvolutionConstants.REGISTRY_FILE
    evolution.append_registry(registry, version)
    print(f"{version.name}: {len(version.samples)} planos, commit {commit}, template {template[:12]}")
    if version.changed is not None:
        print(f"planos que mudaram desde a versão anterior: {', '.join(version.changed) or 'nenhum'}")
    print(f"registro: {EvolutionConstants.REGISTRY_FILE}")


def template_info(root: Path, ref: str | None, template_hash: TemplateHash) -> tuple[str, str, str]:
    """Commit, hash do template e sha do motion-kit: do diretório de trabalho ou de um commit antigo."""
    if ref is None:
        commit = _git(root, "rev-parse", "--short", "HEAD")
        if _git(root, "status", "--porcelain", "--", "video"):
            commit += " + alterações locais em video/"
        return commit, *_project_info(root / RemotionConstants.PROJECT.name, template_hash)
    commit = _git(root, "rev-parse", "--short", ref)
    with tempfile.TemporaryDirectory() as tmp:
        archive = subprocess.run(["git", "archive", ref, "video"], cwd=root, capture_output=True, check=True)
        subprocess.run(["tar", "-x", "-C", tmp], input=archive.stdout, check=True)
        return commit, *_project_info(Path(tmp) / "video", template_hash)


def _project_info(project: Path, template_hash: TemplateHash) -> tuple[str, str]:
    return template_hash(project), evolution.motion_kit_pin((project / "package.json").read_text())


def _git(root: Path, *args: str) -> str:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True, check=True).stdout.strip()
