# Spec: gaps de montagem JSON para Cena e Conceito

- **Estado:** rascunho para análise do dono, 2026-10-24. Não aprova novos planos, campos, componentes ou mudanças editoriais.
- **Direção vigente:** [ADR 033](../decisions/033-montagem-json-no-auto-play.md): JSON primeiro no auto-play; reutilizar antes de ampliar; prova curta antes de extrair algo para o kit.
- **Entrega desta rodada:** diagnóstico documental. Sem implementação, render, download, voz, alteração de episódios, dependências, gates ou criação de issues.
- **Evidência:** [F] confirmado na fonte; [I] interpretação/proposta; [H] hipótese a validar em prova. Limitação confirmada não significa necessidade aprovada.

## 1. Problema e resultado esperado

O auto-play já usa o motion-kit. A pergunta não é como conectar os projetos, mas quais apresentações úteis ainda exigem editar o template React e quais já podem ser montadas apenas com dados.

**Resultado pretendido [I]:** montar uma apresentação uma vez e reutilizá-la com outro conteúdo pelo JSON, sem novo ajuste de TSX, dentro de limites visuais e editoriais explícitos. Se os planos atuais atenderem, a entrega pode ser apenas uma receita verificada. Não é obrigatório criar componente ou campo novo.

**Recorte fornecido pelo dono:** ensaios de aproximadamente 12 minutos, pt-BR, horizontal, para público sem formação em filosofia; pensador ou ideia como assunto principal e anime como caso da explicação. A duração é contexto editorial, não duração obrigatória do piloto.

Três candidatos, não três tipos novos aprovados:

1. Apresentação de pensador com retrato e identificação.
2. Imagem comentada, com comentário e indicação de fonte.
3. Comparação textual entre dois conceitos.

## 2. Skills utilizadas e limites da análise

| Skill/referência local | Aplicação nesta spec | O que não foi executado |
|---|---|---|
| [componentes-do-kit](../../.claude/skills/componentes-do-kit/SKILL.md) | Conferir componente atual, API e versão instalada antes de declarar falta de recurso | MCP específico do kit indisponível nesta sessão; aplicado o fallback de leitura de fontes/tipos |
| [vp-roteiro](../../.agents/skills/vp-roteiro/SKILL.md), [roteiro-explicativo](../../.claude/skills/roteiro-explicativo/SKILL.md) e [planos](../../.claude/skills/roteiro-explicativo/planos.md) | Distinguir intenção da cena, plano suportado, afirmação e âncora; respeitar sentido do texto | Nenhum roteiro, tese ou objetivo editorial de episódio foi escrito |
| [plano-de-imagens](../../.claude/skills/plano-de-imagens/SKILL.md) | Separar retratado, personagem, ilustração, evidência e crédito; não prometer direitos por escolher layout | Sem seleção, busca, download ou aprovação de ativos |
| [analise-de-formato](../../.agents/skills/analise-de-formato/SKILL.md) | Separar medida, leitura e recomendação; reconhecer o recorte `pensador` e o uso de partitura existente | Sem coleta, medição de nicho, execução de scripts ou inferência de desempenho |
| [vp-checagem](../../.agents/skills/vp-checagem/SKILL.md) e [checagem](../../.claude/skills/checagem/SKILL.md) | Revisão independente das afirmações da spec contra a fonte, com cobertura e limitações declaradas | Não é checagem factual de episódio nem parecer de gate editorial |

As skills foram lidas e seus critérios pertinentes aplicados à análise técnica. Não se declara execução completa de workflows editoriais sem pauta, fichas, episódio e gates correspondentes.

**Descoberta [F]:** índice `home-viniciusk-projetos-auto-play`, geração `2026-10-15T02:18:44Z`. A consulta estrutural retornou erro de exclusividade entre `query` e `semantic_query`; a cobertura marcou como alterados schemas, adapter e arquivos principais do template. Usou-se leitura direta desses arquivos. O diagnóstico é dirigido aos três casos, não auditoria exaustiva do repositório.

## 3. Arquitetura e versão realmente consumida

```text
scenes.json -- contrato editorial Python
    -> produção: mídia, áudio, atribuição e tempos
    -> episode.json -- dados resolvidos
    -> adapter Remotion
    -> props JSON por cena -- contrato do template
    -> React: Scene / ShotView / Editorial
    -> componentes do motion-kit por props React/TypeScript
    -> Remotion: segmentos -> ffmpeg: montagem com áudio
```

**Não há dois serviços trocando JSON [F].** O kit é uma dependência instalada dentro do template. O contrato editorial pertence ao auto-play; a biblioteca tem APIs React genéricas. A representação intermediária de props já existe e não precisa virar outro protocolo.

- [F] O pin é `file:vendor/viniciusk-motion-kit-0.7.1.tgz`: [video/package.json](../../video/package.json#L18). As declarações instaladas confirmam as APIs citadas abaixo.
- [F] A [ADR 027](../decisions/027-motion-kit-por-tarball-versionado.md) estabelece tarball versionado e conferência dos tipos instalados. Consultar o checkout vizinho não certifica compatibilidade; mesmo número de versão não substitui comparação das APIs/artefatos usados.
- [F] O adapter está em [app/render/remotion.py](../../app/render/remotion.py#L176); converte inícios de planos em frames e calcula o intervalo até o plano seguinte.
- [F] [shot_bounds](../../app/pipeline/shots.py#L35) resolve âncoras proporcionalmente ao texto sobre a duração do áudio, considerando pausas. Isso não é alinhamento exato de palavras.
- [F] A fonte do plano vem das suas claims em [episode_shots](../../app/pipeline/shots.py#L68); crédito do ativo e conversão de passos são tratados no [adapter](../../app/render/remotion.py#L61). Não são o mesmo dado.

## 4. Recursos que já atendem parte do recorte

| Caso | Alternativa existente [F] | Limite ou cuidado |
|---|---|---|
| Retrato + identificação | `photo` seguido de `lower_third`; a própria skill já recomenda essa montagem | Foto persiste até a próxima mídia/fim da cena; conferir identificação, rosto, legenda, crédito e fonte juntos |
| Imagem + frase comentada | `photo` seguido de `keyword`, com claims próprias quando o comentário deve exibir sua fonte | Frase literal da narração, até 8 palavras; não confundir com comentário independente |
| Comparação de conceitos | `compare`, preferencialmente `side` para o piloto, com `value` e `label` textuais | Comparação textual existe no template local; `ValueCompare` não é necessário para esse ramo |
| Fonte e crédito | `SourceTag` para fonte factual; crédito separado no cartão arquivístico | Fonte não é herdada automaticamente das claims da cena; `StockShot` não recebe o crédito na assinatura atual |
| Prévia parcial | `render-stills.mjs`, `render-scenes.mjs` e comparação pelo vídeo-régua | Render estruturalmente válido não comprova legibilidade nem fidelidade editorial |

Evidências: [regras de camadas](../../video/src/Scene.tsx#L20), [despacho de planos](../../video/src/ShotView.tsx#L126), [foto/crédito e stock](../../video/src/Editorial.tsx#L51), [comparação textual](../../video/src/Editorial.tsx#L157), [receita do roteirista](../../.claude/skills/roteiro-explicativo/SKILL.md#L98).

**Kit disponível, integração não equivalente no JSON [F]:** os tipos instalados em `video/node_modules/@viniciusk/motion-kit/dist/` expõem `CutoutPortrait` e `Highlighter` em `editorial/index.d.ts`, `Pane`/`SplitScreen` na raiz e `FitText` em `i18n/index.d.ts`. `KineticHeadline` oferece `wordFrames`, `exitAt`, piso tipográfico e `onOverflow`. Os specs de foto/keyword e wrappers atuais não expõem toda essa superfície. Isso é subconjunto deliberado, não defeito por si só. `CutoutPortrait` pressupõe imagem recortada; não remove fundo.

## 5. Mapa dos gaps

### G01. Comentário independente não é `keyword`

- **Classe:** limitação confirmada de contrato; necessidade editorial pendente.
- **Problema [F]:** `keyword` não expressa anotação livre ou parágrafo independente. [KeywordShot](../../app/pipeline/schemas.py#L491) limita a 8 palavras e [Scene._visual_plan](../../app/pipeline/schemas.py#L773) exige presença na narração. `quote` tem outra semântica: não deve virar comentário autoral disfarçado de citação.
- **Benefício esperado [H]:** reutilizar imagem comentada sem reescrever React ou deformar a narração para caber no plano.
- **Alternativa atual:** resumir usando trecho fiel da fala; se for citação real, usar `quote` no seu formato próprio. Essas alternativas podem bastar.
- **Responsável:** auto-play define significado e suporte factual; template monta com peças existentes. Nenhum componente novo do kit demonstrado.
- **Menor prova:** comparar uma imagem com frase literal curta e um pedido de comentário independente, ambos sintéticos. Documentar a diferença antes de desenhar campos.
- **Aceite observável:** ou a receita atual atende, ou o dono confirma a necessidade que ela não expressa. Se houver implementação futura, uma segunda troca de conteúdo usa somente JSON, sem quebrar as regras atuais de `keyword`.
- **Dependências/riscos:** decidir G01 não autoriza novo plano. Comentário pode acrescentar afirmação não dita; definir evidência, atribuição e tempo de leitura antes de integrá-lo.

### G02. Disposição lateral de imagem e comentário não é selecionável no recorte atual

- **Classe:** limite confirmado de integração/layout; utilidade ainda hipotética.
- **Problema [F]:** [PhotoSpec/KeywordSpec](../../video/src/types.ts#L8) não oferecem opção lateral; [ArchivalShot](../../video/src/Editorial.tsx#L55) centraliza cartão e [KeywordShot](../../video/src/Editorial.tsx#L379) usa frase com véu sobre a mídia. O JSON não seleciona a montagem imagem à esquerda/comentário à direita.
- **Benefício esperado [H]:** preservar a região importante da imagem e permitir leitura sem sobreposição.
- **Alternativa atual:** overlay existente; prova local em React com flex ou `Pane`/`SplitScreen` se o overlay falhar. Não precisa extrair API pública para testar.
- **Responsável:** template do auto-play; kit somente se surgir falta genérica reproduzível.
- **Menor prova:** mesma imagem e texto em overlay e montagem lateral, sem novos assets nem estilo visual. Usar texto curto primeiro para não confundir geometria com G01.
- **Aceite observável:** imagem relevante, comentário, fonte, crédito e legenda ficam legíveis nas amostras e no trecho; trocar conteúdo não exige reposicionamento manual. Registrar também se overlay já basta.
- **Dependências/riscos:** política de legenda/Host, proporção da imagem e fonte mínima. `Pane` não reduz tipografia automaticamente. Não propor engine de colisão ou coordenadas arbitrárias em JSON.

### G03. Comparação textual tem diagnóstico incompleto de tamanho

- **Classe:** gap confirmado de validação; falha visual ainda não medida.
- **Problema [F]:** [CompareSide](../../app/pipeline/schemas.py#L396) aceita strings; [CompareShot](../../video/src/Editorial.tsx#L185) usa tipografia fixa no ramo textual. [text_fit_warnings](../../app/pipeline/text_fit.py#L58) verifica `label`, não `value`. Uma definição longa pode passar por esses checks e ficar ruim no quadro [H].
- **Benefício esperado [H]:** identificar conteúdo excessivo antes de ajustar/renderizar repetidamente.
- **Alternativa atual:** conceitos curtos, explicação na narração e revisão humana; avaliar `FitText` com piso e diagnóstico antes de inventar medidor ou encolhimento próprios.
- **Responsável:** auto-play para aviso por campo e apresentação do ramo textual. Mudança no kit só se `FitText` revelar limitação genérica.
- **Menor prova:** dois termos curtos e uma comparação assimétrica com definição longa, em pt-BR; medir ambos os `value` e `label`.
- **Aceite observável:** conteúdo curto permanece igual; excesso do caso longo é identificado com cena/campo e não é ocultado por corte ou fonte ilegível. Escolher limites depois da medição, não nesta spec.
- **Dependências/riscos:** fonte carregada, tamanho final e prévia. Não usar `scale` para conceitos; preservar ramo numérico e comportamento dos planos existentes.

### G04. Controle temporal do kit não é todo exposto pelo consumidor

- **Classe:** capacidade existente no kit, integração seletiva; demanda pendente.
- **Problema [F]:** [KeywordSpec](../../video/src/types.ts#L66) contém texto/destaque, enquanto [KeywordShot](../../video/src/Editorial.tsx#L379) fixa `at={4}`. A API instalada de `KineticHeadline` aceita `wordFrames` e `exitAt`; o contrato atual não os oferece nesse plano.
- **Alternativa atual:** duração do plano, `Sequence` e entradas padrão. Já existe `stepFrames` para outros tipos; não é correto dizer que o auto-play não tem controle temporal.
- **Responsável:** auto-play resolve relógio e âncoras; kit anima com frames recebidos. Não colocar alinhador de áudio na biblioteca.
- **Menor prova:** somente se o piloto exigir, definir entrada, permanência e saída em tempos conhecidos e testar antes/no/depois dos limites. Pode começar em props de teste, sem aprovar campos de autoria.
- **Aceite observável:** a mudança temporal necessária é reproduzível ao buscar frames isolados, não corta leitura nem altera os padrões de planos não optantes.
- **Dependências/riscos:** decidir necessidade real; não passar âncoras para o kit. Relógios local/global, arredondamento e duração insuficiente precisam de teste. Alinhamento preciso é trabalho relacionado, não pré-requisito para a prova visual.

### G05. Descoberta e compatibilidade precisam de recorte por receita

- **Classe:** documentação/descoberta; não ausência de componente.
- **Problema [F]:** [planos.md](../../.claude/skills/roteiro-explicativo/planos.md#L6) ilustra `compare` com números, embora o ramo textual exista. A receita retrato+tarja já está na skill. [componentes-do-kit](../../.claude/skills/componentes-do-kit/SKILL.md#L39) manda cruzar a instalação, mas ainda cita caminhos antigos `src/` do checkout; o monorepo usa `packages/motion-kit/src/`.
- **Alternativa atual:** consultar schemas, wrappers e tipos instalados; usar a receita existente em vez de criar outra.
- **Responsável:** auto-play documenta seu subconjunto e exemplos; kit documenta a API genérica. Não alterar skills nesta rodada.
- **Menor prova:** três fichas de receita com plano, campos, import usado, versão, formato, limites e comando de revisão; outra pessoa deve conseguir identificar a montagem correta.
- **Aceite observável:** distinguir disponível no pacote, exposto no JSON e apenas proposto. Incluir comparação textual e a diferença entre comentário e citação, sem prometer todas as props do kit.
- **Dependências/riscos:** confirmar exports instalados na integração. Tipos legíveis no checkout ou versões nominalmente iguais não bastam; exemplos antigos não são prova de estado atual.

### H01. Convivência das camadas precisa de prova, não de plataforma nova

- **Classe:** hipótese visual com histórico de ajuste, não falha geral comprovada.
- **Evidência [F]:** [ArchivalShot](../../video/src/Editorial.tsx#L51) move o crédito acima da foto porque outras camadas o cobriam; [Scene](../../video/src/Scene.tsx#L72) posiciona fonte, legenda e Host separadamente. Já há soluções locais.
- **Alternativa/responsável:** reservas explícitas no template do auto-play. Safe area do kit não certifica ausência de colisões editoriais.
- **Prova/aceite:** revisar os três casos com legenda e, se necessário, Host de teste autorizado; registrar colisões específicas ou ausência delas. Não esconder fonte/crédito para fazer caber.
- **Dependências/riscos:** definição de ocupantes, títulos longos e política final de legenda. Somente colisão reproduzida justifica ajuste; não abrir uma frente de layout automático por antecipação.

## 6. Responsabilidades e manutenção

| Camada | Responsabilidade | Limite |
|---|---|---|
| Contrato Python do auto-play | Conteúdo, intenção, claims, ativos, âncoras e combinações suportadas | Não ser linguagem de CSS, árvore React ou import dinâmico |
| Produção e adapter | Resolver mídia/áudio/tempos e converter para props JSON | Não transferir resolução de âncora ao kit |
| Tipos TS e template | Interpretar o subconjunto aceito, escolher peças e reservar regiões | Não supor que todo componente público já é opção do roteiro |
| motion-kit | Props React, geometria/animação genéricas, tipos e exemplos | Não conhecer fichas, direitos, canais, gates ou o contrato editorial |
| Revisão | Verificar estrutura, quadros e movimento; dono decide o aceite editorial | Não confundir render bem-sucedido com aprovação |

Regras propostas [I]: manter montagem local primeiro; variante pequena quando só muda apresentação; tipo novo somente se a semântica exigir; defaults atuais preservados. Toda ampliação precisa atravessar schema Python, TS, adapter, template, checks, testes e documentação pertinentes, sem criar camadas desnecessárias. Uma capacidade inexistente no kit exige avaliação nele; uma combinação de capacidades existentes pode permanecer no consumidor.

Não criar framework de receitas, registry de layouts, contrato espelhado no kit, serviço, novo renderer ou editor visual. Não migrar para motion-video, criar novos estilos ou alterar episódios aprovados. Extrair composição pública somente após reuso demonstrado, com API menor que a regra editorial do consumidor.

## 7. Piloto e evidências de aceite

**Proposta, ainda não executada:** três cenas independentes de aproximadamente 10 a 15 segundos, com variante curta e longa. Duração ajustável à leitura; não estimar duração real da fala como se fosse medida. Usar imagem original de teste, identificação explicitamente fictícia e conceitos A/B sem atribuições filosóficas reais. Fontes/claims da fixture devem apontar para material sintético local identificável, sem apresentar IDs inventados como evidência de autor real.

| Caso | Base sem ampliar contrato | Variante de investigação | Registro esperado |
|---|---|---|---|
| P1: retrato | `photo` + `lower_third` | Nome/cargo maior; imagem vertical num quadro horizontal | Enquadramento, crédito, fonte e leitura da identificação |
| P2: comentário | `photo` + `keyword` literal curto | Geometria lateral em prova TSX; comentário livre só se D01 confirmar | Separar falta semântica G01 de falta geométrica G02 |
| P3: conceitos | `compare.side` com termos não numéricos | `value` longo de um lado e labels assimétricos | Se schema/check avisam, dimensões observadas e correção mínima |

Para cada variante: conferir antes da entrada, durante o movimento, estado de leitura e saída; assistir ao trecho. Fixar a proposta de fonte mínima e tamanho de visualização antes da comparação e registrar o valor escolhido. Se fontes/legendas ocuparem a tela no produto-alvo, incluir essa ocupação na prova. Sem revisão visual não declarar ausência de colisão.

Ferramentas existentes, comandos futuros a partir de `video/`:

```bash
node render-stills.mjs /caminho/absoluto/pedido-quadros.json
node render-scenes.mjs /caminho/absoluto/pedido-trechos.json
```

[Quadros](../../video/render-stills.mjs): pedido `{publicDir, jobs:[{out, frame, props}]}`, `props` de `SceneProps`. [Trechos](../../video/render-scenes.mjs): `{publicDir, crf, x264Preset, jpegQuality, concurrency, timeoutMs?, jobs:[{out, props}]}`. Preparar pedidos com caminhos locais de teste e props oriundas do adapter quando se validar a integração completa. Prova manual de props/TSX, sozinha, não valida o caminho desde `scenes.json`.

Os trechos desse script são mudos. Se avaliar sincronismo com fala, usar áudio de teste já autorizado e a montagem existente; não gerar voz nem chamar provedor automaticamente. Não usar `npm run render` como atalho verificado: o script atual aponta para `Episode`, enquanto os pedidos acima selecionam suas composições explicitamente. Para mudanças futuras de visual, comparar com o vídeo-régua sem sobrescrever sua base/aprovações; sonda de CPU antes de render longo.

## 8. Sequência pequena e esforço para discussão

1. **Descoberta utilizável:** decidir o significado do comentário, registrar as três receitas e a versão instalada. Aceite: saber montar P1/P3 e a base de P2 sem alterar TSX. Útil sem concluir as demais etapas.
2. **Prova visual:** executar P1 a P3 com variantes e registrar limites. Aceite: cada gap recebe `atende`, `precisa de ajuste` ou `adiado`, com evidência; nenhum campo novo só porque existe no kit.
3. **Implementação condicional:** selecionar um impedimento, começando por ajuste local/API existente. Aceite: caso falho passa, defaults permanecem e não se enfraquecem regras de `keyword`/`quote`.
4. **Integração condicional:** levar apenas a capacidade aprovada pelo schema, tipos e adapter até o template. Aceite: segundo conteúdo percorre o fluxo real sem TSX novo, preservando fonte/crédito e tempos.
5. **Regressão:** testes de contrato/props e revisão da régua. Aceite: mudanças visuais intencionais discriminadas e nenhuma alteração incidental nos planos existentes; publicação de pacote só em trabalho futuro autorizado.

Estimativas de planejamento [I], não baseline: descoberta 1-2 h, piloto 3-5 h e revisão 2-4 h; primeiro ponto de decisão em **6-11 h focadas**. Conclusão com ajustes pequenos, testes e receitas: **12-22 h totais**, incluindo a prova. Comentário livre com ampliação de contrato pode acrescentar **6-12 h**; reestimar após a prova, sem somar automaticamente opções compartilhadas. Não inclui pesquisa, roteiro de 12 min, produção de ativos, voz, espera de máquina nem extração pública no kit.

Medições futuras: tempo até primeira prévia útil, ajustes manuais, correções após prévia e número/motivo de edições de TSX ao trocar conteúdo. Registrar esforço inicial separado do reuso; comparar tarefas equivalentes e não prometer redução nem ganho de audiência.

## 9. Decisões pendentes do dono

| ID | Pergunta | Consequência |
|---|---|---|
| D01 | Comentário é trecho curto da fala, paráfrase independente ou citação literal? | Define se G01 é necessidade e como verificar suporte; não escolher novo `kind` antes disso |
| D02 | Overlay basta ou há necessidade de imagem/texto lado a lado? | G02 só vira implementação se a prova justificar |
| D03 | O horizontal final terá legenda queimada e apresentador? | Define ocupação real a testar; não mudar a política atual nesta spec |
| D04 | O retrato comum atende ou precisa ser recortado? | Se recortado, reutilizar `CutoutPortrait` e trabalho existente; direitos/derivação continuam fora do kit |
| D05 | Como reconciliar o recorte `pensador/ideia` com a orientação anterior centrada no espectador? | Questão editorial/documental, não componente novo |

**D05 em detalhe [F]:** a seção [Ensaio com obra de ficção](../../.claude/skills/roteiro-explicativo/SKILL.md#L191) diz que o assunto é quem assiste; a skill [analise-de-formato](../../.agents/skills/analise-de-formato/SKILL.md#L160) já reconhece `--assunto pensador`. O pedido atual define pensador/ideia como principal para esta spec e prevalece no seu recorte. Falta confirmar se isso vira orientação geral ou variante explícita nas skills; não reescrever a regra anterior nem transplantar o perfil de poder para todo ensaio.

## 10. Trabalho relacionado, sem duplicação

| Trabalho | Relação com esta spec |
|---|---|
| [auto-play #117](https://github.com/ViniciusKoiti/video-pipeline/issues/117) | Inventário de APIs, pin e integração: reaproveitar no recorte de G05 |
| [auto-play #121](https://github.com/ViniciusKoiti/video-pipeline/issues/121) | Protocolo de revisão visual: aplicar ao piloto, não recriar ferramenta |
| [auto-play #82](https://github.com/ViniciusKoiti/video-pipeline/issues/82) | Retrato recortado: somente se D04 exigir |
| [auto-play #127](https://github.com/ViniciusKoiti/video-pipeline/issues/127) | Variantes de dados condicionais: não confundir com falta de comparação textual básica |
| [auto-play #198](https://github.com/ViniciusKoiti/video-pipeline/issues/198) | Tempos de palavras: coordenação futura, sem bloquear prova geométrica |
| [motion-kit #13](https://gitlab.com/ViniciusKoiti/motion-kit/-/issues/13) | Extração de templates após uso: relacionada, não exige extração nesta spec |

Vínculos são referências de escopo, não certificação de conclusão ou nova consulta de status nesta rodada. Esta spec não cria nem altera issues, não substitui a ADR 033 e não aprova implementar todos os gaps.

## 11. Critério de fechamento desta análise

- [ ] Dono analisa D01-D05; decisões não necessárias à primeira prova podem permanecer adiadas.
- [ ] Cada caso tem alternativa atual e limite identificado, sem declarar componente ausente por falha de busca.
- [ ] Prova futura registra conteúdo, versão, props, formato, frames/trecho, revisão e correções; sem baseline inventado.
- [ ] Somente gaps demonstrados viram escopo de implementação; layout/controle genérico vai para o kit apenas se reutilização justificar.

**Verificação desta rodada:** leitura dirigida das skills, contrato, adapter, template, ferramentas de revisão e tipos instalados; conferência de cobertura do índice com fallback de fonte. Não houve testes de runtime, render ou revisão de imagens/vídeos. A validade visual permanece pendente.

Revisão independente em contexto separado, aplicando os critérios de `vp-checagem`/`checagem` à spec técnica: sem achados materiais nas afirmações conferidas, sem aprovação de gate. Verificação automática: 38 referências locais com caminhos e linhas válidos; `git diff --no-index --check` sem erros de whitespace. Links remotos e estado atual das issues não foram revalidados nesta rodada.
