# 029 — Pele do dono em sprites por manifesto, com direção automática

- **Status:** proposta, aguardando o dono (2026-10-16). Nada implementado; onde diz **decisão aberta**, o agente
  não decide.
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
