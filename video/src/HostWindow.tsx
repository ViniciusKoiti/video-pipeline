import React, {useMemo} from "react";
import {AbsoluteFill, useVideoConfig} from "remotion";
import {FloatingWindow} from "@viniciusk/motion-kit";
import {Host, hostAspect} from "@viniciusk/motion-kit/host";
import type {HostIdentity} from "@viniciusk/motion-kit/host";
import {notionistsSkin} from "@viniciusk/motion-kit/host/dicebear";
import {donoSkin, donoSpriteSkin} from "./donoSkin";
import {theme, useFrame} from "./theme";
import type {HostProps, HostSceneDirection} from "./types";

// Apresentador (ADR 013): o personagem Notionists (CC0), ou o desenho do dono (ADR 017; em camadas, ADR 029),
// numa janela flutuante por cima da cena. Olhar, gestos e expressão vêm da direção da cena (ADR 029). A boca
// segue o envelope do áudio da cena (`levels`, um valor por quadro); a janela vem do canto da cena anterior e
// é arrastada ao da cena, nos primeiros quadros. O arrasto não cruza o corte entre cenas: cada cena é um render.
const DRAG_FRAMES = 26;
const ENTER_FRAME = 12;
// Em retrato a janela fica abaixo da fonte do plano, que ocupa o alto da área segura (ADR 014).
const PORTRAIT_TOP_MARGIN = 90; // px de projeto; `kit()` converte para a unidade do FloatingWindow

const Pane: React.FC<{identity: HostIdentity; levels: number[]; manifest?: HostProps["manifest"];
  direction?: HostSceneDirection}> = ({identity, levels, manifest, direction}) => {
  const {width, height} = useVideoConfig();
  // O Notionists é desenhado de corpo inteiro e recortado no busto; o desenho do dono já é um busto.
  const dono = identity.skin === donoSkin.name;
  const skin = useMemo(
    () => (!dono ? notionistsSkin : manifest ? donoSpriteSkin(manifest) : donoSkin),
    [dono, manifest],
  );
  const framing = dono ? "full" : "bust";
  const size = Math.min(height * 0.98, (width * 0.98) / hostAspect(skin, framing));
  // Sem direção (props antigas), como antes: o Notionists gesticula e o dono só fala.
  const scene = direction ?? {gesticulate: !dono};
  return (
    <AbsoluteFill style={{backgroundColor: theme.surface, alignItems: "center", justifyContent: "flex-end"}}>
      <Host identity={identity} skin={skin} size={size} framing={framing} mouthLevels={levels} {...scene} />
    </AbsoluteFill>
  );
};

export const HostWindow: React.FC<{host: HostProps}> = ({host}) => {
  const {corner, fromCorner} = host;
  const {portrait, kit} = useFrame();
  const stops = !fromCorner
    ? [{at: ENTER_FRAME, to: corner}]
    : fromCorner === corner
      ? [{at: 0, to: corner}]
      : [{at: 0, to: fromCorner}, {at: DRAG_FRAMES, to: corner, travel: DRAG_FRAMES}];
  // Depois da primeira cena a janela já estava na tela: `at` antes do início evita a entrada a cada corte.
  return (
    <FloatingWindow width={host.width} stops={stops} at={fromCorner ? -60 : undefined}
      margin={portrait ? {top: kit(PORTRAIT_TOP_MARGIN)} : undefined}>
      <Pane identity={{skin: "notionists", ...host.identity} as HostIdentity} levels={host.levels}
        manifest={host.manifest} direction={host.direction} />
    </FloatingWindow>
  );
};
