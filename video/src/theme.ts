import {continueRender, delayRender, staticFile, useVideoConfig} from "remotion";
import {floatingSafeArea} from "@viniciusk/motion-kit";
import {editorial} from "@viniciusk/motion-kit/theme";
import interUrl from "./fonts/InterVariable.woff2";

// Identidade "negócios moderno" (#48): grafite, branco-gelo e UM destaque dourado.
// Tamanhos são proporcionais à altura do quadro (1080p = 1).
export const theme = {
  bg: "#0E1116",
  surface: "#161B22",
  text: "#EDEDE8",
  muted: "#9AA4B2",
  accent: "#F2B134",
  accentSoft: "rgba(242, 177, 52, 0.18)",
  line: "rgba(237, 237, 232, 0.14)",
  font: "Inter, 'DejaVu Sans', sans-serif",
} as const;

export const u = (height: number, px: number) => (px * height) / 1080;

// O quadro do render (ADR 014): paisagem 16:9 ou retrato 9:16. A unidade `u` mede pelo lado curto, então os px de
// projeto valem os mesmos nos dois perfis (em paisagem, lado curto = altura: nada muda). As peças do kit medem
// pela altura (`useUnit`); `kit(px)` converte px finais do quadro para a prop que elas esperam. Em retrato, a
// legenda, a fonte, a tarja e a janela ficam dentro da área segura `vertical` das plataformas.
export type Frame = {
  width: number;
  height: number;
  portrait: boolean;
  u: (px: number) => number;
  kit: (px: number) => number;
  kitPx: (framePx: number) => number; // o mesmo, a partir de px já medidos no quadro (ex.: `safe`)
  safe: {top: number; right: number; bottom: number; left: number};
};

export const useFrame = (): Frame => {
  const {width, height} = useVideoConfig();
  const portrait = height > width;
  const unit = Math.min(width, height) / 1080;
  const kitUnit = height / 1080;
  const safe = portrait ? floatingSafeArea("vertical", {width, height}) : {top: 0, right: 0, bottom: 0, left: 0};
  return {
    width, height, portrait, u: (px) => px * unit, kit: (px) => (px * unit) / kitUnit,
    kitPx: (framePx) => framePx / kitUnit, safe,
  };
};

// Tema injetado nas peças do motion-kit (ADR 011): o preset `editorial` com as cores e a fonte acima.
export const motionTheme = {
  ...editorial,
  font: theme.font,
  bg: theme.bg,
  surface: theme.surface,
  text: theme.text,
  muted: theme.muted,
  accent: theme.accent,
  line: theme.line,
  neon: 0,
};

// Inter (SIL OFL 1.1, src/fonts/Inter-OFL.txt), carregada localmente: nenhum acesso à rede no render.
const fontReady = delayRender("fonte Inter");
const inter = new FontFace("Inter", `url(${interUrl}) format("woff2")`, {weight: "100 900"});
inter
  .load()
  .then((face) => {
    document.fonts.add(face);
    continueRender(fontReady);
  })
  .catch((error) => {
    console.error("Inter não carregou; usando DejaVu Sans", error);
    continueRender(fontReady);
  });

export const media = (path: string) => staticFile(path);
