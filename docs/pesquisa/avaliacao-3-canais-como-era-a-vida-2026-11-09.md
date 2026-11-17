# Avaliação de 3 canais do nicho "como era a vida" e saturação (2026-11-09)

Pedido do dono. Dados: vidIQ (08–09/11/2026, ~215 créditos nesta frente, contando a coleta anterior), miniaturas, 6 vídeos baixados em 360p com `baixar.py` e medidos com `medir.py` e `folha_densa.py`
(`data/cache/nicho/Como-era-a-vida/`, fora do Git). Leitura das folhas por 3 subagentes **sem saber as views**; relatórios completos em
`docs/pesquisa/canais-como-era-a-vida-2026-11-09/`. Evidência de mercado anterior: `vidiq-como-era-a-vida-2026-11-08.md`.
Limites: 6 vídeos, quadros em 360p, leitura por modelo, cortes/min é só corte seco (subestima vídeo gerado por IA), viés de sobrevivência.

## Os 3 canais e a amostra (campeão × fraco do mesmo canal)

| Canal | Vídeo forte | Vídeo fraco |
|---|---|---|
| Reconstrução Histórica (70 mil insc., IA realista) | Castelo 1200: 781 mil | Casa de camponeses: 50 mil |
| História Clássica (15 mil, "Brasil em [ano]") | Brasil 1964: 749 mil | Brasil 1969: 8 mil |
| Uso dos porquês (77 mil, bonecos de palito) | "O que faziam o dia todo": 291 mil | "Último dia de um neandertal": 2 mil (7 dias de vida) |

**Palpite cego dos agentes:** acertaram 2 de 3. Reconstrução Histórica (castelo, 70%) e Uso dos porquês (dia todo, 70%) acertaram. História Clássica errou (apontou o 1969, 55%).
Nos dois vídeos da História Clássica o roteiro e a produção são quase idênticos; a diferença de 90x vem do tema/ano, não da execução (hipótese: 1964 e a demanda por "ditadura", +84%).

## Critérios

| Critério | Reconstrução Histórica | História Clássica | Uso dos porquês |
|---|---|---|---|
| Miniatura | cena realista de IA, pouco ou nenhum texto, **um detalhe chocante** (rato na colher da taverna: 552 mil); fracos usam o mesmo estilo mas sem ponto focal | ano gigante amarelo + selo vermelho ("Ninguém imaginava isso!"); **mesmo molde em hits e fracos** | boneco + 2 a 4 palavras amarelas em caixa alta; **mesmo molde em hits e fracos** |
| Roteiro | 2ª pessoa sensorial, promessa + "vai te surpreender"; castelo tem arco (viradas em 9:05, 15:30, 18:37), camponeses é lista sem conflito; fonte vaga | "Em [ano],…" catálogo; mesma fórmula nos dois; 0 fontes; 0 menções a golpe/AI-5 | humor + 2ª pessoa; o forte tem espinha por hora do dia com retornos; o fraco vira catálogo de sítios, e o título ("último dia") não é cumprido |
| Comunicação | narrador grave, épico, 124 pal/min | didático, nostálgico, 120 a 127 pal/min | coloquial, irônico, 152 a 170 pal/min |
| Sequência visual | vídeo gerado por IA, plano de ~8 s, protagonista com rosto recorrente, sem texto na tela; falhas: anacronismos (fogão, jeans), sem aviso de IA | acervo P&B + IA genérica, ~100 trocas em 20 min, timecode de fonte à mostra, sem crédito | bonecos 2D, ~14 cortes/min, "você" azul e casal recorrentes; animação real só na abertura, meio é imagem parada com balão |
| Custo para nós | alto (IA realista, consistência) | alto (acervo licenciado ou arte original) | **o mais barato no motion-kit** (cenários planos, 2 a 3 bonecos com poses, balão) |

## Saturação

**Veredito: saturado no formato "reconstrução realista por IA em massa"; não saturado em tópico específico nem em formato com mecanismo/desenho.** O problema real do canal é cold start, não só o nicho.

Sinais de saturação:
1. **Onda de entrantes em 2026:** Reconstrução do Passado (criado 07/03, 68,7 mil inscritos), Arquivos da História (14/03), Atlas do Impossível (19/09, **72 longos em 30 dias**), Bíblia em Ruínas, Codex da Humanidade, além de ≥ 15 canais "Brasil por lugar/ano" nos outliers do vidIQ (vários marcados IA).
2. **Os 4 canais acompanhados explodiram e estabilizaram:** Reconstrução Histórica ganhava ~13 mil inscritos/mês (abr a jun) e 1,7 mil em outubro, publicando 23 a 28 longos/mês (views estáveis em ~1,3 milhão/mês); Uso dos porquês foi de 3 mil a 66 mil em 6 semanas e +2,2 mil em outubro, com vídeos recentes entre 2 mil e 12 mil; História Clássica parada em 15,1 mil desde agosto; História Sem Filtro (o 736x) parou em 1,67 mil e de postar.
3. **Demanda:** "como era a vida" −55% no vidIQ.
4. **Fórmula repetida** entre vídeos (abertura em 2ª pessoa sensorial; "Em [ano],…"): risco de conteúdo repetitivo/em massa (CLAUDE.md §12).

Sinais contra: buscas específicas com concorrência baixa (Polônia 1985: 12,2 mil/mês, competição 15; Brasil 1995: competição 8), canais de 1,7 mil inscritos com hits (736x), e nenhum dos três cita fonte nomeada nem explica mecanismo com diagrama.

## O que levar

1. Tópico decide mais que miniatura ou molde (mesmo molde com 8 mil e 749 mil).
2. Vídeos fortes têm um arco ou espinha (cerco, as horas do dia) e fecho amarrado à tese; os fracos são catálogos.
3. Fonte nomeada e contexto sensível tratado são lacunas dos concorrentes; usar como diferencial é decisão do dono (ADR 055 dispensa fichas neste formato).
4. Bonecos de palito + diagramas é o caminho mais barato e menos disputado: modelo de produção, sem copiar personagem nem composição.
5. Não competir em volume nem em IA realista.
