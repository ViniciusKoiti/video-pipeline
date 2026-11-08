"""Read-only checks for this Short, including text fields omitted by vp medicao."""

import hashlib
import json
from pathlib import Path

from app.pipeline.translation import spoken_numbers

root = Path(__file__).resolve().parents[2]
render = Path(__file__).resolve().parent
text_fields = {"locale", "footer", "kicker", "text", "highlight", "title", "label", "sublabel"}


def nontext(value):
    if isinstance(value, dict):
        return {key: nontext(item) for key, item in value.items() if key not in text_fields}
    if isinstance(value, list):
        return [nontext(item) for item in value]
    return value


def visible_numbers(value, language):
    if isinstance(value, dict):
        for key, item in value.items():
            if key in text_fields and isinstance(item, str):
                yield from spoken_numbers(item, language)
            elif isinstance(item, (dict, list)):
                yield from visible_numbers(item, language)
    elif isinstance(value, list):
        for item in value:
            yield from visible_numbers(item, language)


contents = []
for lang, suffixes, limit in (("pt", ("pt",), 95), ("en", ("en", "ig"), 100)):
    content_bytes = (render / f"content.{lang}.json").read_bytes()
    narration_bytes = (render / f"narracao.{lang}.json").read_bytes()
    content = json.loads(content_bytes)
    narration = json.loads(narration_bytes)
    contents.append(content)
    assert len(content["scenes"]) == len(narration["lines"]) == 7
    assert [scene["id"] for scene in content["scenes"]] == [line["scene"] for line in narration["lines"]]
    words = [len(line["text"].split()) for line in narration["lines"]]
    assert sum(words) <= limit
    assert narration["lines"][0]["delivery"] == "hook"
    assert all(line["delivery"] == "neutral" for line in narration["lines"][1:])
    duration = sum(scene["durationSec"] for scene in content["scenes"])
    assert 35 <= duration <= 45
    assert content["safeArea"] == "shorts" and not content["assets"] and "host" not in content
    for scene, count in zip(content["scenes"], words, strict=True):
        assert count / 2.2 <= scene["durationSec"], (lang, scene["id"], count / 2.2)
        if scene["type"] != "flow":
            continue
        assert 2 <= len(scene["nodes"]) <= 4
        events = [state["atSec"] for state in scene["states"]]
        events += [token["atSec"] for token in scene["tokens"]]
        ends = [token["atSec"] + token["durationSec"] for token in scene["tokens"]]
        assert min(events) >= 1.3
        assert max(events + ends) + 1 <= scene["durationSec"]
    for suffix in suffixes:
        episode = root / "data" / "episodes" / f"short-circuit-breaker-java-{suffix}"
        assert (episode / "content.json").read_bytes() == content_bytes
        assert (episode / "narracao.json").read_bytes() == narration_bytes
        evidence = json.loads((episode / "medicao.json").read_text())
        declared = {entry["valor"] for entry in evidence["numeros"]}
        assert set(visible_numbers(content, narration["language"])) <= declared
        assert {1, 2, 5, 7, 15, 24, 25, 60, 133} <= declared
        if suffix != "pt":
            link = json.loads((episode / "traducao.json").read_text())
            assert link["derived_from"] == "short-circuit-breaker-java-pt"
    print(
        f"{lang}: {sum(words)} words; per scene {words}; "
        f"estimated speech {sum(words) / 2.2:.1f}s; planned {duration:.1f}s"
    )

assert nontext(contents[0]) == nontext(contents[1]), "Non-text fields differ across locales"
for name, expected in (
    ("Demo.java", "79cc94380cc8fadb21d7d6d5876cb8a18aa7151e37b8bcfacf5526f90c2a3274"),
    ("BreakerTest.java", "2781150adc63c873288f625062dd9c376a96015f2623b651db9825f03748d5f5"),
    ("medir.sh", "6d95b9b258c51d6a96b5a3262367d496c04d0a00f8b559df9756c55204fa4032"),
):
    assert hashlib.sha256((render / "demo" / name).read_bytes()).hexdigest() == expected
print(
    "PASS: exact episode copies, all non-text fields equal, visible numbers covered, flow timing, demo hashes"
)
