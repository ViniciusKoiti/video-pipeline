// Número da tela por idioma: lê os mesmos casos que `screen_number` (tests/fixtures/screen-numbers.json).
// Rodar: `npm test` em video/ (Node 22.18+, que roda TypeScript sem build). Fora de `src/` de propósito: o hash
// do template (app/render/remotion.py) cobre `src/*.ts`, e um teste não deve invalidar o cache dos renders.
import assert from "node:assert/strict";
import {readFileSync} from "node:fs";
import {test} from "node:test";
import {SEPARATORS, screenNumber} from "../src/numbers.ts";

type Case = {
  language: "en" | "pt-BR";
  text: string;
  number: null | {prefix: string; value: number; suffix: string; decimals: number; grouped: boolean};
};

const cases: Case[] = JSON.parse(
  readFileSync(new URL("../../tests/fixtures/screen-numbers.json", import.meta.url), "utf8"),
);

for (const {language, text, number} of cases) {
  test(`${language}: ${text}`, () => {
    const parsed = screenNumber(text, language);
    if (number === null) {
      assert.equal(parsed, null);
      return;
    }
    assert.ok(parsed);
    // o hodômetro guarda os espaços do prefixo e do sufixo; o Python devolve os dois sem eles
    assert.deepEqual(
      {prefix: parsed.prefix.trim(), value: parsed.value, suffix: parsed.suffix.trim(),
        decimals: parsed.decimals, grouped: parsed.grouped},
      number,
    );
  });
}

test("pt-BR é o idioma padrão", () => {
  assert.equal(screenNumber("1.500")?.value, 1500);
  assert.equal(screenNumber("US$ 1,500")?.value, 1.5);
});

test("separadores do hodômetro e dos gráficos por idioma", () => {
  assert.deepEqual(SEPARATORS["pt-BR"], {group: ".", decimal: ","});
  assert.deepEqual(SEPARATORS.en, {group: ",", decimal: "."});
});
