# 065 — Especulação declarada por cena (série "E se…?")

- **Status:** aceita pelo dono em 2026-11-26 ("sim, aprovo os três"). Implementada em 2026-11-26 (schema e `vp check`;
  selo na tela, skill e descrição pendentes, ver o fim).
- **Data:** 2026-11-26
- **Relaciona-se com:** ADR 008 (claims), ADR 019 (objetivo e opinião), ADR 055 (ficção declarada, marca no
  manifesto), ADR 061 (beats), `docs/pesquisa/reports/Nicho E se historico.md`

## Contexto

O dono aprovou uma série "E se…?" de história alternativa no Cena e Economia (2026-11-26). O primeiro episódio é
"E se o Brasil tivesse feito a bomba em 1990?". O formato tem duas camadas no mesmo vídeo:

- **o que aconteceu** (a história real, a mudança, o caso comparado de outro país): é fato e precisa de ficha;
- **o que teria acontecido** ("o mais provável é…", "seria…"): é leitura do narrador, sem fonte possível.

A análise de 20 vídeos do nicho mostrou que essa separação decide o resultado:
- o terço de mais views fala a especulação como especulação (30,6% do tempo, contra 5,0% no terço de baixo);
- o terço de baixo narra a linha inventada como crônica, com datas, como se tivesse acontecido (38,8% contra 0%);
- nenhum vídeo do nicho separa na tela o real do chute.

Hoje o pipeline tem duas posições e nenhuma serve:
- sem marca, o `vp check` pede `claims` nos planos com fato na tela e alerta "frase afirmativa sem claims" nas cenas
  de especulação, o que vira ruído no roteiro inteiro;
- com `"fiction": true` (ADR 055), o roteiro inteiro dispensa `claims`, inclusive a parte real, que no "E se" tem de
  ser fichada.

A ADR 019 cobre a opinião ("na minha leitura"), mas não a consequência provável de um passado alternativo.

## Decisão proposta

1. **Marca por cena** no `scenes.json`: `mode: "real" | "especulacao"`, com `real` como padrão. Diferente da ADR 055,
   a marca é da cena e não do manifesto, porque as duas camadas se alternam no mesmo vídeo.
2. **Cena `real`:** nada muda. Fato na fala e dado na tela exigem `claims` com `source_ids`. O caso comparado (por
   exemplo, o Paquistão depois de 1998) é sempre `real`, mesmo no meio da especulação.
3. **Cena `especulacao`:**
   - não exige `claims` e não gera o alerta "frase afirmativa sem claims";
   - **alerta** quando nenhuma frase da cena traz uma marca de especulação ("provavelmente", "seria", "teria",
     "o mais provável", "eu acho", "talvez", "na minha leitura"). É a fronteira entre consequência e crônica que a
     análise do nicho mediu;
   - **erro** quando um plano com dado na tela (`number`, `chart`, `calculation`, `receipt`, `stamp`, `timeline`) não
     tem `claims` e também não declara que o número é estimativa da linha alternativa (`estimate: true`, mostrado
     com o selo). Número inventado nunca aparece como fato;
   - data no futuro alternativo ("em 1995, o Brasil…") gera **atenção** para o gate 2: é o sinal de crônica.
4. **Sinal na tela:** toda cena `especulacao` leva o selo "E SE?" do estilo da série (o carimbo da colagem, maquete
   em `renders/serie-e-se/maquete-colagem/`), e a primeira cena `especulacao` depois de uma cena `real` leva o
   carimbo grande. Isso muda o contrato do render: `episode.json` ganha `mode` por cena (CLAUDE.md §5).
5. **Abertura:** o roteiro diz, até ~0:35, o que é real, o que é chute e como a tela mostra a diferença ("as regras do
   jogo", jogada 1 do topo do nicho). O `vp check` alerta se a primeira cena `especulacao` vier antes de a abertura
   dizer isso (busca por "e se", "vou mudar", "a partir daqui").
6. **Descrição do vídeo:** uma linha dizendo que a linha alternativa é especulação e que as fontes da parte real estão
   nos créditos.

Não muda: §2.3 (licença de ativo), §2.4 (imagem como ilustração; foto de arquivo só na parte real, pela exceção do
dono de 2026-11-26), os gates e a ADR 019 (a tese do dono continua sendo opinião, numa cena `especulacao` ou `real`).

## Opções descartadas

- **Usar `"fiction": true` no roteiro inteiro:** a parte real (o programa nuclear, o fechamento do Cachimbo em 1990)
  ficaria sem ficha, e é ela que dá credibilidade ao formato.
- **Não marcar nada e conviver com os alertas:** o verificador e o gate 2 não teriam como distinguir uma especulação
  bem marcada de um fato sem fonte.

## Custo

- Schema da cena e do `episode.json`; regras novas no `vp check`; selo no template ou no kit (depende da peça
  "carimbo" pedida ao kit em 2026-11-26).
- Skill `roteiro-explicativo`: uma seção "E se", com o molde do relatório.
- Testes no padrão de `tests/test_ficcao_declarada.py`.
- CLAUDE.md §2.2 e §5: uma linha cada.

## Se aprovada

Implementar num PR próprio, antes do gate 2 do primeiro episódio da série. Até lá, o roteirista lista as cenas de
especulação na tabela do `outline.md`, como a ADR 055 fez antes da marca existir.

## Implementado em 2026-11-26

Entrou (PR `adr-065-especulacao`):

- **Cena:** `mode: "real" | "especulacao"` (`Scene.mode`, tipo `SceneMode`), com `real` como padrão. Roteiro antigo
  vale sem mudança, e o campo não é escrito quando vale `real` (o `scenes.json` regravado pelo código não muda).
- **Planos com fato na tela** (`_FactualShot`: `number`, `chart`, `calculation`, `receipt`, `stamp`, `timeline`,
  `quote`, `lower_third`, `compare`, `network`, `family_tree`): `estimate: bool = False`. A regra mora no
  `ScenesManifest._factual_claims`: na cena `real`, plano sem `claims` é erro como antes (o `estimate` não dispensa);
  na cena `especulacao`, é erro sem `claims` e sem `estimate: true`. A ficção declarada (ADR 055) segue dispensando.
- **`vp check`** (`app/pipeline/script/checks/speculation.py`, constantes em `speculation_constants.py`):
  - a cena `especulacao` sai do alerta "frase afirmativa em cena sem claims" (`molde.claimless_statements`);
  - **alerta** para cena `especulacao` sem nenhuma marca na fala (lista fechada `SpeculationConstants.MARKS`:
    "provavelmente", "seria(m)", "teria(m)", "o mais provável", "eu acho", "acho que", "talvez", "na minha
    leitura", "possivelmente", "poderia(m)"), comparada como palavra inteira, sem acento nem maiúscula;
  - **alerta** quando nenhuma cena antes da primeira `especulacao` diz "e se", "vou mudar" ou "a partir daqui"
    (`OPENING_MARKS`); é uma busca por palavra, não confere o tempo (~0:35);
  - **alerta** para `estimate: true` numa cena `real`;
  - **atenção** para ano de quatro dígitos (1000–2099) na fala de uma cena `especulacao`, sinal de crônica (item 3).
- **`episode.json`:** `EpisodeScene.mode` copiado do roteiro e `estimate` dentro do `spec` do plano, os dois só
  escritos quando diferentes do padrão, para o `episode.json` de antes (e seu carimbo no gate 4) não mudar. As props
  do Remotion não mudam: o template não lê nenhum dos dois.
- Testes em `tests/test_especulacao_declarada.py`; CLAUDE.md §2.2 e §5.

Pendente:

- **Selo "E SE?" e carimbo grande na tela** (item 4): depende da peça "carimbo" pedida ao kit; quando existir, o
  `RemotionEngine.scene_props` passa `mode` e `estimate` ao template.
- **Skill `roteiro-explicativo`:** a seção "E se", com o molde do relatório.
- **Linha da descrição** (item 6): na skill `vp-metadados-youtube`, sem regra no `vp check`.
- A conferência da fronteira real × especulação pelo `verificador` e pela skill `checagem`.
