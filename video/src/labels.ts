// Palavras que o template escreve na tela, por idioma do episódio (ADR 011, emenda "número por idioma").
// O que o roteiro escreve (narração, rótulos, textos dos planos) já vem no idioma; aqui ficam só as palavras do
// próprio template e as frases-padrão do motion-kit que ele troca por prop.
import type {Language} from "./types";

export type Labels = {
  source: string; // "Fonte: …" do rodapé (`label` do SourceTag)
  unitIn: string; // subtítulo do gráfico: "em contos de réis" / "in thousands of dollars"
  headline: string; // plano `quote` em estilo manchete
  quote: string; // plano `quote`
  ratioWord: string; // `ValueCompare` em escala: "8 vezes" / "8 times" (a tela não calcula razão; o kit pede a palavra)
  clampNote: string; // `ValueCompare` em escala: aviso de quadrado ampliado
};

export const LABELS: Record<Language, Labels> = {
  "pt-BR": {
    source: "Fonte",
    unitIn: "em",
    headline: "Manchete",
    quote: "Citação",
    ratioWord: "vezes",
    clampNote: "o quadrado menor foi ampliado para continuar visível",
  },
  en: {
    source: "Source",
    unitIn: "in",
    headline: "Headline",
    quote: "Quote",
    ratioWord: "times",
    clampNote: "the smaller square was enlarged to stay visible",
  },
};
