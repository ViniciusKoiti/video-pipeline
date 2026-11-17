from typing import Any

class Pipeline:
    # O pipeline de reconhecimento de fala: (caminho do WAV, **opções) -> {"text": ..., "chunks": [...]}.
    def __call__(self, inputs: str, **kwargs: Any) -> dict[str, Any]: ...

def pipeline(task: str | None = None, model: str | None = None, *, device: str | None = None) -> Pipeline: ...
