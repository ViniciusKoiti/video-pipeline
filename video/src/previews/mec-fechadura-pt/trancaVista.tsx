// Tranca egípcia de madeira em corte lateral (S03 e S18 do mec-fechadura-pt): poste, canal, tranca com aberturas, três pinos e a chave em "pente".
// Sempre no traço de lápis sobre papel (paleta `mao`), para separar a história do mecanismo moderno. Dentro de um StyleProvider do kit.
import React from 'react';
import {DrawPath} from '@viniciuskoitin/motion-kit/styles';
import {PALETAS} from './paleta';
import {
  BOLT, CHANNEL, FLOOR_HOLE_HALF, HOLE_XS, KEY_BAR, OPENING_HALF, PEG_HALF, PEG_LEN, PIN_HALF, POST, SHAFT, TRACOS_S03,
  pegTip, pinBottom, pinTop,
} from './tranca';
import type {EstadoTranca} from './tranca';
import {LEGENDA_DE_ESTUDO} from './legenda';

const W = 1280;
const H = 720;
const layer: React.CSSProperties = {position: 'absolute', inset: 0};
const rect = (x0: number, y0: number, x1: number, y1: number) => `M${x0} ${y0}H${x1}V${y1}H${x0}Z`;
const circulo = (cx: number, cy: number, r: number) => `M${cx - r} ${cy}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`;
const Camada = ({o, children}: {o: number; children: React.ReactNode}) => (o <= 0.001 ? null : <div style={{...layer, opacity: o}}>{children}</div>);

const MADEIRA = {poste: '#dcc7a4', canal: '#b79a6c', tranca: '#cfae7e'} as const;

export function Tranca({e, anima, legenda}: {e: EstadoTranca; anima: boolean; legenda: string}) {
  const v = PALETAS.mao;
  let seed = 300;
  const P = ({d, fill, weight, color, at = 0, dur = 0}: {d: string; fill?: string; weight?: number; color?: string; at?: number; dur?: number}) => (
    <DrawPath d={d} width={W} height={H} at={anima ? at : 0} duration={anima ? dur : 0} color={color ?? v.ink} strokeWidth={weight ?? v.weight} fill={fill}
      wobble={v.wobble} passes={v.passes} boilEvery={v.boil} seed={seed++} style={layer}/>
  );
  const Texto = ({x, y, children, anchor = 'start', size = 24}: {x: number; y: number; children: React.ReactNode; anchor?: 'start' | 'middle' | 'end'; size?: number}) => (
    <text x={x} y={y} textAnchor={anchor} fontFamily="DejaVu Sans, sans-serif" fontSize={size} fontWeight={600} fill={v.text}>{children}</text>
  );
  const T = TRACOS_S03;
  const dx = -e.slide; // a tranca recua para a esquerda
  const pegY = pegTip(e.chave);
  const barTop = pegY + PEG_LEN;

  return (
    <div style={{...layer, backgroundColor: v.bg}}>
      <svg width={W} height={H} style={{...layer, opacity: 0.13}}>
        {Array.from({length: 700}, (_, i) => <circle key={i} cx={(i * 173 + 17) % W} cy={(i * 97 + 23) % H} r={i % 3 ? 0.5 : 1} fill="#9e8e73"/>)}
      </svg>

      {/* poste fixo na porta, com o canal da tranca, os poços dos pinos e os furos por onde sobem os pegs */}
      <P d={rect(POST.x0, POST.y0, POST.x1, POST.y1)} fill={MADEIRA.poste} at={T.poste.at} dur={T.poste.dur}/>
      <P d={rect(POST.x0, CHANNEL.y0, POST.x1, CHANNEL.y1)} fill={MADEIRA.canal} weight={2} at={T.canal.at} dur={T.canal.dur}/>
      {HOLE_XS.map((x, i) => (
        <React.Fragment key={`po${x}`}>
          <P d={rect(x - SHAFT.half, SHAFT.top, x + SHAFT.half, CHANNEL.y0)} fill={MADEIRA.canal} weight={2} at={T.canal.at} dur={T.canal.dur}/>
          <P d={rect(x - FLOOR_HOLE_HALF, CHANNEL.y1, x + FLOOR_HOLE_HALF, POST.y1)} fill={MADEIRA.canal} weight={2} at={T.canal.at} dur={T.canal.dur}/>
        </React.Fragment>
      ))}

      {/* tranca horizontal, com uma abertura vertical por pino (acompanha o recuo) */}
      <div style={{...layer, transform: `translateX(${dx}px)`}}>
        <P d={rect(BOLT.x0, BOLT.y0, BOLT.x1, BOLT.y1)} fill={MADEIRA.tranca} at={T.tranca.at} dur={T.tranca.dur}/>
        {HOLE_XS.map((x) => <P key={`ab${x}`} d={rect(x - OPENING_HALF, BOLT.y0, x + OPENING_HALF, BOLT.y1)} fill={MADEIRA.canal} weight={2} at={T.tranca.at + 8} dur={T.tranca.dur}/>)}
      </div>

      {/* pinos: repousam nas bordas dos furos, dentro das aberturas, e sobem quando os pegs da chave os empurram */}
      {HOLE_XS.map((x, i) => (
        <P key={`pi${x}`} d={rect(x - PIN_HALF, pinTop(e.chave), x + PIN_HALF, pinBottom(e.chave))} fill={v.keyPin} at={T.pinos[i].at} dur={T.pinos[i].dur}/>
      ))}

      {/* chave em pente: barra por baixo do poste, pegs subindo pelos furos; só aparece na S18 */}
      <Camada o={e.chaveVisivel}>
        {HOLE_XS.map((x) => <P key={`pg${x}`} d={rect(x - PEG_HALF, pegY, x + PEG_HALF, barTop)} fill={v.key}/>)}
        <P d={rect(KEY_BAR.x0, barTop, KEY_BAR.x1, barTop + KEY_BAR.h)} fill={v.key}/>
        <P d={circulo(KEY_BAR.x0 - 40, barTop + KEY_BAR.h / 2, 30) + circulo(KEY_BAR.x0 - 40, barTop + KEY_BAR.h / 2, 11)} fill={v.key}/>
      </Camada>

      {/* rótulos, só com termos das fichas liberadas */}
      <svg width={W} height={H} style={layer}>
        <g opacity={e.rotulos.poste}><Texto x={POST.x0 + 20} y={POST.y0 - 14}>Poste</Texto></g>
        <g opacity={e.rotulos.tranca}><Texto x={POST.x0 - 20} y={BOLT.y0 - 12} anchor="end">Tranca</Texto></g>
        <g opacity={e.rotulos.pinos}><Texto x={POST.x1 + 36} y={252}>Pinos</Texto><path d={`M${POST.x1 + 28} 247L${HOLE_XS[2] + 18} 247`} stroke={v.text} strokeWidth={2}/></g>
        <g opacity={e.rotulos.chave}><Texto x={KEY_BAR.x0 - 90} y={barTop + KEY_BAR.h / 2 + 8} anchor="end">Chave</Texto></g>
        <g opacity={e.rotulos.naoConfere}><Texto x={W / 2} y={74} anchor="middle" size={28}>não confere se sobe demais</Texto></g>
        <text x={40} y={34} fontFamily="DejaVu Sans, sans-serif" fontSize={15} fontWeight={600} fill={v.muted}>{LEGENDA_DE_ESTUDO ? legenda : ''}</text>
      </svg>
    </div>
  );
}
