"""Evolução do template: versões do mesmo vídeo-régua, para comparar (#69).

O conteúdo do vídeo-régua fica congelado (roteiro, imagens e voz aprovados) e só o template muda entre as
versões. Cada versão é `vN.mp4` com um `vN.json` ao lado, numa pasta fora do Git; o registro em Markdown fica
no Git. A folha de quadros põe o mesmo instante de cada plano, de todas as versões, numa imagem só (quadros
tirados dos MP4 prontos, sem render novo); o vídeo lado a lado mostra duas versões em movimento.
"""

from __future__ import annotations

import hashlib
import re
import shutil
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from app.media.probe import duration_ms
from app.pipeline.schemas import EpisodeManifest

SAMPLE_AT = 0.7  # fração do plano: depois da entrada, antes da transição
CELL_W, CELL_H = 480, 270
LABEL_W, HEADER_H = 300, 56
SIDE_W, SIDE_H = 960, 540
DURATION_TOLERANCE_MS = 500
BACKGROUND, EMPTY = "0x16181d", "0x2a2d33"
VERSION = re.compile(r"^v(\d+)$")
MOTION_KIT_SHA = re.compile(r"motion-kit[^\"]*\"\s*:\s*\"[^\"]*sha=([0-9a-f]{7,40})")

REGISTRY_HEADER = """# Evolução do template (vídeo-régua)

Uma versão por mudança no visual do formato explicativo, sempre do mesmo vídeo com o conteúdo congelado
(roteiro, imagens e voz aprovados): só o template muda entre as versões. Os vídeos ficam fora do Git, em
`data/episodes/<id>/renders/evolucao/` (`vN.mp4` e `vN.json`); a folha de quadros e o vídeo lado a lado saem
de `scripts/provisorio/evolucao.py`. "Tempo" é o do `montar_episodio.py --preview` (voz em cache + render);
a sonda de CPU acima de 0,3 s indica máquina limitada (CLAUDE.md §3).

| Versão | Vídeo-régua | Render em | Commit | motion-kit | Template | Tempo | Sonda de CPU | O que mudou |
|---|---|---|---|---|---|---|---|---|
"""


class EvolutionError(RuntimeError):
    pass


class Sample(BaseModel):
    """Um instante por plano: uma linha da folha de quadros."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    key: str  # "S01#2": cena e posição do plano na cena
    kind: str
    at_ms: int


class Version(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    name: str
    episode_id: str
    rendered_at: str  # hora do arquivo renderizado
    commit: str
    template_hash: str
    motion_kit: str
    sha256: str
    duration_ms: int
    render_s: float | None = None
    cpu_probe_s: float | None = None
    note: str
    samples: list[Sample]


def samples(episode: EpisodeManifest) -> list[Sample]:
    found = []
    for scene in episode.scenes:
        if not scene.shots:  # v1: um visual por cena
            found.append(Sample(key=f"{scene.id}#1", kind="photo",
                                at_ms=scene.start_ms + round(scene.duration_ms * SAMPLE_AT)))
        for index, shot in enumerate(scene.shots, start=1):
            at = scene.start_ms + shot.start_ms + round(shot.duration_ms * SAMPLE_AT)
            found.append(Sample(key=f"{scene.id}#{index}", kind=shot.spec.kind, at_ms=at))
    return found


def motion_kit_sha(package_json: str) -> str:
    match = MOTION_KIT_SHA.search(package_json)
    if match is None:
        raise EvolutionError("package.json sem o sha do @viniciusk/motion-kit")
    return match.group(1)[:7]


def versions(folder: Path) -> list[str]:
    """Versões guardadas, em ordem numérica (v2 antes de v10)."""
    names = [p.stem for p in folder.glob("v*.json") if VERSION.match(p.stem)]
    return sorted(names, key=lambda name: int(name[1:]))


def load(folder: Path, name: str) -> Version:
    path = folder / f"{name}.json"
    if not path.is_file():
        raise EvolutionError(f"versão {name} não existe em {folder}")
    return Version.model_validate_json(path.read_text())


def store(
    render: Path,
    episode: EpisodeManifest,
    folder: Path,
    *,
    commit: str,
    template_hash: str,
    motion_kit: str,
    note: str,
    render_s: float | None = None,
    cpu_probe_s: float | None = None,
) -> Version:
    """Copia o render como a próxima versão. Recusa render igual a uma versão guardada e render que não
    corresponde ao `episode.json` (os instantes dos planos sairiam errados)."""
    digest = _sha256(render)
    existing = versions(folder)
    for name in existing:
        if load(folder, name).sha256 == digest:
            raise EvolutionError(f"o render é igual à {name}: nada mudou no vídeo")
    length = duration_ms(render)
    if abs(length - episode.duration_ms) > DURATION_TOLERANCE_MS:
        raise EvolutionError(
            f"render com {length} ms e episode.json com {episode.duration_ms} ms: "
            "o episode.json não é o deste render"
        )
    name = f"v{int(existing[-1][1:]) + 1}" if existing else "v1"
    version = Version(
        name=name, episode_id=episode.episode_id,
        rendered_at=datetime.fromtimestamp(render.stat().st_mtime).isoformat(sep=" ", timespec="minutes"),
        commit=commit, template_hash=template_hash, motion_kit=motion_kit, sha256=digest, duration_ms=length,
        render_s=render_s, cpu_probe_s=cpu_probe_s, note=note, samples=samples(episode),
    )
    folder.mkdir(parents=True, exist_ok=True)
    shutil.copy2(render, folder / f"{name}.mp4")
    (folder / f"{name}.json").write_text(version.model_dump_json(indent=2) + "\n")
    return version


def registry_row(version: Version) -> str:
    cells = [
        version.name, f"`{version.episode_id}`", version.rendered_at, f"`{version.commit}`",
        f"`{version.motion_kit}`", f"`{version.template_hash[:12]}`",
        "—" if version.render_s is None else f"{version.render_s:.0f} s",
        "—" if version.cpu_probe_s is None else f"{version.cpu_probe_s:.2f} s".replace(".", ","),
        version.note.replace("|", "\\|").replace("\n", " "),
    ]
    return "| " + " | ".join(cells) + " |"


def append_registry(path: Path, version: Version) -> None:
    text = path.read_text() if path.is_file() else REGISTRY_HEADER
    if not text.endswith("\n"):
        text += "\n"
    path.write_text(text + registry_row(version) + "\n")


def contact_sheet(folder: Path, names: list[str], out: Path) -> Path:
    """Folha de quadros: uma linha por plano, uma coluna por versão, no mesmo instante do plano."""
    loaded = [load(folder, name) for name in names]
    by_version = [{s.key: s for s in version.samples} for version in loaded]
    keys = sorted({key for found in by_version for key in found}, key=_key_order)
    if not keys:
        raise EvolutionError("nenhum plano nas versões escolhidas")
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        parts = [_header(work, loaded)]
        for index, key in enumerate(keys):
            latest = next(found[key] for found in reversed(by_version) if key in found)
            label = [key.replace("#", " · plano "), latest.kind, _clock(latest.at_ms)]
            cells = [
                (folder / f"{version.name}.mp4", min(found[key].at_ms, version.duration_ms - 100))
                if key in found else None
                for version, found in zip(loaded, by_version, strict=True)
            ]
            parts.append(_row(work, index, label, cells))
        out.parent.mkdir(parents=True, exist_ok=True)
        inputs = [arg for part in parts for arg in ("-i", str(part))]
        stack = "".join(f"[{i}:v]" for i in range(len(parts)))
        _run(["ffmpeg", "-v", "error", "-y", *inputs,
              "-filter_complex", f"{stack}vstack=inputs={len(parts)}[out]",
              "-map", "[out]", "-frames:v", "1", "-q:v", "3", str(out)])
    return out


def side_by_side(folder: Path, before: str, after: str, out: Path) -> Path:
    """As duas versões lado a lado (1920×540), com o áudio da segunda."""
    versions_ = [load(folder, before), load(folder, after)]
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp)
        filters = []
        for i, version in enumerate(versions_):
            lines = [f"{version.name} · {version.rendered_at}"]
            label = _text(work / f"side{i}", lines, 26, 20, 16, box=True)
            filters.append(f"[{i}:v]{_fit(SIDE_W, SIDE_H)},{label}[s{i}]")
        filters.append("[s0][s1]hstack=inputs=2[out]")
        out.parent.mkdir(parents=True, exist_ok=True)
        _run([
            "ffmpeg", "-v", "error", "-y",
            "-i", str(folder / f"{before}.mp4"), "-i", str(folder / f"{after}.mp4"),
            "-filter_complex", ";".join(filters), "-map", "[out]", "-map", "1:a?",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "23", "-pix_fmt", "yuv420p",
            "-c:a", "aac", "-b:a", "128k", "-shortest", str(out),
        ])
    return out


def _header(work: Path, loaded: list[Version]) -> Path:
    width = LABEL_W + CELL_W * len(loaded)
    texts = []
    for i, version in enumerate(loaded):
        lines = [f"{version.name} · {version.rendered_at[:10]}"]
        texts.append(_text(work / f"header{i}", lines, 24, LABEL_W + i * CELL_W + 16, 16))
    out = work / "header.png"
    _run(["ffmpeg", "-v", "error", "-y",
          "-f", "lavfi", "-i", f"color=c={BACKGROUND}:s={width}x{HEADER_H}:d=1",
          "-vf", ",".join([*texts, "format=rgb24"]), "-frames:v", "1", str(out)])
    return out


def _row(work: Path, index: int, label: list[str], cells: list[tuple[Path, int] | None]) -> Path:
    args, filters = ["ffmpeg", "-v", "error", "-y"], []
    for i, cell in enumerate(cells):
        if cell is None:  # plano que não existia nessa versão
            args += ["-f", "lavfi", "-i", f"color=c={EMPTY}:s={CELL_W}x{CELL_H}:d=1"]
        else:
            video, at_ms = cell
            args += ["-ss", f"{max(at_ms, 0) / 1000:.3f}", "-i", str(video)]
        filters.append(f"[{i}:v]{_fit(CELL_W, CELL_H)},format=rgb24,trim=end_frame=1[c{i}]")
    args += ["-f", "lavfi", "-i", f"color=c={BACKGROUND}:s={LABEL_W}x{CELL_H}:d=1"]
    text = _text(work / f"row{index:03d}", label, 22, 16, 16)
    filters.append(f"[{len(cells)}:v]{text},format=rgb24,trim=end_frame=1[label]")
    stack = "[label]" + "".join(f"[c{i}]" for i in range(len(cells)))
    filters.append(f"{stack}hstack=inputs={len(cells) + 1}[row]")
    out = work / f"row{index:03d}.png"
    _run([*args, "-filter_complex", ";".join(filters), "-map", "[row]", "-frames:v", "1", str(out)])
    return out


def _fit(width: int, height: int) -> str:
    return (f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
            f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2,setsar=1")


def _text(stem: Path, lines: list[str], size: int, x: int, y: int, box: bool = False) -> str:
    """Um `drawtext` por linha: com quebra de linha no texto, o ffmpeg desenha um quadrado no lugar dela."""
    extra = ":box=1:boxcolor=black@0.6:boxborderw=8" if box else ""
    filters = []
    for i, line in enumerate(lines):
        textfile = stem.with_name(f"{stem.name}-{i}.txt")
        textfile.write_text(line)
        filters.append(f"drawtext=font=Sans:textfile='{_escape(textfile)}':fontcolor=white:fontsize={size}"
                       f":x={x}:y={y + i * round(size * 1.6)}{extra}")
    return ",".join(filters)


def _escape(path: Path) -> str:
    return str(path).replace("\\", "\\\\").replace(":", "\\:").replace("'", "\\'")


def _key_order(key: str) -> tuple[int, str, int]:
    scene, index = key.split("#")
    return len(scene), scene, int(index)


def _clock(ms: int) -> str:
    minutes, rest = divmod(ms, 60_000)
    return f"{minutes}:{rest / 1000:04.1f}".replace(".", ",")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _run(args: list[str]) -> None:
    result = subprocess.run(args, capture_output=True, text=True, check=False)
    if result.returncode != 0:
        raise EvolutionError(f"ffmpeg falhou: {result.stderr.strip()[-400:]}")
