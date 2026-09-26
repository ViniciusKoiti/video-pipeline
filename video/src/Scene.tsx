import React from "react";
import {AbsoluteFill, Img, Sequence, interpolate, staticFile, useCurrentFrame} from "remotion";
import {FilmGrain, ImageBackground} from "@viniciusk/motion-kit/fx";
import {CameraRig} from "@viniciusk/motion-kit/motion";

// Uma cena = uma composição: o durationInFrames da composição é o da cena, então o CameraRig do
// motion-kit faz o push-in por cena. Regras do §9: imagem estreita inteira sobre cópia desfocada;
// movimento leve (zoom + deriva) com folga para a deriva nunca mostrar borda.

export type Cue = {from: number; to: number; text: string}; // quadros relativos à cena
export type Look = {zoom: number; driftX: number; driftY: number; phase: number; grain: number; vignette: boolean};
export type SceneProps = {
  width: number; height: number; fps: number; frames: number; image: string; aspect: number;
  fitMinAspect: number; fadeFrames: number; cues: Cue[]; look: Look;
};

const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;
const DRIFT_MARGIN = 1.04; // folga para a deriva de ±22 px

const Caption: React.FC<{text: string; height: number}> = ({text, height}) => (
  <AbsoluteFill style={{justifyContent: "flex-end", alignItems: "center", paddingBottom: height * 0.06}}>
    <div style={{
      maxWidth: "80%", textAlign: "center", color: "white", fontFamily: "DejaVu Sans, sans-serif",
      fontSize: height * 0.045, lineHeight: 1.25, textShadow: "0 0 4px black, 0 0 4px black, 0 0 2px black",
    }}>{text}</div>
  </AbsoluteFill>
);

export const Scene: React.FC<SceneProps> = (props) => {
  const frame = useCurrentFrame();
  const opacity = Math.min(
    interpolate(frame, [0, props.fadeFrames], [0, 1], clamp),
    interpolate(frame, [props.frames - props.fadeFrames, props.frames], [1, 0], clamp),
  );
  const src = staticFile(props.image);
  const narrow = props.aspect < props.fitMinAspect;
  const {look} = props;
  return (
    <AbsoluteFill style={{backgroundColor: "black"}}>
      <AbsoluteFill style={{opacity}}>
        <CameraRig zoom={look.zoom} driftX={look.driftX} driftY={look.driftY} phase={look.phase}>
          <AbsoluteFill style={{transform: `scale(${DRIFT_MARGIN})`}}>
            {narrow && (
              <Img src={src} style={{position: "absolute", width: "100%", height: "100%", objectFit: "cover",
                filter: "blur(28px) brightness(0.85)"}} />
            )}
            <ImageBackground src={src} fit={narrow ? "contain" : "cover"} scrim={0} grid={false}
              kenBurns={false} bg="transparent" />
          </AbsoluteFill>
        </CameraRig>
      </AbsoluteFill>
      {look.grain > 0 && (
        <FilmGrain width={props.width} height={props.height} opacity={look.grain} vignette={look.vignette} />
      )}
      {props.cues.map((cue) => (
        <Sequence key={`${cue.from}-${cue.text}`} from={cue.from} durationInFrames={Math.max(cue.to - cue.from, 1)}>
          <Caption text={cue.text} height={props.height} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
