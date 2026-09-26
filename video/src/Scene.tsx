import React from "react";
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from "remotion";
import {ShotView} from "./ShotView";
import {theme, u} from "./theme";
import type {SceneProps} from "./types";

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
        {props.shots.map((shot, i) => (
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
