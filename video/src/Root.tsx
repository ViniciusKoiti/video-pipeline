import React from "react";
import {Composition} from "remotion";
import {Episode, type EpisodeProps} from "./Episode";

// Tamanho, fps e duração vêm das props montadas pelo adapter a partir do episode.json.
const EMPTY: EpisodeProps = {
  width: 1920, height: 1080, fps: 30, totalFrames: 1, zoom: 0.06, fadeFrames: 9,
  fitMinAspect: 1.45, burnCaptions: false, scenes: [],
};

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Episode"
    component={Episode}
    durationInFrames={1}
    fps={30}
    width={1920}
    height={1080}
    defaultProps={EMPTY}
    calculateMetadata={({props}) => ({
      durationInFrames: props.totalFrames,
      fps: props.fps,
      width: props.width,
      height: props.height,
    })}
  />
);
