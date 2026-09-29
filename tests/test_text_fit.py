"""Texto que não cabe na peça da tela ou não dá para ler no tempo do plano (ADR 011, emenda de 2026-09-29)."""

from __future__ import annotations

from app.pipeline.schemas import (
    Claim,
    CompareShot,
    CompareSide,
    LowerThirdShot,
    NetworkEdge,
    NetworkNode,
    NetworkShot,
    NetworkStep,
    NumberShot,
    TimelineEvent,
    TimelineShot,
)
from app.pipeline.text_fit import (
    EDGE_LABEL_CHARS,
    NUMBER_OVER_MEDIA,
    lines,
    text_fit_warnings,
)

CLAIMS = [Claim(text="x", source_ids=["source-01"])]


def words(count: int, size: int = 5) -> str:
    return " ".join("a" * size for _ in range(count))


def number(label: str) -> NumberShot:
    return NumberShot(anchor="a", value="10", label=label, claims=CLAIMS)


def network(label: str, role: str = "", *, layout: str = "radial", edge_label: str = "",
            value: str = "") -> NetworkShot:
    return NetworkShot(
        anchor="a", root="raiz", layout=layout, claims=CLAIMS,  # type: ignore[arg-type]
        nodes=[NetworkNode(id="raiz", label="Raiz", kind="company"),
               NetworkNode(id="outro", label=label, role=role, kind="bank")],
        edges=[NetworkEdge.model_validate({"from": "outro", "to": "raiz", "label": edge_label, "value": value,
                                           "claims": [c.model_dump() for c in CLAIMS]})],
        steps=[NetworkStep(anchor="b", nodes=["outro"])],
    )


def test_lines_break_between_words() -> None:
    assert lines("abc def", 7) == 1
    assert lines("abc def", 6) == 2
    assert lines("palavragrandedemais", 5) == 1  # uma palavra maior que a linha ocupa uma
    assert lines("", 10) == 1


def test_number_over_media_fits_one_line_and_full_screen_two() -> None:
    per_line, _ = NUMBER_OVER_MEDIA
    one_line = words(per_line // 6)
    two_lines = words(per_line // 6 + 2)
    assert text_fit_warnings("S01", number(one_line), 3000, over_media=True) == []
    (warning,) = text_fit_warnings("S01", number(two_lines), 3000, over_media=True)
    assert warning.startswith("S01: texto do número sobre a imagem em 2 linhas, cabe 1")
    assert text_fit_warnings("S01", number(two_lines), 3000, over_media=False) == []


def test_compare_and_lower_third_labels() -> None:
    compare = CompareShot(anchor="a", claims=CLAIMS, left=CompareSide(value="1", label=words(20)),
                          right=CompareSide(value="2", label="curto"))
    (warning,) = text_fit_warnings("S02", compare, 5000, over_media=False)
    assert "texto da comparação" in warning
    tarja = LowerThirdShot(anchor="a", claims=CLAIMS, name=words(8), role="cargo")
    (warning,) = text_fit_warnings("S03", tarja, 3000, over_media=True)
    assert "nome da tarja em 2 linhas, cabe 1" in warning


def test_timeline_label_lines_and_reading_time() -> None:
    events = [TimelineEvent(date="1918", label=words(4)), TimelineEvent(date="1926", label=words(4))]
    shot = TimelineShot(anchor="a", claims=CLAIMS, events=events)
    assert text_fit_warnings("S04", shot, 4000, over_media=False) == []  # 46 caracteres em 4 s
    (reading,) = text_fit_warnings("S04", shot, 2000, over_media=False)  # 34 cabem em 2 s
    assert reading == "S04: linha do tempo com 46 caracteres de texto em ~2.0 s; dá para ler ~34"
    events = [TimelineEvent(date="1941", label=words(24)), TimelineEvent(date="1974", label="x")]
    long = TimelineShot(anchor="a", claims=CLAIMS, events=events)
    warnings = text_fit_warnings("S04", long, 60000, over_media=False)
    assert any("evento '1941' da linha do tempo em" in w for w in warnings)


def test_network_node_hanging_over_an_arrow() -> None:
    long_name, role = words(6), words(4)  # 35 caracteres: 2 linhas, mais o papel
    (warning,) = text_fit_warnings("S05", network(long_name, role), 6000, over_media=False)
    assert "ocupa 3 linhas com o papel, cabem 2" in warning
    # Nas camadas, só o nó de onde sai a seta pende sobre ela; aqui ele é `outro`, então conta.
    assert text_fit_warnings("S05", network(long_name, role, layout="layered"), 6000, over_media=False)
    assert text_fit_warnings("S05", network("Banco", role, layout="layered"), 6000, over_media=False) == []


def test_network_arrow_text_and_value() -> None:
    shot = network("Banco", edge_label="x" * (EDGE_LABEL_CHARS + 1), value="v" * 30)
    warnings = text_fit_warnings("S06", shot, 6000, over_media=False)
    assert [w.split(" com ")[0] for w in warnings] == [
        "S06: texto da seta outro→raiz", "S06: valor da seta outro→raiz",
    ]
