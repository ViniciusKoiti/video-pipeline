// Geometria e cinemática da vista em corte do cadeado (cenas S15 e S16 do mec-fechadura-pt). Funções puras, px de um quadro 1280×720.
// Mecanismo (source-03#E50–E60): o came fica na ponta do rotor; um trinco de cada lado, com a ponta angulada num entalhe da haste e uma mola
// que o empurra para fora; o braço de cada trinco repousa na borda do came (um por cima, outro por baixo); ao girar, o came puxa os braços
// para dentro, contra a mola, e os trincos saem dos entalhes. Uma mola sob a ponta mais longa da haste a empurra para fora.
// Valores ilustrativos, como no resto do estudo. O desenho é 180° simétrico em torno do eixo do came (o trinco de baixo é o de cima espelhado).

export const CAM = {x: 640, y: 440} as const; // eixo do rotor e do came
export const CAM_A = 60; // meio comprimento do came (um "palito" arredondado)
export const CAM_B = 16; // meia espessura do came
export const PLUG_R = 34; // raio do rotor visto de frente
export const GIRO = 90; // giro do rotor com a chave, graus, sentido horário
export const R_MAX = 70; // retração máxima procurada pelo solver, px

export const LATCH_DY = -77; // y do trinco de cima em relação ao eixo
export const LATCH_H = 22; // espessura do trinco
export const WEDGE_REL = [[-50, -66], [0, -66], [0, -16]] as const; // braço do trinco de cima, em repouso, em relação ao eixo (cunha de 45°, canto de baixo no centro da reta do came)
export const LEG_L = {x0: 396, x1: 424, bottom: 600} as const; // perna comprida da haste
export const LEG_R = {x0: 856, x1: 884, bottom: 545} as const; // perna curta
export const SHACKLE_TOP = 190; // topo da barra da haste (fechada)
export const SHACKLE_BAR_BOTTOM = 218;
export const NOTCH_DEPTH = 20;
export const NOTCH_HALF = 20;
export const TIP_FLANK = 18; // quanto a ponta do trinco avança além do ombro
export const X_INNER = 700; // ponta de dentro do trinco de cima (em repouso)
export const X_WALL = 800; // parede onde a mola do trinco de cima se apoia
export const BODY = {x0: 330, y0: 330, x1: 950, y1: 650} as const;
export const SHACKLE_RISE = 72; // quanto a mola sobe a haste
export const FREE_AT = NOTCH_DEPTH + 2; // retração a partir da qual a ponta já saiu do entalhe

/** Ponto (x, y) refletido pelo eixo do came (simetria de 180°). */
export const espelho = (x: number, y: number): [number, number] => [2 * CAM.x - x, 2 * CAM.y - y];

/** y do trinco de cima e de baixo. */
export const LATCH_Y_UP = CAM.y + LATCH_DY;
export const LATCH_Y_DOWN = CAM.y - LATCH_DY;

const rad = (g: number) => (g * Math.PI) / 180;
/** Gira (x, y) `graus` em torno da origem, no sentido horário da tela (y para baixo). */
export const girar = (x: number, y: number, graus: number): [number, number] => {
  const a = rad(graus);
  return [x * Math.cos(a) - y * Math.sin(a), x * Math.sin(a) + y * Math.cos(a)];
};

/** Contorno do came (palito arredondado) girado `phi` graus, em coordenadas relativas ao eixo. */
export function camBorda(phi: number): [number, number][] {
  const c = CAM_A - CAM_B;
  const pts: [number, number][] = [];
  const N = 240; // amostragem fina (0,4 px): a folga entre pontos esconderia penetrações de ~1 px
  const M = 120;
  for (let i = 0; i <= N; i++) pts.push([-c + (2 * c * i) / N, -CAM_B]); // reta de cima
  for (let i = 1; i < M; i++) pts.push([c + CAM_B * Math.cos(rad(-90 + (180 * i) / M)), CAM_B * Math.sin(rad(-90 + (180 * i) / M))]); // ponta da direita
  for (let i = 0; i <= N; i++) pts.push([c - (2 * c * i) / N, CAM_B]); // reta de baixo
  for (let i = 1; i < M; i++) pts.push([-c + CAM_B * Math.cos(rad(90 + (180 * i) / M)), CAM_B * Math.sin(rad(90 + (180 * i) / M))]); // ponta da esquerda
  return pts.map(([x, y]) => girar(x, y, phi));
}

/** O braço do trinco de cima (cunha), deslocado `r` para a direita, penetra o came? Devolve a maior profundidade (px) de penetração; <= 0 = sem penetração. */
export function penetracao(phi: number, r: number): number {
  let pior = 0;
  const [[xl, yt], [xr]] = WEDGE_REL;
  const c = yt - xl - r; // hipotenusa: y = x + c (a cunha fica acima dela, y menor)
  for (const [px, py] of camBorda(phi)) {
    if (py <= yt || px >= xr + r || px <= xl + r - 1) continue;
    const fundo = px + c - py; // quanto o ponto está acima da hipotenusa (dentro da cunha)
    if (fundo > pior) pior = fundo;
  }
  return pior;
}

/** Retração do trinco (px, para dentro) com o came girado `phi` graus: a menor que deixa a cunha encostada no came, sem penetrá-lo. */
export function retracao(phi: number): number {
  let lo = 0;
  let hi = R_MAX * 1.6;
  if (penetracao(phi, lo) <= 0.3) return 0;
  for (let k = 0; k < 40; k++) {
    const mid = (lo + hi) / 2;
    if (penetracao(phi, mid) <= 0.3) hi = mid;
    else lo = mid;
  }
  return hi;
}

/** Contorno da haste inteira (barra de cima, perna comprida à esquerda, perna curta à direita, um entalhe em cada), subida `dy` px. */
export function hasteCaminho(dy: number): string {
  const yE = LATCH_Y_UP;
  const yD = LATCH_Y_DOWN;
  const t = -dy; // desloca a haste inteira
  const p: [number, number][] = [
    [LEG_L.x0, SHACKLE_TOP], [LEG_R.x1, SHACKLE_TOP], [LEG_R.x1, LEG_R.bottom], [LEG_R.x0, LEG_R.bottom],
    [LEG_R.x0, yD + NOTCH_HALF], [LEG_R.x0 + NOTCH_DEPTH, yD], [LEG_R.x0, yD - NOTCH_HALF], [LEG_R.x0, SHACKLE_BAR_BOTTOM],
    [LEG_L.x1, SHACKLE_BAR_BOTTOM], [LEG_L.x1, yE - NOTCH_HALF], [LEG_L.x1 - NOTCH_DEPTH, yE], [LEG_L.x1, yE + NOTCH_HALF],
    [LEG_L.x1, LEG_L.bottom], [LEG_L.x0, LEG_L.bottom],
  ];
  return 'M' + p.map(([x, y]) => `${x} ${(y + t).toFixed(1)}`).join('L') + 'Z';
}

/** Polígono do trinco de cima com retração `r`: ponta angulada no entalhe da esquerda, corpo até a ponta de dentro. */
export function trincoCima(r: number): [number, number][] {
  const tipX = LEG_L.x1 - NOTCH_DEPTH + r;
  return [
    [tipX, LATCH_Y_UP], [tipX + TIP_FLANK, LATCH_Y_UP - LATCH_H / 2], [X_INNER + r, LATCH_Y_UP - LATCH_H / 2],
    [X_INNER + r, LATCH_Y_UP + LATCH_H / 2], [tipX + TIP_FLANK, LATCH_Y_UP + LATCH_H / 2],
  ];
}

/** Braço (cunha) do trinco de cima com retração `r`, em coordenadas absolutas. */
export const bracoCima = (r: number): [number, number][] => WEDGE_REL.map(([x, y]) => [CAM.x + x + r, CAM.y + y] as [number, number]);
