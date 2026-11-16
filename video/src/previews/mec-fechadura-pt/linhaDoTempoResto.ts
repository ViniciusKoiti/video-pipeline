// Linhas do tempo de cinco trechos do mec-fechadura-pt: 1.ª parte da S03 (as cinco colunas aparecem), 1.ª parte da S18 (corte alto demais),
// S19 (dois pinos por câmara, ao lado da tranca egípcia), S20 (as molas devolvem os pinos) e a porta com as duas chaves (S01 e reprise na S24).
// Funções puras. Durações da voz final (tempos-resto.json, conferido por check-resto.mjs); dentro de cada cena, os instantes são frações da duração
// (estimativa pela posição das palavras); o tempo exato por palavra só sai do `vp render`.
import {FUNDOS_CERTA, tipX} from './geometria.ts';
import {FPS, pulso, rampa} from './linhaDoTempo.ts';
import type {Estado} from './linhaDoTempo.ts';
import {estadoEntrada} from './entrada.ts';
import type {EstadoEntrada} from './entrada.ts';

export const DURACOES = {S01: 11.2, S02: 6.84, S03: 11.92, S18: 11.6, S19: 6.64, S20: 7.08, S21: 14.4, S22: 9.24, S23: 16.24, S24: 11.16, S25: 7.8} as const;
/** Início do 2.º plano de cada cena, em ms, como o pipeline o calcula (`shot_bounds`, app/pipeline/shots.py, sobre os WAVs de voice/leveled). */
export const ANCORAS_MS = {S03: 5381, S18: 3356, S21: 2945, S24: 7295} as const;
const frames = (s: number) => Math.round(s * FPS);
const framesMs = (ms: number) => Math.round((ms * FPS) / 1000);
export const TOTAL_S03A = framesMs(ANCORAS_MS.S03);
export const TOTAL_S18A = framesMs(ANCORAS_MS.S18);
export const TOTAL_S19 = frames(DURACOES.S19);
export const TOTAL_S20 = frames(DURACOES.S20);
export const TOTAL_S01 = frames(DURACOES.S01);
export const TOTAL_S02 = frames(DURACOES.S02);
export const TOTAL_S24A = framesMs(ANCORAS_MS.S24);
export const TOTAL_S24B = framesMs(DURACOES.S24 * 1000 - ANCORAS_MS.S24);
/** A V2.16 vai do começo da S21 até a âncora do plano `network` ("Ela levanta"). */
export const TOTAL_S21A = framesMs(ANCORAS_MS.S21);
export const TOTAL_S22 = frames(DURACOES.S22);
export const TOTAL_S23 = frames(DURACOES.S23);
export const TOTAL_S25 = frames(DURACOES.S25);

const cinco = (fn: (i: number) => number) => [0, 1, 2, 3, 4].map(fn);
const zeros = () => cinco(() => 0);

// ---- S03, 1.ª parte: a vista em corte completa e em repouso; as colunas se desenham uma a uma (o traço usa os instantes de `Desenho`, anima = true) ----
export function estadoS03A(frame: number): Estado {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_S03A) throw new RangeError(`frame fora de 0..${TOTAL_S03A - 1}: ${frame}`);
  return {
    cena: 'S11', insert: 0, tipPx: -40,
    grupos: {colunas: 1, molas: 1, superiores: 1, chavePinos: 1},
    rotulos: {carcaca: 0, rotor: 0, chave: 0, mola: 0, superior: 0, pinoChave: 0, linha: 0},
    linhaAt: 1_000_000, linhaBrilho: 0, setaGiro: 0, setaGiroCortada: 0, setaForca: 0,
    pulsos: {furos: zeros(), chavePinos: zeros(), superiores: zeros(), juncoes: zeros()},
  };
}

// ---- S18, 1.ª parte: uma chave com cortes rasos demais levanta as colunas além da altura certa e o rotor segue bloqueado; a tela não diz qual pino trava ----
/** Cortes da chave certa, com as colunas 3 e 5 rasas demais (o pino de chave passa da linha). Valores ilustrativos. */
export const FUNDOS_ALTA: readonly number[] = FUNDOS_CERTA.map((y, i) => (i === 2 || i === 4 ? 378 : y));
export const estadoS18A = (frame: number): EstadoEntrada => estadoEntrada(frame, TOTAL_S18A, {alerta: false, juncoes: false});

// ---- S20: a chave sai (ou nunca entrou) e as molas empurram os pinos superiores de volta para dentro dos furos do rotor ----
export function estadoS20(frame: number): Estado {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_S20) throw new RangeError(`frame fora de 0..${TOTAL_S20 - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(TOTAL_S20 * fracao);
  const insert = 1 - rampa(f, a(0.1), a(0.45));
  const tipPx = f < a(0.45) ? tipX(insert) : 300 - 340 * rampa(f, a(0.45), a(0.6)); // sai além da borda (x = -40)
  return {
    cena: 'S11', insert, tipPx,
    grupos: {colunas: 1, molas: 1, superiores: 1, chavePinos: 1},
    rotulos: {carcaca: 0, rotor: 0, chave: 0, mola: 0, superior: 0, pinoChave: 0, linha: 1},
    linhaAt: 0, linhaBrilho: 0, setaGiro: 0, setaGiroCortada: 0,
    setaForca: rampa(f, a(0.5), a(0.5) + 16),
    pulsos: {
      furos: cinco((i) => pulso(f, a(0.62) + 10 * i, 26)), chavePinos: zeros(),
      superiores: cinco((i) => pulso(f, a(0.76) + 8 * i, 30)), juncoes: zeros(),
    },
  };
}

// ---- S19: a coluna de um pino ganha o segundo; com a chave alta demais ela trava o rotor; na altura certa a linha fica livre ----
export const COLUNA = {
  x: 930, shear: 300, chamberTop: 150, keyPin: 110, driver: 70,
  fundoCerto: 410, // y do fundo do corte com a chave certa: o pino de chave fica com o topo na linha de corte
  fundoRaso: 376, // corte raso demais (a lâmina sem corte): o pino de chave passa 34 px da linha
  espacador: 40, // espessura do terceiro pino (S23)
  fundoB: 450, // fundo do corte da 2.ª chave (S23): com o espaçador, a junção espaçador/pino superior fica na linha
} as const;

export type EstadoS19 = {
  driver: number; // 0..1: o segundo pino entra na coluna
  fundo: number; // y do fundo do corte sob a coluna
  seta: number; // seta do rotor
  setaCortada: number; // "X" sobre a seta
  juncao: number; // pulso na junção quando ela volta à linha
  rotulo: number; // "Linha de corte"
  espaco: number; // 0..1: o espaçador (terceiro pino) entre o pino de chave e o superior (S23)
  linha2: number; // as duas junções tracejadas (S23)
  rotuloEsp: number; // "Espaçador"
};

export function estadoS19(frame: number): EstadoS19 {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_S19) throw new RangeError(`frame fora de 0..${TOTAL_S19 - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(TOTAL_S19 * fracao);
  const sobe = rampa(f, a(0.45), a(0.62));
  const desce = rampa(f, a(0.72), a(0.88));
  const fundo = COLUNA.fundoCerto + (COLUNA.fundoRaso - COLUNA.fundoCerto) * (sobe - desce);
  return {
    driver: rampa(f, a(0.22), a(0.4)),
    fundo,
    seta: rampa(f, a(0.42), a(0.42) + 12),
    setaCortada: rampa(f, a(0.6), a(0.6) + 10) * (1 - desce),
    juncao: pulso(f, a(0.9), 30),
    rotulo: rampa(f, a(0.1), a(0.1) + 14),
    espaco: 0, linha2: 0, rotuloEsp: 0,
  };
}

// ---- Porta com as duas chaves (S01 e reprise na S24) ----
export type ChaveId = 'A' | 'B';
export type EstadoPorta = {
  aparece: number; // porta
  chavesVisiveis: number;
  chaves: Record<ChaveId, {prox: number; giro: number}>; // prox: 0 = ao lado, 1 = na fechadura; giro: graus da chave (horário)
  tranca: number; // quanto o trinco da porta recuou, px (0 = trancada)
};

export const GIRO_PORTA = 90;
export const TRINCO_RECUO = 36;

/** `ordem`: primeira e segunda chave a entrar. A certa (A) gira e o trinco recua; a errada (B) entra, tenta e para. */
function janela(f: number, ini: number, fim: number, sai: boolean) {
  const entra = rampa(f, ini, ini + (fim - ini) * 0.25);
  const acao = rampa(f, ini + (fim - ini) * 0.25, ini + (fim - ini) * 0.7);
  // Ao sair, a chave primeiro gira de volta (0,70 a 0,85 da janela) e só então se afasta (0,85 a 1).
  const volta = sai ? rampa(f, ini + (fim - ini) * 0.7, ini + (fim - ini) * 0.85) : 0;
  const sale = sai ? rampa(f, ini + (fim - ini) * 0.85, fim) : 0;
  return {prox: entra * (1 - sale), acao, volta};
}

export function estadoPortaEm(frame: number, total: number, ordem: readonly [ChaveId, ChaveId], intro: boolean, ultimaSai: boolean): EstadoPorta {
  if (!Number.isInteger(frame) || frame < 0 || frame >= total) throw new RangeError(`frame fora de 0..${total - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(total * fracao);
  const s1 = intro ? [a(0.34), a(0.58)] : [a(0.06), a(0.46)];
  const s2 = intro ? [a(0.62), a(0.9)] : [a(0.5), a(0.96)];
  const J = [janela(f, s1[0], s1[1], true), janela(f, s2[0], s2[1], ultimaSai)];
  const chaves: EstadoPorta['chaves'] = {A: {prox: 0, giro: 0}, B: {prox: 0, giro: 0}};
  let tranca = 0;
  ordem.forEach((id, k) => {
    const j = J[k];
    // A certa gira e volta; a errada balança um pouco (tenta girar) e para.
    const giro = id === 'A' ? GIRO_PORTA * j.acao * (1 - j.volta) : 7 * Math.sin(Math.PI * 3 * j.acao) * (j.acao > 0 && j.acao < 1 ? 1 : 0);
    chaves[id] = {prox: j.prox, giro};
    if (id === 'A') tranca = TRINCO_RECUO * j.acao * (1 - j.volta);
  });
  return {
    aparece: intro ? rampa(f, 0, a(0.2)) : 1,
    chavesVisiveis: intro ? rampa(f, a(0.2), a(0.3)) : 1,
    chaves, tranca,
  };
}

export const estadoS01 = (frame: number): EstadoPorta => estadoPortaEm(frame, TOTAL_S01, ['A', 'B'], true, true);
export const estadoS24A = (frame: number): EstadoPorta => estadoPortaEm(frame, TOTAL_S24A, ['B', 'A'], false, false);

// ---- S23: a chave mestra: um terceiro pino (o espaçador) entre os outros dois; a coluna passa a ter duas linhas de corte; duas chaves diferentes a abrem ----
export function estadoS23(frame: number): EstadoS19 {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_S23) throw new RangeError(`frame fora de 0..${TOTAL_S23 - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(TOTAL_S23 * fracao);
  const troca = rampa(f, a(0.72), a(0.84));
  return {
    driver: 1,
    fundo: COLUNA.fundoCerto + (COLUNA.fundoB - COLUNA.fundoCerto) * troca,
    seta: rampa(f, a(0.58), a(0.58) + 12),
    setaCortada: 0,
    juncao: Math.max(pulso(f, a(0.62), 30), pulso(f, a(0.86), 30)),
    rotulo: rampa(f, a(0.02), a(0.02) + 14),
    espaco: rampa(f, a(0.16), a(0.3)),
    linha2: rampa(f, a(0.34), a(0.46)),
    rotuloEsp: rampa(f, a(0.28), a(0.28) + 14),
  };
}

// ---- S24, 2.ª parte (V2.17): a vista em corte com a chave certa; o rotor gira, o came gira junto e toca o bloco da trava ----
import type {EstadoCame} from './linhaDoTempoCadeado.ts';
import {GIRO} from './cadeado.ts';
export function estadoS24B(frame: number): EstadoCame {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_S24B) throw new RangeError(`frame fora de 0..${TOTAL_S24B - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(TOTAL_S24B * fracao);
  const gira = rampa(f, a(0.25), a(0.25) + 60);
  return {
    voltaFrente: 1, lateralScaleX: 1, frenteScaleX: 0,
    aparece: rampa(f, 0, 18),
    angulo: GIRO * gira,
    setaChave: rampa(f, a(0.22), a(0.22) + 14),
    contato: rampa(f, a(0.25) + 56, a(0.25) + 62) * (0.6 + 0.4 * pulso(f, a(0.25) + 62, 40)),
    rotulos: {came: rampa(f, 10, 24), bloco: rampa(f, 16, 30), aciona: rampa(f, a(0.25) + 62, a(0.25) + 76)},
  };
}

// ---- S25: a fechadura em corte, em repouso, se desmonta em peças que flutuam (vista explodida), sem rótulos ----
export const DESLOCAMENTO_S25 = {
  topo: {dx: 0, dy: -120}, molas: {dx: -26, dy: -175}, superiores: {dx: 24, dy: -75},
  rotor: {dx: 0, dy: 30}, chavePinos: {dx: -22, dy: 100}, base: {dx: 0, dy: 175}, chave: {dx: 0, dy: 0},
} as const;
export type GrupoS25 = keyof typeof DESLOCAMENTO_S25;
export type EstadoS25 = {estado: Estado; explosao: Record<GrupoS25, {dx: number; dy: number}>};

export function estadoS25(frame: number): EstadoS25 {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_S25) throw new RangeError(`frame fora de 0..${TOTAL_S25 - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(TOTAL_S25 * fracao);
  const t = rampa(f, a(0.15), a(0.55));
  const grupos = Object.keys(DESLOCAMENTO_S25) as GrupoS25[];
  // As peças flutuam um pouco depois de se afastar (balanço lento, fases diferentes).
  const explosao = Object.fromEntries(grupos.map((g, k) => [g, {
    dx: DESLOCAMENTO_S25[g].dx * t + 4 * t * Math.sin(f / 22 + k),
    dy: DESLOCAMENTO_S25[g].dy * t + 6 * t * Math.sin(f / 17 + 1.7 * k),
  }])) as EstadoS25['explosao'];
  // A chave fica bem além da borda: com a redução de 0,72 do clipe, x = -40 voltaria a aparecer.
  return {estado: {...estadoS03A(0), tipPx: -600}, explosao};
}

// ---- S22: a vista em corte encolhe para o canto; abrem-se a tubular (canal redondo) e a dimple (cortes na lateral) ----
export type EstadoS22 = {
  encolhe: number; abre: number; rotuloTubular: number; chaveTubular: number; rotuloDimple: number; chaveDimple: number; pinosDimple: number;
};
export function estadoS22(frame: number): EstadoS22 {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_S22) throw new RangeError(`frame fora de 0..${TOTAL_S22 - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(TOTAL_S22 * fracao);
  return {
    encolhe: rampa(f, a(0.02), a(0.14)),
    abre: rampa(f, a(0.12), a(0.26)),
    rotuloTubular: rampa(f, a(0.36), a(0.36) + 14),
    chaveTubular: rampa(f, a(0.4), a(0.52)),
    rotuloDimple: rampa(f, a(0.6), a(0.6) + 14),
    chaveDimple: rampa(f, a(0.64), a(0.74)),
    pinosDimple: rampa(f, a(0.74), a(0.88)),
  };
}

// ---- S21, V2.16: a vista em corte de volta, em repouso, com a chave inteira em destaque; sem rótulos ----
export type EstadoS21A = {estado: Estado; destaque: number};
export function estadoS21A(frame: number): EstadoS21A {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_S21A) throw new RangeError(`frame fora de 0..${TOTAL_S21A - 1}: ${frame}`);
  const f = frame;
  const a = (fracao: number) => Math.round(TOTAL_S21A * fracao);
  // Os pinos, as molas e as câmaras esmaecem e a chave ganha contorno (com um pulso leve depois de aceso).
  const foco = rampa(f, a(0.1), a(0.4));
  const esmaece = 1 - (1 - 0.35) * foco;
  return {
    estado: {
      cena: 'S11', insert: 1, tipPx: 990,
      grupos: {colunas: esmaece, molas: esmaece, superiores: esmaece, chavePinos: esmaece},
      rotulos: {carcaca: 0, rotor: 0, chave: 0, mola: 0, superior: 0, pinoChave: 0, linha: 0},
      linhaAt: 0, linhaBrilho: 0, setaGiro: 0, setaGiroCortada: 0, setaForca: 0,
      pulsos: {furos: zeros(), chavePinos: zeros(), superiores: zeros(), juncoes: zeros()},
    },
    destaque: rampa(f, a(0.3), a(0.55)) * (0.75 + 0.25 * pulso(f, a(0.55), 30)),
  };
}

// ---- S02 (V2.0 e V2.0b): o contorno de uma fechadura se desenha em traço; "a gente corta uma ao meio" e ele mostra a vista em corte, sem rótulos ----
const aS02 = (fracao: number) => Math.round(TOTAL_S02 * fracao);
/** Quando cada traço do contorno começa e quanto leva (em quadros, para o `DrawPath`). */
export const TRACOS_S02 = {
  corpo: {at: 0, dur: aS02(0.35)},
  canal: {at: aS02(0.3), dur: aS02(0.12)},
  eixo: {at: aS02(0.4), dur: aS02(0.15)},
} as const;
/** A linha de corte percorre a fechadura da esquerda para a direita, nesta faixa de x (a da carcaça em `geometria.ts`). */
export const CORTE_S02 = {x0: 300, x1: 1000} as const;
export type EstadoS02 = {corte: number; linha: number};
export function estadoS02(frame: number): EstadoS02 {
  if (!Number.isInteger(frame) || frame < 0 || frame >= TOTAL_S02) throw new RangeError(`frame fora de 0..${TOTAL_S02 - 1}: ${frame}`);
  const f = frame;
  return {
    corte: rampa(f, aS02(0.62), aS02(0.86)),
    linha: rampa(f, aS02(0.6), aS02(0.64)) * (1 - rampa(f, aS02(0.86), aS02(0.92))),
  };
}
