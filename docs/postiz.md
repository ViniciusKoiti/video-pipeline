# Postiz: comandos para ferramentas e agentes

Use `.venv/bin/vp postiz` dentro do workspace, inclusive em subpastas. A raiz é localizada pela configuração
do projeto. A camada usa a API pública da instalação configurada, sem depender do login da CLI global do
Postiz nem instalar serviços ou dependências.

## Configuração

Defina `POSTIZ_API_KEY` e `POSTIZ_API_URL` no `.env` local. Para esta instalação, a URL do backend é
`https://postizis.duckdns.org/api`. Variáveis já exportadas no ambiente têm precedência sobre o arquivo.
A chave fica em `SecretStr`; mensagens de erro não incluem cabeçalhos nem o corpo de erros do servidor.
O `.env` não deve entrar no Git. Há campos vazios em [.env.example](../.env.example).

## Comandos

| Comando | Resultado |
|---|---|
| `vp postiz integrations` | Canais conectados: IDs, nomes, provedor, perfil e estado de desativação |
| `vp postiz connect instagram-standalone` | Link de autorização para o dono conectar o Instagram |
| `vp postiz settings ID` | Regras e campos aceitos pelo canal |
| `vp postiz posts --start ISO --end ISO` | Posts na janela, com ID, legenda, horário, estado e canal |
| `vp postiz upload VIDEO.mp4` | ID e caminho da mídia enviada; registra o arquivo e o `sha256` |
| `vp postiz pacote post.json [--episode ID]` | Pacote de decisão para o dono, sem criar nada; confere se os links da legenda abrem (HTTP 404/410 bloqueia, sem resposta ou outro erro vira risco) |
| `vp postiz duvida post.json parecer.json` | Grava o parecer da dúvida cega sobre o último pacote |
| `vp postiz schedule post.json` | IDs das postagens criadas; só com pacote, parecer "segue" e a confirmação do dono |

Sucesso escreve JSON na saída padrão. Falhas de execução escrevem JSON em stderr e saem com código 1;
argumentos inválidos seguem o argparse, com código 2. `--help` funciona sem credenciais.

Os comandos de consulta não agendam. `connect` gera o link; o dono precisa fazer login e autorizar o
Instagram. Confira novamente `integrations` para obter o ID do perfil conectado. Não use o ID do canal
YouTube para publicar no Instagram, mesmo que tenham o mesmo nome.

## Agendar um Reel

Depois de revisar o vídeo e a legenda com o dono:

1. Consulte `integrations` e `settings ID` para conferir o canal.
2. Envie o vídeo com `upload` e use o `id` e o `path` retornados.
3. Salve um JSON no formato nativo do Postiz, como este exemplo, substituindo os três valores de mídia/canal
   e escolhendo uma data futura. O exemplo usa 15/10/2026, às 12h30 de Brasília:

```json
{
  "type": "schedule",
  "date": "2026-10-15T12:30:00-03:00",
  "shortLink": false,
  "tags": [],
  "posts": [{
    "integration": {"id": "ID_DO_INSTAGRAM"},
    "value": [{
      "content": "Trecho de A Planilha é Tua — Nabote.\nMúsica gerada com IA (Suno).",
      "image": [{"id": "ID_DA_MIDIA", "path": "URL_DA_MIDIA"}]
    }],
    "settings": {"__type": "instagram-standalone", "post_type": "post"}
  }]
}
```

4. Rode `.venv/bin/vp postiz pacote post.json` (com `--episode ID` quando o vídeo for de um episódio, para
   conferir o gate 4) e mostre ao dono o pacote: o quê, evidência, riscos, como desfazer e recomendação.
5. Peça a dúvida cega ao agente `duvida-cega`, passando só o caminho do `post.json` (sem resumo nem opinião).
   Salve o JSON que ele devolve em `parecer.json` e grave com `.venv/bin/vp postiz duvida post.json parecer.json`.
   Mostre o parecer ao dono junto com o pacote.
6. Com o "pode" do dono, execute `.venv/bin/vp postiz schedule post.json`. O Claude Code pede a confirmação dele
   antes de rodar (regra `ask` do `.claude/settings.json`). O comando recusa sem pacote para o mesmo JSON, sem
   parecer depois desse pacote ou com parecer "não segue".
7. Consulte `posts --start ... --end ...` e confira os IDs e o estado `QUEUE`. A resposta de criação sozinha
   não comprova que o conteúdo foi publicado.

A camada rejeita datas sem fuso ou no passado, canais ausentes/desativados e tentativas de atualizar posts
existentes. Antes de criar, consulta a janela para detectar o mesmo canal, horário e texto visível da legenda,
normalizando HTML e espaços. O Postiz
não fornece idempotência documentada para essa operação: chamadas concorrentes ainda podem duplicar posts.
Não há repetição automática de POST. Em caso de timeout, consulte a fila antes de tentar novamente.

Cada `upload`, `pacote`, parecer, `schedule` criado e falha de envio vira uma linha em `data/publicacoes/registro.jsonl`,
que só cresce e entra no Git. É ali que ficam os ids das postagens, em vez de copiá-los à mão.

A autorização para publicar continua sendo do dono ([ADR 025](decisions/025-agendamento-pelo-postiz.md)). A camada não aprova gates editoriais nem altera
`review.json`. [Agenda do Nabote](../renders/clipe/agenda-instagram.md).

Contratos oficiais: [API pública](https://docs.postiz.com/public-api/introduction),
[criar posts](https://docs.postiz.com/public-api/posts/create),
[Instagram Standalone](https://docs.postiz.com/public-api/providers/instagram-standalone).

## Depois de publicar

O Postiz não faz estes passos; o `pacote` os lembra entre os riscos:

1. Conferir no YouTube Studio se o vídeo saiu (`ERROR` no Postiz não prova que falhou; não reenvie antes).
2. Fixar o primeiro comentário, à mão.
3. Marcar "conteúdo alterado ou sintético" quando houver voz clonada ou imagem gerada.
4. Registrar a URL e, aos 7 e 28 dias, as leituras no `metrics.json` do episódio.
