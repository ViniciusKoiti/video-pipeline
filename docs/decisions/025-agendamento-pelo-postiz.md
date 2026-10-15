# 025 — Agendamento das postagens pelo Postiz, com autorização do dono

- **Status:** aceito pelo dono em 2026-10-15 ("atualize o §2.8 do CLAUDE.md nesse PR", na sessão em que a
  integração foi revisada e enviada no PR #142)
- **Data:** 2026-10-15
- **Etapa do roadmap:** publicação, depois do gate 4
- **Relaciona-se com:** CLAUDE.md §2.5 (gates humanos) e §2.8 (escopo do MVP; emendado aqui), §2.7 (segredos),
  §2.10 (testes sem rede)

## Contexto

O §2.8 deixava o upload automático fora do MVP, e o §1 dizia que a publicação era sempre manual. Os cortes do
clipe "A Planilha é Tua" (Nabote) já têm agenda no Instagram, confirmada pelo dono em 2026-10-14: cinco Reels,
de 15 a 19/10/2026, às 12h30 de Brasília (`renders/clipe/agenda-instagram.md`). Postar um por dia à mão, no
horário, depende de o dono estar no celular naquela hora.

O dono já usa uma instalação própria do Postiz, que agenda e publica nas redes conectadas a ela; o Nabote estava
conectado só ao YouTube em 2026-10-14. O Postiz tem uma API pública com chave por instalação.

## Decisão

1. **O `vp postiz` é a única exceção ao "upload automático" do §2.8.** Ele consulta canais e posts, gera o link
   de conexão de um canal, envia mídia e cria agendamentos no Postiz do dono (`app/providers/postiz.py`,
   `app/commands/postiz.py`; uso em `docs/postiz.md`). A publicação em si é feita pelo Postiz, no horário marcado.
2. **Só depois do gate 4 e com autorização do dono para aquele agendamento.** O comando não aprova gate, não
   altera `review.json` e não escolhe data sozinho; agente nenhum roda `schedule` sem o pedido do dono na sessão.
3. **A conexão das redes usa o login do dono.** O `connect` só devolve o link de autorização; quem entra na
   conta é o dono.
4. **Credencial só no `.env`** (`POSTIZ_API_KEY`, `POSTIZ_API_URL`), como `SecretStr`. Erros não mostram a chave,
   cabeçalhos nem o corpo da resposta do servidor. A URL precisa ser HTTPS.
5. **Defesas contra agendamento errado:** data com fuso e no futuro, canal existente e ativo, nada de atualizar
   post existente, e recusa de post igual (canal, horário e texto visível da legenda) já na fila. O POST não é
   repetido sozinho; em timeout, consulta-se a fila antes de tentar de novo.
6. **Sem dependência nova:** o cliente usa só a biblioteca padrão e o transporte HTTP do projeto. Os testes
   mockam o transporte e não acessam a rede.

## Consequências

- O §1, o §2.8 e o §4 do CLAUDE.md passam a citar o agendamento autorizado pelo `vp postiz`; o resto do §2.8
  continua valendo (nada de Docker, banco, API web, render em nuvem).
- O Postiz não documenta idempotência na criação de posts: duas chamadas ao mesmo tempo ainda podem duplicar um
  agendamento. Com um só operador por vez, a consulta prévia à fila basta; com vários, seria preciso outra
  proteção.
- A resposta da criação não prova a publicação: conferir o estado `QUEUE` com `vp postiz posts` e, depois do
  horário, o post na rede.
- Mudar a instalação do Postiz é trocar as duas variáveis do `.env`; o código não guarda endereço nem conta.
