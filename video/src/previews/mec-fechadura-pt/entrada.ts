// Entrada de uma chave na vista lateral (S17 e a 1.ª parte da S18): chega à entrada do canal, desliza até estar inteira, a seta do rotor aparece
// cortada. Função pura; as frações são da duração do clipe (`total` frames), estimadas pela posição das palavras.
import {tipX} from './geometria.ts';
import {pulso, rampa} from './linhaDoTempo.ts';
import type {Estado} from './linhaDoTempo.ts';

export type OpcoesEntrada = {
  alerta: boolean; // contorno vermelho nos pinos que cruzam a linha (a tela destaca quais; só na S17)
  juncoes: boolean; // pulsos brancos nas cinco colunas, ao fim (a ideia "cada pilha precisa estar alinhada")
};

export type EstadoEntrada = {estado: Estado; alerta: number[]};

export function estadoEntrada(frame: number, total: number, opc: OpcoesEntrada): EstadoEntrada {
  if (!Number.isInteger(frame) || frame < 0 || frame >= total) throw new RangeError(`frame fora de 0..${total - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(total * fracao);
  const cinco = (fn: (i: number) => number) => [0, 1, 2, 3, 4].map(fn);

  const entra = rampa(f, a(0.08), a(0.22));
  const insert = rampa(f, a(0.22), a(0.48));
  const tipPx = f < a(0.22) ? -40 + 340 * entra : tipX(insert);
  const estado: Estado = {
    cena: 'S11', insert, tipPx,
    grupos: {colunas: 1, molas: 1, superiores: 1, chavePinos: 1},
    rotulos: {carcaca: 0, rotor: 0, chave: 0, mola: 0, superior: 0, pinoChave: 0, linha: rampa(f, a(0.36), a(0.36) + 20)},
    linhaAt: 0, linhaBrilho: 0,
    setaGiro: rampa(f, a(0.55), a(0.55) + 18),
    setaGiroCortada: rampa(f, a(0.6), a(0.6) + 15),
    setaForca: 0,
    pulsos: {
      furos: cinco(() => 0), chavePinos: cinco(() => 0), superiores: cinco(() => 0),
      juncoes: cinco((i) => (opc.juncoes ? pulso(f, a(0.76) + 12 * i, 26) : 0)),
    },
  };
  // O contorno vermelho aparece só depois de a chave terminar de entrar (0,48).
  const alerta = cinco((i) => (opc.alerta ? rampa(f, a(0.49) + 8 * i, a(0.49) + 8 * i + 12) : 0));
  return {estado, alerta};
}
