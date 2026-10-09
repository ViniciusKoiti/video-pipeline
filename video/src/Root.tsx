import React from "react";
import {Composition} from "remotion";
import {Clipe, CLIPE_FPS, CLIPE_PADRAO, clipeMetadata} from "./clipe/Clipe";
import {Scene} from "./Scene";
import type {SceneProps} from "./types";
import "./theme";

// "Scene": uma cena por render (cache por cena no adapter). "Shot" é a mesma composição com um
// plano só, usada pela folha de estilo (`remotion still`).
const EMPTY: SceneProps = {width: 1920, height: 1080, fps: 30, frames: 1, fadeFrames: 0, shots: [], cues: []};
const metadata = ({props}: {props: SceneProps}) => ({
  durationInFrames: props.frames, fps: props.fps, width: props.width, height: props.height,
});

export const RemotionRoot: React.FC = () => (
  <>
    <Composition id="Scene" component={Scene} durationInFrames={1} fps={30} width={1920} height={1080}
      defaultProps={EMPTY} calculateMetadata={metadata} />
    <Composition id="Shot" component={Scene} durationInFrames={1} fps={30} width={1920} height={1080}
      defaultProps={EMPTY} calculateMetadata={metadata} />
    {/* Clipe de letra, fora do contrato do episódio: `inicio`/`fim` em segundos cortam um trecho; `retrato` = 9:16. */}
    <Composition id="Clipe" component={Clipe} durationInFrames={1} fps={CLIPE_FPS} width={1920} height={1080}
      defaultProps={CLIPE_PADRAO} calculateMetadata={clipeMetadata} />
  </>
);
