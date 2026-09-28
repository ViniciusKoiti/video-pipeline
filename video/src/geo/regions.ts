import type {GeoBox, GeoRegion, LonLat} from "@viniciusk/motion-kit/geo";
import southAmerica from "./america-do-sul.json";
import world from "./world-110m.json";

// Contornos por escopo do plano de mapa (ADR 011). Os `id` são os códigos de `map.highlight`; o `vp check`
// confere os códigos contra estes mesmos arquivos (region_codes em app/render/remotion.py).

type RawRegion = {id: string; name?: string; rings: number[][][]; label?: number[]; labelAt?: number[]};

const toRegion = (r: RawRegion, label?: string): GeoRegion => ({
  id: r.id,
  rings: r.rings as LonLat[][],
  label: label ?? r.name,
  labelAt: (r.label ?? r.labelAt) as LonLat | undefined,
});

const SA_COUNTRIES = (southAmerica.countries as RawRegion[]).map((c) => toRegion(c));
const BR_STATES = (southAmerica.states as RawRegion[]).map((s) => toRegion(s));
const SA_NAMES = new Map(SA_COUNTRIES.map((c) => [c.id, c.label]));
const WORLD = (world as RawRegion[]).map((c) => toRegion(c, SA_NAMES.get(c.id)));

// Mundo com os estados do Brasil por cima; região = América do Sul em 1:50m, com mais detalhe.
export const regionsFor = (scope: "region" | "world"): GeoRegion[] =>
  scope === "world" ? [...WORLD, ...BR_STATES] : [...SA_COUNTRIES, ...BR_STATES];

export const WORLD_BOX: GeoBox = {west: -130, south: -56, east: 150, north: 72};

const insideRing = (lon: number, lat: number, ring: LonLat[]) => {
  let inside = false;
  for (let i = 0, j = ring.length - 1; i < ring.length; j = i++) {
    const [xi, yi] = ring[i];
    const [xj, yj] = ring[j];
    if (yi > lat !== yj > lat && lon < ((xj - xi) * (lat - yi)) / (yj - yi) + xi) inside = !inside;
  }
  return inside;
};

const boxOfRings = (rings: LonLat[][]): GeoBox => {
  const pts = rings.flat();
  return {
    west: Math.min(...pts.map((p) => p[0])), south: Math.min(...pts.map((p) => p[1])),
    east: Math.max(...pts.map((p) => p[0])), north: Math.max(...pts.map((p) => p[1])),
  };
};

// Caixa em volta dos lugares, com um mínimo de latitude visível para sobrar referência (litoral, divisa).
export const boxAround = (places: {lat: number; lon: number}[], minSpan: number): GeoBox => {
  const lats = places.map((p) => p.lat);
  const lons = places.map((p) => p.lon);
  const midLat = (Math.min(...lats) + Math.max(...lats)) / 2;
  const midLon = (Math.min(...lons) + Math.max(...lons)) / 2;
  const halfLat = Math.max((Math.max(...lats) - Math.min(...lats)) / 2, minSpan / 2);
  const halfLon = Math.max((Math.max(...lons) - Math.min(...lons)) / 2, minSpan / 2);
  return {west: midLon - halfLon, south: midLat - halfLat, east: midLon + halfLon, north: midLat + halfLat};
};

// Câmera do mapa: de longe (o estado do primeiro lugar, ou o mundo) até os lugares.
export const mapBoxes = (places: {lat: number; lon: number}[], scope: "region" | "world"): [GeoBox, GeoBox] => {
  if (scope === "world") return [WORLD_BOX, boxAround(places, 12)];
  const [first] = places;
  const home = BR_STATES.find((s) => s.rings.some((ring) => insideRing(first.lon, first.lat, ring)));
  const wide = home ? boxOfRings(home.rings) : boxAround(places, 10);
  return [wide, boxAround(places, 1.5)];
};
