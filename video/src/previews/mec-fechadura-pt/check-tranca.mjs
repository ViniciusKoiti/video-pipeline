import assert from 'node:assert/strict';
import {
  ANCORA_S03_MS, ANCORA_S18_MS, BOLT, CHANNEL, DURACAO_S03, DURACAO_S18, FLOOR_HOLE_HALF, HOLE_XS, LIFT_FULL, LIFT_START, OPENING_HALF, PEG_HALF, PEG_LEN, PIN_CLEAR_BOTTOM,
  PIN_HALF, PIN_LEN, PIN_REST_BOTTOM, POST, SHAFT, SLIDE_MAX, TIP_REST, TOTAL_TRANCA_S03, TOTAL_TRANCA_S18, TRACOS_S03,
  estadoTrancaS03, estadoTrancaS18, pegTip, pinBottom, pinTop, trancaLivre,
} from './tranca.ts';
import {FPS} from './linhaDoTempo.ts';

// Peças: pino cabe na abertura e no poço; peg cabe no furo e o furo é mais estreito que o pino (o pino repousa na borda).
assert.ok(PEG_HALF < FLOOR_HOLE_HALF && FLOOR_HOLE_HALF < PIN_HALF && PIN_HALF < OPENING_HALF && PIN_HALF < SHAFT.half);
for (const x of HOLE_XS) {
  assert.ok(x - OPENING_HALF > BOLT.x0 && x + OPENING_HALF < BOLT.x1, 'abertura fora da tranca');
  assert.ok(x - SHAFT.half > POST.x0 && x + SHAFT.half < POST.x1, 'poço fora do poste');
}
assert.ok(BOLT.x1 <= POST.x1 && BOLT.y0 > CHANNEL.y0 && BOLT.y1 < CHANNEL.y1, 'a tranca cabe no canal');
assert.equal(PIN_REST_BOTTOM, CHANNEL.y1);

// Presa: com a chave fora, cada pino atravessa a altura da tranca (a prende). Solta: acima de LIFT_FULL o pino sai da altura da tranca.
assert.ok(pinTop(0) < BOLT.y0 && pinBottom(0) > BOLT.y0, 'em repouso o pino ocupa a abertura da tranca');
assert.ok(!trancaLivre(0) && !trancaLivre(LIFT_FULL - 1) && trancaLivre(LIFT_FULL), 'a tranca só corre a partir da altura certa');
assert.equal(LIFT_FULL, TIP_REST - PIN_CLEAR_BOTTOM);
assert.ok(pinBottom(LIFT_FULL) <= BOLT.y0 && pinTop(LIFT_FULL) >= SHAFT.top, 'o pino levantado cabe no poço e deixa a tranca livre');
assert.equal(PIN_LEN, pinBottom(LIFT_FULL) - pinTop(LIFT_FULL));
// A chave nunca entra no poste: a barra fica abaixo dele, os pegs sobem pelos furos.
for (let L = LIFT_START; L <= LIFT_FULL; L++) assert.ok(pegTip(L) + PEG_LEN >= POST.y1 + 30, `a barra da chave encosta no poste com L = ${L}`);

// Linhas do tempo.
assert.equal(TOTAL_TRANCA_S03, Math.round(((DURACAO_S03 * 1000 - ANCORA_S03_MS) * FPS) / 1000));
assert.equal(TOTAL_TRANCA_S18, Math.round(((DURACAO_S18 * 1000 - ANCORA_S18_MS) * FPS) / 1000));
assert.throws(() => estadoTrancaS03(TOTAL_TRANCA_S03), RangeError);
assert.throws(() => estadoTrancaS18(-1), RangeError);
for (const t of [TRACOS_S03.poste, TRACOS_S03.canal, TRACOS_S03.tranca, ...TRACOS_S03.pinos]) assert.ok(t.at >= 0 && t.at + t.dur <= TOTAL_TRANCA_S03, 'traço passa do fim do clipe');

const zeroUm = (e) => [e.chaveVisivel, ...Object.values(e.rotulos)];
let ultimoRotulo = {};
for (let f = 0; f < TOTAL_TRANCA_S03; f++) {
  const e = estadoTrancaS03(f);
  for (const v of zeroUm(e)) assert.ok(Number.isFinite(v) && v >= -1e-9 && v <= 1 + 1e-9, `valor fora de 0..1 na S03, frame ${f}`);
  assert.equal(e.chaveVisivel, 0, 'a chave não aparece na S03');
  assert.equal(e.slide, 0, 'a tranca não corre na S03');
  ultimoRotulo = e.rotulos;
}
assert.ok(ultimoRotulo.poste > 0.99 && ultimoRotulo.tranca > 0.99 && ultimoRotulo.pinos > 0.99 && ultimoRotulo.chave === 0 && ultimoRotulo.naoConfere === 0);
const primeiro = (nome) => { for (let f = 0; f < TOTAL_TRANCA_S03; f++) if (estadoTrancaS03(f).rotulos[nome] > 0.5) return f; return Infinity; };
assert.ok(primeiro('poste') < primeiro('tranca') && primeiro('tranca') < primeiro('pinos'), 'rótulos da S03 fora da ordem');

let Lant = -Infinity;
let slideAnt = -1;
let comecouRotulo = Infinity;
for (let f = 0; f < TOTAL_TRANCA_S18; f++) {
  const e = estadoTrancaS18(f);
  for (const v of zeroUm(e)) assert.ok(Number.isFinite(v) && v >= -1e-9 && v <= 1 + 1e-9, `valor fora de 0..1 na S18, frame ${f}`);
  assert.ok(e.chave >= Lant - 1e-9 && e.chave <= LIFT_FULL + 1e-9, `a chave passou da altura certa ou recuou, frame ${f}`);
  assert.ok(e.slide >= slideAnt - 1e-9 && e.slide <= SLIDE_MAX + 1e-9, `recuo da tranca fora de ordem, frame ${f}`);
  if (e.slide > 0) assert.ok(trancaLivre(e.chave), `a tranca correu com um pino ainda nela, frame ${f}`);
  if (e.rotulos.naoConfere > 0.01 && comecouRotulo === Infinity) comecouRotulo = f;
  Lant = e.chave;
  slideAnt = e.slide;
}
const fim = estadoTrancaS18(TOTAL_TRANCA_S18 - 1);
assert.ok(Math.abs(fim.chave - LIFT_FULL) < 1e-9 && Math.abs(fim.slide - SLIDE_MAX) < 1e-9 && fim.rotulos.naoConfere > 0.99 && fim.rotulos.chave > 0.99);
// O rótulo "não confere se sobe demais" aparece depois de a tranca se soltar; a chave nunca passa da altura certa (nenhum excesso é mostrado).
let inicioSlide = Infinity;
for (let f = 0; f < TOTAL_TRANCA_S18; f++) if (estadoTrancaS18(f).slide > 0) { inicioSlide = f; break; }
assert.ok(comecouRotulo >= inicioSlide, 'o rótulo aparece antes de a tranca se soltar');

console.log(`tranca egípcia: pino ocupa a abertura em repouso e sai com subida de ${LIFT_FULL} px (a chave para aí, sem excesso); tranca só corre com os três pinos fora; ${TOTAL_TRANCA_S03} frames na S03 e ${TOTAL_TRANCA_S18} na S18 (estimativa pela âncora); valores em 0..1.`);
