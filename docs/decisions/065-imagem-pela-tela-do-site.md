# 065 — Imagem gerada pela tela de um site como adaptador da porta de imagem (`vp imagens`)

- **Status:** aceito pelo dono em 2026-11-20 (plano aprovado: "ok me parece adequado"; configuração no toml:
  "moveriamos essas informações e utilizamos o toml"). Comportamento novo: o PR espera a revisão do dono.
- **Data:** 2026-11-20
- **Pedido do dono:** trazer `scripts/provisorio/fila_imagens.py`, `imagens_navegador.py` e `sites_imagem.toml`
  para o pipeline, com os seletores dos sites no toml.
- **Relaciona-se com:** ADR 006 (portas e adaptadores), ADR 007 (licença `Generated`), ADR 042 (registro de
  comandos), ADR 064 (pacotes por etapa: a fila vai para `app/pipeline/visuals/`); CLAUDE.md §2.1, §2.4, §6 e §8.

## Contexto

Desde 2026-11-11 as imagens para lacuna saem da tela do Gemini, no Chrome que o dono abre e loga, por dois
scripts sem comando: `fila_imagens.py` (pedidos, registro e o que falta) e `imagens_navegador.py` (Playwright via
CDP), com os seletores em `scripts/provisorio/sites_imagem.toml`. Funcionava, mas:

- a porta `ImageGenProvider` não tinha referências (`refs`) e exigia semente e passos (`Generation`), que a tela
  de um site não tem; por isso o navegador ficou fora dela;
- o teto editorial do §6 (12 imagens por episódio, 2 por cena) não era cobrado: o padrão do script era 20 por
  rodada;
- o bloco do ChatGPT estava no toml como se fosse usável, sem os termos conferidos;
- a configuração ficava num toml ao lado do script, fora do `config/providers.toml` que escolhe os outros
  adaptadores.

## Decisão

1. **Porta.** `ImageRequest` ganha `refs` (imagens anexadas ao pedido). `GeneratedImage` ganha `generator` (quem
   gerou) e `origin` (onde reabrir a imagem, a conversa do site); `generation` passa a ser opcional: `None` no
   gerador sem semente. A porta ganha `close()`, chamado uma vez ao fim da rodada. O adaptador pode trocar a
   extensão do `out_path` pela do arquivo recebido (PNG, JPEG ou WebP), nunca a pasta nem o nome.
2. **Adaptador `browser_image`** (`app/providers/image_gen/browser.py`, com `browser_page.py` e
   `browser_network.py`): conecta pelo CDP ao Chrome do dono, abre uma aba nova e faz um pedido por conversa nova.
   Login, captcha ou aviso de limite viram `AccessBlocked` (erro novo de provedor, `access_blocked`) e param a
   rodada; pedido sem imagem vira `InvalidOutput`. Custo por chamada zero (conta do dono, sem API). O Playwright
   segue no extra `navegador` e só é carregado na primeira chamada; os testes usam uma página falsa.
   Endereços de imagem do site podem ser assinados e não vão para erro nem log (§2.7); o diagnóstico do script
   que os imprimia saiu.
3. **Configuração no `config/providers.toml`.** `image_gen = "browser_image"` (era `workers_ai`, que segue sem
   adaptador). `[browser_image]` guarda a porta do Chrome, o site escolhido, a pausa entre pedidos e a espera;
   `[browser_image.sites.<nome>]` guarda os seletores (os mesmos do `sites_imagem.toml`, com nomes de campo em
   inglês, como o resto do arquivo) e `enabled`. Trocar de site é mudar a linha `site`.
4. **Só o Gemini ligado** (decisão do dono de 2026-11-20). O bloco do ChatGPT fica com `enabled = false` até o
   dono conferir os termos de automação; escolher um site desligado ou sem bloco para na composição, antes de
   abrir o navegador. Aviso registrado uma vez: os termos de automação do próprio Gemini também não foram
   conferidos, e o risco é da conta pessoal do dono.
5. **Fila em `app/pipeline/visuals/image_queue.py`.** Mesmo `pedidos.json` (com `cena` opcional) e mesmo
   `registro.jsonl` do script, só acrescentado; as linhas antigas continuam valendo, então uma pasta começada pelo
   script retoma pelo comando. A linha `gerada` ganha `cena` e `conversa` quando existem.
6. **Teto do §6 cobrado** (`app/pipeline/visuals/image_round.py`, valores do `[limits]`): conta o que já está pronto
   na pasta de saída mais o que a rodada vai pedir; pedido sem `cena` conta só no total. Acima do teto, o
   `vp imagens gerar` recusa antes de abrir o navegador; com `--acima-do-teto`, segue e avisa. `vp imagens plano`
   mostra o que passaria.
7. **Comando `vp imagens`** (`plano`, `mapear`, `gerar`), registrado como os outros (ADR 042). `--rodada N` limita a
   rodada (era `--teto`); `--site`, `--cdp`, `--intervalo` e `--espera` saíram da linha de comando e vivem no toml.
   Saída 1 quando algum pedido da rodada falhou.
8. Os dois scripts e o `sites_imagem.toml` saem neste PR. O `registrar_imagens_ia.py` sai no PR do
   `vp assets gerada`; o `gerar_imagens_klein.py` (Workers AI) vira o próximo adaptador da porta.

## Consequências

- Imagem gerada continua fora do episódio até o gate 3: nada aqui cria `assets/<id>.json` nem mexe no
  `scenes.json`. O registro como ativo é o `vp assets gerada` (próximo PR, com a emenda da ADR 007 de 14/11).
- Uma tela que muda quebra os seletores: `vp imagens mapear` lista o que cada um encontra e o conserto é no toml.
- `context.image_gen` passa a montar o navegador; quem quiser o Workers AI troca a linha `image_gen` quando o
  adaptador existir.

## Fora do escopo

- Automação que passe por login, captcha ou limite: o adaptador para, não contorna.
- Ligar o ChatGPT ou outro site: decisão do dono, depois de conferir os termos.
