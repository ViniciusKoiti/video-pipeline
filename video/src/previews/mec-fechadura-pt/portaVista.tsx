// Porta trancada com duas chaves (V0: S01 e reprise na S24 do mec-fechadura-pt), em traço simples. Sem rótulos, sem pessoa. Dentro de um StyleProvider do kit.
// A chave certa (A) entra, gira e o trinco da porta recolhe; a errada (B) entra, tenta e para. Pictograma: a chave gira em torno da própria ponta.
import React from 'react';
import {DrawPath} from '@viniciuskoitin/motion-kit/styles';
import {PALETAS} from './paleta';
import type {Variante} from './paleta';
import type {ChaveId, EstadoPorta} from './linhaDoTempoResto';
import {LEGENDA_DE_ESTUDO} from './legenda';

const W = 1280;
const H = 720;
const layer: React.CSSProperties = {position: 'absolute', inset: 0};
const rect = (x0: number, y0: number, x1: number, y1: number) => `M${x0} ${y0}H${x1}V${y1}H${x0}Z`;
const circulo = (cx: number, cy: number, r: number) => `M${cx - r} ${cy}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`;
const Camada = ({o, children}: {o: number; children: React.ReactNode}) => (o <= 0.001 ? null : <div style={{...layer, opacity: o}}>{children}</div>);

const PORTA = {x0: 540, y0: 60, x1: 1000, y1: 660} as const;
const FECHADURA = {x: 900, y: 380} as const;
const TRINCO = {y0: 362, y1: 398, saliencia: 36} as const;
/** Posição de repouso da ponta de cada chave (lado esquerdo, uma acima da outra) e cortes de cada uma: [distância da ponta, profundidade]. */
const REPOUSO: Record<ChaveId, {x: number; y: number; cortes: [number, number][]}> = {
  A: {x: 380, y: 230, cortes: [[-45, 12], [-85, 18], [-125, 9], [-160, 15]]},
  B: {x: 380, y: 500, cortes: [[-35, 16], [-70, 8], [-110, 17], [-150, 10]]},
};
const PONTA_NA_FECHADURA = {x: FECHADURA.x - 24, y: FECHADURA.y};

/** Chave em traço simples: lâmina com cortes embaixo e argola; a ponta fica em (x, y). */
function chave(x: number, y: number, cortes: [number, number][]): {lamina: string; argola: string} {
  const pts: string[] = [`M${x} ${y - 14}`, `L${x - 190} ${y - 14}`, `L${x - 190} ${y + 14}`];
  for (const [c, dep] of [...cortes].sort((p, q) => p[0] - q[0])) {
    pts.push(`L${x + c - 12} ${y + 14}`, `L${x + c - 8} ${y + 14 - dep}`, `L${x + c + 8} ${y + 14 - dep}`, `L${x + c + 12} ${y + 14}`);
  }
  pts.push(`L${x} ${y + 14}Z`);
  return {lamina: pts.join(''), argola: circulo(x - 232, y, 34) + circulo(x - 232, y, 12)};
}

export function Porta({variant, e, legenda}: {variant: Variante; e: EstadoPorta; legenda: string}) {
  const v = PALETAS[variant];
  let seed = 600;
  const P = ({d, fill, weight, color}: {d: string; fill?: string; weight?: number; color?: string}) => (
    <DrawPath d={d} width={W} height={H} at={0} duration={0} color={color ?? v.ink} strokeWidth={weight ?? v.weight} fill={fill}
      wobble={v.wobble} passes={v.passes} boilEvery={v.boil} seed={seed++} style={layer}/>
  );
  const cor: Record<ChaveId, string> = {A: v.key, B: v.ink};
  return (
    <div style={{...layer, backgroundColor: v.bg}}>
      {v.grain && <svg width={W} height={H} style={{...layer, opacity: 0.13}}>
        {Array.from({length: 700}, (_, i) => <circle key={i} cx={(i * 173 + 17) % W} cy={(i * 97 + 23) % H} r={i % 3 ? 0.5 : 1} fill="#9e8e73"/>)}
      </svg>}
      <Camada o={e.aparece}>
        {/* trinco, por baixo da porta: sai da borda quando trancada e recolhe quando a chave certa gira */}
        <P d={rect(PORTA.x1 - e.tranca, TRINCO.y0, PORTA.x1 + TRINCO.saliencia - e.tranca, TRINCO.y1)} fill={v.ink}/>
        <P d={rect(PORTA.x0, PORTA.y0, PORTA.x1, PORTA.y1)} fill={v.housing}/>
        <P d={rect(PORTA.x0 + 40, PORTA.y0 + 40, PORTA.x1 - 40, PORTA.y1 - 40)} color={v.muted} weight={2}/>
        <P d={circulo(FECHADURA.x, FECHADURA.y, 46)} fill={v.well}/>
        <P d={rect(FECHADURA.x - 6, FECHADURA.y - 16, FECHADURA.x + 6, FECHADURA.y + 16)} fill={v.keyway} weight={2}/>
      </Camada>
      <Camada o={e.chavesVisiveis}>
        {(['A', 'B'] as ChaveId[]).map((id) => {
          const r = REPOUSO[id];
          const k = chave(r.x, r.y, r.cortes);
          const {prox, giro} = e.chaves[id];
          const dx = (PONTA_NA_FECHADURA.x - r.x) * prox;
          const dy = (PONTA_NA_FECHADURA.y - r.y) * prox;
          return (
            <div key={id} style={{...layer, transform: `translate(${dx}px, ${dy}px) rotate(${giro}deg)`, transformOrigin: `${r.x}px ${r.y}px`}}>
              <P d={k.lamina} fill={cor[id]}/>
              <P d={k.argola} fill={cor[id]}/>
            </div>
          );
        })}
      </Camada>
      <svg width={W} height={H} style={layer}>
        <text x={40} y={H - 22} fontFamily="DejaVu Sans, sans-serif" fontSize={15} fontWeight={600} fill={v.muted}>{LEGENDA_DE_ESTUDO ? legenda : ''}</text>
      </svg>
    </div>
  );
}
