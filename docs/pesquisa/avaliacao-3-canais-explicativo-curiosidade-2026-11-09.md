# Avaliação de 3 canais de explicativo/curiosidade e saturação do nicho vizinho (2026-11-09)

Segunda rodada do pedido do dono (a primeira: `avaliacao-3-canais-como-era-a-vida-2026-11-09.md`). Mesmo método: vidIQ (crescimento, vídeos populares, miniaturas), 6 vídeos baixados em 360p
(`data/cache/nicho/Explicativo-curiosidade/`, fora do Git), medição e folhas densas do projeto, leitura por 3 subagentes sem saber as views. Relatórios completos em
`docs/pesquisa/canais-explicativo-curiosidade-2026-11-09/`. Limites: 6 vídeos, 360p, leitura por modelo, "cortes/min" subestima dissolves (e tem artefato de 10 s em um vídeo), checagens factuais dos agentes vêm da memória deles.

## Os canais e a amostra

| Canal | Perfil | Criado / tamanho | Forte × fraco da amostra |
|---|---|---|---|
| Por Trás Do Simples | "por que" de objetos do dia a dia, 4–7 min | 13/03/2026, 12 mil insc., 41 vídeos, 1,17 mi views | Régua: 542 mil × Pedras nos trilhos: 662 |
| Por Que Será? | "por que" de ciência, saúde e notícia, ~10 min, ~1 vídeo/dia | 27/09/2026, 15,5 mil insc. em 6 semanas, 2,2 mi views | Anestesia: 884 mil × Medo de aranha: 2 mil |
| EfeitoDomino | autoajuda/curiosidade com boneco de palito azul, ~8 min | 03/07/2026, 1,48 mil insc., 204 mil views | "Faça isso 5 min depois de comer": 147 mil × "O que humanos faziam o dia todo": 230 |

**Palpite cego:** 2 de 3 (Por Trás Do Simples e Por Que Será? acertaram; o EfeitoDomino errou: o agente apostou no vídeo de história, mas o de saúde teve 147 mil). Somando a rodada anterior: **4 de 6**.
Os dois erros têm a mesma causa provável: **tema com demanda de busca** (1964/ditadura; hábito de saúde), não execução (hipótese).

## Critérios

| Critério | Por Trás Do Simples | Por Que Será? | EfeitoDomino |
|---|---|---|---|
| Miniatura | objeto real + 2–3 palavras amarelas/brancas + seta vermelha; mesmo molde em hits e fracos | marca própria forte: fundo escuro, serifa amarela, uma frase ("VOCÊ APAGA."); mesmo molde em hits e fracos | boneco azul + frase em caixa alta; copia o molde dos canais de boneco |
| Roteiro | pergunta → resposta; o forte é curto (4:17) e literal; fraco com gancho melhor mas lenda contada como fato | paradoxo com atualidade, perguntas numeradas, laço aberto pago; o fraco vira lista de curiosidades e o título ("aranha pequena") não é cumprido | forte: 2 min de preâmbulo sem fato; fraco: cena imersiva e linha do dia, mas com nomes e números errados (Suzman, Wiessner) |
| Comunicação | 139–150 pal/min, locução com sinais de dublagem (pt-PT e "tu" misturados) | 160 pal/min, tom de aula, cita fonte vaga ("uma das revistas", "MIT", Wikipédia) | "você" 21–35/mil, tom de autoajuda, 5 pedidos de ação |
| Visual | IA/stock com dissolve, **nenhum desenha o mecanismo**; texto de IA com erro ("BUIFER ZONE") | slideshow sobre fusões, mas com diagramas úteis (gráfico, tabela da pupila, setas) | boneco 2D com deriva para 3D, cenários de IA, texto de IA errado ("Tosoo 10,000 years") |
| Fonte | quase nenhuma | **"Curiosidades com fonte"** é a promessa do canal; execução vaga | nenhuma, aviso médico responsável |

## Saturação deste nicho

**Veredito: menos saturado que "como era a vida" para um entrante pequeno, mas dominado por velocidade de tema e por gigantes; o estilo boneco de palito já está sendo clonado.**

A favor de entrar:
- Demanda enorme e fragmentada (qualquer "por que/como funciona"), sem prender o canal a uma época.
- Entrante com crescimento rápido: Por Que Será? (6 semanas, 15,5 mil), Por Trás Do Simples (12 mil em 8 meses).
- Qualidade geral baixa: erros de texto de IA, dublagem, lenda como fato, fonte vaga; **ninguém desenha o mecanismo** e o diferencial de fonte conferível está aberto.

Contra:
- **Taxa de acerto baixa** (calculada sobre as listas do vidIQ): Por Trás Do Simples 8 de 41 vídeos acima de 25 mil (20%) e o resto entre 300 e 1,4 mil; Por Que Será? 7 de ~36 acima de 30 mil, o resto 300–2,5 mil; EfeitoDomino 2 de ~50 (4%), a maioria 180–600. Hits concentram quase todas as views (régua = 46% do canal; um vídeo = 72% no EfeitoDomino).
- **Velocidade e gigantes:** "anestesia" saiu no Por Que Será? em 29/09 (884 mil) e depois no Fatos Desconhecidos (23 milhões de inscritos) em 22/10 (316 mil) e em outro canal em 25/10. Quem chega depois divide o tema. O modelo do Por Que Será? (13 vídeos em 8 dias, atrelado a notícia) não cabe num pipeline por código.
- **Cópia:** o EfeitoDomino usa o mesmo boneco azul do Uso dos porquês e copiou o tema do hit dele: 230 views contra 291 mil.
- Crescimento dos pequenos se estabiliza: Por Trás Do Simples +100 inscritos em 9 dias, ~5 mil views/dia.

## O que levar

1. Tema com **objeto ou fenômeno que todo mundo vê** (régua, vidro do carro, anestesia) vence molde e miniatura de novo.
2. O espaço aberto é **mostrar o mecanismo com diagrama animado e fonte conferível**, que é exatamente o que o motion-kit e as fichas do projeto fazem e nenhum dos 3 canais faz. Vídeo de 4 a 7 min (Por Trás Do Simples) é o formato mais barato.
3. **Não competir em notícia nem em volume**, e não copiar o boneco de palito: se houver personagem, ele precisa ser original e consistente.
4. Antes de apostar: testar 3 a 5 vídeos curtos em temas de objetos do dia a dia e ler impressões/CTR no Studio; a leitura de 14/11 do piloto vem antes.
