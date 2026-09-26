import {continueRender, delayRender, staticFile} from "remotion";
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
