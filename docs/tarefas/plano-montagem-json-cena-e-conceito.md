# Plano de implementação: montagem JSON no auto-play

- **Estado:** plano para refinamento do dono, 2026-10-24. O pedido autoriza escrever o plano, não executar suas etapas nem aprovar decisões pendentes.
- **Base:** [spec de gaps](../specs/montagem-json-cena-e-conceito.md), [ADR 033](../decisions/033-montagem-json-no-auto-play.md) e [ADR 027](../decisions/027-motion-kit-por-tarball-versionado.md).
- **Plano complementar:** [motion-kit: composições narradas](../../../motion-kit/docs/plano-composicoes-narradas.md). Link de workspace; não implica documento publicado no remoto.
- **Objetivo:** repetir os três casos do Cena e Conceito trocando dados, sem editar TSX a cada conteúdo, preservando atribuição, leitura e comportamento existente.

## 1. Escopo e resultado mínimo

Horizontal, pt-BR, público leigo; pensador/ideia como assunto e anime como caso. O vídeo futuro pode ter aproximadamente 12 minutos; a primeira prova usa cenas curtas e não produz um episódio completo.

A entrega mínima é uma receita verificada de `photo → lower_third`, `photo → keyword` e `compare.side` textual. Se isso atender, não se exige ampliar o contrato nem alterar o kit. A capacidade prioritária de investigação é imagem comentada: distinguir comentário literal curto, comentário independente e disposição lateral antes de escolher implementação.

**Fora de escopo:** interpretador de React/CSS em JSON, registry de layouts, editor visual, renderizador paralelo, migração para motion-video, novos estilos, alinhador de voz novo, mudanças em episódios aprovados e aquisição de ativos. Claims, direitos, gates, tese e tempos continuam no auto-play.

Os códigos `AP-Cxx` abaixo identificam etapas deste documento; não são issues criadas.

## 2. Ordem e dependências

```text
AP-C01: receitas, compatibilidade e decisões
    -> AP-C02: prova visual com o pacote instalado
        -> resultado: atende / ajuste local / necessidade genérica / adiado
        -> AP-C03: comparação textual, somente se necessário
        -> AP-C04: imagem comentada, somente se necessária
        -> AP-C05: controles temporais, somente se necessários
    -> AP-C06: integração, documentação e regressão do recorte selecionado

Necessidade genérica reproduzida
    -> avaliação no plano do motion-kit
    -> entrega do kit, somente se aprovada
    -> atualização de pacote no AP-C06, somente se necessária
```

AP-C03, AP-C04 e AP-C05 não dependem umas das outras por padrão; cada uma depende da prova e das decisões pertinentes. Trabalhar um impedimento por vez para atribuir mudanças e medir esforço. A descoberta do kit pode ocorrer junto de AP-C01; ela não bloqueia o piloto quando a API instalada já atende.

## 3. AP-C01: fechar receitas e recorte de compatibilidade

**Tipo:** descoberta e decisão. **Gaps:** G05 e decisões D01-D05 da spec.

1. Registrar tarball, integridade no lockfile, versão instalada e imports/props de cada receita. Conferir a API instalada, não só o checkout. Acionar MK-C01 do plano complementar para dúvida de API.
2. Descrever a montagem existente, campos obrigatórios, fonte do plano versus crédito do ativo e limites de conteúdo. Incluir comparação textual, não apenas números.
3. Levar D01-D05 ao dono com o efeito de cada alternativa. Definir primeiro comentário literal/livre, ocupação por legenda/Host e necessidade de layout lateral. Retrato recortado e orientação geral das skills podem ficar adiados sem impedir a base atual.
4. Registrar fonte mínima e tamanho de visualização propostos para a prova antes de compará-la. Não inventar limites finais sem medir.

**Arquivos a consultar:** `video/package.json`, `video/package-lock.json`, tipos instalados, `app/pipeline/schemas.py`, `video/src/{types.ts,Scene.tsx,ShotView.tsx,Editorial.tsx}` e as skills listadas na spec.

**Entrega:** registro curto das três receitas e das decisões, junto ao relatório do piloto; corrigir posteriormente os caminhos antigos da skill `componentes-do-kit`, preservando edições locais do dono.

**Aceite:** outra pessoa identifica como montar os três casos-base e quais opções não são suportadas; nenhuma prop é prometida apenas por existir no checkout. Receita e diagnóstico são úteis mesmo se o restante for adiado.

**Parada:** se comentário literal/overlay bastar, marcar G01/G02 como atendidos no recorte; não desenhar campo novo por antecipação. Sem decisão, avançar somente com a prova-base, sem escolher semântica pelo dono.

## 4. AP-C02: provar os três casos antes de ampliar contratos

**Tipo:** prova visual. **Gaps:** G01-G04 e H01, conforme o caso.

1. Preparar fixture isolada, fora de episódios aprovados, com identificação fictícia, imagem original/autorizada e conceitos A/B. Registrar fontes sintéticas locais de modo verificável; não usar fatos filosóficos ou imagens de anime reais nesta prova.
2. Montar P1 com `photo → lower_third`, P2 com `photo → keyword` literal e P3 com `compare.side` textual; uma variante curta e outra longa/assimétrica para cada caso. Proposta: 10-15 s por cena, ajustável à leitura.
3. Gerar `episode.json` de teste e props pelo adapter para validar a base integrada. Tempos sintéticos devem ser rotulados como teste, não como áudio medido; sincronismo real exige áudio autorizado com duração medida.
4. Revisar quadros antes da entrada, entrada, leitura e saída, além de trechos. Incluir legenda e Host de teste se fizerem parte da ocupação a avaliar, sem usar voz/identidade pessoal.
5. Se a base não atender, comparar uma única mudança por vez. Geometria lateral pode começar em TSX local de teste, com o mesmo texto curto; isso não significa que o JSON já suporte a variante.

**Locais:** usar a organização existente de `tests/fixtures/episodes/` para dados versionáveis; pedidos, props e renders locais em pasta isolada sob `renders/`, respeitando o `.gitignore`. Não versionar outputs de render por padrão. Só criar exemplo TSX temporário/local se a diferença não puder ser provada com o template atual.

**Ferramentas:** `video/render-stills.mjs`, `video/render-scenes.mjs`; formatos dos pedidos constam na spec. O segundo gera trechos mudos. Não usar montador integral que possa gerar voz só para testar layout.

**Entrega:** relatório por caso/variante com entrada usada, versão, dimensões, frames, trecho, problema e menor correção. Classificar cada gap como `atende`, `ajuste local`, `avaliar kit` ou `adiado`.

**Aceite:** saber se trocar conteúdo dispensa TSX e se imagem, identificação, comentário, crédito, fonte e legenda coexistem no recorte testado. Registrar explicitamente as variantes não revisadas e se o sincronismo ficou sem cobertura.

**Parada:** schema válido/render concluído não certifica qualidade. Falha somente de conteúdo retorna ao conteúdo; falha somente de geometria não autoriza comentário livre ou novo tipo editorial.

## 5. AP-C03: diagnosticar excesso na comparação textual

**Tipo:** implementação local condicional. **Gaps:** G03 e H01. **Entrada:** caso de texto excessivo reproduzido no AP-C02 ou necessidade explícita de aviso preventivo aprovada.

1. Criar teste do limite observado em `tests/test_text_fit.py`, distinguindo `value` textual e `label`. Não alterar interpretação numérica nem proibir conceitos curtos já válidos.
2. Acrescentar diagnóstico com cena/campo em `app/pipeline/text_fit.py`; estabelecer limite baseado no layout e prova, não nos exemplos isolados. Aviso aproximado não substitui medição de DOM nem vira erro editorial automático.
3. Se o diagnóstico mostrar que o layout precisa mudar, ajustar apenas o ramo textual de `CompareShot` em `video/src/Editorial.tsx`. Avaliar `FitText` existente, com piso e overflow visível/diagnosticado, antes de escrever outro medidor.
4. Preservar o visual dos casos atuais. Se um novo comportamento de encaixe mudar referências existentes, fazê-lo opt-in ou obter decisão explícita e revisão, em vez de alterar defaults incidentalmente.

**Testes:** `test_text_fit.py`, `test_editorial_shots.py`, `test_number_locale.py`, checks Node existentes e quadros equivalentes curto/longo. Incluir número válido para assegurar que o ramo numérico continua igual.

**Aceite:** excesso identificado sem corte silencioso nem redução ilegível; casos curtos e números existentes preservados; fonte carregada e prévia/final revisados quando a mudança afetar escala. Se encaixe atual bastar, entregar apenas o diagnóstico necessário.

## 6. AP-C04: integrar a apresentação de imagem comentada escolhida

**Tipo:** contrato + template condicionais. **Gaps:** G01/G02/H01. **Entrada:** AP-C02 e decisões D01/D02; D03 para o aceite de convivência.

1. Registrar o que não cabe na receita atual e a opção escolhida. Não enfraquecer `keyword` nem usar `quote` para texto que não seja citação.
2. Definir o menor vocabulário. Se só mudar apresentação, avaliar variante limitada; se mudar semântica, propor tipo específico. **Nome do plano, campos e limites continuam abertos**, não aprovados por este documento.
3. Definir claims/atribuição do comentário, associação com a mídia e duração. Aproveitar o caminho existente de assets e fonte; não criar cópias desses dados no kit. Se mudar contrato persistido, seguir as regras de ADR/schema version do repositório e preservar a leitura dos episódios existentes.
4. Implementar a opção selecionada em `app/pipeline/schemas.py`, `video/src/types.ts` e wrappers/despacho. Alterar `Scene.tsx`, `app/pipeline/shots.py`, atribuição ou adapter somente onde a semântica nova exigir; não duplicar lógica sem necessidade.
5. Para lateral, reservar regiões explícitas de imagem, comentário e ocupantes. Reutilizar React/layout ou `Pane`/`SplitScreen`; sem coordenadas livres, CSS ou árvore de componentes no JSON.
6. Usar crédito e fonte em testes de verdade. Verificar o caminho stock separadamente se escolhido, pois seu wrapper atual não recebe crédito; não supor que uma prop emitida sempre aparece na tela.

**Testes:** `test_editorial_shots.py`, `test_shots.py`, `test_remotion_props.py`, `test_text_fit.py` e testes adicionais mínimos no lugar apropriado. Cobrir válido, campos incompatíveis, comentário sem suporte conforme a regra escolhida, âncora inválida, limites e defaults antigos. Teste semântico não pode ser substituído por prop snapshot.

**Aceite:** duas cenas de conteúdo distinto usam a mesma apresentação só por JSON; fonte/crédito continuam com origem e exibição corretas; imagem legível; nenhum efeito nos planos não optantes. Se a apresentação local atender, não abrir dependência de mudança no kit.

## 7. AP-C05: expor somente o controle temporal necessário

**Tipo:** integração condicional de API existente. **Gap:** G04. **Entrada:** prova de necessidade temporal específica e decisão sobre autoria/resolução desses dados.

1. Definir relógio de cada valor, unidade, intervalos válidos e quem o resolve. Não colocar frames de narração manualmente em `scenes.json` apenas para reproduzir uma prop do kit.
2. Preferir duração/`Sequence` atuais. Se insuficientes, traduzir o controle aprovado para props como `wordFrames`/`exitAt` no template, usando a API instalada e tempos já resolvidos pela produção.
3. Atualizar schema, transformação, tipos e adapter somente para o controle selecionado. Não fazer um passthrough genérico das props do componente nem construir um novo alinhador.
4. Testar antes/no/depois da entrada e saída, plano curto, arredondamento e busca direta de frame. As peças precisam continuar determinísticas sem reproduzir frames anteriores.

**Aceite:** evento necessário acontece no frame resolvido, com tempo de leitura preservado; ausência dos campos mantém comportamento/cache pertinente; nenhum corte de fala ou deslocamento acumulado. Precisão de âncoras de voz é coordenada com #198, não prometida nesta etapa.

## 8. AP-C06: consolidar, integrar pacote se necessário e verificar regressão

**Tipo:** integração no consumidor, documentação e regressão. **Entrada:** AP-C02 e somente as implementações selecionadas, com revisão feita.

1. Completar o caminho de ponta a ponta da fixture: `scenes.json → produção → episode.json → adapter → template`. Registrar quando só foi validado um trecho/props manuais.
2. Se houve entrega no kit, aguardar MK-C04, usar artefato produzido de revisão identificada e seguir ADR 027: build, origem no histórico, tarball versionado, pin/lock e instalação. Atualizar pacote **só se necessário e em execução futura autorizada**; não importar o checkout vizinho ou reutilizar silenciosamente o mesmo nome de tarball para conteúdo diferente.
3. Verificar no pacote instalado os exports e as props exigidas; conferir Remotion/React/peers do consumidor real. O kit e o auto-play têm ambientes de versões diferentes, por isso o teste no kit sozinho não fecha a integração.
4. Atualizar receitas/skills pertinentes: `componentes-do-kit`, `roteiro-explicativo/planos.md`, roteiro e checagem somente no comportamento que mudou. Reconciliar D05 com o dono antes de mudar a regra geral de assunto do ensaio.
5. Executar testes e revisar somente as diferenças esperadas na régua congelada, usando referências/cópias de teste sem sobrescrever episódios e aprovações. Não usar snapshot novo para ocultar regressão.
6. Registrar esforço e cobertura. Aprovada a receita, retirar apenas scaffolding temporário criado nesta entrega que não tenha utilidade de regressão; não remover alterações alheias.

**Comandos de validação futuros, a partir da raiz do auto-play:**

```bash
.venv/bin/python -m pytest tests/test_shots.py tests/test_editorial_shots.py tests/test_remotion_props.py tests/test_text_fit.py tests/test_number_locale.py tests/test_labels_language.py
.venv/bin/ruff check .
npm --prefix video test
```

Executar a suíte offline completa antes de encerrar implementação quando viável. Renders de regressão exigem ambiente disponível, sonda de CPU antes de trabalho longo e um trabalho pesado por vez. Quadros/trechos têm revisão humana declarada; não acionar provedores automaticamente. Testes existentes não certificam todas as novas combinações.

**Aceite final:** três receitas com limites explícitos; segunda troca de conteúdo sem TSX para cada apresentação entregue; testes pertinentes passam; mudanças intencionais discriminadas; nenhuma alteração em episódios aprovados. Se um gap for adiado, declarar o limite em vez de certificar suporte.

## 9. Coordenação, esforço e parada

| Item | Faixa de planejamento | Observação |
|---|---|---|
| AP-C01, incluindo coordenação do inventário MK-C01 | 1-2 h | Usar um único registro, não duplicar levantamento |
| AP-C02: montagem da prova | 3-5 h | Seis variantes curtas, sem produzir ativos externos |
| AP-C02: revisão | 2-4 h | Primeiro ponto de decisão em 6-11 h totais |
| Ajustes pequenos selecionados | 3-6 h | Não comporta todas as frentes condicionais juntas |
| Testes, receitas e fechamento | 3-5 h | Total-base 12-22 h, como na spec |
| Comentário independente com contrato novo | +6-12 h | Reestimar após a prova; não somar mecanicamente trabalho compartilhado |

Faixas não medidas, em horas focadas; não incluem produção editorial de 12 min, voz, ativos, espera de máquina nem mudança pública do kit. Se MK-C01 exigir auditoria adicional, reestimar a descoberta; não somar sua estimativa ao mesmo inventário já contabilizado aqui. Se entrar código no kit, criar previsão própria após o caso mínimo; isso não cabe automaticamente no total-base.

Retornar ao dono se precisar escolher semântica/editorial não decidida, aumentar contrato além da prova, mudar visual padrão ou adicionar dependência. Pode encerrar com receitas e diagnóstico se não houver impedimento; não há quota de componentes novos.

**Vínculos de trabalho existente:** [#117](https://github.com/ViniciusKoiti/video-pipeline/issues/117) inventário; [#121](https://github.com/ViniciusKoiti/video-pipeline/issues/121) revisão; [#82](https://github.com/ViniciusKoiti/video-pipeline/issues/82) recorte; [#198](https://github.com/ViniciusKoiti/video-pipeline/issues/198) palavras/tempos. Não criar issues duplicadas nem tratar esses vínculos como dependências globais de conclusão.

## 10. Checklist de execução futura

- [ ] AP-C01: receitas e decisões mínimas registradas.
- [ ] AP-C02: prova, revisão e classificação dos gaps concluídas.
- [ ] AP-C03: entregue ou adiado com motivo.
- [ ] AP-C04: entregue ou adiado com motivo.
- [ ] AP-C05: entregue ou adiado com motivo.
- [ ] AP-C06: integração, documentação e regressão do recorte entregues.

Nenhuma etapa foi executada pela criação deste plano. Não houve mudança de código, dependências, skills ou episódios; comandos acima são instruções para a implementação futura.
