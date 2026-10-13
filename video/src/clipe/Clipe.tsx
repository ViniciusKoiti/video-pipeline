import React, {useEffect, useState} from "react";
import {
  AbsoluteFill, Audio, continueRender, delayRender, Img, random, Sequence, staticFile, useCurrentFrame, useVideoConfig,
} from "remotion";
import antonUrl from "./fonts/Anton-Regular.ttf";
import cinzelUrl from "./fonts/Cinzel.ttf";
import plexUrl from "./fonts/IBMPlexMono-Regular.ttf";
import letra from "./letra.json";
import brasaoUrl from "./marca/brasao.svg";

// Clipe de letra (tipografia cinética) de "A Planilha é Tua". Fora do contrato `episode.json`: a única
// entrada é `letra.json` (tempo por palavra, de `scripts/provisorio/clipe_tempos.py`) e o áudio no publicDir.
// Duas vozes, duas letras: o poder em serifada de inscrição (Cinzel), o eu em condensada pesada (Anton); as
// falas secas (intro, ponte, outro) em monoespaçada (IBM Plex Mono). Todas SIL OFL 1.1 (`fonts/*-OFL.txt`).
// O brasão do Nabote (`marca/brasao.svg`, de nabote.com.br/marca/) fica num canto e fecha o clipe com "Nabote.".
// Nos cortes (`fecho`), `fim` é o tempo forte em que o próximo verso entraria: ali o som passa para o final da
// própria música (CAUDA) e o último verso se dissolve na tela de fecho (brasão, título, "clipe completo no canal").

export type ClipeProps = {inicio: number; fim: number | null; audio: string | null; retrato: boolean; fecho?: boolean};
type Palavra = {t: string; ini: number; ok: boolean};
type Linha = {secao: string; vez: number; texto: string; ini: number; fim: number; palavras: Palavra[]};

const LINHAS = letra.linhas as Linha[];
export const CLIPE_FPS = 30;
export const CLIPE_PADRAO: ClipeProps = {inicio: 0, fim: null, audio: null, retrato: false, fecho: false};
// Os últimos segundos da faixa: a textura cai em 192,8 s e a música para sozinha em ~195,2 s. O final entra
// nesse ponto, sem antecipar a passagem: antes dele a parte final é alta e soaria como estalo.
const CAUDA = 192.8;
const comFecho = (props: ClipeProps) => Boolean(props.fecho && props.fim !== null);
export const clipeMetadata = ({props}: {props: ClipeProps}) => ({
  fps: CLIPE_FPS,
  width: props.retrato ? 1080 : 1920,
  height: props.retrato ? 1920 : 1080,
  durationInFrames: Math.max(1, Math.round(
    ((props.fim ?? letra.duracao) - props.inicio + (comFecho(props) ? letra.duracao - CAUDA : 0)) * CLIPE_FPS)),
});

// Cores do site do Nabote (nabote.com.br, lidas em 2026-10-08): fundo, texto, dourado (`--gold`, a cor primária)
// e vermelho (`--destructive`) dos temas escuro e claro. O dourado é a voz do poder; o vermelho, só o sangue.
const COR = {preto: "#0a0b0e", osso: "#efebe1", claro: "#faf9f7", tinta: "#1d1e22", ouro: "#d8b45e",
  ouroEscuro: "#8f682b", sangue: "#db4241", sangueEscuro: "#be222a"};
const TEMA = {
  escuro: {bg: COR.preto, fg: COR.osso, forte: COR.sangue, poder: COR.ouro},
  claro: {bg: COR.claro, fg: COR.tinta, forte: COR.sangueEscuro, poder: COR.ouroEscuro},
  sangue: {bg: COR.sangueEscuro, fg: COR.osso, forte: COR.preto, poder: COR.osso},
};
const ANTON = "Anton, 'DejaVu Sans Condensed', sans-serif";
const CINZEL = "Cinzel, 'DejaVu Serif', serif";
const MONO = "'IBM Plex Mono', 'DejaVu Sans Mono', monospace";
const PODER = new Set([
  "estado", "perito", "toga", "tribunal", "stf", "marmore", "altar", "cargo", "divindade", "guardiao", "plano",
  "tecnica", "calculo", "tradicao", "destino", "gloria", "paraiso", "planilha", "relatorio", "grafico", "acabe",
]);
const SANGUE = new Set(["sangra", "mataste", "nabote", "terror"]);
const MONO_SECOES = new Set(["intro", "ponte", "outro"]);
const POP = 4; // quadros da entrada de cada palavra (escala e opacidade, sem quique)
const SEGURA = 1.0; // s que um verso fica depois do fim, quando o próximo demora (no outro, até o próximo)
const EMENDA = 6; // quadros da passagem do som do corte para o final da música
const DISSOLVE = 8; // quadros em que a tela de fecho aparece sobre o último verso

const norm = (word: string) => word.toLowerCase().normalize("NFD").replace(/[^a-z0-9]/g, "");
const clamp = (x: number) => Math.min(1, Math.max(0, x));
const saida = (x: number) => 1 - (1 - clamp(x)) ** 3;
const quadro = (s: number) => Math.round(s * CLIPE_FPS);

// Efeito próprio de alguns versos, escolhido pelo texto (a letra é fixa).
const efeito = (linha: Linha): string | null => {
  const texto = norm(linha.texto);
  if (MONO_SECOES.has(linha.secao)) return null;
  if (texto.startsWith("oplanoecego")) return "apaga";
  if (texto.startsWith("setudoepolitico")) return "mosaico";
  if (texto.startsWith("tuescreve")) return "tacha";
  if (texto.startsWith("queliberdadeeessa")) return "contorno";
  return null;
};

// Quebra em fileiras: na pontuação e no limite de caracteres. Cada fileira é escalada para a largura da caixa.
const fileiras = (palavras: Palavra[], indices: number[], maxc: number): number[][] => {
  const out: number[][] = [[]];
  let len = 0;
  indices.forEach((k, pos) => {
    const size = palavras[k].t.length;
    if (len > 0 && len + 1 + size > maxc) {
      out.push([]);
      len = 0;
    }
    out[out.length - 1].push(k);
    len += (len > 0 ? 1 : 0) + size;
    if (/[,?.!]$/.test(palavras[k].t) && pos < indices.length - 1 && len >= 5) {
      out.push([]);
      len = 0;
    }
  });
  return out.filter((row) => row.length > 0);
};

// Cada verso usa um dos três temas: escuro (padrão), claro (pré-refrão alternado e segunda vez) e sangue ("Mataste").
const paleta = (linha: Linha, indice: number) => {
  const invertida = linha.vez === 2;
  if (linha.secao === "refrao") {
    if (norm(linha.texto).startsWith("mataste")) return TEMA.sangue;
    return invertida ? TEMA.claro : TEMA.escuro;
  }
  if (linha.secao === "pre") return (indice % 2 === 0) !== invertida ? TEMA.claro : TEMA.escuro;
  return TEMA.escuro;
};

const useFontes = () => {
  const [handle] = useState(() => delayRender("fontes do clipe"));
  useEffect(() => {
    const faces = [
      new FontFace("Anton", `url(${antonUrl}) format("truetype")`),
      new FontFace("Cinzel", `url(${cinzelUrl}) format("truetype")`, {weight: "400 900"}),
      new FontFace("IBM Plex Mono", `url(${plexUrl}) format("truetype")`),
    ];
    Promise.all(faces.map((face) => face.load().then((loaded) => document.fonts.add(loaded))))
      .catch((error) => console.error("fonte do clipe não carregou; usando DejaVu", error))
      .finally(() => continueRender(handle));
  }, [handle]);
};

export const Clipe: React.FC<ClipeProps> = (props) => {
  const {inicio, fim, audio} = props;
  useFontes();
  const local = useCurrentFrame();
  const {width, height, durationInFrames} = useVideoConfig();
  const retrato = height > width;
  const fechando = comFecho(props);
  const corteLocal = fechando && fim !== null ? quadro(fim) - quadro(inicio) : durationInFrames;
  // Na tela de fecho a letra fica parada no último quadro antes do corte, por baixo do dissolve.
  const frame = Math.min(local, corteLocal - 1) + quadro(inicio);
  const t = frame / CLIPE_FPS;

  // Área segura das plataformas no vertical (ADR 014: topo 288, base 500, direita 140, esquerda 60 em 1080×1920).
  const k = height / 1920;
  // No vertical o brasão ocupa uma faixa no alto da área segura; no horizontal cabe na margem do canto.
  const faixa = retrato ? 150 * k : 0;
  const caixa = retrato
    ? {top: 288 * k + faixa, bottom: 500 * k, left: 60 * k, right: 140 * k}
    : {top: height * 0.08, bottom: height * 0.08, left: width * 0.08, right: width * 0.08};
  // O SVG do brasão tem margem própria (o desenho ocupa ~2/3 do quadro), por isso a caixa é maior que o desenho.
  const lado = retrato ? 210 * k : height * 0.15;
  const fecho = retrato ? (width - 200 * k) * 1.05 : (height * 0.84) * 0.66; // brasão da tela final
  const selo = (
    <Img src={brasaoUrl} style={{position: "absolute", width: lado, height: lado,
      ...(retrato ? {top: 288 * k - 30 * k, left: 60 * k - 36 * k} : {top: height * 0.005, right: width * 0.012})}} />
  );
  const boxW = width - caixa.left - caixa.right;
  const boxH = height - caixa.top - caixa.bottom;

  let indice = -1;
  LINHAS.forEach((linha, i) => {
    if (linha.ini <= t) indice = i;
  });
  const linha = indice >= 0 ? LINHAS[indice] : null;
  const proxima = indice + 1 < LINHAS.length ? LINHAS[indice + 1] : null;
  const ultima = linha !== null && proxima === null; // "Nabote." fica até o fim
  const segura = linha?.secao === "outro" ? Infinity : SEGURA;
  // No corte, o verso que termina no corte fica até a tela de fecho.
  const ateOCorte = fechando && fim !== null && proxima !== null && proxima.ini >= fim - 0.05;
  const visivel = linha !== null
    && (ultima || ateOCorte || t < Math.min(proxima ? proxima.ini : Infinity, linha.fim + segura));
  // Nos cortes o som entra em 3 quadros; sem fecho sai em 10, com fecho passa em EMENDA quadros para o final da música.
  const som = !audio ? null : fechando ? (
    <>
      <Sequence durationInFrames={corteLocal} layout="none">
        <Audio src={staticFile(audio)} trimBefore={quadro(inicio)}
          volume={(f) => Math.min(1, (f + 1) / 3, (corteLocal - f) / EMENDA)} />
      </Sequence>
      <Sequence from={corteLocal - EMENDA} layout="none">
        <Audio src={staticFile(audio)} trimBefore={quadro(CAUDA)}
          volume={(f) => Math.min(1, (f + 1) / EMENDA)} />
      </Sequence>
    </>
  ) : (
    <Audio src={staticFile(audio)} trimBefore={quadro(inicio)}
      volume={(f) => Math.min(1, (f + 1) / 3, (durationInFrames - f) / 10)} />
  );
  // Tela de fecho dos cortes: brasão, título e chamada para o clipe completo, sobre o último verso parado.
  const tela = fechando && local >= corteLocal ? (
    <AbsoluteFill style={{background: COR.preto, opacity: clamp((local - corteLocal + 1) / DISSOLVE),
      display: "flex", flexDirection: "column", justifyContent: "center", alignItems: "center",
      paddingBottom: retrato ? (500 - 288) * k : 0}}>
      <Img src={brasaoUrl} style={{height: retrato ? 560 * k : height * 0.5, margin: `${-60 * k}px 0`}} />
      <div style={{fontFamily: ANTON, color: COR.osso, fontSize: Math.min(width * 0.8, 1300 * k) / (16 * 0.48),
        textTransform: "uppercase", letterSpacing: "0.01em", lineHeight: 1.1}}>A Planilha é Tua</div>
      <div style={{fontFamily: MONO, color: COR.ouro, fontSize: retrato ? 54 * k : height * 0.045,
        marginTop: 24 * k}}>clipe completo no canal</div>
    </AbsoluteFill>
  ) : null;
  if (!linha || !visivel) return <AbsoluteFill style={{background: COR.preto}}>{som}{selo}{tela}</AbsoluteFill>;

  const lf = frame - quadro(linha.ini);
  const mono = MONO_SECOES.has(linha.secao) && !ultima;
  const fx = efeito(linha);
  const final = linha.secao === "refrao" && linha.vez === 3;
  const cores = paleta(linha, indice);
  const anterior = indice > 0 ? LINHAS[indice - 1] : null;
  // No pré-refrão a tarja cobre a tela no 4º quadro: até lá o fundo ainda é o do verso anterior.
  const tarja = linha.secao === "pre" && lf < 8;
  const fundo = tarja && lf < 4 && anterior ? paleta(anterior, indice - 1).bg : cores.bg;

  // Quais palavras estão na tela (o mosaico troca a primeira metade pela pergunta).
  let indices = linha.palavras.map((_, i) => i);
  let mosaico: number | null = null;
  if (fx === "mosaico") {
    const corte = linha.palavras.findIndex((p) => norm(p.t) === "onde");
    if (t >= linha.palavras[corte].ini) indices = indices.slice(corte);
    else {
      indices = indices.slice(0, corte);
      const desde = frame - quadro(linha.palavras[corte - 1].ini);
      if (desde >= 0) mosaico = desde;
    }
  }
  const corteTacha = fx === "tacha" ? linha.palavras.findIndex((p) => norm(p.t) === "mas") : -1;

  const maxc = mono ? (retrato ? 14 : 22) : retrato ? 13 : 22;
  const rows = fileiras(linha.palavras, indices, maxc);
  const chars = (row: number[]) => row.reduce((sum, i) => sum + linha.palavras[i].t.length, row.length - 1);
  // Largura estimada em "letras de Anton" (≈0,48 em cada, com folga para a entrada em escala): a serifada, mesmo menor, ocupa mais por letra.
  const largura = (row: number[]) => row.reduce((sum, i) => {
    const chave = norm(linha.palavras[i].t);
    const tachada = corteTacha > 0 && i < corteTacha;
    const peso = chave === "stf" ? 1.9 : tachada ? 1.7 : PODER.has(chave) ? 1.25 : 1;
    return sum + linha.palavras[i].t.length * peso;
  }, row.length - 1);
  const teto = boxH * (ultima ? 0.26 : linha.secao === "refrao" ? 0.42 : 0.3);
  let sizes = rows.map((row) => Math.min(teto, (boxW * 0.9) / (Math.max(largura(row), 3) * 0.48)));
  if (mono) sizes = rows.map(() => Math.min(boxH * 0.12, boxW / (Math.max(...rows.map(chars)) * 0.62)));
  const total = sizes.reduce((sum, size) => sum + size * (mono ? 1.5 : 1.38), 0);
  if (total > boxH) sizes = sizes.map((size) => (size * boxH) / total);

  // Movimento do bloco: deriva lenta, tremor nas batidas do refrão e empurrão de saída para o próximo verso.
  const duracao = Math.max(1, quadro((proxima ? proxima.ini : letra.duracao) - linha.ini));
  const deriva = mono ? 1 : 1 + 0.04 * clamp(lf / duracao);
  const direcao = indice % 2 === 0 ? 1 : -1;
  const contiguo = proxima !== null && proxima.ini <= linha.fim + SEGURA;
  const sai = contiguo && !mono && !ateOCorte ? clamp((lf - (duracao - 4)) / 4) : 0;
  let tremor = 0;
  if (linha.secao === "refrao") {
    linha.palavras.forEach((p, i) => {
      const desde = frame - quadro(p.ini);
      if ((i === 0 || final) && desde >= 0 && desde < 5) tremor = Math.max(tremor, (5 - desde) / 5);
    });
  }
  const amp = tremor * (final ? 26 : 14) * (Math.min(width, height) / 1080);
  const dx = amp * (random(`x${frame}`) - 0.5) * 2;
  const dy = amp * (random(`y${frame}`) - 0.5) * 2 - sai * direcao * boxH * 0.4;

  const ultimoIndice = linha.palavras.length - 1;
  const palavra = (i: number, size: number) => {
    const p = linha.palavras[i];
    const wf = frame - quadro(p.ini);
    const chave = norm(p.t);
    const poder = !mono && !ultima && (PODER.has(chave) || (corteTacha > 0 && i < corteTacha));
    const fachada = chave === "stf";
    const tachada = corteTacha > 0 && i < corteTacha ? clamp((frame - quadro(linha.palavras[corteTacha].ini)) / 5) : 0;
    let transform = `scale(${wf < 0 ? 1 : 1.25 - 0.25 * saida(wf / POP)})`;
    if (mono) transform = "none";
    const style: React.CSSProperties = {
      display: "inline-block", position: "relative", marginRight: i === ultimoIndice ? 0 : "0.24em",
      opacity: wf < 0 ? 0 : 1 - 0.5 * tachada, transform,
      fontFamily: mono ? MONO : poder ? CINZEL : ANTON,
      fontWeight: poder ? 700 : 400,
      fontSize: poder ? (fachada ? "1em" : tachada > 0 || (corteTacha > 0 && i < corteTacha) ? "0.84em" : "0.62em") : undefined,
      letterSpacing: poder ? "0.06em" : mono ? 0 : "0.01em",
      color: SANGUE.has(chave) ? cores.forte : poder ? cores.poder : cores.fg,
    };
    if (fx === "contorno") {
      style.color = "transparent";
      style.WebkitTextStroke = `${Math.max(2, size * 0.022)}px ${cores.fg}`;
    }
    let conteudo: React.ReactNode = p.t;
    if (fx === "apaga" && i === ultimoIndice) {
      const some = (frame - quadro(linha.fim + 0.15)) / 2; // uma letra a cada 2 quadros, da direita para a esquerda
      conteudo = p.t.split("").map((c, n) => <span key={n} style={{opacity: p.t.length - n <= some ? 0 : 1}}>{c}</span>);
    }
    return (
      <span key={i} style={style}>
        {conteudo}
        {tachada > 0 && (
          <span style={{position: "absolute", left: "-4%", top: "46%", height: "0.12em", width: `${108 * tachada}%`,
            background: cores.forte}} />
        )}
      </span>
    );
  };

  const revelada = (i: number) => frame >= quadro(linha.palavras[i].ini);
  const cursor = mono && Math.floor(lf / 8) % 2 === 0;
  return (
    <AbsoluteFill style={{background: fundo, overflow: "hidden"}}>
      {som}
      {mosaico !== null && (
        <AbsoluteFill style={{display: "flex", flexWrap: "wrap", alignContent: "flex-start", fontFamily: CINZEL,
          fontWeight: 700, fontSize: boxW * 0.07, lineHeight: 1.25, color: cores.poder, opacity: 0.4}}>
          {Array.from({length: 120}, (_, n) => (
            <span key={n} style={{marginRight: "0.4em", opacity: n < mosaico * 6 ? 1 : 0}}>POLÍTICO</span>
          ))}
        </AbsoluteFill>
      )}
      {!ultima && cores !== TEMA.sangue && selo}
      <div style={{position: "absolute", top: caixa.top, left: caixa.left, width: boxW, height: boxH, display: "flex",
        flexDirection: "column", justifyContent: "center", alignItems: "center", opacity: 1 - sai,
        transform: `translate(${dx}px, ${dy}px) scale(${deriva})`}}>
        {ultima && <Img src={brasaoUrl} style={{height: fecho, margin: `${-fecho * 0.15}px 0 ${-fecho * 0.14}px`}} />}
        {rows.map((row, r) => (
          <div key={r} style={{display: "flex", flexWrap: "nowrap", whiteSpace: "nowrap", alignItems: "baseline",
            justifyContent: "center", fontSize: sizes[r], lineHeight: mono ? 1.5 : 1, padding: mono ? 0 : "0.2em 0 0.18em",
            textTransform: mono ? "none" : "uppercase"}}>
            {row.map((i) => palavra(i, sizes[r]))}
            {cursor && r === rows.length - 1 && revelada(row[row.length - 1]) && (
              <span style={{display: "inline-block", width: "0.55em", height: "1em", marginLeft: "0.2em",
                background: cores.fg, alignSelf: "center"}} />
            )}
          </div>
        ))}
      </div>
      {tarja && (
        <AbsoluteFill style={{background: COR.ouro, transform: `translateX(${(direcao * (lf - 4) * 100) / 4}%)`}} />
      )}
      {final && lf === 0 && <AbsoluteFill style={{background: "#FFFFFF"}} />}
      {tela}
    </AbsoluteFill>
  );
};
