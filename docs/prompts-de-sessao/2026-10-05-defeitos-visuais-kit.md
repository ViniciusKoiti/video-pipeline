# Prompt de sessão: defeitos visuais do motion-kit (2026-10-05)

Colar numa sessão nova do Claude Code aberta em `~/projetos/auto-play`. Estado de partida: pin do `video/` em
`2af5a7e`, `main` do kit em `52f54b7`, skill `componentes-do-kit` mergeada (PR #101), MCP `motion-kit` registrado
no escopo local.

---

Contexto: video-pipeline (CLAUDE.md na raiz). Foco atual, decisão do dono: o template do formato explicativo
(`video/`, Remotion + @viniciusk/motion-kit), uma frente por vez, com calma. Uma frente = um PR; me mostre o
resultado antes de qualquer merge.

Frente de hoje: dois defeitos visuais no motion-kit, corrigidos NO KIT (repositório ~/projetos/motion-kit, GitLab),
antes do PR do pin daqui.

1. Rede (`ExpandingNetwork`, src/graph/ExpandingNetwork.tsx): o valor da seta (`edge.value`, um `DataChip`) tem
   `fontSize={16}` fixo (por volta da linha 298); só os nós têm `labelSize`. Falta uma prop para o tamanho do
   valor e do rótulo da seta, com o default atual.
2. Linha do tempo (`YearTimeline`, src/charts/YearTimeline.tsx): rótulos longos aparecem cortados. A caixa do
   rótulo tem largura `gap * 0.88` (por volta da linha 388) e o contêiner tem `overflow: 'hidden'` (por volta da
   linha 245). Essa causa é uma hipótese: confirme com um quadro renderizado antes de corrigir.

Antes de escrever código:
- Confirme que as ferramentas `mcp__motion-kit__*` estão na sessão. Se não estiverem, rode
  `claude mcp get motion-kit` e me diga o que apareceu.
- Siga a skill `componentes-do-kit` (/componentes-do-kit): `describe_component` para `ExpandingNetwork` e
  `YearTimeline`, e confira o SHA do kit (`git -C ~/projetos/motion-kit rev-parse HEAD`) contra o `sha=` de
  `video/package.json`. O pin do `video/` está em 2af5a7e e o main do kit em 52f54b7; diga qual a diferença.
- Me apresente, antes de editar: o que cada defeito é no código, a mudança mínima proposta (nome e default das
  props, sem mudar o visual de quem não as usa) e as dúvidas em aberto, agrupadas.

Execução, depois do meu "pode":
- Kit: branch a partir do main; mudar só `src/` e a documentação (`src/COMPONENTS.md`); `npm run typecheck`,
  `npm test` e `NODE_OPTIONS=--max-old-space-size=4096 npm run build` (o `dist/` é versionado e é de lá que o
  `video/` consome); teste novo para cada prop. `git push https://gitlab.com/ViniciusKoiti/motion-kit.git <branch>`
  (o SSH do origin está quebrado), MR com `glab`, esperar o pipeline `check`.
- Aqui, só depois do MR do kit mergeado: PR do pin (`video/package.json` e lock) com a versão nova do vídeo-régua
  (CLAUDE.md §1 "Vídeo-régua"): rodar a sonda de CPU antes (> 0,3 s = máquina limitada: parar e me avisar) e
  conferir na folha de quadros que mudaram só os planos de rede e de linha do tempo.

Limites desta sessão:
- Nenhuma chamada a provedor externo (Gemini, Pexels, Cloudflare…). Voz: Kokoro local ou o cache existente.
- Nenhum render além da versão do vídeo-régua do último passo.
- Arquivos `approved` em data/episodes/*/ ficam intactos; dúvida de licença: parar e perguntar.
- Antes de encerrar: `ruff check .` e `pytest` aqui; typecheck e testes no kit.

Pronto quando: MR do kit mergeado com pipeline verde; PR do pin aberto com a v-N e a folha mostrando só os planos
pretendidos; e um resumo meu, em linguagem simples, do que mudou na tela.
