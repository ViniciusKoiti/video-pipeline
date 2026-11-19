"""`vp short checar`, `vp short conferir` e `vp short voz --refazer` (emenda de 2026-11-17 da ADR 062): as
conferências do longo nas linhas da narração do Short, sem rede, sem TTS real e com reconhecedor falso."""

from __future__ import annotations

import json
import shutil
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from tests.fakes import FakeBatchTTS
from tests.test_short_command import make, voz
from tests.test_speech_review import Recognizer

LINES = [
    {"scene": "gancho", "text": "O HashMap guarda tudo em baldes.", "delivery": "hook"},
    {"scene": None, "text": "E quando dois caem no mesmo: o que acontece?"},
    {"scene": "final", "text": "Eu digo isso como opinião: use o padrão.", "delivery": "invite"},
]


def short(tmp_path: Path, lines: list[dict[str, object]] = LINES) -> tuple[Path, Path, SimpleNamespace]:
    folder, narration, context = make(tmp_path, final_name="chatterbox_modal")
    narration.write_text(json.dumps({"language": "pt-BR", "lines": lines}), encoding="utf-8")
    return folder, narration, context


def verb(context: SimpleNamespace, name: str, folder: Path, narration: Path) -> int:
    args = build_parser().parse_args(["short", name, str(folder), str(narration)])
    return handled("vp short", lambda: HANDLERS["short"](args, context))  # type: ignore[arg-type]


def glossary(folder: Path, *terms: dict[str, str]) -> None:
    (folder / "voice").mkdir(exist_ok=True)
    (folder / "voice" / "glossary.json").write_text(json.dumps({"termos": list(terms)}), encoding="utf-8")


def test_checar_points_the_term_the_colon_and_fails_on_the_opinion_label(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = short(tmp_path)
    assert verb(context, "checar", folder, narration) == 1
    out = capsys.readouterr().out
    assert "atenção glossário: 1 termo(s) de fora sem entrada em voice/glossary.json: HashMap" in out
    assert "alerta  fora-1: dois-pontos antes de pergunta" in out
    assert "erro    final: rótulo de opinião ('como opinião')" in out
    assert out.strip().endswith("texto do Short: 3 fala(s), 1 erro(s); 1 ponto(s) de atenção")


def test_checar_passes_with_the_glossary_and_asks_ipa_only_for_the_azure_voice(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = short(tmp_path, LINES[:1])
    glossary(folder, {"escrita": "HashMap", "fala": "réch mép"})
    assert verb(context, "checar", folder, narration) == 0
    assert capsys.readouterr().out.strip() == "texto do Short: 1 fala(s), sem erros"
    context.settings.providers.tts_final = "azure_speech"
    assert verb(context, "checar", folder, narration) == 0
    assert "falta `ipa` em: HashMap" in capsys.readouterr().out


def test_voz_warns_before_the_voice_and_still_speaks(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = short(tmp_path)
    assert voz(context, folder, narration) == 0
    out = capsys.readouterr().out.splitlines()
    assert out[0].startswith("alerta  fora-1") and any(line.startswith("erro    final") for line in out[:3])
    assert len(context.tts_final.calls) == 1  # a porta do texto é o `checar`; a voz não para


def stems(folder: Path) -> dict[str, str]:
    record = json.loads((folder / "narracao.pt.voz.json").read_text(encoding="utf-8"))
    ids = ["gancho", "fora-1", "final"]
    return {line_id: Path(item["wav"]).stem for line_id, item in zip(ids, record["lines"], strict=True)}


@pytest.mark.skipif(shutil.which("ffmpeg") is None, reason="sem ffmpeg")
def test_conferir_hears_each_line_writes_the_report_per_narration_and_the_sheet(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = short(tmp_path)
    glossary(folder, {"escrita": "HashMap", "fala": "réch mép"})
    assert voz(context, folder, narration) == 0
    names = stems(folder)
    context.speech_checker = Recognizer({
        names["gancho"]: "o hash map guarda tudo em baldes",  # o som da grafia: passa
        names["fora-1"]: "e quando dois caem no mesmo o que acontece",
        names["final"]: "eu digo isso como opinião use o padre",
    })
    context.tts_final = FakeBatchTTS()
    capsys.readouterr()
    assert verb(context, "conferir", folder, narration) == 0
    out = capsys.readouterr().out
    assert context.tts_final.calls == [] and context.speech_checker.prompts == ["", "", ""]
    assert "1 trecho(s) para ouvir; voice/conferencia-narracao.pt.json" in out
    assert '"padrão."' in out and '-> ouvido "padre"' in out
    assert f"vp short voz {folder} {narration} --refazer final" in out
    report = json.loads((folder / "voice/conferencia-narracao.pt.json").read_text())
    assert [scene["scene_id"] for scene in report["scenes"]] == ["gancho", "fora-1", "final"]
    assert (folder / "voice/conferencia-narracao.pt-escuta.wav").is_file()


def test_conferir_without_the_voice_record_says_to_run_the_voice(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = short(tmp_path)
    context.speech_checker = Recognizer({})
    assert verb(context, "conferir", folder, narration) == 1
    assert "falta narracao.pt.voz.json: rode `vp short voz` antes de conferir" in capsys.readouterr().err


def test_conferir_refuses_a_narration_changed_after_the_voice(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = short(tmp_path)
    assert voz(context, folder, narration) == 0
    changed = [dict(LINES[0], text="O HashMap mudou."), *LINES[1:]]
    narration.write_text(json.dumps({"language": "pt-BR", "lines": changed}), encoding="utf-8")
    context.speech_checker = Recognizer({})
    assert verb(context, "conferir", folder, narration) == 1
    assert "não bate com a narração" in capsys.readouterr().err


def test_voz_refazer_sets_the_take_aside_and_speaks_only_that_line_again(tmp_path: Path) -> None:
    folder, narration, context = short(tmp_path)
    assert voz(context, folder, narration) == 0
    before = sorted(p.name for p in (folder / "voice").glob("*.wav"))
    context.tts_final = FakeBatchTTS()
    assert voz(context, folder, narration, "--refazer", "fora-1") == 0
    assert len(context.tts_final.calls) == 1
    assert [name.split("-fake")[0] for name in context.tts_final.calls[0]] == ["fora-1"]
    assert sorted(p.name for p in (folder / "voice").glob("*.wav")) == before  # mesmo texto, mesmo nome
    rejected = [p.name for p in (folder / "voice" / "tomadas-recusadas").rglob("*.wav")]
    assert rejected == [name for name in before if name.startswith("fora-1-")]


def test_voz_refazer_refuses_a_line_that_is_not_in_the_narration(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    folder, narration, context = short(tmp_path)
    assert voz(context, folder, narration) == 0
    assert voz(context, folder, narration, "--refazer", "fora-9") == 1
    assert "fora do roteiro: fora-9" in capsys.readouterr().err
