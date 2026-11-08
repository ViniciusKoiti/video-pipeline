"""Benchmark local: pares cegos, volume combinado e episodio intocado."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

from app.media.voice_level import VoiceLevelError, level_voice
from scripts.bench.polimento_voz_ab import main, page, prepare_pair, sha256
from tests.test_voice_level import tone


def fixture(tmp_path: Path) -> tuple[Path, Path, dict]:
    episode = tmp_path / 'ep'
    raw = episode / 'voice' / 'S01.wav'
    tone(raw, 0.05)
    leveled = level_voice(raw)
    scene = {'id': 'S01', 'start_ms': 0, 'duration_ms': 3000,
             'audio': leveled.relative_to(episode).as_posix()}
    baseline = episode / 'baseline.json'
    baseline.write_text(json.dumps({'scenes': [scene]}))
    return episode, baseline, scene


def test_main_makes_blind_pairs_and_never_writes_in_the_episode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    episode, baseline, _ = fixture(tmp_path)
    before = {p: sha256(p) for p in episode.rglob('*') if p.is_file()}
    out = tmp_path / 'ab'
    monkeypatch.setattr('scripts.bench.polimento_voz_ab.cpu_probe', lambda: 0.01)
    monkeypatch.setattr(sys, 'argv', ['ab', '--episodio', str(episode), '--baseline', str(baseline),
                                    '--trecho', '0.5:2.5', '--saida', str(out)])
    main()
    assert {p: sha256(p) for p in episode.rglob('*') if p.is_file()} == before
    key = json.loads((out / 'privado' / 'gabarito.json').read_text())
    [pair] = key['pairs']
    variants = pair['variants']
    assert {v['name'] for v in variants} == {'atual', 'polida'}
    assert {v['label'] for v in variants} == {'A', 'B'}
    assert all(v['duration_ms'] == 2000 for v in variants)
    assert abs(variants[0]['measured']['input_i'] - variants[1]['measured']['input_i']) <= 0.1
    assert all(v['measured']['input_tp'] <= -1.5 for v in variants)
    assert (out / 'par-01-A-pausa-B.wav').is_file()
    content = (out / 'index.html').read_text()
    assert 'atual' not in content and 'polida' not in content
    assert not list((out / 'privado').glob('tmp*'))
    with pytest.raises(SystemExit):
        main()  # nunca sobrescreve o teste


def test_raw_hash_mismatch_stops_before_generating(tmp_path: Path) -> None:
    episode, _, scene = fixture(tmp_path)
    tone(episode / 'voice' / 'S01.wav', 0.1)
    work = tmp_path / 'work'
    work.mkdir()
    with pytest.raises(VoiceLevelError, match='bruto'):
        prepare_pair(episode, scene, 0.5, 2.5, work)
    assert not list(work.iterdir())


def test_html_keeps_sources_neutral_and_has_mobile_viewport() -> None:
    content = page([(8, 12.5), (40.5, 45)])
    assert content.count('<audio ') == 4
    assert 'viewport' in content and 'par-02-B.wav' in content
