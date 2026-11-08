// Geometria do traço do quadro de teste (src/quadro/tinta.ts). Sem rede e sem navegador.
// Rodar: `npm test` em video/ (Node 22.18+).
import assert from "node:assert/strict";
import {test} from "node:test";
import {
  contornoDeTraco, curva, elipse, encadeia, fecha, larguraNoTrecho, pontosAte, poligono, reta, retangulo, ruido, tremer,
} from "../src/quadro/tinta.ts";

const contagem = (texto: string, trecho: string) => texto.split(trecho).length - 1;

test("ruído é determinístico e fica em [0, 1)", () => {
  for (let i = 0; i < 200; i++) {
    const v = ruido(7, i);
    assert.ok(v >= 0 && v < 1, `fora de [0,1): ${v}`);
    assert.equal(v, ruido(7, i));
  }
});

test("o traço afina nas pontas e fica cheio no meio", () => {
  const meio = larguraNoTrecho(0.5, 10);
  assert.ok(larguraNoTrecho(0, 10) > 0, "a ponta não pode sumir");
  assert.ok(larguraNoTrecho(0, 10) < meio, "a ponta é mais fina que o meio");
  assert.ok(Math.abs(meio - 10) < 1e-9, `o meio é a largura base: ${meio}`);
});

test("curva e reta começam e terminam nos pontos pedidos", () => {
  const c = curva([0, 0], [50, 100], [100, 0], 10);
  assert.deepEqual(c[0], [0, 0]);
  assert.deepEqual(c[9], [100, 0]);
  const r = reta([1, 2], [5, 6], 3);
  assert.deepEqual(r[0], [1, 2]);
  assert.deepEqual(r[2], [5, 6]);
});

test("elipse tem n pontos e o primeiro está no ponto à direita do centro", () => {
  const e = elipse(10, 20, 30, 40, 16);
  assert.equal(e.length, 16);
  assert.deepEqual(e[0], [40, 20]);
});

test("pontosAte: nada no início, tudo no fim, metade no meio", () => {
  const base = elipse(0, 0, 10, 10, 40);
  assert.equal(pontosAte(base, 0).length, 0);
  assert.equal(pontosAte(base, 1).length, 40);
  const meio = pontosAte(base, 0.5);
  assert.ok(meio.length >= 19 && meio.length <= 21, `metade de 40 pontos: ${meio.length}`);
});

test("tremor com amplitude 0 não mexe nos pontos; com amplitude > 0 mexe", () => {
  const base = elipse(0, 0, 10, 10, 12);
  assert.deepEqual(tremer(base, 0, 3), base);
  const mexido = tremer(base, 2, 3);
  const deslocados = mexido.filter((p, i) => p[0] !== base[i][0] || p[1] !== base[i][1]);
  assert.ok(deslocados.length > 0);
  for (let i = 0; i < base.length; i++) {
    assert.ok(Math.abs(mexido[i][0] - base[i][0]) <= 2 && Math.abs(mexido[i][1] - base[i][1]) <= 2);
  }
});

test("contorno aberto é um polígono; fechado são dois anéis", () => {
  const aberto = contornoDeTraco(reta([0, 0], [100, 0], 12), 8);
  assert.ok(aberto.startsWith("M "));
  assert.equal(contagem(aberto, "Z"), 1);
  const fechado = contornoDeTraco(elipse(0, 0, 50, 50, 24), 8, true);
  assert.equal(contagem(fechado, "Z"), 2);
});

test("com menos de dois pontos não há contorno nem polígono", () => {
  assert.equal(contornoDeTraco([[0, 0]], 8), "");
  assert.equal(poligono([[0, 0]]), "");
});

test("retângulo e encadeia: os cantos estão na polilinha e a emenda não repete o ponto", () => {
  const r = retangulo(0, 0, 100, 60, 50);
  assert.ok(r.some(([x, y]) => x === 0 && y === 0));
  assert.ok(r.some(([x, y]) => x === 100 && y === 60));
  const junto = encadeia(reta([0, 0], [10, 0]), reta([10, 0], [10, 10]));
  assert.equal(junto.length, 3);
  assert.deepEqual(fecha([[0, 0], [5, 0], [0, 0]]), [[0, 0], [5, 0]]);
});
