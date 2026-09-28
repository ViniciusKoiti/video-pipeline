// Número como aparece na tela ("R$ 47,6 bi", "1.500", "78%", "6ª"), escrito em pt-BR. Espelha
// `screen_number` de app/pipeline/schemas.py (ADR 011), mas guarda prefixo e sufixo com os espaços, para o
// hodômetro mostrar o texto exatamente como na ficha.

const SCREEN_NUMBER = /^(\D*?)([\d.,]*\d)(.*)$/;

export type ScreenNumber = {
  prefix: string;
  value: number;
  suffix: string;
  decimals: number;
  grouped: boolean; // a ficha agrupa milhar ("1.500"); ano e número pequeno não ("2025", "13")
};

export const screenNumber = (text: string): ScreenNumber | null => {
  const match = SCREEN_NUMBER.exec(text.trim());
  if (!match) return null;
  const digits = match[2];
  const value = Number(digits.replace(/\./g, "").replace(",", "."));
  if (!Number.isFinite(value)) return null;
  const decimals = digits.includes(",") ? digits.split(",")[1].length : 0;
  return {prefix: match[1], value, suffix: match[3], decimals, grouped: /\d\.\d{3}/.test(digits)};
};
