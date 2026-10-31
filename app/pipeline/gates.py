"""Gates humanos das etapas feitas por agente ou por pessoa (ADR 009): o que cada decisão carimba e se vale.

O `review.json` é a fonte da verdade (§5). Cada decisão guarda o `input_hash` do que foi revisto; se o
conteúdo muda depois, a decisão deixa de valer e `vp status` mostra isso.

- gate 1 (`sources`): `sources.json` + `facts.json`;
- gate 2 (`script`): `scenes.json` + `outline.md`. Aprovar exige um parecer "approved" do verificador
  (`checagem.json`, gravado por `vp checagem`) sobre as fichas e o roteiro atuais; sem ele, só com o motivo
  do dono (`--sem-checagem`), que vai para as notas da decisão. A escolha da imagem de cada plano
  (`asset_id`) e o bloco de números gerado no `outline.md` (`vp numeros`) ficam fora do carimbo e do parecer:
  trocar uma imagem invalida só a montagem e a prévia (§5), e o bloco sai do `scenes.json`, já carimbado;
- gate 3 (`assets`), por ativo: o arquivo de mídia em `assets/<id>.<ext>`. Aprovar reflete `review_status`
  no `assets/<id>.json`, e o schema recusa sem licença, crédito, `sha256` ou conferência (ADR 007);
- gate 4 (`preview`): o render mais acabado (`renders/final.mp4`, senão `renders/preview.mp4`), o
  `episode.json`, a legenda e o texto do post, quando existem. Aprovar a prévia e depois renderizar o final
  (voz final, legenda refeita) faz o gate mudar: a versão final é revista de novo (#120);
- gate de tradução (`translation`, ADR 034), só em pasta com `traducao.json`: a narração traduzida, o vínculo
  e o original de que ela vem. Aprovar exige que a conferência em código (`vp traducao`) não ache problema.

`missing_pieces` lista o que falta para o vídeo estar pronto e não é gate: hoje, a legenda do vertical.
"""

from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass
from pathlib import Path

from pydantic import ValidationError

from app.pipeline.numbers import strip_block
from app.pipeline.ports import ManifestNotFound, ManifestStore, ReviewGate
from app.pipeline.schemas import (
    Asset,
    CheckEntry,
    CheckLog,
    CheckVerdict,
    Decision,
    EpisodeManifest,
    ReviewEntry,
    Status,
    Step,
)
from app.pipeline.state import Clock, compute_input_hash
from app.pipeline.translation import LINK_FILE, translation_hash, translation_problems

GATE_FILES: dict[Step, tuple[str, ...]] = {
    Step.SOURCES: ("sources.json", "facts.json"),
    Step.SCRIPT: ("scenes.json", "outline.md"),
}
RENDERS = ("renders/final.mp4", "renders/preview.mp4")  # o gate 4 revê o mais acabado
PREVIEW_FILES = ("episode.json", "captions.srt", "legenda-post.txt")  # entram no gate 4 quando existem
GATED_STEPS = (*GATE_FILES, Step.ASSETS, Step.TRANSLATION, Step.PREVIEW)
AUDIO_SUFFIXES = (".mp3", ".m4a", ".wav", ".ogg")  # faixas da trilha, aprovadas no gate 3 (ADR 030)
MEDIA_SUFFIXES = (".jpg", ".jpeg", ".png", ".webp", ".mp4", ".webm", *AUDIO_SUFFIXES)
CHECK_FILE = "checagem.json"
CHECKED_FILES = ("facts.json", "scenes.json", "outline.md")  # o que o verificador confere contra os trechos
ASSET_ID = re.compile(rb'("asset_id"\s*:\s*)"(?:[^"\\]|\\.)*"')  # a imagem escolhida para o plano


class GateError(ValueError):
    pass


@dataclass(frozen=True)
class GateStatus:
    step: Step
    asset_id: str | None
    entry: ReviewEntry | None  # última decisão; None = nenhuma
    current_hash: str | None  # None = o que foi revisto não existe mais
    legacy_hash: str | None = None  # carimbo de antes de a imagem sair do gate 2 (decisões já gravadas)

    @property
    def valid(self) -> bool:
        accepted = {self.current_hash, self.legacy_hash} - {None}
        return self.entry is not None and self.entry.input_hash in accepted


def gate_hash(store: ManifestStore, episode_id: str, step: Step, asset_id: str | None = None) -> str:
    """Hash do que o humano revê nesse gate; mesmo conteúdo, mesmo hash."""
    if step is Step.ASSETS:
        if asset_id is None:
            raise GateError("a etapa assets decide ativo por ativo: informe --asset")
        return "sha256:" + _file_sha256(_media_path(store, episode_id, asset_id))
    if asset_id is not None:
        raise GateError("--asset só vale para a etapa assets")
    if step is Step.PREVIEW:
        return compute_input_hash(_preview_paths(store, episode_id), {}, base=store.path(episode_id, ""))
    if step is Step.TRANSLATION:
        if not store.path(episode_id, LINK_FILE).is_file():
            raise GateError(f"{episode_id}: sem {LINK_FILE}, não é uma tradução (ADR 034)")
        try:
            return translation_hash(store, episode_id)
        except (ManifestNotFound, ValueError) as error:
            raise GateError(f"{episode_id}: {LINK_FILE} inválido ou sem o original ({error})") from None
    names = GATE_FILES.get(step)
    if names is None:
        raise GateError(f"a etapa {step.value} ainda não tem gate por comando")
    paths = [store.path(episode_id, name) for name in names]
    missing = [p.name for p in paths if not p.is_file()]
    if missing:
        raise GateError(f"{episode_id}: faltam {', '.join(missing)} para o gate de {step.value}")
    return content_hash(paths, base=store.path(episode_id, ""))


def content_hash(paths: list[Path], *, base: Path) -> str:
    """Como `compute_input_hash`, sem o que é derivado ou escolhido depois do roteiro: no `scenes.json`, todo
    `asset_id` conta como `null`; no `outline.md`, o bloco de números gerado (`vp numeros`) não conta. Um
    roteiro sem imagens e sem bloco tem o mesmo hash de antes."""
    digest = hashlib.sha256()
    for path in sorted(paths):
        data = path.read_bytes()
        if path.name == "scenes.json":
            data = ASSET_ID.sub(rb"\1null", data)
        elif path.name == "outline.md":
            data = strip_block(data)  # os números gerados saem do scenes.json, já carimbado (#170)
        digest.update(path.relative_to(base).as_posix().encode() + b"\0")
        digest.update(hashlib.sha256(data).digest())
    digest.update(json.dumps({}).encode())
    return "sha256:" + digest.hexdigest()


def record_decision(
    store: ManifestStore,
    review: ReviewGate,
    episode_id: str,
    step: Step,
    decision: Decision,
    *,
    reviewer: str,
    now: Clock,
    asset_id: str | None = None,
    notes: str = "",
    skip_check: str | None = None,
) -> ReviewEntry:
    """Grava a decisão humana no review.json; aprovar um ativo também reflete `review_status` no JSON dele.

    Aprovar o gate 2 pede o parecer do verificador sobre o conteúdo atual, ou o motivo em `skip_check`.
    """
    with store.lock(episode_id):
        input_hash = gate_hash(store, episode_id, step, asset_id)
        if step is Step.SCRIPT and decision is Decision.APPROVED and not check_is_current(store, episode_id):
            if not (skip_check and skip_check.strip()):
                raise GateError(
                    f"{episode_id}: o gate 2 pede o parecer do verificador sobre as fichas e o roteiro "
                    'atuais (rode o agente verificador e `vp checagem`), ou --sem-checagem "motivo"'
                )
            notes = "; ".join(filter(None, [notes, f"sem checagem: {skip_check.strip()}"]))
        if step is Step.TRANSLATION and decision is Decision.APPROVED:
            problems = translation_problems(store, episode_id)
            if problems:
                raise GateError(
                    f"{episode_id}: a conferência da tradução achou {len(problems)} problema(s), "
                    f"rode `vp traducao {episode_id}`: " + "; ".join(problems)
                )
        approved_asset = None
        if asset_id is not None and decision is Decision.APPROVED:
            approved_asset = _approved(store, review, episode_id, asset_id, input_hash)
        entry = ReviewEntry(
            step=step,
            asset_id=asset_id,
            decision=decision,
            reviewer=reviewer,
            at=now(),
            input_hash=input_hash,
            notes=notes,
        )
        review.record(episode_id, entry)
        if approved_asset is not None:
            store.write(episode_id, f"assets/{asset_id}.json", approved_asset)
        return entry


def check_hash(store: ManifestStore, episode_id: str) -> str:
    paths = [store.path(episode_id, name) for name in CHECKED_FILES]
    present = [p for p in paths if p.is_file()]
    if not any(p.name == "scenes.json" for p in present):
        raise GateError(f"{episode_id}: falta scenes.json para o parecer do verificador")
    return content_hash(present, base=store.path(episode_id, ""))


def _legacy_check_hash(store: ManifestStore, episode_id: str) -> str:
    present = [p for p in (store.path(episode_id, name) for name in CHECKED_FILES) if p.is_file()]
    return compute_input_hash(present, {}, base=store.path(episode_id, ""))


def check_log(store: ManifestStore, episode_id: str) -> CheckLog:
    try:
        return store.read(episode_id, CHECK_FILE, CheckLog)
    except ManifestNotFound:
        return CheckLog(episode_id=episode_id)


def record_check(
    store: ManifestStore,
    episode_id: str,
    verdict: CheckVerdict,
    problems: list[str],
    *,
    reviewer: str,
    now: Clock,
) -> CheckEntry:
    """Acrescenta o parecer do verificador ao `checagem.json`, carimbado com o conteúdo conferido."""
    with store.lock(episode_id):
        input_hash = check_hash(store, episode_id)
        entry = CheckEntry(
            verdict=verdict, problems=problems, reviewer=reviewer, at=now(), input_hash=input_hash
        )
        log = check_log(store, episode_id)
        store.write(episode_id, CHECK_FILE, log.model_copy(update={"entries": [*log.entries, entry]}))
        return entry


def latest_check(store: ManifestStore, episode_id: str) -> tuple[CheckEntry | None, bool]:
    """Último parecer e se ele ainda vale (mesmas fichas e roteiro)."""
    entries = check_log(store, episode_id).entries
    if not entries:
        return None, False
    entry = max(entries, key=lambda e: e.at)
    try:
        current = check_hash(store, episode_id)
    except GateError:
        return entry, False
    return entry, entry.input_hash in (current, _legacy_check_hash(store, episode_id))


def check_is_current(store: ManifestStore, episode_id: str) -> bool:
    entry, valid = latest_check(store, episode_id)
    return entry is not None and entry.verdict is CheckVerdict.APPROVED and valid


def gate_report(store: ManifestStore, review: ReviewGate, episode_id: str) -> list[GateStatus]:
    """Última decisão de cada gate e de cada ativo (os que existem e os que só estão no review.json)."""
    log = review.log(episode_id)
    targets: list[tuple[Step, str | None]] = [(step, None) for step in GATE_FILES]
    on_disk = {p.stem for p in store.path(episode_id, "assets").glob("*.json")}
    decided = {e.asset_id for e in log.entries if e.step is Step.ASSETS and e.asset_id}
    targets += [(Step.ASSETS, asset_id) for asset_id in sorted(on_disk | decided)]
    if store.path(episode_id, LINK_FILE).is_file():
        targets.append((Step.TRANSLATION, None))
    targets.append((Step.PREVIEW, None))
    return [
        GateStatus(
            step,
            asset,
            log.latest(step, asset_id=asset),
            _current(store, episode_id, step, asset),
            _legacy(store, episode_id, step),
        )
        for step, asset in targets
    ]


def missing_pieces(store: ManifestStore, episode_id: str) -> list[str]:
    """O que falta no vídeo montado, fora dos gates: no vertical, a legenda queimada (ADR 014 e 021)."""
    path = store.path(episode_id, "episode.json")
    if not path.is_file():
        return []
    episode = EpisodeManifest.model_validate_json(path.read_text())
    captions = episode.captions and store.path(episode_id, episode.captions)
    if episode.video.portrait and not (captions and captions.is_file()):
        return ["legenda (captions.srt)"]
    return []


def _preview_paths(store: ManifestStore, episode_id: str) -> list[Path]:
    render = next((store.path(episode_id, r) for r in RENDERS if store.path(episode_id, r).is_file()), None)
    if render is None:
        raise GateError(f"{episode_id}: nenhum render em renders/ para o gate da prévia")
    extras = [store.path(episode_id, name) for name in PREVIEW_FILES]
    return [render, *(p for p in extras if p.is_file())]


def _approved(
    store: ManifestStore, review: ReviewGate, episode_id: str, asset_id: str, input_hash: str
) -> Asset | None:
    """O ativo aprovado para gravar, ou None quando o JSON já vem aprovado de outro episódio (ativo
    reaproveitado): o arquivo fica como está (§2.6) e só a decisão deste episódio vai para o review.json."""
    asset = store.read(episode_id, f"assets/{asset_id}.json", Asset)
    if asset.sha256 is None or f"sha256:{asset.sha256}" != input_hash:
        raise GateError(f"{asset_id}: o arquivo de mídia não bate com o sha256 do JSON (baixado de novo?)")
    if asset.review_status is Status.APPROVED:
        here = any(
            e.asset_id == asset_id and e.decision is Decision.APPROVED and e.input_hash == input_hash
            for e in review.log(episode_id).entries
        )
        if here:
            raise GateError(f"{asset_id} já está aprovado")
        return None
    try:
        return Asset.model_validate({**asset.model_dump(), "review_status": Status.APPROVED})
    except ValidationError as error:
        problems = "; ".join(e["msg"].removeprefix("Value error, ") for e in error.errors())
        raise GateError(f"{asset_id}: {problems}") from None


def _current(store: ManifestStore, episode_id: str, step: Step, asset_id: str | None = None) -> str | None:
    try:
        return gate_hash(store, episode_id, step, asset_id)
    except GateError:
        return None


def _legacy(store: ManifestStore, episode_id: str, step: Step) -> str | None:
    """O hash dos arquivos inteiros, como era gravado antes (decisões antigas continuam valendo)."""
    names = GATE_FILES.get(step)
    paths = [store.path(episode_id, name) for name in names or ()]
    if not paths or not all(p.is_file() for p in paths):
        return None
    return compute_input_hash(paths, {}, base=store.path(episode_id, ""))


def _media_path(store: ManifestStore, episode_id: str, asset_id: str) -> Path:
    for suffix in MEDIA_SUFFIXES:
        path = store.path(episode_id, f"assets/{asset_id}{suffix}")
        if path.is_file():
            return path
    raise GateError(f"{asset_id}: nenhum arquivo de mídia em assets/")


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()
