# Consistent hashing em Java: plano de animação e narração

**Pauta:** `data/episodes/short-consistent-hashing-java-pt/pauta.md` (aprovada em 2026-11-03). **Roteiro e lição:**
`roteiro.md`. **Fontes:** `fontes.md`. **Medição:** `demo/resultado.txt` (Java 25.0.4.1, 15 rodadas).
**Publicação prevista:** seg 16/11, 12h. Nada agendado nem publicado.
Animações originais (Lottie) geradas por `gerar_animacoes.py`; licença e hash em `licencas.json`.

## 1. Abertura em quadros (direção de 2026-11-07) e capa

A cena `situacao` é a abertura em três quadros de caixas e pontos, sem personagem desenhado: (1) a aplicação e quatro
servidores com as sessões coloridas pelo dono, (2) entra o quinto servidor, (3) as sessões trocam de cor. A cena
`pergunta` (hook) escreve a pergunta no último quadro: "Por que quase toda sessão mudou de lugar?". O primeiro quadro
(`cover: true`) é o da cena `situacao`: "Cache de sessões · Java", app, quatro servidores e as sessões.

## 2. Trechos da fala e cenas (explicação)

| Cena | Trecho da fala | Estado inicial | Blocos e conexões | Ação visível | Estado final | Fonte |
| --- | --- | --- | --- | --- | --- | --- |
| `situacao` | "Entrou o quinto servidor do cache." | 4 servidores, 20 sessões coloridas | Aplicação → cada servidor (seta); cor do ponto = servidor dono | S5 aparece na fila; as sessões recebem a cor do novo dono | 16 de 20 sessões mudaram de cor | exemplo didático (resto por 4 e por 5) |
| `pergunta` | "Por que quase toda sessão mudou de lugar?" | cartão da pergunta | — | pergunta escrita | pergunta aberta | pauta |
| `modulo` | "O servidor é o resto do hash por N, e mudando o N, quase toda chave muda." | N = 4, chaves 0 a 19 com o resto embaixo | fórmula `hash(chave) % N` → resto → servidor Sx | N passa a 5; os restos e as cores mudam | 16 de 20 chaves em outro servidor | conta do exemplo; Dynamo/Karger (F-K2) |
| `medicao-modulo` | "Em cem mil sessões, oitenta por cento trocaram de servidor." | 0 | número | contagem até 80,18% | 80,18% | `resultado.txt` (módulo) |
| `anel` | "No anel, um TreeMap acha o servidor no sentido horário, e o novo toma só o seu arco." | Anel com S1–S4 e 12 chaves coloridas pelo dono | chave → primeiro servidor no sentido horário (pulso); S5 entra entre S2 e S3 | pulso percorre o arco; S5 aparece; o arco de S5 acende; 3 chaves ficam coral | 3 de 12 chaves trocaram, todas para S5; as outras 9 ficaram | Dynamo §4.2 (F-D1, F-D2); Javadoc `ceilingEntry` (F-T1) |
| `comparacao` | "Com cem pontos por servidor, só vinte por cento mudaram, e todas para o novo." | duas colunas | módulo × anel | vencedor destacado | 80,18% × 20,13% | `resultado.txt` (`movidas_pct`, `fora_do_novo`) |
| `pontos` | "Com um ponto por servidor a carga fica torta, e cem pontos virtuais deixam parelha." | barras | carga do servidor mais cheio, % do ideal | 251,5 → 140,2 → 111,2 | limite do anel: depende dos pontos | `resultado.txt`; Dynamo (F-D3, F-D4) |
| `fecho` | "Quantos pontos virtuais você usaria por servidor?" | — | — | convite | pergunta de decisão | pauta |

Duração estimada da fala (2,2 palavras/s): pt ≈ 41 s, en ≈ 44 s (alvo da pauta: 35 a 45 s). Os tempos finais vêm dos WAVs.

## 3. Sequência de impacto no System Design

1. **Aplicação:** a aplicação (cliente do cache) escolhe o servidor de cada sessão antes de consultar (cena `situacao`).
2. **Decisão:** módulo ou anel, e quantos pontos virtuais por servidor (cenas `modulo`, `anel`, `pontos`, fecho).
3. **Benefício medido:** 80,18% → 20,13% das sessões trocam de servidor ao passar de 4 para 5 (cenas `medicao-modulo`,
   `comparacao`); cada uma que troca é uma sessão que some do cache (miss) até ser recriada.
4. **Limite medido:** com 1 ponto por servidor o mais cheio recebe 251,5% da carga ideal; com 100 pontos, 111,2%
   (cena `pontos`). O módulo é mais parelho (100,7%), e o anel usa uma árvore para achar o servidor.
5. **Lacuna declarada:** tudo é em memória; sem rede, sem cache distribuído real, sem tempo de busca na tela.

## 4. Quadro de controle obrigatório (direção editorial)

| Item | Antes da voz/render | Depois do render |
| --- | --- | --- |
| Aplicação | cache de sessões em 4 → 5 servidores; cliente escolhe o servidor (`situacao`) | a conferir nos quadros |
| Decisão de System Design | módulo × anel; pontos por servidor; pergunta e decisão explícitas (`pergunta`, `fecho`) | a conferir |
| Benefício e limite | 80,18% → 20,13%; carga 251,5/140,2/111,2% (`medicao.json`, 15 rodadas) | a conferir; N e hash fixos |
| Explicação visual | restos e cores que mudam (`modulo`); anel com pulso, arco e S5 (`anel`); números da medição | a conferir nos quadros de início, leitura e fim, incluindo textos internos do Lottie |

## 5. Música (planejada; mistura pendente)

- **Divergência registrada:** a pauta (2026-11-03) diz "Sem música"; o pedido do dono de 2026-11-05 torna a trilha
  obrigatória em todo Short de conceito e só admite "sem música" com motivo escrito. Como a pauta não dá motivo,
  segui o pedido mais recente. Se o dono preferir sem música, basta ignorar esta seção.
- **Faixa:** `ytal-spirit-of-fire` ("Spirit of Fire", `data/music/catalog.json`: calmo, intensidade 3, sem vocal,
  608 s, dura mais que o vídeo), a mesma da idempotência. Licença: YouTube Audio Library, só no YouTube.
- **Plano (por cena):**
  - `situacao`, `pergunta`: fundo baixo desde o primeiro quadro.
  - `modulo`: fundo baixo, sem competir com a leitura dos restos.
  - `medicao-modulo`: sem música, para o número medido aparecer limpo.
  - `anel`: fundo baixo (virada), sem competir com o pulso e a troca de cores.
  - `comparacao`, `pontos`: sem música, resultado medido.
  - `fecho`: fundo baixo volta e sai no último quadro.
- **Instagram:** sai sem a faixa (licença só do YouTube).
- **Mistura:** `vp short juntar` ainda não mistura música. Fica registrado como `música planejada, mistura pendente`;
  não declarar o vídeo "com música" antes da mistura. O `music.json` não foi escrito (a mistura não existe).
