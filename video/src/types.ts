// Espelho dos planos do contrato (app/pipeline/schemas.py, ADR 008). Chaves em snake_case como no JSON.

import type {SpriteManifest} from "@viniciusk/motion-kit/host";

export type Crop = {x: number; y: number; width: number; height: number};
export type Motion = "push_in" | "pull_out" | "pan_left" | "pan_right" | "pan_up" | "pan_down" | "still";

type Base = {anchor: string};
export type VisualNeed = "historical_exact" | "contextual_stock" | "map_or_graphic" | "illustrative_reconstruction";
export type PhotoSpec = Base & {kind: "photo"; visual_need?: VisualNeed; crop?: Crop | null; motion?: Motion};
export type BrollSpec = Base & {kind: "broll"};
export type NumberSpec = Base & {kind: "number"; value: string; label: string};
export type ChartSpec = Base & {
  kind: "chart";
  title: string;
  unit?: string;
  points: {label: string; value: number}[];
  type?: "bar" | "bar_horizontal" | "line" | "share"; // ADR 011
  highlight?: string | null; // rótulo do ponto em destaque; sem ele, nenhum destaque
  y_from_zero?: boolean; // só line
  rest?: string | null; // só share
};
export type QuoteSpec = Base & {
  kind: "quote";
  text: string;
  attribution: string;
  style?: "quote" | "headline" | "document";
  document?: {title: string; issuer?: string; date?: string} | null; // ADR 011
  variant?: "report" | "newspaper" | "letter";
};
export type MapSpec = Base & {
  kind: "map";
  places: {name: string; lat: number; lon: number}[];
  scope?: "region" | "world"; // ADR 011
  highlight?: string[]; // "BRA", "BR-SP"
  routes?: {from: string; to: string}[]; // nomes de places
};
export type StampSpec = Base & {kind: "stamp"; date: string; place?: string};
export type LowerThirdSpec = Base & {kind: "lower_third"; name: string; role: string};
export type TimelineSpec = Base & {
  kind: "timeline";
  events: {date: string; label: string; when?: string | null}[]; // when: ano ou data ISO (ADR 011)
};
export type FamilyTreeSpec = Base & {
  kind: "family_tree";
  people: {id: string; name: string; role?: string; parent_ids?: string[]}[];
};

// Planos editoriais (ADR 011).
export type CompareSpec = Base & {
  kind: "compare";
  left: {value: string; label: string};
  right: {value: string; label: string};
  mode?: "side" | "before_after" | "scale";
  emphasis?: "left" | "right" | null;
};
export type NodeKind = "person" | "family" | "company" | "bank" | "government" | "other";
export type NetworkSpec = Base & {
  kind: "network";
  root: string;
  nodes: {id: string; label: string; role?: string; kind: NodeKind}[];
  edges: {from: string; to: string; label?: string; value?: string; style?: "solid" | "dashed"; flow?: boolean}[];
  steps: {anchor: string; nodes?: string[]; highlight?: string[]}[];
  layout?: "radial" | "layered";
};
export type KeywordSpec = Base & {kind: "keyword"; text: string; highlight?: string};

// Planos dos Reels (ADR 028). As partes com `anchor` entram no quadro de `stepFrames`, na ordem em que aparecem.
export type Operator = "+" | "−" | "×" | "÷";
export type CalculationSpec = Base & {
  kind: "calculation";
  terms: {text: string; label?: string; op?: Operator | null; anchor?: string | null}[];
  result: {text: string; label?: string; anchor: string};
};
export type ReceiptSpec = Base & {
  kind: "receipt";
  title?: string;
  items: {label: string; value: string; detail?: string; anchor?: string | null}[];
  total?: {label?: string; value: string; anchor: string} | null;
};
export type HookSpec = Base & {kind: "hook"; text: string; highlight?: string};
export type EndCardSpec = Base & {kind: "end_card"; variant: "save" | "follow" | "next"; text: string; sub?: string};

export type ShotSpec =
  | PhotoSpec | BrollSpec | NumberSpec | ChartSpec | QuoteSpec | MapSpec | StampSpec | LowerThirdSpec
  | TimelineSpec | FamilyTreeSpec | CompareSpec | NetworkSpec | KeywordSpec
  | CalculationSpec | ReceiptSpec | HookSpec | EndCardSpec;

// Série do vídeo, no selo do cartão final (ADR 028).
export type Series = {name: string; part: number; total: number};

export type ShotProps = {
  from: number;
  frames: number;
  spec: ShotSpec;
  media?: string | null;
  credit?: string;
  aspect?: number; // largura/altura da imagem (foto), para o cartão seguir a proporção e o recorte ser exato
  overlay?: boolean; // tarja ou número sobre a foto ou o B-roll anterior (calculado em Scene.tsx, não vem do contrato)
  source?: string; // "Fonte: …" do rodapé, derivado das claims (ADR 011)
  sourceFlag?: string; // ressalva ao lado da fonte ("fonte interessada")
  stepFrames?: number[]; // network, calculation e receipt: quadro de entrada de cada parte, relativo ao plano
  series?: Series; // só end_card, quando o episódio tem série
  // Só broll como textura (ADR 031): quadro do clipe em que o plano começa (continua da mídia anterior) e
  // tamanho do clipe, quando o plano é mais longo que ele e o vídeo recomeça
  startFrom?: number;
  loopFrames?: number;
};
export type Cue = {from: number; to: number; text: string};
// Palavra com tempo (quadros relativos à cena), da legenda palavra a palavra (ADR 023).
export type Word = {from: number; to: number; text: string};

// Apresentador em janela flutuante (ADR 013): o motor já resolve o canto de cada cena e o envelope da boca.
export type HostCorner = "top-left" | "top-right" | "bottom-left" | "bottom-right";
export type HostProps = {
  // `skin` e as peças do Notionists, como o <Host> do motion-kit as lê; a pele `dono` só tem o `skin`
  identity: Record<string, unknown>;
  sprites?: string; // só na pele `dono`: hash das imagens, para o cache da cena acompanhar o desenho
  manifest?: SpriteManifest; // só na pele `dono` em camadas (ADR 029): o `host/dono/sprites.json`
  width: number; // largura da janela, fração do quadro
  corner: HostCorner;
  fromCorner: HostCorner | null; // canto da cena anterior; null na primeira
  levels: number[]; // energia da fala por quadro, de 0 a 1
  direction?: HostSceneDirection; // ADR 029; ausente nas props antigas
};

// Direção automática do apresentador (ADR 029, app/media/host.py), em quadros relativos à cena: para onde
// olha, a expressão pela entrega da fala e os gestos (o ciclo de gesticular, ou ele com o apontar por cima).
export type HostSceneDirection = {
  look: "front" | "left" | "right";
  expression: string;
  gesticulate?: boolean;
  gestures?: {at: number; gesture: string}[];
};

// Idioma do episódio (episode.json). Ausente nas props = pt-BR: o adaptador só o envia fora do padrão.
export type Language = "en" | "pt-BR";

export type SceneProps = {
  width: number;
  height: number;
  fps: number;
  frames: number;
  fadeFrames: number;
  fadeIn?: boolean; // false na primeira cena: o vídeo começa sem fade (ADR 028)
  fadeOut?: boolean; // false quando o mesmo B-roll continua na cena seguinte (ADR 031)
  shots: ShotProps[];
  cues: Cue[];
  words?: Word[]; // só no vertical, quando a cena tem palavras reconhecidas
  host?: HostProps;
  language?: Language;
};
