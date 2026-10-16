import {staticFile} from "remotion";
import {createSpriteSkin} from "@viniciusk/motion-kit/host";
import type {HostSkin, SpriteManifest} from "@viniciusk/motion-kit/host";

// Pele `dono` (ADR 017, parte A): o desenho do dono em 12 imagens, uma por visema, de olho aberto e de olho
// fechado. As imagens são dado pessoal e ficam fora do Git, em `host/dono/` da pasta do episódio (a pasta
// pública do render); a origem e a licença do desenho ficam em `host/dono/origem.json` (app/media/host.py).
// Um gesto e uma expressão só: o resto do vocabulário do `<Host>` cai no repouso.
const WIDTH = 305;
const HEIGHT = 414;
const LICENSE = {name: "ver host/dono/origem.json", url: "", author: "dono do canal"};

export const donoSkin: HostSkin = {
  kind: "image",
  name: "dono",
  license: LICENSE,
  capabilities: {gestures: ["rest"], expressions: ["neutral"], look: false, blink: true},
  aspect: WIDTH / HEIGHT,
  canvas: {width: WIDTH, height: HEIGHT},
  mapViseme: {rest: "rest", mbp: "mbp", ei: "ei", a: "a", ou: "ou", fv: "fv"},
  mapExpression: {neutral: "neutral"},
  mapGesture: {rest: "rest"},
  render: (_identity, state) => staticFile(`host/dono/${state.viseme}${state.blink ? "-piscada" : ""}.png`),
};

// Pele `dono` em camadas (ADR 029): o `host/dono/sprites.json` (formato `host-sprites.v1` do motion-kit,
// conferido pelo `motion-kit sprites check` antes do render) diz a camada de cada imagem e quando ela
// aparece. Olhar, gestos e expressões são os que a arte tiver; o resto cai no repouso.
export const donoSpriteSkin = (manifest: SpriteManifest): HostSkin =>
  createSpriteSkin(manifest, {
    name: "dono",
    license: manifest.license ?? LICENSE,
    url: (file) => staticFile(`host/dono/${file}`),
  });
