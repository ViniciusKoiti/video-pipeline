// Tranca egípcia de madeira (S03 e S18 do mec-fechadura-pt), em corte lateral: geometria e linhas do tempo. Funções puras, px de 1280×720.
// Fontes: source-01#E5 (poste fixo na porta, tranca horizontal que corre nele, aberturas verticais com pinos que a prendem, chave os levanta até uma
// altura suficiente para a tranca correr) e source-02#E12/E13 (os pinos só precisam subir o bastante; nada confere se sobem demais).
// A chave é um "pente" de pegs que sobe por baixo, por furos do poste; valores e forma são ilustrativos.
import {FPS, rampa} from './linhaDoTempo.ts';

export const POST = {x0: 420, y0: 150, x1: 860, y1: 560} as const;
export const CHANNEL = {y0: 340, y1: 404} as const; // canal por onde corre a tranca
export const BOLT = {x0: 160, x1: 800, y0: 342, y1: 402} as const; // tranca em repouso (presa)
export const HOLE_XS = [520, 640, 760] as const; // posição dos pinos e das aberturas
export const OPENING_HALF = 20; // meia largura de cada abertura vertical da tranca
export const SHAFT = {half: 17, top: 200} as const; // poços dos pinos no poste, acima do canal
export const FLOOR_HOLE_HALF = 8; // furos do poste por onde sobem os pegs da chave
export const PIN_HALF = 14;
export const PIN_LEN = 128;
export const PIN_REST_BOTTOM = CHANNEL.y1; // os pinos repousam nas bordas dos furos (y = 404)
export const PIN_CLEAR_BOTTOM = BOLT.y0 - 2; // com o fundo acima disto, o pino saiu da tranca e ela pode correr
export const PEG_HALF = 7;
export const PEG_LEN = 260;
export const TIP_REST = 440; // y da ponta dos pegs com a chave a L = 0
export const LIFT_FULL = TIP_REST - PIN_CLEAR_BOTTOM; // subida que solta a tranca (102 px)
export const LIFT_START = -60; // chave ainda fora do quadro, por baixo
export const KEY_BAR = {x0: 470, x1: 810, h: 32} as const;
export const SLIDE_MAX = 220; // quanto a tranca recua quando solta

/** Ponta dos pegs (y) com a chave levantada `L` px a partir de TIP_REST. */
export const pegTip = (L: number): number => TIP_REST - L;
/** y do fundo de cada pino: repousa na borda do furo e só sobe quando o peg o empurra. */
export const pinBottom = (L: number): number => Math.min(PIN_REST_BOTTOM, pegTip(L));
export const pinTop = (L: number): number => pinBottom(L) - PIN_LEN;
/** A tranca só corre com os três pinos fora dela. */
export const trancaLivre = (L: number): boolean => pinBottom(L) <= PIN_CLEAR_BOTTOM;

const frames = (segundos: number) => Math.round(segundos * FPS);
/** Trecho do plano V1 dentro de cada cena: do começo da âncora ("Os princípios básicos dela" / "A fechadura de madeira do Egito") ao fim da cena. */
export const DURACAO_S03 = 11.92;
export const DURACAO_S18 = 11.6;
// Início do plano V1 em cada cena, em ms, como o pipeline o calcula (`shot_bounds`, app/pipeline/shots.py).
export const ANCORA_S03_MS = 5381;
export const ANCORA_S18_MS = 3356;
export const TOTAL_TRANCA_S03 = frames((DURACAO_S03 * 1000 - ANCORA_S03_MS) / 1000);
export const TOTAL_TRANCA_S18 = frames((DURACAO_S18 * 1000 - ANCORA_S18_MS) / 1000);

const aS03 = (fracao: number) => Math.round(TOTAL_TRANCA_S03 * fracao);
/** Quando cada peça começa a ser traçada na S03 e quantos quadros leva (para o `DrawPath`); na S18 tudo já está desenhado. */
export const TRACOS_S03 = {
  poste: {at: 0, dur: aS03(0.18)},
  canal: {at: aS03(0.08), dur: aS03(0.16)},
  tranca: {at: aS03(0.2), dur: aS03(0.22)},
  pinos: [0, 1, 2].map((i) => ({at: aS03(0.4) + 8 * i, dur: aS03(0.14)})),
} as const;

export type EstadoTranca = {
  chave: number; // L (px de subida da chave)
  chaveVisivel: number;
  slide: number; // recuo da tranca (px)
  rotulos: {poste: number; tranca: number; pinos: number; chave: number; naoConfere: number};
};


/** S03: o esquema se desenha em traço de lápis (poste, canal, tranca, pinos) e os rótulos entram. A chave não aparece. */
export function estadoTrancaS03(frame: number): EstadoTranca {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_TRANCA_S03) throw new RangeError(`frame fora de 0..${TOTAL_TRANCA_S03 - 1}: ${frame}`);
  const f = frame;
  const a = aS03;
  return {
    chave: LIFT_START, chaveVisivel: 0, slide: 0,
    rotulos: {
      poste: rampa(f, a(0.62), a(0.62) + 14), tranca: rampa(f, a(0.7), a(0.7) + 14), pinos: rampa(f, a(0.78), a(0.78) + 14), chave: 0, naoConfere: 0,
    },
  };
}

/** S18 (reprise): a tranca já desenhada; a chave sobe por baixo e levanta os pinos até a altura certa; a tranca se solta. Sem mostrar excesso. */
export function estadoTrancaS18(frame: number): EstadoTranca {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_TRANCA_S18) throw new RangeError(`frame fora de 0..${TOTAL_TRANCA_S18 - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(TOTAL_TRANCA_S18 * fracao);
  const sobe = rampa(f, a(0.12), a(0.5));
  const L = LIFT_START + (LIFT_FULL - LIFT_START) * sobe; // para exatamente na altura que solta a tranca
  return {
    chave: L,
    chaveVisivel: rampa(f, a(0.1), a(0.2)),
    slide: trancaLivre(L) ? SLIDE_MAX * rampa(f, a(0.56), a(0.78)) : 0,
    rotulos: {
      poste: 1, tranca: 1, pinos: 1, chave: rampa(f, a(0.3), a(0.3) + 14), naoConfere: rampa(f, a(0.8), a(0.8) + 16),
    },
  };
}
