import React from 'react';
import {AbsoluteFill, Composition, Sequence, interpolate, registerRoot, useCurrentFrame} from 'remotion';
import {DrawPath, InkStroke, StyleProvider, pencilSketchStyle, solveLimb, pointsAt, shakePoints, taperOutline} from '@viniciuskoitin/motion-kit/styles';
import type {StickLimbsProps} from '@viniciuskoitin/motion-kit/styles';
import {directionAt, handTargets, FPS, FRAMES, SCENE_FRAMES} from './timing';

const PAPER = '#f5efdf';
const INK = '#332e29';
const TEAL = '#6d9d94';
const CORAL = '#d9907d';
const base = pencilSketchStyle({accent: 'green'});
const style = {
  ...base,
  slug: 'agostinho-compaixao-estudo',
  fonts: [],
  theme: {...base.theme, bg: PAPER, surface: PAPER, text: INK, line: INK, accent: TEAL},
  line: {...base.line, width: 4.5, wobble: 1.05, boilEvery: 8, passes: 1},
};
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const layer: React.CSSProperties = {position: 'absolute', inset: 0};

function Line({d, at = 0, duration = 25, color = INK, width = 1280, height = 720, weight = 4, seed = 3}: {
  d: string; at?: number; duration?: number; color?: string; width?: number; height?: number; weight?: number; seed?: number;
}) {
  return <>{d.split(/(?=M)/).filter(Boolean).map((path, index) => <InkStroke key={index}
    d={path} width={width} height={height} color={color} at={at} duration={duration}
    strokeWidth={weight} taper={0.4} wobble={1} boilEvery={8} seed={seed + index} style={layer}/>)}</>;
}

function Limb({shoulder, hand, upper, lower, bend, at, duration, strokeWidth, color, seed, style: css}: StickLimbsProps) {
  const frame = useCurrentFrame();
  const solved = solveLimb({x:shoulder[0],y:shoulder[1]}, {x:hand[0],y:hand[1]}, upper, lower, bend);
  const progress = duration === 0 ? 1 : interpolate(frame, [at ?? 0, (at ?? 0) + (duration ?? 24)], [0,1], clamp);
  const total = upper + lower;
  const points = Array.from({length:50}, (_,i) => {
    const distance = total * i / 49;
    const first = distance <= upper;
    const from = first ? solved.shoulder : solved.elbow;
    const to = first ? solved.elbow : solved.hand;
    const t = first ? distance / upper : (distance - upper) / lower;
    return {x:from.x + (to.x - from.x) * t,y:from.y + (to.y - from.y) * t};
  });
  // InkStroke também reamostra points. A geometria pura do kit evita esse caminho.
  const shaken = shakePoints(points, .5, (seed ?? 0) + Math.floor(frame / 8));
  const outline = taperOutline(pointsAt(shaken, progress), strokeWidth ?? 7, .3, points.length);
  return <svg width={400} height={460} style={css}><path d={outline} fill={color}/></svg>;
}

function Person({who, x, top = 200, instant = false, offer = 0, response = 0, walking = 0}: {
  who: 'lia' | 'bia'; x: number; top?: number; instant?: boolean; offer?: number; response?: number; walking?: number;
}) {
  const frame = useCurrentFrame();
  const lia = who === 'lia';
  const color = lia ? CORAL : TEAL;
  const start = instant ? 0 : 13;
  const duration = instant ? 0 : 24;
  const stroke = (d: string, offset = 0, weight = 4.5, ink = INK) => (
    <Line d={d} width={400} height={460} at={instant ? 0 : start + offset} duration={duration}
      weight={weight} color={ink} seed={lia ? 13 + offset : 87 + offset} />
  );
  const shape = (d: string, fill: string, offset: number) => (
    <DrawPath d={d} width={400} height={460} at={instant ? 0 : start + offset} duration={duration}
      strokeWidth={4.5} color={INK} fill={fill} fillAt={instant ? 0 : start + offset + duration + 5}
      fillDuration={instant ? 0 : 14} wobble={1.1} boilEvery={8} seed={lia ? 10 + offset : 90 + offset} style={layer} />
  );
  const {left:handL, right:handR} = handTargets(who, offer, response);
  const gait = Math.sin(walking * Math.PI * 2) * Math.min(1, Math.abs(walking)) * 12;
  const blink = frame % 106 >= 100;
  const pupil = lia ? response * 4 : -4;
  return <div style={{position: 'absolute', left: x, top, width: 400, height: 460, transform: 'scale(.82)', transformOrigin: 'top left'}}>
    <svg width={400} height={460} style={layer}><ellipse cx={200} cy={447} rx={113} ry={9} fill="#b7a993" opacity={0.16}/></svg>
    <Limb shoulder={[172, 327]} hand={[160 + gait, 438]} upper={56} lower={62} width={400} height={460}
      at={instant ? 0 : start + 9} duration={duration} strokeWidth={7} color={INK} seed={14} style={layer}/>
    <Limb shoulder={[229, 327]} hand={[248 - gait, 438]} upper={56} lower={62} width={400} height={460}
      at={instant ? 0 : start + 12} duration={duration} strokeWidth={7} color={INK} seed={15} style={layer}/>
    {stroke('M137 440 Q153 434 170 440 M236 440 Q250 436 269 442', 14, 5)}
    {shape('M166 172 Q141 181 136 209 L143 323 Q197 340 260 324 L264 208 Q254 181 232 173 L223 192 Q201 204 177 190 Z', color, 4)}
    {shape('M180 149 L177 184 Q200 200 222 183 L219 149 Z', '#eac6a8', 7)}
    <div style={{position:'absolute', inset:0, transform:`rotate(${lia ? 5 - response * 5 : -3}deg)`, transformOrigin:'200px 150px'}}>
      {shape('M141 93 Q140 33 198 28 Q260 25 260 97 L251 140 Q234 173 202 175 Q168 170 149 142 Z', lia ? '#674c40' : '#c7a565', 0)}
      {shape('M153 86 Q169 57 186 65 Q221 89 248 70 L250 116 Q249 151 222 164 Q195 179 173 158 Q150 141 153 86 Z', '#edc8ab', 2)}
      {lia ? stroke('M147 76 Q153 45 176 45 Q169 79 153 98 M188 46 Q223 42 253 69 M250 80 L264 146 M145 93 L140 149', 7, 5) : stroke('M142 76 Q135 34 179 30 Q205 4 231 30 Q264 39 263 71 M160 59 Q201 80 247 60', 7, 5)}
      {stroke(lia ? 'M169 104 Q178 99 187 103 M216 103 Q226 99 234 104' : 'M167 98 Q179 94 188 99 M216 99 Q227 94 237 99', 11, 3.4)}
      <div style={{position:'absolute',inset:0,transform:`translateX(${pupil}px)`}}>
        {stroke(blink ? 'M170 116 Q180 121 189 116 M217 116 Q227 121 236 116' : 'M174 116 L174 120 M226 116 L226 120', 12, 5)}
      </div>
      {stroke('M201 115 Q195 129 201 130', 13, 2.5)}
      {stroke(lia ? 'M184 147 Q199 139 216 146' : 'M187 143 Q201 140 215 143', 15, 3.5)}
      {lia && frame > 58 && frame < 205 ? stroke('M163 128 Q158 143 163 147 Q169 143 163 128', 45, 2.8, '#6d9d94') : null}
    </div>
    <Limb shoulder={[143, 205]} hand={handL} upper={78} lower={92} bend={1} width={400} height={460}
      at={instant ? 0 : start + 15} duration={duration} strokeWidth={7} color={INK} seed={22} style={layer}/>
    <Limb shoulder={[259, 205]} hand={handR} upper={78} lower={92} bend={-1} width={400} height={460}
      at={instant ? 0 : start + 18} duration={duration} strokeWidth={7} color={INK} seed={23} style={layer}/>
    {frame > start + duration + 20 || instant ? <svg width={400} height={460} style={layer}>
      <ellipse cx={handL[0]} cy={handL[1]} rx={9} ry={7} fill="#edc8ab" stroke={INK} strokeWidth={3}/>
      <ellipse cx={handR[0]} cy={handR[1]} rx={9} ry={7} fill="#edc8ab" stroke={INK} strokeWidth={3}/>
    </svg> : null}
  </div>;
}

function Room({second}: {second: boolean}) {
  return <>
    <Line d="M82 558 Q640 553 1198 559" at={0} duration={35} color="#b7a993" weight={2.3}/>
    <Line d={second ? 'M1000 554 L1003 243 Q1090 239 1176 245 L1175 558 M1021 262 L1155 263 L1154 552 M1133 405 L1142 405' : 'M899 226 L1157 230 L1153 425 L900 420 Z M1027 229 L1025 422 M902 325 L1154 328'} at={3} duration={36} weight={3}/>
    {!second && <>
      <Line d="M911 411 L1144 413 M921 400 Q968 339 1020 390 Q1080 319 1138 400" at={28} duration={40} color="#b7a993" weight={2}/>
      <Line d="M150 555 L147 452 L226 454 L221 554 M183 451 Q172 413 144 409 Q145 444 183 451 M184 450 Q191 397 222 391 Q226 433 184 450 M183 447 L181 383" at={20} duration={35} color={TEAL} weight={4}/>
      <Line d="M695 493 L842 493 L837 551 M706 494 L701 551 M743 491 L749 452 L779 453 L774 492 Z" at={20} duration={30} weight={3}/>
    </>}
  </>;
}

function Garden() {
  return <>
    <Line d="M80 568 Q650 555 1200 567 M77 589 Q610 579 1198 590" at={0} duration={30} color="#b7a993" weight={2}/>
    <Line d="M806 551 L801 422 L1167 426 L1171 550 M795 451 L1172 455 M797 479 L1171 483 M822 485 L817 554 M1144 485 L1150 556" at={0} duration={45} weight={3}/>
    <div style={{position:'absolute',inset:0,transform:'scale(.78)',transformOrigin:'170px 554px'}}>
      <Line d="M157 554 Q155 430 153 329 M188 555 L187 329 M171 334 Q96 326 92 274 Q44 229 99 190 Q99 137 155 145 Q200 96 231 158 Q295 157 285 219 Q321 277 258 304 Q243 347 171 334" at={7} duration={47} color={TEAL} weight={3.6}/>
    </div>
    <Line d="M84 554 Q101 528 109 552 Q116 520 127 555 M1165 553 Q1176 528 1182 554" at={50} duration={24} color={TEAL} weight={3}/>
  </>;
}

function Page({page}: {page: number}) {
  const f = useCurrentFrame();
  const direction = directionAt(page * SCENE_FRAMES + f);
  const titles = ['Quando uma amiga sofre…', 'Uma pausa. Um gesto.', 'Ajudar exige compartilhar a dor?'];
  const subtitles = ['Lia recebeu uma notícia difícil.', 'Bia percebe, se aproxima e oferece companhia.', 'Mais tarde, no jardim.'];
  const biaX = page === 1 ? 890 - 300 * direction.arrival : 590;
  const walking = page === 1 && direction.arrival > 0 && direction.arrival < 1 ? (890 - biaX) / 65 : 0;
  const textOpacity = interpolate(f, [8, 28], [0, 1], clamp);
  return <AbsoluteFill>
    <div style={{position:'absolute',left:64,top:38,fontFamily:'DejaVu Sans, sans-serif',fontSize:17,letterSpacing:2,color:'#746b60'}}>CENA E CONCEITO <span style={{color:'#a99b89'}}> / </span> ESTUDO DE ANIMAÇÃO</div>
    <div style={{position:'absolute',left:64,top:88,fontFamily:'Georgia, serif',fontSize:49,fontWeight:600,letterSpacing:-1.4,color:INK,opacity:textOpacity}}>{titles[page]}</div>
    <div style={{position:'absolute',left:67,top:155,fontFamily:'DejaVu Sans, sans-serif',fontSize:23,color:'#746b60',opacity:textOpacity}}>{subtitles[page]}</div>
    {page === 2 ? <Garden/> : <Room second={page === 1}/>}
    <Person who="lia" x={300} instant={page !== 0} offer={direction.offer} response={direction.response}/>
    {page > 0 ? <Person who="bia" x={biaX} instant offer={direction.offer} response={direction.response} walking={walking}/> : null}
    {page === 2 ? <div style={{position:'absolute',left:67,top:614,fontFamily:'Georgia, serif',fontSize:25,fontStyle:'italic',color:'#746b60',opacity:interpolate(f,[110,140],[0,1],clamp)}}>Lia continua triste. Bia continua ao lado.</div> : null}
    <Line d="M66 675 Q640 672 1213 676" at={8} duration={38} color="#b7a993" weight={2}/>
    <div style={{position:'absolute',left:67,bottom:17,fontFamily:'DejaVu Sans, sans-serif',fontSize:15,color:'#8b7f6e'}}>Estudo visual • exemplo fictício • sem narração final</div>
    <div style={{position:'absolute',right:67,bottom:17,fontFamily:'DejaVu Sans, sans-serif',fontSize:15,color:'#8b7f6e'}}>0{page + 1} / 03</div>
  </AbsoluteFill>;
}

function Preview() {
  return <StyleProvider style={style}>
    <AbsoluteFill style={{backgroundColor:PAPER}}>
      <svg width={1280} height={720} style={{position:'absolute',inset:0,opacity:.13}}>
        {Array.from({length:700}, (_,i) => <circle key={i} cx={(i * 173 + 17) % 1280} cy={(i * 97 + 23) % 720} r={i % 3 ? .5 : 1} fill="#9e8e73"/>)}
      </svg>
      {[0,1,2].map(page => <Sequence key={page} from={page * SCENE_FRAMES} durationInFrames={SCENE_FRAMES}><Page page={page}/></Sequence>)}
    </AbsoluteFill>
  </StyleProvider>;
}

registerRoot(() => <Composition id="CompaixaoDesenho" component={Preview} durationInFrames={FRAMES} fps={FPS} width={1280} height={720}/>);
