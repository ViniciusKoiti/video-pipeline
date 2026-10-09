// Palavras que o template escreve na tela, por idioma (ADR 011): as mesmas chaves nos dois, nenhuma vazia.
// Rodar: `npm test` em video/ (Node 22.18+).
import assert from "node:assert/strict";
import {test} from "node:test";
import {LABELS} from "../src/labels.ts";

test("os dois idiomas têm as mesmas palavras, nenhuma vazia", () => {
  assert.deepEqual(Object.keys(LABELS.en).sort(), Object.keys(LABELS["pt-BR"]).sort());
  for (const language of ["en", "pt-BR"] as const) {
    for (const [key, value] of Object.entries(LABELS[language])) {
      assert.ok(value.trim().length > 0, `${language}.${key} vazio`);
    }
  }
});

test("o rodapé e o subtítulo dos gráficos mudam com o idioma", () => {
  assert.equal(LABELS["pt-BR"].source, "Fonte");
  assert.equal(LABELS.en.source, "Source");
  assert.equal(LABELS["pt-BR"].unitIn, "em");
  assert.equal(LABELS.en.unitIn, "in");
  assert.notEqual(LABELS.en.clampNote, LABELS["pt-BR"].clampNote);
});
