"""Efeitos sonoros (ADR 035): do `sfx.json` de um vídeo aos efeitos colocados na junção.

O catálogo é o SFX Kit (CC0, sintetizado em código) que o dono clona em `data/sfx/kit/`; o `sounds.json`
dele é lido direto, com o `sha256` de cada WAV conferido antes do uso (§2.3). Cada efeito (cue) se ancora numa
cena do vídeo por JSON e, dentro dela, num trecho da narração (como os planos, ADR 008) ou num deslocamento em
segundos; o tempo sai do começo real da cena e da duração real da fala. O som começa no momento menos o
`sync.at` do kit (o ponto dele que encontra o momento) e desce `under_voiceover_db` onde o corpo cai sobre a
fala. O código confere o que não depende de ouvir; quem ouve é o dono, na prévia.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from pydantic import Field

from app.media.narration import strip_pauses, timeline_length, timeline_position
from app.pipeline.schemas import Model

SFX_DIR = "sfx"  # em data/: o kit clonado em kit/
KIT_DIR = "kit"
KIT_INDEX = "sounds.json"
SFX_PLAN_FILE = "sfx.json"  # na pasta do vídeo
KIT_VOICE_REFERENCE_LUFS = -16.0  # o kit foi nivelado para uma voz a −16 LUFS (GUIDE.md, §3)
MAX_GAIN_DB = 6.0
MAX_CUES_PER_10S = 8  # acima disso é ruído, não acabamento
COVERS_SPEECH = "On top of speech"  # prefixo do `avoid_for` dos sons que cobrem a voz


class SfxSound(Model):
    """O que usamos do registro de um som no `sounds.json` do kit."""

    id: str
    file: str
    duration: float
    sync_at: float
    meets: str
    onset: float
    body_end: float
    under_voiceover_db: float
    avoid_for: list[str] = []
    fits_seconds: tuple[float, float] | None = None
    sha256: str

    @property
    def covers_speech(self) -> bool:
        return any(a.startswith(COVERS_SPEECH) for a in self.avoid_for)


class SfxKit(Model):
    root: Path
    license: str
    sounds: dict[str, SfxSound]

    def path(self, sound: SfxSound) -> Path:
        return self.root / sound.file

    def file_problem(self, sound: SfxSound) -> str | None:
        path = self.path(sound)
        if not path.is_file():
            return f"{sound.id}: falta o arquivo {sound.file} no kit"
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != sound.sha256:
            return f"{sound.id}: o arquivo não bate com o sha256 do kit"
        return None


def load_kit(data_dir: Path) -> SfxKit | None:
    """O SFX Kit em `data/sfx/kit/`; sem o `sounds.json`, None."""
    root = data_dir / SFX_DIR / KIT_DIR
    index = root / KIT_INDEX
    if not index.is_file():
        return None
    data = json.loads(index.read_text(encoding="utf-8"))
    sounds = {}
    for record in data["sounds"]:
        fits = record.get("fits_seconds")
        sounds[record["id"]] = SfxSound(
            id=record["id"],
            file=record["file"],
            duration=record["duration"],
            sync_at=record["sync"]["at"],
            meets=record["sync"]["meets"],
            onset=record["timing"]["onset"],
            body_end=record["timing"]["body_end"],
            under_voiceover_db=record["under_voiceover_db"],
            avoid_for=record.get("avoid_for", []),
            fits_seconds=tuple(fits) if fits else None,
            sha256=record["sha256"],
        )
    return SfxKit(root=root, license=str(data.get("license", "")), sounds=sounds)


class SfxCue(Model):
    """Um efeito: o som do kit no momento de uma cena. O momento é o começo da cena, mais a posição de `text`
    na fala (quando há), mais `offset_s`."""

    sound: str
    scene: str
    text: str | None = None
    offset_s: float = 0.0
    gain_db: float = Field(default=0.0, le=MAX_GAIN_DB)
    note: str | None = None  # o que acontece na tela nesse momento


class SfxPlan(Model):
    """`sfx.json`: os efeitos de um vídeo, escritos por quem monta o Short; o código confere e coloca."""

    cues: list[SfxCue]


class Speech(Model):
    """A fala de uma cena na junção: começa no começo da cena e dura `seconds`."""

    seconds: float


class PlacedSfx(Model):
    sound: str
    file: Path
    moment_s: float  # o que o som encontra
    start_s: float  # onde o arquivo começa na linha do tempo (nunca negativo)
    trim_s: float  # quanto cortar do começo do arquivo quando o início cairia antes de 0
    gain_db: float
    under_speech: bool


def _moment(cue: SfxCue, scene_start: float, narration: str | None, speech: Speech | None) -> float | None:
    """O momento do efeito em segundos; None se a âncora de texto não existe na fala."""
    moment = scene_start
    if cue.text is not None:
        if narration is None or speech is None:
            return None
        spoken = strip_pauses(narration)
        found = spoken.find(cue.text)
        if found < 0:
            return None
        total = timeline_length(narration)
        moment += timeline_position(narration, found) / total * speech.seconds if total else 0.0
    return moment + cue.offset_s


def plan_problems(
    plan: SfxPlan,
    kit: SfxKit | None,
    scene_starts: Mapping[str, float],
    scene_durations: Mapping[str, float],
    narrations: Mapping[str, str],
    speeches: Mapping[str, Speech],
    check_files: bool = True,
) -> tuple[list[str], list[str]]:
    """(erros, alertas) do plano: sons e cenas que existem, âncoras na fala, sons que cobrem a voz sobre a
    fala, momentos fora da cena e densidade."""
    errors: list[str] = []
    warnings: list[str] = []
    if kit is None:
        return ["sfx: falta o SFX Kit em data/sfx/kit/ (clone de https://github.com/wyzowl/sfx-kit)"], []
    checked: dict[str, str | None] = {}
    moments: list[float] = []
    for n, cue in enumerate(plan.cues, start=1):
        label = f"sfx.json, efeito {n} ({cue.sound} em {cue.scene})"
        sound = kit.sounds.get(cue.sound)
        if sound is None:
            errors.append(f"{label}: som fora do kit")
            continue
        if check_files and cue.sound not in checked:
            checked[cue.sound] = kit.file_problem(sound)
        if checked.get(cue.sound):
            errors.append(f"sfx.json: {checked[cue.sound]}")
        if cue.scene not in scene_starts:
            errors.append(f"{label}: a cena não existe no vídeo")
            continue
        speech = speeches.get(cue.scene)
        moment = _moment(cue, scene_starts[cue.scene], narrations.get(cue.scene), speech)
        if moment is None:
            errors.append(f"{label}: {cue.text!r} não aparece na fala da cena")
            continue
        scene_end = scene_starts[cue.scene] + scene_durations[cue.scene]
        if moment < scene_starts[cue.scene] - 1e-6 or moment > scene_end + 1e-6:
            errors.append(f"{label}: o momento ({moment:.2f} s) cai fora da cena")
            continue
        moments.append(moment)
        if speech and sound.covers_speech:
            body = (moment - sound.sync_at + sound.onset, moment - sound.sync_at + sound.body_end)
            spoken = (scene_starts[cue.scene], scene_starts[cue.scene] + speech.seconds)
            if body[0] < spoken[1] and spoken[0] < body[1]:
                warnings.append(f"{label}: o kit diz que esse som cobre a voz, e ele cai sobre a fala")
    moments.sort()
    for i, moment in enumerate(moments):
        window = [m for m in moments[i:] if m < moment + 10]
        if len(window) > MAX_CUES_PER_10S:
            warnings.append(
                f"sfx.json: {len(window)} efeitos em 10 s a partir de {moment:.1f} s "
                f"(mais de {MAX_CUES_PER_10S})"
            )
            break
    return errors, warnings


def resolve_sfx(
    plan: SfxPlan,
    kit: SfxKit,
    scene_starts: Mapping[str, float],
    narrations: Mapping[str, str],
    speeches: Mapping[str, Speech],
    voice_lufs: float | None = None,
) -> list[PlacedSfx]:
    """Onde cada arquivo começa e com que ganho. `voice_lufs`: a loudness medida da voz, para manter a relação
    que o kit assume (voz a −16 LUFS): voz mais baixa que isso baixa os efeitos junto."""
    reference = 0.0 if voice_lufs is None else voice_lufs - KIT_VOICE_REFERENCE_LUFS
    spans = [
        (scene_starts[s], scene_starts[s] + sp.seconds) for s, sp in speeches.items() if s in scene_starts
    ]
    placed = []
    for cue in plan.cues:
        sound = kit.sounds[cue.sound]
        moment = _moment(cue, scene_starts[cue.scene], narrations.get(cue.scene), speeches.get(cue.scene))
        if moment is None:
            raise ValueError(f"sfx {cue.sound}: {cue.text!r} não aparece na fala de {cue.scene}")
        start = moment - sound.sync_at
        trim = max(0.0, -start)
        start = max(0.0, start)
        body = (start + max(0.0, sound.onset - trim), start + max(0.0, sound.body_end - trim))
        under = any(body[0] < end and begin < body[1] for begin, end in spans)
        gain = cue.gain_db + reference + (sound.under_voiceover_db if under else 0.0)
        placed.append(
            PlacedSfx(
                sound=cue.sound,
                file=kit.path(sound),
                moment_s=round(moment, 3),
                start_s=round(start, 3),
                trim_s=round(trim, 3),
                gain_db=round(gain, 1),
                under_speech=under,
            )
        )
    return placed
