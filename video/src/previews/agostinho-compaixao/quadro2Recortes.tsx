import React from 'react';
import {AbsoluteFill, Composition, Easing, Sequence, interpolate, registerRoot, useCurrentFrame} from 'remotion';
import {Host} from '@viniciuskoitin/motion-kit/host';
import {cutoutWalkPose} from '@viniciuskoitin/motion-kit/host/cutout';
import {InkStroke, StyleProvider, pencilSketchStyle} from '@viniciuskoitin/motion-kit/styles';
import {lia, bia} from './personagens';
import {Pagina, PAGINA_FRAMES, RetratoCartao} from './paginaFonteCena';

/**
 * Quadro 2 do estudo (aproximação e mão oferecida) com os recortes de Lia e Bia.
 * 1280 x 720, 30 fps, 8 s, sem áudio. Exemplo fictício; não é roteiro nem narração.
 * A ordem das ações é a do storyboard: Bia chega, para, oferece; só depois Lia responde.
 */

const W = 1280;
const H = 720;
const FPS = 30;
const FRAMES = 240;
const PAPER = '#f5efdf';
const INK = '#332e29';
const SIZE = 400;
const GROUND = 560;
const K = SIZE / 480;
// Com os dois braços em 'point' (156 unidades do centro), os centros ficam a ~347 unidades: as mãos se tocam.
const LIA_X = 520;
const BIA_FINAL_X = LIA_X + Math.round(347 * K);
const BIA_START_X = 1330;
const WALK_FROM = 30;
const WALK_TO = 100;
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

const base = pencilSketchStyle({accent: 'green'});
const style = {
  ...base,
  slug: 'agostinho-compaixao-recortes',
  fonts: [],
  theme: {...base.theme, bg: PAPER, surface: PAPER, text: INK, line: INK, accent: '#6d9d94'},
  line: {...base.line, width: 4.5, wobble: 1.05, boilEvery: 8, passes: 1},
};

function Line({d, at = 0, duration = 25, weight = 4, seed = 3, color = INK}: {d: string; at?: number; duration?: number; weight?: number; seed?: number; color?: string}) {
  return <>{d.split(/(?=M)/).filter(Boolean).map((path, index) => (
    <InkStroke key={index} d={path} width={W} height={H} color={color} at={at} duration={duration}
      strokeWidth={weight} taper={0.4} wobble={1} boilEvery={8} seed={seed + index}
      style={{position: 'absolute', inset: 0}} />
  ))}</>;
}

/** Posição de Bia, com a chegada desacelerando; a passada acompanha a distância percorrida. */
function biaX(frame: number): number {
  return interpolate(frame, [WALK_FROM, WALK_TO], [BIA_START_X, BIA_FINAL_X], {...clamp, easing: Easing.out(Easing.quad)});
}

function biaPose(frame: number) {
  const walking = frame >= WALK_FROM && frame < WALK_TO;
  const amount = interpolate(frame, [WALK_TO - 14, WALK_TO], [1, 0], clamp);
  const walk = walking ? cutoutWalkPose(BIA_START_X - biaX(frame), {stride: 150, amount}) : {walkPhase: 0, walkAmount: 0};
  // Braço direito do desenho = o que fica do lado de Lia (esquerda de quem olha).
  const arm = frame < 110 ? 'rest' : frame < 135 ? 'bend' : 'point';
  const hand = frame < 135 ? 'relaxed' : 'open';
  return {
    ...walk,
    gazeX: -0.7, gazeY: 0, headTilt: frame >= 100 ? 2 : 0,
    rightArm: arm, rightHand: hand, leftArm: 'rest', leftHand: 'relaxed',
    leftEye: 'open', rightEye: 'open',
  } as const;
}

function liaPose(frame: number) {
  // Lia começa de olhos baixos e tristes; só depois de ver a oferta olha para Bia e responde.
  const looks = frame >= 155;
  const arm = frame < 165 ? 'rest' : frame < 172 ? 'bend' : frame < 180 ? 'open' : 'point';
  const hand = frame < 180 ? 'relaxed' : 'open';
  return {
    gazeX: looks ? 0.7 : 0, gazeY: looks ? 0 : 0.7, headTilt: looks ? 1 : -3,
    leftArm: arm, leftHand: hand, rightArm: 'rest', rightHand: 'relaxed',
    leftEye: 'sad', rightEye: 'sad',
  } as const;
}

type Cena = 1 | 2 | 3;

const TEXTOS: Record<Cena, {titulo: string; sub: string; nota?: string}> = {
  1: {titulo: 'Quando uma amiga sofre…', sub: 'Lia recebeu uma notícia difícil.'},
  2: {titulo: 'Uma pausa. Um gesto.', sub: 'Bia percebe, se aproxima e oferece companhia.'},
  3: {titulo: 'Ajudar exige compartilhar a dor?', sub: 'Mais tarde, no jardim.', nota: 'Lia continua triste. Bia continua ao lado.'},
};

const Quadro: React.FC<{cena: Cena; retrato?: boolean}> = ({cena, retrato = false}) => {
  const local = useCurrentFrame();
  // Na cena 3 (jardim, mais tarde) as duas ficam na pose final da cena 2.
  const frame = cena === 3 ? FRAMES - 1 : local;
  const x = cena === 1 ? BIA_START_X : biaX(frame);
  const t = TEXTOS[cena];
  const box = (cx: number): React.CSSProperties => ({position: 'absolute', left: cx - (SIZE * 400 / 480) / 2, top: GROUND + 20 * K - SIZE});
  const shadow = (cx: number): React.CSSProperties => ({position: 'absolute', left: cx - 95, top: GROUND - 6, width: 190, height: 16, borderRadius: '50%', background: '#d8cdb7'});
  return (
    <AbsoluteFill style={{background: PAPER, fontFamily: 'Arial, sans-serif'}}>
      <StyleProvider style={style}>
        <AbsoluteFill>
          <Line d="M80 560 C400 556 800 562 1200 558" at={0} duration={24} weight={3.5} seed={1} />
          {cena === 1 && <>
            <Line d="M860 250 L1150 246 L1152 430 L862 434 Z M1005 248 L1007 432 M862 340 L1152 338" at={4} duration={30} weight={3.5} seed={30} />
            <Line d="M180 556 L186 470 L262 470 L268 556" at={8} duration={22} weight={3.5} seed={40} color="#6d9d94" />
            <Line d="M224 470 C220 420 190 400 170 380 M224 470 C226 410 232 390 248 360 M224 470 C236 430 270 410 296 400" at={14} duration={22} weight={3.5} seed={44} color="#6d9d94" />
          </>}
          {cena === 2 && <Line d="M1045 556 L1045 245 L1180 242 L1182 555 M1062 262 L1165 260 M1160 405 L1168 405" at={4} duration={28} weight={3.5} seed={20} />}
          {cena === 3 && <>
            <Line d="M150 556 L150 360 M190 556 L190 360" at={4} duration={22} weight={3.5} seed={50} color="#6d9d94" />
            <Line d="M110 340 C60 300 80 220 150 215 C170 160 260 170 270 230 C320 250 310 340 240 360 C200 385 140 380 110 340 Z" at={10} duration={34} weight={3.5} seed={54} color="#6d9d94" />
            <Line d="M960 470 L1210 470 M960 500 L1210 500 M970 470 L970 556 M1200 470 L1200 556 M960 420 L1210 420 L1210 470" at={8} duration={26} weight={3.5} seed={60} />
          </>}
        </AbsoluteFill>
        <div style={shadow(LIA_X)} />
        {cena >= 2 && <div style={shadow(x)} />}
        <Host identity={{skin: 'lia'}} skin={lia} size={SIZE} at={-30} pose={liaPose(cena === 1 ? 0 : frame)} seed={1} style={box(LIA_X)} />
        {cena >= 2 && <Host identity={{skin: 'bia'}} skin={bia} size={SIZE} at={-30} pose={biaPose(frame)} seed={7} style={box(x)} />}
        {cena === 3 && retrato && <RetratoCartao left={950} top={190} width={260} at={20} />}
      </StyleProvider>
      <div style={{position: 'absolute', left: 64, top: 32, fontSize: 18, letterSpacing: 3, color: '#6a6256'}}>CENA E CONCEITO / ESTUDO DE ANIMAÇÃO</div>
      <div style={{position: 'absolute', left: 64, top: 78, fontFamily: 'Georgia, serif', fontWeight: 700, fontSize: 52, color: INK}}>{t.titulo}</div>
      <div style={{position: 'absolute', left: 66, top: 148, fontSize: 24, color: '#6a6256'}}>{t.sub}</div>
      {t.nota && <div style={{position: 'absolute', left: 66, top: 600, fontFamily: 'Georgia, serif', fontStyle: 'italic', fontSize: 26, color: '#6a6256'}}>{t.nota}</div>}
      <div style={{position: 'absolute', left: 66, bottom: 28, fontSize: 18, color: '#6a6256'}}>Estudo visual • exemplo fictício • sem narração final</div>
    </AbsoluteFill>
  );
};

const Estudo: React.FC = () => (
  <AbsoluteFill>
    <Sequence from={0} durationInFrames={FRAMES}><Quadro cena={1} /></Sequence>
    <Sequence from={FRAMES} durationInFrames={FRAMES}><Quadro cena={2} /></Sequence>
    <Sequence from={FRAMES * 2} durationInFrames={PAGINA_FRAMES}>
      <Pagina titulo="Agostinho, uma fonte" sub="Página de fonte; o trecho entra quando o roteiro existir."
        rodape="Estudo visual • exemplo fictício • sem narração final" />
    </Sequence>
    <Sequence from={FRAMES * 2 + PAGINA_FRAMES} durationInFrames={FRAMES}><Quadro cena={3} /></Sequence>
  </AbsoluteFill>
);

const EstudoJunto: React.FC = () => (
  <AbsoluteFill>
    <Sequence from={0} durationInFrames={FRAMES}><Quadro cena={1} /></Sequence>
    <Sequence from={FRAMES} durationInFrames={FRAMES}><Quadro cena={2} /></Sequence>
    <Sequence from={FRAMES * 2} durationInFrames={FRAMES}><Quadro cena={3} retrato /></Sequence>
  </AbsoluteFill>
);

registerRoot(() => (
  <>
    <Composition id="Quadro2Recortes" component={() => <Quadro cena={2} />} durationInFrames={FRAMES} fps={FPS} width={W} height={H} />
    <Composition id="EstudoJunto" component={EstudoJunto} durationInFrames={FRAMES * 3} fps={FPS} width={W} height={H} />
    <Composition id="EstudoRecortes" component={Estudo} durationInFrames={FRAMES * 3 + PAGINA_FRAMES} fps={FPS} width={W} height={H} />
  </>
));
