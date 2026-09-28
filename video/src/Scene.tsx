import React from "react";
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from "remotion";
import {SLIDE_EXIT_FRAMES, SceneSlide} from "@viniciusk/motion-kit";
import {SourceTag} from "@viniciusk/motion-kit/editorial";
import {SceneBackground} from "@viniciusk/motion-kit/fx";
import {CameraRig} from "@viniciusk/motion-kit/motion";
import {MotionThemeProvider} from "@viniciusk/motion-kit/theme";
import {ShotView} from "./ShotView";
import {motionTheme, theme, u} from "./theme";
import type {SceneProps, ShotProps} from "./types";

// Uma cena = um bloco de narração (ADR 008), com as camadas da ADR 011 (decisão 5): a foto ou o B-roll continua
// por baixo dos planos seguintes da cena até a próxima mídia; tarja, carimbo, número e frase entram por cima
// dela; os outros gráficos ficam em tela cheia, sobre o fundo do tema. Fade só nas bordas da cena.
const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;

const MEDIA = new Set(["photo", "broll"]);
const OVERLAY = new Set(["lower_third", "stamp", "number", "keyword"]);

type Layer = "media" | "overlay" | "full";
type Planned = ShotProps & {layer: Layer; enter: boolean; exitAt?: number};

const plan = (shots: ShotProps[], sceneFrames: number): Planned[] => {
  let mediaSeen = false;
  const planned = shots.map((shot, i): Planned => {
    if (MEDIA.has(shot.spec.kind)) {
      mediaSeen = true;
      const next = shots.slice(i + 1).find((s) => MEDIA.has(s.spec.kind));
      return {...shot, frames: (next ? next.from : sceneFrames) - shot.from, layer: "media", enter: false};
    }
    const layer: Layer = OVERLAY.has(shot.spec.kind) && mediaSeen ? "overlay" : "full";
    return {...shot, overlay: layer === "overlay", layer, enter: false};
  });
  // Entre dois planos em tela cheia, o conteúdo desliza (#72); na entrada de mídia, corte seco.
  const full = (p?: Planned) => p?.layer === "full";
  return planned.map((p, i) => ({
    ...p,
    enter: full(p) && full(planned[i - 1]),
    exitAt: full(p) && full(planned[i + 1]) ? p.frames - SLIDE_EXIT_FRAMES : undefined,
  }));
};

// Rede, mapa, cronologia e documento têm câmera própria; os outros cartões ganham um avanço lento (#71).
const ownCamera = (shot: ShotProps) =>
  ["network", "map", "timeline"].includes(shot.spec.kind) ||
  (shot.spec.kind === "quote" && (shot.spec.style === "document" || shot.spec.style === "headline"));

const StageBg: React.FC = () => {
  const {width, height} = useVideoConfig();
  return (
    <AbsoluteFill style={{background: `radial-gradient(ellipse at 30% 20%, ${theme.surface} 0%, ${theme.bg} 70%)`}}>
      <SceneBackground variant="dots" bg="transparent" accents={[theme.accent]} intensity={0.25} vignette={false}
        width={width} height={height} />
    </AbsoluteFill>
  );
};

const Camera: React.FC<{active: boolean; frames: number; children: React.ReactNode}> = ({active, frames, children}) => {
  const {height} = useVideoConfig();
  if (!active) return <>{children}</>;
  return (
    <CameraRig zoom={0.05} driftX={u(height, 6)} driftY={u(height, 4)} rampFrames={frames}>
      {children}
    </CameraRig>
  );
};

// Fonte do plano (ADR 011): em tela cheia, no canto superior direito, longe de títulos e rótulos; sobre a
// imagem, embaixo, acima da legenda (do lado direito quando há tarja).
const Source: React.FC<{shot: Planned}> = ({shot}) => {
  const {height} = useVideoConfig();
  if (shot.layer === "full") {
    return (
      <div style={{position: "absolute", left: 0, right: 0, top: 0, height: u(height, 150)}}>
        <SourceTag text={shot.source!} flag={shot.sourceFlag} side="right" captionSafe={false} at={8} />
      </div>
    );
  }
  return <SourceTag text={shot.source!} flag={shot.sourceFlag} side={shot.spec.kind === "lower_third" ? "right" : "left"}
    at={8} />;
};

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
  const planned = plan(props.shots, props.frames);
  // A legenda some enquanto a frase-chave está na tela: o mesmo texto duas vezes confunde (ADR 011).
  const keyword = planned.some((p) => p.spec.kind === "keyword" && frame >= p.from && frame < p.from + p.frames);
  return (
    <MotionThemeProvider theme={motionTheme}>
      <AbsoluteFill style={{backgroundColor: theme.bg}}>
        <AbsoluteFill style={{opacity}}>
          {planned.map((shot, i) => (
            <Sequence key={i} from={shot.from} durationInFrames={shot.frames}>
              {shot.layer === "full" ? (
                <>
                  <StageBg />
                  <SceneSlide enter={shot.enter} exitAt={shot.exitAt} mode="push">
                    <Camera active={!ownCamera(shot)} frames={shot.frames}>
                      <ShotView {...shot} />
                    </Camera>
                  </SceneSlide>
                </>
              ) : (
                <ShotView {...shot} />
              )}
              {shot.source && <Source shot={shot} />}
            </Sequence>
          ))}
        </AbsoluteFill>
        <AbsoluteFill style={{opacity: keyword ? 0 : 1}}>
          {props.cues.map((cue) => (
            <Sequence key={`${cue.from}-${cue.text}`} from={cue.from} durationInFrames={Math.max(cue.to - cue.from, 1)}>
              <Caption text={cue.text} />
            </Sequence>
          ))}
        </AbsoluteFill>
      </AbsoluteFill>
    </MotionThemeProvider>
  );
};
