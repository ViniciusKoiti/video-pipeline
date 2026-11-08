// Geometria do traço "à mão" do quadro de teste (docs/pesquisa/estilo-desenho-a-mao-2026-11-03.md).
// Pura: sem React nem Remotion, para o `node --test` rodar sem navegador. Tudo é determinístico: mesma semente e
// mesmo quadro dão o mesmo desenho. O traço tem espessura variável (afina nas pontas) e o contorno fechado tem
// espessura uniforme. Nenhum desenho aqui é copiado de terceiros: são curvas e retas calculadas.

export type Ponto = readonly [number, number];

/** Ruído determinístico em [0, 1): a semente e o índice viram um valor fixo. */
export function ruido(semente: number, i: number): number {
  const x = Math.sin((semente + 1) * 12.9898 + (i + 1) * 78.233) * 43758.5453;
  return x - Math.floor(x);
}

const grampo = (v: number, min: number, max: number) => Math.min(max, Math.max(min, v));

/** Curva quadrática de `p0` a `p1` com controle `c`, em `n` pontos (os dois extremos incluídos). */
export function curva(p0: Ponto, c: Ponto, p1: Ponto, n = 24): Ponto[] {
  const pontos: Ponto[] = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1);
    const a = (1 - t) * (1 - t);
    const b = 2 * (1 - t) * t;
    const d = t * t;
    pontos.push([a * p0[0] + b * c[0] + d * p1[0], a * p0[1] + b * c[1] + d * p1[1]]);
  }
  return pontos;
}

/** Reta de `a` a `b`, em `n` pontos (os dois extremos incluídos). */
export function reta(a: Ponto, b: Ponto, n = 2): Ponto[] {
  const pontos: Ponto[] = [];
  for (let i = 0; i < n; i++) {
    const t = i / (n - 1);
    pontos.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
  }
  return pontos;
}

/** Elipse de centro (cx, cy) e raios (rx, ry), em `n` pontos. Não repete o primeiro ponto no fim. */
export function elipse(cx: number, cy: number, rx: number, ry: number, n = 72): Ponto[] {
  const pontos: Ponto[] = [];
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2;
    pontos.push([cx + rx * Math.cos(a), cy + ry * Math.sin(a)]);
  }
  return pontos;
}

/** Retângulo em polilinha fechada, com um ponto a cada `passo` px de borda (para o tremor aparecer). */
export function retangulo(x0: number, y0: number, x1: number, y1: number, passo = 40): Ponto[] {
  const lados: [Ponto, Ponto][] = [
    [[x0, y0], [x1, y0]],
    [[x1, y0], [x1, y1]],
    [[x1, y1], [x0, y1]],
    [[x0, y1], [x0, y0]],
  ];
  const pontos: Ponto[] = [];
  for (const [a, b] of lados) {
    const n = Math.max(1, Math.round(Math.hypot(b[0] - a[0], b[1] - a[1]) / passo));
    for (let i = 0; i < n; i++) {
      const t = i / n;
      pontos.push([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t]);
    }
  }
  return pontos;
}

/** Concatena trechos sem repetir o ponto de emenda. */
export function encadeia(...trechos: Ponto[][]): Ponto[] {
  const pontos: Ponto[] = [];
  for (const trecho of trechos) {
    pontos.push(...(pontos.length === 0 ? trecho : trecho.slice(1)));
  }
  return pontos;
}

/** Tira o último ponto quando ele é o primeiro (contorno fechado que já volta ao início). */
export function fecha(pontos: readonly Ponto[]): Ponto[] {
  const n = pontos.length;
  if (n > 1 && pontos[0][0] === pontos[n - 1][0] && pontos[0][1] === pontos[n - 1][1]) {
    return pontos.slice(0, n - 1);
  }
  return [...pontos];
}

/** Desloca cada ponto por ruído determinístico de até `amplitude` px. Amplitude 0 não mexe em nada. */
export function tremer(pontos: readonly Ponto[], amplitude: number, semente: number): Ponto[] {
  if (amplitude <= 0) return [...pontos];
  return pontos.map((p, i) => [
    p[0] + (ruido(semente, 2 * i) * 2 - 1) * amplitude,
    p[1] + (ruido(semente, 2 * i + 1) * 2 - 1) * amplitude,
  ]);
}

/** Largura do traço no trecho `t` (0 a 1): fina nas pontas, cheia no meio. `base` é a largura máxima. */
export function larguraNoTrecho(t: number, base: number): number {
  return base * (0.3 + 0.7 * Math.pow(Math.sin(Math.PI * grampo(t, 0, 1)), 0.5));
}

/** O trecho inicial de `pontos` até a fração `progresso` (0 a 1), com o último ponto interpolado. */
export function pontosAte(pontos: readonly Ponto[], progresso: number): Ponto[] {
  if (progresso <= 0 || pontos.length === 0) return [];
  if (progresso >= 1) return [...pontos];
  const k = progresso * (pontos.length - 1);
  const inteiro = Math.floor(k);
  const resto = k - inteiro;
  const saida: Ponto[] = pontos.slice(0, inteiro + 1).map((p) => [p[0], p[1]] as Ponto);
  const proximo = pontos[inteiro + 1];
  if (proximo && resto > 0) {
    const a = pontos[inteiro];
    saida.push([a[0] + (proximo[0] - a[0]) * resto, a[1] + (proximo[1] - a[1]) * resto]);
  }
  return saida;
}

/** Path SVG de um polígono fechado ("M … L … Z"). Vazio quando há menos de dois pontos. */
export function poligono(pontos: readonly Ponto[]): string {
  if (pontos.length < 2) return "";
  const [x0, y0] = pontos[0];
  const resto = pontos.slice(1).map(([x, y]) => `L ${x.toFixed(2)} ${y.toFixed(2)}`);
  return [`M ${x0.toFixed(2)} ${y0.toFixed(2)}`, ...resto, "Z"].join(" ");
}

/**
 * Contorno de um traço como polígono(s) a preencher. Aberto: um polígono com a espessura afinando nas pontas.
 * Fechado: dois anéis (fora e dentro), a preencher com `fill-rule: evenodd`; a espessura é uniforme.
 */
export function contornoDeTraco(pontos: readonly Ponto[], largura: number, fechado = false): string {
  const n = pontos.length;
  if (n < 2) return "";
  const esquerda: Ponto[] = [];
  const direita: Ponto[] = [];
  for (let i = 0; i < n; i++) {
    const anterior = pontos[fechado ? (i - 1 + n) % n : Math.max(0, i - 1)];
    const seguinte = pontos[fechado ? (i + 1) % n : Math.min(n - 1, i + 1)];
    const tx = seguinte[0] - anterior[0];
    const ty = seguinte[1] - anterior[1];
    const comprimento = Math.hypot(tx, ty) || 1;
    const nx = -ty / comprimento;
    const ny = tx / comprimento;
    const w = (fechado ? largura : larguraNoTrecho(i / (n - 1), largura)) / 2;
    const [x, y] = pontos[i];
    esquerda.push([x + nx * w, y + ny * w]);
    direita.push([x - nx * w, y - ny * w]);
  }
  if (fechado) return `${poligono(esquerda)} ${poligono(direita)}`;
  return poligono([...esquerda, ...direita.reverse()]);
}
