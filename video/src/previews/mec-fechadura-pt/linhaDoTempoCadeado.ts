// Linhas do tempo das cenas S14 (came e bloco da trava, vista lateral) e S15–S16 (cadeado em corte) do mec-fechadura-pt. Funções puras.
// Durações da voz final (tempos-cadeado.json, conferido por check-cadeado.mjs). Dentro de cada cena, os instantes são frações da duração
// (estimativa pela posição das palavras); o tempo exato por palavra só sai do `vp render`.
import {FREE_AT, GIRO, SHACKLE_RISE, retracao} from './cadeado.ts';
import {FPS, pulso, rampa} from './linhaDoTempo.ts';

export const DURACOES_CADEADO = {S14: 7.4, S15: 10.72, S16: 10.24} as const;
const frames = (s: keyof typeof DURACOES_CADEADO) => Math.round(DURACOES_CADEADO[s] * FPS);
export const TOTAL_CAME = frames('S14');
export const INICIO_CADEADO = {S15: 0, S16: frames('S15')} as const;
export const TOTAL_CADEADO = frames('S15') + frames('S16');

/** Alavanca do came na vista lateral (S14): pivô no fim do eixo do rotor, repouso para cima, gira 90° (horário) até tocar o bloco. */
export const ALAVANCA = {pivoX: 1035, pivoY: 440, comprimento: 80, largura: 20} as const;
export const BLOCO = {x0: 1115, y0: 385, x1: 1255, y1: 495} as const; // "Mecanismo da trava": caixa-preta; a ponta da alavanca toca a face x0

export type EstadoCame = {
  voltaFrente: number; // 0..1: a vista de frente (S13) fecha e a lateral abre
  lateralScaleX: number;
  frenteScaleX: number;
  aparece: number; // eixo, alavanca e bloco entram
  angulo: number; // giro da alavanca e da chave, graus
  setaChave: number; // seta curva na argola da chave
  contato: number; // brilho do bloco quando a alavanca o toca
  rotulos: {came: number; bloco: number; aciona: number};
};

export function estadoCameEm(frame: number): EstadoCame {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_CAME) throw new RangeError(`frame fora de 0..${TOTAL_CAME - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(TOTAL_CAME * fracao);
  const volta = rampa(f, 0, 28);
  const gira = rampa(f, a(0.42), a(0.42) + 60);
  return {
    voltaFrente: volta,
    lateralScaleX: Math.sin((Math.PI / 2) * volta),
    frenteScaleX: Math.cos((Math.PI / 2) * volta),
    aparece: rampa(f, 36, 60),
    angulo: GIRO * gira,
    setaChave: rampa(f, a(0.4), a(0.4) + 14),
    contato: rampa(f, a(0.42) + 56, a(0.42) + 62) * (0.6 + 0.4 * pulso(f, a(0.42) + 62, 40)),
    rotulos: {came: rampa(f, 52, 66), bloco: rampa(f, 74, 88), aciona: rampa(f, a(0.7), a(0.7) + 14)},
  };
}

export type EstadoCadeado = {
  cena: 'S15' | 'S16';
  encolhe: number; // 0..1: a vista da fechadura (fim da S14) encolhe para um canto
  phi: number; // giro do rotor e do came, graus
  retracao: number; // quanto os trincos recuaram, px
  haste: number; // quanto a haste subiu, px
  rotulos: {titulo: number; came: number; trincos: number; mola: number; entalhes: number; haste: number; molaHaste: number};
  pulsos: {trincos: number; molas: number; entalhes: number; molaHaste: number};
};

export function estadoCadeadoEm(frame: number): EstadoCadeado {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_CADEADO) throw new RangeError(`frame fora de 0..${TOTAL_CADEADO - 1}: ${frame}`);
  const f = frame;
  const cena = f < INICIO_CADEADO.S16 ? 'S15' : 'S16';
  const a15 = (fracao: number) => INICIO_CADEADO.S15 + Math.round(frames('S15') * fracao);
  const a16 = (fracao: number) => INICIO_CADEADO.S16 + Math.round(frames('S16') * fracao);

  // S16: o came gira 90° (a chave gira o rotor), os trincos recuam contra a mola; só com as pontas fora dos entalhes a mola sobe a haste.
  const phi = GIRO * rampa(f, a16(0.08), a16(0.5));
  const r = retracao(phi);
  const livre = r >= FREE_AT; // as pontas já saíram dos entalhes
  const subida = rampa(f, a16(0.62), a16(0.9));
  const haste = livre ? SHACKLE_RISE * subida : 0;

  // Na S16 os rótulos dos trincos e da mola do trinco saem (a cena fala do came e da mola da haste); a "Mola" da haste entra.
  const saiS15 = rampa(f, a16(0.05), a16(0.12));
  return {
    cena,
    encolhe: rampa(f, a15(0.02), a15(0.2)),
    phi,
    retracao: r,
    haste,
    rotulos: {
      titulo: rampa(f, a15(0.2), a15(0.3)) * (1 - saiS15),
      came: rampa(f, a15(0.3), a15(0.4)),
      trincos: rampa(f, a15(0.44), a15(0.52)) * (1 - saiS15),
      mola: rampa(f, a15(0.58), a15(0.66)) * (1 - saiS15),
      entalhes: rampa(f, a15(0.72), a15(0.8)) * (1 - saiS15),
      haste: rampa(f, a15(0.88), a15(0.95)),
      molaHaste: rampa(f, a16(0.56), a16(0.64)),
    },
    pulsos: {
      trincos: pulso(f, a15(0.44), 34),
      molas: pulso(f, a15(0.58), 34),
      entalhes: pulso(f, a15(0.72), 34),
      molaHaste: pulso(f, a16(0.6), 40),
    },
  };
}
