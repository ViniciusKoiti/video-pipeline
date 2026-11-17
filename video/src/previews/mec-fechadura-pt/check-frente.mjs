import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {CX, CY, DRIVER_LEN, GIRO, KEYWAY, KEY_PIN_LEN, PIN_HALF, R_HOUSING, R_PLUG, SHEAR_Y, WELL_HALF, WELL_TOP, HOLE_HALF, girar, pilha} from './vistaFrente.ts';
import {DURACOES_FRENTE, INICIO_FRENTE, TOTAL_FRENTE, estadoFrenteEm} from './linhaDoTempoFrente.ts';
import {FPS} from './linhaDoTempo.ts';

// Geometria: a linha de corte é a borda do rotor; com a chave certa, topo do pino de chave e fundo do pino superior ficam nela (F16).
assert.equal(SHEAR_Y, CY - R_PLUG);
const p = pilha();
assert.equal(p.keyPinTop, SHEAR_Y);
assert.equal(p.driverBottom, SHEAR_Y);
assert.equal(p.keyPinBottom, KEYWAY.top, 'o fundo do pino de chave assenta no topo da lâmina (fundo do corte)');
assert.equal(p.keyPinBottom - p.keyPinTop, KEY_PIN_LEN);
assert.equal(p.driverBottom - p.driverTop, DRIVER_LEN);
assert.ok(p.springLength > 10, 'a mola precisa de comprimento visível');
assert.ok(WELL_TOP > CY - R_HOUSING + 15, 'a câmara não pode furar a carcaça por cima');
assert.ok(PIN_HALF < HOLE_HALF && HOLE_HALF < WELL_HALF, 'pino cabe no furo e a câmara é a mais larga');
assert.ok(CY + R_HOUSING < 700, 'a carcaça cabe acima do rodapé do quadro');
// Giro: o pino de chave (topo, 12 h) vai para as 3 h; a pilha da carcaça não gira.
const [gx, gy] = girar(CX, SHEAR_Y + KEY_PIN_LEN / 2, GIRO);
assert.ok(Math.abs(gx - (CX + (CY - SHEAR_Y - KEY_PIN_LEN / 2))) < 1e-9 && Math.abs(gy - CY) < 1e-9, 'pino de chave deve ir às 3 h com 90°');
const [ox, oy] = girar(CX, CY, 123);
assert.ok(Math.abs(ox - CX) < 1e-9 && Math.abs(oy - CY) < 1e-9, 'o centro não se move no giro');

// Tempos = voz.
const tempos = JSON.parse(readFileSync(new URL('./tempos-frente.json', import.meta.url), 'utf8'));
for (const [id, s] of Object.entries(tempos.cenas)) assert.equal(DURACOES_FRENTE[id], s, `duração de ${id} difere da voz`);
assert.equal(tempos.fps, FPS);
assert.equal(INICIO_FRENTE.S13, Math.round(DURACOES_FRENTE.S12 * FPS));
assert.equal(TOTAL_FRENTE, Math.round(DURACOES_FRENTE.S12 * FPS) + Math.round(DURACOES_FRENTE.S13 * FPS));
assert.throws(() => estadoFrenteEm(TOTAL_FRENTE), RangeError);
assert.throws(() => estadoFrenteEm(-1), RangeError);

// Em todos os frames: valores em 0..1, giro só cresce e só começa com a vista de frente inteira, câmera sai do pleno só na S13.
let ultimoAngulo = -1;
let ultimoGiro = -1;
for (let f = 0; f < TOTAL_FRENTE; f++) {
  const e = estadoFrenteEm(f);
  const zeroUm = [e.brilho, e.giroCamera, e.lateralScaleX, e.frenteScaleX, e.setaGiro, ...Object.values(e.rotulos), ...Object.values(e.pulsos)];
  for (const v of zeroUm) assert.ok(Number.isFinite(v) && v >= -1e-9 && v <= 1 + 1e-9, `valor fora de 0..1 no frame ${f}`);
  assert.ok(e.angulo >= ultimoAngulo - 1e-9 && e.angulo <= GIRO + 1e-9, `ângulo fora de ordem no frame ${f}`);
  assert.ok(e.giroCamera >= ultimoGiro - 1e-9, `câmera girou de volta no frame ${f}`);
  if (e.angulo > 0) assert.ok(e.giroCamera > 0.999, `rotor girou antes de a vista de frente abrir (frame ${f})`);
  assert.ok(e.camera.scale >= 1 - 1e-9 && e.camera.scale <= 1.35 + 1e-9, `escala de câmera fora do previsto no frame ${f}`);
  if (f < INICIO_FRENTE.S13) assert.deepEqual(e.camera, {scale: 1, cx: CX, cy: CY}, `a câmera só se move na S13 (frame ${f})`);
  // Nunca as duas vistas inteiras ao mesmo tempo: enquanto uma fecha, a outra abre.
  assert.ok(Math.abs(e.lateralScaleX ** 2 + e.frenteScaleX ** 2 - 1) < 1e-9, `vistas fora de fase no frame ${f}`);
  ultimoAngulo = e.angulo;
  ultimoGiro = e.giroCamera;
}

const inicio = estadoFrenteEm(0);
assert.equal(inicio.lateralScaleX, 1);
assert.equal(inicio.frenteScaleX, 0);
assert.equal(inicio.angulo, 0);
const fimS12 = estadoFrenteEm(INICIO_FRENTE.S13 - 1);
assert.ok(Math.abs(fimS12.angulo - GIRO) < 1e-6, 'ao fim da S12 o rotor está girado');
assert.ok(fimS12.rotulos.carcaca > 0.99 && fimS12.rotulos.rotor > 0.99 && fimS12.rotulos.linha > 0.99);
assert.equal(fimS12.rotulos.chave, 0, 'o rótulo "Chave" sai antes de o rotor girar');
const ultimo = estadoFrenteEm(TOTAL_FRENTE - 1);
assert.ok(Math.abs(ultimo.angulo - GIRO) < 1e-6);
assert.ok(ultimo.rotulos.pinoChave > 0.99 && ultimo.rotulos.superior > 0.99 && ultimo.rotulos.mola > 0.99, 'no fim da S13 os três rótulos estão à vista');
assert.ok(Math.abs(ultimo.camera.scale - 1) < 0.02, 'a câmera recua no fim, com tudo à vista');
// Os rótulos entram na ordem da fala da S13: pino de chave, pino superior, mola.
const quando = (nome) => { for (let f = INICIO_FRENTE.S13; f < TOTAL_FRENTE; f++) if (estadoFrenteEm(f).rotulos[nome] > 0.5) return f; return Infinity; };
assert.ok(quando('pinoChave') < quando('superior') && quando('superior') < quando('mola'), 'rótulos fora da ordem da fala');

console.log(`vista de frente: ${TOTAL_FRENTE} frames (${(TOTAL_FRENTE / FPS).toFixed(2)} s) = S12 + S13 da voz; giro de ${GIRO}° só depois da vista abrir; rótulos na ordem da fala; todos os valores em 0..1.`);
