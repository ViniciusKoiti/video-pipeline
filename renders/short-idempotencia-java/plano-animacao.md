# Idempotência em Java: plano de animação e narração

**Estado:** produção de teste, ângulo A do bloco de novembro (`renders/serie-conceitos/teste-angulos-2026-11.md`).
**Pauta:** `data/episodes/short-idempotencia-java-pt/pauta.md`, aprovada pelo dono em 2026-11-03.
**Publicação prevista:** qua 18/11, 12h de Brasília. Nada foi agendado nem publicado.

## 1. Promessa e capa

- **Capa (cena `gancho`):** "Você clicou duas vezes em pagar. Por que cobrou só uma?"
- **Pergunta central (pauta):** quando o cliente não recebe a resposta e tenta de novo, como a API garante que o
  pagamento acontece uma vez só?
- **Ângulo A:** pergunta sobre o que a pessoa vive, sem termo técnico nos primeiros 5 segundos; a medição própria
  aparece antes de 20 segundos.

## 2. Trechos da fala e cenas

| Cena | Tipo | Fala (`narracao.json`) | Estado inicial → final |
| --- | --- | --- | --- |
| `gancho` | hook | Você clicou duas vezes em pagar. Por que cobrou só uma? (entrega `hook`) | título na tela |
| `cenario` | flow | A resposta se perdeu na volta, e o app mandou o pedido de novo. | app, API e cobranças; a resposta volta tracejada e se perde |
| `sem-chave` | flow | Sem marca, o servidor trata o segundo pedido como um pagamento novo. | o pedido de novo cria outra cobrança |
| `medicao-sem` | number | Simulei dez mil pagamentos com três em cada dez respostas perdidas: sobraram mais de quatro mil cobranças repetidas. | 0 → 4.194 repetidas |
| `chave` | flow | A solução é uma chave por pagamento: com a mesma chave, o servidor devolve o resultado guardado. | a API consulta a chave antes de cobrar; o resultado guardado volta ao app |
| `codigo` | code | Antes de cobrar, o código procura a chave. Se ela já existe, devolve o resultado guardado. | três passos: procura, devolve ou cobra e guarda |
| `comparacao` | versus | Com a chave, as catorze mil tentativas viraram dez mil cobranças, e nenhuma repetida. | sem chave × com chave (14.194 e 10.000 cobranças) |
| `custo` | categories | A chave tem preço: guardar e consultar. Em memória, cada pedido levou mais que o dobro do tempo. | 0,52 µs × 1,58 µs por pedido, só em memória |
| `fecho` | end_card | Por quanto tempo você guardaria essa chave? (entrega `invite`) | pergunta de decisão, sem resposta do vídeo |

Duração total prevista pelo `tempos`: 45,0 s (alvo da pauta: 35 a 45 s).

## 3. Sequência de impacto no System Design (decisão, benefício e limite)

1. **Decisão:** cada pagamento recebe uma chave. O servidor guarda o resultado da primeira execução e o devolve nas
   repetições (cenas `chave` e `codigo`).
2. **Benefício medido:** na simulação, o número de cobranças repetidas cai de 4.194 para 0 (cenas `medicao-sem` e
   `comparacao`), com as mesmas 14.194 tentativas.
3. **Limite medido:** cada pedido ficou mais que o dobro do tempo com a checagem, só em memória (cena `custo`).
   Guardar as chaves ocupa espaço (10.000 entradas no programa).
4. **Limite de projeto, sem medição:** por quanto tempo guardar a chave. A pergunta do fecho deixa isso aberto.

## 4. Quadro de controle obrigatório (direção editorial)

| Item | Antes da voz/render | Depois do render |
| --- | --- | --- |
| Aplicação | API de pagamentos; resposta perdida; retry do cliente (cenas `cenario`, `sem-chave`, `chave`) | a ser conferido no quadro de leitura |
| Decisão de System Design | chave por pagamento e resultado guardado; pergunta e decisão explícitas (`chave`, fecho) | a ser conferido |
| Benefício e limite | repetidas 4.194 → 0; tempo por pedido 0,52 → 1,58 µs, medido em memória (`medicao.json`, 15 rodadas) | a ser conferido; o limite de banco e rede **não** foi medido |
| Explicação visual | fluxos com estados e tokens; código com passos; comparação e categorias com os números da medição | a ser conferido nos quadros de início, leitura e fim |

**Lacuna declarada:** o custo foi medido só em memória. Em banco com rede, o número muda, e a narração diz isso
("Em memória"). Não há medição de banco nem de rede neste vídeo.

## 5. Música (planejada; mistura pendente)

- **Faixa:** `ytal-spirit-of-fire` ("Spirit of Fire", do catálogo `data/music/catalog.json`; calma, intensidade 3,
  sem vocal, 608 s, dura mais que o vídeo). Licença: YouTube Audio Library, válida só no YouTube.
- **Plano:**
  - 0,0 a 12,6 s (`gancho`, `cenario`, `sem-chave`): fundo baixo desde o primeiro quadro.
  - 12,6 a 20,1 s (`medicao-sem`): sem música, para o número medido aparecer limpo.
  - 20,1 a 36,8 s (`chave`, `codigo`, `comparacao`): fundo baixo, sem competir com a leitura dos blocos.
  - 36,8 a 42,4 s (`custo`): sem música, resultado medido.
  - 42,4 a 45,0 s (`fecho`): fundo baixo volta, saindo no último quadro.
- **Mistura:** `vp short juntar` ainda não mistura música (lacuna da skill). Fica registrado como
  `música planejada, mistura pendente`. Não declarar o vídeo "com música" antes da mistura.

## 6. Pendências antes do gate 4

1. Revisar os quadros de início, leitura e fim de cada cena (`review_video` do kit) contra os três defeitos: animação
   cortada, janela sobre o conteúdo e texto sobre o rodapé.
2. Conferir o controle obrigatório depois do render (tabela 4).
3. Montar a mistura de voz (`vp short juntar`) e a música (lacuna acima).
4. Gerar o pacote do gate 4 (`vp short gate`) e rodar a dúvida cega antes de qualquer agendamento. Sem sua
   autorização para o agendamento, nada é publicado.
5. Confirmar o ângulo A (ou trocar a atribuição do bloco) antes de agendar qualquer publicação do bloco.
