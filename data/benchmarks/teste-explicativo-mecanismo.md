# Teste: explicativo de mecanismo (6 vídeos, canal novo)

Decisão do dono em 2026-11-09, depois da avaliação de 6 canais de dois nichos (`docs/pesquisa/avaliacao-3-canais-como-era-a-vida-2026-11-09.md` e
`docs/pesquisa/avaliacao-3-canais-explicativo-curiosidade-2026-11-09.md`): rodar **6 vídeos de teste** com a régua abaixo, num **canal novo criado pelo dono**.
Este arquivo é o registro único do teste (plano, régua e leituras). Os números de mercado vêm do vidIQ de 2026-11-08/09 (estimativas, sem impressões nem CTR).

## Pergunta do teste

Um vídeo curto (4 a 7 min) que **mostra o mecanismo de um objeto ou fenômeno com diagrama animado, no momento em que a fala o explica, e com a fonte na tela**, retém
e atrai mais do que os ensaios atuais do Cena e Conceito? O que ninguém dos 6 canais lidos faz é animar o mecanismo e dar fonte conferível; é essa a aposta.

## Régua (proposta do assistente, aprovada pelo dono em 2026-11-09)

- **Um vídeo "passa"** quando, em **28 dias** (D28) de publicação pública, tem **mais de 261 visualizações** e **porcentagem média visualizada ≥ 28,4%** (Studio).
  Base: `montaigne-desapego`, o melhor longo do Cena e Conceito (261 views em 12 dias, vidIQ de 08/11; 28,40% assistido no relatório de 28–30/10).
- **O teste continua** só se **ao menos 2 dos 6** passam. Caso contrário, **para**.
- Limite conhecido: as duas bases têm janelas diferentes (12 dias × 3 dias de relatório), e o canal novo parte de zero inscritos. A régua é uma linha de corte, não prova de causa.
  Visualização do dono e de conhecidos não se separa nos dados (CLAUDE.md §12: amigos não contam). O D7 é só sinal precoce; a decisão é no D28.

## O que é fixo nos 6 e o que varia

**Fixo:** duração 4 a 7 min, 16:9, pt-BR, formato `explainer`, objetivo `explicar`, funil `topo`; título em pergunta com o objeto (até 65 caracteres); **molde único de capa**
(objeto ou diagrama em primeiro plano, até 3 palavras em caixa alta, sem rosto de terceiros); cartão de fonte na tela; **um diagrama animado do mecanismo** em estados
(inicial → ação → final) ligado à fala; voz final do dono (ADR 016); trilha; público; 1 vídeo por semana, mesmo dia e hora (não testar horário, `crescimento-youtube-embalagem-hipoteses-2026-10-23.md` OF09).

**Varia:** o tema (um objeto ou fenômeno por vídeo) e, **em alternância, o tipo de abertura**: *em cena* (V1, V3, V5) × *em pergunta* (V2, V4, V6). A abertura em cena é a única
diferença que a análise do canal associou a retenção maior (28,4% × 13–19%, n = 3, hipótese fraca). Medida secundária: retenção aos 30 s.

## Hipótese principal (registrar antes; copiar para `metrics.json.hypothesis` na publicação)

> **H-MEC:** o diagrama animado que mostra o mecanismo no momento em que ele é dito, com a fonte na tela, leva o vídeo a mais de 261 visualizações e a ≥ 28,4% de porcentagem
> média visualizada em 28 dias. Variável: formato (mecanismo animado + fonte). Medida: visualizações e porcentagem média visualizada no D28 (Studio); contexto: impressões, CTR,
> origem do tráfego, retenção aos 30 s. Secundária: abertura em cena × em pergunta, por retenção aos 30 s.

## Os 6 vídeos (ordem de produção)

Demanda do vidIQ de 2026-11-09 (volume estimado por mês, competição 0 a 100). "Quem já fez" vem de uma busca de breakout em pt, **não é lista completa**: não prova ausência.

| # | id | Tema | Abertura | Busca/mês · competição | Quem já fez (resultados vidIQ) | Título provisório |
|---|---|---|---|---|---|---|
| 1 | `mec-fechadura-pt` | Fechadura | em cena | ~6,0 mil · 14 | Nenhum explicativo direto do mecanismo; fechadura digital (43,9 mil), "chave bóia por dentro" (20 mil) | Como funciona uma fechadura? O que a chave realmente faz |
| 2 | `mec-macaco-carro-pt` | Macaco de carro | em pergunta | ~49,7 mil · 25 | Nenhum direto; adjacentes: Oficina do Palito (4 mil insc.) com a direção elétrica explicada, 131,6 mil, e a hidráulica, 47,7 mil | Como funciona o macaco de carro? Por que ele levanta o carro |
| 3 | `mec-aviao-velocidade-pt` | Velocidade dos aviões comerciais | em cena | ~16,4 mil · 37 (+46%) | Adjacente: "Aviões usam querosene e não gasolina" 286,7 mil (6,7 mil insc.); Por Trás Do Simples tem altitude, 2,8 mil | Por que os aviões comerciais não voam mais rápido? |
| 4 | `mec-sextante-pt` | Sextante | em pergunta | ~7,7 mil (comp. 9) e ~4,6 mil (comp. 7) | Nenhum relevante retornado | Como funciona um sextante? Medir o céu para achar o caminho |
| 5 | `mec-termeletrica-pt` | Termelétrica | em cena | ~8,9 mil · 31 | Além da Tomada (184 insc.): 1,3 mil views em 6 dias | Como funciona uma termelétrica? Do combustível à tomada |
| 6 | `mec-armadura-pt` | Armadura de cavaleiro | em pergunta | ~12,5 mil · 39 | Nenhum explicativo retornado (só jogos) | Como funciona uma armadura de cavaleiro? Dava para se mover? |

Por que essa ordem: V1 é o diagrama mais simples; V2 tem o maior volume; V6 vem por último por ser a ponte com o "como era a vida" (história + mecanismo) e a mais difícil de modelar.
Os temas **não repetem** vídeo consagrado dos concorrentes (lição do EfeitoDomino: copiar o tema do hit deu 230 views contra 291 mil).

## Ciclo de cada vídeo (nada disso pula os gates do CLAUDE.md §4)

1. Pauta (este repositório, `data/episodes/<id>/pauta.md`) → **dono aprova tema e recorte**.
2. Fontes (≥ 2 independentes) → fichas → **gate 1**.
3. Roteiro com o `roteirista` (explicativo, com `claims` e `source_ids`) → `vp check` → verificador → **gate 2**.
4. Plano de animação (estado inicial, blocos e setas, ação, estado final, fonte) **antes** da voz e do render (`renders/serie-conceitos/direcao-editorial.md`).
5. Voz final → render → imagens/ativos com licença (**gate 3**) → trilha → prévia e descrição (**gate 4**).
6. Publicação autorizada (`vp postiz`, dúvida cega) no canal novo; `vp metricas iniciar` com a hipótese acima, **na data real da publicação**.
7. Leituras D7 e D28 registradas no `metrics.json` e na tabela de baixo.

**Regras do teste:** registrar a hipótese antes de produzir; não mudar título, miniatura ou visibilidade depois de publicar sem anotar a data e o motivo aqui (hoje 4 de 12 títulos do Cena e
Conceito diferem dos agendados); publicar sempre **público**; o rótulo de conteúdo sintético segue uma regra só, decidida pelo dono uma vez (voz clonada do próprio autor, diagramas desenhados por código).

## Checklist do canal novo (é do dono; nada disso foi feito pelo assistente)

- [ ] Criar o canal e escolher nome e handle (não copiar Por Trás Do Simples, Por Que Será?, Uso dos porquês, EfeitoDomino). Registrar aqui: `canal: ________`.
- [ ] Descrição do canal e dos vídeos declarando a voz clonada do autor e o uso de IA, como nos demais canais.
- [ ] Conectar ao Postiz (login e autorização do dono); conferir o ID com `vp postiz integrations`. **Não reaproveitar o ID de outro canal** (a troca de ID em 31/10 perdeu um agendamento).
- [ ] Decidir se o `config/canal.toml` (hoje com o nome do Cena e Conceito e a tag de afiliado) precisa de entrada para o canal novo. Não foi alterado.
- [ ] Passo do Studio por vídeo: legenda (`captions.srt`), comentário fixado, tela final, categoria, rótulo; marcar feito ou não na tabela de baixo.

## Registro das leituras (preencher no Studio)

Janelas: D7 = 7 dias após a publicação, D28 = 28 dias. Passa = > 261 views **e** ≥ 28,4% média visualizada no D28.

| # | id | Publicado (real) | Título vivo | Views D7 | Impr. D7 | CTR D7 | % média vis. D7 | Views D28 | % média vis. D28 | Retenção 30 s | Passa? | Notas (mudanças, Studio, visibilidade) |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | mec-fechadura-pt | | | | | | | | | | | |
| 2 | mec-macaco-carro-pt | | | | | | | | | | | |
| 3 | mec-aviao-velocidade-pt | | | | | | | | | | | |
| 4 | mec-sextante-pt | | | | | | | | | | | |
| 5 | mec-termeletrica-pt | | | | | | | | | | | |
| 6 | mec-armadura-pt | | | | | | | | | | | |

**Decisão no fim:** passaram ___ de 6. Se ≥ 2: continuar e decidir o próximo lote. Se < 2: parar e registrar o motivo provável (tema, execução, exposição).

## O que ficou de fora de propósito

Notícia e tema atrelado a evento (não cabe no ritmo do pipeline); boneco de palito (clonado); imagem de IA realista; "como era a vida" em volume. O "como era a vida" segue só como teste do piloto
`idade-media-ser-rico`, com leitura em 14/11 e 05/12.
