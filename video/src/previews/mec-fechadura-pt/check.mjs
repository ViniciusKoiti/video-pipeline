import assert from 'node:assert/strict';
import {
  BLADE_LEN, BLADE_TOP, BLADE_BOTTOM, CHAMBER_TOP, COLUMNS, DRIVER, HOUSING, KEYWAY, KEY_PIN, PIN_HALF, SHEAR, TIP_IN, TIP_OUT, Y_REST,
  bladeProfile, columnsAt, cutBottom, plugFree, tipX,
} from './geometria.ts';

// Chave certa inteira: o topo de cada pino de chave (a junção com o pino superior) fica exatamente na linha de corte (F16).
const full = columnsAt(1);
for (const c of full) {
  assert.ok(Math.abs(c.keyPinTop - SHEAR) < 0.01, 'junção fora da linha de corte');
  assert.ok(Math.abs(c.driverBottom - SHEAR) < 0.01);
  assert.ok(!c.driverStraddles && !c.keyPinCrosses);
  assert.ok(c.springLength > 0);
}
assert.ok(plugFree(1), 'rotor deveria estar livre com a chave inteira');

// Sem chave: o pino superior atravessa a linha em todas as colunas, e nenhum pino de chave passa dela (rotor travado).
const none = columnsAt(0);
for (const c of none) {
  assert.ok(c.driverStraddles, 'sem chave o pino superior tem de atravessar a linha');
  assert.ok(!c.keyPinCrosses);
  assert.equal(c.keyPinBottom, Y_REST);
}
assert.ok(!plugFree(0));

// Cinco colunas, pinos de chave todos de comprimento diferente (para o desenho ser legível), cortes mais fundos = pinos mais longos.
assert.equal(COLUMNS.length, 5);
assert.equal(new Set(KEY_PIN).size, KEY_PIN.length);
for (let i = 0; i < 5; i++) assert.equal(cutBottom(i), SHEAR + KEY_PIN[i]);

// Em qualquer ponto da inserção: sem NaN, pinos dentro da câmara e do furo, mola com comprimento positivo.
for (let k = 0; k <= 100; k++) {
  const insert = k / 100;
  for (const c of columnsAt(insert)) {
    for (const v of Object.values(c)) if (typeof v === 'number') assert.ok(Number.isFinite(v), `valor não finito em ${insert}`);
    assert.ok(c.keyPinBottom <= Y_REST + 0.01);
    assert.ok(c.driverTop >= CHAMBER_TOP, `pino superior passou do teto da câmara em ${insert}`);
    assert.ok(c.springLength > 0, `mola sem comprimento em ${insert}`);
  }
}

// Perfil da lâmina: d estritamente crescente, topo sempre dentro do canal da chave, lâmina cabe no canal.
const profile = bladeProfile();
for (let k = 1; k < profile.length; k++) assert.ok(profile[k][0] > profile[k - 1][0], 'perfil fora de ordem');
for (const [, y] of profile) assert.ok(y >= KEYWAY.top && y <= BLADE_BOTTOM, 'topo da lâmina fora do canal');
assert.ok(BLADE_BOTTOM <= KEYWAY.bottom && BLADE_TOP >= KEYWAY.top);
assert.equal(tipX(0), TIP_OUT);
assert.equal(tipX(1), TIP_IN);
assert.equal(TIP_IN - BLADE_LEN, HOUSING.x0, 'o ombro da chave tem de ficar na face do rotor com a chave inteira');

// Tudo cabe no quadro e na carcaça.
for (const x of COLUMNS) assert.ok(x - 20 > HOUSING.x0 && x + 20 < HOUSING.x1 && PIN_HALF < 20);
assert.ok(DRIVER > 0 && CHAMBER_TOP > HOUSING.top && SHEAR - DRIVER > CHAMBER_TOP);

console.log('5 colunas; junção na linha de corte com a chave inteira (F16); sem chave o pino superior atravessa a linha; 101 passos de inserção finitos; perfil e canal da chave coerentes.');

// ---- Linha do tempo S04–S11 (linhaDoTempo.ts) ----
import {readFileSync} from 'node:fs';
import {CENAS, DURACOES, FPS, TOTAL, estadoEm, inicio, duracao} from './linhaDoTempo.ts';

const tempos = JSON.parse(readFileSync(new URL('./tempos.json', import.meta.url), 'utf8'));
for (const [id, segundos] of Object.entries(tempos.cenas)) assert.equal(DURACOES[id], segundos, `duração de ${id} difere da voz`);
assert.equal(FPS, tempos.fps);
for (let k = 1; k < CENAS.length; k++) assert.equal(CENAS[k].from, CENAS[k - 1].from + CENAS[k - 1].frames, 'cenas não contíguas');
assert.equal(TOTAL, CENAS.reduce((soma, c) => soma + c.frames, 0));
assert.throws(() => estadoEm(TOTAL), RangeError);
assert.throws(() => estadoEm(-1), RangeError);

// Início: sem chave no quadro, sem rótulos. Fim da S09: rotor travado, chave ainda no canal. Fim da S11: tudo alinhado.
const inicial = estadoEm(0);
assert.equal(inicial.tipPx, -40);
assert.equal(inicial.insert, 0);
assert.equal(inicial.rotulos.linha, 0);
const fimS09 = estadoEm(inicio('S10') - 1);
assert.equal(fimS09.insert, 0);
assert.equal(fimS09.tipPx, 300);
assert.ok(columnsAt(fimS09.insert).every((c) => c.driverStraddles), 'fim da S09: sem chave, os pinos superiores atravessam a linha');
assert.ok(fimS09.rotulos.linha > 0.99, 'a linha de corte tem de estar rotulada ao fim da S09');
const ultimo = estadoEm(TOTAL - 1);
assert.ok(ultimo.insert > 0.9999 && plugFree(ultimo.insert), 'fim da S11: rotor livre');
assert.ok(Math.abs(ultimo.tipPx - TIP_IN) < 0.1);
assert.ok(estadoEm(inicio('S07')).tipPx === 300 && estadoEm(inicio('S09')).tipPx === 300, 'chave parada no canal da S07 à S09');
assert.equal(estadoEm(inicio('S07')).rotulos.pinoChave, 0);
assert.equal(estadoEm(inicio('S07') - 1).rotulos.pinoChave, 0);

// Em todos os frames: valores finitos, opacidades e pulsos entre 0 e 1, a chave só avança, pinos dentro da câmara.
let ultimoInsert = -1;
let ultimaPonta = -Infinity;
for (let f = 0; f < TOTAL; f++) {
  const e = estadoEm(f);
  const faixa = [...Object.values(e.grupos), ...Object.values(e.rotulos), e.linhaBrilho, e.setaGiro, e.setaGiroCortada, e.setaForca,
    ...e.pulsos.furos, ...e.pulsos.chavePinos, ...e.pulsos.superiores, ...e.pulsos.juncoes];
  for (const v of faixa) assert.ok(Number.isFinite(v) && v >= -1e-9 && v <= 1 + 1e-9, `valor fora de 0..1 no frame ${f}`);
  assert.ok(e.insert >= ultimoInsert - 1e-9, `chave recuou no frame ${f}`);
  assert.ok(e.tipPx >= ultimaPonta - 1e-9, `ponta da chave recuou no frame ${f}`);
  ultimoInsert = e.insert;
  ultimaPonta = e.tipPx;
  for (const c of columnsAt(e.insert)) assert.ok(c.driverTop >= CHAMBER_TOP && c.springLength > 0, `pino passou do teto da câmara no frame ${f}`);
}
// Cada cena dura o que a voz dura (a S10 termina com a chave inteira antes da S11).
assert.ok(estadoEm(inicio('S11')).insert > 0.9999, 'a chave tem de estar inteira quando a S11 começa');
assert.ok(duracao('S10') / FPS === DURACOES.S10 || Math.abs(duracao('S10') / FPS - DURACOES.S10) < 0.02);
console.log(`linha do tempo: ${CENAS.length} cenas, ${TOTAL} frames (${(TOTAL / FPS).toFixed(2)} s) = soma da voz; chave parada de S07 a S09; rotor travado ao fim da S09 e livre ao fim da S11; todos os valores em 0..1.`);
