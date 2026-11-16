// Estudo visual do vídeo mec-fechadura-pt: vista em corte do cilindro de pinos (plano-animacao.md, V2.x).
// Piloto isolado: não altera o template compartilhado nem o kit (CLAUDE.md §15). Sem pessoa, sem foto, sem IA realista.
// 1280×720 lógicos; renderize com `--scale=1.5` para 1920×1080.
//  - FechaduraCorteLimpo / FechaduraCorteMao: quadros parados (chave certa inserida), para escolher o traço.
//  - FechaduraClipe: animação S04–S11 no traço limpo, guiada pela voz (linhaDoTempo.ts).
import React from 'react';
import {AbsoluteFill, Composition, registerRoot, useCurrentFrame} from 'remotion';
import {DrawPath, StyleProvider, editorialStyle, pencilSketchStyle} from '@viniciuskoitin/motion-kit/styles';
import {
  BLADE_BOTTOM, BLADE_LEN, BLADE_TOP, CHAMBER_TOP, COLUMNS, H, HOUSING, KEYWAY, PIN_HALF, SHEAR, W, Y_REST,
  bladeProfile, columnsAt, tipX,
} from './geometria';
import {FPS, TOTAL, estadoEm} from './linhaDoTempo';
import type {Estado} from './linhaDoTempo';
import {TOTAL_FRENTE, estadoFrenteEm} from './linhaDoTempoFrente';
import {Frente} from './frente';
import {CameLateral} from './came';
import {Cadeado} from './cadeadoVista';
import {TOTAL_CADEADO, TOTAL_CAME, estadoCadeadoEm, estadoCameEm} from './linhaDoTempoCadeado';
import type {EstadoCame} from './linhaDoTempoCadeado';
import {FUNDOS_ERRADA, TOTAL_ERRADA, estadoErradaEm} from './linhaDoTempoErrada';
import {Tranca} from './trancaVista';
import {Coluna} from './colunaVista';
import {Porta} from './portaVista';
import {Outras} from './variasVista';
import {
  CORTE_S02, FUNDOS_ALTA, TOTAL_S01, TOTAL_S02, TOTAL_S03A, TOTAL_S18A, TOTAL_S19, TOTAL_S20, TOTAL_S21A, TOTAL_S22, TOTAL_S23, TOTAL_S24A, TOTAL_S24B, TOTAL_S25,
  TRACOS_S02, estadoS01, estadoS02, estadoS03A, estadoS18A, estadoS19, estadoS20, estadoS21A, estadoS22, estadoS23, estadoS24A, estadoS24B, estadoS25,
} from './linhaDoTempoResto';
import {TOTAL_TRANCA_S03, TOTAL_TRANCA_S18, estadoTrancaS03, estadoTrancaS18} from './tranca';

import {PALETAS} from './paleta';
import type {Variante} from './paleta';
import {LEGENDA_DE_ESTUDO} from './legenda';

const estilos = (() => {
  const mao = pencilSketchStyle({accent: 'green'});
  return {
    limpo: {...editorialStyle, slug: 'fechadura-limpo', fonts: [],
      theme: {...editorialStyle.theme, bg: PALETAS.limpo.bg, surface: PALETAS.limpo.bg, text: PALETAS.limpo.ink, line: PALETAS.limpo.ink}},
    mao: {...mao, slug: 'fechadura-mao', fonts: [],
      theme: {...mao.theme, bg: PALETAS.mao.bg, surface: PALETAS.mao.bg, text: PALETAS.mao.ink, line: PALETAS.mao.ink}},
  } as const;
})();

const layer: React.CSSProperties = {position: 'absolute', inset: 0};
const rect = (x0: number, y0: number, x1: number, y1: number) => `M${x0} ${y0}H${x1}V${y1}H${x0}Z`;
const circulo = (cx: number, cy: number, r: number, sweep = 0) =>
  `M${cx - r} ${cy}a${r} ${r} 0 1 ${sweep} ${2 * r} 0a${r} ${r} 0 1 ${sweep} ${-2 * r} 0Z`;

/** Mola em ziguezague entre y0 e y1, com `n` voltas. */
function mola(x: number, y0: number, y1: number, n = 6, amp = 10): string {
  const step = (y1 - y0) / n;
  const pts = [`M${x} ${y0}`];
  for (let k = 0; k < n; k++) pts.push(`L${x + (k % 2 === 0 ? amp : -amp)} ${(y0 + (k + 0.5) * step).toFixed(1)}`);
  pts.push(`L${x} ${y1}`);
  return pts.join('');
}

/** A chave como polígono: ponta em `tip`, perfil com os cortes, ombro, haste. A argola vem à parte. */
function chave(tip: number, fundos?: readonly number[]): {corpo: string; cx: number; cy: number} {
  const perfil = bladeProfile(fundos).map(([d, y]) => `L${(tip - d).toFixed(1)} ${y.toFixed(1)}`);
  const haste = tip - BLADE_LEN - 100;
  const corpo = `M${tip} ${BLADE_BOTTOM}L${tip} ${Y_REST}${perfil.slice(1).join('')}L${haste} ${BLADE_TOP}L${haste} ${BLADE_BOTTOM}Z`;
  return {corpo, cx: haste - 55, cy: (BLADE_TOP + BLADE_BOTTOM) / 2};
}

/** Tudo visível, tudo desenhado: o estado dos quadros parados. */
const ESTADO_FINAL = (insert: number): Estado => ({
  cena: 'S11', insert, tipPx: tipX(insert),
  grupos: {colunas: 1, molas: 1, superiores: 1, chavePinos: 1},
  rotulos: {carcaca: 1, rotor: 1, chave: 1, mola: 1, superior: 1, pinoChave: 1, linha: 1},
  linhaAt: 0, linhaBrilho: 0, setaGiro: 0, setaGiroCortada: 0, setaForca: 0,
  pulsos: {furos: [0, 0, 0, 0, 0], chavePinos: [0, 0, 0, 0, 0], superiores: [0, 0, 0, 0, 0], juncoes: [0, 0, 0, 0, 0]},
});

const Camada = ({o, children}: {o: number; children: React.ReactNode}) => (o <= 0.001 ? null : <div style={{...layer, opacity: o}}>{children}</div>);

export type GrupoExplosao = 'topo' | 'rotor' | 'base' | 'molas' | 'superiores' | 'chavePinos' | 'chave';
/** Deslocamento de cada grupo de peças na vista explodida (S25), em px. */
export type Explosao = Record<GrupoExplosao, {dx: number; dy: number}>;

/** `fundos`: cortes de outra chave (S17); `alerta[i]` (0..1): contorno vermelho no pino da coluna i que cruza a linha de corte;
 *  `explodir`: afasta cada grupo de peças (S25). */
export function Desenho({variant, e, anima, mostrarCame, legenda, fundos, alerta, explodir, semLinha, destaqueChave}: {
  variant: Variante; e: Estado; anima: boolean; mostrarCame: boolean; legenda: string; fundos?: readonly number[]; alerta?: readonly number[];
  explodir?: Explosao; semLinha?: boolean; destaqueChave?: number;
}) {
  const v = PALETAS[variant];
  let seed = 1;
  // `at` e `dur` só valem na animação: o traço se desenha uma vez; nos quadros parados, já está desenhado.
  const P = ({d, fill, weight, color, dash, at = 0, dur = 0}: {
    d: string; fill?: string; weight?: number; color?: string; dash?: 'solid' | 'dashed'; at?: number; dur?: number;
  }) => (
    <DrawPath d={d} width={W} height={H} at={anima ? at : 0} duration={anima ? dur : 0} color={color ?? v.ink} strokeWidth={weight ?? v.weight}
      fill={fill} wobble={v.wobble} passes={v.passes} boilEvery={v.boil} seed={seed++} dash={dash} style={layer}/>
  );
  const Texto = ({x, y, children, anchor = 'start', size = 22, color = v.text}: {
    x: number; y: number; children: React.ReactNode; anchor?: 'start' | 'middle' | 'end'; size?: number; color?: string;
  }) => <text x={x} y={y} textAnchor={anchor} fontFamily="DejaVu Sans, sans-serif" fontSize={size} fontWeight={600} fill={color}>{children}</text>;

  const G = ({g, children}: {g: GrupoExplosao; children: React.ReactNode}) => (explodir
    ? <div style={{...layer, transform: `translate(${explodir[g].dx}px, ${explodir[g].dy}px)`}}>{children}</div>
    : <>{children}</>);
  const colunas = columnsAt(e.insert, fundos);
  const k = chave(e.tipPx, fundos);
  const cam = {x: HOUSING.x1 + 35, y: 440};
  const colAt = (i: number) => 45 + 14 * i; // as colunas se desenham da esquerda para a direita (S04)
  const linha = `M${HOUSING.x0 - 20} ${SHEAR}H${HOUSING.x1 + 10}`;

  return (
    <StyleProvider style={estilos[variant]}>
      <AbsoluteFill style={{backgroundColor: v.bg}}>
        {v.grain && <svg width={W} height={H} style={{...layer, opacity: 0.13}}>
          {Array.from({length: 700}, (_, i) => <circle key={i} cx={(i * 173 + 17) % W} cy={(i * 97 + 23) % H} r={i % 3 ? 0.5 : 1} fill="#9e8e73"/>)}
        </svg>}

        {/* carcaça: lajes de cima e de baixo; rotor; canal da chave */}
        <G g="topo"><P d={rect(HOUSING.x0, HOUSING.top, HOUSING.x1, SHEAR)} fill={v.housing} dur={40}/></G>
        <G g="base"><P d={rect(HOUSING.x0, HOUSING.bottom, HOUSING.x1, HOUSING.bottomEnd)} fill={v.housing} dur={40}/></G>
        <G g="rotor">
          <P d={rect(HOUSING.x0, SHEAR, HOUSING.x1, HOUSING.bottom)} fill={v.plug} at={6} dur={40}/>
          <P d={rect(HOUSING.x0, KEYWAY.top, HOUSING.x1, KEYWAY.bottom)} fill={v.keyway} at={12} dur={30}/>
        </G>

        {/* câmaras da carcaça e furos do rotor (grupo "colunas") */}
        <Camada o={e.grupos.colunas}>
          <G g="topo">{COLUMNS.map((x, i) => <P key={`w${x}`} d={rect(x - 20, CHAMBER_TOP, x + 20, SHEAR)} fill={v.well} weight={2} at={colAt(i)} dur={18}/>)}</G>
          <G g="rotor">{COLUMNS.map((x, i) => <P key={`h${x}`} d={rect(x - PIN_HALF - 2, SHEAR, x + PIN_HALF + 2, KEYWAY.top)} fill={v.hole} weight={2} at={colAt(i)} dur={18}/>)}</G>
        </Camada>
        <Camada o={Math.max(...e.pulsos.furos)}>
          {COLUMNS.map((x, i) => <Camada key={`ph${x}`} o={e.pulsos.furos[i]}>
            <P d={rect(x - PIN_HALF - 2, SHEAR, x + PIN_HALF + 2, KEYWAY.top)} color={v.shear} weight={5}/>
          </Camada>)}
        </Camada>

        {/* molas, pinos superiores e pinos de chave: um grupo cada, para o foco */}
        <Camada o={e.grupos.molas}><G g="molas">
          {colunas.map((c, i) => <P key={`s${c.x}`} d={mola(c.x, CHAMBER_TOP + 3, c.driverTop)} color={v.spring} at={colAt(i)} dur={18}/>)}
        </G></Camada>
        <Camada o={e.grupos.superiores}><G g="superiores">
          {colunas.map((c, i) => <P key={`d${c.x}`} d={rect(c.x - PIN_HALF, c.driverTop, c.x + PIN_HALF, c.driverBottom)} fill={v.driver} at={colAt(i)} dur={18}/>)}
        </G></Camada>
        <Camada o={e.grupos.chavePinos}><G g="chavePinos">
          {colunas.map((c, i) => <P key={`k${c.x}`} d={rect(c.x - PIN_HALF, c.keyPinTop, c.x + PIN_HALF, c.keyPinBottom)} fill={v.keyPin} at={colAt(i)} dur={18}/>)}
        </G></Camada>
        {colunas.map((c, i) => (
          <React.Fragment key={`pp${c.x}`}>
            <Camada o={e.pulsos.chavePinos[i]}><P d={rect(c.x - PIN_HALF, c.keyPinTop, c.x + PIN_HALF, c.keyPinBottom)} color={v.shear} weight={5}/></Camada>
            <Camada o={e.pulsos.superiores[i]}><P d={rect(c.x - PIN_HALF, c.driverTop, c.x + PIN_HALF, c.driverBottom)} color={v.alerta} weight={5}/></Camada>
          </React.Fragment>
        ))}
        {/* pino que cruza a linha de corte, em vermelho (S17): o superior que a atravessa ou o de chave que passa dela */}
        {alerta && colunas.map((c, i) => (
          <Camada key={`al${c.x}`} o={alerta[i]}>
            {c.driverStraddles && <P d={rect(c.x - PIN_HALF, c.driverTop, c.x + PIN_HALF, c.driverBottom)} color={v.alerta} weight={5}/>}
            {c.keyPinCrosses && <P d={rect(c.x - PIN_HALF, c.keyPinTop, c.x + PIN_HALF, c.keyPinBottom)} color={v.alerta} weight={5}/>}
          </Camada>
        ))}
        {/* setas de força das molas (S08) */}
        <Camada o={e.setaForca}>
          {COLUMNS.map((x) => <P key={`f${x}`} d={`M${x + 32} 185V235M${x + 26} 227L${x + 32} 235L${x + 38} 227`} color={v.shear} weight={3}/>)}
        </Camada>

        {/* chave: lâmina com os cortes, haste e argola */}
        <G g="chave">
          <P d={k.corpo} fill={v.key}/>
          <P d={circulo(k.cx, k.cy, 58) + circulo(k.cx, k.cy, 22, 1)} fill={v.key}/>
        </G>
        {destaqueChave !== undefined && <Camada o={destaqueChave}><P d={k.corpo} color={v.shear} weight={6}/><P d={circulo(k.cx, k.cy, 58)} color={v.shear} weight={6}/></Camada>}

        {/* linha de corte: se desenha na S09 e acende na S11 */}
        {!semLinha && <P d={linha} color={v.shear} weight={v.weight + 2} dash="dashed" at={anima ? e.linhaAt : 0} dur={40}/>}
        <Camada o={e.linhaBrilho * 0.4}><P d={linha} color={v.shear} weight={v.weight + 9}/></Camada>
        {COLUMNS.map((x, i) => (
          <Camada key={`j${x}`} o={e.pulsos.juncoes[i]}>
            <P d={circulo(x, SHEAR, 12 + 16 * e.pulsos.juncoes[i])} color={v.shear} weight={4}/>
          </Camada>
        ))}

        {/* seta curva do rotor (S05), e o "X" quando ele não gira (S09) */}
        <Camada o={e.setaGiro}>
          <P d="M1112.5 392.4A55 55 0 1 1 1049.6 482.1M1054.8 495.1L1049.6 482.1L1063.3 485" color={v.shear} weight={4}/>
        </Camada>
        <Camada o={e.setaGiroCortada}><P d="M1070 478L1100 508M1100 478L1070 508" color={v.alerta} weight={5}/></Camada>

        {/* came e o bloco "Mecanismo da trava" (só nos quadros parados; entram na S14) */}
        {mostrarCame && <>
          <P d={`M${HOUSING.x1} ${cam.y}H${cam.x - 22}`}/>
          <P d={circulo(cam.x, cam.y, 22)} fill={v.driver}/>
          <P d={`M${cam.x + 24} ${cam.y}H${cam.x + 58}M${cam.x + 50} ${cam.y - 7}L${cam.x + 58} ${cam.y}L${cam.x + 50} ${cam.y + 7}`}/>
          <P d={rect(1100, 385, 1255, 495)} color={v.muted} dash="dashed"/>
        </>}

        {/* rótulos, só com termos das fichas liberadas */}
        <svg width={W} height={H} style={layer}>
          <g opacity={e.rotulos.carcaca}><Texto x={HOUSING.x0 + 20} y={HOUSING.top - 12}>Carcaça</Texto></g>
          <g opacity={e.rotulos.rotor}><Texto x={HOUSING.x0 + 20} y={HOUSING.bottom - 12}>Rotor</Texto></g>
          <g opacity={e.rotulos.linha}><Texto x={HOUSING.x0 - 28} y={SHEAR + 7} anchor="end">Linha de corte</Texto></g>
          <g opacity={e.rotulos.mola}><Texto x={1024} y={196}>Mola</Texto><path d="M903 190H1016" stroke={v.text} strokeWidth={2}/></g>
          <g opacity={e.rotulos.superior}><Texto x={1024} y={268}>Pino superior</Texto><path d="M905 262H1016" stroke={v.text} strokeWidth={2}/></g>
          <g opacity={e.rotulos.pinoChave}><Texto x={1024} y={362}>Pino de chave</Texto><path d="M905 356H1016" stroke={v.text} strokeWidth={2}/></g>
          <g opacity={e.rotulos.chave}><Texto x={anima ? Math.max(k.cx, 145) : k.cx} y={BLADE_BOTTOM + 52} anchor="middle">Chave</Texto></g>
          {mostrarCame && <>
            <Texto x={cam.x} y={cam.y + 52} anchor="middle" size={20}>Came</Texto>
            <Texto x={1177} y={436} anchor="middle" size={18}>Mecanismo</Texto>
            <Texto x={1177} y={460} anchor="middle" size={18}>da trava</Texto>
          </>}
          <Texto x={40} y={H - 22} size={15} color={v.muted}>{LEGENDA_DE_ESTUDO ? legenda : ''}</Texto>
        </svg>
      </AbsoluteFill>
    </StyleProvider>
  );
}

/** Quadro parado: chave certa inserida. */
export function Corte({variant = 'limpo', insert = 1}: {variant?: Variante; insert?: number}) {
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · chave certa inserida · valores ilustrativos, sem narração final`;
  return <Desenho variant={variant} e={ESTADO_FINAL(insert)} anima={false} mostrarCame legenda={legenda}/>;
}

/** Animação S04–S11 no traço escolhido, guiada pela voz. */
export function Clipe({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoEm(Math.min(frame, TOTAL - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena ${e.cena} · valores ilustrativos, sem narração final`;
  return <Desenho variant={variant} e={e} anima mostrarCame={false} legenda={legenda}/>;
}

/** S12 e S13: a vista lateral (estado final da S11) gira 90° para a vista de frente, o rotor gira com a chave e a câmera rotula a pilha. */
export function ClipeFrente({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoFrenteEm(Math.min(frame, TOTAL_FRENTE - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena ${e.cena} · vista de frente · valores ilustrativos, sem narração final`;
  const lateral = {...ESTADO_FINAL(1), linhaBrilho: e.brilho};
  return (
    <StyleProvider style={estilos[variant]}>
      <AbsoluteFill style={{backgroundColor: PALETAS[variant].bg}}>
        {e.lateralScaleX > 0.001 && (
          <div style={{...layer, transform: `scaleX(${e.lateralScaleX})`, transformOrigin: '50% 50%'}}>
            <Desenho variant={variant} e={lateral} anima={false} mostrarCame={false} legenda={legenda}/>
          </div>
        )}
        {e.frenteScaleX > 0.001 && (
          <div style={{...layer, transform: `scaleX(${e.frenteScaleX})`, transformOrigin: '50% 50%'}}>
            <Frente variant={variant} e={e} legenda={legenda}/>
          </div>
        )}
      </AbsoluteFill>
    </StyleProvider>
  );
}

/** Estado final da S11 sem os rótulos dos pinos e da mola (a S14 fala do came; a alavanca em repouso cobriria o "Pino de chave"). */
function cenaCameLateral(soRotor = false): Estado {
  const final = ESTADO_FINAL(1);
  const rotulos = {...final.rotulos, mola: 0, superior: 0, pinoChave: 0, ...(soRotor ? {carcaca: 0, chave: 0} : {})};
  return {...final, linhaBrilho: 0, rotulos};
}

/** Vista lateral no estado final da S11 (chave inteira, rotor livre) com o came e o bloco da trava por cima (S14). */
function CenaCame({variant, e, legenda, soRotor = false}: {variant: Variante; e: EstadoCame; legenda: string; soRotor?: boolean}) {
  return (
    <>
      <Desenho variant={variant} e={cenaCameLateral(soRotor)} anima={false} mostrarCame={false} legenda={legenda}/>
      <CameLateral variant={variant} e={e}/>
    </>
  );
}

/** S14: a vista de frente (fim da S13) gira de volta para a lateral; o came aparece na ponta de trás do rotor, gira com a chave e toca o bloco. */
export function ClipeCame({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoCameEm(Math.min(frame, TOTAL_CAME - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena S14 · valores ilustrativos, sem narração final`;
  const frenteFinal = estadoFrenteEm(TOTAL_FRENTE - 1);
  return (
    <StyleProvider style={estilos[variant]}>
      <AbsoluteFill style={{backgroundColor: PALETAS[variant].bg}}>
        {e.lateralScaleX > 0.001 && (
          <div style={{...layer, transform: `scaleX(${e.lateralScaleX})`, transformOrigin: '50% 50%'}}>
            <CenaCame variant={variant} e={e} legenda={legenda}/>
          </div>
        )}
        {e.frenteScaleX > 0.001 && (
          <div style={{...layer, transform: `scaleX(${e.frenteScaleX})`, transformOrigin: '50% 50%'}}>
            <Frente variant={variant} e={frenteFinal} legenda={legenda}/>
          </div>
        )}
      </AbsoluteFill>
    </StyleProvider>
  );
}

/** S15 e S16: a vista da fechadura (fim da S14) encolhe para o canto; o cadeado em corte mostra trincos, haste e molas; o came os solta. */
export function ClipeCadeado({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoCadeadoEm(Math.min(frame, TOTAL_CADEADO - 1));
  const v = PALETAS[variant];
  const legenda = `Estudo visual · ${v.rotulo} · cena ${e.cena} · cadeado em corte · valores ilustrativos, sem narração final`;
  const fimS14 = estadoCameEm(TOTAL_CAME - 1);
  const s = 1 - (1 - 0.26) * e.encolhe;
  const t = 24 * e.encolhe;
  return (
    <StyleProvider style={estilos[variant]}>
      <AbsoluteFill style={{backgroundColor: v.bg}}>
        <Cadeado variant={variant} e={e} legenda={legenda}/>
        <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, overflow: 'hidden', transformOrigin: '0 0',
          transform: `translate(${t}px, ${t}px) scale(${s})`, boxShadow: e.encolhe > 0 ? `0 0 0 ${3 / s}px ${v.muted}` : 'none'}}>
          <CenaCame variant={variant} e={fimS14} legenda=""/>
        </div>
        <svg width={W} height={H} style={layer}>
          <g opacity={e.encolhe > 0.9 ? 1 : 0}>
            <text x={24} y={24 + H * 0.26 + 24} fontFamily="DejaVu Sans, sans-serif" fontSize={18} fontWeight={600} fill={v.muted}>Fechadura (vista em corte)</text>
          </g>
        </svg>
      </AbsoluteFill>
    </StyleProvider>
  );
}

/** S17: a chave errada entra, os pinos não se alinham na linha de corte (os que a cruzam em vermelho) e o rotor fica bloqueado. */
export function ClipeErrada({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const {estado, alerta} = estadoErradaEm(Math.min(frame, TOTAL_ERRADA - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena S17 · chave errada · valores ilustrativos, sem narração final`;
  return <Desenho variant={variant} e={estado} anima={false} mostrarCame={false} legenda={legenda} fundos={FUNDOS_ERRADA} alerta={alerta}/>;
}

/** S03 (plano V1): o esquema da tranca egípcia se desenha em traço de lápis. */
export function ClipeTrancaS03() {
  const frame = useCurrentFrame();
  const e = estadoTrancaS03(Math.min(frame, TOTAL_TRANCA_S03 - 1));
  return (
    <StyleProvider style={estilos.mao}>
      <Tranca e={e} anima legenda="Estudo visual · traço de lápis · cena S03, plano V1 · valores ilustrativos, sem narração final"/>
    </StyleProvider>
  );
}

/** S18 (reprise do V1): a chave levanta os pinos até a altura certa e a tranca se solta; o rótulo diz que ela não confere se sobe demais. */
export function ClipeTrancaS18() {
  const frame = useCurrentFrame();
  const e = estadoTrancaS18(Math.min(frame, TOTAL_TRANCA_S18 - 1));
  return (
    <StyleProvider style={estilos.mao}>
      <Tranca e={e} anima={false} legenda="Estudo visual · traço de lápis · cena S18, reprise do V1 · valores ilustrativos, sem narração final"/>
    </StyleProvider>
  );
}

/** S03, 1.ª parte: a vista em corte completa e em repouso; as cinco colunas se desenham uma a uma, sem rótulos. */
export function ClipeS03Colunas({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoS03A(Math.min(frame, TOTAL_S03A - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena S03, plano V2.1 · valores ilustrativos, sem narração final`;
  return <Desenho variant={variant} e={e} anima mostrarCame={false} legenda={legenda}/>;
}

/** S18, 1.ª parte: uma chave com cortes rasos demais levanta as colunas além da altura certa; o rotor segue bloqueado; a tela não diz qual pino trava. */
export function ClipeS18Alta({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const {estado, alerta} = estadoS18A(Math.min(frame, TOTAL_S18A - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena S18, plano V3.1 · corte alto demais · valores ilustrativos, sem narração final`;
  return <Desenho variant={variant} e={estado} anima={false} mostrarCame={false} legenda={legenda} fundos={FUNDOS_ALTA} alerta={alerta}/>;
}

/** S19: a tranca egípcia (um pino por posição) à esquerda; à direita a coluna ganha o segundo pino e, com a chave alta demais, trava o rotor. */
export function ClipeS19({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoS19(Math.min(frame, TOTAL_S19 - 1));
  const v = PALETAS[variant];
  const tranca = estadoTrancaS03(TOTAL_TRANCA_S03 - 1);
  const s = 0.46;
  const legenda = `Estudo visual · ${v.rotulo} · cena S19 · valores ilustrativos, sem narração final`;
  return (
    <StyleProvider style={estilos[variant]}>
      <AbsoluteFill style={{backgroundColor: v.bg}}>
        <Coluna variant={variant} e={e} legenda={legenda}/>
        <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, overflow: 'hidden', transformOrigin: '0 0',
          transform: `translate(24px, 170px) scale(${s})`, boxShadow: `0 0 0 ${3 / s}px ${v.muted}`}}>
          <Tranca e={tranca} anima={false} legenda=""/>
        </div>
        <svg width={W} height={H} style={{position: 'absolute', inset: 0}}>
          <text x={24} y={170 + H * s + 28} fontFamily="DejaVu Sans, sans-serif" fontSize={20} fontWeight={600} fill={v.muted}>Egito: um pino por posição</text>
        </svg>
      </AbsoluteFill>
    </StyleProvider>
  );
}

/** S20: a chave sai (ou nunca entrou) e as molas empurram os pinos superiores de volta para dentro dos furos do rotor. */
export function ClipeS20({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoS20(Math.min(frame, TOTAL_S20 - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena S20 · valores ilustrativos, sem narração final`;
  return <Desenho variant={variant} e={e} anima={false} mostrarCame={false} legenda={legenda}/>;
}

/** Porta trancada e duas chaves (V0). `reprise`: a da S24 (a errada entra e para, a certa entra, gira e o trinco recolhe). */
export function ClipePorta({variant = 'limpo', reprise = false}: {variant?: Variante; reprise?: boolean}) {
  const frame = useCurrentFrame();
  const total = reprise ? TOTAL_S24A : TOTAL_S01;
  const e = (reprise ? estadoS24A : estadoS01)(Math.min(frame, total - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena ${reprise ? 'S24, reprise do V0' : 'S01, V0'} · valores ilustrativos, sem narração final`;
  return (
    <StyleProvider style={estilos[variant]}>
      <Porta variant={variant} e={e} legenda={legenda}/>
    </StyleProvider>
  );
}

/** S22: a vista em corte encolhe para o canto; abrem-se a tubular (canal redondo) e a dimple (cortes na lateral). */
export function ClipeS22({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoS22(Math.min(frame, TOTAL_S22 - 1));
  const v = PALETAS[variant];
  const s = 1 - (1 - 0.3) * e.encolhe;
  const legenda = `Estudo visual · ${v.rotulo} · cena S22 · valores ilustrativos, sem narração final`;
  return (
    <StyleProvider style={estilos[variant]}>
      <AbsoluteFill style={{backgroundColor: v.bg}}>
        <Outras variant={variant} e={e}/>
        <div style={{position: 'absolute', left: 0, top: 0, width: W, height: H, overflow: 'hidden', transformOrigin: '0 0',
          transform: `translate(${24 * e.encolhe}px, ${248 * e.encolhe}px) scale(${s})`, boxShadow: e.encolhe > 0 ? `0 0 0 ${3 / s}px ${v.muted}` : 'none'}}>
          <Desenho variant={variant} e={estadoS03A(0)} anima={false} mostrarCame={false} legenda=""/>
        </div>
        <svg width={W} height={H} style={layer}>
          <text x={40} y={H - 22} fontFamily="DejaVu Sans, sans-serif" fontSize={15} fontWeight={600} fill={v.muted}>{LEGENDA_DE_ESTUDO ? legenda : ''}</text>
        </svg>
      </AbsoluteFill>
    </StyleProvider>
  );
}

/** S23: a chave mestra: o espaçador entra entre os dois pinos, a coluna passa a ter duas linhas de corte e duas chaves a abrem. */
export function ClipeS23({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoS23(Math.min(frame, TOTAL_S23 - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena S23 · valores ilustrativos, sem narração final`;
  return (
    <StyleProvider style={estilos[variant]}>
      <Coluna variant={variant} e={e} legenda={legenda}/>
    </StyleProvider>
  );
}

/** S24, 2.ª parte (V2.17): a vista em corte com a chave certa; o rotor gira, o came gira junto e toca o bloco da trava. */
export function ClipeS24B({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoS24B(Math.min(frame, TOTAL_S24B - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena S24, V2.17 · valores ilustrativos, sem narração final`;
  return (
    <StyleProvider style={estilos[variant]}>
      <AbsoluteFill style={{backgroundColor: PALETAS[variant].bg}}>
        <CenaCame variant={variant} e={e} legenda={legenda} soRotor/>
      </AbsoluteFill>
    </StyleProvider>
  );
}

/** S25: a vista em corte em repouso se desmonta em peças que flutuam (vista explodida), sem rótulos; reduzida para caber no quadro. */
export function ClipeS25({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const {estado, explosao} = estadoS25(Math.min(frame, TOTAL_S25 - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena S25 · valores ilustrativos, sem narração final`;
  return (
    <StyleProvider style={estilos[variant]}>
      <AbsoluteFill style={{backgroundColor: PALETAS[variant].bg}}>
        <div style={{...layer, transformOrigin: '640px 395px', transform: 'scale(0.72)'}}>
          <Desenho variant={variant} e={estado} anima={false} mostrarCame={false} legenda="" explodir={explosao} semLinha/>
        </div>
        <svg width={W} height={H} style={layer}>
          <text x={40} y={H - 22} fontFamily="DejaVu Sans, sans-serif" fontSize={15} fontWeight={600} fill={PALETAS[variant].muted}>{LEGENDA_DE_ESTUDO ? legenda : ''}</text>
        </svg>
      </AbsoluteFill>
    </StyleProvider>
  );
}

/** S21, V2.16: a vista em corte de volta, em repouso, com a chave inteira em destaque, sem rótulos. */
export function ClipeS21A({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const {estado, destaque} = estadoS21A(Math.min(frame, TOTAL_S21A - 1));
  const legenda = `Estudo visual · ${PALETAS[variant].rotulo} · cena S21, V2.16 · valores ilustrativos, sem narração final`;
  return <Desenho variant={variant} e={estado} anima={false} mostrarCame={false} legenda={legenda} semLinha destaqueChave={destaque}/>;
}

/** S02: o contorno de uma fechadura se desenha em traço; a linha de corte o percorre e, atrás dela, aparece a vista em corte (sem rótulos). */
export function ClipeS02({variant = 'limpo'}: {variant?: Variante}) {
  const frame = useCurrentFrame();
  const e = estadoS02(Math.min(frame, TOTAL_S02 - 1));
  const v = PALETAS[variant];
  const T = TRACOS_S02;
  const xCorte = CORTE_S02.x0 + (CORTE_S02.x1 - CORTE_S02.x0) * e.corte;
  const legenda = `Estudo visual · ${v.rotulo} · cena S02, V2.0 e V2.0b · valores ilustrativos, sem narração final`;
  const P = ({d, at, dur, weight, color, dash}: {d: string; at: number; dur: number; weight?: number; color?: string; dash?: 'solid' | 'dashed'}) => (
    <DrawPath d={d} width={W} height={H} at={at} duration={dur} color={color ?? v.ink} strokeWidth={weight ?? v.weight} wobble={v.wobble} passes={v.passes}
      boilEvery={v.boil} seed={900 + at} dash={dash} style={layer}/>
  );
  return (
    <StyleProvider style={estilos[variant]}>
      <AbsoluteFill style={{backgroundColor: v.bg}}>
        {/* contorno exterior: carcaça, entrada da chave à esquerda e eixo à direita, só em traço */}
        <P d={rect(HOUSING.x0, HOUSING.top, HOUSING.x1, HOUSING.bottomEnd)} at={T.corpo.at} dur={T.corpo.dur}/>
        <P d={`M${HOUSING.x0} ${KEYWAY.top}H${HOUSING.x0 + 46}V${KEYWAY.bottom}H${HOUSING.x0}`} at={T.canal.at} dur={T.canal.dur}/>
        <P d={`M${HOUSING.x1} 440H${HOUSING.x1 + 70}`} at={T.eixo.at} dur={T.eixo.dur}/>
        {/* vista em corte, revelada da esquerda para a direita atrás da linha de corte */}
        {e.corte > 0 && (
          <div style={{...layer, clipPath: `inset(0 ${((W - xCorte) / W) * 100}% 0 0)`}}>
            <Desenho variant={variant} e={estadoS03A(0)} anima={false} mostrarCame={false} legenda="" semLinha/>
          </div>
        )}
        {e.linha > 0.001 && (
          <div style={{...layer, opacity: e.linha}}><P d={`M${xCorte} ${HOUSING.top - 30}V${HOUSING.bottomEnd + 30}`} at={0} dur={0} color={v.shear} weight={v.weight + 1} dash="dashed"/></div>
        )}
        <svg width={W} height={H} style={layer}>
          <text x={40} y={H - 22} fontFamily="DejaVu Sans, sans-serif" fontSize={15} fontWeight={600} fill={v.muted}>{LEGENDA_DE_ESTUDO ? legenda : ''}</text>
        </svg>
      </AbsoluteFill>
    </StyleProvider>
  );
}

registerRoot(() => (
  <>
    <Composition id="FechaduraS02" component={ClipeS02} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S02} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraS21A" component={ClipeS21A} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S21A} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraS22" component={ClipeS22} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S22} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraS23" component={ClipeS23} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S23} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraS24B" component={ClipeS24B} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S24B} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraS25" component={ClipeS25} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S25} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraS03Colunas" component={ClipeS03Colunas} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S03A} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraS18Alta" component={ClipeS18Alta} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S18A} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraS19" component={ClipeS19} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S19} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraS20" component={ClipeS20} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_S20} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraPortaS01" component={ClipePorta} defaultProps={{variant: 'limpo' as Variante, reprise: false}}
      durationInFrames={TOTAL_S01} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraPortaS24" component={ClipePorta} defaultProps={{variant: 'limpo' as Variante, reprise: true}}
      durationInFrames={TOTAL_S24A} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraClipeErrada" component={ClipeErrada} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_ERRADA} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraTrancaS03" component={ClipeTrancaS03} durationInFrames={TOTAL_TRANCA_S03} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraTrancaS18" component={ClipeTrancaS18} durationInFrames={TOTAL_TRANCA_S18} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraClipeCame" component={ClipeCame} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_CAME} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraClipeCadeado" component={ClipeCadeado} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_CADEADO} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraClipeFrente" component={ClipeFrente} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL_FRENTE} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraCorteLimpo" component={Corte} defaultProps={{variant: 'limpo' as Variante, insert: 1}}
      durationInFrames={1} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraCorteMao" component={Corte} defaultProps={{variant: 'mao' as Variante, insert: 1}}
      durationInFrames={1} fps={FPS} width={W} height={H}/>
    <Composition id="FechaduraClipe" component={Clipe} defaultProps={{variant: 'limpo' as Variante}}
      durationInFrames={TOTAL} fps={FPS} width={W} height={H}/>
  </>
));
