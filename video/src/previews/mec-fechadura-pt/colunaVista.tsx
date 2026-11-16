// Coluna de pinos da S19 do mec-fechadura-pt: um pino por posição (como na tranca egípcia) vira dois; com a chave alta demais a coluna trava o rotor,
// na altura certa a linha de corte fica livre. A tela não destaca qual pino trava (F23). Dentro de um StyleProvider do kit; quadros parados.
import React from 'react';
import {DrawPath} from '@viniciuskoitin/motion-kit/styles';
import {PALETAS} from './paleta';
import type {Variante} from './paleta';
import {COLUNA} from './linhaDoTempoResto';
import type {EstadoS19} from './linhaDoTempoResto';
import {molaV} from './util';
import {LEGENDA_DE_ESTUDO} from './legenda';

const W = 1280;
const H = 720;
const layer: React.CSSProperties = {position: 'absolute', inset: 0};
const rect = (x0: number, y0: number, x1: number, y1: number) => `M${x0} ${y0}H${x1}V${y1}H${x0}Z`;
const circulo = (cx: number, cy: number, r: number) => `M${cx - r} ${cy}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`;
const Camada = ({o, children}: {o: number; children: React.ReactNode}) => (o <= 0.001 ? null : <div style={{...layer, opacity: o}}>{children}</div>);

const CASA = {x0: 700, x1: 1160, top: 110, rotorBottom: 560} as const;
const CANAL = {top: 372, bottom: 520} as const;
const LAMINA = {x0: 660, x1: 1010, top: 376, bottom: 515} as const;
const COR_ESPACADOR: Record<Variante, string> = {limpo: '#b08cf0', mao: '#a98bd0'};

export function Coluna({variant, e, legenda}: {variant: Variante; e: EstadoS19; legenda: string}) {
  const v = PALETAS[variant];
  let seed = 500;
  const P = ({d, fill, weight, color, dash}: {d: string; fill?: string; weight?: number; color?: string; dash?: 'solid' | 'dashed'}) => (
    <DrawPath d={d} width={W} height={H} at={0} duration={0} color={color ?? v.ink} strokeWidth={weight ?? v.weight} fill={fill}
      wobble={v.wobble} passes={v.passes} boilEvery={v.boil} seed={seed++} dash={dash} style={layer}/>
  );
  const {x, shear, chamberTop, keyPin, driver} = COLUNA;
  const pinoTop = e.fundo - keyPin;
  const dy = (1 - e.driver) * -60; // o segundo pino desce para dentro da câmara
  const espTop = pinoTop - COLUNA.espacador * e.espaco; // o espaçador (S23) empurra o pino superior para cima
  const driverBottom = espTop + dy;
  const driverTop = driverBottom - driver;
  const lamina = `M${LAMINA.x0} ${LAMINA.bottom}V${LAMINA.top}H${x - 45}L${x - 18} ${e.fundo}H${x + 18}L${x + 45} ${LAMINA.top}H${LAMINA.x1}V${LAMINA.bottom}Z`;
  const linha = `M${CASA.x0 - 20} ${shear}H${CASA.x1 + 20}`;

  return (
    <div style={{...layer, backgroundColor: v.bg}}>
      {v.grain && <svg width={W} height={H} style={{...layer, opacity: 0.13}}>
        {Array.from({length: 700}, (_, i) => <circle key={i} cx={(i * 173 + 17) % W} cy={(i * 97 + 23) % H} r={i % 3 ? 0.5 : 1} fill="#9e8e73"/>)}
      </svg>}
      <P d={rect(CASA.x0, CASA.top, CASA.x1, shear)} fill={v.housing}/>
      <P d={rect(CASA.x0, shear, CASA.x1, CASA.rotorBottom)} fill={v.plug}/>
      <P d={rect(CASA.x0, CANAL.top, CASA.x1, CANAL.bottom)} fill={v.keyway}/>
      <P d={rect(x - 20, chamberTop, x + 20, shear)} fill={v.well} weight={2}/>
      <P d={rect(x - 16, shear, x + 16, CANAL.top)} fill={v.hole} weight={2}/>

      <P d={lamina} fill={v.key}/>
      <P d={rect(x - 14, pinoTop, x + 14, e.fundo)} fill={v.keyPin}/>
      <Camada o={e.espaco}><P d={rect(x - 14, espTop, x + 14, pinoTop)} fill={COR_ESPACADOR[variant]}/></Camada>
      <Camada o={e.driver}>
        <P d={molaV(x, chamberTop + 3, driverTop, 5, 10)} color={v.spring}/>
        <P d={rect(x - 14, driverTop, x + 14, driverBottom)} fill={v.driver}/>
      </Camada>

      <P d={linha} color={v.shear} weight={v.weight + 2} dash="dashed"/>
      <Camada o={e.linha2}>
        <P d={`M${x - 70} ${pinoTop}H${x + 70}`} color={v.shear} weight={3} dash="dashed"/>
        <P d={`M${x - 70} ${espTop}H${x + 70}`} color={v.shear} weight={3} dash="dashed"/>
      </Camada>
      <Camada o={e.juncao}><P d={circulo(x, shear, 12 + 16 * e.juncao)} color={v.shear} weight={4}/></Camada>
      <Camada o={e.seta}><P d="M1112.5 392.4A55 55 0 1 1 1049.6 482.1M1054.8 495.1L1049.6 482.1L1063.3 485" color={v.shear} weight={4}/></Camada>
      <Camada o={e.setaCortada}><P d="M1070 478L1100 508M1100 478L1070 508" color={v.alerta} weight={5}/></Camada>

      <svg width={W} height={H} style={layer}>
        <g opacity={e.rotulo}>
          <text x={CASA.x0 + 16} y={shear - 12} fontFamily="DejaVu Sans, sans-serif" fontSize={22} fontWeight={600} fill={v.text}>Linha de corte</text>
        </g>
        <g opacity={e.rotuloEsp}>
          <path d={`M${x + 18} ${(pinoTop + espTop) / 2}H${x + 56}`} stroke={v.text} strokeWidth={2}/>
          <text x={x + 62} y={(pinoTop + espTop) / 2 + 7} fontFamily="DejaVu Sans, sans-serif" fontSize={22} fontWeight={600} fill={v.text}>Espaçador</text>
        </g>
        <text x={40} y={H - 22} fontFamily="DejaVu Sans, sans-serif" fontSize={15} fontWeight={600} fill={v.muted}>{LEGENDA_DE_ESTUDO ? legenda : ''}</text>
      </svg>
    </div>
  );
}
