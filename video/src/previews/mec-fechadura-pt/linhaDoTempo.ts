// Linha do tempo do corte principal (cenas S04 a S11 do mec-fechadura-pt): frame → estado do desenho.
// Função pura. As durações são as da voz final (tempos.json, conferido por check.mjs). Dentro de cada cena, os instantes
// são frações da duração da cena (estimativa pela posição das palavras); o tempo exato por palavra só sai do `vp render`.
import {tipX} from './geometria.ts';

export const FPS = 30;
export const ORDEM = ['S04', 'S05', 'S06', 'S07', 'S08', 'S09', 'S10', 'S11'] as const;
export type CenaId = (typeof ORDEM)[number];

// Segundos de voz por cena (voice/leveled/*.wav de 2026-11-09). check.mjs compara com tempos.json.
export const DURACOES: Record<CenaId, number> = {S04: 6.76, S05: 9.44, S06: 8.92, S07: 7.28, S08: 10.28, S09: 12.32, S10: 6.04, S11: 11.2};

export const CENAS = (() => {
  let from = 0;
  return ORDEM.map((id) => {
    const frames = Math.round(DURACOES[id] * FPS);
    const cena = {id, from, frames};
    from += frames;
    return cena;
  });
})();
export const TOTAL = CENAS[CENAS.length - 1].from + CENAS[CENAS.length - 1].frames;
export const inicio = (id: CenaId): number => CENAS.find((c) => c.id === id)!.from;
export const duracao = (id: CenaId): number => CENAS.find((c) => c.id === id)!.frames;

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const suave = (v: number) => {
  const t = clamp01(v);
  return t * t * (3 - 2 * t);
};
/** 0 antes de `a`, 1 depois de `b`, suave entre os dois. */
export const rampa = (frame: number, a: number, b: number): number => (b <= a ? (frame >= a ? 1 : 0) : suave((frame - a) / (b - a)));
/** Pulso 0 → 1 → 0 que começa em `a` e dura `dur` frames. */
export const pulso = (frame: number, a: number, dur: number): number => Math.sin(Math.PI * clamp01((frame - a) / dur));

/** Opacidade dos grupos que o espectador não precisa olhar naquele momento. */
export const DIM = 0.35;

export type Estado = {
  cena: CenaId;
  insert: number; // 0 (chave fora) … 1 (chave inteira): é o que move os pinos
  tipPx: number; // x da ponta da chave (0 = fora do quadro, à esquerda)
  grupos: {colunas: number; molas: number; superiores: number; chavePinos: number}; // opacidade de cada grupo (foco)
  rotulos: {carcaca: number; rotor: number; chave: number; mola: number; superior: number; pinoChave: number; linha: number};
  linhaAt: number; // frame em que a linha de corte começa a se desenhar
  linhaBrilho: number; // 0..1, brilho da linha livre (S11)
  setaGiro: number; // seta curva do rotor (S05 a S09), 0..1
  setaGiroCortada: number; // o "X" sobre ela (S09), 0..1
  setaForca: number; // setas de força das molas (S08), 0..1
  pulsos: {furos: number[]; chavePinos: number[]; superiores: number[]; juncoes: number[]};
};

const cinco = (fn: (i: number) => number) => [0, 1, 2, 3, 4].map(fn);

export function estadoEm(frame: number): Estado {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL) throw new RangeError(`frame fora de 0..${TOTAL - 1}: ${frame}`);
  const f = frame;
  const s = (id: CenaId) => inicio(id);
  const d = (id: CenaId) => duracao(id);
  const cena = CENAS.find((c) => f >= c.from && f < c.from + c.frames)!.id;
  const apos = (id: CenaId, fracao: number) => s(id) + Math.round(d(id) * fracao);

  // Chave: fora do quadro até a S06; entra até o canal e para; na S10 desliza até estar inteira (insert 0 → 1).
  const aproximar = rampa(f, s('S06') + 10, apos('S06', 0.5));
  const insert = rampa(f, s('S10') + 25, apos('S10', 0.78) + 25);
  const tipPx = f < s('S10') ? -40 + 340 * aproximar : tipX(insert); // começa além da borda (x = -40), sem traço no quadro

  // Foco: na S05 as colunas esmaecem para olhar a carcaça e o rotor; cada grupo volta na cena em que é explicado.
  const esmaece = rampa(f, s('S05'), s('S05') + 15);
  const volta = (id: CenaId) => rampa(f, s(id), s(id) + 12);
  const foco = (retorno: number) => 1 - (1 - DIM) * esmaece * (1 - retorno);
  const grupos = {
    colunas: foco(volta('S09')),
    molas: foco(Math.max(volta('S08'), volta('S09'))),
    superiores: foco(Math.max(volta('S08'), volta('S09'))),
    chavePinos: foco(Math.max(volta('S07'), volta('S09'))),
  };

  const rotulos = {
    carcaca: rampa(f, s('S05') + 10, s('S05') + 24),
    rotor: rampa(f, s('S05') + 18, s('S05') + 32),
    chave: rampa(f, s('S06') + 5, s('S06') + 20),
    pinoChave: rampa(f, s('S07') + 20, s('S07') + 34),
    superior: rampa(f, s('S08') + 20, s('S08') + 34),
    mola: rampa(f, s('S08') + 46, s('S08') + 60),
    linha: rampa(f, apos('S09', 0.12), apos('S09', 0.12) + 25),
  };

  const sai = rampa(f, s('S10'), s('S10') + 15);
  const setaGiro = rampa(f, apos('S05', 0.6), apos('S05', 0.6) + 30) * (1 - sai);
  const setaGiroCortada = rampa(f, apos('S09', 0.7), apos('S09', 0.7) + 15) * (1 - sai);
  const setaForca = rampa(f, apos('S08', 0.55), apos('S08', 0.55) + 20) * (1 - volta('S09'));

  const pulsos = {
    furos: cinco((i) => pulso(f, apos('S06', 0.5) + 12 * i, 26)),
    chavePinos: cinco((i) => pulso(f, s('S07') + 24 + 14 * i, 28)),
    superiores: cinco((i) => pulso(f, apos('S09', 0.45) + 10 * i, 22)),
    juncoes: cinco((i) => pulso(f, s('S11') + 20 + 22 * i, 26)),
  };

  return {
    cena, insert, tipPx, grupos, rotulos, linhaAt: apos('S09', 0.12), linhaBrilho: rampa(f, s('S11'), s('S11') + 20),
    setaGiro, setaGiroCortada, setaForca, pulsos,
  };
}
