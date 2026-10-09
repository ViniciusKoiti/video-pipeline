"""Busca de candidatos em bancos de imagem por necessidade visual (provisório até `vp assets`, #20–#23).

Uso: `.venv/bin/python scripts/provisorio/buscar_candidatos.py <episode-id> <pedidos.json> [--limit N]`

`pedidos.json`: `{"pedidos": [{"id": "cimento", "plano": "S01 · ...", "consultas": ["..."],
"midias": ["video", "photo"], "min_duration_s": 4, "orientacao": "portrait"}]}`.

- Usa os bancos da cascata de config/providers.toml que têm adapter e chave no .env; os outros são pulados
  com aviso (o Coverr é só manual).
- Orientação do arquivo: `orientacao` do pedido (`landscape` ou `portrait`); sem ela, a do `scenes.json`
  do episódio (ADR 014), e sem o arquivo, `landscape`. Em retrato só entram arquivos em pé de pelo menos
  1080×1920.
- Cada consulta vai a cada banco em cada mídia pedida; `--limit` candidatos por chamada (padrão 5), para a
  triagem humana escolher até 2 por plano. Tudo é ilustração: `visual_need` sempre `contextual_stock`.
- Saída: `data/episodes/<id>/candidatos/<pedido>.json` com o ativo (licença, autor, página, crédito), a
  miniatura no cache, largura, altura, duração, banco, consulta e mídia. Falha de um banco (cota, chave)
  fica registrada no arquivo e não interrompe os outros (§2.1). Nada é baixado em resolução final aqui.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from app.bootstrap import DEFAULT_REGISTRY, ConfigurationError  # noqa: E402
from app.pipeline.schemas import Orientation, VisualNeed  # noqa: E402
from app.providers.archives.base import ArchiveProvider, AssetCandidate, AssetQuery  # noqa: E402
from app.providers.errors import ProviderError  # noqa: E402
from app.settings import load_settings  # noqa: E402


def available_archives(settings) -> list[ArchiveProvider]:  # noqa: ANN001
    archives = []
    for name in settings.providers.archives:
        registration = DEFAULT_REGISTRY["archives"].get(name)
        if registration is None or registration.factory is None:
            continue  # acervo ainda sem adapter (Commons, LoC, Flickr Commons)
        try:
            archives.append(registration.factory(settings))
        except ConfigurationError as error:
            print(f"pulado: {name} ({error})")
    return archives


def episode_orientation(episode_dir: Path) -> Orientation:
    """`orientation` do scenes.json do episódio (ADR 014); sem o arquivo, 16:9."""
    scenes = episode_dir / "scenes.json"
    if scenes.is_file() and json.loads(scenes.read_text()).get("orientation") == "portrait":
        return "portrait"
    return "landscape"


def _relative(path: Path) -> str:
    """Caminho a partir da raiz do repositório; com `DATA_DIR` fora dela (worktree), o caminho inteiro."""
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def _record(candidate: AssetCandidate, bank: str, text: str, media: str) -> dict:
    thumb = candidate.thumbnail_path
    return {
        "banco": bank,
        "consulta": text,
        "midia": media,
        "largura": candidate.width,
        "altura": candidate.height,
        "duracao_s": candidate.duration_s,
        "miniatura": _relative(thumb) if thumb else None,
        "ativo": candidate.asset.model_dump(mode="json"),
    }


def main() -> None:
    formatter = argparse.RawDescriptionHelpFormatter
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=formatter)
    parser.add_argument("episode_id")
    parser.add_argument("pedidos", type=Path)
    parser.add_argument("--limit", type=int, default=5, help="candidatos por chamada (padrão 5)")
    args = parser.parse_args()
    settings = load_settings(ROOT)
    out_dir = settings.data_dir / "episodes" / args.episode_id / "candidatos"
    out_dir.mkdir(parents=True, exist_ok=True)
    archives = available_archives(settings)
    print("bancos:", ", ".join(a.info.name for a in archives) or "nenhum")
    default_orientation = episode_orientation(out_dir.parent)

    for pedido in json.loads(args.pedidos.read_text())["pedidos"]:
        found: dict[str, dict] = {}
        failures = []
        orientation = pedido.get("orientacao", default_orientation)
        if orientation not in ("landscape", "portrait"):
            raise SystemExit(f"{pedido['id']}: orientacao é landscape ou portrait, não {orientation!r}")
        for text in pedido["consultas"]:
            for media in pedido.get("midias", ["video"]):
                query = AssetQuery(
                    text=text,
                    visual_need=VisualNeed.CONTEXTUAL_STOCK,
                    limit=args.limit,
                    media=media,
                    min_duration_s=pedido.get("min_duration_s") if media == "video" else None,
                    orientation=orientation,
                )
                for archive in archives:
                    try:
                        candidates = archive.search_assets(query)
                    except ProviderError as error:
                        failures.append({"banco": archive.info.name, "consulta": text, "motivo": str(error)})
                        continue
                    for c in candidates:
                        found.setdefault(c.asset.id, _record(c, archive.info.name, text, media))
        result = {"pedido": pedido, "candidatos": list(found.values()), "falhas": failures}
        (out_dir / f"{pedido['id']}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
        by_bank = {}
        for c in found.values():
            by_bank[c["banco"]] = by_bank.get(c["banco"], 0) + 1
        print(f"{pedido['id']} ({orientation}): {len(found)} candidatos {by_bank}; falhas: {len(failures)}")


if __name__ == "__main__":
    main()
