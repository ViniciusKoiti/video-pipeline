// Geometria da vista de frente (corte transversal) da fechadura de pinos, usada nas cenas S12 e S13 do mec-fechadura-pt.
// Funções puras, em px de um quadro de 1280×720. Valores ilustrativos, como em geometria.ts (plano-animacao.md, "Duas vistas").
// Regra da ficha F16, também aqui: com a chave certa o topo do pino de chave fica na linha de corte (a borda do rotor).

export const CX = 640; // centro do rotor
export const CY = 360; // meio do quadro: a câmera centra em (W/2, H/2)
export const R_HOUSING = 270; // raio externo da carcaça (cabe acima do rodapé do quadro)
export const R_PLUG = 150; // raio do rotor; o círculo de raio R_PLUG é a linha de corte
export const PIN_HALF = 14; // meia largura dos pinos, como na vista lateral
export const HOLE_HALF = 16; // meia largura do furo do rotor
export const WELL_HALF = 20; // meia largura da câmara da carcaça
export const SHEAR_Y = CY - R_PLUG; // y da linha de corte na posição das 12 horas
export const KEY_PIN_LEN = 90; // do fundo do corte da chave até a linha de corte
export const DRIVER_LEN = 60;
export const WELL_TOP = CY - 240; // teto da câmara, onde a mola se apoia
export const KEYWAY = {half: 18, top: CY - (R_PLUG - KEY_PIN_LEN), bottom: CY + 110} as const; // canal da chave; topo = fundo do corte
export const BLADE = {half: 16, top: KEYWAY.top, bottom: KEYWAY.bottom - 10} as const; // lâmina da chave vista em seção

/** Giro final do rotor com a chave, em graus (sentido horário). */
export const GIRO = 90;

export type Pilha = {
  driverTop: number;
  driverBottom: number;
  springLength: number;
  keyPinTop: number;
  keyPinBottom: number;
};

/** Pilha das 12 horas, com a chave certa. Pino de chave em coordenadas do rotor antes de girar (topo na linha de corte, fundo no corte da chave). */
export function pilha(): Pilha {
  const driverBottom = SHEAR_Y;
  const driverTop = driverBottom - DRIVER_LEN;
  return {driverTop, driverBottom, springLength: driverTop - WELL_TOP, keyPinTop: SHEAR_Y, keyPinBottom: SHEAR_Y + KEY_PIN_LEN};
}

/** Ponto do plano depois de girar `graus` (horário) em torno do centro do rotor. */
export function girar(x: number, y: number, graus: number): [number, number] {
  const a = (graus * Math.PI) / 180;
  const dx = x - CX;
  const dy = y - CY;
  return [CX + dx * Math.cos(a) - dy * Math.sin(a), CY + dx * Math.sin(a) + dy * Math.cos(a)];
}
