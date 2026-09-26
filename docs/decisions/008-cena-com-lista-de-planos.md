# 008 — Cena com lista de planos; `episode.json` v2; português

- **Status:** aceito
- **Data:** 2026-09-26
- **Etapa do roadmap:** #48, passo 1 (fatia vertical Votorantim)
- **Substitui:** a decisão 1 da ADR 007 ("uma cena = um visual") e amplia o contrato congelado da ADR 001

## Contexto

O vídeo de teste com "uma cena = um bloco de narração = um visual" ficou com cara de slideshow narrado,
exatamente o que a política de conteúdo inautêntico do YouTube cita (§12). Canais de referência do formato
explicativo (ex.: How Money Works) trocam de plano a cada 2–4 s e usam números, gráficos, manchetes, mapas e
nomes na tela. O dono aprovou mudar o modelo e produzir a fatia vertical em português, com a voz `pm_alex`.

## Decisão

1. **A cena continua sendo um bloco de narração (um WAV)** e ganha uma **lista de planos tipados**. Cada
   plano fica **ancorado num trecho da narração** (`anchor`), que precisa aparecer no texto, em ordem.
2. **Tipos de plano:**
   - com ativo: `photo` (com `crop` e `motion`) e `broll` (vídeo);
   - gráficos: `number`, `chart`, `quote` (citação ou manchete **recriada como tipografia**, nunca print),
     `map`, `stamp` (data e lugar), `lower_third` (nome e cargo), `timeline` e `family_tree`.
3. **§2.2 vale para a tela:** todo plano que afirma algo (`number`, `chart`, `quote`, `stamp`,
   `lower_third`, `timeline`, `family_tree`) exige `claims` com `source_ids`. `unknown_source_refs` e a
   regra "banco de imagens nunca é registro" (§2.4) passam a checar plano a plano.
4. **Tempo dos planos:** proporcional à posição da âncora na narração, sobre a duração real do WAV
   (`app/pipeline/shots.py`). Os tempos por palavra do alinhamento (etapa 17) substituem a proporção
   quando existirem.
5. **Ritmo é alerta, não bloqueio:** plano com menos de 1,5 s; média fora de 2–4 s (explicativo) ou 4–6 s
   (documentário).
6. **Compatibilidade:** uma cena sem planos é a forma v1 e vale como um único plano de foto
   (`effective_shots`). O `episode.json` tem `schema_version` 1 (um visual por cena) ou 2 (planos
   contíguos cobrindo a cena, com `media` só em foto e B-roll). O motor ffmpeg aceita a v2 com um plano de
   foto por cena e dá erro claro para vários planos (etapas #41 e #48). O decisor de modalidade conta
   planos, não cenas.
7. **Idioma:** o contrato aceita `en` e `pt-BR`. A voz é configurada por idioma
   (`[kokoro] voices = { en = "am_michael", "pt-BR" = "pm_alex" }`) e o pedido de narração informa o idioma.

## Consequências

- A etapa 11 (invalidação) passa a trabalhar por plano: trocar a imagem de um plano refaz só aquele trecho.
- Os próximos passos da #48 são trazer o Remotion + motion-kit para o `main` renderizando planos, e os
  componentes de documentário do template.
- A etapa 27 (roteiro) precisa gerar a lista de planos em JSON validado, e a etapa 28 (cenas) deixa de ser
  "um visual por cena".
