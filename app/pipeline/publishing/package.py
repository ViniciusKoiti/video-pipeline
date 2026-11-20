"""O pacote de vídeo e texto do gate 4 (RF6, ADR 050): `renders/final.mp4` e `legenda-post.txt`.

Montar o pacote é validar tudo **antes** de escrever e só então publicar:

- o vídeo existe, é MP4, não está vazio e mede mais que zero (ffprobe, injetado); o texto do post lê pelo
  contrato (legenda não vazia, título opcional); o id do episódio é válido. Falha aqui não escreve nada;
- o mesmo vídeo e o mesmo texto não escrevem nada; outro conteúdo passa pelo `WriteGuard` (ADR 039) **antes
  da primeira cópia**: com o gate 4 aprovado para os arquivos de hoje, a troca é recusada e manda reabrir;
- a publicação grava o marcador `renders/pacote.json` como `writing`, depois o vídeo e o texto (cada um
  inteiro, por temporário e conferido contra a origem) e só no fim o marcador `complete`. Uma falha no meio
  deixa o marcador `writing`: o pacote **não** conta como completo (`package_problems`), e repetir o comando
  termina. Episódio sem marcador (anterior a esta regra) segue valendo.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Callable
from pathlib import Path

from pydantic import ValidationError

from app.errors import PipelineError
from app.media.probe import ProbeError
from app.pipeline.atomic_files import write_atomic
from app.pipeline.constants.package_constants import PackageConstants as Constants
from app.pipeline.file_hash import sha256_file
from app.pipeline.models.package_action import PackageAction
from app.pipeline.models.package_marker import PackageMarker
from app.pipeline.models.post_text import PostText
from app.pipeline.ports import ManifestStore, WriteGuard


class PackageError(PipelineError, ValueError):
    """Pacote que não pode ser montado ou está incompleto; a mensagem diz o quê. Nada foi escrito."""


def read_post(path: Path) -> PostText:
    """O texto do primeiro post do JSON do Postiz: `posts[0].value[0].content` e o título opcional."""
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except OSError as error:
        raise PackageError(f"{path.name}: não foi possível ler ({error})") from error
    except ValueError as error:
        raise PackageError(f"{path.name}: JSON inválido ({error})") from error
    posts = data.get("posts") if isinstance(data, dict) else None
    entry = posts[0] if isinstance(posts, list) and posts else None
    values = entry.get("value") if isinstance(entry, dict) else None
    first = values[0] if isinstance(values, list) and values else None
    caption = first.get("content") if isinstance(first, dict) else None
    if not isinstance(caption, str) or not caption.strip():
        raise PackageError(f"{path.name}: falta posts[0].value[0].content (a legenda do post)")
    settings = entry.get("settings") if isinstance(entry, dict) else None
    title = settings.get("title") if isinstance(settings, dict) else None
    if title is not None and not isinstance(title, str):
        raise PackageError(f"{path.name}: posts[0].settings.title deve ser um texto")
    return PostText(title or None, caption)


def package_problems(store: ManifestStore, episode_id: str) -> list[str]:
    """O que impede o pacote de valer: gravação interrompida ou arquivo que não é mais o do marcador. Sem
    marcador (episódio anterior a esta regra), nada a dizer."""
    marker_path = store.path(episode_id, Constants.MARKER)
    if not marker_path.is_file():
        return []
    try:
        marker = PackageMarker.model_validate_json(marker_path.read_text(encoding="utf-8"))
    except ValidationError:
        return [f"{Constants.MARKER} ilegível: refaça o pacote"]
    if marker.state != "complete":
        return ["a gravação do pacote foi interrompida: rode o `gate` de novo"]
    problems = []
    for name, digest in ((Constants.VIDEO, marker.video_sha256), (Constants.TEXT, marker.text_sha256)):
        path = store.path(episode_id, name)
        if not path.is_file() or sha256_file(path) != digest:
            problems.append(f"{name} não é o do pacote (mudou depois de montado): refaça o pacote")
    return problems


class PackagePublisher:
    def __init__(self, store: ManifestStore, guard: WriteGuard, measure: Callable[[Path], float]) -> None:
        self._store, self._guard, self._measure = store, guard, measure  # `measure`: segundos do MP4

    def publish(self, episode_id: str, video: Path, post: Path) -> PackageAction:
        self._validate(episode_id, video)
        text = read_post(post).render().encode("utf-8")
        video_sha = sha256_file(video)
        text_sha = _sha(text)
        with self._store.lock(episode_id):
            final, caption = (self._store.path(episode_id, n) for n in (Constants.VIDEO, Constants.TEXT))
            if _same(final, video_sha) and _same_text(caption, text_sha):
                if self._marker_is_complete(episode_id, video_sha, text_sha) is not False:
                    return PackageAction.UNCHANGED
                self._write_marker(episode_id, "complete", video_sha, text_sha)  # só faltava o último passo
                return PackageAction.PUBLISHED
            # antes da primeira cópia: com o gate 4 aprovado, a troca é recusada
            if not _same(final, video_sha):
                self._guard.check(episode_id, Constants.VIDEO)
            if not _same_text(caption, text_sha):
                self._guard.check(episode_id, Constants.TEXT, text)
            self._write_marker(episode_id, "writing", video_sha, text_sha)
            write_atomic(final, video.read_bytes())
            if sha256_file(final) != video_sha:
                raise PackageError(f"{Constants.VIDEO}: a cópia não bate com o original; refaça o pacote")
            write_atomic(caption, text)
            self._write_marker(episode_id, "complete", video_sha, text_sha)
        return PackageAction.PUBLISHED

    def _validate(self, episode_id: str, video: Path) -> None:
        if not Constants.EPISODE_ID.match(episode_id):
            raise PackageError(f"id de episódio inválido: {episode_id!r}")
        if not video.is_file() or video.suffix.lower() != ".mp4" or video.stat().st_size == 0:
            raise PackageError(f"{video}: o vídeo deve ser um arquivo .mp4 existente e não vazio")
        try:
            seconds = self._measure(video)
        except ProbeError as error:
            raise PackageError(f"{video.name}: o ffprobe não leu o vídeo ({error})") from error
        if not seconds > 0:
            raise PackageError(f"{video.name}: o vídeo não mede mais que zero")

    def _marker_is_complete(self, episode_id: str, video_sha: str, text_sha: str) -> bool | None:
        """None: sem marcador (anterior à regra). True: completo e para este vídeo e texto. False: o resto."""
        path = self._store.path(episode_id, Constants.MARKER)
        if not path.is_file():
            return None
        try:
            marker = PackageMarker.model_validate_json(path.read_text(encoding="utf-8"))
        except ValidationError:
            return False
        return (marker.state, marker.video_sha256, marker.text_sha256) == ("complete", video_sha, text_sha)

    def _write_marker(self, episode_id: str, state: str, video_sha: str, text_sha: str) -> None:
        marker = PackageMarker(state=state, video_sha256=video_sha, text_sha256=text_sha)  # type: ignore[arg-type]
        write_atomic(
            self._store.path(episode_id, Constants.MARKER), marker.model_dump_json(indent=2).encode() + b"\n"
        )


def _sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _same(path: Path, digest: str) -> bool:
    return path.is_file() and sha256_file(path) == digest


def _same_text(path: Path, digest: str) -> bool:
    return path.is_file() and _sha(path.read_bytes()) == digest
