# Reel Amazon: "Como a Amazon adiciona um servidor sem esvaziar o cache?" (plano de animação, 2026-11-08)

**Texto e fontes:** `../../reels-por-empresa.md` (Reel 1), `../../fontes.md` (F-D1 a F-D5). **Medição:** `../../demo/resultado.txt`
(Java 25.0.4.1, 15 rodadas). **Episódio:** `data/episodes/reel-consistent-hashing-amazon-pt` (e `-en`).
**Saída:** YouTube pt `@viniciusnakahara`, segunda 09/11/2026 12h (decisão do dono, 2026-11-08); en depois.
**Capa:** `../../miniaturas/capa-reel-1-amazon.jpg` (a pergunta e o logo oficial da Amazon; aprovada pelo dono).

## 1. Cenas (uma por bloco de fala), estados e fonte

| Cena | Fala (pt) | Estado inicial → final | Blocos e setas | Fonte |
| --- | --- | --- | --- | --- |
| `pergunta` | Como a Amazon adiciona um servidor sem esvaziar o cache? | cartão da pergunta → pergunta escrita | — | pauta |
| `anel` | No Dynamo, chaves e servidores ficam num anel, e cada chave vai para o primeiro servidor no sentido horário, e quando um servidor entra, só os vizinhos sentem a mudança. | anel S1–S4 com 12 chaves → S5 entra e toma só o seu arco (3 de 12 trocam, todas para S5) | chave → primeiro servidor no sentido horário (pulso) | Dynamo §4.2 (F-D1, F-D2); Javadoc `ceilingEntry` (F-T1) |
| `medicao` | Na minha medição, o resto do hash mexeu em oitenta por cento das chaves, e o anel com cem pontos por servidor, em vinte. | duas colunas → vencedor destacado | módulo × anel, 100 pontos | `resultado.txt` (`movidas_pct`) |
| `pontos` | Com um ponto só a carga fica torta, e por isso o Dynamo usa vários pontos por servidor, os nós virtuais. | barras → 251,5 / 140,2 / 111,2 | carga do servidor mais cheio, em % da ideal | `resultado.txt`; Dynamo (F-D3, F-D4) |
| `fecho` | Quantos pontos virtuais você daria para cada servidor? | — → convite | — | pergunta ao público |

Duração estimada da fala (2,2 palavras/s): ≈ 42 s (meta 35 a 45 s). Os tempos finais vêm dos WAVs (`vp short tempos`).
Entregas: `hook` na abertura, `invite` no fecho, o resto `neutral` (60% neutras; sem `turn`, regra da skill).

## 2. Impacto no System Design

1. **Aplicação:** cache distribuído de sessões; quem escolhe o servidor é o cliente do cache.
2. **Decisão:** resto do hash ou anel, e quantos pontos por servidor.
3. **Benefício medido:** 80,18% → 20,13% das sessões trocam de servidor ao passar de 4 para 5.
4. **Limite medido:** com 1 ponto o servidor mais cheio recebe 251,5% da carga ideal; com 100, 111,2%.
5. **Lacuna declarada:** só em memória, sem rede nem cache real; a explicação do mecanismo é do Dynamo (2007).

## 3. Controle obrigatório (direção editorial)

| Item | Antes da voz | Depois do render |
| --- | --- | --- |
| Aplicação | cache de sessões, 4 → 5 servidores (`anel`) | a conferir nos quadros |
| Decisão de System Design | resto × anel e pontos por servidor (`pergunta`, `fecho`) | a conferir |
| Benefício e limite | 80,18% → 20,13%; 251,5 / 140,2 / 111,2% (`medicao.json`) | a conferir |
| Sequência animada | anel com pulso, arco e S5 (`anel`); versus e barras (`medicao`, `pontos`) | a conferir nos quadros de início, leitura e fim, incluindo o texto dentro do Lottie |

## 4. Música (decidida pelo dono em 2026-11-08: com música no YouTube; Instagram sem)

- **Faixa:** `ytal-spirit-of-fire` ("Spirit of Fire", Jesse Gallagher; `data/music/catalog.json`: calmo, inspirador, intensidade 3,
  sem vocal, 608 s, dura mais que o vídeo). Licença: YouTube Audio Library, **só no YouTube** (`data/benchmarks/termos-musica.md`).
- **Plano por cena** (nível `low`, fade de 0,6 s):
  - `pergunta` (`hook`): fundo baixo desde o primeiro quadro.
  - `anel`: fundo baixo (explicação do mecanismo), sai no fim de "só os vizinhos sentem a mudança".
  - `medicao`, `pontos`: **sem música**, para os números medidos aparecerem limpos.
  - `fecho` (`invite`): o fundo volta em "Quantos pontos virtuais" e sai no último quadro.
- **Mistura:** `vp short juntar` não mistura música. Por decisão do dono (2026-11-08), a mistura é feita fora do `juntar`, como na
  idempotência, por `misturar_musica.py` (nesta pasta), que lê o `content.voz.json` para achar os tempos reais das cenas.
  A saída com música é só a do YouTube; o pacote do Instagram usa o vídeo sem a faixa.
- **Crédito:** a descrição do YouTube cita a faixa; o gate 3 da faixa neste episódio é do dono.
