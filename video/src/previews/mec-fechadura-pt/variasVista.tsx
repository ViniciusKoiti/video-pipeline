// Outras fechaduras de pinos (S22 do mec-fechadura-pt): a tubular (canal da chave redondo, chave tubular) e a dimple (cortes na lateral da chave, não no topo).
// O desenho só afirma o canal redondo e a posição dos cortes (F30, F31); nada além disso (nem a quantidade de pinos). Dentro de um StyleProvider do kit.
import React from 'react';
import {DrawPath} from '@viniciuskoitin/motion-kit/styles';
import {PALETAS} from './paleta';
import type {Variante} from './paleta';
import type {EstadoS22} from './linhaDoTempoResto';

const W = 1280;
const H = 720;
const layer: React.CSSProperties = {position: 'absolute', inset: 0};
const rect = (x0: number, y0: number, x1: number, y1: number) => `M${x0} ${y0}H${x1}V${y1}H${x0}Z`;
const circulo = (cx: number, cy: number, r: number) => `M${cx - r} ${cy}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`;
/** Anel (círculo com furo), pelo enrolamento oposto do furo. */
const anel = (cx: number, cy: number, ro: number, ri: number) =>
  `M${cx - ro} ${cy}a${ro} ${ro} 0 1 0 ${2 * ro} 0a${ro} ${ro} 0 1 0 ${-2 * ro} 0ZM${cx - ri} ${cy}a${ri} ${ri} 0 1 1 ${2 * ri} 0a${ri} ${ri} 0 1 1 ${-2 * ri} 0Z`;
const Camada = ({o, children}: {o: number; children: React.ReactNode}) => (o <= 0.001 ? null : <div style={{...layer, opacity: o}}>{children}</div>);

export const PAINEL_TUBULAR = {cx: 640, cy: 360, x0: 450, x1: 830, y0: 130, y1: 590} as const;
export const PAINEL_DIMPLE = {cx: 1040, cy: 360, x0: 850, x1: 1230, y0: 130, y1: 590} as const;
/** Entalhes na lateral da lâmina da dimple: [altura em relação ao centro, profundidade], à esquerda e à direita. */
const ENTALHES_ESQ: [number, number][] = [[-62, 8], [0, 12], [62, 6]];
const ENTALHES_DIR: [number, number][] = [[-32, 10], [30, 7], [86, 12]];

export function Outras({variant, e}: {variant: Variante; e: EstadoS22}) {
  const v = PALETAS[variant];
  let seed = 700;
  const P = ({d, fill, weight, color}: {d: string; fill?: string; weight?: number; color?: string}) => (
    <DrawPath d={d} width={W} height={H} at={0} duration={0} color={color ?? v.ink} strokeWidth={weight ?? v.weight} fill={fill}
      wobble={v.wobble} passes={v.passes} boilEvery={v.boil} seed={seed++} style={layer}/>
  );
  const T = PAINEL_TUBULAR;
  const D = PAINEL_DIMPLE;
  const ang = [20, 95, 170, 245, 320];
  return (
    <div style={{...layer, backgroundColor: v.bg}}>
      {v.grain && <svg width={W} height={H} style={{...layer, opacity: 0.13}}>
        {Array.from({length: 700}, (_, i) => <circle key={i} cx={(i * 173 + 17) % W} cy={(i * 97 + 23) % H} r={i % 3 ? 0.5 : 1} fill="#9e8e73"/>)}
      </svg>}

      {/* tubular: de frente, canal da chave redondo, chave tubular (um anel com entalhes na borda) */}
      <Camada o={e.abre}>
        <P d={rect(T.x0, T.y0, T.x1, T.y1)} color={v.muted} weight={2}/>
        <P d={circulo(T.cx, T.cy, 160)} fill={v.housing}/>
        <P d={circulo(T.cx, T.cy, 80)} fill={v.keyway}/>
        <P d={circulo(T.cx, T.cy, 24)} fill={v.well}/>
      </Camada>
      <Camada o={e.chaveTubular * e.abre}>
        <div style={{...layer, transform: `scale(${0.5 + 0.5 * e.chaveTubular})`, transformOrigin: `${T.cx}px ${T.cy}px`}}>
          <P d={anel(T.cx, T.cy, 72, 40)} fill={v.key}/>
          {ang.map((g) => <P key={g} d={circulo(T.cx + 72 * Math.cos((g * Math.PI) / 180), T.cy + 72 * Math.sin((g * Math.PI) / 180), 7)} fill={v.keyway} weight={1.5}/>)}
        </div>
      </Camada>

      {/* dimple: corte transversal da lâmina, com os entalhes nas laterais; pinos vindos dos dois lados leem os entalhes */}
      <Camada o={e.abre}>
        <P d={rect(D.x0, D.y0, D.x1, D.y1)} color={v.muted} weight={2}/>
        <P d={circulo(D.cx, D.cy, 160)} fill={v.housing}/>
        <P d={rect(D.cx - 30, D.cy - 112, D.cx + 30, D.cy + 112)} fill={v.keyway}/>
      </Camada>
      <Camada o={e.chaveDimple * e.abre}>
        <P d={rect(D.cx - 16, D.cy - 104, D.cx + 16, D.cy + 104)} fill={v.key}/>
        {ENTALHES_ESQ.map(([dy, dep]) => <P key={`l${dy}`} d={circulo(D.cx - 16, D.cy + dy, dep + 2)} fill={v.keyway} weight={1.5}/>)}
        {ENTALHES_DIR.map(([dy, dep]) => <P key={`r${dy}`} d={circulo(D.cx + 16, D.cy + dy, dep + 2)} fill={v.keyway} weight={1.5}/>)}
      </Camada>
      <Camada o={e.abre}>
        {ENTALHES_ESQ.map(([dy, dep]) => {
          const ponta = D.cx - 30 + (14 + dep) * e.pinosDimple; // recuado na parede do canal; avança até o fundo do entalhe
          return <P key={`pl${dy}`} d={rect(D.cx - 112, D.cy + dy - 6, ponta, D.cy + dy + 6)} fill={v.keyPin}/>;
        })}
        {ENTALHES_DIR.map(([dy, dep]) => {
          const ponta = D.cx + 30 - (14 + dep) * e.pinosDimple;
          return <P key={`pr${dy}`} d={rect(ponta, D.cy + dy - 6, D.cx + 112, D.cy + dy + 6)} fill={v.keyPin}/>;
        })}
      </Camada>

      <svg width={W} height={H} style={layer}>
        <g opacity={e.rotuloTubular}><text x={T.cx} y={T.y1 + 38} textAnchor="middle" fontFamily="DejaVu Sans, sans-serif" fontSize={24} fontWeight={600} fill={v.text}>Tubular: canal redondo</text></g>
        <g opacity={e.rotuloDimple}><text x={D.cx} y={D.y1 + 38} textAnchor="middle" fontFamily="DejaVu Sans, sans-serif" fontSize={24} fontWeight={600} fill={v.text}>Dimple: cortes na lateral</text></g>
      </svg>
    </div>
  );
}
