# Tarefa: conectar o Instagram ao Postiz (instalação própria)

Você é um agente encarregado de conectar uma conta do Instagram ao Postiz instalado pelo dono em
`https://postizis.duckdns.org`. Faça tudo o que puder sozinho e **chame o dono só nos pontos marcados com 🛑**.
Quando chamar, diga em uma ou duas frases o que precisa e o que ele deve fazer; depois continue de onde parou.

## Objetivo

Ao final, o canal **Instagram (Standalone)** aparece em Postiz › canais conectados, ativo, e o comando
`postiz integrations:list` (com a chave da API pública do Postiz) lista uma integração com
`"identifier": "instagram-standalone"`.

**Não publique nada**, nem post de teste. A publicação é sempre feita depois da revisão humana.

## Contexto

- Postiz instalado pelo dono. Frontend: `https://postizis.duckdns.org`. Backend: `https://postizis.duckdns.org/api`.
- Caminho escolhido: **Instagram Standalone** (login direto pelo Instagram, sem página do Facebook).
  Documentação oficial: https://docs.postiz.com/providers/instagram (confira nela se algo abaixo divergir; em
  conflito, vale a documentação e você avisa o dono no relatório).
- A conta precisa ser **profissional** no Instagram (Business; Criador provavelmente também serve, confira).
- O app da Meta fica em **modo de desenvolvimento**: basta a conta do dono ter função de testadora. Não é preciso
  pedir análise do app nem verificar a empresa.

## Passos

### 1. Conta profissional no Instagram

- Verifique se a conta do Instagram que o dono quer usar já é profissional.
- 🛑 Se não for, pergunte ao dono qual conta usar e peça que ele faça a troca no app (Configurações › Tipo de conta
  e ferramentas › Mudar para conta profissional). Trocar o tipo de conta é decisão dele; não troque por conta
  própria.

### 2. App na Meta

- Abra https://developers.facebook.com/apps.
- 🛑 Se for preciso fazer login, fazer verificação em duas etapas ou criar a conta de desenvolvedor, chame o dono.
  Nunca peça a senha dele no chat.
- Crie um app novo:
  - Tipo **"Outro"** (Other).
  - Se o assistente de criação mostrar casos de uso em vez de tipos, escolha o de gerenciar mensagens e conteúdo
    no Instagram.
  - Nome sugerido: `Postiz Nabote`.
- 🛑 Se a Meta pedir um portfólio de negócios (Business portfolio) e houver mais de um, ou nenhum, pergunte ao
  dono qual usar ou se pode criar.
- No app, adicione o produto **Instagram** › **API com login do Instagram / Instagram Business Login**.
- Em URLs de redirecionamento OAuth válidas (configurações do Business Login), coloque exatamente:
  `https://postizis.duckdns.org/integrations/social/instagram-standalone`
- Se a tela pedir permissões, garanta as de publicação de conteúdo:
  - `instagram_business_basic`
  - `instagram_business_content_publish`
  - `instagram_business_manage_comments` e `instagram_business_manage_insights`, se aparecerem.
- Em Funções do app › Funções › **Testadores do Instagram**, adicione o @ da conta do dono.
- 🛑 Peça ao dono para aceitar o convite no Instagram (Configurações › Apps e sites › Convites de testador). Espere
  a confirmação antes de seguir.
- Anote o **Instagram App ID** e o **Instagram App Secret** da tela de configuração da API do Instagram. São os da
  seção do Instagram, não o App ID do Facebook do topo da página.

### 3. Variáveis no servidor do Postiz

- 🛑 Pergunte ao dono como acessar o servidor onde o Postiz roda (SSH, painel, onde fica o `docker-compose.yml`),
  se você ainda não tiver esse acesso.
- Encontre onde a instalação define as variáveis. Procure onde já estão `MAIN_URL`, `FRONTEND_URL` ou
  `NEXT_PUBLIC_BACKEND_URL`; costuma ser o bloco `environment:` do `docker-compose.yml` ou um `.env` ao lado dele.
- Faça uma cópia do arquivo antes de editar (ex.: `docker-compose.yml.bak-AAAA-MM-DD`).
- Acrescente, no mesmo formato das variáveis que já estão lá:
  ```
  INSTAGRAM_APP_ID="<Instagram App ID>"
  INSTAGRAM_APP_SECRET="<Instagram App Secret>"
  ```
- Não altere nenhuma outra variável.
- 🛑 Antes de reiniciar o Postiz, avise o dono, porque o serviço fica fora do ar por alguns instantes. Depois
  reinicie (com Docker: `docker compose up -d` na pasta do compose) e confirme que o site volta a abrir.

### 4. Conectar o canal

- No Postiz (`https://postizis.duckdns.org`): **Add Channel** › **Instagram (Standalone)**.
- 🛑 O login e a autorização no Instagram são do dono: chame-o para entrar e clicar em "Permitir".
- Confirme que o canal aparece conectado e sem aviso de erro.

## Regras

- **Segredos:**
  - O App Secret e a chave da API do Postiz nunca vão para o chat, para logs, para commits nem para o repositório
    `auto-play`.
  - Só vão para o arquivo de configuração do servidor do Postiz.
  - No relatório, escreva "configurado" em vez do valor.
- **Coisas que você não faz:**
  - Não publique, não agende e não apague posts.
  - Não desconecte canais existentes: LinkedIn e três canais do YouTube, entre eles o Nabote Songs.
- Não mude configurações da conta do Instagram, do Facebook ou do Postiz além do descrito aqui.
- Não aceite pagamento, plano pago, verificação de empresa nem envio do app para análise. Se a Meta exigir algum
  desses para seguir, pare e 🛑 chame o dono.
- Se um passo falhar duas vezes do mesmo jeito, pare e 🛑 chame o dono com a mensagem de erro exata.

## Erros conhecidos

| Sintoma | Causa provável | O que fazer |
|---|---|---|
| "Insufficient developer role" | A conta não é testadora ou não aceitou o convite | Passo 2, testadores; 🛑 dono aceita o convite |
| Erro de redirect URI no login | URL diferente da cadastrada | Conferir caractere por caractere, com `https` e sem barra final |
| "Instagram (Standalone)" não aparece em Add Channel | Variáveis não carregadas ou versão antiga do Postiz | Conferir o arquivo e reiniciar; 🛑 se a versão não tiver o provedor, avisar o dono antes de atualizar |
| Conecta, mas publicar dá erro de permissão | Permissão de publicação ausente | Conferir `instagram_business_content_publish` no app |

## Relatório final

Responda ao dono com:

1. O canal conectado: nome e @ que aparecem no Postiz.
2. O nome e o ID do app criado na Meta (o ID não é segredo; o App Secret é).
3. O arquivo do servidor que foi editado e onde ficou a cópia de segurança.
4. Qualquer divergência entre este roteiro e a documentação ou as telas atuais da Meta.
5. O que ficou pendente, se ficou algo.
