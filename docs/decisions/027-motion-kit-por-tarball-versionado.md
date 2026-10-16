# 027 — motion-kit por tarball versionado no `video/`

- **Status:** aceito pelo dono em 2026-10-16 (o tarball versionado no repositório, por enquanto; registry depois)
- **Data:** 2026-10-16
- **Etapa do roadmap:** template do `explainer` (`video/`)
- **Relaciona-se com:** ADR 001 (um motor por formato), CLAUDE.md §2.9 (dependência nova) e §14 (cruzar o kit
  com o checkout), MR !30 do motion-kit (monorepo e versão 0.4.0)

## Contexto

Até a 0.3.0, `video/package.json` fixava o `@viniciusk/motion-kit` num commit do GitLab: a URL
`.../repository/archive.tar.gz?sha=<sha>` baixa o repositório inteiro, e a raiz dele era o pacote. O último
commit fixado foi o `2ec39fb` (`feat/word-caption`).

O motion-kit virou um monorepo (`feat/library-release`, levado ao `main` pelo MR !30). A biblioteca está em
`packages/motion-kit` e a raiz é o workspace privado `motion-kit-repo`. A URL por SHA passou a instalar essa
raiz, sem `dist/` nem exports: o jeito antigo não serve mais para nenhuma versão nova do kit.

Na mesma mudança, `@remotion/layout-utils` e `@remotion/paths` deixaram de ser dependências do kit e viraram
peer: quem instala o kit declara as duas, na versão do Remotion que já usa.

## Decisão

1. **O kit entra como o arquivo do `npm pack`, versionado no repositório:**
   `video/vendor/viniciusk-motion-kit-<versão>.tgz`, com
   `"@viniciusk/motion-kit": "file:vendor/viniciusk-motion-kit-<versão>.tgz"` no `package.json`. O lock guarda a
   integridade do arquivo, e o `npm ci` instala sem rede para o kit.
2. **Um arquivo só em `vendor/`.** Subir o kit troca o arquivo, sem deixar o anterior: o Git guarda o histórico.
3. **A origem fica no commit.** A mensagem do commit que troca o arquivo diz de qual commit do motion-kit ele
   saiu e em que MR. O arquivo é gerado com `npm pack` dentro de `packages/motion-kit`, a partir de um checkout
   limpo daquele commit, depois de `npm run check`. A primeira versão é a 0.4.0, gerada do `068f4a3`
   (`feat/reels`, MR !30); a árvore desse commit é a do `90cac99`, de onde o `npm run check` passou.
4. **`@remotion/layout-utils` e `@remotion/paths` ficam declaradas no `video/package.json`**, na versão exata
   do `remotion` (4.0.529 hoje), que já estavam na árvore pelo kit. As duas têm licença MIT (lock do `video/`).
5. **O que o template renderiza é o pacote instalado.** Para conferir uma prop, vale o tipo em
   `video/node_modules/@viniciusk/motion-kit/dist/` (ou o `CHANGELOG.md` do kit até aquela versão); o MCP
   `motion-kit` lê o checkout, que pode estar à frente.

## Alternativas

- **Registry de pacotes (npm do GitLab ou npmjs):** é o caminho limpo e o que o README do kit já sugere
  (`npm install @viniciusk/motion-kit`). Pede publicar a cada versão, com token, e configurar o `.npmrc` do
  `video/`. Fica para quando as versões ficarem frequentes ou o kit tiver outro usuário.
- **URL de arquivo de outro ponto do GitLab** (artefato de CI, release): depende de pipeline e de link estável,
  que o kit ainda não tem.
- **`file:` apontando para o checkout do motion-kit:** cria dependência do caminho de outro projeto na máquina,
  que o workspace proíbe ("nenhum projeto importa código do outro").

## Consequências

- Cada versão do kit soma cerca de 2,4 MB ao histórico do repositório. Aceitável enquanto a troca for rara; se
  passar de uma por semana, rever pelo registry.
- `app/media/evolution.py` lê o kit fixado das duas formas (`motion_kit_pin`): o SHA curto até a 0.3.0, a versão
  do tarball daqui em diante. As versões antigas do registro do vídeo-régua continuam com o SHA.
- CLAUDE.md §3 e §14, a skill `componentes-do-kit` e o mapa do `workspace-video` trocam "SHA do pin" pela
  versão do tarball.
- Trocar o kit muda o `template_hash` (`app/render/remotion.py`), e as cenas renderizadas de novo usam a versão
  nova. Um episódio com o gate 4 aprovado não é renderizado de novo por causa disso.
