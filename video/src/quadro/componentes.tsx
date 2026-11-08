import React, {useId} from "react";
import {Easing, interpolate, useCurrentFrame} from "remotion";
import {contornoDeTraco, pontosAte, poligono, retangulo, ruido, tremer, type Ponto} from "./tinta";

// Componentes do traço "à mão" do quadro de teste. Cada um é uma camada absoluta na caixa em que está; a geometria
// vem de `tinta.ts` (testada). Nada aqui é arte de terceiros: é código sobre curvas próprias.

const camada = (largura: number, altura: number): React.CSSProperties => ({
  position: "absolute", left: 0, top: 0, width: largura, height: altura, overflow: "visible", pointerEvents: "none",
});

/** Progresso de 0 a 1 entre `at` e `at + duration`; `duration` 0 = já desenhado a partir de `at`. */
export function progressoDe(f: number, at: number, duration: number): number {
  if (duration <= 0) return f >= at ? 1 : 0;
  return interpolate(f, [at, at + duration], [0, 1], {
    extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.inOut(Easing.cubic),
  });
}

type Dimensoes = {largura: number; altura: number};

/**
 * Traço de tinta que se desenha. Aberto: espessura afina nas pontas. Fechado: contorno de espessura uniforme.
 * Treme a cada `boil` quadros (a linha "ferve"), com semente fixa por traço.
 */
export function Tinta({pontos, espessura, cor, at = 0, duracao = 20, semente = 0, tremor = 1.2, ferve = 4,
  fechado = false, largura, altura}: Dimensoes & {
  pontos: readonly Ponto[]; espessura: number; cor: string; at?: number; duracao?: number; semente?: number;
  tremor?: number; ferve?: number; fechado?: boolean;
}) {
  const f = useCurrentFrame();
  const p = progressoDe(f, at, duracao);
  if (p <= 0) return null;
  const quadro = ferve > 0 ? Math.floor(f / ferve) : 0;
  const d = contornoDeTraco(tremer(pontosAte(pontos, p), tremor, semente + quadro * 7.31), espessura, fechado);
  if (!d) return null;
  return (
    <svg width={largura} height={altura} style={camada(largura, altura)}>
      <path d={d} fill={cor} fillRule="evenodd" />
    </svg>
  );
}

/** Mancha chapada, com deslocamento (`dx`, `dy`): o desalinhamento de sobreposição de impressão. */
export function Chapado({pontos, cor, dx = 0, dy = 0, largura, altura, at = 0, duracao = 0}: Dimensoes & {
  pontos: readonly Ponto[]; cor: string; dx?: number; dy?: number; at?: number; duracao?: number;
}) {
  const f = useCurrentFrame();
  const p = progressoDe(f, at, duracao);
  if (p <= 0) return null;
  return (
    <svg width={largura} height={altura} style={{...camada(largura, altura), opacity: p}}>
      <path d={poligono(pontos)} fill={cor} transform={`translate(${dx} ${dy})`} />
    </svg>
  );
}

/** Sombra em hachura: linhas paralelas de passo `espaco`, presas à forma. */
export function Hachura({pontos, espaco = 12, angulo = -45, peso = 3, cor, largura, altura}: Dimensoes & {
  pontos: readonly Ponto[]; espaco?: number; angulo?: number; peso?: number; cor: string;
}) {
  const id = `hach${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  return (
    <svg width={largura} height={altura} style={camada(largura, altura)}>
      <defs>
        <pattern id={id} width={espaco} height={espaco} patternUnits="userSpaceOnUse"
          patternTransform={`rotate(${angulo})`}>
          <line x1={0} y1={0} x2={0} y2={espaco} stroke={cor} strokeWidth={peso} />
        </pattern>
      </defs>
      <path d={poligono(pontos)} fill={`url(#${id})`} />
    </svg>
  );
}

/** Manchas de papel: círculos de cor de ocre, transparentes nas bordas. Determinísticas pela semente. */
export function Papel({largura, altura, semente = 3, manchas = 9}: Dimensoes & {semente?: number; manchas?: number}) {
  const lista = Array.from({length: manchas}, (_, i) => ({
    x: ruido(semente, 4 * i) * largura,
    y: ruido(semente, 4 * i + 1) * altura,
    r: 160 + ruido(semente, 4 * i + 2) * 260,
    a: 0.02 + ruido(semente, 4 * i + 3) * 0.03,
  }));
  const id = `papel${useId().replace(/[^a-zA-Z0-9]/g, "")}`;
  return (
    <svg width={largura} height={altura} style={camada(largura, altura)}>
      <defs>
        {lista.map((m, i) => (
          <radialGradient id={`${id}-${i}`} key={i}>
            <stop offset="0" stopColor="#B88A4A" stopOpacity={m.a} />
            <stop offset="1" stopColor="#B88A4A" stopOpacity={0} />
          </radialGradient>
        ))}
      </defs>
      {lista.map((m, i) => <circle key={i} cx={m.x} cy={m.y} r={m.r} fill={`url(#${id}-${i})`} />)}
    </svg>
  );
}

/** Moldura de cor chapada, com a borda tremida. A área de dentro fica vazia (evenodd). */
export function Banda({largura, altura, espessura, cor, margem = 24, semente = 9, tremor = 3}: Dimensoes & {
  espessura: number; cor: string; margem?: number; semente?: number; tremor?: number;
}) {
  const fora = tremer(retangulo(margem, margem, largura - margem, altura - margem, 40), tremor, semente);
  const m = margem + espessura;
  const dentro = tremer(retangulo(m, m, largura - m, altura - m, 40), tremor, semente + 5);
  return (
    <svg width={largura} height={altura} style={camada(largura, altura)}>
      <path d={`${poligono(fora)} ${poligono(dentro)}`} fill={cor} fillRule="evenodd" />
    </svg>
  );
}
