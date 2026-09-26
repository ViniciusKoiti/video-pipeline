import React from "react";
import {AbsoluteFill, Easing, Img, OffthreadVideo, interpolate, useCurrentFrame, useVideoConfig} from "remotion";
import {FilmGrain} from "@viniciusk/motion-kit/fx";
import {useCountUp, useSpringIn, useStagger} from "@viniciusk/motion-kit";
import geo from "./geo/america-do-sul.json";
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
  const digits = match?.[2] ?? "";
  const target = match ? Number(digits.replace(/\./g, "").replace(",", ".")) : NaN;
  // Conta com a forma escrita na ficha: milhar só se ela agrupa ("1.500" sim; "2025", "13" não) e as mesmas
  // casas decimais ("29,4" sempre com uma), para ano não virar "2.025" nem o decimal tremer na contagem.
  // useCountUp devolve inteiros: conta em décimos (ou centésimos) e divide.
  const decimals = digits.includes(",") ? digits.split(",")[1].length : 0;
  const scale = 10 ** decimals;
  const counted = useCountUp(3, 22, 0, Number.isFinite(target) ? Math.round(target * scale) : 0) / scale;
  const format = {useGrouping: /\d\.\d{3}/.test(digits), minimumFractionDigits: decimals, maximumFractionDigits: decimals};
  const shown = match && Number.isFinite(target) ? `${match[1]}${counted.toLocaleString("pt-BR", format)}${match[3]}` : spec.value;
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

const LowerThird: React.FC<{spec: LowerThirdSpec; overlay?: boolean}> = ({spec, overlay = false}) => {
  const {height} = useVideoConfig();
  const frame = useCurrentFrame();
  const slide = interpolate(frame, [0, 12], [-40, 0], clamp);
  const opacity = interpolate(frame, [0, 10], [0, 1], clamp);
  const scale = overlay ? 0.8 : 1; // sobre a foto, menor e num painel, para não cobrir o assunto
  const tag = (
    <div style={{position: "absolute", left: u(height, overlay ? 110 : 160), bottom: u(height, overlay ? 150 : 200),
      display: "flex", alignItems: "stretch", gap: u(height, 26 * scale), opacity, transform: `translateX(${slide}px)`,
      ...(overlay && {background: "rgba(14, 17, 22, 0.86)", padding: `${u(height, 22)}px ${u(height, 34)}px`,
        borderRadius: u(height, 6), boxShadow: "0 16px 40px rgba(0,0,0,0.45)"})}}>
      <div style={{width: u(height, 8 * scale), background: theme.accent, borderRadius: 2}} />
      <div style={{display: "flex", flexDirection: "column", gap: u(height, 10 * scale)}}>
        <div style={{fontSize: u(height, 76 * scale), fontWeight: 800, letterSpacing: -1}}>{spec.name}</div>
        <div style={{fontSize: u(height, 36 * scale), color: theme.muted, fontWeight: 500}}>{spec.role}</div>
      </div>
    </div>
  );
  return overlay ? (
    <AbsoluteFill style={{color: theme.text, fontFamily: theme.font}}>{tag}</AbsoluteFill>
  ) : (
    <Stage align="left">{tag}</Stage>
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

// Contornos do Natural Earth 1:50m (domínio público, src/geo/README.md), com a caixa de cada região.
type Ring = number[][];
type Region = {name: string; rings: Ring[]; box: [number, number, number, number]; label?: number[]; uf?: string};
const boxOf = (rings: Ring[]): Region["box"] => {
  const pts = rings.flat();
  return [Math.min(...pts.map((p) => p[0])), Math.min(...pts.map((p) => p[1])),
    Math.max(...pts.map((p) => p[0])), Math.max(...pts.map((p) => p[1]))];
};
const COUNTRIES: Region[] = geo.countries.map((c) => ({...c, box: boxOf(c.rings)}));
const STATES: Region[] = geo.states.map((s) => ({...s, box: boxOf(s.rings)}));

const insideRing = (lon: number, lat: number, ring: Ring) => {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if (yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
};

// Câmera: abre no estado (~10° de latitude na tela) e fecha nos pinos; os pinos entram depois do zoom.
const MapPins: React.FC<{spec: MapSpec; frames: number}> = ({spec, frames}) => {
  const {width, height} = useVideoConfig();
  const frame = useCurrentFrame();
  const lats = spec.places.map((p) => p.lat);
  const lons = spec.places.map((p) => p.lon);
  const lat0 = (Math.min(...lats) + Math.max(...lats)) / 2;
  const lon0 = (Math.min(...lons) + Math.max(...lons)) / 2;
  const k = Math.cos((lat0 * Math.PI) / 180); // equirretangular: 1° de longitude encolhe com a latitude
  const spanLat = Math.max(Math.max(...lats) - Math.min(...lats), 0.25);
  const spanLon = Math.max((Math.max(...lons) - Math.min(...lons)) * k, 0.25);
  // Fechado: os pinos em ~40% da tela e pelo menos 1,5° de latitude visível, para sobrar referência
  // (litoral, divisa) em volta. Em px por grau.
  const tight = Math.min((0.4 * height) / spanLat, (0.4 * width) / spanLon, height / 1.5);
  const wide = Math.min(tight, height / 10);
  const zoomEnd = Math.min(45, Math.round(frames * 0.45));
  const t = interpolate(frame, [0, zoomEnd], [0, 1], {...clamp, easing: Easing.inOut(Easing.cubic)});
  const scale = Math.exp(Math.log(wide) + (Math.log(tight) - Math.log(wide)) * t);
  const at = (s: number) => (lon: number, lat: number) => ({
    x: width / 2 + (lon - lon0) * k * s,
    y: height / 2 - (lat - lat0) * s,
  });
  const project = at(scale);
  const final = at(tight);
  const [vx0, vx1] = [lon0 - width / (2 * k * scale), lon0 + width / (2 * k * scale)];
  const [vy0, vy1] = [lat0 - height / (2 * scale), lat0 + height / (2 * scale)];
  const visible = (r: Region) => r.box[2] >= vx0 && r.box[0] <= vx1 && r.box[3] >= vy0 && r.box[1] <= vy1;
  const path = (r: Region) =>
    r.rings.map((ring) => ring.map(([lon, lat], i) => {
      const p = project(lon, lat);
      return `${i ? "L" : "M"}${p.x.toFixed(1)},${p.y.toFixed(1)}`;
    }).join("") + "Z").join("");
  const home = STATES.find((st) => st.rings.some((ring) => insideRing(spec.places[0].lon, spec.places[0].lat, ring)));
  const delays = useStagger(spec.places.length, 8, 6).map((d) => d + Math.max(0, zoomEnd - 8));
  return (
    <Stage>
      <svg width={width} height={height} style={{position: "absolute", inset: 0}}>
        {COUNTRIES.filter(visible).map((c) => (
          <path key={c.name} d={path(c)} fill="#141922" stroke="rgba(237, 237, 232, 0.22)" strokeWidth={1.5} />
        ))}
        {STATES.filter(visible).map((st) => (
          <path key={st.uf} d={path(st)} fill={st === home ? "#1C2330" : "none"}
            stroke={st === home ? "rgba(242, 177, 52, 0.45)" : "rgba(237, 237, 232, 0.12)"}
            strokeWidth={st === home ? 2 : 1} />
        ))}
      </svg>
      {STATES.filter(visible).map((st) => {
        const p = project(st.label![0], st.label![1]);
        return (
          <div key={`label-${st.uf}`} style={{position: "absolute", left: p.x, top: p.y, transform: "translate(-50%, -50%)",
            opacity: (st === home ? 0.9 : 0.45) * (1 - t), fontSize: u(height, 26), fontWeight: 600, letterSpacing: 4,
            color: theme.muted, textTransform: "uppercase", whiteSpace: "nowrap"}}>{st.name}</div>
        );
      })}
      {spec.places.map((place, i) => {
        const {x, y} = project(place.lon, place.lat);
        // Vizinho próximo no enquadramento final: o pino mais ao sul leva o rótulo para baixo.
        const f = final(place.lon, place.lat);
        const labelBelow = spec.places.some((other, j) => {
          const q = final(other.lon, other.lat);
          const close = j !== i && Math.abs(q.x - f.x) < u(height, 320) && Math.abs(q.y - f.y) < u(height, 90);
          return close && (f.y > q.y || (f.y === q.y && i > j));
        });
        const shown = interpolate(frame, [delays[i], delays[i] + 10], [0, 1], clamp);
        const pulse = 1 + 0.35 * Math.sin((frame - delays[i]) / 6);
        return (
          <div key={place.name} style={{position: "absolute", left: x, top: y, opacity: shown}}>
            <div style={{position: "absolute", width: u(height, 26), height: u(height, 26), borderRadius: "50%",
              background: theme.accent, transform: "translate(-50%, -50%)"}} />
            <div style={{position: "absolute", width: u(height, 26), height: u(height, 26), borderRadius: "50%",
              border: `2px solid ${theme.accent}`, transform: `translate(-50%, -50%) scale(${pulse * 1.8})`, opacity: 0.5}} />
            <div style={{position: "absolute", left: u(height, 30), top: labelBelow ? u(height, 14) : -u(height, 54),
              whiteSpace: "nowrap", fontSize: u(height, 40), fontWeight: 700,
              textShadow: `0 0 12px ${theme.bg}`}}>{place.name}</div>
          </div>
        );
      })}
    </Stage>
  );
};

// --- Despacho por tipo --------------------------------------------------------------------------

export const ShotView: React.FC<ShotProps> = ({spec, media: path, frames, credit, aspect, overlay}) => {
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
      return <LowerThird spec={spec} overlay={overlay} />;
    case "chart":
      return <Chart spec={spec} />;
    case "timeline":
      return <Timeline spec={spec} />;
    case "family_tree":
      return <FamilyTree spec={spec} />;
    case "map":
      return <MapPins spec={spec} frames={frames} />;
  }
};
