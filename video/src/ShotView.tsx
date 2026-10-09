import React from "react";
import {AbsoluteFill, interpolate, useCurrentFrame, useVideoConfig} from "remotion";
import {useSpringIn} from "@viniciusk/motion-kit";
import {
  ArchivalShot, BrollShot, ChartShot, CompareShot, DocumentShot, KeywordShot, LowerThirdShot, MapShot, NetworkShot,
  NumberShot, StampShot, StockShot, TimelineShot,
} from "./Editorial";
import {LABELS} from "./labels";
import {useLanguage} from "./language";
import {media, theme, useFrame} from "./theme";
import type {FamilyTreeSpec, QuoteSpec, ShotProps} from "./types";

const clamp = {extrapolateLeft: "clamp", extrapolateRight: "clamp"} as const;

// --- Assinatura: o fio dourado que se desenha em todo plano gráfico ------------------------------

const GoldRule: React.FC<{width: number; delay?: number}> = ({width, delay = 4}) => {
  const frame = useCurrentFrame();
  const grow = interpolate(frame, [delay, delay + 14], [0, width], clamp);
  return <div style={{width: grow, height: 3, background: theme.accent, borderRadius: 2}} />;
};

// Palco dos planos em tela cheia: sem fundo próprio (o fundo do tema fica em Scene.tsx, parado, para a
// transição deslizar só o conteúdo).
const Stage: React.FC<{children: React.ReactNode; align?: "center" | "left"}> = ({children, align = "center"}) => {
  const {u} = useFrame();
  return (
    <AbsoluteFill
      style={{
        color: theme.text,
        fontFamily: theme.font,
        justifyContent: "center",
        alignItems: align === "center" ? "center" : "flex-start",
        padding: `0 ${u(160)}px`,
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

// --- Peças que continuam do template (sem equivalente no kit) ------------------------------------

const Quote: React.FC<{spec: QuoteSpec}> = ({spec}) => {
  const {u} = useFrame();
  const labels = LABELS[useLanguage()];
  const enter = useEnter();
  const headline = spec.style === "headline";
  return (
    <Stage align="left">
      <div style={{...enter, display: "flex", flexDirection: "column", gap: u(30), maxWidth: u(1450)}}>
        <div style={{color: theme.accent, fontSize: u(28), fontWeight: 700, letterSpacing: 3,
          textTransform: "uppercase"}}>{headline ? labels.headline : labels.quote}</div>
        <div style={{fontSize: u(headline ? 86 : 70), fontWeight: headline ? 800 : 600, lineHeight: 1.12,
          letterSpacing: headline ? -1.5 : -0.5}}>{headline ? spec.text : `“${spec.text}”`}</div>
        <GoldRule width={u(120)} delay={8} />
        <div style={{fontSize: u(30), color: theme.muted}}>— {spec.attribution}</div>
      </div>
    </Stage>
  );
};

const FamilyTree: React.FC<{spec: FamilyTreeSpec}> = ({spec}) => {
  const {width, height} = useVideoConfig();
  const {u} = useFrame();
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
  const minGap = u(380);
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
          border: `1px solid ${theme.line}`, borderTop: `4px solid ${theme.accent}`, padding: `${u(18)}px ${u(28)}px`,
          textAlign: "center", minWidth: u(300)}}>
          <div style={{fontSize: u(34), fontWeight: 700}}>{p.name}</div>
          {p.role && <div style={{fontSize: u(24), color: theme.muted, marginTop: u(6)}}>{p.role}</div>}
        </div>
      ))}
    </Stage>
  );
};

// --- Despacho por tipo (ADR 008 e ADR 011) -------------------------------------------------------

export const ShotView: React.FC<ShotProps> = ({spec, media: path, frames, credit, aspect, overlay, stepFrames}) => {
  switch (spec.kind) {
    case "photo":
      return spec.visual_need && spec.visual_need !== "historical_exact" ? (
        <StockShot spec={spec} src={media(path ?? "")} />
      ) : (
        <ArchivalShot spec={spec} src={media(path ?? "")} credit={credit} aspect={aspect} />
      );
    case "broll":
      return <BrollShot src={media(path ?? "")} />;
    case "number":
      return <NumberShot spec={spec} overlay={overlay} />;
    case "quote":
      return spec.style === "document" || spec.style === "headline" ? (
        <DocumentShot spec={spec} frames={frames} />
      ) : (
        <Quote spec={spec} />
      );
    case "stamp":
      return <StampShot spec={spec} overlay={overlay} />;
    case "lower_third":
      return <LowerThirdShot spec={spec} overlay={overlay} />;
    case "chart":
      return <ChartShot spec={spec} />;
    case "timeline":
      return <TimelineShot spec={spec} frames={frames} />;
    case "family_tree":
      return <FamilyTree spec={spec} />;
    case "map":
      return <MapShot spec={spec} frames={frames} />;
    case "compare":
      return <CompareShot spec={spec} />;
    case "network":
      return <NetworkShot spec={spec} stepFrames={stepFrames} />;
    case "keyword":
      return <KeywordShot spec={spec} overlay={overlay} />;
  }
};
