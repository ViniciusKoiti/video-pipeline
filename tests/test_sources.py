"""RF5 (fontes): um registro para as três entradas, id sob lock, sem duplicar, sem substituir aprovada e com
recuperação definida quando o registro falha no meio."""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

import pytest

from app.pipeline.gates import record_decision
from app.pipeline.models.extracted_source import ExtractedSource
from app.pipeline.models.source_draft import SourceDraft
from app.pipeline.ports import EpisodeLocked, ImmutableManifest
from app.pipeline.protection import ReviewWriteGuard
from app.pipeline.reopen import reopen_gate
from app.pipeline.schemas import Decision, SourceKind, SourcesManifest, Step
from app.pipeline.sources import (
    SourceError,
    SourceRegistry,
    declared,
    fetch_url,
    from_bytes,
    from_file,
)
from app.storage.json_files import JsonFileStore, JsonReviewGate

EP = "ep-fontes"
HTML = (
    b"<html><body><nav>menu</nav><p>Primeiro   paragrafo.</p><p>Segundo.</p>"
    b"<script>x()</script></body></html>"
)
NOW = datetime(2026, 11, 1, 12, 0, tzinfo=UTC)


def pdf_text(path: Path) -> str:
    assert path.read_bytes().startswith(b"%PDF-")
    return "Linha um do\npdf.\n\nSegundo bloco.\n"


def draft(url: str | None = "https://exemplo.org/a", **kw: object) -> SourceDraft:
    base = {"title": "Fonte A", "kind": SourceKind.SECONDARY, "url": url}
    return SourceDraft(**{**base, **kw})  # type: ignore[arg-type]


class Env:
    def __init__(self, tmp_path: Path, *, init: bool = True) -> None:
        self.store = JsonFileStore(tmp_path / "episodes")
        self.review = JsonReviewGate(self.store)
        self.guard = ReviewWriteGuard(self.store, self.review)
        self.registry = SourceRegistry(self.store, self.guard, lambda: NOW)
        if init:
            self.store.write(EP, "sources.json", SourcesManifest(episode_id=EP, sources=[]))
            self.store.path(EP, "facts.json").write_text("{}")

    def ids(self) -> list[str]:
        return [s.id for s in self.store.read(EP, "sources.json", SourcesManifest).sources]

    def files(self) -> list[str]:
        folder = self.store.path(EP, "")
        found = (p.relative_to(folder) for p in folder.rglob("*") if p.is_file() and p.name != ".lock")
        return sorted(str(p) for p in found)

    def approve(self) -> None:
        record_decision(
            self.store, self.review, EP, Step.SOURCES, Decision.APPROVED, reviewer="Dono", now=lambda: NOW
        )


@pytest.fixture
def env(tmp_path: Path) -> Env:
    return Env(tmp_path)


def html() -> ExtractedSource:
    return from_bytes(HTML, pdf_text)


# --- As três entradas viram o mesmo valor -------------------------------------------------------


def test_html_pdf_and_declared_text_share_one_extracted_shape(tmp_path: Path) -> None:
    page = from_bytes(HTML, pdf_text)
    assert (page.suffix, page.paragraphs) == (
        "html",
        ("Primeiro paragrafo.", "Segundo."),
    )  # sem nav nem script
    pdf = from_bytes(b"%PDF-1.4 ...", pdf_text)
    assert (pdf.suffix, pdf.paragraphs) == ("pdf", ("Linha um do pdf.", "Segundo bloco."))
    note = tmp_path / "nota.md"
    note.write_text("2  ovos\n\n  1 colher de sopa\n")
    mine = declared(note)
    assert (mine.suffix, mine.paragraphs) == ("md", ("2 ovos", "1 colher de sopa"))  # uma linha, um trecho
    saved = tmp_path / "a.pdf"
    saved.write_bytes(b"%PDF-1.4 ...")
    assert from_file(saved, pdf_text).paragraphs == pdf.paragraphs  # o PDF salvo à mão


def test_fetch_downloads_outside_the_episode_and_empty_text_is_refused(tmp_path: Path) -> None:
    seen: list[str] = []

    def download(url: str, dest: Path) -> Path:
        seen.append(url)
        dest.write_bytes(HTML)
        return dest

    assert fetch_url("https://exemplo.org/a", download, pdf_text).paragraphs[0] == "Primeiro paragrafo."
    assert seen == ["https://exemplo.org/a"]
    with pytest.raises(SourceError, match="nenhum texto"):
        from_bytes(b"<html><script>x()</script></html>", pdf_text)
    with pytest.raises(SourceError, match="não existe"):
        from_file(tmp_path / "nada.pdf", pdf_text)
    with pytest.raises(SourceError, match="não existe"):
        declared(tmp_path / "nada.md")


# --- Registro -----------------------------------------------------------------------------------


def test_register_writes_original_text_and_excerpts_then_the_manifest(env: Env) -> None:
    result = env.registry.register(EP, draft(authors=("Silva, Ana",), interested=True, notes="n"), html())
    assert result.created and result.source.id == "source-01"
    assert env.files() == [
        "excerpts/source-01.md",
        "facts.json",
        "sources.json",
        "sources/raw/source-01.html",
        "sources/source-01.txt",
    ]
    assert env.store.path(EP, "sources/source-01.txt").read_text() == "Primeiro paragrafo.\n\nSegundo.\n"
    assert "[source-01#E1] Primeiro paragrafo." in env.store.path(EP, "excerpts/source-01.md").read_text()
    [stored] = env.store.read(EP, "sources.json", SourcesManifest).sources
    assert (stored.authors, stored.interested, stored.notes, stored.retrieved_at) == (
        ["Silva, Ana"],
        True,
        "n",
        NOW,
    )


def test_the_id_is_the_next_free_one_even_with_gaps(env: Env) -> None:
    for url in ("https://exemplo.org/a", "https://exemplo.org/b"):
        env.registry.register(EP, draft(url), html())
    manifest = env.store.read(EP, "sources.json", SourcesManifest)
    env.store.write(EP, "sources.json", manifest.model_copy(update={"sources": manifest.sources[1:]}))
    assert env.registry.register(EP, draft("https://exemplo.org/c"), html()).source.id == "source-03"


def test_two_registries_never_repeat_an_id(tmp_path: Path) -> None:
    first, second = Env(tmp_path), Env(tmp_path, init=False)  # dois "processos" sobre o mesmo episódio
    one = first.registry.register(EP, draft("https://exemplo.org/a"), html()).source.id
    two = second.registry.register(EP, draft("https://exemplo.org/b"), html()).source.id
    assert (one, two) == ("source-01", "source-02")


def test_the_registry_holds_the_episode_lock(env: Env) -> None:
    with env.store.lock(EP), pytest.raises(EpisodeLocked):
        env.registry.register(EP, draft(), html())
    assert env.ids() == []


def test_repeating_a_url_or_a_declared_text_does_not_duplicate_or_overwrite(env: Env, tmp_path: Path) -> None:
    first = env.registry.register(EP, draft(title="Original"), html())
    before = env.files()
    again = env.registry.register(EP, draft(title="Outro título", notes="novo"), html())
    assert (again.created, again.source) == (False, first.source)  # o metadado novo não substitui
    note = tmp_path / "nota.md"
    note.write_text("um\ndois\n")
    mine = SourceDraft(title="Nota", kind=SourceKind.DECLARED)
    one = env.registry.register(EP, mine, declared(note))
    two = env.registry.register(EP, mine, declared(note))
    assert (one.created, two.created, two.source.id) == (True, False, one.source.id)
    note.write_text("um\ndois\ntrês\n")
    assert env.registry.register(EP, mine, declared(note)).created  # outro texto: outra fonte
    assert env.files() != before and env.ids() == ["source-01", "source-02", "source-03"]
    assert env.store.read(EP, "sources.json", SourcesManifest).sources[1].url is None


def test_an_approved_gate_one_refuses_before_writing_anything_and_reopening_allows_it(env: Env) -> None:
    env.registry.register(EP, draft(), html())
    env.approve()
    files = env.files()
    with pytest.raises(ImmutableManifest, match="gate de sources"):
        env.registry.register(EP, draft("https://exemplo.org/nova"), html())
    assert env.files() == files and env.ids() == ["source-01"]  # nem raw, nem texto, nem trechos
    assert not env.registry.register(EP, draft(), html()).created  # repetir a já aprovada não escreve
    reopen_gate(
        env.store, env.review, EP, Step.SOURCES, reviewer="Dono", reason="fonte nova", now=lambda: NOW
    )
    assert env.registry.register(EP, draft("https://exemplo.org/nova"), html()).source.id == "source-02"


# --- Falha no meio ------------------------------------------------------------------------------


@pytest.mark.parametrize("fail_at", ["text", "excerpts", "manifest"])
def test_a_failure_before_the_manifest_leaves_no_source_and_the_retry_recovers(
    env: Env, monkeypatch: pytest.MonkeyPatch, fail_at: str
) -> None:
    from app.pipeline import sources

    manifest_before = env.store.path(EP, "sources.json").read_bytes()
    real_write, real_store_write = sources.write_atomic, env.store.write

    def boom_atomic(path: Path, data: bytes) -> None:
        if (fail_at == "text" and path.suffix == ".txt") or (fail_at == "excerpts" and path.suffix == ".md"):
            raise OSError("disco cheio")
        real_write(path, data)

    def boom_store(episode_id: str, name: str, manifest: object) -> None:
        raise OSError("disco cheio")

    monkeypatch.setattr(sources, "write_atomic", boom_atomic)
    if fail_at == "manifest":
        monkeypatch.setattr(env.store, "write", boom_store)
    with pytest.raises(OSError, match="disco cheio"):
        env.registry.register(EP, draft(), html())
    monkeypatch.setattr(sources, "write_atomic", real_write)
    monkeypatch.setattr(env.store, "write", real_store_write)
    assert env.store.path(EP, "sources.json").read_bytes() == manifest_before  # a fonte não existe
    assert not list(env.store.path(EP, "").rglob(".*.partial"))  # nenhum temporário sobra
    result = env.registry.register(EP, draft(), html())  # a retomada reaproveita o id e sobrescreve a sobra
    assert (result.created, result.source.id, env.ids()) == (True, "source-01", ["source-01"])
    assert env.store.path(EP, "sources/source-01.txt").read_text() == "Primeiro paragrafo.\n\nSegundo.\n"


def test_an_orphan_original_with_another_suffix_is_cleaned_on_retry(env: Env) -> None:
    orphan = env.store.path(EP, "sources/raw/source-01.pdf")
    orphan.parent.mkdir(parents=True)
    orphan.write_bytes(b"%PDF- sobra de uma tentativa que nao chegou ao manifesto")
    env.registry.register(EP, draft(), html())
    assert [p for p in env.files() if "raw" in p] == ["sources/raw/source-01.html"]


def test_the_manifest_is_published_last(env: Env, monkeypatch: pytest.MonkeyPatch) -> None:
    present: list[list[str]] = []
    real = env.store.write

    def spy(episode_id: str, name: str, manifest: object) -> None:
        present.append(env.files())
        real(episode_id, name, manifest)  # type: ignore[arg-type]

    monkeypatch.setattr(env.store, "write", spy)
    env.registry.register(EP, draft(), html())
    assert {"sources/raw/source-01.html", "sources/source-01.txt", "excerpts/source-01.md"} <= set(present[0])
