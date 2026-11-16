// Linha do tempo das cenas S12 e S13 do mec-fechadura-pt (vista de frente): frame → estado do desenho. Função pura.
// Durações da voz final (tempos-frente.json, conferido por check.mjs). Dentro de cada cena, os instantes são frações da duração
// (estimativa pela posição das palavras); o tempo exato por palavra só sai do `vp render`.
import {GIRO, SHEAR_Y, KEY_PIN_LEN, CX, CY, girar} from './vistaFrente.ts';
import {FPS, pulso, rampa} from './linhaDoTempo.ts';

export const ORDEM_FRENTE = ['S12', 'S13'] as const;
export type CenaFrenteId = (typeof ORDEM_FRENTE)[number];
export const DURACOES_FRENTE: Record<CenaFrenteId, number> = {S12: 9.0, S13: 7.04};

const FRAMES = {S12: Math.round(DURACOES_FRENTE.S12 * FPS), S13: Math.round(DURACOES_FRENTE.S13 * FPS)};
export const INICIO_FRENTE = {S12: 0, S13: FRAMES.S12} as const;
export const TOTAL_FRENTE = FRAMES.S12 + FRAMES.S13;

export type Camera = {scale: number; cx: number; cy: number};
export type EstadoFrente = {
  cena: CenaFrenteId;
  brilho: number; // brilho da linha livre na vista lateral (0..1)
  giroCamera: number; // 0 = só a vista lateral, 1 = só a de frente
  lateralScaleX: number;
  frenteScaleX: number;
  angulo: number; // giro do rotor com a chave, em graus
  setaGiro: number;
  rotulos: {carcaca: number; rotor: number; linha: number; chave: number; pinoChave: number; superior: number; mola: number};
  pulsos: {pinoChave: number; superior: number; mola: number; camara: number};
  camera: Camera;
};

const lerp = (a: number, b: number, t: number) => a + (b - a) * t;
const PLENO: Camera = {scale: 1, cx: CX, cy: CY};
/** Pino de chave já girado (ponto médio dele, na posição final do rotor) e a pilha das 12 horas. */
const [KX, KY] = girar(CX, SHEAR_Y + KEY_PIN_LEN / 2, GIRO);
export const FOCO_PINO_CHAVE: Camera = {scale: 1.35, cx: KX, cy: KY};
export const FOCO_PILHA: Camera = {scale: 1.35, cx: CX, cy: CY - 205};
const entre = (a: Camera, b: Camera, t: number): Camera => ({scale: lerp(a.scale, b.scale, t), cx: lerp(a.cx, b.cx, t), cy: lerp(a.cy, b.cy, t)});

export function estadoFrenteEm(frame: number): EstadoFrente {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_FRENTE) throw new RangeError(`frame fora de 0..${TOTAL_FRENTE - 1}: ${frame}`);
  const f = frame;
  const cena: CenaFrenteId = f < INICIO_FRENTE.S13 ? 'S12' : 'S13';
  const a12 = (fracao: number) => INICIO_FRENTE.S12 + Math.round(FRAMES.S12 * fracao);
  const a13 = (fracao: number) => INICIO_FRENTE.S13 + Math.round(FRAMES.S13 * fracao);

  // S12: brilho na linha livre → giro de câmera de 90° (a vista lateral fecha, a de frente abre) → o rotor gira com a chave.
  const giroCamera = rampa(f, 36, 84);
  const giroRotor = rampa(f, a12(0.7), a12(0.7) + 60);
  const virada = a12(0.7) + 60; // depois dela o rotor está girado; a chave sai de cena
  // Na S13 a câmera chega perto e cortaria os rótulos laterais: eles saem no começo do zoom; Carcaça, Rotor e Pino de chave voltam quando a câmera recua.
  const saiZoom = rampa(f, a13(0), a13(0.08));
  const volta = (fracao: number) => rampa(f, a13(fracao), a13(fracao) + 14);
  const rotulos = {
    carcaca: Math.max(rampa(f, 90, 104) * (1 - saiZoom), volta(0.8)),
    rotor: Math.max(rampa(f, 98, 112) * (1 - saiZoom), volta(0.86)),
    linha: rampa(f, 108, 122) * (1 - saiZoom),
    chave: rampa(f, 118, 132) * (1 - rampa(f, a12(0.7) - 6, a12(0.7) + 6)),
    pinoChave: Math.max(rampa(f, a13(0.22), a13(0.22) + 14) * (1 - rampa(f, a13(0.36), a13(0.36) + 20)), volta(0.88)),
    superior: rampa(f, a13(0.5), a13(0.5) + 14),
    mola: rampa(f, a13(0.62), a13(0.62) + 14),
  };

  // S13: a câmera vai do pino de chave (dentro do rotor) à pilha das 12 horas e recua no fim, com os três rótulos à vista.
  let camera = PLENO;
  if (f >= INICIO_FRENTE.S13) {
    const entra = rampa(f, a13(0), a13(0.1));
    const percorre = rampa(f, a13(0.36), a13(0.36) + 40);
    const recua = rampa(f, a13(0.86), a13(0.98));
    camera = entre(entre(entre(PLENO, FOCO_PINO_CHAVE, entra), FOCO_PILHA, percorre), PLENO, recua);
  }

  return {
    cena,
    brilho: pulso(f, 4, 40),
    giroCamera,
    lateralScaleX: Math.cos((Math.PI / 2) * giroCamera),
    frenteScaleX: Math.sin((Math.PI / 2) * giroCamera),
    angulo: GIRO * giroRotor,
    setaGiro: rampa(f, a12(0.66), a12(0.66) + 16) * (1 - rampa(f, virada + 6, virada + 24)),
    rotulos,
    pulsos: {
      pinoChave: pulso(f, a13(0.22), 40),
      superior: pulso(f, a13(0.5), 36),
      mola: pulso(f, a13(0.62), 36),
      camara: pulso(f, a13(0.84), 30),
    },
    camera,
  };
}
