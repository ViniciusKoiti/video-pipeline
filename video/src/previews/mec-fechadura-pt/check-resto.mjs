import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {BLADE_BOTTOM, BLADE_TOP, CHAMBER_TOP, HOUSING, SHEAR, Y_REST, columnsAt, plugFree} from './geometria.ts';
import {ALAVANCA, BLOCO} from './linhaDoTempoCadeado.ts';
import {FPS} from './linhaDoTempo.ts';
import {
  ANCORAS_MS, COLUNA, DESLOCAMENTO_S25, DURACOES, FUNDOS_ALTA, GIRO_PORTA, TOTAL_S01, TOTAL_S03A, TOTAL_S18A, TOTAL_S19, TOTAL_S20,
  TOTAL_S02, CORTE_S02, TRACOS_S02, TOTAL_S21A, TOTAL_S22, TOTAL_S23, TOTAL_S24A, TOTAL_S24B, TOTAL_S25, TRINCO_RECUO,
  estadoS01, estadoS02, estadoS03A, estadoS18A, estadoS19, estadoS20, estadoS21A, estadoS22, estadoS23, estadoS24A, estadoS24B, estadoS25,
} from './linhaDoTempoResto.ts';

const faixa01 = (nome, valores, f) => { for (const v of valores) assert.ok(Number.isFinite(v) && v >= -1e-9 && v <= 1 + 1e-9, `${nome}: valor fora de 0..1 no frame ${f}`); };

// Tempos = voz.
const tempos = JSON.parse(readFileSync(new URL('./tempos-resto.json', import.meta.url), 'utf8'));
for (const [id, s] of Object.entries(tempos.cenas)) assert.equal(DURACOES[id], s, `duração de ${id} difere da voz`);
assert.equal(tempos.fps, FPS);
for (const [id, ms] of Object.entries(tempos.ancoras_ms)) assert.equal(ANCORAS_MS[id], ms, `âncora de ${id} difere do arquivo de tempos`);
assert.equal(TOTAL_S19, Math.round(DURACOES.S19 * FPS));
assert.equal(TOTAL_S20, Math.round(DURACOES.S20 * FPS));
assert.equal(TOTAL_S01, Math.round(DURACOES.S01 * FPS));
assert.throws(() => estadoS19(TOTAL_S19), RangeError);
assert.throws(() => estadoS20(-1), RangeError);
assert.throws(() => estadoS01(TOTAL_S01), RangeError);

// ---- S02 (V2.0 e V2.0b): contorno em traço, depois o corte revela a vista em corte ----
assert.equal(TOTAL_S02, Math.round(DURACOES.S02 * FPS));
assert.equal(CORTE_S02.x0, HOUSING.x0);
assert.equal(CORTE_S02.x1, HOUSING.x1);
for (const t of Object.values(TRACOS_S02)) assert.ok(t.at >= 0 && t.at + t.dur <= TOTAL_S02, 'traço do contorno passa do fim da cena');
let corteAnt = -1;
let primeiroCorte = Infinity;
for (let f = 0; f < TOTAL_S02; f++) {
  const e = estadoS02(f);
  faixa01('S02', [e.corte, e.linha], f);
  assert.ok(e.corte >= corteAnt - 1e-9, `o corte recuou no frame ${f}`);
  if (e.corte > 0 && primeiroCorte === Infinity) primeiroCorte = f;
  if (e.corte > 0) assert.ok(f >= TRACOS_S02.corpo.at + TRACOS_S02.corpo.dur, `corte antes de o contorno terminar, frame ${f}`);
  if (e.linha > 0.01) assert.ok(e.corte > 0 || f >= Math.round(TOTAL_S02 * 0.6), `linha de corte fora de hora, frame ${f}`);
  corteAnt = e.corte;
}
assert.ok(estadoS02(0).corte === 0 && estadoS02(TOTAL_S02 - 1).corte === 1 && estadoS02(TOTAL_S02 - 1).linha === 0, 'termina com a vista em corte inteira e sem a linha');
assert.ok(primeiroCorte > Math.round(TOTAL_S02 * 0.6) - 1, 'o corte começa em "a gente corta uma ao meio" (62% da fala)');

// ---- S03, 1.ª parte: tudo desenhado em repouso, sem chave, sem rótulos, sem linha de corte ----
for (let f = 0; f < TOTAL_S03A; f += 7) {
  const e = estadoS03A(f);
  assert.equal(e.insert, 0);
  assert.equal(e.tipPx, -40);
  assert.ok(Object.values(e.rotulos).every((v) => v === 0), 'a S03 não leva rótulos');
}
assert.ok(columnsAt(0).every((c) => c.driverStraddles), 'em repouso o pino superior atravessa a linha em todas as colunas');

// ---- S18, 1.ª parte: cortes rasos demais; as colunas 3 e 5 passam da linha; rotor bloqueado; a tela não destaca qual trava ----
assert.equal(FUNDOS_ALTA.length, 5);
for (const y of FUNDOS_ALTA) assert.ok(y > BLADE_TOP && y < BLADE_BOTTOM && y <= Y_REST, `corte fora da lâmina: ${y}`);
const alta = columnsAt(1, FUNDOS_ALTA);
assert.ok(alta[2].keyPinCrosses && alta[4].keyPinCrosses, 'as colunas 3 e 5 passam da linha');
assert.ok(alta.filter((c) => !c.keyPinCrosses).every((c) => Math.abs(c.keyPinTop - SHEAR) < 0.01), 'as outras colunas ficam alinhadas');
assert.ok(!alta.every((c) => Math.abs(c.keyPinTop - SHEAR) < 0.01), 'o rotor não está livre');
for (let k = 0; k <= 200; k++) for (const c of columnsAt(k / 200, FUNDOS_ALTA)) assert.ok(c.driverTop >= CHAMBER_TOP && c.springLength > 0, `pino fora da câmara em ${k / 200}`);
for (let f = 0; f < TOTAL_S18A; f++) {
  const {estado, alerta} = estadoS18A(f);
  assert.ok(alerta.every((v) => v === 0), 'a tela não destaca qual pino trava');
  assert.ok(estado.pulsos.juncoes.every((v) => v === 0));
  faixa01('S18A', [estado.insert, estado.setaGiro, estado.setaGiroCortada, ...Object.values(estado.rotulos)], f);
}
assert.ok(estadoS18A(TOTAL_S18A - 1).estado.setaGiroCortada > 0.99);

// ---- S20: a chave sai e as molas devolvem os pinos superiores aos furos do rotor ----
assert.ok(columnsAt(1).every((c) => Math.abs(c.keyPinTop - SHEAR) < 0.01) && plugFree(1), 'no começo a chave certa está dentro e o rotor está livre');
let insertAnt = 2;
let pontaAnt = Infinity;
for (let f = 0; f < TOTAL_S20; f++) {
  const e = estadoS20(f);
  faixa01('S20', [e.insert, e.setaForca, ...e.pulsos.furos, ...e.pulsos.superiores, ...Object.values(e.rotulos)], f);
  assert.ok(e.insert <= insertAnt + 1e-9 && e.tipPx <= pontaAnt + 1e-9, `a chave voltou no frame ${f}`);
  if (e.setaForca > 0.01) assert.ok(e.insert < 0.02, `setas de força antes de a chave sair, frame ${f}`);
  insertAnt = e.insert;
  pontaAnt = e.tipPx;
}
const fim20 = estadoS20(TOTAL_S20 - 1);
assert.equal(fim20.insert, 0);
assert.equal(fim20.tipPx, -40);
assert.ok(columnsAt(0).every((c) => c.driverStraddles), 'ao fim os pinos superiores voltam a atravessar a linha');

// ---- S19: segundo pino entra; chave alta demais trava; altura certa libera ----
assert.equal(COLUNA.fundoCerto - COLUNA.keyPin, COLUNA.shear, 'com o corte certo o topo do pino de chave fica na linha');
const topoRaso = COLUNA.fundoRaso - COLUNA.keyPin;
assert.ok(topoRaso < COLUNA.shear - 20, 'com o corte raso o pino de chave passa da linha');
assert.ok(topoRaso - COLUNA.driver - COLUNA.chamberTop > 20, 'a mola mantém comprimento com o corte raso');
let primeiroSobe = Infinity;
let driverCheio = Infinity;
for (let f = 0; f < TOTAL_S19; f++) {
  const e = estadoS19(f);
  faixa01('S19', [e.driver, e.seta, e.setaCortada, e.juncao, e.rotulo], f);
  assert.ok(e.fundo >= COLUNA.fundoRaso - 1e-9 && e.fundo <= COLUNA.fundoCerto + 1e-9);
  if (e.fundo < COLUNA.fundoCerto - 0.01 && primeiroSobe === Infinity) primeiroSobe = f;
  if (e.driver > 0.999 && driverCheio === Infinity) driverCheio = f;
  if (e.setaCortada > 0.01) assert.ok(e.fundo < COLUNA.fundoCerto - 0.2, `"X" sobre a seta sem a chave alta, frame ${f}`);
}
assert.ok(driverCheio <= primeiroSobe, 'o segundo pino entra antes de a chave subir demais');
assert.equal(estadoS19(TOTAL_S19 - 1).fundo, COLUNA.fundoCerto, 'ao fim a chave volta à altura certa');
assert.ok(estadoS19(0).driver === 0);

// ---- Porta: A gira e o trinco recolhe; B entra, balança até 7° e para ----
const verPorta = (nome, total, estado, intro) => {
  for (let f = 0; f < total; f++) {
    const e = estado(f);
    faixa01(nome, [e.aparece, e.chavesVisiveis, e.chaves.A.prox, e.chaves.B.prox], f);
    for (const id of ['A', 'B']) if (e.chaves[id].giro !== 0) assert.ok(e.chaves[id].prox > 0.99, `a chave ${id} girou fora da fechadura, frame ${f}`);
    assert.ok(e.tranca >= 0 && e.tranca <= TRINCO_RECUO + 1e-9);
    if (e.tranca > 0) assert.ok(e.chaves.A.giro > 0, `o trinco recuou sem a chave certa girar, frame ${f}`);
    assert.ok(Math.abs(e.chaves.B.giro) <= 7 + 1e-9, 'a chave errada só balança');
    assert.ok(e.chaves.A.giro >= 0 && e.chaves.A.giro <= GIRO_PORTA + 1e-9);
    assert.ok(!(e.chaves.A.prox > 0.01 && e.chaves.B.prox > 0.01), `as duas chaves na fechadura ao mesmo tempo, frame ${f}`);
  }
  if (intro) assert.equal(estado(0).aparece, 0);
};
verPorta('S01', TOTAL_S01, estadoS01, true);
verPorta('S24A', TOTAL_S24A, estadoS24A, false);
const fim01 = estadoS01(TOTAL_S01 - 1);
assert.ok(fim01.chaves.A.prox === 0 && fim01.chaves.B.prox === 0 && fim01.tranca === 0 && fim01.chavesVisiveis > 0.99, 'a S01 termina com as duas chaves lado a lado e a porta trancada');
const fim24 = estadoS24A(TOTAL_S24A - 1);
assert.ok(fim24.chaves.A.prox > 0.99 && fim24.chaves.A.giro > GIRO_PORTA - 1e-6 && Math.abs(fim24.tranca - TRINCO_RECUO) < 1e-6 && fim24.chaves.B.prox === 0, 'a reprise termina com a chave certa girada e o trinco recolhido');
let viuB = false;
for (let f = 0; f < TOTAL_S24A; f++) { const e = estadoS24A(f); if (e.chaves.B.prox > 0.99) viuB = true; if (e.chaves.A.prox > 0.01) assert.ok(viuB, 'na reprise a errada entra antes da certa'); }

// ---- S21, V2.16: vista em corte em repouso com a chave em destaque ----
assert.equal(TOTAL_S21A, Math.round((ANCORAS_MS.S21 * FPS) / 1000));
let dest = -1;
for (let f = 0; f < TOTAL_S21A; f++) {
  const {estado, destaque} = estadoS21A(f);
  faixa01('S21A', [destaque, estado.grupos.colunas, estado.grupos.molas, estado.grupos.superiores, estado.grupos.chavePinos, ...Object.values(estado.rotulos)], f);
  assert.ok(Object.values(estado.rotulos).every((v) => v === 0), 'a V2.16 não leva rótulos');
  assert.ok(plugFree(estado.insert) && columnsAt(estado.insert).every((c) => Math.abs(c.keyPinTop - SHEAR) < 0.01), 'a chave está inteira e o rotor livre');
  if (f > 0) assert.ok(destaque >= dest - 0.3, `o destaque oscilou demais no frame ${f}`);
  dest = destaque;
}
const fim21 = estadoS21A(TOTAL_S21A - 1);
assert.ok(fim21.destaque > 0.7 && fim21.estado.grupos.colunas < 0.4, 'ao fim a chave está em destaque e o resto esmaecido');
assert.equal(estadoS21A(0).destaque, 0);

// ---- S22: tubular e dimple ----
assert.equal(TOTAL_S22, Math.round(DURACOES.S22 * FPS));
let rotTub = Infinity;
let rotDim = Infinity;
for (let f = 0; f < TOTAL_S22; f++) {
  const e = estadoS22(f);
  faixa01('S22', Object.values(e), f);
  if (e.rotuloTubular > 0.5 && rotTub === Infinity) rotTub = f;
  if (e.rotuloDimple > 0.5 && rotDim === Infinity) rotDim = f;
  if (e.chaveTubular > 0.01) assert.ok(e.abre > 0.99, `chave tubular antes de o painel abrir, frame ${f}`);
  if (e.pinosDimple > 0.01) assert.ok(e.chaveDimple > 0.99, `pinos da dimple antes da chave, frame ${f}`);
  if (e.abre > 0.01) assert.ok(e.encolhe > 0.5, `painéis abrindo antes de a vista principal encolher, frame ${f}`);
}
assert.ok(rotTub < rotDim, 'a tubular vem antes da dimple, como na fala');
assert.ok(estadoS22(0).encolhe === 0 && estadoS22(TOTAL_S22 - 1).pinosDimple > 0.99 && estadoS22(TOTAL_S22 - 1).rotuloDimple > 0.99);

// ---- S23: espaçador e duas chaves ----
assert.equal(TOTAL_S23, Math.round(DURACOES.S23 * FPS));
assert.equal(COLUNA.fundoB - COLUNA.keyPin - COLUNA.espacador, COLUNA.shear, 'com a 2.ª chave a junção espaçador/pino superior fica na linha');
let menorMola = Infinity;
let linha2Em = Infinity;
let espacoEm = Infinity;
let trocaEm = Infinity;
for (let f = 0; f < TOTAL_S23; f++) {
  const e = estadoS23(f);
  faixa01('S23', [e.driver, e.seta, e.setaCortada, e.juncao, e.rotulo, e.espaco, e.linha2, e.rotuloEsp], f);
  const pinoTop = e.fundo - COLUNA.keyPin;
  const espTop = pinoTop - COLUNA.espacador * e.espaco;
  menorMola = Math.min(menorMola, espTop - COLUNA.driver - COLUNA.chamberTop);
  if (e.juncao > 0.5) assert.ok(Math.abs(pinoTop - COLUNA.shear) < 1 || Math.abs(espTop - COLUNA.shear) < 1, `pulso de junção com a coluna desalinhada, frame ${f}`);
  if (e.espaco > 0.5 && espacoEm === Infinity) espacoEm = f;
  if (e.linha2 > 0.5 && linha2Em === Infinity) linha2Em = f;
  if (e.fundo > COLUNA.fundoCerto + 1 && trocaEm === Infinity) trocaEm = f;
}
assert.ok(menorMola > 20, `a mola some em algum ponto da S23 (${menorMola})`);
assert.ok(espacoEm < linha2Em && linha2Em < trocaEm, 'ordem: espaçador, segunda linha, troca de chave');
assert.ok(Math.abs(estadoS23(TOTAL_S23 - 1).fundo - COLUNA.fundoB) < 1e-6);

// ---- S24, 2.ª parte (V2.17) ----
assert.equal(ALAVANCA.pivoX + ALAVANCA.comprimento, BLOCO.x0);
let ang = -1;
for (let f = 0; f < TOTAL_S24B; f++) {
  const e = estadoS24B(f);
  faixa01('S24B', [e.aparece, e.setaChave, e.contato, ...Object.values(e.rotulos)], f);
  assert.ok(e.angulo >= ang - 1e-9 && e.angulo <= 90 + 1e-9);
  if (e.contato > 0.01) assert.ok(e.angulo > 87, `bloco aceso antes de a alavanca tocá-lo, frame ${f}`);
  if (e.angulo > 0) assert.ok(e.aparece > 0.99);
  ang = e.angulo;
}
const f24 = estadoS24B(TOTAL_S24B - 1);
assert.ok(Math.abs(f24.angulo - 90) < 1e-6 && f24.contato > 0.5 && f24.rotulos.came > 0.99 && f24.rotulos.bloco > 0.99 && f24.lateralScaleX === 1);

// ---- S25: vista explodida ----
assert.equal(TOTAL_S25, Math.round(DURACOES.S25 * FPS));
const noInicio = estadoS25(0).explosao;
for (const g of Object.keys(DESLOCAMENTO_S25)) assert.ok(noInicio[g].dx === 0 && noInicio[g].dy === 0, `a explosão começa com as peças no lugar (${g})`);
for (let f = 0; f < TOTAL_S25; f += 5) {
  const {estado, explosao} = estadoS25(f);
  assert.equal(estado.tipPx, -600, 'a chave fica fora do quadro, mesmo com a redução');
  for (const g of Object.keys(DESLOCAMENTO_S25)) {
    assert.ok(Math.abs(explosao[g].dx) <= Math.abs(DESLOCAMENTO_S25[g].dx) + 10 && Math.abs(explosao[g].dy) <= Math.abs(DESLOCAMENTO_S25[g].dy) + 10, `peça ${g} passou do deslocamento previsto`);
  }
}
const fimS25 = estadoS25(TOTAL_S25 - 1).explosao;
// Com a redução de 0,72 em torno de (640, 395), tudo cabe no quadro de 1280×720 em qualquer instante.
const ESC = 0.72;
const ancorar = (y) => 395 + (y - 395) * ESC;
for (let f = 0; f < TOTAL_S25; f++) {
  const x = estadoS25(f).explosao;
  assert.ok(ancorar(HOUSING.top + x.topo.dy - 4) >= 0 && ancorar(CHAMBER_TOP + x.molas.dy - 4) >= 0, `peça de cima fora do quadro, frame ${f}`);
  assert.ok(ancorar(HOUSING.bottomEnd + x.base.dy + 4) <= 720, `peça de baixo fora do quadro, frame ${f}`);
}
assert.ok(fimS25.base.dy > 150 && fimS25.topo.dy < -100, 'ao fim as peças estão afastadas');

console.log(`resto: S01 porta (${TOTAL_S01} frames), S03 colunas (${TOTAL_S03A}), S18 corte alto (${TOTAL_S18A}), S19 (${TOTAL_S19}), S20 (${TOTAL_S20}), S21 V2.16 (${TOTAL_S21A}), S22 (${TOTAL_S22}), S23 (${TOTAL_S23}), S24 porta (${TOTAL_S24A}) e V2.17 (${TOTAL_S24B}), S25 (${TOTAL_S25}); geometria coerente com F16; tempos = voz; valores em 0..1.`);
