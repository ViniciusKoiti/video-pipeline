import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {
  BODY, CAM, FREE_AT, GIRO, LATCH_DY, LATCH_H, LATCH_Y_DOWN, LATCH_Y_UP, LEG_L, LEG_R, NOTCH_DEPTH, R_MAX, SHACKLE_RISE, X_INNER, X_WALL,
  camBorda, espelho, penetracao, retracao, trincoCima,
} from './cadeado.ts';
import {
  ALAVANCA, BLOCO, DURACOES_CADEADO, INICIO_CADEADO, TOTAL_CADEADO, TOTAL_CAME, estadoCadeadoEm, estadoCameEm,
} from './linhaDoTempoCadeado.ts';
import {FPS} from './linhaDoTempo.ts';

// ---- Cinemática do came e dos trincos (S15–S16) ----
assert.equal(retracao(0), 0, 'com o came em repouso os trincos não recuam');
let anterior = -1;
for (let phi = 0; phi <= GIRO + 1e-9; phi += 0.5) {
  const r = retracao(phi);
  assert.ok(Number.isFinite(r) && r >= 0 && r <= R_MAX, `retração fora de 0..${R_MAX} em ${phi}°: ${r}`);
  // Tolerância de 0,5 px: perto do repouso o canto da cunha roça a reta do came (profundidades de ~0,3 px, o limiar do solver).
  assert.ok(r >= anterior - 0.5, `a retração diminuiu em ${phi}° (${r} < ${anterior})`);
  if (phi > 30) assert.ok(r >= anterior - 0.05, `a retração diminuiu em ${phi}° depois do contato (${r} < ${anterior})`);
  assert.ok(penetracao(phi, r) <= 0.31, `braço penetra o came em ${phi}°`);
  if (r > 1) assert.ok(penetracao(phi, r - 1) > 0.3, `o braço não encosta no came em ${phi}° (folga)`);
  const minY = Math.min(...camBorda(phi).map(([, y]) => y));
  assert.ok(minY > LATCH_DY + LATCH_H / 2 - 3, `o came encosta no trinco em ${phi}°`);
  assert.ok(X_WALL - (X_INNER + r) >= 20, `mola do trinco sem comprimento em ${phi}°`);
  anterior = r;
}
const rFinal = retracao(GIRO);
assert.ok(rFinal >= FREE_AT + 10 && rFinal <= R_MAX, `retração final ${rFinal} não solta a haste com folga`);

// Geometria: a ponta do trinco encaixa no entalhe em repouso e sai dele quando retraído; o de baixo é o de cima espelhado.
const repouso = trincoCima(0);
assert.equal(repouso[0][0], LEG_L.x1 - NOTCH_DEPTH, 'a ponta fica no fundo do entalhe');
assert.ok(trincoCima(rFinal)[0][0] >= LEG_L.x1 + 2, 'com o came girado a ponta sai do entalhe');
assert.equal(LATCH_Y_DOWN, 2 * CAM.y - LATCH_Y_UP);
assert.deepEqual(espelho(...espelho(123, 456)), [123, 456]);
assert.equal(espelho(LEG_L.x0, 0)[0], LEG_R.x1, 'as pernas da haste são simétricas em x');
assert.equal(espelho(LEG_L.x1, 0)[0], LEG_R.x0);
for (const [x, y] of [...repouso, ...trincoCima(rFinal)]) assert.ok(x > BODY.x0 && x < BODY.x1 && y > BODY.y0 && y < BODY.y1, 'trinco fora do corpo');
assert.ok(LEG_R.bottom > LATCH_Y_DOWN + 20, 'a perna curta alcança o entalhe de baixo');
assert.ok(LEG_L.bottom > LATCH_Y_UP + 20, 'a perna comprida alcança o entalhe de cima');
assert.ok(LEG_L.bottom > LEG_R.bottom, 'a mola fica sob a ponta mais longa');
assert.ok(BODY.y1 - 5 - (LEG_L.bottom - SHACKLE_RISE) > BODY.y1 - 5 - LEG_L.bottom, 'a mola da haste expande');

// ---- Tempos = voz ----
const tempos = JSON.parse(readFileSync(new URL('./tempos-cadeado.json', import.meta.url), 'utf8'));
for (const [id, s] of Object.entries(tempos.cenas)) assert.equal(DURACOES_CADEADO[id], s, `duração de ${id} difere da voz`);
assert.equal(tempos.fps, FPS);
assert.equal(TOTAL_CAME, Math.round(DURACOES_CADEADO.S14 * FPS));
assert.equal(INICIO_CADEADO.S16, Math.round(DURACOES_CADEADO.S15 * FPS));
assert.equal(TOTAL_CADEADO, Math.round(DURACOES_CADEADO.S15 * FPS) + Math.round(DURACOES_CADEADO.S16 * FPS));
assert.throws(() => estadoCameEm(TOTAL_CAME), RangeError);
assert.throws(() => estadoCadeadoEm(TOTAL_CADEADO), RangeError);
assert.throws(() => estadoCadeadoEm(-1), RangeError);

// ---- S14: came e bloco ----
assert.equal(ALAVANCA.pivoX + ALAVANCA.comprimento, BLOCO.x0, 'a ponta da alavanca a 90° toca a face do bloco');
assert.ok(BLOCO.y0 < ALAVANCA.pivoY && ALAVANCA.pivoY < BLOCO.y1);
let angulo = -1;
for (let f = 0; f < TOTAL_CAME; f++) {
  const e = estadoCameEm(f);
  const faixa = [e.voltaFrente, e.lateralScaleX, e.frenteScaleX, e.aparece, e.setaChave, e.contato, ...Object.values(e.rotulos)];
  for (const v of faixa) assert.ok(Number.isFinite(v) && v >= -1e-9 && v <= 1 + 1e-9, `valor fora de 0..1 na S14, frame ${f}`);
  assert.ok(e.angulo >= angulo - 1e-9 && e.angulo <= GIRO + 1e-9, `ângulo da alavanca fora de ordem, frame ${f}`);
  assert.ok(Math.abs(e.lateralScaleX ** 2 + e.frenteScaleX ** 2 - 1) < 1e-9, `vistas fora de fase na S14, frame ${f}`);
  if (e.contato > 0.01) assert.ok(e.angulo > GIRO - 3, `bloco aceso antes de a alavanca tocá-lo, frame ${f}`);
  if (e.angulo > 0) assert.ok(e.aparece > 0.99, `alavanca girou antes de aparecer, frame ${f}`);
  angulo = e.angulo;
}
assert.equal(estadoCameEm(0).frenteScaleX, 1);
const fimCame = estadoCameEm(TOTAL_CAME - 1);
assert.ok(Math.abs(fimCame.angulo - GIRO) < 1e-6 && fimCame.contato > 0.5 && fimCame.rotulos.came > 0.99 && fimCame.rotulos.bloco > 0.99 && fimCame.rotulos.aciona > 0.99);

// ---- S15–S16: cadeado ----
let phiAnt = -1;
let rAnt = -1;
for (let f = 0; f < TOTAL_CADEADO; f++) {
  const e = estadoCadeadoEm(f);
  const faixa = [e.encolhe, ...Object.values(e.rotulos), ...Object.values(e.pulsos)];
  for (const v of faixa) assert.ok(Number.isFinite(v) && v >= -1e-9 && v <= 1 + 1e-9, `valor fora de 0..1 no cadeado, frame ${f}`);
  assert.ok(e.phi >= phiAnt - 1e-9 && e.phi <= GIRO + 1e-9, `giro do came fora de ordem, frame ${f}`);
  assert.ok(e.retracao >= rAnt - 0.05, `trincos avançaram de volta, frame ${f}`);
  assert.ok(e.haste >= -1e-9 && e.haste <= SHACKLE_RISE + 1e-9, `haste fora de curso, frame ${f}`);
  if (e.haste > 0) assert.ok(e.retracao >= FREE_AT, `a haste subiu com os trincos ainda nos entalhes, frame ${f}`);
  if (e.cena === 'S15') assert.ok(e.phi === 0 && e.haste === 0 && e.retracao === 0, `o cadeado se mexeu na S15, frame ${f}`);
  phiAnt = e.phi;
  rAnt = e.retracao;
}
const inicio = estadoCadeadoEm(0);
assert.equal(inicio.encolhe, 0);
assert.ok(estadoCadeadoEm(INICIO_CADEADO.S16 - 1).encolhe > 0.99);
// Os rótulos da S15 entram na ordem da fala: No cadeado, Came, Trincos, Mola, Entalhes, Haste.
const quando = (nome) => { for (let f = 0; f < TOTAL_CADEADO; f++) if (estadoCadeadoEm(f).rotulos[nome] > 0.5) return f; return Infinity; };
const ordem = ['titulo', 'came', 'trincos', 'mola', 'entalhes', 'haste'].map(quando);
assert.ok(ordem.every((t, k) => t < Infinity && (k === 0 || t > ordem[k - 1])), `rótulos fora da ordem da fala: ${ordem}`);
const ultimo = estadoCadeadoEm(TOTAL_CADEADO - 1);
assert.ok(Math.abs(ultimo.phi - GIRO) < 1e-6 && Math.abs(ultimo.haste - SHACKLE_RISE) < 1e-6, 'ao fim da S16 o rotor girou e a haste saiu');
assert.ok(ultimo.rotulos.molaHaste > 0.99 && ultimo.rotulos.came > 0.99 && ultimo.rotulos.haste > 0.99);
// A haste só sobe depois de o came terminar de soltar os trincos.
let fimGiro = 0;
let inicioSubida = Infinity;
for (let f = INICIO_CADEADO.S16; f < TOTAL_CADEADO; f++) {
  const e = estadoCadeadoEm(f);
  if (e.phi < GIRO - 1e-6) fimGiro = f;
  if (e.haste > 0 && inicioSubida === Infinity) inicioSubida = f;
}
assert.ok(inicioSubida > fimGiro - 40, 'a haste sobe cedo demais em relação ao giro do came');

console.log(`cadeado: retração de 0 a ${rFinal.toFixed(1)} px com o came de 0° a ${GIRO}°, braço sempre encostado e nunca dentro do came; ponta sai do entalhe; haste só sobe com os trincos soltos; ${TOTAL_CAME} frames na S14 e ${TOTAL_CADEADO} na S15 + S16, iguais à voz; rótulos na ordem da fala.`);
