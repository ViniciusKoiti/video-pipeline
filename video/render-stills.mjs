// Quadros avulsos de planos (folha de estilo). Empacota uma vez; uma imagem por job.
// Uso: node render-stills.mjs pedido.json
// pedido: {publicDir, jobs: [{out, frame, props}]}   (props no formato de SceneProps)
import {readFileSync, rmSync} from "node:fs";
import path from "node:path";
import {bundle} from "@remotion/bundler";
import {renderStill, selectComposition} from "@remotion/renderer";

const request = JSON.parse(readFileSync(process.argv[2], "utf8"));
const serveUrl = await bundle({entryPoint: path.resolve("src/index.ts"), publicDir: request.publicDir});
try {
  for (const job of request.jobs) {
    const composition = await selectComposition({serveUrl, id: "Shot", inputProps: job.props});
    await renderStill({composition, serveUrl, inputProps: job.props, output: job.out, frame: job.frame, imageFormat: "png"});
    console.log(JSON.stringify({done: job.out}));
  }
} finally {
  rmSync(serveUrl, {recursive: true, force: true}); // o pacote (~250 MB) não fica no /tmp
}
