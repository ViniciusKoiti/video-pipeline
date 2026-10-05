import React from "react";
import {AbsoluteFill, useVideoConfig} from "remotion";
import {FloatingWindow} from "@viniciusk/motion-kit";
import {Host, hostAspect} from "@viniciusk/motion-kit/host";
import type {HostIdentity} from "@viniciusk/motion-kit/host";
import {notionistsSkin} from "@viniciusk/motion-kit/host/dicebear";
import {theme} from "./theme";
import type {HostProps} from "./types";

// Apresentador (ADR 013): o personagem Notionists (CC0) numa janela flutuante por cima da cena. A boca segue o
// envelope do áudio da cena (`levels`, um valor por quadro); a janela vem do canto da cena anterior e é
// arrastada ao da cena, nos primeiros quadros. O arrasto não cruza o corte entre cenas: cada cena é um render.
const DRAG_FRAMES = 26;
const ENTER_FRAME = 12;

const Pane: React.FC<{identity: HostIdentity; levels: number[]}> = ({identity, levels}) => {
  const {width, height} = useVideoConfig();
  const framing = "bust";
  const size = Math.min(height * 0.98, (width * 0.98) / hostAspect(notionistsSkin, framing));
  return (
    <AbsoluteFill style={{backgroundColor: theme.surface, alignItems: "center", justifyContent: "flex-end"}}>
      <Host identity={identity} skin={notionistsSkin} size={size} framing={framing} mouthLevels={levels} gesticulate />
    </AbsoluteFill>
  );
};

export const HostWindow: React.FC<{host: HostProps}> = ({host}) => {
  const {corner, fromCorner} = host;
  const stops = !fromCorner
    ? [{at: ENTER_FRAME, to: corner}]
    : fromCorner === corner
      ? [{at: 0, to: corner}]
      : [{at: 0, to: fromCorner}, {at: DRAG_FRAMES, to: corner, travel: DRAG_FRAMES}];
  // Depois da primeira cena a janela já estava na tela: `at` antes do início evita a entrada a cada corte.
  return (
    <FloatingWindow width={host.width} stops={stops} at={fromCorner ? -60 : undefined}>
      <Pane identity={{...host.identity, skin: "notionists"} as HostIdentity} levels={host.levels} />
    </FloatingWindow>
  );
};
