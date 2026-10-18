# 007 — Contratos de dados e política de licenças

- **Status:** aceito
- **Data:** 2026-09-25
- **Etapa do roadmap:** #3

## Contexto

O §6 do CLAUDE.md lista os campos dos manifestos, mas deixa em aberto a granularidade das cenas, como a
aprovação humana é registrada, quais licenças podem chegar ao render e o formato do vídeo. A
`docs/spec-v0.4.md` original não está no repositório; os contratos saem do CLAUDE.md.

## Decisões

1. **Uma cena = um bloco de narração = um WAV = um visual.** Com 20–35 cenas em 5–7 min (~14 s cada),
   trocar uma frase ou uma imagem invalida só aquela cena. Um mapa pode voltar em várias cenas, por isso o
   ativo usa `used_in_scenes` (lista) em vez do `used_in_scene` do §6.
2. **Claims citam fonte e, opcionalmente, trecho.** `source_ids` continua obrigatório (§2.2);
   `excerpt_ids` (`source-01#E3`) já existe e precisa pertencer às fontes citadas. Vira obrigatório quando
   a ADR 002 (etapa 26) for aceita.
3. **`review.json` é a fonte única das decisões humanas.** Entradas só são acrescentadas, por etapa,
   cena ou ativo, com `input_hash` do que foi revisado: se o conteúdo muda, a aprovação deixa de valer.
   O `review_status` dos outros manifestos é só reflexo, escrito pelo código.
4. **Lista fechada de licenças aceitas** para um ativo chegar a `approved`: `PD-US`, `PD-old`, `CC0-1.0`,
   `CC-BY-2.0/2.5/3.0/4.0`, `Flickr-NKCR`, `Pexels`, `Generated` (Workers AI) e `Original` (gráfico do
   projeto). Ficam **fora**, e portanto em revisão humana: CC-BY-SA (o compartilhamento pela mesma licença
   poderia alcançar o vídeo inteiro), qualquer NC (o canal pretende monetizar) e licença não identificada.
   Regras adicionais para aprovar: `sha256` do arquivo final; domínio público exige o raciocínio em
   `usage_notes`; CC-BY exige `author` e `attribution_text`; ativo de acervo exige `page_url`.
   Decisão de negócio do dono do projeto, não parecer jurídico.
5. **Formato do vídeo:** 1920×1080, 30 fps, áudio 48 kHz, 16:9 validado no `episode.json`; a prévia em
   1280×720 é opção do render, não do contrato.

## Consequências

- `app/pipeline/schemas.py` implementa tudo acima; `tests/fixtures/episodes/pilot-example/` é o exemplo
  de referência (conteúdo fictício, URLs `example.org`).
- Regras entre arquivos são funções: `unknown_source_refs` (§2.2) e `visual_need_violations` (§2.4:
  Pexels e Workers AI nunca como `historical_exact`).
- `script.json` ainda não tem schema: nasce na etapa 27 com o formato que o LLM precisar produzir.
- Ampliar a lista de licenças exige nova ADR.

## Emenda — 2026-09-26

`CC-BY-3.0-BR` (Creative Commons Atribuição 3.0 Brasil, mesmos termos do CC BY 3.0, usada pela Agência
Brasil) entra na lista, com as mesmas exigências de `author` e `attribution_text`. Aprovado pelo dono do
projeto na pesquisa da fatia Votorantim (`docs/pesquisa/votorantim-viabilidade.md`).

## Emenda — 2026-09-26 (bancos de imagem)

Pixabay, Unsplash e Coverr entram na lista ao lado do Pexels, para fotos e B-roll de ilustração (abertura v2 da
Votorantim, #48). Os termos foram lidos nas páginas oficiais em 2026-09-26 e estão registrados em
`data/benchmarks/termos-bancos-de-imagem.md`. Decisão do dono do projeto, não parecer jurídico.

1. **Licenças novas:** `Pixabay` (Content License), `Unsplash` (Unsplash License) e `Coverr` (licença própria da
   Coverr). A parte do acervo em CC0 (no Pexels, quando a página indica; no Pixabay, o que foi publicado antes de
   9/1/2019) entra como `CC0-1.0`. Um ativo de banco só é aprovado com a licença do próprio banco ou `CC0-1.0`, e
   a licença de um banco não vale para outro provedor.
2. **Regra comum para aprovar um ativo de banco** (Pexels, Pixabay, Unsplash, Coverr):
   - `page_url`;
   - `author` e `attribution_text`: o crédito vai para o `credits.txt` e a descrição mesmo quando a licença não
     exige, porque as APIs do Pexels e do Unsplash pedem;
   - `usage_notes` com a conferência humana dos direitos de terceiros, que as quatro licenças deixam com o
     usuário: nenhuma pessoa reconhecível em close, nenhuma pessoa retratada como doente ou tomando remédio,
     nenhuma marca, logo ou texto visível, nenhum uso em contexto político.
3. **Nunca registro:** os quatro bancos entram em `visual_need_violations` (nunca `historical_exact`, §2.4).
4. **Pixabay:** adapter pela API (100 requisições por 60 s, respostas em cache por 24 h, arquivo baixado em vez
   de hotlink). Sem aprovação de acesso completo, a foto chega a no máximo 1280 px: usar de preferência para vídeo.
5. **Unsplash:** adapter pela API, só para foto (a API não tem vídeo), em modo demo (50 requisições por hora).
   O adapter cumpre os termos da API:
   - chama `download_location` a cada download;
   - grava o crédito "Photo by <autor> on Unsplash", com links para o perfil do autor e para o Unsplash
     (`utm_source`, `utm_medium=referral`), no `credits.txt` e na descrição.

   A foto editada dentro do vídeo é tratada como obra derivada, que as diretrizes dispensam do hotlink ("If the
   image is remixed to create a derivative creative image, these results do not need to be hotlinked"). Essa
   leitura é do dono do projeto: os termos da API foram escritos para apps que exibem as imagens e não tratam de
   vídeo.
6. **Coverr:** só clipes baixados à mão pelo dono no site, sob a licença da página `/license`. Não há adapter de
   API enquanto a documentação da API disser que o acesso gratuito não cobre "commercial use", o que contradiz a
   página de desenvolvedores. Ficam de fora os vídeos da Shutterstock que aparecem nas listagens e os clipes
   marcados "AI Generated".
7. **Áudio:** o B-roll de banco entra sem som. O template já faz isso; os termos do Pexels e do Pixabay citam
   "audio or video samples" entre os possíveis direitos de terceiros.

## Emenda proposta — 2026-10-17 (programa de criadores do detentor)

**Status:** proposta, sem decisão. Depende da resposta da KADOKAWA ao e-mail sobre o CSP e da decisão do dono. Até
lá, nada muda no código nem na lista acima. Contexto: `docs/pesquisa/reports/Nicho recap de anime.md` (adendo CSP) e
`docs/pesquisa/research_notes/Nicho recap de anime/csp_kadokawa.md`.

1. **Licença nova `Holder-Program`.** Cobre trecho de vídeo ou quadro de uma obra de terceiros usado sob um
   programa oficial do próprio detentor (o primeiro caso é o Creator Support Program da KADOKAWA). Vale só para os
   títulos cuja diretriz publicada cubra o uso. Título sem diretriz continua fora.
2. **Para aprovar o ativo**, além de `sha256` e `page_url`:
   - `program` (ex.: `KADOKAWA-CSP`) e a obra: título, episódio e o `source_sha256` da importação (#156);
   - cópia datada da página da diretriz guardada no episódio, com URL, data e `sha256`. As diretrizes somem sem
     aviso; a de *Mattan* já sumiu;
   - limite da diretriz em segundos por episódio de origem e por vídeo publicado. O `vp check` soma os trechos de
     cada episódio, pelos PTS do índice da #156, e barra o que passar do limite;
   - `attribution_text` exigido pela diretriz, copiado para a descrição e o `credits.txt`;
   - `usage_notes` com a conferência humana de música, miniatura, voz e plataforma, e a data do pré-registro do canal.
3. **Só YouTube.** O vídeo com ativo `Holder-Program` não pode ser agendado em outra rede pelo `vp postiz`
   (ADR 025). Nas outras redes, só material próprio que leve ao vídeo do YouTube, se a diretriz permitir.
4. **Fora até haver resposta escrita do detentor:** personagem gerado por IA, fan art, música do anime e imagem de
   episódio na miniatura.
5. **Diretriz que muda ou some:** a cópia guardada prova a permissão na data. Ativo ainda não aprovado volta a
   `needs_review`; vídeo já publicado mantém o registro.
6. **Reivindicação esperada:** o detentor reivindica o vídeo e fica com parte ou toda a receita. A reivindicação não
   pode ser contestada, e isso deve constar no pacote do gate 4.

Decisão do dono do projeto, não parecer jurídico. Ao ser aceita, a emenda exige o schema novo em
`app/pipeline/schemas.py`, o check de tempo por episódio, o bloqueio no `vp postiz` e a atualização do §6 do CLAUDE.md
no mesmo commit.

## Emenda proposta — 2026-10-17 (citação para crítica: quadros e miniatura)

**Status:** aceita pelo dono em 2026-10-17 ("sim, aceito a emenda"), com as opções 3 (quadros parados como
citação dentro do vídeo) e 4 (quadro da obra na miniatura) e os limites abaixo. **Implementação pendente:** até o
schema e o check entrarem, nenhum ativo `Citacao` chega a `approved`.

**Implementada em 2026-10-17:**
- em `app/pipeline/schemas.py`: `Provider.OFFICIAL`, a licença `Citacao` e o campo `work`;
- no `vp check`: `citation_violations` (quadros por vídeo, tempo de tela estimado e proibição de B-roll);
- testes em `tests/test_citation.py`;
- §6 do CLAUDE.md atualizado.

O tempo real só existe depois da voz. A miniatura, as franquias fora e o strike ficam no gate, sem regra em
código. Contexto:
`docs/pesquisa/reports/Nicho recap de anime.md`, adendos de demanda e franquias. Decisão de risco do dono, não
parecer jurídico. A base é a citação para crítica (Lei 9.610/98, art. 46, III: "na medida justificada para o fim a
atingir") e o exemplo do YPP "Using clips for a critical review".

1. **Licença nova `Citacao`.** Cobre só quadro parado de uma obra que é assunto do argumento do vídeo (ensaio,
   análise, crítica). Ficam fora: trecho de vídeo, áudio da obra, painel em sequência que reproduza uma cena e
   arte promocional (pôster, key visual).
2. **Dentro do vídeo:**
   - até **10 quadros** por vídeo;
   - cada quadro na tela **só enquanto a narração comenta aquele quadro**, até **8 s**;
   - quadros seguidos não podem imitar movimento;
   - recorte e zoom para destacar o que se comenta são permitidos;
   - o quadro não pode ser espelhado nem disfarçado para escapar da detecção.
3. **Miniatura:** um quadro da obra, sem arte promocional, com texto ou gráfico nosso ocupando parte relevante da
   imagem. O dono confirma o risco da miniatura a cada vídeo, no gate 4.
4. **Origem do quadro: só material oficial público do detentor** (decisão do dono em 2026-10-17): trailer, PV,
   episódio publicado pelo próprio detentor ou licenciado no canal oficial dele, e site oficial. Mídia comprada
   fica para uma decisão futura. O print de streaming fica fora: a Crunchyroll limita o uso de capturas a fins não
   comerciais. A extração pode usar a #156 (frames com PTS) sobre essa origem, e o `page_url` aponta a publicação
   oficial. Para *Death Note* (2006; © D.N. Dream Partners, VAP, Shueisha, Madhouse, NTV), os candidatos são:
   - o trailer distribuído pela VIZ Media;
   - os 37 episódios que a VIZ publicou no próprio canal do YouTube, segundo a imprensa em 2022, só nos EUA. Isso
     falta conferir.
5. **Para aprovar o ativo:**
   - `sha256` e `page_url` (ou a descrição da mídia própria);
   - a obra (título, estúdio e detentor conhecido);
   - `usage_notes` com a **justificativa**: que trecho da narração o quadro ilustra e por quê;
   - `attribution_text` para a descrição e o `credits.txt`.

   Cada quadro passa pelo gate 3.
6. **Franquias fora** até haver evidência de como o detentor trata ensaios: obras da Toei (*One Piece*, *Dragon
   Ball*) e da ShoPro (*Pokémon*), que já tem strike por imagem parada.
7. **Reivindicação ou strike:**
   - registro no `review.json`;
   - nenhuma contestação sem decisão do dono;
   - **um strike suspende a série** até o dono revisar esta emenda.
8. **Contagem em código, quando aceita:** o `vp check` conta os quadros `Citacao` e o tempo de tela de cada um.

Ao ser aceita, a emenda pede no mesmo commit:
- a licença e os campos novos em `app/pipeline/schemas.py`;
- o check;
- a atualização do §2.3 e do §6 do CLAUDE.md.
