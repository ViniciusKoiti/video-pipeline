"""Cópia de cada fala com a cadência aplicada (`voice/paced/`): os silêncios refeitos pelo plano da cena.

O `silencedetect` do ffmpeg acha os silêncios. A cabeça vira exatamente `HEAD_S` de silêncio, a cauda vira o
intervalo planejado até a próxima cena e, dentro da cena, cada silêncio longo (fim de frase) vira o do plano,
mas só quando a quantidade deles bate com a de fins de frase do texto; senão ficam como estão e o relatório
diz. Em volta de cada corte fica `MARGIN_S` do áudio original, para não comer o fim nem o ataque da sílaba.
O WAV de origem não muda, e a cópia é refeita só quando a origem ou o plano mudam (o nome leva os dois).
"""

from __future__ import annotations

import hashlib
import re
import subprocess
import tempfile
import wave
from pathlib import Path

from app.errors import PipelineError
from app.media.constants.voice_pacing_constants import VoicePacingConstants as C
from app.media.models.scene_pacing import ScenePacing
from app.media.models.voice_pacing import VoicePacing
from app.media.probe import duration_ms
from app.media.wav import wav_is_valid

Edit = tuple[float, float, float]  # (início do corte, fim do corte, silêncio novo), em segundos


class VoicePacingError(PipelineError, RuntimeError):
    pass


def pacing_policy(pacing: VoicePacing) -> str:
    return f"cadencia-v{C.VERSION}:{pacing.model_dump_json()}"


def _ffmpeg(args: list[str], name: str) -> str:
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-nostdin", *args], capture_output=True, text=True, check=False
    )
    if result.returncode:
        raise VoicePacingError(f"{name}: falha ao aplicar a cadência: {result.stderr.strip()[-250:]}")
    return result.stderr


def silences(path: Path) -> tuple[list[tuple[float, float]], float]:
    """Todos os silêncios do WAV (inclusive os das pontas) e a duração, em segundos."""
    detect = f"silencedetect=noise={C.NOISE_DB}dB:d={C.MIN_SILENCE_S}"
    log = _ffmpeg(["-i", str(path), "-af", detect, "-f", "null", "-"], path.name)
    total = duration_ms(path) / 1000
    starts = [max(0.0, float(x)) for x in re.findall(r"silence_start: (-?[\d.]+)", log)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", log)]
    return list(zip(starts, [*ends, *[total] * (len(starts) - len(ends))], strict=True)), total


def edits(found: list[tuple[float, float]], total: float, plan: ScenePacing) -> tuple[list[Edit], str]:
    """Os cortes que levam os silêncios de `found` ao `plan`, e a nota do que se fez com os internos."""
    begin = next((end for start, end in found if start <= C.EDGE_S), 0.0)
    finish = next((start for start, end in found if end >= total - C.EDGE_S and start > begin), total)
    margin = C.MARGIN_S
    result: list[Edit] = [(0.0, max(0.0, begin - margin), max(0.0, C.HEAD_S - min(margin, begin)))]
    inner = [(s, e) for s, e in found if s > begin and e < finish and e - s >= C.SENTENCE_SILENCE_S]
    if len(inner) == len(plan.internal_s):
        note = f"internas={len(inner)}"
        for (start, end), target in zip(inner, plan.internal_s, strict=True):
            result.append((start + margin, end - margin, max(0.0, target - 2 * margin)))
    else:
        note = f"internas_mantidas({len(inner)}!={len(plan.internal_s)})"
    cut = min(total, finish + margin)
    result.append((cut, total, max(0.0, plan.tail_s - C.HEAD_S - margin)))
    return result, note


def _apply(source: Path, out: Path, cuts: list[Edit]) -> None:
    with wave.open(str(source), "rb") as reader:
        params = reader.getparams()
        data = reader.readframes(params.nframes)
    frame = params.nchannels * params.sampwidth
    rate = params.framerate

    def index(seconds: float) -> int:
        return min(params.nframes, max(0, round(seconds * rate))) * frame

    built = bytearray()
    cursor = 0
    for start, end, silence in sorted(cuts):
        built += data[cursor:max(cursor, index(start))]
        built += bytes(round(silence * rate) * frame)
        cursor = max(cursor, index(end))
    built += data[cursor:]
    with wave.open(str(out), "wb") as writer:
        writer.setparams(params)
        writer.writeframes(bytes(built))


def pace_voice(source: Path, plan: ScenePacing, folder: Path) -> tuple[Path, str]:
    """A cópia de `source` com a cadência de `plan`, em `folder`, e a nota sobre os silêncios internos."""
    if not wav_is_valid(source):
        raise VoicePacingError(f"{source.name}: WAV ausente ou inválido")
    found, total = silences(source)
    cuts, note = edits(found, total, plan)
    digest = hashlib.sha256(source.read_bytes()).hexdigest()
    key = hashlib.sha256(f"{digest}|v{C.VERSION}|{plan.policy()}".encode()).hexdigest()[:C.DIGEST_CHARS]
    out = folder / f"{source.stem}-{key}.wav"
    if wav_is_valid(out):
        return out, note
    folder.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=folder) as scratch:
        pcm = Path(scratch) / "pcm.wav"
        _ffmpeg(["-n", "-i", str(source), "-c:a", "pcm_s16le", str(pcm)], source.name)
        partial = Path(scratch) / "paced.wav"
        _apply(pcm, partial, cuts)
        if not wav_is_valid(partial):
            raise VoicePacingError(f"{source.name}: cópia com a cadência saiu vazia")
        partial.replace(out)
    return out, note
