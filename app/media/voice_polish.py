"""Cadeia opcional antes do loudnorm; sem cauda nem mudanca de duracao."""

from app.media.models.voice_polish import VoicePolish


def polish_filters(polish: VoicePolish | None) -> str:
    if polish is None:
        return ""
    filters = [f"highpass=f={polish.highpass_hz}"]
    if polish.eq_gain_db:
        filters.append(
            f"equalizer=f={polish.eq_hz}:t=o:w={polish.eq_width_octaves}:g={polish.eq_gain_db}"
        )
    filters.append(
        f"deesser=i={polish.deesser_intensity}:m={polish.deesser_max}:f={polish.deesser_frequency}"
    )
    return ",".join(filters) + ","
