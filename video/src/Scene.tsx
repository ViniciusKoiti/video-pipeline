import React from "react";
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from "remotion";
import {ShotView} from "./ShotView";
import {theme, u} from "./theme";
import type {SceneProps, ShotProps} from "./types";

// Uma cena = um bloco de narração (ADR 008): planos em sequência com corte seco; fade só nas bordas.
const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;

const Caption: React.FC<{text: string}> = ({text}) => {
  const {height} = useVideoConfig();
  return (
    <AbsoluteFill style={{justifyContent: "flex-end", alignItems: "center", paddingBottom: u(height, 70)}}>
      <div style={{maxWidth: "78%", textAlign: "center", color: theme.text, fontFamily: theme.font, fontWeight: 600,
        fontSize: u(height, 44), lineHeight: 1.25, textShadow: "0 0 6px #000, 0 0 3px #000"}}>{text}</div>
    </AbsoluteFill>
  );
};

// Tarja ou número logo depois de uma foto ou B-roll na mesma cena é desenhado sobre essa mídia: ela segue em
// movimento por baixo e o painel entra por cima (regra do template, #48; o contrato continua uma lista de planos).
const MEDIA = new Set(["photo", "broll"]);
const PANEL = new Set(["lower_third", "number"]);
const layout = (shots: ShotProps[]): ShotProps[] =>
  shots.map((shot, i) => {
    const next = shots[i + 1];
    const underPanel = MEDIA.has(shot.spec.kind) && next !== undefined && PANEL.has(next.spec.kind);
    const overlay = PANEL.has(shot.spec.kind) && MEDIA.has(shots[i - 1]?.spec.kind ?? "");
    return {...shot, frames: underPanel ? shot.frames + next.frames : shot.frames, overlay};
  });

export const Scene: React.FC<SceneProps> = (props) => {
  const frame = useCurrentFrame();
  const fade = Math.min(props.fadeFrames, Math.floor(props.frames / 2));
  const opacity =
    fade > 0
      ? Math.min(
          interpolate(frame, [0, fade], [0, 1], clamp),
          interpolate(frame, [props.frames - fade, props.frames], [1, 0], clamp),
        )
      : 1;
  return (
    <AbsoluteFill style={{backgroundColor: theme.bg}}>
      <AbsoluteFill style={{opacity}}>
        {layout(props.shots).map((shot, i) => (
          <Sequence key={i} from={shot.from} durationInFrames={shot.frames}>
            <ShotView {...shot} />
          </Sequence>
        ))}
      </AbsoluteFill>
      {props.cues.map((cue) => (
        <Sequence key={`${cue.from}-${cue.text}`} from={cue.from} durationInFrames={Math.max(cue.to - cue.from, 1)}>
          <Caption text={cue.text} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
