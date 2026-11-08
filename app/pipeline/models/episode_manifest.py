from __future__ import annotations

from typing import Literal, Self

from pydantic import Field, model_validator

from app.pipeline.models._schemas_types import (
    EpisodeId,
    Language,
    NonEmpty,
    RelPath,
    _unique,
    portrait_problems,
    reels_shot_problems,
)
from app.pipeline.models.episode_format import EpisodeFormat
from app.pipeline.models.episode_music import EpisodeMusic
from app.pipeline.models.episode_scene import EpisodeScene
from app.pipeline.models.host_spec import HostSpec
from app.pipeline.models.model import Model
from app.pipeline.models.series import Series
from app.pipeline.models.video_spec import VideoSpec


class EpisodeManifest(Model):
    """Única entrada do motor de montagem (§6). Timing vem da duração real dos WAVs.
    Versões: 1 (ADR 001, um visual por cena) e 2 (ADR 008, lista de planos). Mudar exige nova ADR."""

    schema_version: Literal[1, 2] = 1
    episode_id: EpisodeId
    title: NonEmpty
    language: Language
    format: EpisodeFormat = EpisodeFormat.ARCHIVAL_DOCUMENTARY
    video: VideoSpec = Field(default_factory=VideoSpec)
    scenes: list[EpisodeScene] = Field(min_length=1)
    captions: RelPath | None = None  # captions.srt editável
    host: HostSpec | None = None  # apresentador em janela flutuante (ADR 013); só `explainer`
    series: Series | None = None  # selo do cartão final (ADR 028, emenda à ADR 026); só `explainer`
    music: list[EpisodeMusic] = []  # trilha sonora (ADR 030); só `explainer`; vazio = sem trilha

    @property
    def duration_ms(self) -> int:
        return self.scenes[-1].end_ms

    @model_validator(mode="after")
    def _ordered_timeline(self) -> Self:
        _unique([s.id for s in self.scenes], "ids de cena")
        with_shots = [bool(s.shots) for s in self.scenes]
        if self.schema_version == 1 and any(with_shots):
            raise ValueError("schema_version 1 não tem planos; use 2 (ADR 008)")
        if self.schema_version == 2 and not all(with_shots):
            raise ValueError("schema_version 2 exige planos em todas as cenas")
        if self.host is not None and self.format != EpisodeFormat.EXPLAINER:
            raise ValueError("host (apresentador) só existe no formato explainer (ADR 013)")
        if self.series is not None and self.format != EpisodeFormat.EXPLAINER:
            raise ValueError("series (selo do cartão final) só existe no formato explainer (ADR 028)")
        if self.music:
            if self.format != EpisodeFormat.EXPLAINER:
                raise ValueError("music (trilha) só existe no formato explainer (ADR 030)")
            if (last := max(m.end_ms for m in self.music)) > self.duration_ms:
                raise ValueError(f"trilha termina em {last} ms, depois do fim do vídeo")
            beds = sorted((m for m in self.music if m.role == "bed"), key=lambda m: m.start_ms)
            for previous_bed, current_bed in zip(beds, beds[1:], strict=False):
                if current_bed.start_ms < previous_bed.end_ms:
                    raise ValueError(f"fundos sobrepostos: {previous_bed.asset_id} e {current_bed.asset_id}")
        if self.video.portrait:
            if self.format != EpisodeFormat.EXPLAINER:
                raise ValueError("o perfil vertical (9:16) só existe no formato explainer (ADR 014)")
            problems = [
                p
                for scene in self.scenes
                for p in portrait_problems(scene.id, [shot.spec.kind for shot in scene.shots])
            ]
            if problems:
                raise ValueError("; ".join(problems))
        kinds = [(scene.id, [shot.spec.kind for shot in scene.shots]) for scene in self.scenes]
        if problems := reels_shot_problems(kinds, portrait=self.video.portrait):
            raise ValueError("; ".join(problems))
        for previous, current in zip(self.scenes, self.scenes[1:], strict=False):
            if current.start_ms < previous.end_ms:
                raise ValueError(f"cena {current.id} começa antes do fim de {previous.id}")
        return self
