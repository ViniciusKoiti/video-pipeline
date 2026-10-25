// Renderiza cenas avulsas do template (uma composição "Scene" por cena), sem áudio.
// Empacota uma vez e reaproveita o Chrome entre as cenas. Uso: node render-scenes.mjs pedido.json
// pedido: {publicDir, crf, x264Preset, jpegQuality, concurrency, timeoutMs?, jobs: [{out, props}]}
// timeoutMs: quanto um quadro pode esperar por imagem ou vídeo (padrão do Remotion: 30 s); um JPEG de 15 MB e um
// B-roll pesado em 8 abas paralelas estouraram esse padrão em 2026-10-24.
import {readFileSync} from "node:fs";
import path from "node:path";
import {bundle} from "@remotion/bundler";
import {renderMedia, selectComposition} from "@remotion/renderer";

const request = JSON.parse(readFileSync(process.argv[2], "utf8"));
const serveUrl = await bundle({entryPoint: path.resolve("src/index.ts"), publicDir: request.publicDir});
for (const job of request.jobs) {
  const timeoutInMilliseconds = request.timeoutMs ?? 30000;
  const composition = await selectComposition({serveUrl, id: "Scene", inputProps: job.props, timeoutInMilliseconds});
  await renderMedia({
    composition, serveUrl, inputProps: job.props, outputLocation: job.out, codec: "h264",
    crf: request.crf, x264Preset: request.x264Preset, pixelFormat: "yuv420p", colorSpace: "bt709",
    jpegQuality: request.jpegQuality, concurrency: request.concurrency, muted: true, logLevel: "error",
    timeoutInMilliseconds,
  });
  console.log(JSON.stringify({done: job.out}));
}
