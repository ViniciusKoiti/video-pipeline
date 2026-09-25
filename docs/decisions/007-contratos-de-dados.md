# 007 — Contratos de dados e política de licenças

- **Status:** aceito
- **Data:** 2026-09-25
- **Etapa do roadmap:** #3

## Contexto

O §6 do CLAUDE.md lista os campos dos manifestos, mas deixa em aberto a granularidade das cenas, como a
aprovação humana é registrada, quais licenças podem chegar ao render e o formato do vídeo. A
`docs/spec-v0.4.md` original não está no repositório; os contratos saem do CLAUDE.md.

## Decisões

1. **Uma cena = um bloco de narração = um WAV = um visual.** Com 20–35 cenas em 5–7 min (~14 s cada),
   trocar uma frase ou uma imagem invalida só aquela cena. Um mapa pode voltar em várias cenas, por isso o
   ativo usa `used_in_scenes` (lista) em vez do `used_in_scene` do §6.
2. **Claims citam fonte e, opcionalmente, trecho.** `source_ids` continua obrigatório (§2.2);
   `excerpt_ids` (`source-01#E3`) já existe e precisa pertencer às fontes citadas. Vira obrigatório quando
   a ADR 002 (etapa 26) for aceita.
3. **`review.json` é a fonte única das decisões humanas.** Entradas só são acrescentadas, por etapa,
   cena ou ativo, com `input_hash` do que foi revisado: se o conteúdo muda, a aprovação deixa de valer.
   O `review_status` dos outros manifestos é só reflexo, escrito pelo código.
4. **Lista fechada de licenças aceitas** para um ativo chegar a `approved`: `PD-US`, `PD-old`, `CC0-1.0`,
   `CC-BY-2.0/2.5/3.0/4.0`, `Flickr-NKCR`, `Pexels`, `Generated` (Workers AI) e `Original` (gráfico do
   projeto). Ficam **fora**, e portanto em revisão humana: CC-BY-SA (o compartilhamento pela mesma licença
   poderia alcançar o vídeo inteiro), qualquer NC (o canal pretende monetizar) e licença não identificada.
   Regras adicionais para aprovar: `sha256` do arquivo final; domínio público exige o raciocínio em
   `usage_notes`; CC-BY exige `author` e `attribution_text`; ativo de acervo exige `page_url`.
   Decisão de negócio do dono do projeto, não parecer jurídico.
5. **Formato do vídeo:** 1920×1080, 30 fps, áudio 48 kHz, 16:9 validado no `episode.json`; a prévia em
   1280×720 é opção do render, não do contrato.

## Consequências

- `app/pipeline/schemas.py` implementa tudo acima; `tests/fixtures/episodes/pilot-example/` é o exemplo
  de referência (conteúdo fictício, URLs `example.org`).
- Regras entre arquivos são funções: `unknown_source_refs` (§2.2) e `visual_need_violations` (§2.4:
  Pexels e Workers AI nunca como `historical_exact`).
- `script.json` ainda não tem schema: nasce na etapa 27 com o formato que o LLM precisar produzir.
- Ampliar a lista de licenças exige nova ADR.
