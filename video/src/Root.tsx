import React from "react";
import {Composition} from "remotion";
import {Scene, type SceneProps} from "./Scene";

// Tamanho, fps e duração vêm das props de cada cena, montadas pelo adapter (app/render/remotion.py).
const EMPTY: SceneProps = {
  width: 1920, height: 1080, fps: 30, frames: 1, image: "", aspect: 16 / 9, fitMinAspect: 1.45,
  fadeFrames: 9, cues: [], look: {zoom: 0.06, driftX: 22, driftY: 14, phase: 0, grain: 0.06, vignette: true},
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Scene"
    component={Scene}
    durationInFrames={1}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={EMPTY}
    calculateMetadata={({props}) => ({
      durationInFrames: props.frames, fps: props.fps, width: props.width, height: props.height,
    })}
  />
);
