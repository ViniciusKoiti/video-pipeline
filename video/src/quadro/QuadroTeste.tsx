import React, {useEffect, useState} from "react";
import {AbsoluteFill, Sequence, continueRender, delayRender, interpolate, useCurrentFrame} from "remotion";
import {Callout, Stepped, StyleProvider, StyleTexture, pencilSketchStyle} from "@viniciuskoitin/motion-kit/styles";
import antonUrl from "../clipe/fonts/Anton-Regular.ttf";
import {Banda, Chapado, Hachura, Papel, Tinta} from "./componentes";
import {curva, elipse, encadeia, fecha, poligono, reta, retangulo} from "./tinta";

// Teste de estilo "desenho à mão" (docs/pesquisa/estilo-desenho-a-mao-2026-11-03.md). Fora do contrato do
// episódio, como o `Clipe`: não entra em `Scene` nem em nenhum vídeo existente. Sem narração. Os traços vêm de
// `tinta.ts` (geometria própria, testada) e os componentes de `componentes.tsx`. Personagem é forma nossa.

export const QUADRO_W = 1920;
export const QUADRO_H = 1080;
export const QUADRO_FPS = 30;
export const QUADRO_FRAMES = 600;

const INK = "#161616";
const PAPER = "#F3E9D2";
const GREEN = "#3B8E5A";
const PINK = "#E7A3AE";
const OCRE = "#D9B26A";
const WHITE = "#FFFDF7";
const SOMBRA = "#5b4a2a";

const base = pencilSketchStyle({accent: "green"});
const estilo: typeof base = {
  ...base,
  slug: "quadro-teste",
  theme: {...base.theme, bg: PAPER, surface: PAPER, text: INK, line: INK, accent: GREEN, font: "'Inter', sans-serif"},
  line: {...base.line, width: 8, wobble: 2.5, passes: 1, boilEvery: 4, cap: "round"},
  fonts: [],
};

const ANTON = "Anton, 'DejaVu Sans Condensed', sans-serif";

// Anton carregada uma vez, antes do primeiro quadro (mesmo padrão do `Clipe`).
function useAnton(): boolean {
  const [handle] = useState(() => delayRender("fonte do quadro de teste"));
  const [pronta, setPronta] = useState(false);
  useEffect(() => {
    new FontFace("Anton", `url(${antonUrl}) format("truetype")`)
      .load()
      .then((face) => {
        document.fonts.add(face);
        setPronta(true);
      })
      .finally(() => continueRender(handle));
  }, [handle]);
  return pronta;
}

// Caixa padrão de personagem e de objeto: todas as camadas usam o mesmo quadro de coordenadas.
const CAIXA = {largura: 400, altura: 460};

// Membro direito: sobe da lateral até o selo. Só os braços e as pernas trocam de posição, em passos; o corpo fica
// parado (hold). Este componente tem que ficar dentro de `<Stepped>`: é ele que lê o quadro já congelado.
function BracoDireito({at, duracao}: {at: number; duracao: number}) {
  const f = useCurrentFrame();
  const t = interpolate(f, [at, at + duracao], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <Tinta pontos={curva([290, 230], [300 + t * 60, 240 - t * 60], [300 + t * 120, 250 - t * 150])}
      espessura={9} cor={INK} semente={61} at={0} duracao={0} {...CAIXA} />
  );
}

// Corpo arredondado (um oval, e não a gota verde do mascote do vendedor de referência). Centro (200, 200).
const CORPO = elipse(200, 200, 120, 136, 96);
const SOMBRA_CHAO = elipse(200, 376, 118, 18, 60);
const OLHO_E = elipse(165, 175, 22, 22, 48);
const OLHO_D = elipse(235, 175, 22, 22, 48);
const PUPILA_E = elipse(169, 179, 8, 8, 24);
const PUPILA_D = elipse(239, 179, 8, 8, 24);

function Personagem({expressao, cx, cy}: {expressao: "neutro" | "ansioso"; cx: number; cy: number}) {
  const sobrancelhas = expressao === "ansioso"
    ? {e: reta([140, 146], [190, 160]), d: reta([210, 160], [260, 146])}
    : {e: curva([142, 158], [165, 146], [190, 158]), d: curva([210, 158], [235, 146], [258, 158])};
  return (
    <div style={{position: "absolute", left: cx - 200, top: cy - 200, width: CAIXA.largura, height: CAIXA.altura}}>
      <Hachura pontos={SOMBRA_CHAO} espaco={11} angulo={-40} peso={2.5} cor={SOMBRA} {...CAIXA} />
      <Chapado pontos={CORPO} cor={OCRE} dx={7} dy={5} {...CAIXA} />
      <Tinta pontos={CORPO} espessura={10} cor={INK} fechado semente={11} at={0} duracao={22} {...CAIXA} />
      <Chapado pontos={OLHO_E} cor={WHITE} at={6} duracao={10} {...CAIXA} />
      <Chapado pontos={OLHO_D} cor={WHITE} at={6} duracao={10} {...CAIXA} />
      <Tinta pontos={OLHO_E} espessura={5} cor={INK} fechado semente={21} at={6} duracao={12} {...CAIXA} />
      <Tinta pontos={OLHO_D} espessura={5} cor={INK} fechado semente={22} at={6} duracao={12} {...CAIXA} />
      <Chapado pontos={PUPILA_E} cor={INK} at={8} duracao={6} {...CAIXA} />
      <Chapado pontos={PUPILA_D} cor={INK} at={8} duracao={6} {...CAIXA} />
      <Tinta pontos={sobrancelhas.e} espessura={6} cor={INK} semente={31} at={10} duracao={10} {...CAIXA} />
      <Tinta pontos={sobrancelhas.d} espessura={6} cor={INK} semente={32} at={10} duracao={10} {...CAIXA} />
      <Tinta pontos={curva([170, 232], [200, 252], [230, 232])} espessura={6} cor={INK} semente={41} at={14}
        duracao={10} {...CAIXA} />
      <Stepped fps={12}>
        <BracoDireito at={18} duracao={42} />
      </Stepped>
      <Tinta pontos={curva([112, 215], [70, 232], [70, 262])} espessura={9} cor={INK} semente={51} at={4}
        duracao={10} {...CAIXA} />
      <Tinta pontos={reta([150, 330], [140, 430])} espessura={9} cor={INK} semente={52} at={8} duracao={10}
        {...CAIXA} />
      <Tinta pontos={reta([250, 330], [262, 430])} espessura={9} cor={INK} semente={53} at={8} duracao={10}
        {...CAIXA} />
    </div>
  );
}

function Caderno({x, y}: {x: number; y: number}) {
  const caixa = {largura: 120, altura: 90};
  return (
    <div style={{position: "absolute", left: x, top: y, width: 120, height: 90}}>
      <Tinta pontos={retangulo(0, 0, 120, 90, 30)} espessura={6} cor={INK} fechado semente={71} at={2} duracao={14}
        {...caixa} />
      <Tinta pontos={reta([16, 26], [104, 26])} espessura={4} cor={INK} semente={72} at={10} duracao={12} {...caixa} />
      <Tinta pontos={reta([16, 46], [104, 46])} espessura={4} cor={INK} semente={73} at={10} duracao={12} {...caixa} />
      <Tinta pontos={reta([16, 66], [84, 66])} espessura={4} cor={INK} semente={74} at={10} duracao={12} {...caixa} />
    </div>
  );
}

function Cena1() {
  const f = useCurrentFrame();
  const opacidade = interpolate(f, [0, 12], [0, 1], {extrapolateRight: "clamp"});
  return (
    <AbsoluteFill>
      <div style={{position: "absolute", left: 160, top: 220, fontFamily: ANTON, fontSize: 150, lineHeight: 1.02,
        color: INK, textTransform: "uppercase", opacity: opacidade}}>
        Quanto sobra<br />no fim do mês?
      </div>
      <div style={{position: "absolute", left: 160, top: 620}}>
        <Tinta pontos={curva([0, 14], [420, 0], [860, 16], 40)} espessura={16} cor={GREEN} at={30} duracao={24}
          largura={860} altura={36} />
      </div>
      <div style={{position: "absolute", left: 160, top: 690, fontFamily: "Inter, sans-serif", fontSize: 44,
        color: INK, opacity: interpolate(f, [40, 56], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"})}}>
        Um exemplo, em quadro branco. Sem narração.
      </div>
    </AbsoluteFill>
  );
}

function Cena2() {
  return (
    <AbsoluteFill>
      <Caderno x={120} y={560} />
      <Personagem expressao="ansioso" cx={560} cy={560} />
      <Callout target={[690, 420]} offset={[180, -120]} at={28} duration={20} color={INK} labelSize={44}>
        William gasta tudo que recebe.
      </Callout>
    </AbsoluteFill>
  );
}

// Pote: contorno fechado de tinta; o líquido sobe em passos e é recortado pela forma do pote.
const POTE = fecha(encadeia(
  reta([100, 60], [100, 120]),
  curva([100, 120], [60, 140], [60, 220]),
  reta([60, 220], [60, 400]),
  curva([60, 400], [60, 420], [80, 420]),
  reta([80, 420], [280, 420]),
  curva([280, 420], [300, 420], [300, 400]),
  reta([300, 400], [300, 220]),
  curva([300, 220], [300, 140], [260, 120]),
  reta([260, 120], [260, 60]),
  reta([260, 60], [100, 60]),
));
const CAIXA_POTE = {largura: 340, altura: 440};

function Enchimento() {
  const f = useCurrentFrame();
  const nivel = interpolate(f, [20, 110], [0, 300], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  return (
    <div style={{position: "absolute", inset: 0, clipPath: `path('${poligono(POTE)}')`}}>
      <div style={{position: "absolute", left: 0, right: 0, bottom: 0, height: nivel, background: GREEN}} />
    </div>
  );
}

function Cena3() {
  const f = useCurrentFrame();
  const valor = interpolate(f, [0, 90], [500, 6250], {extrapolateRight: "clamp"});
  const texto = "R$ " + Math.round(valor).toLocaleString("pt-BR");
  return (
    <AbsoluteFill>
      <div style={{position: "absolute", left: 160, top: 180, fontFamily: ANTON, fontSize: 130, color: INK}}>
        {texto}
      </div>
      <div style={{position: "absolute", left: 160, top: 372, fontFamily: "Inter, sans-serif", fontSize: 44, color: INK}}>
        poupando R$ 500 por mês, em renda fixa
      </div>
      <div style={{position: "absolute", left: 1180, top: 300, width: CAIXA_POTE.largura, height: CAIXA_POTE.altura}}>
        <Stepped fps={12}>
          <Enchimento />
        </Stepped>
        <Hachura pontos={retangulo(236, 140, 292, 412, 40)} espaco={9} angulo={-55} peso={2} cor={SOMBRA}
          {...CAIXA_POTE} />
        <Tinta pontos={POTE} espessura={10} cor={INK} fechado semente={81} at={0} duracao={24} {...CAIXA_POTE} />
      </div>
    </AbsoluteFill>
  );
}

function Selo({x, y, texto, at, cor}: {x: number; y: number; texto: string; at: number; cor: string}) {
  const f = useCurrentFrame();
  const opacidade = interpolate(f, [at + 12, at + 22], [0, 1], {extrapolateLeft: "clamp", extrapolateRight: "clamp"});
  const circulo = elipse(120, 120, 110, 110, 72);
  return (
    <div style={{position: "absolute", left: x, top: y, width: 240, height: 240}}>
      <Chapado pontos={circulo} cor={cor} dx={6} dy={5} largura={240} altura={240} at={at} duracao={18} />
      <Tinta pontos={circulo} espessura={9} cor={INK} fechado semente={90 + at} at={at} duracao={22}
        largura={240} altura={240} />
      <div style={{position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center",
        fontFamily: ANTON, fontSize: 44, color: INK, textTransform: "uppercase", opacity: opacidade}}>
        {texto}
      </div>
    </div>
  );
}

function Cena4() {
  return (
    <AbsoluteFill>
      <Selo x={300} y={300} texto="Poupar" at={0} cor={GREEN} />
      <Selo x={840} y={300} texto="Reservar" at={20} cor={PINK} />
      <Selo x={1380} y={300} texto="Investir" at={40} cor={OCRE} />
      <div style={{position: "absolute", left: 160, top: 760, fontFamily: "Inter, sans-serif", fontSize: 40, color: INK}}>
        Teste de estilo. Não publicar.
      </div>
    </AbsoluteFill>
  );
}

function Cena() {
  const pronta = useAnton();
  if (!pronta) return null;
  return (
    <AbsoluteFill style={{background: PAPER}}>
      <Papel largura={QUADRO_W} altura={QUADRO_H} />
      <StyleTexture grain={0.1} vignette={0.05} />
      <Banda largura={QUADRO_W} altura={QUADRO_H} espessura={40} cor={GREEN} margem={24} />
      <Sequence from={0} durationInFrames={120}><Cena1 /></Sequence>
      <Sequence from={120} durationInFrames={180}><Cena2 /></Sequence>
      <Sequence from={300} durationInFrames={150}><Cena3 /></Sequence>
      <Sequence from={450} durationInFrames={150}><Cena4 /></Sequence>
    </AbsoluteFill>
  );
}

export const QuadroTeste: React.FC = () => (
  <StyleProvider style={estilo}>
    <Cena />
  </StyleProvider>
);
