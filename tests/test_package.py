"""RF6 (pacote): o vídeo e o texto do gate 4 são validados antes de escrever e só valem completos."""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.media.probe import ProbeError
from app.pipeline.gates import record_decision
from app.pipeline.models.package_action import PackageAction
from app.pipeline.package import PackageError, PackagePublisher, package_problems, read_post
from app.pipeline.ports import EpisodeLocked, ImmutableManifest
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.reopen import reopen_gate
from app.pipeline.schemas import Decision, Step
from app.storage.json_files import JsonFileStore, JsonReviewGate

EP = "short-teste-pt"
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)


def post_json(caption: str = "Legenda do Short.", title: str | None = "Título do Short") -> dict:
    settings = {"title": title} if title is not None else {}
    return {"posts": [{"settings": settings, "value": [{"content": caption}]}]}


class Env:
    def __init__(self, tmp_path: Path) -> None:
        self.store = JsonFileStore(tmp_path / "episodes")
        self.review = JsonReviewGate(self.store)
        self.measure = lambda path: 12.5
        self.publisher = PackagePublisher(
            self.store, ReviewWriteGuard(self.store, self.review), self._measure
        )
        self.video = tmp_path / "entrega.mp4"
        self.video.write_bytes(b"video-v1")
        self.post = self.write_post(post_json())

    def _measure(self, path: Path) -> float:
        return self.measure(path)

    def write_post(self, data: object) -> Path:
        path = self.video.parent / "post.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def publish(self) -> PackageAction:
        return self.publisher.publish(EP, self.video, self.post)

    def path(self, name: str) -> Path:
        return self.store.path(EP, name)

    def files(self) -> list[str]:
        folder = self.store.path(EP, "")
        if not folder.is_dir():
            return []
        return sorted(
            str(p.relative_to(folder)) for p in folder.rglob("*") if p.is_file() and p.name != ".lock"
        )

    def approve(self) -> None:
        record_decision(
            self.store, self.review, EP, Step.PREVIEW, Decision.APPROVED, reviewer="Dono", now=lambda: NOW
        )


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


# --- O texto do post ------------------------------------------------------------------------------


def test_the_post_text_is_title_blank_line_caption_and_without_title_only_the_caption(tmp_path: Path) -> None:
    path = tmp_path / "post.json"
    path.write_text(json.dumps(post_json()))
    assert read_post(path).render() == "Título do Short\n\nLegenda do Short.\n"
    path.write_text(json.dumps(post_json(title=None)))
    assert read_post(path).render() == "Legenda do Short.\n"
    path.write_text(json.dumps(post_json(title="")))
    assert read_post(path).title is None  # título vazio é sem título


@pytest.mark.parametrize(
    ("raw", "match"),
    [
        ('{"posts": []}', "falta posts"),
        ('{"posts": "x"}', "falta posts"),
        ('{"posts": [1]}', "falta posts"),
        ('{"posts": [{"value": []}]}', "falta posts"),
        ('{"posts": [{"value": [{"content": "  "}]}]}', "falta posts"),
        ('{"posts": [{"value": [{"content": 7}]}]}', "falta posts"),
        ('{"posts": [{"settings": {"title": 3}, "value": [{"content": "ok"}]}]}', "title deve ser um texto"),
        ("[1, 2]", "falta posts"),
        ("{isto nao e json", "JSON inválido"),
    ],
)
def test_a_post_outside_the_contract_is_a_package_error(tmp_path: Path, raw: str, match: str) -> None:
    path = tmp_path / "post.json"
    path.write_text(raw)
    with pytest.raises(PackageError, match=f"post.json: .*{match}"):
        read_post(path)


# --- Montar o pacote ------------------------------------------------------------------------------


def test_a_new_package_writes_video_text_and_a_complete_marker(env: Env) -> None:
    assert env.publish() is PackageAction.PUBLISHED
    assert env.files() == ["legenda-post.txt", "renders/final.mp4", "renders/pacote.json"]
    assert env.path("renders/final.mp4").read_bytes() == b"video-v1"
    assert env.path("legenda-post.txt").read_text() == "Título do Short\n\nLegenda do Short.\n"
    assert json.loads(env.path("renders/pacote.json").read_text())["state"] == "complete"
    assert package_problems(env.store, EP) == []


def test_the_same_video_and_text_write_nothing(env: Env) -> None:
    env.publish()
    stamps = {n: env.path(n).stat().st_mtime_ns for n in env.files()}
    assert env.publish() is PackageAction.UNCHANGED
    assert {n: env.path(n).stat().st_mtime_ns for n in env.files()} == stamps


@pytest.mark.parametrize("what", ["video", "text"])
def test_a_changed_video_or_text_replaces_the_package_as_a_whole(env: Env, what: str) -> None:
    env.publish()
    if what == "video":
        env.video.write_bytes(b"video-v2")
    else:
        env.post = env.write_post(post_json(caption="Outra legenda."))
    assert env.publish() is PackageAction.PUBLISHED and package_problems(env.store, EP) == []
    assert env.path("renders/final.mp4").read_bytes() == (b"video-v2" if what == "video" else b"video-v1")
    assert ("Outra legenda." in env.path("legenda-post.txt").read_text()) is (what == "text")


# --- Validar antes de escrever --------------------------------------------------------------------


@pytest.mark.parametrize("bad", ["Ep Inválido", "ep_x", "-ep", "ep--x", "", "EP"])
def test_an_invalid_episode_id_is_refused_before_anything_is_created(env: Env, bad: str) -> None:
    with pytest.raises(PackageError, match="id de episódio inválido"):
        env.publisher.publish(bad, env.video, env.post)
    assert not (env.store.path("", "").parent / "episodes" / bad).exists() or bad == ""


def test_a_bad_video_is_refused_before_anything_is_written(env: Env, tmp_path: Path) -> None:
    empty, wrong, missing = tmp_path / "vazio.mp4", tmp_path / "video.mov", tmp_path / "nada.mp4"
    empty.write_bytes(b"")
    wrong.write_bytes(b"x")
    for video in (empty, wrong, missing):
        with pytest.raises(PackageError, match="arquivo .mp4 existente e não vazio"):
            env.publisher.publish(EP, video, env.post)
    env.measure = lambda path: 0.0
    with pytest.raises(PackageError, match="não mede mais que zero"):
        env.publish()

    def unreadable(path: Path) -> float:
        raise ProbeError("ffprobe não leu")

    env.measure = unreadable
    with pytest.raises(PackageError, match="o ffprobe não leu o vídeo"):
        env.publish()
    assert env.files() == []


def test_a_bad_post_never_leaves_a_new_video_beside_an_old_text(env: Env) -> None:
    """O defeito de antes: o vídeo era copiado antes de ler o post, e um JSON ruim misturava o pacote."""
    env.publish()
    env.video.write_bytes(b"video-v2")
    env.post = env.write_post({"posts": []})
    with pytest.raises(PackageError, match="falta posts"):
        env.publish()
    assert env.path("renders/final.mp4").read_bytes() == b"video-v1"  # o pacote anterior segue inteiro
    assert package_problems(env.store, EP) == []


# --- O gate 4 aprovado ----------------------------------------------------------------------------


def test_an_approved_package_refuses_a_swap_before_the_first_copy_and_reopening_allows_it(env: Env) -> None:
    env.publish()
    env.approve()
    before = {n: env.path(n).read_bytes() for n in env.files()}
    env.video.write_bytes(b"video-v2")
    with pytest.raises(ImmutableManifest, match="renders/final.mp4 está carimbado pelo gate de preview"):
        env.publish()
    assert {n: env.path(n).read_bytes() for n in env.files()} == before  # nem o marcador mudou
    env.video.write_bytes(b"video-v1")
    env.post = env.write_post(post_json(caption="Texto novo."))
    with pytest.raises(ImmutableManifest, match="legenda-post.txt"):
        env.publish()
    assert {n: env.path(n).read_bytes() for n in env.files()} == before
    reopen_gate(
        env.store, env.review, EP, Step.PREVIEW, reviewer="Dono", reason="trocar a legenda", now=lambda: NOW
    )
    assert env.publish() is PackageAction.PUBLISHED
    assert "Texto novo." in env.path("legenda-post.txt").read_text()


def test_repeating_the_same_package_after_the_approval_is_not_an_error(env: Env) -> None:
    env.publish()
    env.approve()
    assert env.publish() is PackageAction.UNCHANGED


# --- Falha no meio --------------------------------------------------------------------------------


@pytest.mark.parametrize("fail_at", ["video", "text", "marker"])
def test_a_failure_in_the_middle_never_counts_as_a_complete_package_and_the_retry_finishes(
    env: Env, monkeypatch: pytest.MonkeyPatch, fail_at: str
) -> None:
    from app.pipeline import package

    real = package.write_atomic
    state = {"markers": 0}

    def boom(path: Path, data: bytes) -> None:
        if path.name == "final.mp4" and fail_at == "video":
            raise OSError("disco cheio")
        if path.name == "legenda-post.txt" and fail_at == "text":
            raise OSError("disco cheio")
        if path.name == "pacote.json":
            state["markers"] += 1
            if state["markers"] == 2 and fail_at == "marker":
                raise OSError("disco cheio")
        real(path, data)

    monkeypatch.setattr(package, "write_atomic", boom)
    with pytest.raises(OSError, match="disco cheio"):
        env.publish()
    assert package_problems(env.store, EP) == ["a gravação do pacote foi interrompida: rode o `gate` de novo"]
    assert not list(env.store.path(EP, "").rglob(".*.partial"))  # nenhum temporário sobra
    monkeypatch.setattr(package, "write_atomic", real)
    assert env.publish() is PackageAction.PUBLISHED and package_problems(env.store, EP) == []
    assert env.path("renders/final.mp4").read_bytes() == b"video-v1"


def test_a_package_changed_by_hand_after_it_was_made_is_reported(env: Env) -> None:
    env.publish()
    env.path("renders/final.mp4").write_bytes(b"outro video")
    env.path("legenda-post.txt").write_text("outra legenda")
    assert package_problems(env.store, EP) == [
        "renders/final.mp4 não é o do pacote (mudou depois de montado): refaça o pacote",
        "legenda-post.txt não é o do pacote (mudou depois de montado): refaça o pacote",
    ]


def test_an_episode_without_a_marker_is_a_legacy_package_and_a_broken_marker_is_reported(env: Env) -> None:
    assert package_problems(env.store, EP) == []  # sem marcador: anterior a esta regra
    env.publish()
    env.path("renders/pacote.json").write_text("{isto nao e json")
    assert "ilegível" in package_problems(env.store, EP)[0]


def test_the_episode_lock_is_exclusive_for_the_package(env: Env) -> None:
    with env.store.lock(EP), pytest.raises(EpisodeLocked):
        env.publish()
    assert "renders/final.mp4" not in env.files()


# --- O comando `vp short gate` ------------------------------------------------------------------------------


def test_the_gate_command_builds_the_package_and_stops_with_a_message_when_approved(
    env: Env, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    from types import SimpleNamespace

    from app.cli import HANDLERS, build_parser
    from app.commands.errors import run

    context = SimpleNamespace(store=env.store, review=env.review)
    monkeypatch.setattr("app.commands.short_gate.duration_ms", lambda path: 12_500)
    argv = ["short", "gate", str(env.video), str(env.post), "--episodio", EP]

    def gate() -> int:
        return run("vp short", lambda: HANDLERS["short"](build_parser().parse_args(argv), context))  # type: ignore[arg-type]

    assert gate() == 0
    out = capsys.readouterr().out
    assert "gate:" in out and "(12.5 s)" in out and "pacote montado" in out
    assert f"vp approve {EP} --step preview" in out and f"vp postiz pacote {env.post} --episode {EP}" in out
    assert gate() == 0
    assert "já estava igual" in capsys.readouterr().out
    env.approve()
    env.video.write_bytes(b"video-v2")
    assert gate() == 1
    assert "carimbado pelo gate de preview" in capsys.readouterr().err
    assert env.path("renders/final.mp4").read_bytes() == b"video-v1"
