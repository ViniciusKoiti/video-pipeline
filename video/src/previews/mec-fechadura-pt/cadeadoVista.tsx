// Vista em corte do cadeado (S15 e S16 do mec-fechadura-pt): rotor com came, dois trincos com mola e braço, haste com dois entalhes e a mola sob a
// ponta mais longa. Precisa estar dentro de um StyleProvider do kit. Quadros parados; a cinemática está em cadeado.ts.
import React from 'react';
import {DrawPath} from '@viniciuskoitin/motion-kit/styles';
import {PALETAS} from './paleta';
import type {Variante} from './paleta';
import {
  BODY, CAM, CAM_A, CAM_B, LATCH_H, LATCH_Y_DOWN, LATCH_Y_UP, LEG_L, NOTCH_DEPTH, PLUG_R, X_INNER, X_WALL,
  bracoCima, espelho, hasteCaminho, trincoCima,
} from './cadeado';
import type {EstadoCadeado} from './linhaDoTempoCadeado';
import {molaH, molaV, poligono} from './util';
import {LEGENDA_DE_ESTUDO} from './legenda';

const W = 1280;
const H = 720;
const layer: React.CSSProperties = {position: 'absolute', inset: 0};
const rect = (x0: number, y0: number, x1: number, y1: number) => `M${x0} ${y0}H${x1}V${y1}H${x0}Z`;
const circulo = (cx: number, cy: number, r: number) => `M${cx - r} ${cy}a${r} ${r} 0 1 0 ${2 * r} 0a${r} ${r} 0 1 0 ${-2 * r} 0Z`;
const espelhar = (pts: ReadonlyArray<readonly [number, number]>): [number, number][] => pts.map(([x, y]) => espelho(x, y));
const Camada = ({o, children}: {o: number; children: React.ReactNode}) => (o <= 0.001 ? null : <div style={{...layer, opacity: o}}>{children}</div>);

/** Stadium do came centrado no eixo, em repouso na horizontal. */
const CAME_D = (() => {
  const c = CAM_A - CAM_B;
  return `M${CAM.x - c} ${CAM.y - CAM_B}H${CAM.x + c}A${CAM_B} ${CAM_B} 0 0 1 ${CAM.x + c} ${CAM.y + CAM_B}H${CAM.x - c}A${CAM_B} ${CAM_B} 0 0 1 ${CAM.x - c} ${CAM.y - CAM_B}Z`;
})();

export function Cadeado({variant, e, legenda}: {variant: Variante; e: EstadoCadeado; legenda: string}) {
  const v = PALETAS[variant];
  let seed = 200;
  const P = ({d, fill, weight, color, dash}: {d: string; fill?: string; weight?: number; color?: string; dash?: 'solid' | 'dashed'}) => (
    <DrawPath d={d} width={W} height={H} at={0} duration={0} color={color ?? v.ink} strokeWidth={weight ?? v.weight} fill={fill}
      wobble={v.wobble} passes={v.passes} boilEvery={v.boil} seed={seed++} dash={dash} style={layer}/>
  );
  const Texto = ({x, y, children, anchor = 'start', size = 22}: {x: number; y: number; children: React.ReactNode; anchor?: 'start' | 'middle' | 'end'; size?: number}) => (
    <text x={x} y={y} textAnchor={anchor} fontFamily="DejaVu Sans, sans-serif" fontSize={size} fontWeight={600} fill={v.text}>{children}</text>
  );
  const r = e.retracao;
  const trincoC = poligono(trincoCima(r));
  const trincoB = poligono(espelhar(trincoCima(r)));
  const bracoC = poligono(bracoCima(r));
  const bracoB = poligono(espelhar(bracoCima(r)));
  const molaC = molaH(LATCH_Y_UP, X_INNER + r, X_WALL);
  const molaB = molaH(LATCH_Y_DOWN, 2 * CAM.x - X_WALL, 2 * CAM.x - (X_INNER + r));
  const paredeC = rect(X_WALL, LATCH_Y_UP - 24, X_WALL + 20, LATCH_Y_UP + 24);
  const paredeB = rect(2 * CAM.x - X_WALL - 20, LATCH_Y_DOWN - 24, 2 * CAM.x - X_WALL, LATCH_Y_DOWN + 24);
  const molaHaste = molaV((LEG_L.x0 + LEG_L.x1) / 2, LEG_L.bottom - e.haste, BODY.y1 - 5, 5, 10);

  return (
    <div style={{...layer, backgroundColor: v.bg}}>
      {v.grain && <svg width={W} height={H} style={{...layer, opacity: 0.13}}>
        {Array.from({length: 700}, (_, i) => <circle key={i} cx={(i * 173 + 17) % W} cy={(i * 97 + 23) % H} r={i % 3 ? 0.5 : 1} fill="#9e8e73"/>)}
      </svg>}

      {/* corpo (corte), com as paredes onde as molas dos trincos se apoiam */}
      <P d={rect(BODY.x0, BODY.y0, BODY.x1, BODY.y1)} fill={v.housing}/>
      <P d={paredeC} fill={v.well} weight={2}/>
      <P d={paredeB} fill={v.well} weight={2}/>

      {/* haste: sobe quando a mola a empurra */}
      <P d={hasteCaminho(e.haste)} fill={v.ink}/>
      <P d={molaHaste} color={v.spring}/>
      <Camada o={e.pulsos.molaHaste}><P d={molaHaste} color={v.shear} weight={5}/></Camada>

      {/* trincos, braços e molas (o de baixo é o de cima espelhado pelo eixo do came) */}
      <P d={molaC} color={v.spring}/>
      <P d={molaB} color={v.spring}/>
      <Camada o={e.pulsos.molas}><P d={molaC} color={v.shear} weight={5}/><P d={molaB} color={v.shear} weight={5}/></Camada>
      <P d={trincoC} fill={v.keyPin}/>
      <P d={trincoB} fill={v.keyPin}/>
      <P d={bracoC} fill={v.keyPin}/>
      <P d={bracoB} fill={v.keyPin}/>
      <Camada o={e.pulsos.trincos}><P d={trincoC} color={v.shear} weight={5}/><P d={trincoB} color={v.shear} weight={5}/></Camada>
      <Camada o={e.pulsos.entalhes}>
        <P d={circulo(LEG_L.x1 - NOTCH_DEPTH / 2, LATCH_Y_UP, 26)} color={v.shear} weight={4}/>
        <P d={circulo(espelho(LEG_L.x1 - NOTCH_DEPTH / 2, 0)[0], LATCH_Y_DOWN, 26)} color={v.shear} weight={4}/>
      </Camada>

      {/* rotor (de frente) e came, que giram juntos: a fenda da chave fica perpendicular ao came */}
      <P d={circulo(CAM.x, CAM.y, PLUG_R)} fill={v.plug}/>
      <div style={{...layer, transform: `rotate(${e.phi}deg)`, transformOrigin: `${CAM.x}px ${CAM.y}px`}}>
        <P d={CAME_D} fill={v.driver}/>
        <P d={rect(CAM.x - 5, CAM.y - 14, CAM.x + 5, CAM.y + 14)} fill={v.key} weight={2}/>
      </div>

      {/* rótulos, só com termos das fichas liberadas */}
      <svg width={W} height={H} style={layer}>
        <g opacity={e.rotulos.titulo}><Texto x={1235} y={70} anchor="end" size={30}>No cadeado</Texto></g>
        <g opacity={e.rotulos.came}><Texto x={550} y={446} anchor="end">Came</Texto><path d={`M556 441L${CAM.x - CAM_A - 4} ${CAM.y}`} stroke={v.text} strokeWidth={2}/></g>
        <g opacity={e.rotulos.trincos}>
          <Texto x={CAM.x} y={300} anchor="middle">Trinco</Texto><path d={`M${CAM.x} 308V${LATCH_Y_UP - LATCH_H / 2 - 4}`} stroke={v.text} strokeWidth={2}/>
          <Texto x={CAM.x} y={592} anchor="middle">Trinco</Texto><path d={`M${CAM.x} 562V${LATCH_Y_DOWN + LATCH_H / 2 + 4}`} stroke={v.text} strokeWidth={2}/>
        </g>
        <g opacity={e.rotulos.mola}>
          <Texto x={724} y={318}>Mola</Texto><path d={`M740 326L750 ${LATCH_Y_UP - 11}`} stroke={v.text} strokeWidth={2}/>
          <Texto x={556} y={592} anchor="end">Mola</Texto><path d={`M530 566L530 ${LATCH_Y_DOWN + 11}`} stroke={v.text} strokeWidth={2}/>
        </g>
        <g opacity={e.rotulos.entalhes}>
          <Texto x={370} y={LATCH_Y_UP + 6} anchor="end">Entalhes</Texto><path d={`M376 ${LATCH_Y_UP}L${LEG_L.x1 - NOTCH_DEPTH} ${LATCH_Y_UP}`} stroke={v.text} strokeWidth={2}/>
          <Texto x={906} y={LATCH_Y_DOWN + 6}>Entalhes</Texto><path d={`M900 ${LATCH_Y_DOWN}L${espelho(LEG_L.x1 - NOTCH_DEPTH, 0)[0]} ${LATCH_Y_DOWN}`} stroke={v.text} strokeWidth={2}/>
        </g>
        <g opacity={e.rotulos.haste}><Texto x={370} y={284} anchor="end">Haste</Texto><path d={`M376 280L${LEG_L.x0} 280`} stroke={v.text} strokeWidth={2}/></g>
        <g opacity={e.rotulos.molaHaste}><Texto x={370} y={640} anchor="end">Mola</Texto><path d={`M376 634L${(LEG_L.x0 + LEG_L.x1) / 2 - 12} 630`} stroke={v.text} strokeWidth={2}/></g>
        <text x={40} y={H - 22} fontFamily="DejaVu Sans, sans-serif" fontSize={15} fontWeight={600} fill={v.muted}>{LEGENDA_DE_ESTUDO ? legenda : ''}</text>
      </svg>
    </div>
  );
}
