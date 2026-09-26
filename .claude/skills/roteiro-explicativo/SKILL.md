---
name: roteiro-explicativo
description: |
  Escreve o roteiro de um episódio explicativo (estilo How Money Works) a partir das fichas de fatos:
  pergunta central, gancho, viradas ligadas por causa, narração falada e lista de planos por cena
  (scenes.json v2, ADR 008). Use depois do fichamento aprovado e antes da checagem (ADR 009).
argument-hint: "<episode-id>"
---

# Roteiro explicativo: fichas → outline.md + scenes.json

Você escreve **só** com o que está em `data/episodes/<id>/facts.json`. Se uma frase precisa de um fato
que não está nas fichas, não escreva a frase: anote a lacuna no fim do `outline.md`.

## Saída

1. `data/episodes/<id>/outline.md`, para a revisão humana (gate 2): pergunta central, gancho, as viradas
   em ordem com os ids das fichas (F03, F07...), o fecho, e as lacunas.
2. `data/episodes/<id>/scenes.json`, no schema `ScenesManifest` (`app/pipeline/schemas.py`), com planos
   (exemplo só de formato; os textos não são fatos verificados):

```json
{
  "episode_id": "votorantim-fatia",
  "language": "pt-BR",
  "scenes": [
    {
      "id": "S02",
      "narration": "Mas a história começa em 1918, com uma fábrica de tecidos que ninguém queria.",
      "shots": [
        {"kind": "stamp", "anchor": "Mas a história", "date": "1918", "place": "Sorocaba (SP)",
         "claims": [{"text": "compra em 1918", "source_ids": ["source-01"], "excerpt_ids": ["source-01#E12"]}]},
        {"kind": "photo", "anchor": "uma fábrica de tecidos", "visual_need": "historical_exact",
         "search_query": "Fábrica de Tecidos Votorantim 1918", "asset_id": null, "motion": "push_in"}
      ]
    }
  ]
}
```

## Método

1. **Pergunta central.** Uma pergunta que o vídeo responde e que o público quer ver respondida
   ("como uma fábrica falida virou a semente de um dos maiores grupos do país?"). Tudo que não ajuda a
   responder sai.
2. **Gancho.** Abra com o fato mais forte (`number`, `conflict` ou `curiosity`), mesmo fora da ordem
   cronológica. Depois volte ao começo.
3. **Espinha de viradas.** Três a cinco `turning_point` em ordem. Entre elas, ligue por causa: "mas"
   (um obstáculo) ou "por isso" / "então" (uma consequência). Se só couber "e depois", falta um fato de
   causa ou a cena sobra. Só escreva causa que a ficha sustenta.
4. **Mecanismo.** Onde o público perguntaria "como?", use uma ficha `mechanism`. Contexto só o mínimo.
5. **Fecho com fato.** Responda à pergunta central com um fato, sem moral nem frase de efeito.
6. **Cenas.** Uma cena = um bloco de narração de 1 a 3 frases (5 a 12 s, cerca de 75 a 180 caracteres;
   a voz fala ~15 caracteres por segundo).
7. **Planos.** Um plano a cada 2 a 4 s (30 a 60 caracteres de narração). `anchor` é um trecho literal da
   narração, em ordem; o primeiro plano cobre o início da cena. Escolha pelo conteúdo:
   - número dito → `number` (o valor exato da ficha, com a unidade no `label`);
   - data ou lugar → `stamp`; lugares e deslocamentos → `map`;
   - pessoa entrando na história → `photo` (se houver retrato) e `lower_third` (nome e papel);
   - sequência de eventos → `timeline`; parentesco → `family_tree`; comparação de valores → `chart`;
   - frase de documento → `quote` com o texto literal da fonte; `style: "headline"` só para manchete
     real de jornal. Nunca invente citação nem manchete.
   - `photo`/`broll`: `visual_need` correto (§2.4), `search_query` específica (pessoa, lugar, ano) e
     `asset_id: null`; a busca de ativos é outra etapa.
8. **Toda afirmação tem trecho.** Narração que afirma fato → `claims` na cena; plano que mostra número,
   data, nome, cargo, citação ou gráfico → `claims` no plano. Use `source_ids` e `excerpt_ids` das
   evidências das fichas usadas. O texto na tela repete a ficha: não arredonde nem "atualize" valores.
9. **Narração para ser falada** em pt-BR (voz Kokoro `pm_alex`):
   - frases de até ~20 palavras, uma ideia por frase, alternando curtas e longas;
   - anos em algarismos; outros números escritos como devem ser ditos ("mil e quinhentos operários");
   - sigla por extenso na primeira vez; nomes próprios vão para `voice/glossary.json` se a pronúncia
     falhar;
   - sem "nesse vídeo", "você não vai acreditar", "fica até o final", "e isso muda tudo".
10. **Ritmo do formato:** média de 2 a 4 s por plano; nenhum abaixo de 1,5 s.

## Fechamento

- Passe a skill `humanizer-narracao` na narração.
- Rode `.venv/bin/vp check <id>` até zero erros; trate os alertas de ritmo.
- Entregue para o agente `verificador` (contexto limpo) antes do gate 2.
