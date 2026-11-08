import React from 'react';
import {createCutoutSkin} from '@viniciuskoitin/motion-kit/host/cutout';
import type {CutoutPartRenderer} from '@viniciuskoitin/motion-kit/host/cutout';

/**
 * Lia e Bia: recortes da fábrica do kit, na mesma família da receita A do apresentador azul
 * (`apresentadorAzul.referencia.tsx`). Personagens fictícias e originais.
 */

const INK = '#302c2b';

const LIA = {skin: '#e8c4a0', hair: '#2b2523', outfit: '#d9907d', pants: '#3b4252', accent: '#f2d6b8'};
const BIA = {skin: '#e8c4a0', hair: '#c8a25a', outfit: '#5f9a93', pants: '#3b4252', accent: '#f2d6b8'};

/** Sobrancelhas de tristeza: pontas de dentro levantadas. */
const sobrancelhasTristes: CutoutPartRenderer = ({colors}) => (
  <g data-part="brows" stroke={colors.hair} strokeWidth="5" strokeLinecap="round" fill="none">
    <path d="M143 120 Q166 114 190 101" />
    <path d="M210 101 Q234 114 257 120" />
  </g>
);

const bocaTriste: CutoutPartRenderer = () => (
  <path d="M185 223 Q200 209 215 223" fill="none" stroke={INK} strokeWidth="3" strokeLinecap="round" />
);

const bocaAtenta: CutoutPartRenderer = () => (
  <path d="M186 218 Q200 222 214 218" fill="none" stroke={INK} strokeWidth="3" strokeLinecap="round" />
);

/** Lágrima junto do olho direito do desenho (esquerda de quem olha). */
const lagrima: CutoutPartRenderer = () => (
  <path d="M150 196 Q143 210 150 216 Q157 210 150 196Z" fill="#9cc7d8" stroke={INK} strokeWidth="1.5" />
);

/** Coque no alto, atrás do cabelo da frente. */
const cabeloComCoque: CutoutPartRenderer = ({colors}) => (
  <g data-part="hair-bun">
    <circle cx="200" cy="35" r="28" fill={colors.hair} stroke={INK} strokeWidth="2" />
    <path d="M94 135 L95 95 Q100 40 200 38 Q300 40 305 95 L307 134 Q276 108 266 94 Q204 120 135 99Z" fill={colors.hair} stroke={INK} strokeWidth="2" />
  </g>
);

export const lia = createCutoutSkin({
  name: 'lia', hair: 'bob', outfit: 'sweater', hands: 'bare', colors: LIA,
  parts: {brows: sobrancelhasTristes, mouth: bocaTriste, accessories: lagrima},
});

export const bia = createCutoutSkin({
  name: 'bia', hair: 'none', outfit: 'sweater', hands: 'bare', colors: BIA,
  parts: {hair: cabeloComCoque, mouth: bocaAtenta},
});
