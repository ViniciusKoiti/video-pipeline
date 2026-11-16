// Came e bloco "Mecanismo da trava" sobre a vista lateral (S14 do mec-fechadura-pt): o eixo sai da ponta de trás do rotor, a alavanca do came gira
// com a chave e toca o bloco. Camada que vai por cima de `Desenho` (index.tsx), dentro do mesmo StyleProvider. Quadros parados.
import React from 'react';
import {DrawPath} from '@viniciuskoitin/motion-kit/styles';
import {PALETAS} from './paleta';
import type {Variante} from './paleta';
import {HOUSING} from './geometria';
import {ALAVANCA, BLOCO} from './linhaDoTempoCadeado';
import type {EstadoCame} from './linhaDoTempoCadeado';
import {arcoComSeta} from './util';

const W = 1280;
const H = 720;
const layer: React.CSSProperties = {position: 'absolute', inset: 0};
const rect = (x0: number, y0: number, x1: number, y1: number) => `M${x0} ${y0}H${x1}V${y1}H${x0}Z`;
const circulo = (cx: number, cy: number, r: number) => `M${cx - r} ${cy}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`;
const Camada = ({o, children}: {o: number; children: React.ReactNode}) => (o <= 0.001 ? null : <div style={{...layer, opacity: o}}>{children}</div>);

/** Centro da argola da chave com a chave inteira (geometria.ts: ponta em TIP_IN = 990, haste 100 px, argola 55 px além). */
const ARGOLA = {x: 145, y: 443.5} as const;

export function CameLateral({variant, e}: {variant: Variante; e: EstadoCame}) {
  const v = PALETAS[variant];
  let seed = 400;
  const P = ({d, fill, weight, color, dash}: {d: string; fill?: string; weight?: number; color?: string; dash?: 'solid' | 'dashed'}) => (
    <DrawPath d={d} width={W} height={H} at={0} duration={0} color={color ?? v.ink} strokeWidth={weight ?? v.weight} fill={fill}
      wobble={v.wobble} passes={v.passes} boilEvery={v.boil} seed={seed++} dash={dash} style={layer}/>
  );
  const Texto = ({x, y, children, anchor = 'middle', size = 20}: {x: number; y: number; children: React.ReactNode; anchor?: 'start' | 'middle' | 'end'; size?: number}) => (
    <text x={x} y={y} textAnchor={anchor} fontFamily="DejaVu Sans, sans-serif" fontSize={size} fontWeight={600} fill={v.text}>{children}</text>
  );
  const {pivoX: px, pivoY: py, comprimento, largura} = ALAVANCA;
  return (
    <>
      <Camada o={e.aparece}>
        <P d={`M${HOUSING.x1} ${py}H${px - 14}`}/>
        <P d={rect(BLOCO.x0, BLOCO.y0, BLOCO.x1, BLOCO.y1)} color={v.muted} dash="dashed"/>
        <div style={{...layer, transform: `rotate(${e.angulo}deg)`, transformOrigin: `${px}px ${py}px`}}>
          <P d={rect(px - largura / 2, py - comprimento, px + largura / 2, py + 8)} fill={v.driver}/>
        </div>
        <P d={circulo(px, py, 16)} fill={v.driver}/>
      </Camada>
      <Camada o={e.contato}><P d={rect(BLOCO.x0, BLOCO.y0, BLOCO.x1, BLOCO.y1)} color={v.shear} weight={5}/></Camada>
      <Camada o={e.setaChave}><P d={arcoComSeta(ARGOLA.x, ARGOLA.y, 82, -80, -5)} color={v.shear} weight={4}/></Camada>
      <svg width={W} height={H} style={layer}>
        <g opacity={e.rotulos.came}><Texto x={px} y={py + 62}>Came</Texto><path d={`M${px} ${py + 20}V${py + 44}`} stroke={v.text} strokeWidth={2}/></g>
        <g opacity={e.rotulos.bloco}><Texto x={(BLOCO.x0 + BLOCO.x1) / 2} y={py - 6} size={18}>Mecanismo</Texto><Texto x={(BLOCO.x0 + BLOCO.x1) / 2} y={py + 18} size={18}>da trava</Texto></g>
        <g opacity={e.rotulos.aciona}><Texto x={(BLOCO.x0 + BLOCO.x1) / 2} y={BLOCO.y1 + 30}>aciona</Texto></g>
      </svg>
    </>
  );
}
