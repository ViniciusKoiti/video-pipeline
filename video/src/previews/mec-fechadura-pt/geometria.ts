// Geometria da vista em corte da fechadura de pinos (episódio mec-fechadura-pt).
// Funções puras, em px de um quadro de 1280×720 (renderize com --scale=1.5 para 1080p).
// Os valores são exemplo didático, não medida de nenhuma fechadura real (plano-animacao.md, "Valores ilustrativos").
// Regra da ficha F16: com a chave certa inteira, o topo de cada pino de chave fica na linha de corte.

export const W = 1280;
export const H = 720;

export const SHEAR = 300; // y da linha de corte (onde o rotor encontra a carcaça)
export const COLUMNS = [430, 545, 660, 775, 890] as const; // x de cada coluna (cinco, como a patente descreve)
export const KEY_PIN = [105, 85, 125, 95, 115] as const; // comprimento de cada pino de chave (todos diferentes)
export const DRIVER = 70; // comprimento do pino superior (igual nas cinco colunas)
export const PIN_HALF = 14; // meia largura dos pinos
export const Y_REST = 440; // y do fundo do pino de chave sem chave (dentro do canal da chave)
export const CHAMBER_TOP = 165; // y do teto da câmara na carcaça (onde a mola se apoia)

export const HOUSING = {x0: 300, x1: 1000, top: 120, bottom: 560, bottomEnd: 620} as const;
export const KEYWAY = {top: 370, bottom: 520} as const; // canal da chave, dentro do rotor
export const BLADE_TOP = 372; // topo da lâmina sem corte
export const BLADE_BOTTOM = 515;
export const BLADE_LEN = 690; // da ponta até o ombro da chave
export const TIP_IN = 990; // x da ponta com a chave inteira
export const TIP_OUT = 300; // x da ponta com a chave encostada na face do rotor
export const CUT_FLAT = 18; // meia largura do fundo de cada corte
export const CUT_SLOPE = 45; // meia largura de cada corte, com as rampas
export const TIP_CHAMFER = 40; // comprimento do chanfro da ponta

const clamp01 = (v: number) => Math.min(1, Math.max(0, v));
const lerp = (a: number, b: number, t: number) => a + (b - a) * t;

/** y do fundo de cada corte da chave: o pino de chave pousa aqui (F16). */
export const cutBottom = (i: number): number => SHEAR + KEY_PIN[i];
/** Fundos dos cortes da chave certa; uma chave errada passa outro vetor (um y por coluna) às funções abaixo. */
export const FUNDOS_CERTA: readonly number[] = KEY_PIN.map((k) => SHEAR + k);

/** Perfil do topo da lâmina: pontos [d, y], com d a distância atrás da ponta (cresce para o ombro). */
export function bladeProfile(fundos: readonly number[] = FUNDOS_CERTA): [number, number][] {
  const points: [number, number][] = [[0, Y_REST], [TIP_CHAMFER, BLADE_TOP]];
  for (let i = COLUMNS.length - 1; i >= 0; i--) {
    const d = TIP_IN - COLUMNS[i];
    points.push([d - CUT_SLOPE, BLADE_TOP], [d - CUT_FLAT, fundos[i]], [d + CUT_FLAT, fundos[i]], [d + CUT_SLOPE, BLADE_TOP]);
  }
  points.push([BLADE_LEN, BLADE_TOP]);
  return points;
}

/** y do topo da lâmina a uma distância d atrás da ponta; Infinity onde não há lâmina. */
export function bladeTopAt(d: number, fundos: readonly number[] = FUNDOS_CERTA): number {
  if (d < 0 || d > BLADE_LEN) return Infinity;
  const profile = bladeProfile(fundos);
  for (let k = 1; k < profile.length; k++) {
    const [d0, y0] = profile[k - 1];
    const [d1, y1] = profile[k];
    if (d <= d1) return d1 === d0 ? y1 : lerp(y0, y1, (d - d0) / (d1 - d0));
  }
  return BLADE_TOP;
}

/** x da ponta da chave para o progresso de inserção 0 (fora) … 1 (inteira). */
export const tipX = (insert: number): number => lerp(TIP_OUT, TIP_IN, clamp01(insert));

export type Column = {
  x: number;
  keyPinTop: number;
  keyPinBottom: number;
  driverTop: number;
  driverBottom: number;
  springLength: number;
  driverStraddles: boolean; // o pino superior atravessa a linha de corte
  keyPinCrosses: boolean; // o pino de chave sobe além da linha de corte
};

/** Estado das cinco colunas para o progresso de inserção `insert`. */
export function columnsAt(insert: number, fundos: readonly number[] = FUNDOS_CERTA): Column[] {
  const tip = tipX(insert);
  return COLUMNS.map((x, i) => {
    const bottom = Math.min(Y_REST, bladeTopAt(tip - x, fundos));
    const keyPinTop = bottom - KEY_PIN[i];
    const driverBottom = keyPinTop;
    const driverTop = driverBottom - DRIVER;
    return {
      x,
      keyPinTop,
      keyPinBottom: bottom,
      driverTop,
      driverBottom,
      springLength: driverTop - CHAMBER_TOP,
      driverStraddles: driverTop < SHEAR && driverBottom > SHEAR,
      keyPinCrosses: keyPinTop < SHEAR,
    };
  });
}

/** O rotor está livre quando nenhum pino atravessa a linha (todas as junções exatamente nela). */
export const plugFree = (insert: number): boolean => columnsAt(insert).every((c) => Math.abs(c.keyPinTop - SHEAR) < 0.01);
