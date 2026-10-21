"""Coleta vídeos de páginas públicas do YouTube para o CSV da medição de demanda.

Uso:
  python3 -I coleta.py canal <@handle> <grupo> <csv> [--paginas N] [--bruto DIR]
  python3 -I coleta.py busca "<consulta>" <grupo> <csv> [--bruto DIR]
  python3 -I coleta.py idioma <csv>

- canal: aba /@handle/videos e as páginas seguintes (as mesmas que o navegador carrega ao rolar), até N
  páginas (padrão 4) ou até passar de 180 dias.
- busca: primeira página de /results. Cada linha leva o canal de quem publicou.
- idioma: para um vídeo de cada canal do CSV, imprime o título original (oEmbed) ao lado do coletado. Com
  hl=pt, o YouTube traduz títulos em inglês e espanhol, então confira antes de pôr o canal num grupo.

Sem login nem cookies. Pausa de 2,5 s antes de cada requisição. Em HTTP 429, para com código 3.
"""

from __future__ import annotations

import argparse
import csv
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

UA = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0 Safari/537.36"
PAUSE_S = 2.5
COLUMNS = [
    "canal", "grupo", "video_id", "titulo", "duracao_s", "views", "idade_texto", "idade_dias_aprox",
    "data_coleta", "fonte", "inscritos_canal",
]


def fetch(url: str, body: dict | None = None) -> str:
    time.sleep(PAUSE_S)
    headers = {"User-Agent": UA, "Accept-Language": "pt-BR,pt;q=0.9"}
    data = None
    if body is not None:
        headers["Content-Type"] = "application/json"
        data = json.dumps(body).encode()
    try:
        with urllib.request.urlopen(urllib.request.Request(url, data, headers), timeout=60) as response:
            return response.read().decode("utf-8", errors="ignore")
    except urllib.error.HTTPError as error:
        if error.code == 429:
            print(f"429 em {url}: pare e registre", file=sys.stderr)
            sys.exit(3)
        raise


def initial_data(html: str) -> dict:
    match = re.search(r"var ytInitialData = (\{.*?\});</script>", html, re.S)
    return json.loads(match.group(1)) if match else {}


def text(value) -> str:
    if not value:
        return ""
    if isinstance(value, str):
        return value
    if "simpleText" in value:
        return value["simpleText"]
    if "content" in value:
        return value["content"]
    return "".join(run.get("text", "") for run in value.get("runs", []))


def seconds(value: str) -> int | None:
    if not value or not re.fullmatch(r"\d{1,3}(:\d{2}){1,2}", value):
        return None
    total = 0
    for part in value.split(":"):
        total = total * 60 + int(part)
    return total


def count(value: str) -> int | None:
    """'46 mil', '1,2 mi', '892', '46 mil visualizações', 'Nenhuma visualização'."""
    if not value:
        return None
    value = value.replace("\xa0", " ").strip()
    if value.lower().startswith("nenhuma"):
        return 0
    match = re.match(r"([\d.,]+)\s*(mil|mi|bi)?", value)
    if not match:
        return None
    number, unit = match.groups()
    number = number.replace(".", "").replace(",", "." if unit else "")
    return round(float(number) * {None: 1, "mil": 1e3, "mi": 1e6, "bi": 1e9}[unit])


def age_days(value: str) -> int | None:
    match = re.search(r"há (\d+)\s*(\w+)", value or "")
    if not match:
        return None
    n, unit = int(match.group(1)), match.group(2)
    if unit.startswith("sem"):
        return 7 * n
    if unit.startswith(("segundo", "minuto", "hora")):
        return 0
    if unit.startswith("dia"):
        return n
    if unit.startswith(("mês", "mes")):
        return 30 * n
    if unit.startswith("ano"):
        return 365 * n
    return None


def walk(node, keys=("lockupViewModel", "videoRenderer")):
    if isinstance(node, dict):
        for key in keys:
            if key in node:
                yield key, node[key]
                return
        for value in node.values():
            yield from walk(value, keys)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value, keys)


def handle_in(node) -> str | None:
    match = re.search(r'"canonicalBaseUrl": "/(@[^"]+)"', json.dumps(node, ensure_ascii=False))
    return urllib.parse.unquote(match.group(1)) if match else None


def from_lockup(node: dict) -> dict | None:
    if node.get("contentType") not in (None, "LOCKUP_CONTENT_TYPE_VIDEO"):
        return None
    meta = node.get("metadata", {}).get("lockupMetadataViewModel", {})
    image = json.dumps(node.get("contentImage", {}), ensure_ascii=False)
    badges = re.findall(r'"thumbnailBadgeViewModel": \{"text": "([^"]+)"', image)
    parts = [
        text(part.get("text"))
        for row in meta.get("metadata", {}).get("contentMetadataViewModel", {}).get("metadataRows", [])
        for part in row.get("metadataParts", [])
    ]
    views_pattern = r"visualiza|^\d[\d.,]*\s*(mil|mi|bi)?$"
    views = next((p for p in parts if re.search(views_pattern, p.replace("\xa0", " "))), "")
    age = next((p for p in parts if p.startswith("há ")), "")
    return {
        "video_id": node.get("contentId"), "titulo": text(meta.get("title")),
        "duracao_s": next((seconds(b) for b in badges if seconds(b)), None),
        "views_txt": views, "idade_texto": age, "handle": handle_in(meta),
    }


def from_renderer(node: dict) -> dict:
    owner = node.get("ownerText") or node.get("longBylineText") or {}
    handle = None
    for run in owner.get("runs", []):
        url = run.get("navigationEndpoint", {}).get("browseEndpoint", {}).get("canonicalBaseUrl", "")
        if url.startswith("/@"):
            handle = urllib.parse.unquote(url[1:])
    return {
        "video_id": node.get("videoId"), "titulo": text(node.get("title")),
        "duracao_s": seconds(text(node.get("lengthText"))), "views_txt": text(node.get("viewCountText")),
        "idade_texto": text(node.get("publishedTimeText")), "handle": handle,
    }


def videos(data: dict) -> list[dict]:
    found, seen = [], set()
    for kind, node in walk(data):
        video = from_lockup(node) if kind == "lockupViewModel" else from_renderer(node)
        if video and video["video_id"] and video["video_id"] not in seen:
            seen.add(video["video_id"])
            found.append(video)
    return found


def subscribers(data: dict) -> int | None:
    header = json.dumps(data.get("header", {}), ensure_ascii=False).replace("\xa0", " ")
    match = re.search(r'"content": "([\d.,]+ ?(?:mil|mi)?) (?:de )?inscritos?"', header)
    return count(match.group(1)) if match else None


def continuation_token(node) -> str | None:
    if isinstance(node, dict):
        if "continuationCommand" in node:
            return node["continuationCommand"].get("token")
        children = node.values()
    elif isinstance(node, list):
        children = node
    else:
        return None
    for child in children:
        token = continuation_token(child)
        if token:
            return token
    return None


def save_raw(directory: Path | None, name: str, content: str) -> None:
    if directory:
        directory.mkdir(parents=True, exist_ok=True)
        (directory / name).write_text(content, encoding="utf-8")


def collect_channel(handle: str, pages: int, raw: Path | None) -> tuple[list[dict], int | None]:
    handle = "@" + handle.lstrip("@")
    html = fetch(f"https://www.youtube.com/{urllib.parse.quote(handle)}/videos?hl=pt&gl=BR")
    save_raw(raw, f"{handle[1:]}.p1.html", html)
    data = initial_data(html)
    found, subs = videos(data), subscribers(data)
    key = re.search(r'"INNERTUBE_API_KEY":"([^"]+)"', html)
    version = re.search(r'"INNERTUBE_CLIENT_VERSION":"([^"]+)"', html)
    token = continuation_token(data)
    for page in range(2, pages + 1):
        ages = [age_days(v["idade_texto"]) or 0 for v in found]
        if not (token and key and version) or (ages and max(ages) > 180):
            break
        body = {"context": {"client": {"clientName": "WEB", "clientVersion": version.group(1), "hl": "pt",
                                       "gl": "BR"}}, "continuation": token}
        url = f"https://www.youtube.com/youtubei/v1/browse?key={key.group(1)}&prettyPrint=false"
        payload = fetch(url, body)
        save_raw(raw, f"{handle[1:]}.p{page}.json", payload)
        data = json.loads(payload)
        found += [v for v in videos(data) if v["video_id"] not in {f["video_id"] for f in found}]
        token = continuation_token(data)
    for video in found:
        video["handle"] = handle
    return found, subs


def collect_search(query: str, raw: Path | None) -> list[dict]:
    html = fetch(f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(query)}&hl=pt&gl=BR")
    save_raw(raw, "busca_" + re.sub(r"\W+", "_", query.lower()).strip("_")[:60] + ".html", html)
    return [v for v in videos(initial_data(html)) if v["handle"]]


def blank(value: int | None) -> int | str:
    return "" if value is None else value


def append(path: Path, group: str, found: list[dict], source: str, subs: int | None) -> None:
    new = not path.exists()
    with path.open("a", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(target, fieldnames=COLUMNS)
        if new:
            writer.writeheader()
        for video in found:
            writer.writerow({
                "canal": video["handle"], "grupo": group, "video_id": video["video_id"],
                "titulo": video["titulo"], "duracao_s": blank(video["duracao_s"]),
                "views": blank(count(video["views_txt"])), "idade_texto": video["idade_texto"],
                "idade_dias_aprox": blank(age_days(video["idade_texto"])),
                "data_coleta": date.today().isoformat(), "fonte": source, "inscritos_canal": blank(subs),
            })
    print(f"{len(found)} vídeos ({group}) -> {path}")


def check_language(path: Path) -> None:
    first: dict[str, tuple[str, str]] = {}
    with path.open(encoding="utf-8") as source:
        for row in csv.DictReader(source):
            first.setdefault(row["canal"], (row["video_id"], row["titulo"]))
    print("canal | título original (oEmbed) | título coletado")
    for channel, (video_id, collected) in first.items():
        watch = urllib.parse.quote(f"https://www.youtube.com/watch?v={video_id}", safe="")
        try:
            original = json.loads(fetch(f"https://www.youtube.com/oembed?url={watch}&format=json")).get("title")
        except urllib.error.HTTPError as error:
            original = f"HTTP {error.code}"
        print(f"{channel} | {original} | {collected}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("modo", choices=["canal", "busca", "idioma"])
    parser.add_argument("alvo", help="@handle, consulta ou, no modo idioma, o CSV")
    parser.add_argument("grupo", nargs="?")
    parser.add_argument("csv", nargs="?", type=Path)
    parser.add_argument("--paginas", type=int, default=4)
    parser.add_argument("--bruto", type=Path, help="pasta para guardar o HTML/JSON bruto (use o scratchpad)")
    args = parser.parse_args()
    if args.modo == "idioma":
        check_language(Path(args.alvo))
        return
    if not (args.grupo and args.csv):
        parser.error("canal e busca pedem <grupo> e <csv>")
    if args.modo == "canal":
        found, subs = collect_channel(args.alvo, args.paginas, args.bruto)
        append(args.csv, args.grupo, found, "aba /videos do canal", subs)
    else:
        append(args.csv, args.grupo, collect_search(args.alvo, args.bruto), f"busca: {args.alvo}", None)


if __name__ == "__main__":
    main()
