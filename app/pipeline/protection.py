"""Proteção de escrita (§2.6) derivada do `review.json`, a única autoridade das aprovações (§5).

O que cada gate carimba fica protegido enquanto a última decisão dele é "aprovado" e ainda vale (o hash
revisto bate com o conteúdo de agora). Mudou o conteúdo por fora, a aprovação já caiu e nada se protege;
reaberto com `vp reopen` (`app.pipeline.reopen`), o alvo é liberado e só ele. Não existe projeção no
`manifest.json`: a regra é recalculada a cada consulta.

Uma escrita que deixa intacto o hash normalizado do gate passa: trocar o `asset_id` de um plano (gate 3) ou
regenerar o bloco de números do `outline.md` não mexe no que o gate 2 aprovou.
"""

from __future__ import annotations

from pathlib import Path

from app.pipeline.constants.gates_constants import GatesConstants as Constants
from app.pipeline.gates import current_hash, legacy_hash
from app.pipeline.ports import ImmutableManifest, ManifestStore, ReviewGate
from app.pipeline.review_hashes import hash_contents
from app.pipeline.schemas import Decision, ReviewEntry, Step


class ReviewWriteGuard:
    def __init__(self, store: ManifestStore, review: ReviewGate) -> None:
        self._store = store
        self._review = review

    def check(self, episode_id: str, name: str, candidate: bytes | None = None) -> None:
        owner = self._owner(name)
        if owner is None or (owner[0] is Step.PREVIEW and name not in self._stamped_preview(episode_id)):
            return
        step, asset_id = owner
        entry = self._review.log(episode_id).latest(step, asset_id=asset_id)
        if entry is None or entry.decision is not Decision.APPROVED:
            return
        current = current_hash(self._store, episode_id, step, asset_id)
        if entry.input_hash not in (current, legacy_hash(self._store, episode_id, step)):
            return  # o conteúdo mudou depois da decisão: ela já não vale
        if candidate is not None and self._unchanged(episode_id, name, step, entry, current, candidate):
            return
        target = asset_id or step.value
        raise ImmutableManifest(
            f"{episode_id}/{name} está carimbado pelo gate de {target}; reabra com `vp reopen` (§2.6)"
        )

    @staticmethod
    def _owner(name: str) -> tuple[Step, str | None] | None:
        for step, names in Constants.GATE_FILES.items():
            if name in names:
                return step, None
        if name.startswith("assets/"):
            path = Path(name)
            if path.suffix == ".json" or path.suffix in Constants.MEDIA_SUFFIXES:
                return Step.ASSETS, path.stem
        if name in (*Constants.RENDERS, *Constants.PREVIEW_FILES):
            return Step.PREVIEW, None
        return None

    def _stamped_preview(self, episode_id: str) -> set[str]:
        """O que o gate 4 carimba hoje: o render mais acabado e os textos que já existem (`gate_hash`)."""

        def there(name: str) -> bool:
            return self._store.path(episode_id, name).is_file()

        render = next((r for r in Constants.RENDERS if there(r)), None)
        return {*([render] if render else []), *(n for n in Constants.PREVIEW_FILES if there(n))}

    def _unchanged(
        self, episode_id: str, name: str, step: Step, entry: ReviewEntry, current: str | None,
        candidate: bytes,
    ) -> bool:
        """A escrita manteria o hash normalizado que o humano aprovou? (só gates de arquivos de texto)"""
        names = Constants.GATE_FILES.get(step)
        if names is None or entry.input_hash != current:
            return False
        base = self._store.path(episode_id, "")
        contents = {base / n: (base / n).read_bytes() for n in names}
        contents[base / name] = candidate
        return hash_contents(contents, base=base) == entry.input_hash
