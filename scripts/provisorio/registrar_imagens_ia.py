"""Registra as imagens geradas por IA do episódio idade-media-ser-rico como ativos do pipeline.

Uso (na raiz do auto-play, com o .venv):
  PYTHONPATH=. .venv/bin/python scripts/provisorio/registrar_imagens_ia.py [--aplicar]

Sem --aplicar só imprime o plano. Com --aplicar:
- copia cada imagem usada por algum plano para assets/ia-<slug>.jpg e cria assets/ia-<slug>.json
  (provider original, license_id Generated, sha256, prompt no usage_notes, needs_review);
- no scenes.json, os planos `broll` do mapa viram `photo` com `asset_id` e `motion`, e planos
  consecutivos da mesma cena que caem na mesma imagem são fundidos (fica o primeiro);
- preenche imagens-ia/registro.csv com uma linha por arquivo de imagem (inclusive folhas e capas).
Reexecutável: com o scenes.json já convertido (algum plano com asset_id) a conversão é pulada; ativo já
registrado com o mesmo sha256 fica como está (a conferência anotada no usage_notes sobrevive); imagem
refeita (sha256 diferente) substitui o .jpg, atualiza o sha256 e volta a conferência para pendente, desde
que o ativo não esteja aprovado. Nada é aprovado aqui: o gate 3 é do dono (vp approve --step assets).
Escrito na sessão de 2026-11-06; vale para este episódio (caminhos fixos abaixo).
"""

from __future__ import annotations

import csv
import hashlib
import json
import re
import shutil
import sys
from collections import Counter
from datetime import datetime
from pathlib import Path

from app.pipeline.models.asset import Asset
from app.pipeline.schemas import ScenesManifest

EP = Path("data/episodes/idade-media-ser-rico")
IA = EP / "imagens-ia"
SRC = IA / "personagem"
ASSETS = EP / "assets"
APLICAR = "--aplicar" in sys.argv
HOJE = datetime.now().astimezone().date().isoformat()
GERADOR = "a confirmar pelo dono (os JPEGs não trazem metadado do gerador)"
MOTIONS = ("push_in", "pan_right", "pull_out", "pan_left")
PROMPT_CENA = re.compile(r"^### (\S+\.png)\s+·\s+cena (S\d+)\s*\n```\n(.*?)\n```", re.M | re.S)
PROMPT_GUIA = re.compile(
    r"\*\*(?:Prompt )?(\w+)[^\n]*?`(?:personagem|capa)/([0-9a-z\-]+\.png)`[^\n]*\n+```\n(.*?)\n```", re.S
)
PENDENTE = (
    "Conferência visual (texto, objeto moderno, logo/brasão, avatar, mãos, espaço de legenda): pendente."
)
CONFERIDA = re.compile(r"Conferência visual por agente em \d{4}-\d{2}-\d{2}.*$", re.S)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def prompts() -> dict[str, tuple[str, str]]:
    """arquivo -> (cena, prompt) a partir de prompts-cenas.md."""
    text = (IA / "prompts-cenas.md").read_text(encoding="utf-8")
    return {m.group(1): (m.group(2), " ".join(m.group(3).split())) for m in PROMPT_CENA.finditer(text)}


def guia_prompts() -> dict[str, tuple[str, str]]:
    """Folhas e capas: arquivo -> (id do prompt no guia, prompt)."""
    text = (IA / "00-guia-e-estilo.md").read_text(encoding="utf-8")
    out = {m.group(2): (m.group(1), " ".join(m.group(3).split())) for m in PROMPT_GUIA.finditer(text)}
    out.setdefault("00c-elenco.png", ("2c", ""))  # a folha do elenco está em outra forma no guia
    return out


def notas(arq: str, cena_prompt: str, prompt: str, desc: str) -> str:
    numero = Path(arq).stem.split("-")[0]
    return (
        f"Ilustração gerada por IA pelo dono do canal em {HOJE} (gerador: {GERADOR}; "
        "registro em imagens-ia/registro.csv), no estilo único do episódio "
        "(imagens-ia/00-guia-e-estilo.md: desenho 2D de contorno grosso, paleta medieval apagada). "
        "Ilustração, nunca registro de época (CLAUDE.md §2.4); a divulgação de conteúdo sintético no "
        "YouTube é decisão do dono no gate 4. Licença Generated com provider original, no critério da "
        "decisão do dono de 2026-10-27 (termos do gerador pendentes em "
        "data/benchmarks/termos-chatgpt-imagem.md). "
        f"Prompt {numero} de imagens-ia/prompts-cenas.md (cena {cena_prompt}), gerado com o bloco de "
        f'estilo e a folha do personagem anexada quando marcado [AVATAR]: "{prompt}". '
        f"Pedido do roteiro: {desc.strip()}. "
        f"Arquivo de origem: imagens-ia/personagem/{arq} (JPEG 1024x572 apesar da extensão). "
        f"{PENDENTE}"
    )


def converter(data: dict, por_plano: dict[tuple[str, int], tuple[str, str]]) -> int:
    """broll -> photo + asset_id + motion; planos seguidos da mesma imagem viram um só. Devolve quantos."""
    convertidos = 0
    motion_i = 0
    for s in data["scenes"]:
        novos = []
        anterior_asset = None
        for i, shot in enumerate(s["shots"]):
            chave = (s["id"], i)
            if chave not in por_plano:
                novos.append(shot)
                anterior_asset = None
                continue
            arq, desc = por_plano[chave]
            if shot["kind"] != "broll":
                raise SystemExit(f"{chave}: esperado broll, achei {shot['kind']}")
            asset_id = "ia-" + Path(arq).stem
            if asset_id == anterior_asset:
                continue  # mesma imagem do plano anterior: o movimento segue sem reiniciar
            close = desc.startswith("AVATAR") and re.search(r"retrato|close|de frente|rosto", desc)
            motion = "push_in" if close else MOTIONS[motion_i % len(MOTIONS)]
            motion_i += 1
            novo = {"kind": "photo", "anchor": shot["anchor"]}
            if shot.get("claims"):
                novo["claims"] = shot["claims"]
            novo.update(
                {
                    "visual_need": shot["visual_need"],
                    "search_query": shot["search_query"],
                    "asset_id": asset_id,
                    "motion": motion,
                }
            )
            novos.append(novo)
            anterior_asset = asset_id
            convertidos += 1
        s["shots"] = novos
    return convertidos


def extensao(path: Path) -> str:
    """Extensão pelo conteúdo real (as imagens do dono são JPEG com nome .png)."""
    with path.open("rb") as f:
        cabecalho = f.read(8)
    return ".png" if cabecalho == b"\x89PNG\r\n\x1a\n" else ".jpg"


def gravar_ativo(asset: Asset, origem: Path) -> str:
    """Devolve 'novo', 'igual' ou 'refeito'; recusa mexer em ativo aprovado."""
    js = ASSETS / f"{asset.id}.json"
    destino = ASSETS / f"{asset.id}{extensao(origem)}"
    midias = [ASSETS / f"{asset.id}{s}" for s in (".jpg", ".jpeg", ".png", ".webp")]
    if js.exists():
        atual = Asset.model_validate_json(js.read_text(encoding="utf-8"))
        if atual.sha256 == asset.sha256 and destino.exists():
            return "igual"
        if atual.review_status == "approved":
            raise SystemExit(f"{asset.id}: aprovado, não substituo (reabra com vp reopen --step assets)")
        notas_novas = CONFERIDA.sub(PENDENTE, atual.usage_notes)
        asset = atual.model_copy(update={"sha256": asset.sha256, "usage_notes": notas_novas,
                                         "used_in_scenes": asset.used_in_scenes})
        estado = "refeito"
    else:
        estado = "novo"
    # mídia anterior com outra extensão não pode sobrar: o render lê .jpg antes de .png
    for antiga in midias:
        if antiga != destino and antiga.exists():
            antiga.unlink()
    shutil.copyfile(origem, destino)
    js.write_text(asset.model_dump_json(indent=2) + "\n", encoding="utf-8")
    return estado


def main() -> int:
    arquivos = sorted(p.name for p in SRC.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg"})
    por_prefixo: dict[str, str] = {}
    for nome in arquivos:
        m = re.match(r"^(x?\d{2})-", nome)
        if m:
            if m.group(1) in por_prefixo:
                raise SystemExit(f"prefixo repetido: {m.group(1)}")
            por_prefixo[m.group(1)] = nome
    textos = prompts()
    with (IA / "mapa-planos.csv").open(encoding="utf-8") as f:
        mapa = list(csv.DictReader(f))

    # 1. imagem efetiva de cada plano (com fallback) e cenas por imagem
    planos: list[tuple[str, int, str, str]] = []  # (cena, idx, arquivo, descricao)
    fallbacks: list[tuple[str, str, str]] = []
    for r in mapa:
        pref = r["imagem"]
        if pref not in por_prefixo:
            fallbacks.append((r["cena"], pref, r["fallback_sem_extra"]))
            pref = r["fallback_sem_extra"]
        planos.append((r["cena"], int(r["plano_idx"]), por_prefixo[pref], r["descricao_do_roteiro"]))
    usadas: dict[str, list[str]] = {}
    for cena, _, arq, _ in planos:
        usadas.setdefault(arq, [])
        if cena not in usadas[arq]:
            usadas[arq].append(cena)

    # 2. scenes.json (só se ainda estiver na forma do roteirista, com planos broll sem asset_id)
    scenes_path = EP / "scenes.json"
    data = json.loads(scenes_path.read_text(encoding="utf-8"))
    ja_convertido = any("asset_id" in sh for s in data["scenes"] for sh in s["shots"])
    convertidos = 0
    if not ja_convertido:
        convertidos = converter(data, {(c, i): (arq, desc) for c, i, arq, desc in planos})
    total_planos = sum(len(s["shots"]) for s in data["scenes"])
    ScenesManifest.model_validate(data)  # o schema do projeto aceita?

    # 3. ativos
    agora = datetime.now().astimezone().isoformat(timespec="seconds")
    ativos: list[tuple[Asset, Path]] = []
    for arq, cenas_uso in sorted(usadas.items()):
        cena_prompt, prompt = textos[arq]
        desc = next(d for c, _, a, d in planos if a == arq)
        asset = Asset.model_validate(
            {
                "id": "ia-" + Path(arq).stem,
                "provider": "original",
                "provider_id": f"imagens-ia/personagem/{arq}",
                "license_id": "Generated",
                "usage_notes": notas(arq, cena_prompt, prompt, desc),
                "retrieved_at": agora,
                "sha256": sha256(SRC / arq),
                "review_status": "needs_review",
                "used_in_scenes": sorted(cenas_uso),
            }
        )
        ativos.append((asset, SRC / arq))

    # 4. registro.csv
    guia = guia_prompts()
    formato = "JPEG 1024x572 com extensão .png"
    linhas = []
    for nome in arquivos:
        if nome in textos:
            cena, _ = textos[nome]
            pid = Path(nome).stem.split("-")[0]
            obs = f"registrado como assets/ia-{Path(nome).stem}" if nome in usadas else "sem plano no mapa"
        else:
            pid, _ = guia.get(nome, ("?", ""))
            cena = "folha" if nome.startswith("00") else "capa"
            obs = "folha de referência do personagem (não entra no vídeo)" if nome.startswith("00") else ""
        linhas.append([f"personagem/{nome}", pid, cena, GERADOR, HOJE, "", f"{formato}; {obs}"])
    for nome in sorted(p.name for p in (IA / "capa").iterdir()):
        pid, _ = guia.get(nome, ("3?", ""))
        obs = "candidata a miniatura (skill miniatura, entre os gates 3 e 4)"
        linhas.append([f"capa/{nome}", pid, "capa", GERADOR, HOJE, "", f"{formato}; {obs}"])
    faltam = [f for f in textos if f not in arquivos]
    if "00c-elenco.png" not in arquivos:
        faltam.append("00c-elenco.png")

    print(f"arquivos em personagem/: {len(arquivos)}; prompts: {len(textos)}; faltam: {faltam}")
    print(f"planos do mapa: {len(planos)}; fallbacks: {fallbacks}")
    print(f"imagens usadas: {len(usadas)}; ativos: {len(ativos)}")
    if ja_convertido:
        print(f"scenes.json já convertido ({total_planos} planos); conversão pulada")
    else:
        print(f"planos convertidos em photo: {convertidos}; planos depois da fusão: {total_planos}")
        motions = Counter(sh["motion"] for s in data["scenes"] for sh in s["shots"] if sh["kind"] == "photo")
        print("motions:", motions)
    print("linhas do registro.csv:", len(linhas))
    if not APLICAR:
        print("(simulação; nada gravado)")
        return 0

    ASSETS.mkdir(exist_ok=True)
    estados = Counter(gravar_ativo(asset, origem) for asset, origem in ativos)
    print("ativos:", dict(estados))
    if not ja_convertido:
        scenes_path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    registro = IA / "registro.csv"
    if estados.get("novo") or not registro.exists():
        with registro.open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f)
            w.writerow(["arquivo", "prompt_id", "cena", "gerador", "data", "aprovado", "observacao"])
            w.writerows(linhas)
        print("registro.csv reescrito")
    else:
        print("registro.csv mantido (nenhum ativo novo)")
    print("gravado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
