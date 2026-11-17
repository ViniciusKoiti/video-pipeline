# Termos de uso dos logos de Amazon, Discord e Akamai (consulta de 2026-11-08)

**Para quê:** o dono pediu os logos das três empresas na miniatura dos Reels de consistent hashing e escolheu "logo
oficial do kit de imprensa" (2026-11-08). Antes de baixar qualquer arquivo, os termos oficiais foram lidos. **Conclusão:
nenhum deles cobre, como lido, o uso do logo na capa de um vídeo sobre a empresa; nenhum logo foi baixado.**
Páginas salvas só no scratchpad da sessão; aspas abaixo copiadas do texto extraído delas.

## Amazon: Associates Central, "Trademark Guidelines"

https://affiliate-program.amazon.com/help/operating/amazonmarks/ (lida em 2026-11-08)

- Escopo: "apply to your use of our and our affiliates' trademarks and logos that we may make available to you from
  time to time, including as part of any content you obtain from us". "You will not use any Amazon Mark in any other
  place, for any other purpose, or in any other manner." "any use of an Amazon Mark in violation of these Guidelines
  will automatically terminate any license related to your use of the Amazon Marks."
- Forma: "You may display an Amazon Mark only in the exact format in which we provide it to you." "Each Amazon Mark must
  appear by itself, with reasonable spacing between each side of the Amazon Mark and other visual, graphic or textual
  elements." (uma miniatura com palavra e personagem ao lado não cumpre isto.)
- Proibido: uso "that implies sponsorship or endorsement by us" e "other than as specifically authorized under the
  Agreements".
- Único logo liberado sem revisão a "Influencers or Publishers": "available at Amazon", "to promote the availability of
  products and services at Amazon". É o do bloco de livros do `description.txt`; não serve a um vídeo sobre o Dynamo.
- Anúncios de terceiros que apontam para a Amazon (https://advertising.amazon.com/resources/ad-policy/brand-usage): "The
  Amazon and Smile logos are not permitted in third-party advertising by vendors and sellers linking in to Amazon." e
  "Other uses of the Amazon brand require review and written approval by Amazon".

## Discord: Brand Assets e "Legal Brand Guidelines"

https://discord.com/branding (lida em 2026-11-08; kit em "View Brand Kit")

- "You must have permission from Discord before using any of the Discord Marks or Brand Assets except as permitted
  here."
- Permitido: "Use the Discord Marks to inform people that you are a Discord user and/or that you have a Discord server",
  sem "imply that you are Discord, or somehow sponsored by or acting on behalf of Discord"; e "only on digital assets".
- "Feel free to use our logo in color, black or white." mas "Please do not edit, change, distort, recolor, or
  reconfigure the Discord logo." O símbolo só "when the Discord brand is clearly visible or has been well established
  elsewhere."
- Não há, no texto lido, exceção para uso editorial ou para falar sobre a empresa. Um vídeo que explica o post de
  engenharia do Discord não é "informar que você é usuário do Discord".

## Akamai: **não lido**

- `akamai.com/site/es/documents/akamai/akamai-brand-guide-for-third-party-use.pdf` e
  `akamai.com/us/en/about/news/media-resources.jsp` devolveram **HTTP 403** ao `curl`. Não contornei o bloqueio.
- Só há o resumo de uma busca (não é fonte): o guia de terceiros mandaria perguntas e pedidos de permissão a
  `brand@akamai.com`, com um formulário de permissão. Falta o texto oficial para dizer se o uso é permitido.

## O que isto significa para o projeto

- Logo não cabe na lista fechada de licenças da ADR 007; `Citacao` é para obra citada em crítica, não para marca.
- Pelos termos acima, usar os três logos exige **permissão por escrito** de cada empresa (Amazon e Discord dizem isso
  literalmente; Akamai falta ler). Nada foi registrado como ativo `approved`.
- O nome da empresa em texto (fonte do canal) não é o logo e não depende de arquivo de terceiros. Dizer "Amazon" na
  fala e no rodapé já é o que o roteiro faz.

## Decisão do dono (2026-11-08)

Depois de ver o resultado acima, o dono respondeu: "Pode usar sem permissão mesmo, não é problemático". Os logos da
Amazon (Media Center) e do Discord (kit oficial) foram baixados e entraram **sem alteração** nas capas dos Reels e do
Short de consistent hashing, registrados em `renders/short-consistent-hashing-java/miniaturas/logos.json` com
`license: logo-oficial-sem-permissao` e `review_status: needs_review`. O risco é do dono: uma reclamação de marca pode
derrubar a capa ou gerar strike (CLAUDE.md §6, nota do `Citacao`). Não é emenda à ADR 007: a lista fechada continua como
está, e este uso fica como exceção registrada por vídeo. Falta o logo da Akamai (acesso bloqueado, ver acima).
Pendente em `descricao`/comentário fixado: "Amazon e o logotipo Amazon são marcas registradas da Amazon.com, Inc. ou de
suas afiliadas" (exigência do texto da Amazon) e o equivalente para Discord e Akamai.

## Akamai: página de mídia lida em 2026-11-08 (atualiza a seção "não lido")

https://www.akamai.com/newsroom/media-resources foi aberta pelo leitor de páginas da sessão (HTTP 200); o `curl` segue levando 403, então os trechos
abaixo vêm do relatório do leitor (cada citação limitada a 125 caracteres) e **não foram conferidos no navegador**:
- "The logo consists of two basic elements: the blue wavelike symbol and the word "Akamai" (known as the wordmark)."
- Proporção e arranjo do símbolo e da palavra "should be used exactly as provided."; "The wordmark should never appear without the wave symbol."
- "This is a legally protected trademark of Akamai Technologies, Inc."
- Terceiros não-imprensa (fornecedor, cliente, parceiro) que peçam permissão: "please follow the Brand Permission Request process."
- Arquivos: o link "Download logo" aponta para `.../2025/akamai-logos.zip` (4 SVGs: azul, preto, e as versões com fundo); o guia de marca em PDF
  (`akamai-brand-guidelines.pdf`) **não foi aberto**, então regras de cor, espaço e tamanho mínimo seguem sem leitura.
- Como o uso aqui é sem permissão, vale o mesmo registro da seção "Decisão do dono": risco do dono, sem sugerir patrocínio.
Capa do Reel 3 refeita com o logo oficial; a provisória em texto ficou em `miniaturas/provisorias/`.
