from typing import Any

class _Generate:
    def remote(self, job: dict[str, Any]) -> dict[str, Any]: ...

class _Instance:
    generate: _Generate

class _Factory:
    def __call__(self, *, model_name: str) -> _Instance: ...

class Cls:
    @classmethod
    def from_name(cls, app_name: str, name: str) -> _Factory: ...
