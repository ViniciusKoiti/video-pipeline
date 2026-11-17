"""Gera imagens pela tela de um site de IA (Gemini, ChatGPT), no Chrome que o dono abriu e logou.

Uso (raiz do auto-play, com `uv sync --extra navegador`):
  1. O dono abre o Chrome com a porta de depuração e um perfil só para isto, e faz o login à mão:
       chromium --remote-debugging-port=9222 --user-data-dir=$HOME/.cache/chrome-imagens
  2. .venv/bin/python scripts/provisorio/imagens_navegador.py plano  pedidos.json --saida PASTA
     .venv/bin/python scripts/provisorio/imagens_navegador.py mapear gemini
     .venv/bin/python scripts/provisorio/imagens_navegador.py gerar pedidos.json --saida PASTA --site gemini \
         [--teto 20] [--intervalo 45] [--espera 180] [--cdp http://127.0.0.1:9222]

`plano` não abre navegador: mostra o que falta. `mapear` abre o site e lista o que cada seletor de
`sites_imagem.toml` encontra, mais os botões e campos da página, para conferir e corrigir os seletores.
`gerar` faz um pedido por conversa nova: anexa as referências, digita o prompt, espera a imagem e a grava em
PASTA com o id do pedido (fila e registro em `fila_imagens.py`).

Freios (decisão do dono, 2026-11-11: conta principal, sem API): uma imagem por vez, `--intervalo` segundos
entre pedidos, `--teto` por rodada. Login, captcha ou aviso de limite param a rodada na hora; o script não
tenta passar por verificação nem disfarça a automação. Duas falhas seguidas também param (seletor quebrado).
Os termos de cada site para uso automatizado da tela não foram conferidos: o risco para a conta é do dono.
Imagem gerada é ilustração (§2.4) e só entra em episódio como ativo `Generated`, pelo gate 3.

Trocar ou somar site: um bloco em `sites_imagem.toml`; um site que não caiba nos seletores implementa `Site`.
"""

from __future__ import annotations

import argparse
import base64
import contextlib
import sys
import time
import tomllib
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import fila_imagens as fila  # noqa: E402

from app.commands.errors import run  # noqa: E402
from app.errors import PipelineError  # noqa: E402

SITES = Path(__file__).with_name("sites_imagem.toml")
FALHAS_SEGUIDAS = 2
LADO_MINIMO = 256
# Última imagem carregada da resposta, em base64. Lê o arquivo pelo endereço; se o endereço já não responde
# (blob revogado), copia os pixels já decodificados para um PNG.
LER_IMAGEM = f"""async (imgs) => {{
  const boas = imgs.filter(i => i.complete && i.naturalWidth >= {LADO_MINIMO});
  if (!boas.length) return null;
  const img = boas[boas.length - 1];
  const base64 = async (blob) => {{
    const bytes = new Uint8Array(await blob.arrayBuffer());
    let texto = '';
    for (let i = 0; i < bytes.length; i += 32768) {{
      texto += String.fromCharCode(...bytes.subarray(i, i + 32768));
    }}
    return btoa(texto);
  }};
  try {{
    return await base64(await (await fetch(img.src)).blob());
  }} catch (erro) {{
    const tela = document.createElement('canvas');
    tela.width = img.naturalWidth;
    tela.height = img.naturalHeight;
    tela.getContext('2d').drawImage(img, 0, 0);
    return await base64(await new Promise(feito => tela.toBlob(feito, 'image/png')));
  }}
}}"""
ULTIMA_IMAGEM = f"""(imgs) => {{
  const boas = imgs.filter(i => i.complete && i.naturalWidth >= {LADO_MINIMO});
  return boas.length ? (boas[boas.length - 1].currentSrc || boas[boas.length - 1].src) : null;
}}"""
LISTAR = """() => [...document.querySelectorAll(
    'button, [role=button], input, textarea, [contenteditable=true]')]
  .filter(e => e.offsetParent !== null || e.type === 'file')
  .map(e => [e.tagName.toLowerCase(), e.type || '', e.getAttribute('aria-label') || '',
             e.getAttribute('data-testid') || '', (e.innerText || '').trim().slice(0, 40)].join(' | '))"""


class Bloqueio(PipelineError, RuntimeError):
    """Login, verificação ou limite: a rodada inteira para."""


class SemImagem(PipelineError, RuntimeError):
    """O pedido não rendeu imagem: registra a falha e segue para o próximo."""


class Site(Protocol):
    nome: str

    def gerar(self, pedido: fila.Pedido, espera_s: int) -> bytes: ...


def config(nome: str) -> dict[str, Any]:
    sites = tomllib.loads(SITES.read_text(encoding="utf-8"))
    if nome not in sites:
        raise PipelineError(f"site {nome!r} não está em {SITES.name} (há: {', '.join(sites)})")
    return sites[nome]


class SiteDeConversa:
    """Site de conversa operado só pelos seletores do TOML."""

    def __init__(self, nome: str, page: Any, cfg: dict[str, Any]) -> None:
        self.nome, self.page, self.cfg = nome, page, cfg

    def conferir_bloqueio(self) -> None:
        url = self.page.url
        for trecho in self.cfg["bloqueio_url"]:
            if trecho in url:
                raise Bloqueio(f"o site foi para {trecho} (login ou verificação); rodada parada")
        for texto in self.cfg["bloqueio_texto"]:
            if self.page.get_by_text(texto, exact=False).first.is_visible():
                raise Bloqueio(f"o site mostrou {texto!r}; rodada parada")

    def anexar(self, refs: tuple[Path, ...]) -> None:
        arquivos = [str(r) for r in refs]
        cliques = self.cfg["anexo_botao"]
        if not cliques:
            self.page.locator(self.cfg["anexo"]).first.set_input_files(arquivos)
            return
        with self.page.expect_file_chooser() as escolha:
            for seletor in cliques:
                self.page.locator(seletor).first.click()
        escolha.value.set_files(arquivos)

    def gerar(self, pedido: fila.Pedido, espera_s: int) -> bytes:
        page, cfg = self.page, self.cfg
        self.escutar_rede()
        page.goto(cfg["url"], wait_until="domcontentloaded")
        caixa = page.locator(cfg["caixa"]).first
        try:
            caixa.wait_for(state="visible", timeout=30_000)
        except Exception as error:  # noqa: BLE001 - o Playwright não é importado no topo
            self.conferir_bloqueio()
            raise SemImagem(f"não achei a caixa do prompt ({cfg['caixa']})") from error
        self.conferir_bloqueio()
        for seletor in cfg.get("preparo", []):
            self.conferir_bloqueio()  # o menu aberto pelo clique anterior pode trazer o aviso de limite
            alvo = page.locator(seletor).first
            if alvo.get_attribute("aria-disabled") == "true":  # ferramenta desligada pelo site: limite de uso
                raise Bloqueio(f"o site desativou {seletor} (limite de uso?); rodada parada")
            if alvo.get_attribute("aria-checked") == "true":  # já ligado: clicar desligaria
                page.keyboard.press("Escape")
                continue
            alvo.click()
            page.wait_for_timeout(800)
        if pedido.refs:
            self.anexar(pedido.refs)
            page.wait_for_timeout(3_000)
        antes = page.locator(cfg["imagem"]).count()
        self.desde = len(self.respostas)  # só respostas depois do envio: nunca o anexo de referência
        self.refs_sha = {fila.sha256(r.read_bytes()) for r in pedido.refs}
        caixa.click()
        page.keyboard.insert_text(pedido.prompt)
        if cfg["enviar"]:
            page.locator(cfg["enviar"]).first.click()
        else:
            page.keyboard.press("Enter")
        limite = time.monotonic() + espera_s
        while time.monotonic() < limite:
            page.wait_for_timeout(2_000)
            self.conferir_bloqueio()
            ocupado = cfg["ocupado"] and page.locator(cfg["ocupado"]).first.is_visible()
            if not ocupado and page.locator(cfg["imagem"]).count() > antes:
                print(f"  conversa: {page.url}", file=sys.stderr)  # para reabrir a imagem depois, se preciso
                return self.baixar()
        raise SemImagem(f"sem imagem nova em {espera_s} s")

    def baixar(self) -> bytes:
        page, cfg = self.page, self.cfg
        if cfg["baixar"] == "botao":
            with page.expect_download() as download:
                page.locator(cfg["botao_baixar"]).last.click()
            return Path(download.value.path()).read_bytes()
        for _ in range(45):  # a imagem aparece na conversa antes de terminar de carregar
            page.wait_for_timeout(2_000)
            # imagem preguiçosa só carrega quando entra na tela; sem ela, tenta no próximo giro
            with contextlib.suppress(Exception):
                page.locator(cfg["imagem"]).last.scroll_into_view_if_needed(timeout=2_000)
            try:
                dados = page.locator(cfg["imagem"]).evaluate_all(LER_IMAGEM)
            except Exception:  # noqa: BLE001 - canvas "tainted": imagem de outra origem sem CORS
                dados = self.ler_pelo_navegador()
            if dados:
                return base64.b64decode(dados)
        raise SemImagem(f"nenhuma imagem carregada com {LADO_MINIMO} px ou mais")

    def escutar_rede(self) -> None:
        """Guarda as respostas de imagem da aba (CDP), para ler os bytes originais sem nova requisição."""
        self.respostas: list[tuple[str, str]] = []
        self.cdp = self.page.context.new_cdp_session(self.page)
        buffers = {"maxTotalBufferSize": 200_000_000, "maxResourceBufferSize": 50_000_000}
        self.cdp.send("Network.enable", buffers)

        def guardar(evento: dict[str, Any]) -> None:
            resposta = evento["response"]
            if resposta.get("mimeType", "").startswith("image/"):
                self.respostas.append((evento["requestId"], resposta["url"]))

        self.cdp.on("Network.responseReceived", guardar)

    def ler_pelo_navegador(self) -> str | None:
        """Bytes da imagem pela resposta de rede que o navegador já recebeu.

        O endereço do <img> pode diferir do da resposta (redirecionamento, parâmetros de tamanho): aceita o
        mesmo endereço ou o mesmo começo, só entre as respostas chegadas depois do envio, e recusa bytes
        iguais a uma referência anexada. Sem achar, devolve None e o laço de baixar() tenta de novo; cada
        tentativa sem sucesso escreve o endereço no stderr para diagnóstico."""
        src = self.page.locator(self.cfg["imagem"]).evaluate_all(ULTIMA_IMAGEM)
        if not src:
            return None
        base = src.split("=")[0].split("?")[0]
        novas = self.respostas[self.desde:]
        candidatas = [r for r in novas if r[1] == src] or [r for r in novas if r[1].startswith(base)]
        if not candidatas and "/gg-dl/" in src:  # Gemini: <img> em gg-dl, resposta em rd-gg-dl
            candidatas = [r for r in novas if "gg-dl/" in r[1]]
        maior: str | None = None
        for pedido_id, _ in candidatas:
            try:
                corpo = self.cdp.send("Network.getResponseBody", {"requestId": pedido_id})
            except Exception:  # noqa: BLE001 - corpo fora do buffer: tenta a próxima
                continue
            dados = corpo["body"] if corpo.get("base64Encoded") else base64.b64encode(
                corpo["body"].encode("latin-1")).decode()
            if fila.sha256(base64.b64decode(dados)) in self.refs_sha:
                continue
            if maior is None or len(dados) > len(maior):  # a imagem inteira, não a miniatura
                maior = dados
        if maior:
            return maior
        print(f"  [diagnóstico] src={src[:140]} respostas={[u[:90] for _, u in novas[-4:]]}",
              file=sys.stderr)
        return None


def abrir(cdp: str) -> tuple[Any, Any]:
    """Conecta ao Chrome do dono e abre uma aba nova nele. Devolve (playwright, página)."""
    from playwright.sync_api import Error, sync_playwright

    pw = sync_playwright().start()
    try:
        browser = pw.chromium.connect_over_cdp(cdp)
    except Error as error:
        pw.stop()
        raise PipelineError(
            f"não conectei ao Chrome em {cdp}; abra-o com --remote-debugging-port=9222 e faça o login"
        ) from error
    return pw, browser.contexts[0].new_page()


def plano(args: argparse.Namespace) -> int:
    pedidos = fila.ler_pedidos(args.pedidos)
    faltam = fila.pendentes(pedidos, args.saida)
    print(f"{len(pedidos)} pedidos; {len(pedidos) - len(faltam)} prontos; {len(faltam)} pendentes")
    for pedido in faltam:
        print(f"  {pedido.id}  refs={len(pedido.refs)}  {pedido.prompt[:70]}")
    return 0


def mapear(args: argparse.Namespace) -> int:
    cfg = config(args.site)
    pw, page = abrir(args.cdp)
    try:
        page.goto(cfg["url"], wait_until="domcontentloaded")
        page.wait_for_timeout(5_000)
        print(f"url atual: {page.url}")
        for campo in ("caixa", "enviar", "anexo", "imagem", "ocupado", "botao_baixar"):
            if cfg[campo]:
                print(f"  {campo:13} {page.locator(cfg[campo]).count():3} elemento(s)  {cfg[campo]}")
        print("botões e campos visíveis (tag | type | aria-label | data-testid | texto):")
        for linha in page.evaluate(LISTAR):
            print(f"  {linha}")
    finally:
        page.close()
        pw.stop()
    return 0


def gerar(args: argparse.Namespace) -> int:
    faltam = fila.pendentes(fila.ler_pedidos(args.pedidos), args.saida)[: args.teto]
    if not faltam:
        print("nada pendente")
        return 0
    pw, page = abrir(args.cdp)
    site: Site = SiteDeConversa(args.site, page, config(args.site))
    seguidas = 0
    try:
        for i, pedido in enumerate(faltam):
            if i:
                time.sleep(args.intervalo)
            try:
                destino = fila.guardar(args.saida, pedido, site.nome, site.gerar(pedido, args.espera))
            except Bloqueio as error:
                fila.anotar_falha(args.saida, pedido, site.nome, str(error))
                raise
            except (SemImagem, fila.FilaError) as error:
                fila.anotar_falha(args.saida, pedido, site.nome, str(error))
                print(f"  {pedido.id}: falhou ({error})")
                seguidas += 1
                if seguidas >= FALHAS_SEGUIDAS:
                    aviso = f"{seguidas} falhas seguidas; conferir seletores com `mapear`"
                    raise PipelineError(aviso) from error
                continue
            seguidas = 0
            print(f"  {pedido.id}: {destino}")
    finally:
        page.close()
        pw.stop()
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="comando", required=True)
    for nome, acao in (("plano", plano), ("gerar", gerar)):
        p = sub.add_parser(nome)
        p.add_argument("pedidos", type=Path)
        p.add_argument("--saida", type=Path, required=True)
        p.set_defaults(acao=acao)
    g = sub.choices["gerar"]
    g.add_argument("--site", default="gemini")
    g.add_argument("--teto", type=int, default=20, help="máximo de imagens nesta rodada")
    g.add_argument("--intervalo", type=int, default=45, help="segundos entre pedidos")
    g.add_argument("--espera", type=int, default=180, help="segundos à espera de cada imagem")
    m = sub.add_parser("mapear")
    m.add_argument("site")
    m.set_defaults(acao=mapear)
    for p in (g, m):
        p.add_argument("--cdp", default="http://127.0.0.1:9222")
    args = parser.parse_args()
    return args.acao(args)


if __name__ == "__main__":
    raise SystemExit(run("imagens_navegador", main))
