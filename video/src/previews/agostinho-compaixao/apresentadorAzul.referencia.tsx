/**
 * O apresentador azul dos vídeos de divulgação (receita A da folha `FolhaAzul.tsx`, escolhida pelo dono em
 * 2026-10-27): a pele de recortes do kit com um capuz levantado atrás da cabeça e o rosto sem orelhas.
 */
import { createCutoutSkin } from '@viniciuskoitin/motion-kit/host/cutout';
import type { CutoutPartRenderer } from '@viniciuskoitin/motion-kit/host/cutout';

const INK = '#302c2b';
export const AZUL = { skin: '#e8c4a0', hair: '#2b2523', outfit: '#2f6fb3', pants: '#2f3542', accent: '#f2c14e', gloves: '#1f4778', lining: '#1f4778' };

/** Capuz levantado atrás da cabeça, com o rosto inteiro à mostra. */
export const capuz: CutoutPartRenderer = ({ colors }) => (
  <g data-factory-part="hood-up">
    <path d="M200 22 C282 22 328 84 328 158 C328 234 282 284 200 288 C118 284 72 234 72 158 C72 84 118 22 200 22Z" fill={colors.outfit} stroke={INK} strokeWidth="2" />
    <path d="M200 38 C268 38 312 92 312 158 C312 222 270 268 200 272 C130 268 88 222 88 158 C88 92 132 38 200 38Z" fill={colors.lining} />
  </g>
);

/** O rosto sem as orelhas, para caber dentro do capuz. */
export const rosto: CutoutPartRenderer = ({ colors }) => (
  <path d="M200 49 C263 49 307 89 307 151 C307 211 264 255 200 260 C136 255 93 211 93 151 C93 89 137 49 200 49Z" fill={colors.skin} stroke={INK} strokeWidth="2" />
);

export const apresentadorAzul = createCutoutSkin({
  name: 'azul', hair: 'crop', outfit: 'jacket', hands: 'mittens', colors: AZUL,
  parts: { backHair: capuz, head: rosto },
});
