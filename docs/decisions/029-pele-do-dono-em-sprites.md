# 029 — Pele do dono em sprites por manifesto, com direção automática

- **Status:** aceita pelo dono em 2026-10-16 e implementada (seção "Implementação"). As decisões abertas 3 e 4
  seguem a proposta; 1, 2 e 5 continuam com o dono e não travam o código, só o vídeo final com a pele nova.
- **Data:** 2026-10-16
- **Etapa do roadmap:** frente do apresentador (continuação da ADR 017, parte A)
- **Relaciona-se com:** ADR 007 (licenças), ADR 013 (apresentador em janela), ADR 014 (vertical), ADR 017 (pele
  `dono`), ADR 022 (entrega da fala), ADR 027 (kit por tarball); motion-kit 0.5.0 e 0.6.0 (pele de sprites,
  MR !31 e !32)

## Contexto

A pele `dono` (ADR 017, parte A) são 12 imagens inteiras, uma por boca, com e sem piscada. A regra está em código:
`app/media/host.py` exige os 12 nomes e `video/src/donoSkin.ts` monta o nome do arquivo pelo estado. Com isso o
apresentador só fala e pisca: não vira o rosto, não gesticula, não muda de expressão. Para cada estado novo,
imagens inteiras novas, e a conta passa de 100.

O motion-kit ganhou a pele de sprites em camadas (0.5.0) e a pasta pela convenção de nomes (0.6.0):

- **Manifesto (`sprites.json`, formato `host-sprites.v1`):** diz a camada de cada imagem e quando ela aparece.
- **Montagem pelos nomes:** `motion-kit sprites init <pasta>` escreve o manifesto a partir dos nomes dos arquivos
  (`cabeca-esq.png`, `boca-a.png`, `bracos-aponta.png`).
- **Conferência:** `motion-kit sprites check <pasta>` confere o manifesto e os arquivos.

As 8 camadas que já existem (`docs/sprites-bruto/camadas/`: base, 6 bocas, olhos fechados) viram um manifesto sem
erro.

## Proposta

1. **A pasta `host/dono/` do episódio passa a ter camadas e um `sprites.json`.** Continua fora do Git e com o
   `origem.json` obrigatório. O manifesto é gerado por `npx motion-kit sprites init` dentro de `video/` e pode ser
   editado à mão (licença, ordem das camadas, recortes); rodar de novo mantém o que foi editado.
2. **O Python não reimplementa o formato.** `app/media/host.py` roda `motion-kit sprites check` (do `video/`
   instalado) antes do render e para com a mensagem do comando. O `sprites_hash` passa a cobrir o `sprites.json`
   e todos os arquivos que ele cita.
3. **O adaptador manda o manifesto nas props** (`host.sprites`), e `donoSkin.ts` vira `createSpriteSkin(manifesto,
   { url: (file) => staticFile('host/dono/' + file) })`. Trocar um desenho continua refazendo as cenas.
4. **Direção automática**, calculada em `app/media/host.py` e enviada nas props, sem campo novo no roteiro:
   - **Olhar:** para o lado do conteúdo. Janela num canto da direita olha para a esquerda (`left`), e vice-versa.
   - **Gesto:** aponta (`point`) quando entra na cena um `number`, `compare`, `calculation`, `receipt` ou `chart`,
     por ~1,5 s. No resto da fala, gesticula (o ciclo `gesticulate` do kit).
   - **Expressão pela entrega da fala (ADR 022):** `hook` → `raised`, `turn` → `furrow`; as outras ficam em
     `neutral`. São expressões de base, que toda pele conhece. Na arte do dono, os nomes viram apelidos no
     `sprites.aliases.json` da pasta (`{"surpresa": {"expression": "raised"}}`).
   - O que a pele não desenha cai no repouso: a mesma direção vale para a Notionists e para um dono só com boca e
     piscada.
5. **Os episódios antigos continuam.** Sem `sprites.json` em `host/dono/`, vale a pele de 12 imagens de hoje
   (`thiel-contrato-pt`, `thiel-empresa-pt`).
6. **O kit sobe para a 0.6.0** pelo processo da ADR 027, depois do MR !32.

## Decisões abertas (do dono)

1. **Origem e licença da arte.** O `origem.json` está em `needs_review` sem gerador. Sem o gerador e os termos, a
   pele (antiga ou nova) só serve para prévia. A lista fechada da ADR 007 também não tem entrada para ativo de
   autoria do dono.
2. **Os 33 sprites versionados em `docs/sprites-bruto/`.** A ADR 017 diz "fora do Git". Ou saem do histórico, ou
   esta ADR registra a exceção (o repositório é privado).
3. **A direção automática do item 4 vale também para a Notionists?** A proposta é que sim, já que o que a pele não
   sabe cai no repouso. Isso muda o `template_hash` e o desenho de vídeos renderizados de novo.
4. **Campo opcional no roteiro para mandar no apresentador** ("aqui ri", "aqui olha para a câmera"). A proposta é
   esperar o uso da direção automática antes de abrir campo novo no contrato.
5. **A primeira leva de arte:**
   - cabeças em 3 ângulos (frente, ¾ esquerda, ¾ direita);
   - 4 expressões (neutra, `raised`, `furrow`, riso);
   - 5 gestos (repouso, apontar, mão aberta, contar, dar de ombros);
   - olhos fechados por ângulo.

## Implementação (2026-10-16)

- **Kit 0.6.0** em `video/vendor/`, pelo processo da ADR 027, do commit `4556fa7` do motion-kit (branch
  `feat/sprite-cli`, MR !32). O MR foi mesclado no `main` em `d5ba5c4`, com `packages/motion-kit` idêntico ao
  do `4556fa7`: o arquivo vale como está. Depois o kit subiu para a 0.7.0 (`9b9561a`, MR !33), que só muda o
  catálogo de estilos do vídeo por JSON; o template não usa o catálogo, e nenhum quadro muda.
- **Conferência:** `app/media/host.py` roda `node video/node_modules/@viniciusk/motion-kit/bin/motion-kit.mjs
  sprites check host/dono` antes do render (`RemotionEngine.render`), só quando há `sprites.json`; o erro para o
  render com a mensagem do comando. Sem `npx`, para não depender de rede.
- **Hash:** com `sprites.json`, cobre o manifesto, os arquivos que ele cita e o `origem.json`. Imagem da pasta
  fora do manifesto não entra no render nem no hash.
- **Props:** o manifesto vai em `host.manifest`, não em `host.sprites` como dizia o item 3: `host.sprites` já era
  o hash das imagens, e continua sendo. A direção vai em `host.direction` (`look`, `expression` e `gesticulate`
  ou `gestures`).
- **Gestos:** o `<Host>` não mistura gesto agendado com o ciclo de gesticular. Numa cena em que o apresentador
  aponta, o Python escreve o ciclo por extenso (repouso ↔ mão aberta a cada 21 quadros, os números do kit) com o
  apontar por cima. O ciclo para meia volta antes de apontar, para não piscar um gesto de poucos quadros. Dois
  planos de apontar a menos de 1,5 s um do outro emendam.
- **Entrega no `episode.json` (emenda ao contrato):** a entrega da fala só existia no roteiro, e o motor lê só o
  `episode.json`. `EpisodeScene` ganha `delivery` opcional (os mesmos valores da ADR 022), copiado por
  `scripts/provisorio/montar_episodio.py`. `schema_version` não muda: um `episode.json` antigo vale como está,
  com a expressão neutra.
- **Template:** `donoSpriteSkin(manifesto)` em `video/src/donoSkin.ts` (`createSpriteSkin` com
  `staticFile('host/dono/' + arquivo)`); `HostWindow.tsx` escolhe a pele pelo manifesto e passa a direção ao
  `<Host>`. Props sem direção (cache antigo) se comportam como antes.
- **Conferido:** com as 8 camadas reais numa cópia temporária, o `sprites init` do kit instalado gera o manifesto
  (8 sprites, 3 camadas, um aviso esperado: a camada "olhos" só tem o olho fechado), o `check` passa e a cena em
  retrato monta a pele. Na Notionists, com gancho e número, a sobrancelha sobe, a mão aponta e o olhar vai para o
  conteúdo. A cópia foi apagada.
- **Efeito no cache:** toda cena com apresentador ganha `direction` nas props e é renderizada de novo.

## O que não muda

- A boca segue o áudio da cena (envelope RMS), como hoje.
- O canto da janela continua saindo de `host_corners` (ADR 013), e o olhar só lê o canto escolhido.
- Nenhuma imagem sai da máquina. As ferramentas do kit leem só a pasta local.

## Consequências, se aceita

- **Código:**
  - `app/media/host.py`: conferência pelo comando do kit, hash do manifesto e a direção automática;
  - `app/render/remotion.py`: `host.sprites` e a direção nas props;
  - `video/src/donoSkin.ts` e `HostWindow.tsx`;
  - `video/package.json`: kit 0.6.0;
  - testes da direção (olhar pelo canto, aponta no número, expressão pela entrega).
- **Documentação:** CLAUDE.md §6 (apresentador) e a ADR 017, com a emenda datada.
- **Antes de um vídeo com a pele nova:** vídeo-régua e sonda de CPU.
