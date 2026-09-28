import React from "react";
import {AbsoluteFill, useVideoConfig} from "remotion";
import {Odometer} from "@viniciusk/motion-kit";
import {BarChart, LineChart, ShareChart, ValueCompare, YearTimeline} from "@viniciusk/motion-kit/charts";
import {
  ArchivalPhoto, DateStamp, DocumentPage, KineticHeadline, LowerThird as KitLowerThird,
} from "@viniciusk/motion-kit/editorial";
import {FootageBackground, ImageBackground} from "@viniciusk/motion-kit/fx";
import {GeoMap} from "@viniciusk/motion-kit/geo";
import type {LonLat} from "@viniciusk/motion-kit/geo";
import {ExpandingNetwork} from "@viniciusk/motion-kit/graph";
import {mapBoxes, regionsFor} from "./geo/regions";
import {NODE_ICONS} from "./icons";
import {screenNumber} from "./numbers";
import {theme, u} from "./theme";
import type {
  ChartSpec, CompareSpec, KeywordSpec, LowerThirdSpec, MapSpec, NetworkSpec, NumberSpec, PhotoSpec, QuoteSpec,
  StampSpec, TimelineSpec,
} from "./types";

// Planos da ADR 011 com as peças do motion-kit 0.2 (tema `editorial` injetado em Scene.tsx). Tempos em quadros
// relativos ao plano. A tela nunca calcula razão, variação nem soma (decisão 7).

// Peças sem escala própria (gráficos): desenhadas num quadro de 1920×1080 e escaladas para a composição.
const Design: React.FC<{children: React.ReactNode}> = ({children}) => {
  const {height} = useVideoConfig();
  return (
    <AbsoluteFill>
      <div style={{position: "absolute", left: 0, top: 0, width: 1920, height: 1080, transformOrigin: "top left",
        transform: `scale(${height / 1080})`}}>{children}</div>
    </AbsoluteFill>
  );
};

const Title: React.FC<{title: string; subtitle?: string}> = ({title, subtitle}) => (
  <div style={{display: "flex", flexDirection: "column", gap: 14}}>
    <div style={{fontSize: 52, fontWeight: 700, color: theme.text, fontFamily: theme.font}}>{title}</div>
    <div style={{width: 120, height: 3, background: theme.accent, borderRadius: 2}} />
    {subtitle && <div style={{fontSize: 30, color: theme.muted, fontFamily: theme.font}}>{subtitle}</div>}
  </div>
);

// --- Mídia --------------------------------------------------------------------------------------

export const ArchivalShot: React.FC<{spec: PhotoSpec; src: string; credit?: string; aspect?: number}> = ({
  spec, src, credit, aspect = 16 / 9,
}) => (
  <ArchivalPhoto src={src} aspect={aspect} crop={spec.crop ?? undefined} motion={spec.motion ?? "push_in"}
    credit={credit} />
);

// Foto de banco ou ilustração: colorida e em tela cheia, para não parecer registro de época (§2.4).
export const StockShot: React.FC<{spec: PhotoSpec; src: string}> = ({spec, src}) => {
  const crop = spec.crop ?? {x: 0, y: 0, width: 1, height: 1};
  const focus = `${(crop.x + crop.width / 2) * 100}% ${(crop.y + crop.height / 2) * 100}%`;
  return <ImageBackground src={src} motion={spec.motion ?? "push_in"} focus={focus} scrim={0.12} />;
};

export const BrollShot: React.FC<{src: string}> = ({src}) => <FootageBackground src={src} scrim={0.12} />;

// --- Números ------------------------------------------------------------------------------------

// O hodômetro mostra o número como a ficha escreve: milhar só se ela agrupa, as mesmas casas decimais,
// prefixo e sufixo fixos. Texto sem número fica estático.
const Digits: React.FC<{value: string; fontSize: number}> = ({value, fontSize}) => {
  const parsed = screenNumber(value);
  if (!parsed) return <span style={{fontSize, fontWeight: 800}}>{value}</span>;
  return (
    <Odometer to={parsed.value} decimals={parsed.decimals} decimalSeparator="," groupSeparator="."
      format={parsed.grouped ? "grouped" : "plain"} prefix={parsed.prefix || undefined}
      suffix={parsed.suffix || undefined} font="sans" fontSize={fontSize} color={theme.text} delay={3}
      duration={30} />
  );
};

export const NumberShot: React.FC<{spec: NumberSpec; overlay?: boolean}> = ({spec, overlay = false}) => {
  const {height} = useVideoConfig();
  if (overlay) {
    // Sobre a foto ou o B-roll: painel no canto, para a mídia continuar visível.
    return (
      <AbsoluteFill style={{color: theme.text, fontFamily: theme.font}}>
        <div style={{position: "absolute", left: u(height, 110), bottom: u(height, 150), maxWidth: u(height, 1100),
          display: "flex", flexDirection: "column", gap: u(height, 14), background: "rgba(14, 17, 22, 0.86)",
          padding: `${u(height, 26)}px ${u(height, 38)}px`, borderRadius: u(height, 6),
          boxShadow: "0 16px 40px rgba(0,0,0,0.45)"}}>
          <Digits value={spec.value} fontSize={u(height, 120)} />
          <div style={{width: u(height, 120), height: 3, background: theme.accent, borderRadius: 2}} />
          <div style={{fontSize: u(height, 32), color: theme.muted, fontWeight: 500}}>{spec.label}</div>
        </div>
      </AbsoluteFill>
    );
  }
  return (
    <AbsoluteFill style={{justifyContent: "center", alignItems: "center", color: theme.text, fontFamily: theme.font}}>
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", gap: u(height, 28)}}>
        <Digits value={spec.value} fontSize={u(height, 220)} />
        <div style={{width: u(height, 180), height: 3, background: theme.accent, borderRadius: 2}} />
        <div style={{fontSize: u(height, 44), color: theme.muted, fontWeight: 500, textAlign: "center",
          maxWidth: u(height, 1200)}}>{spec.label}</div>
      </div>
    </AbsoluteFill>
  );
};

// Dois valores; sem número reconhecível, lado a lado em texto (a tela não converte nem calcula).
export const CompareShot: React.FC<{spec: CompareSpec}> = ({spec}) => {
  const {height} = useVideoConfig();
  const left = screenNumber(spec.left.value);
  const right = screenNumber(spec.right.value);
  if (left && right) {
    const side = (n: NonNullable<typeof left>, label: string) => ({
      value: n.value, label, prefix: n.prefix || undefined, suffix: n.suffix || undefined, decimals: n.decimals,
      format: n.grouped ? ("grouped" as const) : ("plain" as const),
    });
    return (
      <ValueCompare left={side(left, spec.left.label)} right={side(right, spec.right.label)}
        mode={spec.mode ?? "side"} emphasis={spec.emphasis ?? undefined} showRatio={false} at={4} duration={40} />
    );
  }
  const column = (s: {value: string; label: string}) => (
    <div style={{display: "flex", flexDirection: "column", alignItems: "center", gap: u(height, 18), flex: 1}}>
      <div style={{fontSize: u(height, 110), fontWeight: 800}}>{s.value}</div>
      <div style={{fontSize: u(height, 36), color: theme.muted, textAlign: "center"}}>{s.label}</div>
    </div>
  );
  return (
    <AbsoluteFill style={{flexDirection: "row", alignItems: "center", padding: `0 ${u(height, 160)}px`,
      color: theme.text, fontFamily: theme.font}}>
      {column(spec.left)}
      <div style={{width: 2, height: u(height, 260), background: theme.line}} />
      {column(spec.right)}
    </AbsoluteFill>
  );
};

// --- Gráficos -----------------------------------------------------------------------------------

const decimalsOf = (values: number[]) =>
  Math.max(0, ...values.map((v) => (String(v).split(".")[1] ?? "").length));
const yearValue = (label: string) => {
  const [y, m = "1", d = "1"] = label.split("-");
  return Number(y) + (Number(m) - 1) / 12 + (Number(d) - 1) / 365;
};

export const ChartShot: React.FC<{spec: ChartSpec}> = ({spec}) => {
  const type = spec.type ?? "bar";
  const unit = spec.unit ?? "";
  // "%" cola no número; unidade longa ("contos de réis") vai para o subtítulo, não para cada valor.
  const inline = unit === "%" ? "%" : "";
  const subtitle = unit && unit !== "%" ? `em ${unit}` : undefined;
  const decimals = decimalsOf(spec.points.map((p) => p.value));
  let chart: React.ReactNode;
  if (type === "line") {
    const labels = new Map(spec.points.map((p) => [yearValue(p.label), p.label]));
    chart = (
      <LineChart width={1600} height={660} unit={inline} decimals={decimals} yFromZero={spec.y_from_zero ?? true}
        points={spec.points.map((p) => ({x: yearValue(p.label), y: p.value}))}
        formatX={(x: number) => labels.get(x) ?? String(Math.round(x))}
        annotate={spec.highlight ? [{x: yearValue(spec.highlight), text: spec.highlight}] : undefined} />
    );
  } else if (type === "share") {
    chart = (
      <ShareChart width={1600} variant="bar100" unit={unit.startsWith("%") ? "%" : inline} decimals={decimals}
        highlight={spec.highlight ?? undefined} rest={spec.rest ?? undefined}
        parts={spec.points.map((p) => ({label: p.label, value: p.value}))} />
    );
  } else {
    chart = (
      <BarChart width={1600} height={620} orientation={type === "bar_horizontal" ? "horizontal" : "vertical"}
        unit={inline} decimals={decimals} labelSize={34} maxBarThickness={type === "bar_horizontal" ? 110 : 240}
        bars={spec.points.map((p) => ({label: p.label, value: p.value,
          color: p.label === spec.highlight ? theme.accent : theme.muted}))} />
    );
  }
  return (
    <Design>
      <div style={{position: "absolute", left: 160, top: 120, right: 160, bottom: 120, display: "flex",
        flexDirection: "column", gap: 40}}>
        <Title title={spec.title} subtitle={subtitle} />
        <div style={{flex: 1, display: "flex", alignItems: "center", justifyContent: "center"}}>{chart}</div>
      </div>
    </Design>
  );
};

// --- Tempo, lugar, relações ---------------------------------------------------------------------

// Com `when` em todos os eventos, escala real; senão, espaçamento igual (ADR 011). A data escrita é o rótulo.
export const TimelineShot: React.FC<{spec: TimelineSpec; frames: number}> = ({spec, frames}) => {
  const real = spec.events.every((e) => e.when);
  const events = spec.events.map((e, i) => ({
    date: real ? (/^\d{4}$/.test(e.when!) ? Number(e.when) : e.when!) : i + 1,
    label: e.label,
    dateLabel: e.date,
  }));
  const per = Math.max(20, (frames - 12) / events.length);
  const travel = Math.min(40, Math.round(per * 0.4));
  return (
    <YearTimeline events={events} scale={real ? "proportional" : "even"} at={6} travel={travel}
      hold={Math.max(8, Math.round(per - travel))} />
  );
};

export const MapShot: React.FC<{spec: MapSpec; frames: number}> = ({spec, frames}) => {
  const scope = spec.scope ?? "region";
  const zoomEnd = Math.min(45, Math.round(frames * 0.45));
  const [wide, tight] = mapBoxes(spec.places, scope);
  const at = new Map(spec.places.map((p) => [p.name, [p.lon, p.lat] as LonLat]));
  return (
    <GeoMap
      regions={regionsFor(scope)}
      camera={[{box: wide, at: 0}, {box: tight, at: zoomEnd, travel: zoomEnd}]}
      highlight={(spec.highlight ?? []).map((id, i) => ({id, at: 10 + i * 14}))}
      pins={spec.places.map((p, i) => ({lon: p.lon, lat: p.lat, label: p.name, at: Math.max(0, zoomEnd - 8) + i * 6}))}
      routes={(spec.routes ?? []).map((r, i) => ({from: at.get(r.from)!, to: at.get(r.to)!, at: zoomEnd + i * 10,
        duration: Math.max(20, Math.min(50, frames - zoomEnd - 10))}))}
    />
  );
};

export const NetworkShot: React.FC<{spec: NetworkSpec; stepFrames?: number[]}> = ({spec, stepFrames}) => {
  const {height} = useVideoConfig();
  return (
    <ExpandingNetwork
      root={spec.root}
      layout={spec.layout ?? "radial"}
      nodes={spec.nodes.map((n) => ({id: n.id, label: n.label, sublabel: n.role || undefined, kind: n.kind,
        icon: NODE_ICONS[n.kind]}))}
      edges={spec.edges.map((e) => ({from: e.from, to: e.to, label: e.label || undefined, value: e.value || undefined,
        style: e.style ?? "solid", flow: e.flow ?? false}))}
      steps={spec.steps.map((s, i) => ({at: stepFrames?.[i] ?? 0, nodes: s.nodes,
        highlight: s.highlight?.length ? s.highlight : undefined}))}
      nodeRadius={u(height, 46)}
      labelSize={u(height, 32)}
      layoutOptions={{ringGap: 340}}
      drift={u(height, 5)}
    />
  );
};

// --- Texto --------------------------------------------------------------------------------------

// Página recriada: só o cabeçalho e o trecho são texto; o resto são barras neutras (DocumentPage).
export const DocumentShot: React.FC<{spec: QuoteSpec; frames: number}> = ({spec, frames}) => {
  const header = spec.document ?? {title: spec.attribution};
  return (
    <DocumentPage
      variant={spec.style === "headline" ? "newspaper" : spec.variant ?? "report"}
      header={{title: header.title, issuer: header.issuer || undefined, date: header.date || undefined}}
      quote={spec.text}
      zoomAt={Math.round(frames * 0.22)}
      zoomFrames={Math.max(20, Math.round(frames * 0.35))}
      highlightDuration={Math.min(30, Math.round(frames * 0.25))}
    />
  );
};

export const KeywordShot: React.FC<{spec: KeywordSpec; overlay?: boolean}> = ({spec, overlay = false}) => (
  <AbsoluteFill>
    {overlay && <AbsoluteFill style={{background: "rgba(14, 17, 22, 0.55)"}} />}
    <KineticHeadline text={spec.text} highlight={spec.highlight || undefined} at={4} />
  </AbsoluteFill>
);

export const StampShot: React.FC<{spec: StampSpec; overlay?: boolean}> = ({spec, overlay = false}) => (
  <AbsoluteFill>
    {overlay ? (
      <DateStamp date={spec.date} place={spec.place || undefined} mode="corner" corner="top-left" at={4} />
    ) : (
      <DateStamp date={spec.date} place={spec.place || undefined} mode="hero" scrim={0} at={4} />
    )}
  </AbsoluteFill>
);

// Sobre a foto, a tarja sobe um pouco para não cobrir o crédito da imagem.
export const LowerThirdShot: React.FC<{spec: LowerThirdSpec; overlay?: boolean}> = ({spec, overlay = false}) => (
  <AbsoluteFill>
    <KitLowerThird name={spec.name} role={spec.role} at={0} offsetY={overlay ? 190 : 120} />
  </AbsoluteFill>
);
