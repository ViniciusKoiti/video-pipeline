// Quadros avulsos do clipe de letra, para conferir o texto no quadro sem renderizar vídeo.
// Uso: node render-clipe-stills.mjs <pasta de saída> <retrato: 0|1> <segundo> [<segundo> ...]
import path from "node:path";
import {bundle} from "@remotion/bundler";
import {renderStill, selectComposition} from "@remotion/renderer";

const [outDir, retrato, ...seconds] = process.argv.slice(2);
const inputProps = {inicio: 0, fim: null, audio: null, retrato: retrato === "1"};
const serveUrl = await bundle({entryPoint: path.resolve("src/index.ts")});
const composition = await selectComposition({serveUrl, id: "Clipe", inputProps});
for (const s of seconds) {
  const output = path.join(outDir, `${retrato === "1" ? "v" : "h"}-${String(s).padStart(6, "0")}.jpeg`);
  await renderStill({composition, serveUrl, inputProps, output, frame: Math.round(Number(s) * 30), imageFormat: "jpeg",
    scale: 0.4});
  console.log(output);
}
