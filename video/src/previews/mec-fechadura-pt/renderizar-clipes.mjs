// Renderiza cada plano de clipes-manifesto.json (mec-fechadura-pt) como MP4 mudo 1920x1080, na faixa de quadros exata do plano.
// Empacota uma vez; um render por vez (CLAUDE.md §3). Saída em renders/mec-fechadura-pt/<pasta>/<asset-id>.mp4 e um log-render.jsonl.
// Plano com `segura_ultimo_quadro` > 0: renderiza o conteúdo e estende o último quadro com ffmpeg (tpad).
// Uso (de dentro de video/): node src/previews/mec-fechadura-pt/renderizar-clipes.mjs <pasta-de-saida> [asset-id ...]
import {appendFileSync, existsSync, mkdirSync, readFileSync, renameSync, statSync, unlinkSync} from "node:fs";
import {spawnSync} from "node:child_process";
import path from "node:path";
import {bundle} from "@remotion/bundler";
import {renderMedia, selectComposition} from "@remotion/renderer";

const raiz = path.resolve("..");
const [pasta, ...ids] = process.argv.slice(2);
if (!pasta) throw new Error("informe a pasta de saída (ex.: clipes-v2)");
const saidaDir = path.join(raiz, "renders/mec-fechadura-pt", pasta);
mkdirSync(saidaDir, {recursive: true});
const manifesto = JSON.parse(readFileSync(path.join(raiz, "data/episodes/mec-fechadura-pt/clipes-manifesto.json"), "utf8"));
const so = new Set(ids);
const planos = manifesto.filter((p) => so.size === 0 || so.has(p.asset_id));
const log = path.join(saidaDir, "log-render.jsonl");

const serveUrl = await bundle({entryPoint: path.resolve("src/previews/mec-fechadura-pt/index.tsx")});
for (const p of planos) {
  const final = path.join(saidaDir, `${p.asset_id}.mp4`);
  if (existsSync(final) && statSync(final).size > 0) {
    console.log(JSON.stringify({pulado: p.asset_id}));
    continue;
  }
  const segura = p.segura_ultimo_quadro > 0;
  const bruto = segura ? path.join(saidaDir, `.${p.asset_id}.bruto.mp4`) : final;
  const t0 = Date.now();
  let erro = null;
  try {
    const composition = await selectComposition({serveUrl, id: p.composicao, inputProps: {}});
    await renderMedia({
      composition, serveUrl, inputProps: {}, outputLocation: bruto, codec: "h264", scale: 1.5, muted: true, concurrency: 4,
      logLevel: "error", frameRange: [p.quadro_inicial, p.quadro_final_exclusivo - 1],
    });
    if (segura) {
      const r = spawnSync("ffmpeg", ["-v", "error", "-y", "-i", bruto, "-vf", `tpad=stop_mode=clone:stop=${p.segura_ultimo_quadro}`,
        "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", "-an", final], {encoding: "utf8"});
      if (r.status !== 0) throw new Error(`ffmpeg tpad: ${r.stderr}`);
      unlinkSync(bruto);
    }
  } catch (e) {
    erro = String(e).slice(0, 400);
  }
  const linha = {asset_id: p.asset_id, ok: erro === null, segundos: Math.round((Date.now() - t0) / 100) / 10, quadros: p.quadros_do_plano, erro};
  appendFileSync(log, JSON.stringify(linha) + "\n");
  console.log(JSON.stringify(linha));
}
