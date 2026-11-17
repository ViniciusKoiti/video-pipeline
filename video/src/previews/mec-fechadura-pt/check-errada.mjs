import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {BLADE_BOTTOM, BLADE_TOP, CHAMBER_TOP, COLUMNS, SHEAR, TIP_IN, Y_REST, bladeProfile, columnsAt, plugFree, tipX} from './geometria.ts';
import {DURACAO_ERRADA, FUNDOS_ERRADA, TOTAL_ERRADA, estadoErradaEm} from './linhaDoTempoErrada.ts';
import {FPS} from './linhaDoTempo.ts';

// A chave errada tem cinco cortes, todos válidos para a lâmina (perfil crescente, dentro do canal) e diferentes dos da chave certa em quatro colunas.
assert.equal(FUNDOS_ERRADA.length, COLUMNS.length);
for (const y of FUNDOS_ERRADA) assert.ok(y > BLADE_TOP && y < BLADE_BOTTOM && y <= Y_REST, `corte fora da lâmina: ${y}`);
const perfil = bladeProfile(FUNDOS_ERRADA);
for (let k = 1; k < perfil.length; k++) assert.ok(perfil[k][0] > perfil[k - 1][0], 'perfil da chave errada fora de ordem');

// Com a chave errada inteira: a coluna 1 está alinhada, as outras não; ao menos um pino superior atravessa a linha e um pino de chave passa dela; o rotor não está livre.
const cheia = columnsAt(1, FUNDOS_ERRADA);
assert.ok(Math.abs(cheia[0].keyPinTop - SHEAR) < 0.01, 'a coluna 1 deveria estar alinhada');
assert.ok(cheia.slice(1).every((c) => Math.abs(c.keyPinTop - SHEAR) > 5), 'as outras colunas deveriam estar fora da linha');
assert.ok(cheia.some((c) => c.driverStraddles), 'ao menos um pino superior atravessa a linha');
assert.ok(cheia.some((c) => c.keyPinCrosses), 'ao menos um pino de chave passa da linha');
assert.ok(cheia.every((c) => c.driverStraddles || c.keyPinCrosses || Math.abs(c.keyPinTop - SHEAR) < 0.01));
assert.equal(plugFree(1) && cheia.every((c) => Math.abs(c.keyPinTop - SHEAR) < 0.01), false, 'o rotor não pode estar livre com a chave errada');
// Em qualquer ponto da inserção: finito, pino dentro da câmara, mola com comprimento.
for (let k = 0; k <= 200; k++) {
  for (const c of columnsAt(k / 200, FUNDOS_ERRADA)) {
    for (const v of Object.values(c)) if (typeof v === 'number') assert.ok(Number.isFinite(v));
    assert.ok(c.keyPinBottom <= Y_REST + 0.01 && c.driverTop >= CHAMBER_TOP && c.springLength > 0, `pino fora da câmara em ${k / 200}`);
  }
}

// Tempo = voz.
const tempos = JSON.parse(readFileSync(new URL('./tempos-errada.json', import.meta.url), 'utf8'));
assert.equal(tempos.cenas.S17, DURACAO_ERRADA);
assert.equal(tempos.fps, FPS);
assert.equal(TOTAL_ERRADA, Math.round(DURACAO_ERRADA * FPS));
assert.throws(() => estadoErradaEm(TOTAL_ERRADA), RangeError);
assert.throws(() => estadoErradaEm(-1), RangeError);

let insertAnt = -1;
let pontaAnt = -Infinity;
for (let f = 0; f < TOTAL_ERRADA; f++) {
  const {estado: e, alerta} = estadoErradaEm(f);
  const faixa = [e.insert, e.linhaBrilho, e.setaGiro, e.setaGiroCortada, ...Object.values(e.rotulos), ...Object.values(e.grupos), ...e.pulsos.juncoes, ...alerta];
  for (const v of faixa) assert.ok(Number.isFinite(v) && v >= -1e-9 && v <= 1 + 1e-9, `valor fora de 0..1 no frame ${f}`);
  assert.ok(e.insert >= insertAnt - 1e-9 && e.tipPx >= pontaAnt - 1e-9, `a chave recuou no frame ${f}`);
  if (alerta.some((v) => v > 0.01)) assert.ok(e.insert > 0.999, `alerta antes de a chave entrar, frame ${f}`);
  if (e.setaGiroCortada > 0.01) assert.ok(e.insert > 0.999 && e.setaGiro > 0.99, `seta cortada antes de a chave entrar, frame ${f}`);
  insertAnt = e.insert;
  pontaAnt = e.tipPx;
}
const inicio = estadoErradaEm(0).estado;
assert.equal(inicio.tipPx, -40);
assert.equal(inicio.insert, 0);
const fim = estadoErradaEm(TOTAL_ERRADA - 1);
assert.ok(Math.abs(fim.estado.tipPx - TIP_IN) < 0.1 && fim.estado.setaGiroCortada > 0.99 && fim.estado.rotulos.linha > 0.99);
assert.ok(fim.alerta.every((v) => v > 0.99));
assert.ok(tipX(1) === TIP_IN);

console.log(`chave errada: coluna 1 alinhada e as outras não; ${cheia.filter((c) => c.driverStraddles).length} pino(s) superior(es) atravessam a linha e ${cheia.filter((c) => c.keyPinCrosses).length} pino(s) de chave passam dela; ${TOTAL_ERRADA} frames (${(TOTAL_ERRADA / FPS).toFixed(2)} s) = S17 da voz; valores em 0..1.`);
