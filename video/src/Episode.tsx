import React from "react";
import {AbsoluteFill, Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame} from "remotion";

// Mesmas regras do motor ffmpeg (app/render/ffmpeg.py) para a comparação ser justa: imagem com
// proporção < fitMinAspect aparece inteira sobre cópia desfocada; zoom lento; fade na entrada e na saída.

export type Cue = {from: number; to: number; text: string}; // quadros relativos à cena
export type Scene = {
  id: string; startFrame: number; frames: number; image: string; audio: string; aspect: number; cues: Cue[];
};
export type EpisodeProps = {
  width: number; height: number; fps: number; totalFrames: number; zoom: number; fadeFrames: number;
  fitMinAspect: number; burnCaptions: boolean; scenes: Scene[];
};

const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;
const fill: React.CSSProperties = {position: "absolute", width: "100%", height: "100%"};

const Caption: React.FC<{text: string; height: number}> = ({text, height}) => (
  <AbsoluteFill style={{justifyContent: "flex-end", alignItems: "center", paddingBottom: height * 0.06}}>
    <div style={{
      maxWidth: "80%", textAlign: "center", color: "white", fontFamily: "DejaVu Sans, sans-serif",
      fontSize: height * 0.045, lineHeight: 1.25, textShadow: "0 0 4px black, 0 0 4px black, 0 0 2px black",
    }}>{text}</div>
  </AbsoluteFill>
);

const SceneView: React.FC<{scene: Scene; props: EpisodeProps}> = ({scene, props}) => {
  const frame = useCurrentFrame();
  const scale = 1 + (props.zoom * frame) / Math.max(scene.frames - 1, 1);
  const opacity = Math.min(
    interpolate(frame, [0, props.fadeFrames], [0, 1], clamp),
    interpolate(frame, [scene.frames - props.fadeFrames, scene.frames], [1, 0], clamp),
  );
  const src = staticFile(scene.image);
  const narrow = scene.aspect < props.fitMinAspect;
  return (
    <AbsoluteFill style={{backgroundColor: "black"}}>
      <AbsoluteFill style={{opacity, transform: `scale(${scale})`}}>
        {narrow && <Img src={src} style={{...fill, objectFit: "cover", filter: "blur(28px) brightness(0.88)"}} />}
        <Img src={src} style={{...fill, objectFit: narrow ? "contain" : "cover"}} />
      </AbsoluteFill>
      <Audio src={staticFile(scene.audio)} />
      {props.burnCaptions && scene.cues.map((cue) => (
        <Sequence key={`${cue.from}-${cue.text}`} from={cue.from} durationInFrames={Math.max(cue.to - cue.from, 1)}>
          <Caption text={cue.text} height={props.height} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};

export const Episode: React.FC<EpisodeProps> = (props) => (
  <AbsoluteFill style={{backgroundColor: "black"}}>
    {props.scenes.map((scene) => (
      <Sequence key={scene.id} from={scene.startFrame} durationInFrames={scene.frames}>
        <SceneView scene={scene} props={props} />
      </Sequence>
    ))}
  </AbsoluteFill>
);
