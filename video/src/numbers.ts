// Número como aparece na tela ("R$ 47,6 bi", "1.500", "78%", "6ª"; em inglês "US$ 1,500", "$4.2 bn"). Espelha
// `screen_number` de app/pipeline/schemas.py (ADR 011), mas guarda prefixo e sufixo com os espaços, para o
// hodômetro mostrar o texto exatamente como na ficha. O idioma é o do episódio: o mesmo texto vale outro número
// em outro ("1,500" é 1.500 em inglês e 1,5 em português). Os dois lados leem os mesmos casos
// (tests/fixtures/screen-numbers.json).

import type {Language} from "./types";

const SCREEN_NUMBER = /^(\D*?)([\d.,]*\d)(.*)$/;

// Separador de milhar e de decimal de cada idioma; vale também para o hodômetro e para a prop `locale` dos gráficos.
export const SEPARATORS: Record<Language, {group: string; decimal: string}> = {
  "pt-BR": {group: ".", decimal: ","},
  en: {group: ",", decimal: "."},
};

export type ScreenNumber = {
  prefix: string;
  value: number;
  suffix: string;
  decimals: number;
  grouped: boolean; // a ficha agrupa milhar ("1.500"); ano e número pequeno não ("2025", "13")
};

export const screenNumber = (text: string, language: Language = "pt-BR"): ScreenNumber | null => {
  const match = SCREEN_NUMBER.exec(text.trim());
  if (!match) return null;
  const {group, decimal} = SEPARATORS[language];
  const digits = match[2];
  const value = Number(digits.split(group).join("").replace(decimal, "."));
  if (!Number.isFinite(value)) return null;
  const [integer, fraction = ""] = digits.split(decimal);
  return {prefix: match[1], value, suffix: match[3], decimals: fraction.length, grouped: integer.includes(group)};
};
