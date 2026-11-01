"""Registro de fontes de um episódio (RF5, §13.1, ADR 009): baixada, salva à mão ou declarada pelo dono.

As três entradas viram o mesmo `ExtractedSource` e passam por um registro só:

- **Id sob lock:** o `source-NN` é o próximo livre, calculado e usado com o episódio travado; duas execuções
  não repetem id.
- **Repetição não duplica:** a mesma URL, ou o mesmo texto declarado, devolve a fonte que já existe e não
  escreve nada. Metadado novo (título, autores) não substitui o registrado.
- **Aprovada não é substituída:** com o gate 1 aprovado, `sources.json` está carimbado (ADR 039); o registro
  recusa antes de escrever qualquer arquivo, e reabrir (`vp reopen --step sources`) libera.
- **Recuperação definida:** original, texto e trechos são gravados (um `replace` por arquivo) e o
  `sources.json` por último. Falha antes disso deixa arquivos de um id que o manifesto não tem; a próxima
  tentativa reaproveita o mesmo id e os sobrescreve. A fonte só existe depois do manifesto.
"""

from __future__ import annotations

import tempfile
from collections.abc import Callable
from pathlib import Path

from app.errors import PipelineError
from app.pipeline.atomic_files import write_atomic
from app.pipeline.constants.sources_constants import SourcesConstants as Constants
from app.pipeline.excerpts import numbered_view
from app.pipeline.extract import as_source_text, decode_html, html_paragraphs, pdf_paragraphs
from app.pipeline.models.extracted_source import ExtractedSource
from app.pipeline.models.source_draft import SourceDraft
from app.pipeline.models.source_registration import SourceRegistration
from app.pipeline.ports import ManifestStore, WriteGuard
from app.pipeline.schemas import Source, SourceKind, SourcesManifest
from app.pipeline.state import Clock

PdfText = Callable[[Path], str]  # o texto que o `pdftotext` tira do PDF
Downloader = Callable[[str, Path], Path]  # (url, destino) -> arquivo baixado; sem rede nos testes


class SourceError(PipelineError, ValueError):
    """Fonte que não pode ser registrada (sem texto, arquivo ausente); nada foi escrito."""


def from_bytes(raw: bytes, pdf_text: PdfText) -> ExtractedSource:
    if raw[: len(Constants.PDF_MAGIC)] == Constants.PDF_MAGIC:
        with tempfile.TemporaryDirectory() as folder:
            pdf = Path(folder) / "fonte.pdf"
            pdf.write_bytes(raw)
            paragraphs, suffix = pdf_paragraphs(pdf_text(pdf)), "pdf"
    else:
        paragraphs, suffix = html_paragraphs(decode_html(raw)), "html"
    return _extracted(raw, suffix, paragraphs, "o original")


def fetch_url(url: str, download: Downloader, pdf_text: PdfText) -> ExtractedSource:
    """Baixa para uma pasta temporária (nada entra no episódio) e extrai o texto."""
    with tempfile.TemporaryDirectory() as folder:
        return from_bytes(download(url, Path(folder) / "fonte.download").read_bytes(), pdf_text)


def from_file(path: Path, pdf_text: PdfText) -> ExtractedSource:
    """Arquivo salvo à mão no navegador (servidor que recusa o robô)."""
    if not path.is_file():
        raise SourceError(f"{path} não existe")
    return from_bytes(path.read_bytes(), pdf_text)


def declared(path: Path) -> ExtractedSource:
    """Material do dono: cada linha não vazia é um trecho (receita e nota são listas)."""
    if not path.is_file():
        raise SourceError(f"{path} não existe")
    raw = path.read_bytes()
    lines = [" ".join(line.split()) for line in raw.decode("utf-8").splitlines() if line.strip()]
    return _extracted(raw, path.suffix.lstrip(".") or "txt", lines, path.name)


def _extracted(raw: bytes, suffix: str, paragraphs: list[str], origin: str) -> ExtractedSource:
    if not paragraphs:
        raise SourceError(f"nenhum texto extraído de {origin}; fonte não registrada")
    return ExtractedSource(raw, suffix, tuple(paragraphs))


class SourceRegistry:
    def __init__(self, store: ManifestStore, guard: WriteGuard, now: Clock) -> None:
        self._store, self._guard, self._now = store, guard, now

    def register(self, episode_id: str, draft: SourceDraft, extracted: ExtractedSource) -> SourceRegistration:
        text = as_source_text(list(extracted.paragraphs))
        with self._store.lock(episode_id):
            manifest = self._store.read(episode_id, "sources.json", SourcesManifest)
            known = self._known(episode_id, manifest, draft, text)
            if known is not None:
                return SourceRegistration(known, created=False)
            source = self._new(manifest, draft)
            updated = manifest.model_copy(update={"sources": [*manifest.sources, source]})
            self._guard.check(episode_id, "sources.json", (updated.model_dump_json(indent=2) + "\n").encode())
            self._publish(episode_id, source, extracted, text)
            self._store.write(episode_id, "sources.json", updated)  # por último: a fonte só existe agora
            return SourceRegistration(source, created=True)

    def _new(self, manifest: SourcesManifest, draft: SourceDraft) -> Source:
        numbers = [int(m[1]) for s in manifest.sources if (m := Constants.ID.match(s.id))]
        source_id = f"source-{max(numbers, default=0) + 1:02d}"
        return Source(
            id=source_id,
            title=draft.title,
            url=draft.url,
            kind=draft.kind,
            retrieved_at=self._now(),
            local_path=f"sources/{source_id}.txt",
            notes=draft.notes,
            interested=draft.interested,
            authors=list(draft.authors),
        )

    def _known(
        self, episode_id: str, manifest: SourcesManifest, draft: SourceDraft, text: str
    ) -> Source | None:
        """A fonte que já é esta: a mesma URL, ou, entre as declaradas, o mesmo texto."""
        for source in manifest.sources:
            if draft.url is not None and source.url == draft.url:
                return source
            both_declared = draft.kind is SourceKind.DECLARED and source.kind is SourceKind.DECLARED
            if both_declared and self._text_of(episode_id, source) == text:
                return source
        return None

    def _text_of(self, episode_id: str, source: Source) -> str | None:
        path = self._store.path(episode_id, source.local_path)
        return path.read_text(encoding="utf-8") if path.is_file() else None

    def _publish(self, episode_id: str, source: Source, extracted: ExtractedSource, text: str) -> None:
        raw_dir = self._store.path(episode_id, "sources/raw")
        for orphan in raw_dir.glob(f"{source.id}.*"):  # sobra de uma tentativa que não chegou ao manifesto
            orphan.unlink()
        write_atomic(raw_dir / f"{source.id}.{extracted.suffix}", extracted.raw)
        write_atomic(self._store.path(episode_id, source.local_path), text.encode("utf-8"))
        view = numbered_view(source, text)
        write_atomic(self._store.path(episode_id, f"excerpts/{source.id}.md"), view.encode("utf-8"))
