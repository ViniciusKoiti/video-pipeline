"""Adapter experimental do MoneyPrinterTurbo (etapa 8, branch `experimento-mpt`).

O MPT roda isolado (clone + venv próprios, fora do repositório) e é chamado por subprocesso com
`experiments/mpt_driver.py`. Ele não tem cache por cena nem prévia: todo render é completo, e a prévia
é o mesmo vídeo com legendas, reduzido para 720p com ffmpeg.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

from app.media.probe import duration_ms
from app.pipeline.schemas import EpisodeManifest
from app.providers.base import ProviderInfo
from app.render.base import RenderResult, target_spec

DRIVER = Path(__file__).resolve().parents[2] / "experiments" / "mpt_driver.py"


class MptError(RuntimeError):
    pass


class MoneyPrinterTurboEngine:
    def __init__(
        self,
        root: Path,
        *,
        threads: int = 8,
        fit_mode: str = "contain",  # "cover" cortaria navios e pessoas (§9)
        font: str = "BeVietnamPro-Medium.ttf",
        burn_captions_preview: bool = True,
        burn_captions_final: bool = False,
    ) -> None:
        self.info = ProviderInfo("moneyprinterturbo", remote=False)
        self._root = root.expanduser()
        self._threads = threads
        self._fit_mode = fit_mode
        self._font = font
        self._burn = {True: burn_captions_preview, False: burn_captions_final}

    def render(
        self, episode: EpisodeManifest, episode_dir: Path, out: Path, *, preview: bool = False
    ) -> RenderResult:
        python = self._root / ".venv" / "bin" / "python"
        if not python.exists():
            raise MptError(f"MoneyPrinterTurbo não instalado em {self._root} (uv sync --frozen --no-dev)")
        spec = target_spec(episode, preview=preview)
        work = out.parent / f".mpt-{'preview' if preview else 'final'}"
        shutil.rmtree(work, ignore_errors=True)  # o MPT não tem cache por cena
        work.mkdir(parents=True)
        full = work / "full.mp4" if preview else out
        request = {
            "episode": episode.model_dump(mode="json"),
            "episode_dir": str(episode_dir.resolve()),
            "work_dir": str(work.resolve()),
            "out": str(full.resolve()),
            "threads": self._threads,
            "fit_mode": self._fit_mode,
            "font": self._font,
            "subtitles": self._burn[preview],
        }
        request_path = work / "request.json"
        request_path.write_text(json.dumps(request))
        result = subprocess.run(
            [str(python), str(DRIVER), str(request_path)],
            cwd=self._root,
            env={"PATH": "/usr/bin:/bin", "PYTHONPATH": str(self._root), "HOME": str(Path.home())},
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0 or not full.exists():
            raise MptError(f"MoneyPrinterTurbo falhou: {(result.stderr or result.stdout).strip()[-800:]}")
        if preview:
            subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-i", str(full), "-vf", f"scale={spec.width}:{spec.height}",
                 "-c:v", "libx264", "-preset", "veryfast", "-crf", "20", "-c:a", "copy", str(out)],
                check=True,
            )
        return RenderResult(path=out, width=spec.width, height=spec.height, duration_ms=duration_ms(out))
