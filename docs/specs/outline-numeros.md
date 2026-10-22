# #170: números do roteiro gerados por código e comparados com o nicho

**Status:** implementada (2026-10-19). Decisões do dono: D4 e D5 aceitas; D1, D2 e D3 como recomendado (o bloco
fica fora do carimbo, a abertura é o primeiro décimo, o `plano-imagens.md` é gerado). Diferença do desenho: o perfil
sai de um script novo da skill, `brief.py`, que lê os CSVs da análise só com a biblioteca padrão, em vez de uma
opção `--brief` no `analisar.py`, que exige pandas.
**Relaciona-se com:** ADR 031 (perfil de formato do nicho, partes B e D), ADR 018 (resumo do radar), skill
`analise-de-formato`.
**Issue:** [#170](https://github.com/ViniciusKoiti/video-pipeline/issues/170).
**Caso de prova:** `death-note-fins-meios`, roteiro da rodada 36 (gates 1, 2 e 3 aprovados).

## 1. Problema

O `outline.md` traz duas coisas misturadas:
- **Parte escrita à mão:** decisões do dono, espinha, ligações, lacunas e a palavra que pesa.
- **Parte que só copia o `scenes.json`:** quantas cenas e planos, pausas, "você", duração, ritmo, alertas do `vp check`,
  tabela dos quadros citados e quais ativos aparecem em cada cena.

A segunda parte é escrita à mão a cada rodada e envelhece a cada mudança do roteiro ou das imagens. No Death Note, o
verificador reprovou 15 rodadas seguidas (22 a 36), a maioria por um desses números velhos, não por fato errado. Cada
rodada custa de 6 a 8 minutos de agente. O verificador também reconta tudo à mão, e às vezes erra a conta: ele chegou a
dizer 14 "você" quando eram 15.

Há um segundo problema, maior: os números sozinhos não dizem se o roteiro está no formato do nicho. Quando
exploramos o nicho, a skill `analise-de-formato` mediu 40 vídeos e salvou as medidas: terço de mais views e terço de
menos, por grupo (`tercos.csv`), correlação com as views (`correlacoes.csv`), curva por décimo do vídeo (`curva.csv`),
voz (`voz.csv`) e texto na tela (`texto-na-tela.tsv`). No Death Note, essa comparação foi feita à mão, num relatório
que nenhum agente lia, e com unidades diferentes das nossas. A ADR 031 (partes B e D, ainda propostas) já pede que
esse perfil vire arquivo do episódio e alerta do `vp check`.

## 2. Objetivo e limites

**Objetivo:**
- **Calcular:** o código calcula a parte numérica, com as mesmas regras do `vp check`.
- **Medir como o nicho:** o código calcula as medidas que o nicho tem, nas mesmas unidades e com as mesmas palavras
  contadas.
- **Comparar:** compara essas medidas com o perfil do nicho salvo na exploração (seção 3.2).
- **Gravar:** grava os números e a comparação num bloco marcado do `outline.md`, e o `plano-imagens.md`.
- **Avisar:** o `vp check` avisa quando o bloco não bate com o `scenes.json` e quando uma medida foge de um padrão
  forte do nicho.

Ninguém escreve, reconta nem compara esses números à mão.

**Fora do escopo:**
- **Parte escrita à mão do outline:** continua do roteirista e do verificador.
- **Duração real:** o cálculo usa a estimativa por caracteres, a mesma do `vp check`, e não o tempo dos WAVs. Usar o
  tempo real quando a voz existir fica para depois (ver a seção 9).
- **Gates:** nenhuma regra de gate muda, exceto a decisão D1 da seção 8, que é sua.

## 3. Definições: cada número e a regra exata

Todos vêm de funções que já existem:
- `effective_shots`;
- `shot_bounds` (`app/pipeline/shots.py`);
- `timeline_length`, `strip_pauses` e `pause_positions` (`app/media/narration.py`);
- as constantes do `app/pipeline/check.py`;
- o ritmo da voz final em `speech_chars_per_second(settings)`, hoje 14 caracteres por segundo.

| Número | Regra |
|---|---|
| cenas | `len(scenes)` |
| planos | soma de `len(effective_shots(cena))` |
| planos com texto | planos cujo `kind` não está em `MEDIA_SHOT_KINDS` (`photo`, `broll`) |
| pausas | soma de `len(pause_positions(narração))` |
| palavras | soma de `len(strip_pauses(narração).split())` |
| duração estimada | soma de `timeline_length(narração)` ÷ caracteres por segundo |
| "você" | ocorrências de `você` ou `vocês` (o mesmo padrão do `analisar.py`) no texto sem pausas; total e número de cenas |
| "você" no fecho | ocorrências cuja posição, no texto corrido sem pausas, cai nos últimos 10% dos caracteres |
| tempo de cada plano | `shot_bounds(narração, planos, duração da cena)`, como no `vp check` |
| alertas de ritmo | plano com menos de `MIN_SHOT_MS` (1,5 s), ou com mais de `MAX_SHOT_MS` (6 s) sem estar em `LONG_KINDS`; a mesma regra e a mesma ordem do `vp check` |
| ritmo da abertura | planos que **começam** nos primeiros 10% da duração estimada, em planos por minuto; e o ritmo do resto |
| quadros citados | planos `photo` cujo ativo tem `license_id: Citacao`, com cena, âncora, ativo e tempo; total de usos e de ativos distintos |
| ativos por cena | para cada ativo, as cenas em ordem de primeira aparição; total de ativos usados |
| baixados fora do vídeo | ativos em `assets/` que nenhum plano usa |

**Abertura:** hoje o outline do Death Note diz "S156–S110", um recorte escolhido à mão (23 planos em ~91 s). A regra dos
10% dá 21 planos em ~79 s. Os dois são válidos, mas só o segundo é reproduzível. Veja a decisão D2.

### 3.1 Medidas na unidade do nicho

O nicho foi medido em vídeos prontos: cortes pelo ffmpeg e palavras pela legenda. Para comparar, o roteiro precisa da
mesma conta. São estas as colunas de `tercos.csv` e as regras equivalentes no roteiro:

| Medida do nicho | No roteiro |
|---|---|
| `duracao_s` | duração estimada |
| `palavras_min` | palavras ÷ duração × 60 |
| `cortes_min` | **trocas de imagem** ÷ duração × 60. Uma troca é um plano que muda o que se vê na tela inteira: plano de mídia com ativo diferente do anterior, ou plano gráfico que não é sobreposição. Planos seguidos do mesmo vídeo de textura **não** são troca (é a continuidade da ADR 031), e a tarja ou o número sobre a foto também não. Contar planos daria um número que o nicho não tem |
| `plano_medio_s` | duração ÷ trocas |
| `voce_por_mil`, `nos_por_mil`, `eu_por_mil`, `fonte_por_mil` | ocorrências por mil palavras, com os mesmos padrões de `SPOKEN` em `analisar.py` (por exemplo, "eu" conta também "pra mim" e "acho"; "fonte" conta "estudo" e "pesquisa") |
| `palavras_60s`, `voce_60s`, `cortes_60s` | o mesmo no primeiro minuto estimado |
| curva por décimo (`curva.csv`) | as mesmas medidas em cada décimo; o "fecho" é o último décimo |
| texto na tela (`texto-na-tela.tsv`) | planos com texto ÷ planos |
| voz (`voz.csv`: pausas por minuto, silêncio) | só depois da voz gerada, medida no WAV; antes disso, marcas de pausa por minuto como estimativa |

Os padrões de palavra ficam num lugar só. `app/pipeline/numbers.py` tem a versão do código, e um teste confere que ela é
igual à do `analisar.py`, que é script de skill e roda sem o pacote `app`.

### 3.2 Perfil do nicho no episódio (`formato-brief.json`, ADR 031 parte B)

- **Quem grava:** o `analisar.py` ganha a opção `--brief`. Ela grava o `formato-brief.json` a partir de `tercos.csv`,
  `correlacoes.csv` e `curva.csv`.
- **Onde fica:** um script copia a versão datada para `data/episodes/<id>/formato-brief.json`, como o
  `radar-brief.json` dos Reels (ADR 018).

O arquivo traz, para cada medida:
- o valor do terço de mais views e o do terço de menos;
- `n`;
- o ρ de Spearman com as views;
- a força: `pattern` ou `hint`.

```json
{"nicho": "Nicho recap de anime", "grupo": "H", "data": "2026-10-18", "n": 20,
 "medidas": {"voce_por_mil": {"alto": 7.9, "baixo": 4.6, "rho": 0.28, "forca": "hint"},
             "cortes_min": {"alto": 14.9, "baixo": 19.0, "rho": -0.22, "forca": "hint"}}}
```

É forma, nunca fonte (§2.2): nenhum número do perfil vai para a fala ou para a tela.

### 3.3 O que a comparação mostraria hoje no Death Note

Calculado com a regra acima no roteiro aprovado. O nicho é o grupo H, terço de cima e terço de baixo. Os números
foram calculados uma vez e entram no aceite.

| Medida | Death Note | H, terço de cima | H, terço de baixo |
|---|---|---|---|
| duração | ~791 s | 549 s | 698 s |
| palavras por minuto | 152 | 180 | 155 |
| trocas de imagem por minuto | 5,5 (73 trocas) | 14,9 | 19,0 |
| plano médio | 10,8 s | 4,0 s | 3,2 s |
| "você" por mil | 7,5 | 7,9 | 4,6 |
| "eu" por mil | 1,5 | 2,2 | 3,2 |
| fonte por mil | 5,0 | 1,1 | 0,0 |
| "você" no primeiro minuto | 0 | 2 | 1 |
| trocas no primeiro minuto | 13 | 13 | 20,5 |

A tabela já diz coisas que hoje só apareceriam num relatório lido à mão:
- o Death Note fala "estudo/pesquisa" quase 5 vezes mais que o terço de cima;
- não diz "você" no primeiro minuto;
- troca de imagem bem menos que o grupo H. Essa é a escolha da textura, que fica perto do grupo H0, de filosofia sem
  anime: 3,1 no terço de cima.

Com ρ ≤ 0,3 e 20 vídeos, tudo isso ainda é `hint`: vira informação no bloco, não alerta (ADR 031).

## 4. Desenho

### 4.1 Módulo `app/pipeline/numbers.py`

Funções puras, sem leitura de disco, testáveis sem rede:

```python
@dataclass(frozen=True)
class ShotTiming:
    scene_id: str
    shot: Shot
    start_ms: float  # desde o começo do vídeo
    ms: float

def shot_timings(scenes: ScenesManifest, chars_per_second: float) -> list[ShotTiming]: ...

@dataclass(frozen=True)
class ScriptNumbers:
    scenes: int
    shots: int
    text_shots: int
    pauses: int
    words: int
    duration_ms: float
    voce: int
    voce_scenes: int
    voce_closing: int
    opening: tuple[int, float]      # planos, ms
    rest: tuple[int, float]
    rhythm_alerts: list[tuple[str, str, str, float]]   # cena, kind, âncora, ms
    citations: list[tuple[str, str, str, float]]       # cena, âncora, ativo, ms
    assets_by_use: dict[str, list[str]]                # ativo -> cenas
    unused_assets: list[str]

def script_numbers(scenes, assets: dict[str, Asset], chars_per_second) -> ScriptNumbers: ...
def render_block(numbers: ScriptNumbers) -> str: ...   # Markdown do bloco
def render_image_plan(scenes, numbers, assets) -> str: ...   # plano-imagens.md
```

**Refatoração necessária:** `_check_scenes` no `check.py` passa a usar o mesmo `shot_timings`. Assim o tempo de cada
plano tem uma fonte só, e o número que o bloco mostra é sempre o que o `vp check` usa. O comportamento do `vp check`
não muda, e os testes atuais dele provam isso.

### 4.2 O bloco no `outline.md`

Gerado entre dois marcadores, com os números e a comparação com o nicho:

```markdown
<!-- números: gerado por `vp numeros`; não editar à mão -->
## Números do roteiro (gerado)

- 89 cenas, 159 planos (15 com texto), 13 pausas, 2.002 palavras, ~791 s (~13 min) a 14 caracteres por segundo.
- "você": 15 vezes em 14 cenas; 6 no último décimo.
- Ritmo: abertura (primeiros 10%) com 21 planos em ~79 s (~15,9 por minuto); o resto com 138 planos em ~712 s.
- Alertas de ritmo do `vp check` (13): S019 photo "De onde veio a frase" ~6,1 s; …

| # | Cena | Âncora | Ativo `Citacao` | Tempo |
|---|---|---|---|---|
| 1 | S001 | "Light faz um deles escrever" | `viz-trailer-omega-regras` | ~4,8 s |
…

### Formato × nicho (perfil de 2026-10-18, grupo H, n = 20)

| Medida | Roteiro | Terço de cima | Terço de baixo | Força |
|---|---|---|---|---|
| "você" por mil | 7,5 | 7,9 | 4,6 | hint (ρ 0,28) |
…
<!-- números: fim -->

Sem `formato-brief.json` no episódio, a seção "Formato × nicho" diz isso numa linha e o resto do bloco sai igual.
```

O que fica fora do bloco continua escrito à mão. As seções do outline que hoje repetem esses números ("Duração e
números", a tabela de quadros) passam a apontar para o bloco.

### 4.3 Comando `vp numeros <id>`

Um handler em `HANDLERS` (`app/cli.py`), no padrão dos outros.
- **Sem opção:** imprime o bloco e diz se o `outline.md` e o `plano-imagens.md` batem com ele. Não grava nada.
- **`--escrever`:** grava o bloco no `outline.md` (troca o que está entre os marcadores, ou acrescenta no fim) e
  regrava o `plano-imagens.md`.
- **`--used-in-scenes`:** acerta o `used_in_scenes` de cada `assets/<id>.json` a partir do roteiro. Só mexe nesse campo.
  Ativo `approved` só muda com essa opção explícita, e o comando diz quais mudaram.
- **Idempotente:** rodar duas vezes seguidas não muda nada.

### 4.4 `vp check`

Quatro avisos novos, todos `alerta` e nunca `erro`:
- `outline.md: bloco de números desatualizado (rode vp numeros <id> --escrever)`, quando o bloco existe e difere do
  calculado;
- `outline.md: sem bloco de números`, só quando o `scenes.json` já tem algum `asset_id`;
- `assets/<id>.json: used_in_scenes diz [...], o roteiro usa [...]`;
- `formato: <medida> = <valor>; o terço de cima do nicho tem <valor> (pattern, ρ <x>)`. Só para medida com força
  `pattern` que esteja do lado do terço de baixo (ADR 031, parte D). Um `hint` nunca vira alerta.

### 4.5 Skills e agentes

- **`roteiro-explicativo` e o agente `roteirista`:** não escrevem número do roteiro à mão. Rodam
  `vp numeros <id> --escrever` antes de entregar (o Bash do agente passa a permitir esse comando).
- **`plano-de-imagens`:** o passo 7 troca o recálculo à mão por `vp numeros <id> --escrever --used-in-scenes`.
- **`checagem`:** o bloco gerado está fora da conferência, porque o código já confere. O verificador olha só a parte
  escrita à mão e o `vp check`.
- **`analise-de-formato`:** o passo de análise termina com `analisar.py --brief`. O perfil do nicho passa a ser um
  arquivo que o roteiro lê, e não só um relatório.
- **`roteiro-explicativo`:** com o perfil no episódio, o roteirista lê a seção "Formato × nicho" do bloco. O
  `outline.md` ganha a seção "Formato", escrita à mão: cada `pattern` seguido, ou não, e por quê (ADR 031, parte C).

## 5. Testes (sem rede)

- **Fixture `tests/fixtures/episodes/numeros-death-note/`:** um recorte do Death Note com 21 cenas, de S115 a S060, o
  mesmo da prévia de 3 minutos. Leva os `assets/*.json` usados (só os JSON, com a mídia trocada por arquivos vazios
  com o mesmo nome) e ao menos um ativo `Citacao`. Os números esperados ficam escritos no teste.
- **Casos:**
  - pausa conta 10 caracteres no tempo e não conta na palavra;
  - "você" com maiúscula e com pontuação ("você?", "Você,");
  - plano `broll` longo não gera alerta, e `photo` longo gera;
  - `lower_third` logo depois de foto (sobreposição) tem o próprio tempo;
  - cena sem planos (forma v1);
  - ativo `Citacao` usado duas vezes conta dois usos e um ativo;
  - ativo baixado e sem uso aparece em "fora do vídeo".
- **Bloco:**
  - `render_block` é estável (mesma entrada, mesmo texto);
  - `--escrever` duas vezes não muda o arquivo;
  - texto fora dos marcadores fica intacto, byte a byte.
- **`vp check`:**
  - os testes atuais passam sem mudança;
  - um teste novo de cada aviso.

## 6. Aceite com o Death Note (local, fora do CI)

`data/episodes/` não vai para o Git, então esta prova roda à mão e o resultado entra no PR. Rodando
`vp numeros death-note-fins-meios` no roteiro da rodada 36, os números têm de ser os que o verificador aprovou. Calculei
hoje com as funções atuais:

| Número | Esperado |
|---|---|
| cenas e planos | 89 e 159 |
| planos com texto | 15 |
| pausas e palavras | 13 e 2.002 |
| duração | ~791 s |
| "você" | 15 em 14 cenas; 6 no último décimo |
| alertas de ritmo | 13: S019, S039, S120, S055, S056, S062, S064, S068, S123, S025, S048, S140, S132 |
| quadros `Citacao` | 6 usos de 5 ativos: S001 4,8 s · S003 3,0 · S145 3,3 · S057 1,7 · S060 3,4 · S098 4,7 |
| ativos usados | 37 |
| abertura (regra dos 10%) | 21 planos em ~79 s |
| medidas na unidade do nicho | as da tabela da seção 3.3 (por exemplo, 73 trocas, 5,5 por minuto; "você" 7,5 por mil; fonte 5,0 por mil) |
| perfil | `formato-brief.json` gerado do `tercos.csv` atual com os valores da coluna "H" da seção 3.3 |

Qualquer diferença aponta erro no código ou no outline, e o PR diz qual foi. Só depois disso, e com a sua decisão, o
outline do Death Note ganha o bloco (ver D1).

## 7. Plano de implementação (um PR)

1. **Extrair:** `shot_timings` do `check.py` para `numbers.py`. O `check.py` passa a usá-la, e os testes atuais devem
   passar sem mudança.
2. **Calcular:** `script_numbers`, com a fixture e os testes da seção 5.
3. **Escrever:** `render_block` e `render_image_plan`, com os testes de estabilidade e de texto intacto.
4. **Comando:** `vp numeros`, com `--escrever` e `--used-in-scenes`, e os testes de CLI.
4b. **Perfil do nicho:** `analisar.py --brief`, o script que copia o perfil datado para o episódio, as medidas na
   unidade do nicho (seção 3.1), o teste que confere que os padrões de palavra são iguais aos do `analisar.py`, e a
   seção "Formato × nicho" do bloco.
5. **Avisar:** os três avisos do `vp check`.
6. **Método:** skills e agentes (seção 4.5), o CLAUDE.md §10 (comando novo) e o fluxograma 1 (o passo
   `vp numeros` no lugar do `[falta]`).
7. **Aceite:** rodar no Death Note sem `--escrever` e colar no PR a comparação da seção 6.
8. **Fechamento:** `pytest` e `ruff check .`.

Estimativa: um PR médio. São cerca de 300 linhas de código e 250 de teste. Não há dependência nova.

## 8. Decisões para o dono

- **D1. O bloco gerado entra no carimbo do gate 2?** Recomendo que **não**: o carimbo e o parecer ignoram o que está
  entre os marcadores, como já ignoram o `asset_id` (PR #169). O bloco sai inteiro do `scenes.json`, que já é
  carimbado, então não esconde nada. Se entrar no carimbo, cada `--escrever` pede uma nova aprovação sua.
- **D2. Abertura:** regra fixa dos 10%, que é reproduzível (recomendo), ou a faixa de cenas que o roteirista declara
  no outline.
- **D3. `plano-imagens.md`:** gerado pelo mesmo comando (recomendo) ou continua à mão.
- **D4. ADR 031, partes B e D:** a comparação com o nicho implementa essas duas partes, que ainda são propostas.
  Aceitar as duas junto com este trabalho, ou entregar só os números agora e a comparação depois.
- **D5. Quando uma medida vira `pattern`:** proposta: |ρ| ≥ 0,4 com n ≥ 20, e o terço de cima diferente do de baixo na
  mesma direção do ρ. Hoje nenhuma medida do grupo H chega lá. No H0, `plano_medio_s` tem ρ −0,57, mas com n = 18, abaixo do mínimo.

## 9. Riscos e depois

- **Estimativa e voz real:** os tempos são estimados a 14 caracteres por segundo, e a voz real varia. O bloco diz que é
  estimativa. Usar a duração dos WAVs quando existirem é um passo seguinte, pequeno, porque o `shot_timings` já recebe
  a duração por cena.
- **Outline sem marcadores:** em episódios antigos, o `--escrever` acrescenta o bloco no fim e não toca no resto. As
  linhas antigas com números ficam até alguém tirá-las.
- **Duas fontes de verdade:** se a refatoração do `check.py` for pulada, o bloco e o `vp check` podem divergir. Por
  isso o passo 1 vem antes de tudo.
