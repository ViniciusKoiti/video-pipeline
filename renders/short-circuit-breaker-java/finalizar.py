"""Audit existing leveled speech and prepare derived, frame-aligned Short inputs."""

import argparse
import copy
import hashlib
import json
import math
import re
import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def save(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def snapshot(path):
    digest = hashlib.sha256(path.read_bytes()).hexdigest()[:12]
    backup = HERE / "originais" / f"{path.parent.name}-{path.stem}-{digest}{path.suffix}"
    if not backup.exists():
        backup.parent.mkdir(parents=True, exist_ok=True)
        backup.write_bytes(path.read_bytes())
    return str(backup.relative_to(ROOT))


def intervals_from_log(log, seconds):
    intervals = []
    start = None
    for match in re.finditer(r"silence_(start|end):\s*([0-9.]+)", log):
        if match[1] == "start":
            start = float(match[2])
        elif start is not None:
            intervals.append([start, float(match[2])])
            start = None
    if start is not None:
        intervals.append([start, seconds])
    return intervals


def audit(languages):
    report = {"filter": "silencedetect=noise=-50dB:d=0.5", "boundary_margin_s": 0.05, "languages": {}}
    problems = []
    for language in languages:
        episode = ROOT / "data/episodes" / f"short-circuit-breaker-java-{language}"
        record = load(episode / "narracao.voz.json")
        narration = load(episode / "narracao.json")
        assert [line["text"] for line in record["lines"]] == [line["text"] for line in narration["lines"]]
        rows = []
        for line in record["lines"]:
            wav = episode / line["wav"]
            assert "voice/leveled/" in line["wav"] and line.get("level")
            assert hashlib.sha256(wav.read_bytes()).hexdigest() == line["level"]["wav_sha256"]
            command = [
                "ffmpeg",
                "-hide_banner",
                "-nostats",
                "-i",
                str(wav),
                "-af",
                report["filter"],
                "-f",
                "null",
                "-",
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=True)
            intervals = intervals_from_log(result.stderr, line["seconds"])
            begin, end = line["speech"]
            internal = [span for span in intervals if span[0] > begin + 0.05 and span[1] < end - 0.05]
            row = {
                "scene": line["scene"],
                "wav": str(wav.relative_to(ROOT)),
                "seconds": line["seconds"],
                "speech": line["speech"],
                "silences": intervals,
                "internal": internal,
                "level": line["level"],
            }
            rows.append(row)
            if internal:
                problems.append(f"{language}/{line['scene']}: {internal}")
        report["languages"][language] = rows
    report["problems"] = problems
    save(HERE / "auditoria-pausas.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 1 if problems else 0


def prepare(languages):
    previous_audit = load(HERE / "auditoria-pausas.json")
    assert not previous_audit["problems"], "Fix internal pauses before preparing timings"
    report = {"originals_preserved": [], "languages": {}, "shared_timeline": False}
    for language in languages:
        episode = ROOT / "data/episodes" / f"short-circuit-breaker-java-{language}"
        narration = load(episode / "narracao.json")
        record_path = episode / "narracao.voz.json"
        record = load(record_path)
        assert [line["text"] for line in record["lines"]] == [line["text"] for line in narration["lines"]]
        source = HERE / f"content.{language}.json"
        report["originals_preserved"].extend([snapshot(source), snapshot(record_path)])
        content = copy.deepcopy(load(source))
        rows = []
        for scene, line, audited in zip(
            content["scenes"], record["lines"], previous_audit["languages"][language], strict=True
        ):
            assert scene["id"] == line["scene"] == audited["scene"]
            assert line["level"]["wav_sha256"] == audited["level"]["wav_sha256"]
            padding = 0.8 if language == "pt" else 0.35
            if language == "pt" and scene["id"] in {"aberto", "medido"}:
                padding = 0.7
            spoken = line["speech"][1] - line["speech"][0]
            duration = math.ceil((spoken + padding) * 10 - 1e-9) / 10
            original_duration = scene["durationSec"]
            scene["durationSec"] = duration
            if scene["type"] == "flow":
                event_end = max(
                    [event["atSec"] for event in scene["states"]]
                    + [token["atSec"] + token["durationSec"] for token in scene["tokens"]]
                )
                # Leave stabilization (11 frames) plus a full second of reading.
                last = min(spoken - 0.45, duration - 1.4)
                assert last > 1.3
                scale = (last - 1.3) / (event_end - 1.3)
                for state in scene["states"]:
                    state["atSec"] = round(1.3 + (state["atSec"] - 1.3) * scale, 3)
                for token in scene["tokens"]:
                    token["atSec"] = round(1.3 + (token["atSec"] - 1.3) * scale, 3)
                    token["durationSec"] = round(token["durationSec"] * scale, 3)
            rows.append(
                {
                    "scene": scene["id"],
                    "speech_s": round(spoken, 3),
                    "original_s": original_duration,
                    "duration_s": duration,
                    "reading_tail_s": round(duration - spoken, 3),
                }
            )
        total = round(sum(row["duration_s"] for row in rows), 3)
        assert 35 <= total <= 45
        assert max(row["reading_tail_s"] for row in rows) < 1
        destination = HERE / "pronto" / f"content.{language}.json"
        save(destination, content)
        report["languages"][language] = {
            "voice_record": str(record_path.relative_to(ROOT)),
            "input": str(destination.relative_to(ROOT)),
            "total_s": total,
            "speech_s": round(sum(row["speech_s"] for row in rows), 3),
            "scenes": rows,
        }
    report["note"] = (
        "Derived per-language timings only; original common authoring inputs remain unchanged. "
        "vp traducao checks authoring content.json, not these timed derivatives. No approval granted. "
        "Join trims each WAV to speech bounds. "
        "PT reading tails keep the planned duration at least 35 seconds."
    )
    save(HERE / "finalizacao-tempos.json", report)
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


def check(languages):
    kit = ROOT.parent / "motion-kit/packages/motion-video/dist/video.mjs"
    reports = {}
    for language in languages:
        content = HERE / "pronto" / f"content.{language}.voz.json"
        reports[language] = {}
        for action in ("validate", "inspect"):
            command = ["node", str(kit), action, content.name]
            result = subprocess.run(command, cwd=content.parent, capture_output=True, text=True)
            data = json.loads(result.stdout)
            save(HERE / f"finalizacao-{action}.{language}.json", data)
            assert result.returncode == 0 and data.get("success"), data
            assert not data.get("diagnostics"), data.get("diagnostics")
            reports[language][action] = {"success": True, "diagnostics": []}
        voiced = load(content)
        episode = ROOT / "data/episodes" / f"short-circuit-breaker-java-{language}"
        narration = load(episode / "narracao.json")
        record = load(episode / "narracao.voz.json")
        assert [line["text"] for line in record["lines"]] == [line["text"] for line in narration["lines"]]
        audio_command = ["ffmpeg", "-hide_banner", "-nostats"]
        filters = []
        for scene, line in zip(voiced["scenes"], record["lines"], strict=True):
            spoken = line["speech"][1] - line["speech"][0]
            assert 0.35 <= scene["durationSec"] - spoken < 1
            if scene["type"] == "flow":
                assert min(event["atSec"] for event in scene["states"] + scene["tokens"]) >= 1.3
                assert (
                    max(
                        [event["atSec"] for event in scene["states"]]
                        + [event["atSec"] + event["durationSec"] for event in scene["tokens"]]
                    )
                    + 1
                    <= scene["durationSec"]
                )
            index = len(filters)
            audio_command.extend(["-i", str(episode / line["wav"])])
            filters.append(
                f"[{index}:a]atrim=start={line['speech'][0]}:end={line['speech'][1]},asetpts=PTS-STARTPTS,apad=whole_dur={scene['durationSec']},atrim=duration={scene['durationSec']}[s{index}]"
            )
        labels = "".join(f"[s{index}]" for index in range(len(filters)))
        filters.append(f"{labels}concat=n={len(filters)}:v=0:a=1,silencedetect=noise=-50dB:d=0.5[a]")
        audio_command.extend(["-filter_complex", ";".join(filters), "-map", "[a]", "-f", "null", "-"])
        audio_result = subprocess.run(audio_command, capture_output=True, text=True, check=True)
        total = sum(scene["durationSec"] for scene in voiced["scenes"])
        silences = intervals_from_log(audio_result.stderr, total)
        max_silence = max((end - start for start, end in silences), default=0)
        audio_report = {
            "filter": "silencedetect=noise=-50dB:d=0.5",
            "method": (
                "In-memory audio-only concat of leveled WAV speech trims, "
                "padded to frame-aligned scene durations. "
                "No audio/video file rendered or original WAV modified."
            ),
            "silences": silences,
            "max_silence_s": round(max_silence, 6),
            "problems": [span for span in silences if span[1] - span[0] > 1],
        }
        save(HERE / f"finalizacao-audio.{language}.json", audio_report)
        assert not audio_report["problems"], audio_report
        save(episode / "content.voz.json", voiced)
        reports[language]["duration_s"] = round(sum(scene["durationSec"] for scene in voiced["scenes"]), 3)
        reports[language]["voice_record"] = str((episode / "narracao.voz.json").relative_to(ROOT))
        reports[language]["max_actual_silence_s"] = audio_report["max_silence_s"]
    if {"pt", "en"} <= set(languages):

        def semantic(value):
            if isinstance(value, dict):
                return {
                    key: semantic(item)
                    for key, item in value.items()
                    if key
                    not in {
                        "durationSec",
                        "atSec",
                        "locale",
                        "footer",
                        "kicker",
                        "text",
                        "highlight",
                        "title",
                        "label",
                        "sublabel",
                    }
                }
            if isinstance(value, list):
                return [semantic(item) for item in value]
            return value

        assert semantic(load(HERE / "pronto/content.pt.voz.json")) == semantic(
            load(HERE / "pronto/content.en.voz.json")
        )
        reports["cross_language"] = (
            "Only localized text and time fields differ; "
            "scene/node/edge/token identities, states, routes and numbers retained."
        )
    save(HERE / "finalizacao-checks.json", reports)
    print(json.dumps(reports, ensure_ascii=False, indent=2))
    return 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("action", choices=["audit", "prepare", "check"])
    parser.add_argument("languages", nargs="*", default=["pt", "en"])
    args = parser.parse_args()
    return {"audit": audit, "prepare": prepare, "check": check}[args.action](args.languages)


if __name__ == "__main__":
    raise SystemExit(main())
