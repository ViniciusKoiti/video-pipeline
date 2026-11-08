"""RF5 (briefs): a cópia do resumo valida antes de escrever, não troca por engano e não perde o anterior."""

from __future__ import annotations

from pathlib import Path

import pytest

from app.pipeline.briefs import BriefError, format_spec, install_brief, radar_spec
from app.pipeline.models.brief_action import BriefAction
from app.pipeline.numbers import FormatBrief
from app.pipeline.ports import EpisodeLocked
from app.storage.json_files import JsonFileStore
from tests.test_numbers import brief as format_brief
from tests.test_radar import brief as radar_brief

EP = "ep-brief"


@pytest.fixture
def store(tmp_path: Path) -> JsonFileStore:
    store = JsonFileStore(tmp_path / "episodes")
    store.path(EP, "").mkdir(parents=True)
    return store


def radar_text(niche: str = "exemplo", generated_at: str = "2026-10-12T03:21:19+00:00") -> str:
    return radar_brief(niche=niche, generated_at=generated_at).model_dump_json(indent=2, by_alias=True)


def format_text(nicho: str = "teste", data: str = "2026-10-18") -> str:
    raw = format_brief("voce_por_mil", 9.0, 4.0, "pattern").model_dump(mode="json", by_alias=True)
    brief = FormatBrief.model_validate({**raw, "nicho": nicho, "data": data})
    return brief.model_dump_json(indent=2, by_alias=True)


def names(store: JsonFileStore) -> list[str]:
    return sorted(p.name for p in store.path(EP, "").iterdir() if p.name != ".lock")


SPECS = [
    pytest.param(radar_spec, radar_text, "radar-brief.json", id="radar"),
    pytest.param(format_spec, format_text, "formato-brief.json", id="formato"),
]


@pytest.mark.parametrize(("spec", "make", "file"), SPECS)
def test_a_new_brief_is_installed_and_the_same_one_changes_nothing(
    store: JsonFileStore, spec, make, file
) -> None:  # type: ignore[no-untyped-def]
    first = install_brief(store, EP, spec(), make())
    assert (first.action, first.archived, names(store)) == (BriefAction.INSTALLED, None, [file])
    before = store.path(EP, file).read_bytes()
    again = install_brief(store, EP, spec(), make())
    assert again.action is BriefAction.UNCHANGED and store.path(EP, file).read_bytes() == before
    assert names(store) == [file]


@pytest.mark.parametrize(("spec", "make", "file"), SPECS)
def test_another_brief_is_refused_without_replace_and_names_what_is_there(
    store: JsonFileStore, spec, make, file
) -> None:  # type: ignore[no-untyped-def]
    install_brief(store, EP, spec(), make())
    kept = store.path(EP, file).read_bytes()
    other = make("outro") if spec is radar_spec else make("outro")
    with pytest.raises(BriefError, match=rf"{file} já tem outro conteúdo \(.*\); use --atualizar"):
        install_brief(store, EP, spec(), other)
    assert store.path(EP, file).read_bytes() == kept and names(store) == [file]


def test_replace_keeps_the_previous_one_with_its_own_date_in_the_name(store: JsonFileStore) -> None:
    install_brief(store, EP, radar_spec(), radar_text("velho", "2026-10-01T12:00:00+00:00"))
    result = install_brief(
        store, EP, radar_spec(), radar_text("novo", "2026-10-12T03:21:19+00:00"), replace=True
    )
    assert (result.action, result.archived) == (BriefAction.REPLACED, "radar-brief.20261001-120000.json")
    assert '"niche": "velho"' in store.path(EP, "radar-brief.20261001-120000.json").read_text()
    assert '"niche": "novo"' in store.path(EP, "radar-brief.json").read_text()


def test_two_replacements_with_the_same_date_never_overwrite_a_kept_one(store: JsonFileStore) -> None:
    """O nome do guardado só tem a data: dois perfis do mesmo dia perdiam o primeiro."""
    install_brief(store, EP, format_spec(), format_text("a", "2026-10-18"))
    install_brief(store, EP, format_spec(), format_text("b", "2026-10-18"), replace=True)  # guarda o "a"
    third = install_brief(
        store, EP, format_spec(), format_text("c", "2026-10-19"), replace=True
    )  # guarda o "b"
    assert third.archived == "formato-brief-2026-10-18.2.json"
    assert '"nicho": "a"' in store.path(EP, "formato-brief-2026-10-18.json").read_text()
    assert '"nicho": "b"' in store.path(EP, "formato-brief-2026-10-18.2.json").read_text()
    assert names(store) == [
        "formato-brief-2026-10-18.2.json",
        "formato-brief-2026-10-18.json",
        "formato-brief.json",
    ]


def test_a_content_already_kept_is_reused_not_duplicated(store: JsonFileStore) -> None:
    """Uma tentativa que guardou o anterior e parou antes da troca, repetida, não cria um segundo guardado."""
    install_brief(store, EP, format_spec(), format_text("a", "2026-10-18"))
    store.path(EP, "formato-brief-2026-10-18.json").write_text(
        store.path(EP, "formato-brief.json").read_text()
    )
    result = install_brief(store, EP, format_spec(), format_text("b", "2026-10-19"), replace=True)
    assert result.archived == "formato-brief-2026-10-18.json"
    assert names(store) == ["formato-brief-2026-10-18.json", "formato-brief.json"]


def test_an_unreadable_current_brief_is_kept_by_hash_when_replaced(store: JsonFileStore) -> None:
    store.path(EP, "radar-brief.json").write_text("{isto nao e um resumo", encoding="utf-8")
    with pytest.raises(BriefError, match="ilegível"):
        install_brief(store, EP, radar_spec(), radar_text())
    result = install_brief(store, EP, radar_spec(), radar_text(), replace=True)
    assert result.archived is not None and result.archived.startswith("radar-brief.")
    assert store.path(EP, result.archived).read_text() == "{isto nao e um resumo"


@pytest.mark.parametrize(
    ("spec", "text"), [(radar_spec, '{"schema": "outro"}'), (format_spec, "[1, 2]"), (radar_spec, "")]
)
def test_a_brief_outside_the_contract_is_refused_before_any_write(store: JsonFileStore, spec, text) -> None:  # type: ignore[no-untyped-def]
    with pytest.raises(BriefError, match="fora do contrato"):
        install_brief(store, EP, spec(), text, replace=True)
    assert names(store) == []


def test_a_missing_episode_is_an_error_and_its_folder_is_not_created(tmp_path: Path) -> None:
    store = JsonFileStore(tmp_path / "episodes")
    with pytest.raises(BriefError, match="episódio ep-fantasma não existe"):
        install_brief(store, "ep-fantasma", radar_spec(), radar_text())
    assert not (tmp_path / "episodes" / "ep-fantasma").exists()


def test_a_failure_during_the_swap_keeps_the_current_brief_and_the_retry_recovers(
    store: JsonFileStore, monkeypatch: pytest.MonkeyPatch
) -> None:
    from app.pipeline import briefs

    install_brief(store, EP, format_spec(), format_text("a", "2026-10-18"))
    current = store.path(EP, "formato-brief.json").read_bytes()
    real = briefs.write_atomic
    calls: list[str] = []

    def boom(path: Path, data: bytes) -> None:
        calls.append(path.name)
        if path.name == "formato-brief.json":
            raise OSError("disco cheio")
        real(path, data)

    monkeypatch.setattr(briefs, "write_atomic", boom)
    with pytest.raises(OSError, match="disco cheio"):
        install_brief(store, EP, format_spec(), format_text("b", "2026-10-19"), replace=True)
    assert calls == ["formato-brief-2026-10-18.json", "formato-brief.json"]  # o guardado vem antes da troca
    assert store.path(EP, "formato-brief.json").read_bytes() == current  # nunca um episódio sem resumo
    monkeypatch.setattr(briefs, "write_atomic", real)
    result = install_brief(store, EP, format_spec(), format_text("b", "2026-10-19"), replace=True)
    assert result.archived == "formato-brief-2026-10-18.json"  # reaproveitou o que a tentativa já guardou
    assert not list(store.path(EP, "").glob(".*.partial"))


def test_the_episode_lock_is_exclusive_for_the_copy(store: JsonFileStore) -> None:
    with store.lock(EP), pytest.raises(EpisodeLocked):
        install_brief(store, EP, radar_spec(), radar_text())
    assert names(store) == []
