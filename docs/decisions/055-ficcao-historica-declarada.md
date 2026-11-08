# 055 — Ficção histórica declarada (formato "sua vida em cada nível")

Data: 2026-11-05. **Status: aceita pelo dono em 2026-11-05. Decisão final (mesmo dia): o formato "sua vida em cada nível" / "como era ser X" dispensa fichas, fontes e claims
(opção C para este formato, com a regra de fato movida para o roteirista de cada formato). O texto de "Aplicado em" abaixo descreve a etapa anterior (variante B) e foi superado neste ponto:
o `roteirista-ficcao-historica` não exige ficha nem claim; só se obriga a não afirmar com precisão o que não saiba sustentar e a não tomar texto de outro canal como base.**
Etapa anterior: variante da opção B, com a regra de fato do roteiro deixando de ser global e passando a ser de cada roteirista.
Pedido do dono: tirar a exigência de fonte do `CLAUDE.md` §2.2, movê-la para o roteirista atual e criar um roteirista para o novo formato.
Relacionada às ADRs 008 (claims), 009 (fichas) e 019 (objetivo).

**Aplicado em 2026-11-05 (só texto, sem código):** `CLAUDE.md` §2.2 (o número foi mantido porque ADRs 007, 008, 011, 019, 031, o `pesquisador` e a skill `fichamento` o citam;
mudou o conteúdo) e §15 (nova linha); `.claude/agents/roteirista.md` (recebe a regra); novos `.claude/agents/roteirista-ficcao-historica.md` e `.claude/skills/roteiro-ficcao-historica/SKILL.md`.

**Continua em código (não mudou):** o `vp check` e os schemas validam as claims que existirem e dão **alerta**, não erro, em "frase afirmativa em cena sem claims". **Pendente:** um marcador
de ficção por cena no `scenes.json`, o ajuste do `vp check` e do `vp numeros` para não alertar nas cenas marcadas, e a skill `checagem` conferir a fronteira entre as duas camadas.
Enquanto o marcador não existe, o roteirista lista as cenas de ficção na tabela do `outline.md`.
**Resolvido em 2026-11-07 pela ADR 056:** o marcador é o regime de fontes do vídeo (`sources_policy: entretenimento` no `scenes.json`), não da cena;
com ele o schema dispensa claims, o rodapé não sai e o `vp check` não alerta frase sem claim.

## Problema

O formato "sua vida em cada nível da Idade Média" é narrado em segunda pessoa e tem cenas vividas ("você acorda…", "o servo está ao pé da cama…"). Essas frases não têm uma fonte
que as sustente, porque são reconstrução. Já os dados que o vídeo usa para dar peso (datas, números, preços, costumes, instituições, nomes) são fato e podem estar errados.
Na análise do vídeo-modelo apareceram vários desses erros (ex.: açúcar "por grama" em 1340, que é anacronismo).

## O que o pipeline faz hoje

Cena sem claim **não é erro**: o `vp check` dá só alerta ("frase afirmativa em cena sem claims") e termina sem erros. O roteiro do Agostinho tem quatro desses alertas, nas
cenas do exemplo inventado. O que bloqueia é uma `claim` sem `source_ids` ou uma ficha sem citação literal. Ou seja, uma cena de ficção já cabe; falta uma forma de **declarar**
que ela é ficção, para o alerta deixar de ser ruído e o espectador saber o que é fato e o que é reconstrução.

## Opções

**A. Manter tudo como está.** Funciona com alertas, mas o roteiro de ficção fica poluído de avisos e nada obriga a separar fato de reconstrução.

**B. Ficção declarada, com fato ainda fichado (recomendada).**
- Cena ou trecho marcado como `ficção declarada` (protagonista, pensamentos, diálogo, detalhe sensorial) **não exige claim** e não gera alerta.
- Qualquer dado apresentado como fato (data, número, preço, medida, instituição, costume, nome de pessoa real) **continua exigindo claim, ficha e trecho literal**.
- O vídeo diz no começo e na descrição que a vida do "você" é reconstrução, e quais partes são fato. O verificador confere a fronteira entre as duas no gate 2.
- Não muda: ativo com licença (§2.3), imagem como ilustração (§2.4), gates humanos (§2.5), divulgação de conteúdo alterado ou IA.
- Custo: um marcador por cena no `scenes.json`, ajuste do `vp check` e do `vp numeros`, texto na skill `roteiro-explicativo`, testes.

**C. Retirar a exigência de fonte para o formato.**
- Tudo pode ser inventado, sem fichas.
- Perde-se o diferencial do canal (CLAUDE.md §1: "fontes verificáveis") e os gates 1 e 2 deixam de ter função neste formato. Os erros de fato (como o do açúcar) passam sem barreira.
- Pesa na política de conteúdo repetitivo ou em massa do YouTube (§12) e no risco de conteúdo enganoso sobre história apresentada como real. Seria preciso rever também o objetivo do vídeo.

## Recomendação

Opção **B**. Ela resolve o que atrapalha o formato (cena vivida sem fonte) sem abrir mão do que o seu canal tem de diferente (os dados históricos conferidos). A opção C é possível,
mas é uma decisão sobre o que o canal é, não só sobre este vídeo; se for a escolha, deve ser registrada como tal.

## Se aprovada (B)

Emendar o `CLAUDE.md` §2.2 e §6, o schema da cena, o `vp check` e `vp numeros`, a skill `roteiro-explicativo`, e escrever os testes. Só depois disso o piloto "Como era ser rico na Idade Média?"
usa a marca. Até lá, o piloto segue as regras de hoje, com alertas nas cenas vividas.
