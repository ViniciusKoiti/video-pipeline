"""Partes puras do `scripts/provisorio/shorts_tec.py` (skill `shorts-tec`): nada de rede, voz nem ffmpeg."""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from app.pipeline.motion_inputs import MotionInputError

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def shorts_tec():
    script = ROOT / "scripts" / "provisorio" / "shorts_tec.py"
    spec = importlib.util.spec_from_file_location("shorts_tec", script)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    # O dataclass com `from __future__ import annotations` resolve os tipos pelo módulo em `sys.modules`.
    sys.modules["shorts_tec"] = module
    spec.loader.exec_module(module)
    return module


def test_filtro_do_ffmpeg_atrasa_cada_fala_ate_a_cena_e_fecha_no_alvo(shorts_tec) -> None:
    text = shorts_tec.mix_filter([0, 2000], 8.2)
    assert "[1:a]aformat=sample_rates=48000:channel_layouts=mono,adelay=0|0[v0]" in text
    assert "[2:a]aformat=sample_rates=48000:channel_layouts=mono,adelay=2000|2000[v1]" in text
    assert "[v0][v1]amix=inputs=2:normalize=0" in text
    assert "apad=whole_dur=8.200" in text and "loudnorm=I=-14" in text
    assert text.endswith(",aresample=48000[voz]")


def test_fala_fica_entre_os_silencios_das_pontas(shorts_tec) -> None:
    log = (
        "silence_start: 0\nsilence_end: 1.028667\nsilence_start: 2.7285\nsilence_end: 2.954792\n"
        "silence_start: 3.5685\nsilence_end: 3.92\n"
    )
    begin, end = shorts_tec.bounds_from_log(log, 3.92)
    assert (begin, end) == (pytest.approx(0.9487, abs=1e-3), pytest.approx(3.6485, abs=1e-3))
    # Sem silêncio nas pontas: o arquivo inteiro. Silêncio aberto até o fim: o fim antecipa.
    assert shorts_tec.bounds_from_log("silence_start: 1.1\nsilence_end: 1.4\n", 3.2) == (0.0, 3.2)
    assert shorts_tec.bounds_from_log("silence_start: 2.65\n", 3.2) == (0.0, pytest.approx(2.73))


def test_filtro_mistura_o_audio_do_render_quando_ele_existe(shorts_tec) -> None:
    text = shorts_tec.mix_filter([0, 2000], 8.2, video_audio=True)
    assert "[0:a]aformat=sample_rates=48000:channel_layouts=mono[v0a]" in text
    assert "[v0a][v0][v1]amix=inputs=3:normalize=0" in text
    assert "amix=inputs=2" in shorts_tec.mix_filter([0, 2000], 8.2)


def test_filtro_corta_a_fala_no_trecho_falado(shorts_tec) -> None:
    text = shorts_tec.mix_filter([0, 2000], 8.2, trims=[(0.3, 2.7), (0.0, 1.2)])
    assert "[1:a]atrim=0.300:2.700,asetpts=PTS-STARTPTS,aformat=" in text
    assert "[2:a]atrim=0.000:1.200,asetpts=PTS-STARTPTS,aformat=" in text


def test_nome_do_wav_muda_com_texto_entrega_e_voz_e_fala_fora_do_json_ganha_indice(shorts_tec) -> None:
    line = shorts_tec.Line("gancho", "Descrevi seis cenas.", "hook")
    a = shorts_tec.wav_name(line, 0, "chatterbox_modal", "voz-a")
    assert a.startswith("gancho-chatterbox_modal-ptbr-") and a.endswith(".wav")
    # O idioma entra no nome: a fala em inglês da mesma cena não apaga a em português.
    assert shorts_tec.wav_name(line, 0, "chatterbox_modal", "voz-a", "en").startswith(
        "gancho-chatterbox_modal-en-"
    )
    assert a != shorts_tec.wav_name(line, 0, "chatterbox_modal", "voz-b")
    neutral = shorts_tec.Line("gancho", "Descrevi seis cenas.", "neutral")
    assert a != shorts_tec.wav_name(neutral, 0, "chatterbox_modal", "voz-a")
    # O Kokoro ignora a entrega: o nome não muda com ela.
    assert shorts_tec.wav_name(line, 0, "kokoro", "k") == shorts_tec.wav_name(neutral, 0, "kokoro", "k")
    fora = shorts_tec.Line(None, "Fora do JSON.")
    assert shorts_tec.wav_name(fora, 3, "kokoro", "k").startswith("fora-3-kokoro-ptbr-")


def test_nome_do_wav_segue_o_texto_falado_do_glossario_e_nao_muda_sem_termo(shorts_tec) -> None:
    line = shorts_tec.Line("gancho", "Um objeto JSON.")
    plain = shorts_tec.wav_name(line, 0, "chatterbox_modal", "v")
    assert shorts_tec.wav_name(line, 0, "chatterbox_modal", "v", spoken=line.text) == plain
    assert shorts_tec.wav_name(line, 0, "chatterbox_modal", "v", spoken="Um objeto jêison.") != plain


def test_narracao_lida_do_json_com_entrega_neutra_por_padrao(shorts_tec, tmp_path: Path) -> None:
    path = tmp_path / "narracao.pt.json"
    lines = [{"scene": "gancho", "text": " Oi. "}, {"scene": None, "text": "Fora."}]
    path.write_text(json.dumps({"language": "pt-BR", "lines": lines}))
    language, lines = shorts_tec.load_lines(path)
    assert language == "pt-BR"
    assert lines == [shorts_tec.Line("gancho", "Oi.", "neutral"), shorts_tec.Line(None, "Fora.", "neutral")]
    path.write_text(json.dumps({"language": "pt-BR", "lines": []}))
    with pytest.raises(MotionInputError, match="lines"):  # sem linhas, e sem `language`, o erro é do projeto
        shorts_tec.load_lines(path)
    path.write_text(json.dumps({"lines": [{"text": "Oi."}]}))
    with pytest.raises(MotionInputError, match="language"):
        shorts_tec.load_lines(path)
