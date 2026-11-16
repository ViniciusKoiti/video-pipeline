# Série Kafka — Shorts técnicos em pt (2026-11-15)

Pauta e fontes: `serie.md`. Cenários cena a cena: `cenarios.md`. Fontes primárias numeradas: `fontes/`.
Cada episódio tem a pasta `<id>/` com `content.pt.json`, `narracao.pt.json`, `lottie/`, `licencas.json`,
`fontes.md`, `posts/post-youtube-pt.json` e `final.pt.mp4`. A pasta de produção (voz, renders do kit, pacote do
gate 4) é `data/episodes/<id>/`, fora do Git.

| # | id | Título proposto | Data proposta |
| --- | --- | --- | --- |
| 1 | `short-kafka-por-que-existe-pt` | PEDIDO TRAVADO: POR QUE O KAFKA EXISTE | seg 16/11 12h |
| 2 | `short-kafka-fila-log-pt` | LER NÃO APAGA: FILA OU LOG NO KAFKA | ter 17/11 12h |
| 3 | `short-kafka-particao-pt` | PEDIDO EMBARALHADO? A CHAVE DO KAFKA RESOLVE | qua 18/11 12h |
| 4 | `short-kafka-qual-usar-pt` | KAFKA, RABBITMQ OU SQS: QUAL USAR? | qui 19/11 12h |

Datas e títulos são proposta (títulos em CAIXA ALTA, força nas duas primeiras palavras, pedido do dono em
2026-11-15): decisão do dono no gate 4. Nada foi agendado.

## Como refazer

```bash
uv run --no-sync python renders/serie-kafka/gerar.py            # content, narração e Lottie dos 4
E=data/episodes/<id>
.venv/bin/vp short voz $E $E/narracao.json                       # voz clonada (Modal), só com pedido do dono
.venv/bin/vp short tempos $E $E/content.json $E/narracao.json
(cd $E && node ~/projetos/motion-kit-rebase/packages/motion-video/dist/video.mjs render content.voz.json > render.json)
.venv/bin/vp short juntar $E $E/out/production/<runId>/video.mp4 $E/content.voz.json $E/narracao.json \
  --saida renders/serie-kafka/<id>/final.pt.mp4
uv run --no-sync python renders/serie-kafka/posts.py
.venv/bin/vp short gate renders/serie-kafka/<id>/final.pt.mp4 renders/serie-kafka/<id>/posts/post-youtube-pt.json --episodio <id>
```

O kit roda pelo worktree `~/projetos/motion-kit-rebase` (motion-video 0.3.1): o checkout principal do motion-kit
está no branch `feat/gym-reception`, sem as cenas `versus`/`lanes`, e o `dist` dele importa o nome antigo do pacote.

## Controle obrigatório (direção editorial)

| Item | Antes da voz/render | Depois do render |
| --- | --- | --- |
| Aplicação | app de delivery fictício; serviços de pedidos, pagamento, restaurante, entregador, notificação | celular e blocos reconhecíveis nos quadros do ep1; eps 2–4 a conferir no quadro final |
| Decisão de System Design | ep1 chamada direta × tópico; ep2 fila × log; ep3 chave e nº de partições; ep4 fila ou log pelo padrão de consumo | dita na fala e mostrada no `versus` final de cada um |
| Benefício e limite | só o que as fontes dizem (`fontes.md` de cada episódio); sem medição | conferido contra o `fontes.md` |
| Explicação visual | fluxos com fichas e estados, log com ponteiros, raias, esteira, código | quadros conferidos no ep1; eps 2–4 conferidos depois do render |

## Pendências

- **Gate 4 de cada um é do dono:** assistir `data/episodes/<id>/renders/final.mp4` e
  `vp approve <id> --step preview --notes "assisti"`.
- **Música:** planejada como fundo baixo com `ytal-spirit-of-fire` (a mesma de idempotência), mas o
  `vp short juntar` ainda não mistura música: **música planejada, mistura pendente**. Os MP4 saem só com voz.
- **Divulgação:** a descrição diz "Voz clonada com IA"; marcar "conteúdo alterado ou sintético" no Studio.
- **Mídia no post:** `vp postiz upload` antes do `pacote`; a lista `image` do post está vazia.
- **en e Instagram:** não feitos.
- **Hipótese (para `metrics.json` depois de publicar):** abrir com o celular (sem cartão de pergunta) mantém mais
  gente nos 3 primeiros segundos que os Shorts técnicos anteriores; medida: retenção aos 3 s e "continuaram
  assistindo" no Studio, aos 7 e 28 dias.

## Versão em inglês (2026-11-15)

`traduzir.py` gera cada `<base>-en` a partir do pt já montado: mesmas cenas, tempos, números e animações; só os
textos mudam (dicionário por episódio, e texto em pt sem tradução é erro), com o código Java em inglês
(`orderId`, tópico `orders`) e horários em formato americano. A abertura do celular é reescalada no tempo para a
fala em inglês (`WARP`), sem mudar o `content.json`. `vp traducao <id>-en` sem problemas nos quatro (ADR 034);
voz clonada com as referências em `data/voice-references/en/`. Posts em `posts/post-youtube-en.json`, no canal em
inglês dos Shorts técnicos.

| # | id | Título proposto |
| --- | --- | --- |
| 1 | `short-kafka-por-que-existe-en` | ORDER STUCK: WHY KAFKA EXISTS |
| 2 | `short-kafka-fila-log-en` | READING DOESN'T DELETE: QUEUE OR LOG IN KAFKA |
| 3 | `short-kafka-particao-en` | SCRAMBLED ORDERS? KAFKA'S KEY FIXES IT |
| 4 | `short-kafka-qual-usar-en` | KAFKA, RABBITMQ OR SQS: WHICH ONE? |

Gate da tradução (dono): `vp approve <id>-en --step translation`; gate 4 como no pt.
