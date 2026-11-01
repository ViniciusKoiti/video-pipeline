"""RF7: `vp metricas` (iniciar, ler, pendentes e tabela); sem rede, com o registro do Postiz de mentira."""

from __future__ import annotations

from datetime import date
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.cli import HANDLERS, build_parser
from app.commands.errors import run as handled
from app.pipeline.metrics import load_metrics
from tests.test_metrics import EPISODE, PUBLISHED, registry


@pytest.fixture
def root(tmp_path: Path) -> Path:
    registry(tmp_path)
    (tmp_path / "data" / "episodes" / EPISODE).mkdir(parents=True)
    return tmp_path


def run(root: Path, *argv: str) -> int:
    """O caminho real do comando: parser do `vp`, `HANDLERS` e o handler central de erros (ADR 045)."""
    args = build_parser().parse_args(["metricas", *argv])
    context = SimpleNamespace(settings=SimpleNamespace(data_dir=root / "data"))
    return handled("vp metricas", lambda: HANDLERS["metricas"](args, context))  # type: ignore[arg-type]


def episode_file(root: Path) -> Path:
    return root / "data" / "episodes" / EPISODE / "metrics.json"


def start(root: Path, *extra: str, publication: str = EPISODE) -> int:
    return run(root, "iniciar", publication, "--platform", "youtube", "--format", "longo", *extra)


def read(root: Path, *extra: str, window: str = "d7") -> int:
    base = ["--read-at", "2026-10-27", "--views", "1500", "--comments", "3", "--ctr", "4.2"]
    return run(root, "ler", EPISODE, window, *base, *extra)


def test_iniciar_takes_date_channel_and_post_from_the_postiz_registry_and_never_overwrites(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert start(root, "--hypothesis", "abertura com pergunta") == 0
    assert "registro do Postiz" in capsys.readouterr().out
    saved = load_metrics(episode_file(root))
    assert (
        saved.published_at == PUBLISHED and saved.post_id == "post-1" and saved.channel == "Cena e Conceito"
    )
    assert saved.hypothesis == "abertura com pergunta" and saved.readings == {}
    assert start(root) == 1
    assert "vp metricas: já existe:" in capsys.readouterr().err


def test_iniciar_without_a_known_date_or_channel_is_an_error_and_flags_complete_it(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    other = "sem-registro"
    assert start(root, publication=other) == 1
    assert "sem --published-at e sem agendamento deste id" in capsys.readouterr().err
    when = PUBLISHED.isoformat()
    assert start(root, "--published-at", when, publication=other) == 1
    assert "sem --channel e sem canal no registro" in capsys.readouterr().err
    assert start(root, "--published-at", when, "--channel", "Nabote Songs", publication=other) == 0
    assert (root / "data" / "publicacoes" / "metricas" / f"{other}.json").is_file()  # sem pasta de episódio
    assert "flags" in capsys.readouterr().out


def test_ler_records_the_window_with_sources_and_requests_and_refuses_a_second_reading(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert start(root) == 0
    capsys.readouterr()
    extra = ["--origem", "Navegação=42", "--origem", "Sugeridos=31", "--pedido", "duvida: como achar o livro"]
    assert read(root, *extra) == 0
    window = load_metrics(episode_file(root))
    d7 = window.readings["d7"]
    assert (d7.views, d7.ctr_percent, d7.likes) == (1500, 4.2, None)  # o que não veio fica nulo, nunca zero
    assert [(s.name, s.percent) for s in d7.traffic_sources] == [("Navegação", 42.0), ("Sugeridos", 31.0)]
    assert (window.requests[0].kind, window.requests[0].date) == ("duvida", date(2026, 10, 27))
    capsys.readouterr()
    assert read(root, "--views", "1") == 1
    assert "d7 já lida em 2026-10-27; use --refazer" in capsys.readouterr().err
    assert read(root, "--views", "1", "--refazer") == 0
    after = load_metrics(episode_file(root))
    assert after.readings["d7"].views == 1 and len(after.requests) == 1


def test_ler_refuses_a_missing_file_and_a_window_that_has_not_closed(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    assert run(root, "ler", "ninguem", "d7", "--views", "1") == 1
    err = capsys.readouterr().err
    assert "não existe:" in err and "vp metricas iniciar" in err
    assert start(root) == 0
    capsys.readouterr()
    assert run(root, "ler", EPISODE, "d28", "--read-at", "2026-11-01", "--views", "9") == 1
    assert "recusado: leitura d28 em 2026-11-01: a janela só fecha em" in capsys.readouterr().err
    assert load_metrics(episode_file(root)).readings == {}  # nada foi gravado


def test_pendentes_and_tabela_cover_every_publication(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert run(root, "pendentes") == 0
    assert "nenhum metrics.json" in capsys.readouterr().out
    assert start(root) == 0
    assert (
        start(root, "--published-at", PUBLISHED.isoformat(), "--channel", "Nabote Songs", publication="clipe")
        == 0
    )
    assert read(root) == 0
    capsys.readouterr()
    assert run(root, "pendentes", "--hoje", "2026-11-20") == 0
    assert "vencidas e não lidas: 3" in capsys.readouterr().out  # d28 do episódio, d7 e d28 do clipe
    assert run(root, "tabela") == 0
    assert (root / "data" / "publicacoes" / "metricas.csv").is_file()
    assert "2 publicação(ões), 4 linha(s)" in capsys.readouterr().out


def test_a_malformed_source_or_request_is_a_usage_error_from_argparse(
    root: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    for option, value in (
        ("--origem", "sem igual"),
        ("--origem", "Navegação=muito"),
        ("--pedido", "sem dois pontos"),
    ):
        with pytest.raises(SystemExit) as usage:
            build_parser().parse_args(["metricas", "ler", EPISODE, "d7", option, value])
        assert usage.value.code == 2
    assert "origem sem '='" in capsys.readouterr().err


def test_tabela_writes_where_saida_says(root: Path, capsys: pytest.CaptureFixture[str]) -> None:
    assert start(root) == 0
    out = root / "fora" / "tabela.csv"
    assert run(root, "tabela", "--saida", str(out)) == 0
    assert out.is_file() and not (root / "data" / "publicacoes" / "metricas.csv").exists()
    assert f"{out}: 1 publicação(ões), 2 linha(s)" in capsys.readouterr().out
