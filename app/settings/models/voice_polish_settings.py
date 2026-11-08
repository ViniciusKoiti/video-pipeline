from app.media.models.voice_polish import VoicePolish


class VoicePolishSettings(VoicePolish):
    enabled: bool = False

    def active(self) -> VoicePolish | None:
        return VoicePolish.model_validate(self.model_dump(exclude={"enabled"})) if self.enabled else None
