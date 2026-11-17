// Helpers de desenho compartilhados pelas vistas do estudo mec-fechadura-pt (sem React).
const rad = (g: number) => (g * Math.PI) / 180;

/** Arco no sentido horário em torno de (cx, cy), de `a0` a `a1` graus (0° = 3 horas, 90° = 6 horas), com ponta de seta no fim. */
export function arcoComSeta(cx: number, cy: number, r: number, a0: number, a1: number): string {
  const ponto = (g: number) => [cx + r * Math.cos(rad(g)), cy + r * Math.sin(rad(g))] as const;
  const [x0, y0] = ponto(a0);
  const [x1, y1] = ponto(a1);
  const tx = -Math.sin(rad(a1)); // tangente horária no fim do arco
  const ty = Math.cos(rad(a1));
  const nx = Math.cos(rad(a1));
  const ny = Math.sin(rad(a1));
  const ponta = (s: number) => `M${x1.toFixed(1)} ${y1.toFixed(1)}L${(x1 - 16 * tx + s * 9 * nx).toFixed(1)} ${(y1 - 16 * ty + s * 9 * ny).toFixed(1)}`;
  return `M${x0.toFixed(1)} ${y0.toFixed(1)}A${r} ${r} 0 0 1 ${x1.toFixed(1)} ${y1.toFixed(1)}${ponta(1)}${ponta(-1)}`;
}

/** Mola em ziguezague na horizontal, entre x0 e x1, em y, com `n` voltas. */
export function molaH(y: number, x0: number, x1: number, n = 8, amp = 9): string {
  const step = (x1 - x0) / n;
  const pts = [`M${x0.toFixed(1)} ${y}`];
  for (let k = 0; k < n; k++) pts.push(`L${(x0 + (k + 0.5) * step).toFixed(1)} ${y + (k % 2 === 0 ? amp : -amp)}`);
  pts.push(`L${x1.toFixed(1)} ${y}`);
  return pts.join('');
}

/** Mola em ziguezague na vertical, entre y0 e y1, em x, com `n` voltas. */
export function molaV(x: number, y0: number, y1: number, n = 6, amp = 10): string {
  const step = (y1 - y0) / n;
  const pts = [`M${x} ${y0.toFixed(1)}`];
  for (let k = 0; k < n; k++) pts.push(`L${x + (k % 2 === 0 ? amp : -amp)} ${(y0 + (k + 0.5) * step).toFixed(1)}`);
  pts.push(`L${x} ${y1.toFixed(1)}`);
  return pts.join('');
}

/** Caminho de um polígono fechado a partir dos pontos. */
export const poligono = (pts: ReadonlyArray<readonly [number, number]>): string =>
  pts.map(([x, y], k) => `${k === 0 ? 'M' : 'L'}${x.toFixed(1)} ${y.toFixed(1)}`).join('') + 'Z';
