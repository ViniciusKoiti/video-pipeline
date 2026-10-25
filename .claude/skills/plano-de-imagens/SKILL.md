---
name: plano-de-imagens
description: |
  Monta o plano de imagens de um episódio com roteiro aprovado: o que mostrar em cada plano, de onde vem
  (banco, Commons, quadro oficial da obra), a conferência de pessoas, marcas e texto e o registro de cada
  ativo. Valida o plano com o dono antes de baixar. Use depois do gate 2 e antes do gate 3.
argument-hint: "<episode-id>"
---

# Plano de imagens: roteiro aprovado → ativos conferidos

O roteiro já diz **o que** cada plano pede (`kind`, `visual_need`, `search_query`, âncora). Esta etapa decide
**qual** imagem entra e **onde ela pode ficar**, sem mudar fala, âncora de texto nem claim. A imagem não pode afirmar
o que a fala e as fontes não afirmam. Este é o erro mais comum desta etapa, e o `vp check` não o pega.

Regras de base, que valem antes de tudo: CLAUDE.md §2.3 e §2.4 (licença registrada; banco e imagem gerada são
ilustração, nunca registro), §6 (campos do ativo), §8 (cascata, regras dos bancos) e a ADR 007 com a emenda de
citação (quadros da obra).

## O que você escreve

- `plano-imagens.md`: o plano cena a cena (cena, tempo, âncora, tipo, ativo, licença) e a lista dos ativos usados.
- `decisoes-imagens.md`: cada escolha do dono, com data. Fica fora do `scenes.json`.
- `assets/<id>.json` (pelos scripts) e o `usage_notes` de cada um, com a conferência real.
- No `scenes.json`, o `asset_id` de cada plano, e `photo` → `broll` onde o dono escolheu textura.
  - **Gate 2 hoje:** o carimbo cobre o `scenes.json` inteiro, então gravar ou trocar `asset_id` derruba o gate 2 e o
    parecer do verificador. É preciso uma rodada do verificador e a reaprovação do dono (aconteceu no
    `kira-voto-brasil`).
  - **Depois do PR #169** (o carimbo passa a ignorar o `asset_id`), trocar a imagem não derruba mais.
  - **Tipo do plano ou âncora:** trocar derruba sempre, e aí o verificador confere e o dono reaprova.

## Método

1. **Ler.** Leia o `scenes.json`, o `outline.md` (espinha, quadros de citação, lacunas) e o `decisoes-imagens.md`. Liste
   os planos `photo` e `broll` com `visual_need`, `search_query` e âncora.
2. **Planejar por trecho** (os blocos da espinha do outline). Para cada trecho, separe:
   - **Retrato, página de livro, obra de arte:** Commons, Library of Congress e Flickr Commons (`historical_exact` ou
     `illustrative_reconstruction`).
   - **Quadro da obra** (`Citacao`): só material oficial. Veja "Quadros da obra" abaixo.
   - **Textura** (`contextual_stock`): um ou dois vídeos de banco por trecho, segurados (ADR 031, parte A: o mesmo
     vídeo continua entre planos e cenas). Foi o que o dono escolheu no `death-note-fins-meios`. Tornar isso o padrão
     do formato depende da ADR 031, partes B–E; até lá, pergunte ao dono se vai textura por trecho ou foto por plano.
   - **Foto pontual de banco:** só onde a fala pede um objeto concreto (o anel de Giges, a balança).
3. **Validar com o dono antes de baixar** (regra do dono). Mostre o plano por trecho, com a contagem do que já existe,
   do que reusar e do que buscar, e as decisões em aberto, numa pergunta só. Provedor externo (bancos, Commons,
   YouTube) só com pedido do dono na sessão.
4. **Buscar candidatos.** Escreva um `pedidos.json` com um pedido por trecho: consultas em inglês, `midias`, duração
   mínima e orientação. Rode `scripts/provisorio/buscar_candidatos.py <id> pedidos.json --limit 4`. Monte as folhas
   com `folhas.py` (nesta pasta).
   - **Triagem:** abra cada folha. Descarte o que tem rosto, marca, logo, texto legível ou contexto político, e
     indique um ou dois números por trecho. O dono escolhe.
   - **Folha fraca:** se um tema vier fraco, refaça a busca com outras palavras antes de mostrar.
5. **Baixar e conferir.** Rode `scripts/provisorio/baixar_escolhidos.py <id> <cena> <asset-id>`.
   - **Conferência do vídeo:** confira o vídeo **inteiro** com `conferencia.py` (quadros espaçados do começo ao
     fim), não a miniatura. Uma pessoa pode entrar no segundo 1.
   - **Conferência da foto:** confira a foto em resolução cheia. Letreiros ilegíveis na miniatura aparecem a 2.000
     px, e o `push_in` amplia.
   - **Registro:** escreva no `usage_notes` o que viu.
   - **Ativo reprovado:** não apague. Escreva `NÃO USAR (motivo, data)` no `usage_notes`.
6. **Commons.** Busque pela API, confira a licença na página do arquivo e o domínio público no país de origem.
   - **Licenças aceitas:** PD, CC0 e CC-BY. Nunca CC-BY-SA nem NC. Use o `license_id` da lista do schema
     (`ACCEPTED_LICENSES` em `app/pipeline/schemas.py`): CC0 é `CC0-1.0`, e o `vp approve` recusa `CC0`.
   - **Registro:** `provider: wikimedia_commons`, autor, `attribution_text` e o raciocínio no `usage_notes`.
   - **Texto da obra:** registre o texto que aparece nela (título da página, legenda pintada, assinatura,
     monograma).
7. **Gravar no roteiro.**
   - `asset_id` em cada plano.
   - Textura: `kind: broll` com `search_query: "textura: <o que o vídeo mostra>"`.
   - O `search_query` descreve o que o ativo **mostra**, não o que o roteiro pediu.
   - Recalcule o `used_in_scenes` de todos os ativos a partir do `scenes.json`.
   - Rode `vp check`. Atualize `plano-imagens.md`, `decisoes-imagens.md` e, no outline, a tabela de quadros, os
     números e as lacunas.
8. **Checar.** Mande o verificador conferir as imagens com as regras abaixo, abrindo os arquivos, **na mesma conversa
   em que ele já checou o texto** (retome o agente; não abra outro: skill `checagem`, "Rodadas e contexto"). Grave o
   parecer com `vp checagem`. Depois vêm o gate 2 de novo, se o tipo de algum plano mudou, e o gate 3, ativo por ativo
   (`vp approve <id> --step assets --asset <asset-id>`).

## Onde cada imagem pode ficar

| Regra | Errado (já aconteceu) | Certo |
|---|---|---|
| Quadro da obra só sob a fala que ele comprova. Trailer e cena oficial não dizem de que episódio são, então quadro de personagem vai em fala **só sobre o personagem**, nunca sob fala que narra uma cena de episódio | close de Light sob "Ainda no último episódio, Light confessa"; Naomi sob "Light mente… e consegue o nome dela" | Light em "Soa parecido com Light?"; Naomi em "ex-agente do FBI e companheira de Raye Penber"; a cena do episódio fica na textura |
| Texto legível no quadro concorda com a fala | regra dos "40 seconds… heart attack" sob "quarenta segundos depois, o coração para" (o texto diz outra coisa) | a página "The human whose name is written in this note shall die" sob "É uma Death Note" |
| Retrato do autor só onde a fala é sobre o autor, nunca sobre um personagem dele | Dostoiévski sob "E se alguém se achasse acima das regras?" e nas páginas de *Crime e Castigo* | retrato em "Fiódor Dostoiévski", página de rosto onde a fala é sobre o livro |
| Textura não ilustra literalmente o evento da fala | multidão de banco sob "uma multidão… cerca o prédio da SPK" | multidão só no "vulgo" de Maquiavel; a cena do anime fica na fumaça |
| Banco sem pessoa reconhecível, marca, logo ou texto legível, conferido em resolução cheia | estante com títulos legíveis; cidade com letreiros de banco e hotel; vídeo do estádio com jogadora a partir de 1 s | cinema vazio, estádio visto do alto, conferidos quadro a quadro |
| Texto que é parte da obra é permitido e fica registrado | "sem texto" num retrato com legenda pintada | `usage_notes` e outline dizem qual texto aparece |
| Página de livro mostra só as linhas que a fala cita; o resto da página pode trazer outra versão do texto | recorte de *O Príncipe* com "conto di vivere" logo antes de a fala dizer "vencer" | recorte de três linhas, de "sta dello stato" a "si guarda al fine. Facci", sem a linha do "vivere" |
| O registro descreve tudo o que a imagem mostra: carimbos, cota, ilustração, número de página | página de rosto de 1550 registrada como "só o título", com xilogravura e dois carimbos de posse | `usage_notes` lista o retrato em xilogravura, os carimbos e a cota |

## Quadros da obra (`Citacao`, emenda da ADR 007)

- **Fonte:** só canal oficial do detentor ou da distribuidora licenciada (VIZ, Crunchyroll). O `usage_notes` diz qual
  foi, por quê, e que o trailer não identifica o episódio.
- **Download:** o YouTube pede login. Use os cookies só com o consentimento do dono naquela sessão:
  - copie o `cookies.txt` (fora do Git) para uma cópia com `chmod 600`;
  - nunca mostre o conteúdo;
  - apague a cópia ao terminar, com sucesso ou falha.
  - **yt-dlp:** precisa de uma versão recente com `--js-runtimes node`; a versão antiga falha com "The page needs to
    be reloaded".
- **Achar o quadro:** baixe em 360p para a varredura, faça a folha de cortes (`decupagem.py` da skill
  `analise-de-formato`) e depois baixe em 1080p só o trecho do quadro (`--download-sections`).
- **Crédito:** escolha quadro sem a marca do canal. Não recorte a marca para tirá-la. O crédito da obra vai no
  rodapé e em `credits.txt`.
- **Movimento:** quadro parado (`motion: still`).
- **Limites:** até 10 quadros por vídeo e até 8 s cada (o `vp check` conta). A miniatura com quadro é decisão do dono
  no gate 4.
- **Registro:** `provider: official`, `license_id: Citacao`, `work`, `provider_id: "youtube:<id>@<segundos>s"`.

## Ferramentas desta pasta

- `folhas.py <episódio>`: uma folha por pedido em `candidatos/galeria/<pedido>.jpg`, com as miniaturas numeradas e a
  duração, e a lista de ids na mesma ordem (`<pedido>.ids.json`).
- `conferencia.py <video.mp4> <saida.jpg> [--quadros 8]`: quadros espaçados do vídeo inteiro numa faixa, para a
  conferência de pessoas, marcas e texto.

Os dois usam só o ffmpeg. Rode com `python3 -I`.
