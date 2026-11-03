# Produzir "como as coisas são feitas" e histórias de marcas com os visuais atuais

Consulta: 01/11/2026. Continuação da rodada de [panorama.md](panorama.md): a pergunta que ficou aberta era se os
dois sinais mais próximos do MCP (fabricação de produto conhecido; história de marca) cabem nos planos e nos
ativos que o pipeline já tem. Análise de viabilidade, sem medir demanda; nada foi produzido, baixado ou agendado.

## Conclusão

- **Como é feito:** cabe nos planos atuais **se o vídeo for diagrama do processo, não filmagem da fábrica**.
  O gargalo é o ativo real: imagens de linha de produção são, em geral, do fabricante ou de terceiros,
  sem licença da lista fechada da ADR 007. O vídeo de referência (Dentro das Fábricas, marcado como IA) mostra o
  que a demanda pede visualmente, e é justamente o que não podemos copiar nem imitar como "registro".
- **História de marca:** é o caminho de menor risco, porque reaproveita o molde de perfil de poder
  (`docs/pesquisa/modelo-perfil-de-poder.md`) e os planos que o Votorantim já exercitou. Pede escolher uma marca
  com documentação pública suficiente antes de prometer título.
- **Recomendação (julgamento editorial):** se for testar fora de filosofia, começar por **marca**, e deixar
  "como é feito" para um produto cujo processo tenha fonte técnica aberta (norma, patente expirada, relatório
  de órgão, material educativo com licença) e que se explique em etapas.

## Planos que já existem e o que cada um faria

Fonte: `app/pipeline/models/*_shot.py`.

| Necessidade do vídeo | Plano existente | Observação |
|---|---|---|
| Etapas de um processo, uma depois da outra | `network` com `layout: layered` (entra no ritmo da narração) | Mais próximo de "fluxo de blocos e setas". Nós e arestas precisam de claim com fonte. |
| Antes/depois, escala | `compare` (`before_after`, `scale`) | Serve para tamanho de lote, quantidade, preço por unidade. |
| Evolução de uma marca | `timeline`, `chart` (`line`, `share`) | Faturamento e participação só com dado de fonte; interessada (empresa) confrontada. |
| Onde fica / expansão | `map` (region/world) | Mapa Natural Earth em domínio público. |
| Números e contas | `number`, `calculation`, `receipt` | `calculation` e `receipt` hoje são do vertical (Reels); no longo, `number` e `chart`. |
| Citação, documento, manchete | `quote` (`headline`, `document`) | Recriado como tipografia, nunca print. |
| Ambiente e textura | `broll`, `photo` (Pexels/Pixabay/Unsplash) | Ilustração, nunca registro do fato (§2.4). Sem pessoa reconhecível, marca, logo ou texto. |
| Pessoas/família | `family_tree`, `lower_third` | Úteis em história de marca e dono. |

## Lacunas concretas

1. **O kit já tem esteira e fluxo, o template do longo não os expõe** (verificado em 01/11/2026 pelo MCP
   `motion-kit` e no tarball):
   - `Pipeline` (esteira de estágios com itens correndo; `rejectRatio` derruba uma fração em cada estágio): cena
     JSON `pipeline` no `motion-video`; exportado em `@viniciusk/motion-kit` **0.7.1**, a versão que `video/` instala.
   - `FlowDiagram` (nós com estado e dados viajando pelas setas): cena JSON `flow`; **não está no 0.7.1**
     (o subpacote `graph` do tarball só tem o `ExpandingNetwork`). O checkout em `~/projetos/motion-kit` está na
     0.7.3. Se está nela, usar exige subir o pin (ADR 027) e passar pelo vídeo-régua.
   - Nenhum dos dois aparece em `video/src` nem entre os `kind` de plano de `app/pipeline/models/`. Hoje só o
     `motion-video` do kit (usado nos Shorts técnicos, como `short-concorrencia-fluxo-pt`) os renderiza.
   - Mesmo com `Pipeline`, ela mostra etapas e itens genéricos fluindo, não a matéria-prima virando produto.
     É boa para "etapas de um processo", não para "como a fábrica transforma X".
   - Caminhos: (a) usar o `network` layered que já temos; (b) novo `kind` `pipeline` no schema e no template
     (mudança de contrato de plano + régua); (c) fazer o vídeo no `motion-video` do kit, como os Shorts.
2. **Ativo de fábrica é o ponto frágil.** Fotos de linha de produção e de fábrica quase sempre pertencem à
   empresa. Material do site oficial não é licença (nota de direitos, item 3). Alternativas: banco de imagem
   genérico como ambiente, ilustração gerada (Workers AI, máx. 12 por episódio, divulgada) ou diagrama original.
3. **Fonte do processo.** A regra da claim com `source_ids` vale para cada etapa do diagrama. Processo industrial
   específico de uma marca costuma ser segredo ou só descrito pela própria empresa (fonte interessada). Um produto
   genérico (como se faz pão de queijo industrial, por exemplo) tem mais chance de fonte técnica independente,
   mas isso é hipótese, não verificado.
4. **Risco do YPP.** O formato "explicação em diagrama + narração" se aproxima de "apresentação de slides com pouco
   valor narrativo" se cada episódio for só uma sequência de caixas. Defesa já prevista: pesquisa própria, pergunta
   com tensão (não só "como é"), variação de estrutura entre episódios.

## Caminho 1 testado: o `network` em camadas como fluxo de processo

Validação só de schema, com quatro etapas genéricas ("Etapa 1..4"), sem conteúdo de episódio e sem render:
`NetworkShot` com `layout: layered`, nós `kind: other`, uma aresta por passada e um `step` por etapa **passa**.

- **Funciona:** as etapas entram no ritmo da narração (`steps` com âncora) e o template já usa `layeredLayout`
  (`video/src/Editorial.tsx`). Cada aresta exige `claims` com `source_ids`: cada transição do processo sai
  sustentada por fonte, o que combina com a regra §2.2.
- **Limites:** o tipo de nó foi pensado para pessoas e instituições (`person`, `company`, `bank`, `government`,
  `family`, `other`); `other` cai num ícone genérico (círculo) e o roteiro não escolhe ícone. Então etapa de
  fábrica vira caixa com círculo, sem imagem do que ela faz. `flow: true` na aresta quer dizer "dinheiro correndo",
  não matéria correndo, e não deve ser usado para o processo.
- **Não foi renderizado.** Falta ver se o resultado é legível com 5–8 etapas; isso pede um render de teste,
  que só faço se o dono pedir.

## Teste mínimo sugerido (para o dono decidir)

Não é pauta aprovada. Duas perguntas por linha, cada uma já formulável como pergunta de vídeo:

- **Marca:** "O que aconteceu com a Mesbla?" (já listada em [alternativas.md](alternativas.md)); precisa de fontes
  societárias e de jornal de época, e o Hemeroteca Digital deu HTTP 403 para a ferramenta. Pode exigir download
  manual pelo dono.
- **Processo:** um produto cotidiano com fonte técnica aberta, escolhido depois de levantar fontes. Não escolhi
  nenhum: citar um aqui seria fato de memória.

Para qualquer um, os passos do fluxo normal seguem: pauta com título provisório e conceito de capa, hipótese
com variável e medida, `vp briefs formato`/`analise-de-formato` do nicho novo, fontes, gate 1.

## Decisões que são do dono

1. Fora de filosofia no Cena e Conceito ou em canal separado (ver [publicacao.md](publicacao.md)).
2. Marca ou processo como primeiro teste.
3. Se aceita um componente novo de "processo" no template (passa pelo vídeo-régua) ou fica só com os planos atuais.

## Lacunas desta nota

Não assisti aos vídeos de referência, não consultei o motion-kit por componente de fluxo e não verifiquei
disponibilidade de fontes para nenhuma marca ou produto. As views citadas vêm do panorama (MCP, via coordenação).
