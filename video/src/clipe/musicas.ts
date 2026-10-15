import planilha from "./letra.json";
import vinha from "./vinha/letra.json";

// O que muda de uma música para a outra no clipe de letra. A composição (`Clipe.tsx`) é a mesma: três vozes
// tipográficas, cores e brasão do Nabote. Cada letra vem de `scripts/provisorio/clipe_tempos.py`.

export type Palavra = {t: string; ini: number; ok: boolean};
export type Linha = {secao: string; vez: number; texto: string; ini: number; fim: number; palavras: Palavra[]};
export type Efeito = "apaga" | "mosaico" | "tacha" | "contorno";

export type Musica = {
  titulo: string;
  duracao: number;
  linhas: Linha[];
  // Os últimos segundos da faixa, para onde o som dos cortes passa no fecho.
  cauda: number;
  // Palavras (normalizadas) na voz do poder (Cinzel dourada) e no vermelho do sangue.
  poder: Set<string>;
  sangue: Set<string>;
  // Efeito próprio de alguns versos, pelo começo do texto normalizado (a letra é fixa).
  efeitos: [string, Efeito][];
  // Versos do refrão que ganham o fundo vermelho.
  refraoSangue: string[];
  // Como o clipe completo termina: o último verso com o brasão grande ("Nabote.") ou, a partir de `fechoEm`
  // segundos, a tela do brasão com o título.
  fim: {tipo: "verso"} | {tipo: "titulo"; fechoEm: number};
};

export const MUSICAS: Record<string, Musica> = {
  planilha: {
    titulo: "A Planilha é Tua",
    duracao: planilha.duracao,
    linhas: planilha.linhas as Linha[],
    // A textura cai em 192,8 s e a música para sozinha em ~195,2 s. Antes disso a parte final é alta e soaria
    // como estalo.
    cauda: 192.8,
    poder: new Set([
      "estado", "perito", "toga", "tribunal", "stf", "marmore", "altar", "cargo", "divindade", "guardiao", "plano",
      "tecnica", "calculo", "tradicao", "destino", "gloria", "paraiso", "planilha", "relatorio", "grafico", "acabe",
    ]),
    sangue: new Set(["sangra", "mataste", "nabote", "terror"]),
    efeitos: [["oplanoecego", "apaga"], ["setudoepolitico", "mosaico"], ["tuescreve", "tacha"],
      ["queliberdadeeessa", "contorno"]],
    refraoSangue: ["mataste"],
    fim: {tipo: "verso"},
  },
  vinha: {
    titulo: "A Vinha Não é Sua",
    duracao: vinha.duracao,
    linhas: vinha.linhas as Linha[],
    // A voz acaba em ~194,5 s; batidas fortes em 194,2, 196,2 e 199,4 s e parada seca em 200,5 s. Os cortes passam
    // para o final logo antes da batida de 196,2 s.
    cauda: 196.0,
    poder: new Set([
      "rei", "palacio", "avaliacao", "sentenca", "autoridade", "assinatura", "cargo", "mandato", "mandatos",
      "eleicao", "discurso", "comicio", "cartaz", "palanque", "presidente", "partido", "direcao", "gestao",
      "mensalao", "lula", "dilma", "acabe",
    ]),
    sangue: new Set(["mataste", "nabote", "tomaram", "tomar", "tomas"]),
    efeitos: [["duasvozesmentirosas", "contorno"], ["vicartazperder", "apaga"]],
    refraoSangue: ["avinhanaoesua"],
    // A tela do brasão com o título termina de entrar (8 quadros) na batida de 196,2 s e fica até a parada.
    fim: {tipo: "titulo", fechoEm: 195.93},
  },
};
