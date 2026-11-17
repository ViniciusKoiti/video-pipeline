// Paletas dos dois traços do estudo visual do mec-fechadura-pt (plano-animacao.md). Compartilhadas pela vista lateral e pela vista de frente.
export type Variante = 'limpo' | 'mao';

export type Paleta = {
  bg: string; ink: string; housing: string; well: string; plug: string; hole: string; keyway: string; key: string;
  keyPin: string; driver: string; spring: string; text: string; muted: string; shear: string; alerta: string;
  wobble: number; passes: number; boil: number | null; weight: number; grain: boolean; rotulo: string;
};

export const PALETAS: Record<Variante, Paleta> = {
  // Fundo escuro, traço fino e reto, cores chapadas. A linha de corte é branca (plano-animacao.md).
  limpo: {
    bg: '#0f1724', ink: '#d6deee', housing: '#586278', well: '#3a4357', plug: '#356bb3', hole: '#1d3a66', keyway: '#0d1422',
    key: '#f2c230', keyPin: '#3fbf86', driver: '#f08a3c', spring: '#e6ebf5', text: '#e6ebf5', muted: '#9aa6bd', shear: '#ffffff',
    alerta: '#ff6b6b', wobble: 0, passes: 1, boil: null, weight: 2.6, grain: false, rotulo: 'traço limpo',
  },
  // Papel e tinta, com o tremor e os repasses do estilo pencil-sketch do kit, como no estudo do Agostinho.
  mao: {
    bg: '#f5efdf', ink: '#332e29', housing: '#d4cdbd', well: '#ebe3d0', plug: '#a9cbdb', hole: '#8db5c9', keyway: '#e3d9c1',
    key: '#f1c75b', keyPin: '#93d3a2', driver: '#f0a96e', spring: '#332e29', text: '#332e29', muted: '#7a6f60', shear: '#b8372e',
    alerta: '#b8372e', wobble: 1.5, passes: 2, boil: 8, weight: 4, grain: true, rotulo: 'traço à mão',
  },
};
