import React from 'react';
import {AbsoluteFill, Img, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {InkStroke, StyleProvider, pencilSketchStyle} from '@viniciuskoitin/motion-kit/styles';

/**
 * Teste de "página de fonte": uma pintura de acervo dentro do quadro de traço, com crédito e um bloco de
 * texto reservado. Estudo isolado: não é roteiro, não tem trecho citado e não entra no episódio.
 * A imagem vem de `--public-dir` (cópia do ativo `commons-champaigne-agostinho`).
 */

const W = 1280;
const H = 720;
const FPS = 30;
export const PAGINA_FRAMES = 180;
const PAPER = '#f5efdf';
const INK = '#332e29';
const MUTED = '#6a6256';
const clamp = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;

// Recorte do original 1485x1917: x 450-1485, y 150-800 (rosto e coração; sem o texto pintado do ativo).
const CROP = {x: 450, y: 150, w: 1035, h: 650};
const FRAME_BOX = {left: 90, top: 220, width: 520};
const SCALE = FRAME_BOX.width / CROP.w;
const FRAME_H = Math.round(CROP.h * SCALE);

const base = pencilSketchStyle({accent: 'green'});
const style = {
  ...base,
  slug: 'agostinho-pagina-de-fonte',
  fonts: [],
  theme: {...base.theme, bg: PAPER, surface: PAPER, text: INK, line: INK, accent: '#6d9d94'},
  line: {...base.line, width: 4.5, wobble: 1.05, boilEvery: 8, passes: 1},
};

function Line({d, at = 0, duration = 25, weight = 3.5, seed = 3, color = INK}: {d: string; at?: number; duration?: number; weight?: number; seed?: number; color?: string}) {
  return <>{d.split(/(?=M)/).filter(Boolean).map((path, index) => (
    <InkStroke key={index} d={path} width={W} height={H} color={color} at={at} duration={duration}
      strokeWidth={weight} taper={0.4} wobble={1} boilEvery={8} seed={seed + index}
      style={{position: 'absolute', inset: 0}} />
  ))}</>;
}

type PaginaProps = {titulo?: string; sub?: string; rodape?: string};

export const Pagina: React.FC<PaginaProps> = ({
  titulo = 'Página de fonte',
  sub = 'Teste de imagem de acervo dentro do quadro.',
  rodape = 'Estudo visual • sem trecho citado • sem narração final',
}) => {
  const frame = useCurrentFrame();
  const {left, top, width} = FRAME_BOX;
  const right = left + width;
  const bottom = top + FRAME_H;
  const imageOpacity = interpolate(frame, [26, 50], [0, 1], clamp);
  const textX = 700;
  return (
    <AbsoluteFill style={{background: PAPER, fontFamily: 'Arial, sans-serif'}}>
      <StyleProvider style={style}>
        <AbsoluteFill>
          <Line d={`M${left - 8} ${top - 8} L${right + 8} ${top - 10} L${right + 10} ${bottom + 8} L${left - 6} ${bottom + 10} Z`} at={4} duration={26} seed={11} />
          {[0, 1, 2, 3, 4, 5, 6, 7].map((i) => (
            <Line key={i} d={`M${textX} ${252 + i * 34} L${textX + (i === 7 ? 210 : 470)} ${250 + i * 34}`} at={34 + i * 6} duration={16} weight={3} seed={30 + i} color="#b9ae9b" />
          ))}
        </AbsoluteFill>
      </StyleProvider>
      <div style={{position: 'absolute', left, top, width, height: FRAME_H, overflow: 'hidden', opacity: imageOpacity}}>
        <Img src={staticFile('champaigne.jpg')}
          style={{position: 'absolute', left: -CROP.x * SCALE, top: -CROP.y * SCALE, width: 1485 * SCALE, height: 1917 * SCALE}} />
      </div>
      <div style={{position: 'absolute', left, top: bottom + 22, width, fontSize: 18, lineHeight: 1.35, color: MUTED}}>
        Pintura de Philippe de Champaigne, c. 1645–50 (LACMA). Domínio público, via Wikimedia Commons.
      </div>
      <div style={{position: 'absolute', left: textX, top: 196, fontSize: 18, letterSpacing: 2, color: MUTED}}>TRECHO A DEFINIR COM O ROTEIRO</div>
      <div style={{position: 'absolute', left: 64, top: 32, fontSize: 18, letterSpacing: 3, color: MUTED}}>CENA E CONCEITO / ESTUDO DE ANIMAÇÃO</div>
      <div style={{position: 'absolute', left: 64, top: 78, fontFamily: 'Georgia, serif', fontWeight: 700, fontSize: 52, color: INK}}>{titulo}</div>
      <div style={{position: 'absolute', left: 66, top: 148, fontSize: 24, color: MUTED}}>{sub}</div>
      <div style={{position: 'absolute', left: 66, bottom: 28, fontSize: 18, color: MUTED}}>{rodape}</div>
    </AbsoluteFill>
  );
};

/**
 * Cartão com o retrato dentro de outra cena (Agostinho junto da animação): moldura de traço, a pintura recortada
 * (sem texto pintado legível) e o crédito. Deve ficar dentro do StyleProvider da cena.
 */
export const RetratoCartao: React.FC<{left: number; top: number; width: number; at?: number}> = ({left, top, width, at = 20}) => {
  const frame = useCurrentFrame();
  const s = width / CROP.w;
  const h = Math.round(CROP.h * s);
  const opacity = interpolate(frame, [at + 22, at + 46], [0, 1], clamp);
  const r = left + width;
  const b = top + h;
  return (
    <>
      <Line d={`M${left - 6} ${top - 6} H${r + 6} V${b + 6} H${left - 6} V${top - 6}`} at={at} duration={24} seed={71} />
      <div style={{position: 'absolute', left, top, width, height: h, overflow: 'hidden', opacity}}>
        <Img src={staticFile('champaigne.jpg')}
          style={{position: 'absolute', left: -CROP.x * s, top: -CROP.y * s, width: 1485 * s, height: 1917 * s}} />
      </div>
      <div style={{position: 'absolute', left, top: b + 14, width, fontSize: 15, lineHeight: 1.3, color: MUTED, opacity}}>
        Agostinho, pintura de Champaigne, c. 1645–50 (LACMA).
      </div>
    </>
  );
};
