# Termos dos bancos de imagem: Pexels, Pixabay, Unsplash, Coverr (consulta de 2026-09-26)

Registro do §7 do CLAUDE.md para a abertura v2 da Votorantim (#48): licença, atribuição, proibições e regras
de API de cada fonte, lidas nas páginas oficiais em **2026-09-26**. Leitura feita por agentes de leitura de
página (WebFetch). As seis frases que mais pesam na decisão foram conferidas numa segunda leitura (marcadas
com ✔). Citações no original. Não é parecer jurídico. O teste com a conta real (§7) fica para quando as
chaves estiverem no `.env`.

Limites da leitura:

- Pexels: o FAQ da API (help.pexels.com) respondeu 403; `/api/documentation/` foi lida literalmente até
  "Search for Videos" (39 de 73 mil caracteres). O resto veio resumido e não é usado aqui.
- Unsplash: `/documentation` e `/spec/v1.json` lidos literalmente só no começo.
- Coverr: `/pricing` lida só em parte.

## Resumo

| | Pexels | Pixabay | Unsplash | Coverr |
|---|---|---|---|---|
| Licença | Pexels License (parte do acervo em CC0) | Content License (CC0 se publicado antes de 09/01/2019) | Unsplash License | licença própria, sem nome |
| Na lista da ADR 007 | sim (`Pexels`) | não | não | não |
| Uso comercial e modificação | sim | sim | sim | sim |
| Crédito pela licença | apreciado | apreciado | apreciado | apreciado |
| Crédito pela API | link para a Pexels; fotógrafo "when possible" | mostrar a origem ao exibir resultados | obrigatório a cada exibição, com links | logo clicável da Coverr |
| Vídeo pela API | sim | sim | não encontrado (só foto e ilustração) | sim |
| Limite | 200/h e 20 mil/mês | 100 por 60 s | 50/h (demo); 1.000/h com aprovação | 50/h (demo); produção só com plano pago |
| Headers de cota | `X-Ratelimit-Limit/Remaining/Reset` (só em 2xx) | `X-RateLimit-Limit/Remaining/Reset` | `X-Ratelimit-Limit/Remaining` | não encontrado |
| Cache | não encontrado | obrigatório, 24 h | não encontrado | não encontrado |
| Hotlink | não encontrado | imagem: proibido o permanente, baixar; vídeo: pode embutir | obrigatório no app, com exceção para obra derivada | previsto (URL assinada ligada à chave) |
| Registrar o download | não encontrado | não | obrigatório (`download_location`) | obrigatório (ping do `mp4_download`) |
| Termos atualizados em | 15/11/2024 | 18/11/2024 | sem data | 04/04/2023 |

## Regras comuns que afetam a busca

- **Pessoa reconhecível.** Todas deixam os direitos de imagem com o usuário. Pexels e Pixabay proíbem uso
  "immoral or illegal", "especially Content which features a recognisable person", e dão como exemplo de uso
  ofensivo retratar alguém "as suffering from, or medicating for, a physical or mental ailment" ✔ e uso "in a
  political context". Consequência para o gancho: o plano de farmácia ou remédio não pode mostrar pessoa
  reconhecível doente ou tomando remédio; nenhuma pessoa de banco de imagem nos trechos sobre Estado e política.
- **Marca e logo.** Todas excluem da licença as marcas que aparecem na imagem. Pexels e Pixabay proíbem uso
  comercial "in relation to goods and services" de conteúdo com marca; o FAQ do Pixabay sugere remover logos.
  O critério da sessão (nenhuma marca, logo ou texto visível) cobre isso.
- **Endosso e engano.** Pexels e Pixabay proíbem sugerir que pessoa ou marca retratada endossa o usuário e
  dar a impressão de que o conteúdo foi criado por ele. A nossa regra de sempre tratar o banco como
  ilustração (§2.4) e dar crédito cobre isso.
- **Reclamação de direitos.** Pexels e Pixabay: "you have to stop using the Content immediately, at your own
  expense" e apagar o conteúdo. Guardar `page_url`, `retrieved_at` e `sha256` permite achar e trocar o plano.
- **Áudio do vídeo.** Os ToS de Pexels e Pixabay listam "audio or video samples" entre os possíveis direitos
  de terceiros. O template já toca o B-roll sem som (`OffthreadVideo muted` em `video/src/ShotView.tsx`).
- **Uso em massa.** Pexels e Pixabay proíbem "bulk, large-scale or systematic copying". A busca do pipeline
  (poucas consultas por plano, até 2 candidatos) fica muito abaixo disso.

## Pexels

Páginas: [licença](https://www.pexels.com/license/) (sem data),
[termos](https://www.pexels.com/terms-of-service/) ("Last updated: November 15th, 2024"),
[API](https://www.pexels.com/api/) (sem data), [documentação da API](https://www.pexels.com/api/documentation/)
(sem data). Não há página separada de "API terms" linkada.

- **Licença.** "Attribution is not required. Giving credit to the photographer or Pexels is not necessary but
  always appreciated." Parte do acervo está em CC0, indicado na página da foto. Uso em vídeo: combinar com
  outras mídias "is not Standalone use, so long as the combined effect is to make a "new" creative work". A
  página de licença cita o YouTube como exemplo de uso.
- **Proibições (além das comuns).** "Don't sell unaltered copies"; "Don't redistribute or sell the photos and
  videos on other stock photo or wallpaper platforms"; uso como marca registrada; "You may not copy or
  replicate core functionality of Pexels".
- **API.** Chave gratuita no header `Authorization`. "By default, the API is rate-limited to 200 requests per
  hour and 20,000 requests per month." Headers `X-Ratelimit-Limit`, `X-Ratelimit-Remaining` e
  `X-Ratelimit-Reset` (timestamp UNIX da virada do mês), "only returned on successful (2xx) responses".
  Crédito: "show a prominent link to Pexels" ("Photos provided by Pexels") e "Always credit our photographers
  when possible (e.g. "Photo by John Doe on Pexels" with a link to the photo page on Pexels)". Cache, hotlink e
  registro de download: não encontrados.
- **Vídeo.** `GET https://api.pexels.com/v1/videos/search` com `query`, `orientation`, `size` (`large` 4K,
  `medium` Full HD, `small` HD), `locale` e `per_page` (máx. 80). Campos: `width`, `height`, `duration`
  (segundos), `url`, `image`, `user {name, url}` e `video_files[] {quality, file_type, width, height, fps,
  link}`. O exemplo da documentação traz um arquivo `"quality": "hls"` com `width`/`height` nulos (`.m3u8`):
  filtrar.

## Pixabay

Páginas: [resumo da licença](https://pixabay.com/service/license-summary/) (sem data),
[termos](https://pixabay.com/service/terms/) ("Last updated: November 18, 2024"),
[API](https://pixabay.com/api/docs/) (sem data), [FAQ](https://pixabay.com/service/faq/) (sem data).

- **Licença.** "Content License"; conteúdo com "Published date" anterior a 9/1/2019 é CC0. Só o texto
  completo, nos termos, vale: "only the full Content License is legally binding". Crédito: "You do not need to
  credit Pixabay or the contributor of Content when you use it"; formato sugerido "by [Contributor] via
  Pixabay". O FAQ dá "Adding the photo to a video montage" como exemplo de alteração.
- **Proibições (além das comuns).** Venda ou distribuição "on a Standalone basis" (filtro, cor, recorte e
  redimensionamento continuam sendo Standalone); uso como marca registrada; "data mining, extraction, scraping
  (...) including without limitation for machine learning purposes". Sobre pessoa reconhecível, o FAQ diz: "It
  is best to contact the artist and inquire about a model release if a person is recognisable."
- **API.** Chave obrigatória (parâmetro `key`). "By default, you can make up to 100 requests per 60 seconds";
  acima disso, HTTP 429. Headers `X-RateLimit-Limit`, `X-RateLimit-Remaining` e `X-RateLimit-Reset`.
  "Requests must be cached for 24 hours." "Permanent hotlinking of images (using Pixabay URLs in your app) is
  not allowed. If you intend to use the images, please download them to your server first." "Videos may be
  embedded directly in your applications. Yet, we recommend storing them on your server." "Show your users
  where the images and videos are from, whenever search results are displayed." "The API is made for real
  human requests; do not send lots of automated queries." "Systematic mass downloads are not allowed." A
  página institucional (`/service/about/api/`) fala em "Unlimited requests", o que contradiz a documentação.
  Seguimos a documentação.
- **Foto.** Sem aprovação para "full API access", a maior imagem é `largeImageURL`, "Scaled image with a
  maximum width/height of 1280px" ✔. `fullHDURL` (até 1920 px) e `imageURL` (original) exigem essa aprovação ✔.
  Uma foto do Pixabay chega ao vídeo 1920×1080 ampliada.
- **Vídeo.** `GET https://pixabay.com/api/videos/`. Tamanhos: `large` "usually has a dimension of 3840x2160"
  (pode vir vazio); `medium` "usually has a dimension of 1920x1080, older videos have a dimension of 1280x720"
  e "is available for all Pixabay videos". Campos por tamanho: `url`, `width`, `height`, `size` e `thumbnail`.
  `duration` aparece no exemplo, mas a unidade não está documentada. Conferir `width`/`height` reais.

## Unsplash

Páginas: [licença](https://unsplash.com/license), [termos](https://unsplash.com/terms) e
[termos da API](https://unsplash.com/api-terms) (todos sem data);
[diretrizes da API](https://help.unsplash.com/en/articles/2511245-unsplash-api-guidelines) e artigos de
[hotlink](https://help.unsplash.com/en/articles/2511271-guideline-hotlinking-images),
[download](https://help.unsplash.com/en/articles/2511258-guideline-triggering-a-download),
[crédito](https://help.unsplash.com/en/articles/2511315-guideline-attribution) e
[limite](https://help.unsplash.com/en/articles/3887917-when-should-i-apply-for-a-higher-rate-limit)
("Written by Unsplash Dev — July 27, 2026"); [documentação](https://unsplash.com/documentation) (último
changelog de 7/1/2025); [licença Unsplash+](https://unsplash.com/plus/license).

- **Licença.** Uso comercial e modificação sem pedir permissão, "(though attribution is appreciated!)".
  "Images cannot be sold without significant modification." A licença não fala de vídeo; a concessão é genérica
  ("download, copy, modify, distribute, perform, and use"). Os termos (seção 5) dizem que a licença não inclui
  "Trademarks, logos, or brands that appear in Images", "People's images if they are recognizable in the
  Images" e "Works of art or authorship that appear in Images".
- **Unsplash+.** Tem licença própria e paga. Os termos da API dizem que "all Images that are made available
  through the APIs are provided pursuant to the Unsplash License". Nenhum campo para filtrar Unsplash+ foi
  encontrado. Desde 7/1/2025 a API devolve ilustrações junto com as fotos.
- **API: obrigações escritas para apps que exibem imagens.**
  - Crédito: "Notwithstanding anything in Unsplash License and Unsplash Terms & Conditions to the contrary",
    "each time you or your Developer App displays an Image, your Developer App must attribute Unsplash, the
    Unsplash photographer" com link para o perfil e `utm_source`/`utm_medium=referral`.
  - Hotlink: "you must directly use or embed the related image URLs returned by the API in your Developer Apps".
    O descumprimento é "a material breach". Exceção nas diretrizes: "If the image is remixed to create a
    derivative creative image, these results do not need to be hotlinked" ✔.
  - Download: "each time there is a download of an Image or other comparable event", chamar
    `photo.links.download_location` com a chave.
  - Uso: "The API is to be used for non-automated, high-quality, and authentic experiences". Evitar
    "displaying advertising near to the API content".
  - Limite: 50/h em demo, modo para "small personal projects that aren't intended for the public"; 1.000/h
    depois de aprovação para produção. Headers `X-Ratelimit-Limit` e `X-Ratelimit-Remaining`. Arquivos em
    `images.unsplash.com` não contam.
  - Termos: proibido usar as imagens em "machine learning and/or artificial intelligence datasets" e acessar o
    site com "bots, spiders, scripts, crawlers, scrapers".
- **Vídeo.** Nenhum endpoint encontrado.
- **O que as páginas não dizem.** Se "displays an Image" alcança uma imagem editada num vídeo publicado fora
  do app; se a exceção de obra derivada cobre essa edição; se "advertising near to the API content" alcança um
  vídeo monetizado.

## Coverr

Páginas: [licença](https://coverr.co/license) (sem data), [termos](https://coverr.co/terms)
("Last updated: Apr. 4th, 2023"), [desenvolvedores](https://coverr.co/developers),
[documentação da API](https://api.coverr.co/docs) e subpáginas `/start/`, `/auth/`, `/videos/` e `/schema/`
(todas sem data).

- **Licença.** "Coverr.co grants you an irrevocable, non-exclusive, worldwide copyright license". Uso comercial
  e modificação permitidos. "Coverr started as CC0 (no copyright reserved)", e deixou de ser. Crédito: "You are
  not required to add an attribution credit to the original creator or to Coverr.co", "although it is
  appreciated when possible". "Coverr.co reserves the right to modify these license terms at any time."
- **Não permitido.** "Utilizing trademarks, logos, or brands that appear in the videos or music tracks"; "We do
  not hold releases for any brands, trademarks, or identifiable properties or landmarks". A Coverr obtém
  autorização das pessoas filmadas, mas não a repassa: "Recognizable individuals have rights related to
  commercial use of their image and likeness". Revender ou redistribuir; montar serviço concorrente; treinar IA.
- **Site.** Os termos dão só "non-commercial use of the Website" (o site, não os vídeos). Os vídeos seguem a
  página de licença. Os termos proíbem robôs e extração automática no site. Lei de Israel.
- **Catálogo misturado.**
  - Vídeos da Shutterstock aparecem nas listagens, com link de afiliado para shutterstock.com, e não são
    conteúdo Coverr.
  - Alguns vídeos têm o rótulo "AI Generated", sem licença própria encontrada.
  - O Coverr+ (pago) tem "the same non-exclusive, non-transferable, worldwide license" (termos, 15.2).
- **API.** Chave imediata com conta; demo gratuita com 50/h; produção exige plano Pro ou Ultimate (pago,
  fora do §2.1). Crédito: "show your users where the videos are pulled from", com o logo clicável. Download:
  "pinging the `mp4_download` is a MUST and not optional" ✔. Hotlink previsto (URL assinada, sem expiração,
  ligada à chave). Campos: `duration`, `max_width`, `max_height` (sem descrição), `is_vertical`,
  `aspect_ratio` e `urls {mp4, mp4_preview, mp4_download}`. Escolher a resolução está "COMING SOON". A
  página não diz que resolução o `mp4_download` entrega.
- **Contradição sobre uso comercial pela API** ✔:
  - a documentação diz "This access is free as long as you don’t charge for it yourself, AKA re-sell or use the
    videos for commercial use.";
  - a página de desenvolvedores responde "Can I use the API for commercial purposes?" com "Absolutely. All
    content accessed through the API is commercially licensed."
