// Espelho dos planos do contrato (app/pipeline/schemas.py, ADR 008). Chaves em snake_case como no JSON.

export type Crop = {x: number; y: number; width: number; height: number};
export type Motion = "push_in" | "pull_out" | "pan_left" | "pan_right" | "pan_up" | "pan_down" | "still";

type Base = {anchor: string};
export type PhotoSpec = Base & {kind: "photo"; crop?: Crop | null; motion?: Motion};
export type BrollSpec = Base & {kind: "broll"};
export type NumberSpec = Base & {kind: "number"; value: string; label: string};
export type ChartSpec = Base & {kind: "chart"; title: string; unit?: string; points: {label: string; value: number}[]};
export type QuoteSpec = Base & {kind: "quote"; text: string; attribution: string; style?: "quote" | "headline"};
export type MapSpec = Base & {kind: "map"; places: {name: string; lat: number; lon: number}[]};
export type StampSpec = Base & {kind: "stamp"; date: string; place?: string};
export type LowerThirdSpec = Base & {kind: "lower_third"; name: string; role: string};
export type TimelineSpec = Base & {kind: "timeline"; events: {date: string; label: string}[]};
export type FamilyTreeSpec = Base & {
  kind: "family_tree";
  people: {id: string; name: string; role?: string; parent_ids?: string[]}[];
};

export type ShotSpec =
  | PhotoSpec | BrollSpec | NumberSpec | ChartSpec | QuoteSpec | MapSpec | StampSpec | LowerThirdSpec
  | TimelineSpec | FamilyTreeSpec;

export type ShotProps = {
  from: number;
  frames: number;
  spec: ShotSpec;
  media?: string | null;
  credit?: string;
  aspect?: number; // largura/altura da imagem (foto), para o cartão seguir a proporção e o recorte ser exato
};
export type Cue = {from: number; to: number; text: string};

export type SceneProps = {
  width: number;
  height: number;
  fps: number;
  frames: number;
  fadeFrames: number;
  shots: ShotProps[];
  cues: Cue[];
};
