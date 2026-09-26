import React from "react";
import {AbsoluteFill, Img, OffthreadVideo, interpolate, useCurrentFrame, useVideoConfig} from "remotion";
import {FilmGrain} from "@viniciusk/motion-kit/fx";
import {useCountUp, useSpringIn, useStagger} from "@viniciusk/motion-kit";
import {media, theme, u} from "./theme";
import type {
  ChartSpec, FamilyTreeSpec, LowerThirdSpec, MapSpec, NumberSpec, PhotoSpec, QuoteSpec, ShotProps, StampSpec,
  TimelineSpec,
} from "./types";

const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;

// --- Assinatura: o fio dourado que se desenha em todo plano gráfico ------------------------------

const GoldRule: React.FC<{width: number; delay?: number}> = ({width, delay = 4}) => {
  const frame = useCurrentFrame();
  const grow = interpolate(frame, [delay, delay + 14], [0, width], clamp);
  return <div style={{width: grow, height: 3, background: theme.accent, borderRadius: 2}} />;
};

const Stage: React.FC<{children: React.ReactNode; align?: "center" | "left"}> = ({children, align = "center"}) => {
  const {height} = useVideoConfig();
  return (
    <AbsoluteFill
      style={{
        background: `radial-gradient(ellipse at 30% 20%, ${theme.surface} 0%, ${theme.bg} 70%)`,
        color: theme.text,
        fontFamily: theme.font,
        justifyContent: "center",
        alignItems: align === "center" ? "center" : "flex-start",
        padding: `0 ${u(height, 160)}px`,
      }}
    >
      {children}
    </AbsoluteFill>
  );
};

const useEnter = (delay = 0) => {
  const t = useSpringIn(delay, {damping: 200}, 24);
  return {opacity: t, transform: `translateY(${(1 - t) * 24}px)`};
};

// --- Foto como peça de evidência ----------------------------------------------------------------

const motionTransform = (motion: PhotoSpec["motion"], p: number) => {
  const zoom = 0.06;
  switch (motion) {
    case "pull_out":
      return `scale(${1 + zoom * (1 - p)})`;
    case "pan_left":
      return `scale(1.08) translateX(${(0.5 - p) * 3}%)`;
    case "pan_right":
      return `scale(1.08) translateX(${(p - 0.5) * 3}%)`;
    case "pan_up":
      return `scale(1.08) translateY(${(0.5 - p) * 3}%)`;
    case "pan_down":
      return `scale(1.08) translateY(${(p - 0.5) * 3}%)`;
    case "still":
      return "none";
    default:
      return `scale(${1 + zoom * p})`;
  }
};

const Photo: React.FC<{spec: PhotoSpec; src: string; frames: number; credit?: string; aspect?: number}> = ({
  spec, src, frames, credit, aspect = 16 / 9,
}) => {
  const frame = useCurrentFrame();
  const {width, height} = useVideoConfig();
  const p = frames > 1 ? frame / (frames - 1) : 0;
  // O cartão segue a proporção da região mostrada (a foto inteira ou o recorte de detalhe).
  const crop = spec.crop ?? {x: 0, y: 0, width: 1, height: 1};
  const regionAspect = (crop.width * aspect) / crop.height;
  let cardW = width * 0.8;
  let cardH = cardW / regionAspect;
  if (cardH > height * 0.8) {
    cardH = height * 0.8;
    cardW = cardH * regionAspect;
  }
  const imgW = cardW / crop.width; // a imagem inteira, na escala em que o recorte preenche o cartão
  const imgH = imgW / aspect;
  return (
    <AbsoluteFill style={{background: theme.bg}}>
      <Img src={src} style={{position: "absolute", width: "100%", height: "100%", objectFit: "cover",
        filter: "blur(40px) brightness(0.35) grayscale(1)", transform: "scale(1.1)"}} />
      <AbsoluteFill style={{justifyContent: "center", alignItems: "center"}}>
        <div style={{width: cardW, height: cardH, overflow: "hidden", position: "relative",
          border: `1px solid ${theme.line}`, boxShadow: "0 30px 80px rgba(0,0,0,0.55)", background: theme.bg}}>
          <div style={{position: "absolute", inset: 0, transform: motionTransform(spec.motion, p)}}>
            <Img src={src} style={{position: "absolute", left: -crop.x * imgW, top: -crop.y * imgH, width: imgW,
              height: imgH, filter: "grayscale(1) contrast(1.06)"}} />
          </div>
          <FilmGrain width={cardW} height={cardH} opacity={0.07} vignette />
        </div>
      </AbsoluteFill>
      {credit && (
        <div style={{position: "absolute", left: (width - cardW) / 2, top: (height + cardH) / 2 + u(height, 16),
          color: theme.muted, fontFamily: theme.font, fontSize: u(height, 22), letterSpacing: 0.4}}>{credit}</div>
      )}
    </AbsoluteFill>
  );
};

const Broll: React.FC<{src: string}> = ({src}) => (
  <AbsoluteFill style={{background: theme.bg}}>
    <OffthreadVideo src={src} muted style={{width: "100%", height: "100%", objectFit: "cover"}} />
    <AbsoluteFill style={{background: "linear-gradient(180deg, rgba(14,17,22,0) 55%, rgba(14,17,22,0.75) 100%)"}} />
  </AbsoluteFill>
);

// --- Planos gráficos ----------------------------------------------------------------------------

const NUMBER_RE = /^(\D*?)([\d.,]+)(.*)$/;

const NumberCallout: React.FC<{spec: NumberSpec}> = ({spec}) => {
  const {height} = useVideoConfig();
  const match = NUMBER_RE.exec(spec.value);
  const target = match ? Number(match[2].replace(/\./g, "").replace(",", ".")) : NaN;
  const counted = useCountUp(3, 22, 0, Number.isFinite(target) ? target : 0);
  const shown = match && Number.isFinite(target) ? `${match[1]}${counted.toLocaleString("pt-BR")}${match[3]}` : spec.value;
  const enter = useEnter();
  return (
    <Stage>
      <div style={{...enter, display: "flex", flexDirection: "column", alignItems: "center", gap: u(height, 28)}}>
        <div style={{fontSize: u(height, 220), fontWeight: 800, letterSpacing: -4, fontVariantNumeric: "tabular-nums",
          lineHeight: 1}}>{shown}</div>
        <GoldRule width={u(height, 180)} />
        <div style={{fontSize: u(height, 44), color: theme.muted, fontWeight: 500, textAlign: "center",
          maxWidth: u(height, 1200)}}>{spec.label}</div>
      </div>
    </Stage>
  );
};

const Quote: React.FC<{spec: QuoteSpec}> = ({spec}) => {
  const {height} = useVideoConfig();
  const enter = useEnter();
  const headline = spec.style === "headline";
  return (
    <Stage align="left">
      <div style={{...enter, display: "flex", flexDirection: "column", gap: u(height, 30), maxWidth: u(height, 1450)}}>
        <div style={{color: theme.accent, fontSize: u(height, 28), fontWeight: 700, letterSpacing: 3,
          textTransform: "uppercase"}}>{headline ? "Manchete" : "Citação"}</div>
        <div style={{fontSize: u(height, headline ? 86 : 70), fontWeight: headline ? 800 : 600, lineHeight: 1.12,
          letterSpacing: headline ? -1.5 : -0.5}}>{headline ? spec.text : `“${spec.text}”`}</div>
        <GoldRule width={u(height, 120)} delay={8} />
        <div style={{fontSize: u(height, 30), color: theme.muted}}>— {spec.attribution}</div>
      </div>
    </Stage>
  );
};

const Stamp: React.FC<{spec: StampSpec}> = ({spec}) => {
  const {height} = useVideoConfig();
  const enter = useEnter();
  return (
    <Stage>
      <div style={{...enter, display: "flex", flexDirection: "column", alignItems: "center", gap: u(height, 22)}}>
        {spec.place && <div style={{fontSize: u(height, 40), letterSpacing: 8, textTransform: "uppercase",
          color: theme.muted, fontWeight: 600}}>{spec.place}</div>}
        <GoldRule width={u(height, 260)} />
        <div style={{fontSize: u(height, 150), fontWeight: 800, color: theme.accent, letterSpacing: -2,
          fontVariantNumeric: "tabular-nums"}}>{spec.date}</div>
      </div>
    </Stage>
  );
};

const LowerThird: React.FC<{spec: LowerThirdSpec}> = ({spec}) => {
  const {height} = useVideoConfig();
  const frame = useCurrentFrame();
  const slide = interpolate(frame, [0, 12], [-40, 0], clamp);
  const opacity = interpolate(frame, [0, 10], [0, 1], clamp);
  return (
    <Stage align="left">
      <div style={{position: "absolute", left: u(height, 160), bottom: u(height, 200), display: "flex",
        alignItems: "stretch", gap: u(height, 26), opacity, transform: `translateX(${slide}px)`}}>
        <div style={{width: u(height, 8), background: theme.accent, borderRadius: 2}} />
        <div style={{display: "flex", flexDirection: "column", gap: u(height, 10)}}>
          <div style={{fontSize: u(height, 76), fontWeight: 800, letterSpacing: -1}}>{spec.name}</div>
          <div style={{fontSize: u(height, 36), color: theme.muted, fontWeight: 500}}>{spec.role}</div>
        </div>
      </div>
    </Stage>
  );
};

const Chart: React.FC<{spec: ChartSpec}> = ({spec}) => {
  const {height} = useVideoConfig();
  const frame = useCurrentFrame();
  const max = Math.max(...spec.points.map((p) => p.value));
  const delays = useStagger(spec.points.length, 5, 6);
  const barArea = u(height, 520);
  return (
    <Stage align="left">
      <div style={{display: "flex", flexDirection: "column", gap: u(height, 40), width: "100%"}}>
        <div style={{fontSize: u(height, 52), fontWeight: 700}}>{spec.title}</div>
        <GoldRule width={u(height, 120)} />
        <div style={{display: "flex", alignItems: "flex-end", gap: u(height, 48), height: barArea}}>
          {spec.points.map((point, i) => {
            const grow = interpolate(frame, [delays[i], delays[i] + 16], [0, point.value / max], clamp);
            const last = i === spec.points.length - 1;
            return (
              <div key={point.label} style={{display: "flex", flexDirection: "column", alignItems: "center",
                gap: u(height, 14), flex: 1}}>
                <div style={{fontSize: u(height, 34), fontWeight: 700, fontVariantNumeric: "tabular-nums",
                  opacity: grow > 0.05 ? 1 : 0}}>{point.value.toLocaleString("pt-BR")}{spec.unit ? ` ${spec.unit}` : ""}</div>
                <div style={{width: "100%", height: grow * (barArea - u(height, 120)),
                  background: last ? theme.accent : theme.line, borderRadius: 4}} />
                <div style={{fontSize: u(height, 30), color: theme.muted}}>{point.label}</div>
              </div>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};

const Timeline: React.FC<{spec: TimelineSpec}> = ({spec}) => {
  const {height} = useVideoConfig();
  const frame = useCurrentFrame();
  const delays = useStagger(spec.events.length, 8, 10);
  const line = interpolate(frame, [0, 18], [0, 100], clamp);
  return (
    <Stage>
      <div style={{position: "relative", width: "100%", height: u(height, 300)}}>
        <div style={{position: "absolute", top: "50%", left: 0, width: `${line}%`, height: 3, background: theme.accent}} />
        <div style={{position: "absolute", inset: 0, display: "flex", justifyContent: "space-between"}}>
          {spec.events.map((event, i) => {
            const t = interpolate(frame, [delays[i], delays[i] + 10], [0, 1], clamp);
            return (
              <div key={event.date + event.label} style={{display: "flex", flexDirection: "column", alignItems: "center",
                justifyContent: "center", gap: u(height, 26), opacity: t, flex: 1}}>
                <div style={{fontSize: u(height, 54), fontWeight: 800, color: theme.accent}}>{event.date}</div>
                <div style={{width: u(height, 22), height: u(height, 22), borderRadius: "50%", background: theme.accent,
                  boxShadow: `0 0 0 ${u(height, 10)}px ${theme.accentSoft}`}} />
                <div style={{fontSize: u(height, 32), color: theme.text, textAlign: "center", maxWidth: u(height, 420)}}>
                  {event.label}
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </Stage>
  );
};

const FamilyTree: React.FC<{spec: FamilyTreeSpec}> = ({spec}) => {
  const {width, height} = useVideoConfig();
  const frame = useCurrentFrame();
  const depth: Record<string, number> = {};
  const depthOf = (id: string): number => {
    if (depth[id] !== undefined) return depth[id];
    const person = spec.people.find((p) => p.id === id);
    const parents = person?.parent_ids ?? [];
    depth[id] = parents.length ? Math.max(...parents.map(depthOf)) + 1 : 0;
    return depth[id];
  };
  spec.people.forEach((p) => depthOf(p.id));
  const levels = Math.max(...Object.values(depth)) + 1;
  const rows: string[][] = Array.from({length: levels}, () => []);
  spec.people.forEach((p) => rows[depth[p.id]].push(p.id));
  const pos: Record<string, {x: number; y: number}> = {};
  const minGap = u(height, 380);
  rows.forEach((row, level) => {
    const y = height * (0.24 + (0.52 * level) / Math.max(levels - 1, 1));
    const xs = row.map((id, i) => {
      const parents = spec.people.find((p) => p.id === id)?.parent_ids ?? [];
      return parents.length
        ? parents.reduce((sum, pid) => sum + pos[pid].x, 0) / parents.length // centro dos pais
        : (width * (i + 1)) / (row.length + 1);
    });
    const order = row.map((id, i) => ({id, x: xs[i]})).sort((a, b) => a.x - b.x);
    order.forEach((node, i) => {
      if (i > 0) node.x = Math.max(node.x, order[i - 1].x + minGap); // desencavala a linha
      pos[node.id] = {x: node.x, y};
    });
  });
  const reveal = (level: number) => interpolate(frame, [level * 10, level * 10 + 12], [0, 1], clamp);
  return (
    <Stage>
      <svg width={width} height={height} style={{position: "absolute", inset: 0}}>
        {spec.people.flatMap((p) =>
          (p.parent_ids ?? []).map((parent) => (
            <line key={`${parent}-${p.id}`} x1={pos[parent].x} y1={pos[parent].y} x2={pos[p.id].x} y2={pos[p.id].y}
              stroke={theme.accent} strokeWidth={3} opacity={reveal(depth[p.id])} />
          )),
        )}
      </svg>
      {spec.people.map((p) => (
        <div key={p.id} style={{position: "absolute", left: pos[p.id].x, top: pos[p.id].y,
          transform: "translate(-50%, -50%)", opacity: reveal(depth[p.id]), background: theme.surface,
          border: `1px solid ${theme.line}`, borderTop: `4px solid ${theme.accent}`, padding: `${u(height, 18)}px ${u(height, 28)}px`,
          textAlign: "center", minWidth: u(height, 300)}}>
          <div style={{fontSize: u(height, 34), fontWeight: 700}}>{p.name}</div>
          {p.role && <div style={{fontSize: u(height, 24), color: theme.muted, marginTop: u(height, 6)}}>{p.role}</div>}
        </div>
      ))}
    </Stage>
  );
};

const MapPins: React.FC<{spec: MapSpec}> = ({spec}) => {
  const {width, height} = useVideoConfig();
  const frame = useCurrentFrame();
  const lats = spec.places.map((p) => p.lat);
  const lons = spec.places.map((p) => p.lon);
  // Enquadra os pontos com folga proporcional à distância entre eles (mínimo de 0,3°).
  const pad = Math.max(0.3, 0.25 * Math.max(Math.max(...lats) - Math.min(...lats), Math.max(...lons) - Math.min(...lons)));
  const [minLat, maxLat] = [Math.min(...lats) - pad, Math.max(...lats) + pad];
  const [minLon, maxLon] = [Math.min(...lons) - pad, Math.max(...lons) + pad];
  const project = (lat: number, lon: number) => ({
    x: width * (0.15 + (0.7 * (lon - minLon)) / (maxLon - minLon)),
    y: height * (0.15 + (0.7 * (maxLat - lat)) / (maxLat - minLat)),
  });
  const delays = useStagger(spec.places.length, 8, 6);
  return (
    <Stage>
      <svg width={width} height={height} style={{position: "absolute", inset: 0}}>
        {Array.from({length: 9}, (_, i) => (
          <React.Fragment key={i}>
            <line x1={(width * i) / 8} y1={0} x2={(width * i) / 8} y2={height} stroke={theme.line} strokeWidth={1} />
            <line x1={0} y1={(height * i) / 8} x2={width} y2={(height * i) / 8} stroke={theme.line} strokeWidth={1} />
          </React.Fragment>
        ))}
      </svg>
      {spec.places.map((place, i) => {
        const {x, y} = project(place.lat, place.lon);
        const crowded = spec.places.slice(0, i).some((other) => {
          const q = project(other.lat, other.lon);
          return Math.abs(q.x - x) < u(height, 320) && Math.abs(q.y - y) < u(height, 90);
        });
        const t = interpolate(frame, [delays[i], delays[i] + 10], [0, 1], clamp);
        const pulse = 1 + 0.35 * Math.sin((frame - delays[i]) / 6);
        return (
          <div key={place.name} style={{position: "absolute", left: x, top: y, opacity: t}}>
            <div style={{position: "absolute", width: u(height, 26), height: u(height, 26), borderRadius: "50%",
              background: theme.accent, transform: "translate(-50%, -50%)"}} />
            <div style={{position: "absolute", width: u(height, 26), height: u(height, 26), borderRadius: "50%",
              border: `2px solid ${theme.accent}`, transform: `translate(-50%, -50%) scale(${pulse * 1.8})`, opacity: 0.5}} />
            <div style={{position: "absolute", left: u(height, 30), top: crowded ? u(height, 14) : -u(height, 54),
              whiteSpace: "nowrap",
              fontSize: u(height, 40), fontWeight: 700}}>{place.name}</div>
          </div>
        );
      })}
    </Stage>
  );
};

// --- Despacho por tipo --------------------------------------------------------------------------

export const ShotView: React.FC<ShotProps> = ({spec, media: path, frames, credit, aspect}) => {
  switch (spec.kind) {
    case "photo":
      return <Photo spec={spec} src={media(path ?? "")} frames={frames} credit={credit} aspect={aspect} />;
    case "broll":
      return <Broll src={media(path ?? "")} />;
    case "number":
      return <NumberCallout spec={spec} />;
    case "quote":
      return <Quote spec={spec} />;
    case "stamp":
      return <Stamp spec={spec} />;
    case "lower_third":
      return <LowerThird spec={spec} />;
    case "chart":
      return <Chart spec={spec} />;
    case "timeline":
      return <Timeline spec={spec} />;
    case "family_tree":
      return <FamilyTree spec={spec} />;
    case "map":
      return <MapPins spec={spec} />;
  }
};
