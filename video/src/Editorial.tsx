import React from "react";
import {AbsoluteFill, Sequence, interpolate, useCurrentFrame, useVideoConfig} from "remotion";
import {Odometer} from "@viniciusk/motion-kit";
import {BarChart, LineChart, ShareChart, ValueCompare, YearTimeline} from "@viniciusk/motion-kit/charts";
import {
  ArchivalPhoto, DateStamp, DocumentPage, EndCta, Equation, HookCard, KineticHeadline, LowerThird as KitLowerThird,
  Receipt, fitCard,
} from "@viniciusk/motion-kit/editorial";
import {FootageBackground, ImageBackground} from "@viniciusk/motion-kit/fx";
import {GeoMap} from "@viniciusk/motion-kit/geo";
import type {LonLat} from "@viniciusk/motion-kit/geo";
import {ExpandingNetwork, layeredLayout, networkDepths} from "@viniciusk/motion-kit/graph";
import type {NetworkPositions} from "@viniciusk/motion-kit/graph";
import {mapBoxes, regionsFor} from "./geo/regions";
import {NODE_ICONS} from "./icons";
import {LABELS} from "./labels";
import {useLanguage} from "./language";
import {SEPARATORS, screenNumber} from "./numbers";
import {theme, useFrame} from "./theme";
import type {
  CalculationSpec, ChartSpec, CompareSpec, EndCardSpec, HookSpec, KeywordSpec, LowerThirdSpec, MapSpec, NetworkSpec,
  NumberSpec, PhotoSpec, QuoteSpec, ReceiptSpec, Series, StampSpec, TimelineSpec,
} from "./types";

// Planos da ADR 011 com as peças do motion-kit 0.2 (tema `editorial` injetado em Scene.tsx). Tempos em quadros
// relativos ao plano. A tela nunca calcula razão, variação nem soma (decisão 7).

// Peças sem escala própria (gráficos): desenhadas num quadro de projeto (1920×1080 em paisagem, 1080×1920 em
// retrato) e escaladas pelo lado curto para a composição.
const Design: React.FC<{children: React.ReactNode}> = ({children}) => {
  const {width, height, u} = useFrame();
  const scale = u(1);
  return (
    <AbsoluteFill>
      <div style={{position: "absolute", left: 0, top: 0, width: width / scale, height: height / scale,
        transformOrigin: "top left", transform: `scale(${scale})`}}>{children}</div>
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

// O crédito vai acima da foto, alinhado à direita, e não embaixo como no kit: embaixo entram a tarja, o painel
// do número e a fonte, que ficam por cima da foto nos planos seguintes da cena e cobriam o crédito.
const CARD = {maxWidth: 0.78, maxHeight: 0.74}; // os padrões do ArchivalPhoto

export const ArchivalShot: React.FC<{spec: PhotoSpec; src: string; credit?: string; aspect?: number}> = ({
  spec, src, credit, aspect = 16 / 9,
}) => {
  const {width, height} = useVideoConfig();
  const {u} = useFrame();
  const frame = useCurrentFrame();
  const crop = spec.crop ?? {x: 0, y: 0, width: 1, height: 1};
  const card = fitCard((crop.width * aspect) / crop.height, width * CARD.maxWidth, height * CARD.maxHeight);
  return (
    <ArchivalPhoto src={src} aspect={aspect} crop={spec.crop ?? undefined} motion={spec.motion ?? "push_in"}
      maxWidth={CARD.maxWidth} maxHeight={CARD.maxHeight}>
      {credit && (
        <div style={{position: "absolute", right: (width - card.width) / 2,
          bottom: (height + card.height) / 2 + u(14), maxWidth: card.width, textAlign: "right",
          fontFamily: theme.font, fontSize: u(22), lineHeight: 1.3, color: theme.muted,
          opacity: interpolate(frame, [12, 24], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})}}>
          {credit}
        </div>
      )}
    </ArchivalPhoto>
  );
};

// Foto de banco ou ilustração: colorida e em tela cheia, para não parecer registro de época (§2.4).
export const StockShot: React.FC<{spec: PhotoSpec; src: string}> = ({spec, src}) => {
  const crop = spec.crop ?? {x: 0, y: 0, width: 1, height: 1};
  const focus = `${(crop.x + crop.width / 2) * 100}% ${(crop.y + crop.height / 2) * 100}%`;
  return <ImageBackground src={src} motion={spec.motion ?? "push_in"} focus={focus} scrim={0.12} />;
};

export const BrollShot: React.FC<{src: string}> = ({src}) => <FootageBackground src={src} scrim={0.12} />;

// --- Números ------------------------------------------------------------------------------------

// O hodômetro mostra o número como a ficha escreve: milhar só se ela agrupa, as mesmas casas decimais,
// prefixo e sufixo fixos, com os separadores do idioma do episódio. Texto sem número fica estático.
const Digits: React.FC<{value: string; fontSize: number}> = ({value, fontSize}) => {
  const language = useLanguage();
  const parsed = screenNumber(value, language);
  if (!parsed) return <span style={{fontSize, fontWeight: 800}}>{value}</span>;
  const {group, decimal} = SEPARATORS[language];
  return (
    <Odometer to={parsed.value} decimals={parsed.decimals} decimalSeparator={decimal} groupSeparator={group}
      format={parsed.grouped ? "grouped" : "plain"} prefix={parsed.prefix || undefined}
      suffix={parsed.suffix || undefined} font="sans" fontSize={fontSize} color={theme.text} delay={3}
      duration={30} />
  );
};

// Em retrato o número cabe na largura: o corpo cai até caber (um caractere ocupa ~0,62 do corpo).
const fitDigits = (value: string, maxWidth: number, size: number) =>
  Math.min(size, maxWidth / (Math.max(value.length, 1) * 0.62));

export const NumberShot: React.FC<{spec: NumberSpec; overlay?: boolean}> = ({spec, overlay = false}) => {
  const {u, width, portrait, safe} = useFrame();
  if (overlay) {
    // Sobre a foto ou o B-roll: painel no canto, para a mídia continuar visível. Em retrato fica na área segura,
    // acima da legenda.
    const maxWidth = portrait ? width - safe.left - safe.right : u(1100);
    const digits = portrait ? fitDigits(spec.value, maxWidth - u(76), u(120)) : u(120);
    return (
      <AbsoluteFill style={{color: theme.text, fontFamily: theme.font}}>
        <div style={{position: "absolute", left: portrait ? safe.left : u(110),
          bottom: portrait ? safe.bottom + u(240) : u(150), maxWidth,
          display: "flex", flexDirection: "column", gap: u(14), background: "rgba(14, 17, 22, 0.86)",
          padding: `${u(26)}px ${u(38)}px`, borderRadius: u(6),
          boxShadow: "0 16px 40px rgba(0,0,0,0.45)"}}>
          <Digits value={spec.value} fontSize={digits} />
          <div style={{width: u(120), height: 3, background: theme.accent, borderRadius: 2}} />
          <div style={{fontSize: u(portrait ? 36 : 32), color: theme.muted, fontWeight: 500}}>{spec.label}</div>
        </div>
      </AbsoluteFill>
    );
  }
  const digits = portrait ? fitDigits(spec.value, width * 0.9, u(220)) : u(220);
  // Em retrato o número centraliza abaixo da janela do apresentador (cantos de cima), como a comparação
  // (COMPARE_TOP); centrado no quadro, um rótulo de três linhas empurrava o topo do número para baixo da janela.
  return (
    <AbsoluteFill style={{justifyContent: "center", alignItems: "center", color: theme.text, fontFamily: theme.font,
      top: portrait ? u(COMPARE_TOP) : undefined}}>
      <div style={{display: "flex", flexDirection: "column", alignItems: "center", gap: u(28)}}>
        <Digits value={spec.value} fontSize={digits} />
        <div style={{width: u(180), height: 3, background: theme.accent, borderRadius: 2}} />
        <div style={{fontSize: u(portrait ? 46 : 44), color: theme.muted, fontWeight: 500, textAlign: "center",
          maxWidth: portrait ? width * 0.84 : u(1200)}}>{spec.label}</div>
      </div>
    </AbsoluteFill>
  );
};

// Dois valores; sem número reconhecível, lado a lado em texto (a tela não converte nem calcula).
// Topo da região da comparação em retrato, em px de projeto: abaixo da janela do apresentador (cantos de cima).
const COMPARE_TOP = 240;

export const CompareShot: React.FC<{spec: CompareSpec}> = ({spec}) => {
  const {u, kit, kitPx, width, portrait, safe} = useFrame();
  const language = useLanguage();
  // Em retrato a comparação fica entre a janela do apresentador e a zona da legenda (ADR 021 e 023). O
  // `AbsoluteFill` traz `height: 100%`, que venceria o `bottom`: a altura sai das duas bordas.
  const area = portrait ? {top: u(COMPARE_TOP), bottom: safe.bottom + u(260), height: "auto"} : undefined;
  const left = screenNumber(spec.left.value, language);
  const right = screenNumber(spec.right.value, language);
  if (left && right) {
    const {group, decimal} = SEPARATORS[language];
    const side = (n: NonNullable<typeof left>, label: string) => ({
      value: n.value, label, prefix: n.prefix || undefined, suffix: n.suffix || undefined, decimals: n.decimals,
      format: n.grouped ? ("grouped" as const) : ("plain" as const),
    });
    // Em retrato os valores empilham (layout do kit) dentro da largura do quadro.
    const stacked = portrait
      ? {layout: "vertical" as const, maxWidth: kitPx(width - 2 * u(70)), valueSize: kit(150), labelSize: kit(38)}
      : {};
    // Em retrato a comparação começa abaixo da janela do apresentador (no alto, abaixo da fonte), não no centro.
    return (
      <AbsoluteFill style={area}>
        <ValueCompare left={side(left, spec.left.label)} right={side(right, spec.right.label)}
          mode={spec.mode ?? "side"} emphasis={spec.emphasis ?? undefined} showRatio={false} at={4} duration={40}
          groupSeparator={group} decimalSeparator={decimal} locale={language}
          ratioWord={LABELS[language].ratioWord} clampNote={LABELS[language].clampNote} {...stacked} />
      </AbsoluteFill>
    );
  }
  // Em retrato as colunas empilham: `flex: 1` daria a cada uma metade da altura do quadro e o texto estouraria o topo.
  const column = (s: {value: string; label: string}) => (
    <div style={{display: "flex", flexDirection: "column", alignItems: "center", gap: u(portrait ? 14 : 18),
      flex: portrait ? "none" : 1}}>
      <div style={{fontSize: u(portrait ? 64 : 110), fontWeight: 800, textAlign: "center", lineHeight: portrait ? 1.1 : undefined}}>{s.value}</div>
      <div style={{fontSize: u(portrait ? 30 : 36), color: theme.muted, textAlign: "center"}}>{s.label}</div>
    </div>
  );
  return (
    <AbsoluteFill style={{flexDirection: portrait ? "column" : "row", alignItems: "center",
      justifyContent: portrait ? "center" : undefined, gap: portrait ? u(36) : undefined,
      ...area,
      padding: `0 ${u(portrait ? 70 : 160)}px`, color: theme.text, fontFamily: theme.font}}>
      {column(spec.left)}
      <div style={portrait ? {height: 2, width: u(220), background: theme.line}
        : {width: 2, height: u(260), background: theme.line}} />
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
  const {portrait, safe, u} = useFrame();
  const language = useLanguage();
  // Tela de projeto: 1920×1080 (paisagem, gráficos de 1600 px) ou 1080×1920 (retrato, gráficos de 940 px). Em
  // retrato o título começa 150 px abaixo do topo da área segura: acima dele fica a fonte do plano.
  const chartWidth = portrait ? 940 : 1600;
  const design = (framePx: number) => framePx / u(1);
  const type = spec.type ?? "bar";
  const unit = spec.unit ?? "";
  // "%" cola no número; unidade longa ("contos de réis") vai para o subtítulo, não para cada valor.
  const inline = unit === "%" ? "%" : "";
  const subtitle = unit && unit !== "%" ? `${LABELS[language].unitIn} ${unit}` : undefined;
  const decimals = decimalsOf(spec.points.map((p) => p.value));
  let chart: React.ReactNode;
  if (type === "line") {
    const labels = new Map(spec.points.map((p) => [yearValue(p.label), p.label]));
    chart = (
      <LineChart width={chartWidth} height={portrait ? 600 : 660} unit={inline} decimals={decimals} locale={language}
        yFromZero={spec.y_from_zero ?? true}
        points={spec.points.map((p) => ({x: yearValue(p.label), y: p.value}))}
        formatX={(x: number) => labels.get(x) ?? String(Math.round(x))}
        annotate={spec.highlight ? [{x: yearValue(spec.highlight), text: spec.highlight}] : undefined} />
    );
  } else if (type === "share") {
    chart = (
      <ShareChart width={chartWidth} variant="bar100" unit={unit.startsWith("%") ? "%" : inline} decimals={decimals}
        locale={language} highlight={spec.highlight ?? undefined} rest={spec.rest ?? undefined}
        parts={spec.points.map((p) => ({label: p.label, value: p.value}))} />
    );
  } else {
    // O BarChart do kit fixado formata em pt-BR (sem `locale`): em inglês o `vp check` só deixa passar o que as
    // duas convenções escrevem igual (inteiro abaixo de mil; app/pipeline/check.py).
    chart = (
      <BarChart width={chartWidth} height={portrait ? 600 : 620} orientation={type === "bar_horizontal" ? "horizontal" : "vertical"}
        unit={inline} decimals={decimals} labelSize={34} maxBarThickness={type === "bar_horizontal" ? 110 : 240}
        bars={spec.points.map((p) => ({label: p.label, value: p.value,
          color: p.label === spec.highlight ? theme.accent : theme.muted}))} />
    );
  }
  return (
    <Design>
      <div style={{position: "absolute", left: portrait ? 70 : 160, top: portrait ? design(safe.top) + 150 : 120,
        right: portrait ? 70 : 160, bottom: portrait ? design(safe.bottom) + 280 : 120, display: "flex", flexDirection: "column", gap: 40}}>
        <Title title={spec.title} subtitle={subtitle} />
        <div style={{flex: 1, display: "flex", alignItems: portrait ? "flex-start" : "center",
          justifyContent: "center"}}>{chart}</div>
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

// Rede em camadas de cima para baixo, com as setas descendo: se a maioria delas aponta para a raiz (o dinheiro
// chega nela), a raiz fica embaixo. O nome do nó pendura embaixo do círculo, no começo da seta que sai dele, e o
// texto e o valor da seta ficam no meio e perto do fim, sem disputar espaço. Deitada não cabe: numa seta de
// ~400 px o texto e o valor, de tamanho fixo no kit, se sobrepõem. Distâncias em px de 1080p, convertidas para a
// tela da rede (NETWORK_CANVAS).
const LAYER_GAP = 240;
const NODE_GAP = 300;
const LAYERED_MAX_SCALE = 1.4; // abaixo do enquadramento justo (~1,5 com três camadas): folga para o último nome

const layeredPositions = (spec: NetworkSpec, u: (px: number) => number): NetworkPositions => {
  const ids = spec.nodes.map((n) => n.id);
  const links = spec.edges.map((e) => ({from: e.from, to: e.to}));
  const world = layeredLayout(ids, links, spec.root, {layerGap: u(LAYER_GAP), nodeGap: u(NODE_GAP)});
  const depth = networkDepths(ids, links, spec.root, false);
  const inward = spec.edges.filter((e) => (depth.get(e.from) ?? 0) > (depth.get(e.to) ?? 0)).length;
  const flip = inward * 2 > spec.edges.length ? -1 : 1;
  return Object.fromEntries(Object.entries(world).map(([id, p]) => [id, {x: p.x, y: flip * p.y}]));
};

// O kit desenha a rede com medidas fixas em px (caixa do nome com 260, texto da seta com 17, valor com 16), que
// cabem numa tela de 1280×720. A rede é desenhada nessa tela e ampliada: a prévia (720p) e o final (1080p) ficam
// iguais, em vez de o final quebrar mais linhas nos nomes e encolher o texto das setas.
const NETWORK_CANVAS = {width: 1280, height: 720};

export const NetworkShot: React.FC<{spec: NetworkSpec; stepFrames?: number[]}> = ({spec, stepFrames}) => {
  const {height} = useVideoConfig();
  return (
    <AbsoluteFill>
      <div style={{position: "absolute", left: 0, top: 0, ...NETWORK_CANVAS,
        transform: `scale(${height / NETWORK_CANVAS.height})`, transformOrigin: "top left"}}>
        <Sequence layout="none" {...NETWORK_CANVAS}>
          <NetworkCanvas spec={spec} stepFrames={stepFrames} />
        </Sequence>
      </div>
    </AbsoluteFill>
  );
};

const NetworkCanvas: React.FC<{spec: NetworkSpec; stepFrames?: number[]}> = ({spec, stepFrames}) => {
  const {u} = useFrame();
  const layered = spec.layout === "layered";
  return (
    <ExpandingNetwork
      root={spec.root}
      layout={spec.layout ?? "radial"}
      positions={layered ? layeredPositions(spec, u) : undefined}
      maxScale={layered ? LAYERED_MAX_SCALE : undefined}
      nodes={spec.nodes.map((n) => ({id: n.id, label: n.label, sublabel: n.role || undefined, kind: n.kind,
        icon: NODE_ICONS[n.kind]}))}
      edges={spec.edges.map((e) => ({from: e.from, to: e.to, label: e.label || undefined, value: e.value || undefined,
        style: e.style ?? "solid", flow: e.flow ?? false}))}
      steps={spec.steps.map((s, i) => ({at: stepFrames?.[i] ?? 0, nodes: s.nodes,
        highlight: s.highlight?.length ? s.highlight : undefined}))}
      nodeRadius={u(46)}
      labelSize={u(32)}
      layoutOptions={{ringGap: 340}}
      drift={u(5)}
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

export const KeywordShot: React.FC<{spec: KeywordSpec; overlay?: boolean}> = ({spec, overlay = false}) => {
  const {u, kit, width, portrait} = useFrame();
  // Em retrato a frase quebra na largura do quadro e fica menor (as peças do kit medem pela altura).
  const fit = portrait ? {fontSize: kit(104), maxWidth: kit(width / u(1) - 140), align: "center" as const} : {};
  return (
    <AbsoluteFill>
      {overlay && <AbsoluteFill style={{background: "rgba(14, 17, 22, 0.55)"}} />}
      <KineticHeadline text={spec.text} highlight={spec.highlight || undefined} at={4} {...fit} />
    </AbsoluteFill>
  );
};

export const StampShot: React.FC<{spec: StampSpec; overlay?: boolean}> = ({spec, overlay = false}) => {
  const {u, kit, kitPx, width, portrait, safe} = useFrame();
  if (overlay) {
    // Selo no canto; em retrato, abaixo do topo coberto pela plataforma.
    return (
      <AbsoluteFill style={portrait ? {top: safe.top} : undefined}>
        <DateStamp date={spec.date} place={spec.place || undefined} mode="corner" corner="top-left" at={4}
          {...(portrait ? {offset: kitPx(safe.left), dateSize: kit(44), placeSize: kit(24)} : {})} />
      </AbsoluteFill>
    );
  }
  const fit = portrait
    ? {dateSize: kit(Math.min(150, (width / u(1) * 0.88) / (Math.max(spec.date.length, 1) * 0.58))), placeSize: kit(34)}
    : {};
  return (
    <AbsoluteFill>
      <DateStamp date={spec.date} place={spec.place || undefined} mode="hero" scrim={0} at={4} {...fit} />
    </AbsoluteFill>
  );
};

// Sobre a foto, a tarja sobe um pouco para não cobrir o crédito da imagem. Em retrato fica na área segura,
// acima da legenda.
export const LowerThirdShot: React.FC<{spec: LowerThirdSpec; overlay?: boolean}> = ({spec, overlay = false}) => {
  const {u, kit, kitPx, width, portrait, safe} = useFrame();
  const tall = portrait
    ? {offsetX: kitPx(safe.left), offsetY: kitPx(safe.bottom + u(260)), maxWidth: kitPx(width - safe.left - safe.right),
      nameSize: kit(46), roleSize: kit(28)}
    : {offsetY: overlay ? 190 : 120};
  return (
    <AbsoluteFill>
      <KitLowerThird name={spec.name} role={spec.role} at={0} {...tall} />
    </AbsoluteFill>
  );
};

// --- Reels: conta, nota, gancho e cartão final (ADR 028) ----------------------------------------

// Só no vertical (o contrato recusa em 16:9). As peças do kit medem as margens a partir da área segura `vertical`;
// em cima fica a fonte do plano (`u(150)` abaixo da área segura, Scene.tsx) e embaixo a legenda (`u(260)`).
const useReelBox = () => {
  const {u, kitPx} = useFrame();
  return {safeArea: "vertical" as const, insets: {top: kitPx(u(150)), right: 48, bottom: kitPx(u(260)), left: 48}};
};

// A tela não calcula (ADR 020): termos e resultado são os textos do roteiro; o valor só faz os dígitos rolarem até
// o mesmo texto. Cada parte entra no quadro em que a narração a diz (`stepFrames`).
export const CalculationShot: React.FC<{spec: CalculationSpec; stepFrames?: number[]}> = ({spec, stepFrames = []}) => {
  const language = useLanguage();
  const {group, decimal} = SEPARATORS[language];
  const box = useReelBox();
  const at = (i: number) => stepFrames[i] ?? 0;
  const value = (text: string) => screenNumber(text, language)?.value;
  return (
    <AbsoluteFill>
      <Equation
        terms={spec.terms.map((t, i) => ({text: t.text, label: t.label || undefined, value: value(t.text), at: at(i),
          op: t.op ?? undefined}))}
        result={{text: spec.result.text, label: spec.result.label || undefined, value: value(spec.result.text),
          at: at(spec.terms.length)}}
        groupSeparator={group} decimalSeparator={decimal} {...box} />
    </AbsoluteFill>
  );
};

// Nota ou orçamento: a peça não soma; o total é o do roteiro, conferido pelo `vp check` (ADR 028, decisão 2).
export const ReceiptShot: React.FC<{spec: ReceiptSpec; stepFrames?: number[]}> = ({spec, stepFrames = []}) => {
  const labels = LABELS[useLanguage()];
  const box = useReelBox();
  const at = (i: number) => stepFrames[i] ?? 0;
  return (
    <AbsoluteFill>
      <Receipt title={spec.title || undefined}
        items={spec.items.map((item, i) => ({label: item.label, value: item.value, detail: item.detail || undefined,
          at: at(i)}))}
        total={spec.total ? {label: spec.total.label || labels.total, value: spec.total.value,
          at: at(spec.items.length)} : undefined}
        {...box} />
    </AbsoluteFill>
  );
};

// Gancho no primeiro plano do vídeo: legível já no quadro 0 (a primeira cena começa sem fade, Scene.tsx).
export const HookShot: React.FC<{spec: HookSpec}> = ({spec}) => (
  <AbsoluteFill>
    <HookCard text={spec.text} highlight={spec.highlight || undefined} bg="transparent" {...useReelBox()} />
  </AbsoluteFill>
);

// Cartão final com o selo da série. Sem fade próprio: a cena já termina com o dela.
export const EndCardShot: React.FC<{spec: EndCardSpec; series?: Series}> = ({spec, series}) => {
  const labels = LABELS[useLanguage()];
  const badge = series
    ? {text: `${series.name} · ${labels.part} ${series.part} ${labels.of} ${series.total}`, part: series.part,
      total: series.total}
    : undefined;
  return (
    <AbsoluteFill>
      <EndCta variant={spec.variant} text={spec.text} sub={spec.sub || undefined} series={badge} bg="transparent"
        fadeFrames={0} {...useReelBox()} />
    </AbsoluteFill>
  );
};
