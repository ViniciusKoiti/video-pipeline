// Vista de frente (corte transversal) da fechadura de pinos: um círculo dentro de outro, a pilha às 12 horas (S12 e S13 do mec-fechadura-pt).
// Precisa estar dentro de um StyleProvider do kit (quem monta a composição fornece). Quadros parados, sem animação de traço.
import React from 'react';
import {DrawPath} from '@viniciuskoitin/motion-kit/styles';
import {PALETAS} from './paleta';
import type {Variante} from './paleta';
import {
  BLADE, CX, CY, HOLE_HALF, KEYWAY, PIN_HALF, R_HOUSING, R_PLUG, SHEAR_Y, WELL_HALF, WELL_TOP, pilha,
} from './vistaFrente';
import type {EstadoFrente} from './linhaDoTempoFrente';
import {arcoComSeta} from './util';
import {LEGENDA_DE_ESTUDO} from './legenda';

const W = 1280;
const H = 720;
const layer: React.CSSProperties = {position: 'absolute', inset: 0};
const rect = (x0: number, y0: number, x1: number, y1: number) => `M${x0} ${y0}H${x1}V${y1}H${x0}Z`;
const circulo = (cx: number, cy: number, r: number) => `M${cx - r} ${cy}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`;

function mola(x: number, y0: number, y1: number, n = 5, amp = 10): string {
  const step = (y1 - y0) / n;
  const pts = [`M${x} ${y0}`];
  for (let k = 0; k < n; k++) pts.push(`L${x + (k % 2 === 0 ? amp : -amp)} ${(y0 + (k + 0.5) * step).toFixed(1)}`);
  pts.push(`L${x} ${y1}`);
  return pts.join('');
}

const Camada = ({o, children}: {o: number; children: React.ReactNode}) => (o <= 0.001 ? null : <div style={{...layer, opacity: o}}>{children}</div>);

export function Frente({variant, e, legenda}: {variant: Variante; e: EstadoFrente; legenda: string}) {
  const v = PALETAS[variant];
  let seed = 100;
  const P = ({d, fill, weight, color, dash}: {d: string; fill?: string; weight?: number; color?: string; dash?: 'solid' | 'dashed'}) => (
    <DrawPath d={d} width={W} height={H} at={0} duration={0} color={color ?? v.ink} strokeWidth={weight ?? v.weight} fill={fill}
      wobble={v.wobble} passes={v.passes} boilEvery={v.boil} seed={seed++} dash={dash} style={layer}/>
  );
  const Texto = ({x, y, children, anchor = 'start', size = 22}: {x: number; y: number; children: React.ReactNode; anchor?: 'start' | 'middle' | 'end'; size?: number}) => (
    <text x={x} y={y} textAnchor={anchor} fontFamily="DejaVu Sans, sans-serif" fontSize={size} fontWeight={600} fill={v.text}>{children}</text>
  );
  const p = pilha();
  const c = e.camera;
  const camera = `translate(${W / 2}px, ${H / 2}px) scale(${c.scale}) translate(${-c.cx}px, ${-c.cy}px)`;
  const pinoChave = rect(CX - PIN_HALF, p.keyPinTop, CX + PIN_HALF, p.keyPinBottom);
  const pinoSuperior = rect(CX - PIN_HALF, p.driverTop, CX + PIN_HALF, p.driverBottom);
  const molaD = mola(CX, WELL_TOP + 3, p.driverTop);

  return (
    <div style={{...layer, backgroundColor: v.bg}}>
      <div style={{...layer, transform: camera, transformOrigin: '0 0'}}>
        {/* carcaça fixa, com a câmara das 12 horas */}
        <P d={circulo(CX, CY, R_HOUSING)} fill={v.housing}/>
        <P d={rect(CX - WELL_HALF, WELL_TOP, CX + WELL_HALF, SHEAR_Y)} fill={v.well} weight={2}/>

        {/* rotor, com a chave e o pino de chave dentro: tudo gira junto */}
        <div style={{...layer, transform: `rotate(${e.angulo}deg)`, transformOrigin: `${CX}px ${CY}px`}}>
          <P d={circulo(CX, CY, R_PLUG)} fill={v.plug}/>
          <P d={rect(CX - HOLE_HALF, SHEAR_Y, CX + HOLE_HALF, KEYWAY.top)} fill={v.hole} weight={2}/>
          <P d={rect(CX - KEYWAY.half, KEYWAY.top, CX + KEYWAY.half, KEYWAY.bottom)} fill={v.keyway} weight={2}/>
          <P d={rect(CX - BLADE.half, BLADE.top, CX + BLADE.half, BLADE.bottom)} fill={v.key}/>
          <P d={pinoChave} fill={v.keyPin}/>
          <Camada o={e.pulsos.pinoChave}><P d={pinoChave} color={v.shear} weight={5}/></Camada>
        </div>

        {/* pino superior e mola ficam na câmara da carcaça, parados */}
        <P d={molaD} color={v.spring}/>
        <P d={pinoSuperior} fill={v.driver}/>
        <Camada o={e.pulsos.superior}><P d={pinoSuperior} color={v.alerta} weight={5}/></Camada>
        <Camada o={e.pulsos.mola}><P d={molaD} color={v.shear} weight={5}/></Camada>
        <Camada o={e.pulsos.camara}><P d={rect(CX - WELL_HALF, WELL_TOP, CX + WELL_HALF, SHEAR_Y)} color={v.shear} weight={5}/></Camada>

        {/* linha de corte: a borda do rotor */}
        <P d={circulo(CX, CY, R_PLUG)} color={v.shear} weight={v.weight + 2} dash="dashed"/>

        {/* seta curva: o rotor gira com a chave */}
        <Camada o={e.setaGiro}><P d={arcoComSeta(CX, CY, R_PLUG + 55, -68, 18)} color={v.shear} weight={4}/></Camada>

        {/* rótulos, só com termos das fichas liberadas */}
        <svg width={W} height={H} style={layer}>
          <g opacity={e.rotulos.carcaca}><Texto x={300} y={CY - 150} anchor="end">Carcaça</Texto><path d={`M308 ${CY - 155}L${CX - 170} ${CY - 138}`} stroke={v.text} strokeWidth={2}/></g>
          <g opacity={e.rotulos.rotor}><Texto x={300} y={CY + 170} anchor="end">Rotor</Texto><path d={`M308 ${CY + 165}L${CX - 100} ${CY + 60}`} stroke={v.text} strokeWidth={2}/></g>
          <g opacity={e.rotulos.linha}><Texto x={985} y={CY - 100}>Linha de corte</Texto><path d={`M978 ${CY - 105}L${CX + 130} ${CY - 75}`} stroke={v.text} strokeWidth={2}/></g>
          <g opacity={e.rotulos.chave}><Texto x={CX} y={KEYWAY.bottom + 100} anchor="middle">Chave</Texto><path d={`M${CX} ${KEYWAY.bottom + 62}V${KEYWAY.bottom + 2}`} stroke={v.text} strokeWidth={2}/></g>
          <g opacity={e.rotulos.pinoChave}><Texto x={985} y={CY + 70}>Pino de chave</Texto><path d={`M978 ${CY + 65}L${CX + 112} ${CY + 5}`} stroke={v.text} strokeWidth={2}/></g>
          <g opacity={e.rotulos.superior}><Texto x={560} y={CY - 200} anchor="end">Pino superior</Texto><path d={`M568 ${CY - 205}L${CX - PIN_HALF - 2} ${CY - 205}`} stroke={v.text} strokeWidth={2}/></g>
          <g opacity={e.rotulos.mola}><Texto x={720} y={CY - 250}>Mola</Texto><path d={`M712 ${CY - 254}L${CX + 12} ${CY - 225}`} stroke={v.text} strokeWidth={2}/></g>
        </svg>
      </div>
      <svg width={W} height={H} style={layer}>
        <text x={40} y={H - 22} fontFamily="DejaVu Sans, sans-serif" fontSize={15} fontWeight={600} fill={v.muted}>{LEGENDA_DE_ESTUDO ? legenda : ''}</text>
      </svg>
    </div>
  );
}
