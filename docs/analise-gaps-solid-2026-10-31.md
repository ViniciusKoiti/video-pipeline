# Gaps de SOLID na aplicação e no desenho proposto (2026-10-31)

Análise, sem implementação. Base: [scripts provisórios](analise-scripts-provisorios-2026-10-31.md),
[tamanho dos módulos](analise-tamanho-modulos-2026-10-31.md) e
[desenho em objetos](desenho-orientado-a-objetos-2026-10-31.md), confrontados com o código local.

Sequência de execução e critérios de passagem em
[fluxo de refatoração e gates](fluxo-refatoracao-solid-2026-11-01.md). O relatório abaixo preserva o diagnóstico
de 2026-10-31; o fluxo registra quais verificações já foram implantadas e o que continua pendente.

**O desenho é uma boa direção, mas ainda não é um contrato pronto para implementar.** Os maiores riscos
estão na proteção das aprovações, na retomada após falhas e na substituição dos provedores. Transformar
funções em classes ou repartir arquivos não resolve esses riscos por si só.

O recorte é a migração dos scripts e suas fronteiras com CLI, voz, armazenamento, gates e mídia; não é
uma auditoria completa de todos os módulos ou do template. As interfaces novas dos documentos são propostas,
portanto os problemas nelas são riscos de desenho, não bugs já executáveis.

## 1. Como interpretar SOLID neste projeto

| Princípio | Pergunta prática |
|---|---|
| S — responsabilidade única | Esta unidade muda por uma única categoria de motivo, ou mistura política editorial, armazenamento e provedor? |
| O — aberto para extensão | Um novo provedor consegue entrar pela porta e pelo registro, sem acrescentar condições pelo nome no orquestrador? |
| L — substituição | Qualquer implementação cumpre as mesmas garantias de saída, erro, cache e ciclo de vida? |
| I — segregação de interfaces | Cada consumidor recebe apenas as capacidades que usa? |
| D — inversão de dependência | A regra da aplicação depende de contratos ou conhece configuração e detalhes concretos de infraestrutura? |

Não é necessário usar herança para aplicar L: os `Protocol`s também têm contratos de comportamento.
Tamanho e complexidade são sinais para inspeção; não provam violação de S. Uma função que valida várias
regras coesas pode ter uma responsabilidade. Extrair cada `if` não garante que essa responsabilidade ficou melhor.

Vale preservar: portas existentes, adapters montados no bootstrap, valores tipados, transformações puras,
composição entre longo e Short, e gates humanos. Não há necessidade demonstrada de framework, contêiner de
injeção, barramento de eventos, classe base de produção ou sistema de plugins.

## 2. Mapa dos gaps

P1 = resolver o contrato antes de migrar produção; P2 = resolver ao implementar o componente;
P3 = ajustar documentação e guardas de arquitetura durante a migração.

| Gap | Prioridade | Situação | SOLID relacionado |
|---|---|---|---|
| G01 Aprovação e estado não compartilham a mesma proteção | P1 | código atual; proposta não fecha | S, D |
| G02 Publicação de arquivos não tem garantia uniforme | P1 | código atual; proposta parcial | S, L |
| G03 Falha parcial e reutilização podem impedir retomada | P1 | integração proposta com núcleo atual | L |
| G04 Contrato TTS e de lote ainda incompleto | P1 | código atual e proposta | O, L, I, D |
| G05 Identidade do cache e compatibilidade indefinidas | P1 | código atual e proposta | S, L |
| G06 Comandos independentes contradizem `Production.run()` | P1 | proposta | S, I |
| G07 `Context` continua amplo e expõe configuração | P2 | código atual e proposta | I, D |
| G08 `EpisodeFolder` concentra políticas diferentes | P2 | proposta | S, I |
| G09 Tipos compartilhados apontam para o orquestrador | P2 | proposta | S, D |
| G10 Modelos tipados ainda precisam de invariantes | P2 | proposta | L, D |
| G11 Contratos de acervo e registro precisam preservar comportamento | P2 | código atual e proposta | O, L |
| G12 Guardas e plano de migração não acompanham todo o desenho | P3 | código atual e documentos | O, D |

Nem toda falha de consistência é uma violação direta de SOLID. Nos G01–G03, o problema operacional mostra
que a responsabilidade e o contrato entre componentes ainda não estão fechados.

## 3. Evidências, consequências e menor correção

### G01 — `write_output` não reconhece sozinho a aprovação feita pelo CLI

**Evidência atual:** [`cli._decide`](../app/cli.py) chama
[`gates.record_decision`](../app/pipeline/gates.py), que acrescenta a decisão no `review.json`, e atualiza
o JSON do ativo quando aplicável. Não atualiza os estados de `manifest.json`.
Já [`state.write_output`](../app/pipeline/state.py) consulta apenas `protected_outputs` desse manifesto.
[`JsonFileStore.write`](../app/storage/json_files.py) recusa JSON com status de topo aprovado, uma garantia
diferente da aprovação por hash no review. `approve_step`, usado nos testes de estado, é outra entrada.

**Consequência:** `SourceRegistry` ou `Production` não podem prometer proteção de tudo que o dono aprovou
apenas por chamarem `write_output`. A detecção posterior de hash alterado não impede a sobrescrita anterior.

**Menor correção:** manter `review.json` como autoridade e definir uma única verificação de proteção,
compartilhada pelos novos escritores e pelo fluxo de estado. Definir explicitamente quais saídas cada gate
protege e como a reabertura libera a escrita; `vp reopen` ainda é placeholder. Uma projeção no manifesto pode
existir, mas precisa de regra de reconstrução e consistência, sem virar segunda autoridade.

**Aceite:** aprovar pelo mesmo caminho do CLI e tentar alterar fontes, episódio e pacote final pelo novo
serviço deve recusar antes de escrever; reabertura explícita deve permitir apenas o que foi reaberto.

### G02 — Atomicidade de JSON não cobre WAV, vídeo nem um conjunto de arquivos

**Evidência atual:** `JsonFileStore.write` usa temporário e `replace` para um JSON.
[`montar_episodio`](../scripts/provisorio/montar_episodio.py) apaga WAVs antigos antes da síntese e escreve
`episode.json` diretamente. [`shorts_tec.cmd_gate`](../scripts/provisorio/shorts_tec.py) copia o vídeo final
antes de terminar de interpretar o post. O desenho melhora o WAV com `VoiceLibrary.promote`, mas
`EpisodeFolder.stage_final`, `AssetIntake` e o registro de fontes ainda não explicitam a mesma garantia.

**Consequência:** uma falha pode destruir a última saída utilizável ou deixar vídeo, texto e metadados
de execuções diferentes. Quatro escritas atômicas de arquivos não são uma transação de quatro arquivos.

**Menor correção:** definir o responsável pela publicação de cada conjunto: validar entradas e proteção,
preparar em temporários no filesystem de destino, conferir mídia, publicar e só então limpar obsoletos.
Registrar o conjunto concluído por último e definir como recuperar uma publicação interrompida. Não exigir
um gerenciador genérico de transações: cada operação precisa apenas de um protocolo recuperável explícito.
IDs de fontes devem ser alocados e confirmados sob o mesmo lock de registro; `next_id()` isolado não reserva ID.

**Aceite:** injetar falha na síntese, na cópia e antes do último manifesto; a versão anterior continua
utilizável e a reexecução não duplica fonte nem aceita pacote incompleto.

### G03 — `needs_review` por cena não equivale a resultado reutilizável da etapa inteira

**Evidência atual:** [`for_each_scene`](../app/pipeline/failures.py) já permite continuar após `ProviderError`.
O script longo termina com `SystemExit`; o novo `Narrator` promete `SceneOutcome` por cena.
Mas [`state.plan`](../app/pipeline/state.py) reutiliza `NEEDS_REVIEW` com hash igual, e `run_step` devolve
estado e caminhos de saída, não o valor produzido pela ação. Também não verifica ali se as saídas ainda existem.

**Consequência na integração:** se a voz parcial ficar em `NEEDS_REVIEW`, repetir a mesma entrada pode pular
as cenas que falharam. Além disso, `Production` precisa reconstruir WAVs e relatório quando a ação não roda.
A proposta de `run()` “parando no primeiro erro” precisa distinguir falha de cena de falha impeditiva de etapa.

**Menor correção:** definir resultados incompletos como retomáveis, persistir resultados por cena e reconstruir
o resultado no caminho de reutilização. Só reutilizar conclusão quando os artefatos necessários estiverem
íntegros. Continuar as cenas independentes; impedir montagem/render se faltar áudio obrigatório.
Não converter erro de programação ou corrupção de entrada em falha recuperável de provedor.

**Aceite:** três cenas, a segunda falha: a terceira é gerada; na retomada só a segunda chama TTS.
Apagar uma saída concluída deve provocar recuperação ou erro explícito, nunca reutilização silenciosa.

### G04 — `Protocol` descreve métodos, mas ainda faltam garantias de substituição do TTS

**Evidência:** a porta atual em [`tts/base.py`](../app/providers/tts/base.py) contém apenas síntese simples.
O desenho acrescenta `fingerprint`, `BatchTTS` e `Closeable`, uma boa segregação de capacidades opcionais.
Entretanto `SpeechRequest` aceita `voice` e `lexicon`, enquanto o fingerprint proposto recebe apenas texto,
idioma e entrega. [`GeminiTTS`](../app/providers/tts/gemini.py) exige uma voz e um idioma por lote e recusa
léxico fonético; [`KokoroTTS`](../app/providers/tts/kokoro.py) o aplica. `max_batch_chars` sozinho não descreve
as condições de lote. `isinstance(..., BatchTTS)` não comprova essas garantias de comportamento.

**Menor correção:** fingerprint e síntese precisam usar os mesmos parâmetros efetivos — receber o pedido
ou documentar um subconjunto que exclua explicitamente overrides. Especificar ordem, cardinalidade, caminhos
de retorno e tratamento de arquivos parciais no lote; formar grupos compatíveis por voz/idioma e respeitar
pausas. Manter fallback apenas para a recusa prevista (`InvalidOutput`), sem repetir individualmente uma cota
esgotada como se fosse problema de corte. O dono do recurso deve garantir fechamento também na exceção e
esclarecer se o TTS emprestado pelo `Context` pode ser fechado e reutilizado depois.

**Aceite:** ampliar [`test_contracts.py`](../tests/test_contracts.py) para os adapters aplicáveis: mesma
entrada efetiva → mesma identidade; lote mantém correspondência; falha não publica arquivo final inválido;
fechamento ocorre no caminho de erro. Fakes acompanham o contrato, sem métodos opcionais vazios.

### G05 — A promessa de preservar o cache ainda tem exceções não especificadas

**Evidência:** o script usa o alias `gemini` nos nomes; `GeminiTTS.info.name` é `gemini_tts`.
O desenho passa `provider_name` separado do TTS, mantém nomes distintos para longo/Short e promete preservar
os WAVs. Também corrige o fingerprint de entrega apenas não neutra. Porém
[`ChatterboxTTS.synthesize_speech`](../app/providers/tts/chatterbox.py) consulta os parâmetros da entrega neutra
e usa neutra como fallback: alterá-los também pode mudar a fala. A referência e a versão do algoritmo de
corte/junção participam da identidade efetiva.

**Consequência:** trocar a origem do nome pode invalidar cache em massa; omitir parâmetros pode reutilizar
áudio incorreto. A assinatura `fingerprint(language)` do inventário também difere da assinatura com texto e
entrega no desenho detalhado.

**Menor correção:** fixar a identidade do cache independentemente do nome de exibição; documentar uma única
assinatura e os parâmetros efetivos que invalidam voz. Preservar explicitamente o formato legado onde for
correto, e separar migração de nomes da correção de cache incorreto. Não prometer zero regenerações para
entradas cuja chave antiga não identificava todos os parâmetros.

**Aceite:** exemplos reais dos nomes antigos de longo/Short, alias Gemini, dois idiomas, pausas, glossário,
entrega neutra e fallback. Alterar um parâmetro efetivo invalida só as falas afetadas.

### G06 — O comando de voz proposto também monta episódio e gera legendas

**Evidência documental:** o §8.2 da análise dos scripts recomenda `voice`, `subs` e `render` sem encadear.
No desenho, `run_voice` chama `Production.run()` com `render=False`, mas `run()` faz
voz → episódio → legendas → render. A opção só elimina o último passo.

**Consequência:** gerar voz passa a depender de ativos necessários à montagem e pode escrever legendas.
Isso importa porque a voz de rascunho está prevista antes da seleção final dos ativos.

**Menor correção:** cada handler chama a operação correspondente; a operação usa artefatos persistidos,
sem depender de métodos chamados anteriormente na mesma instância. Um método de conveniência que faz tudo
só entra se houver uso concreto. Separar intenção de voz final da resolução do vídeo, hoje combinadas nas
opções `final` e `preview`. Pré-condições devem ser verificadas na operação, inclusive sob o lock quando
dependem de conteúdo mutável, e não apenas pelo handler antes da chamada.

**Aceite:** `voice` funciona com roteiro válido sem imagens escolhidas, não renderiza nem alinha palavras;
`subs` usa WAVs existentes; `render` não sintetiza voz. Comandos separados sobrevivem ao reinício do processo.

### G07 — Ampliar `Context` corrige a tipagem, mas não segrega as dependências dos serviços

**Evidência atual:** [`Context`](../app/pipeline/ports.py) expõe todas as portas e `Settings`.
[`LazyContext`](../app/bootstrap.py) já implementa `tts_final`, `tts_named` e `word_aligner`, ausentes da porta
e do [`FakeContext`](../tests/fakes/__init__.py). Completar os dois é necessário. Entretanto `Production` e
`ShortProduction` propostos continuam recebendo o contexto inteiro, apesar da regra “nenhum objeto lê Settings”.

**Menor correção:** resolver voz, renderer, pasta e opções na composição; passar aos serviços as dependências
que realmente usam. Manter o `Context` como conveniência do CLI é aceitável. Não criar uma interface por
método automaticamente: parâmetros concretos de valor e as portas existentes bastam na maioria dos casos.
`Narrator` já aponta nessa direção ao receber TTS, biblioteca e glossário.

**Aceite:** testar o núcleo de voz sem construir `Settings`, provedores de imagem ou configuração de Postiz;
trocar o TTS não exige mudar o orquestrador.

### G08 — `EpisodeFolder` pode se tornar um objeto que conhece toda a aplicação

**Evidência proposta:** o objeto concentra layout, leitura de schemas, localização de mídia, lock, política
de aprovação e preparação do pacote final. O §3.9 ainda permite `EpisodeBrief` receber nomes de arquivo e
`CandidateIndex` conhecer sua pasta; portanto a regra “único que sabe nomes” já tem exceções no desenho.

**Menor correção:** usar `EpisodeFolder` para localizar e acessar artefatos do episódio. A política comum
de proteção pertence ao fluxo de escrita; a preparação de vídeo e post pertence à operação de saída.
Definir qual camada é dona de cada nome e migrar consumidores aos poucos, sem fazer o objeto delegar cada
função de todos os módulos. Ter um `Path` não é, sozinho, motivo suficiente para criar uma classe.

**Aceite:** mudar a preparação do post não altera o acesso a fontes; mudar o layout não obriga a reescrever
as transformações de áudio. Chamadores não contornam a proteção escrevendo em caminhos expostos.

### G09 — Colocar tipos compartilhados em `short.py` cria dependência do fluxo específico

**Evidência proposta:** `translation.py` importaria `Narration` de `short.py`, que também contém
`ShortProduction`. `app/media/earshot.py` ganharia `AudioReviewPlan.from_content(MotionContent, SfxPlan, SfxKit)`;
esses tipos estão propostos em `pipeline/short.py` e já vivem em `pipeline/sfx.py`.
Como o pipeline usa mídia, isso abre dependência de volta ao pipeline e risco de ciclo.

**Menor correção:** colocar valores realmente compartilhados em módulo de contratos coeso, sem orquestração.
Montar `AudioReviewPlan` na camada que conhece os formatos de produção; o earshot recebe cortes e expectativas
prontos. Não criar uma grande pasta genérica `common` para esconder dependências.

**Aceite:** importar tradução ou earshot não carrega `ShortProduction`; mídia não precisa conhecer os
comandos nem o ciclo de produção para medir áudio.

### G10 — Substituir dicionários por modelos não especifica as invariantes dos arquivos

**Evidência proposta:** `MotionContent` ainda aceita `dict[str, Any]`; `VoicedLine` tem caminho `str`,
`seconds: float` e dois números em `speech`; `NarrationLine` atual admite qualquer entrega e cena opcional.
As assinaturas não dizem como impedir IDs repetidos, fps zero, duração não finita ou fala fora do WAV.

**Menor correção:** validar na entrada apenas o contrato consumido: IDs únicos, fps e durações positivos e
finitos, `0 <= begin < end <= seconds`, referências válidas e caminhos contidos na pasta autorizada.
Preservar campos desconhecidos do kit ao carregar/salvar, sem reconstruir o JSON inteiro com um schema local
desatualizável. Definir o significado de ausência de cena e sua identidade estável no cache.

**Aceite:** entrada inválida falha antes de rede ou escrita; ciclo load/save e `fitted` preserva conteúdo
do kit que o auto-play não interpreta, sem alterar o objeto original acidentalmente.

### G11 — Acervo tolerante e entrada de ativos precisam de contratos distintos

**Evidência atual:** `LazyContext.archives` aborta ao montar um banco indisponível; o script de busca contorna
o bootstrap. O desenho melhora isso com `ArchiveCascade`, mantendo `archives` compatível. Já
[`baixar_escolhidos`](../scripts/provisorio/baixar_escolhidos.py) baixa diretamente no destino e substitui
`used_in_scenes` por uma lista de uma cena a cada execução.

**Menor correção:** pular indisponibilidade esperada com motivo explícito; não engolir erro de programação
ou provedor pago bloqueado. Diferenciar “nenhum candidato” de “nenhum banco disponível”. `AssetIntake` deve
recusar substituição de aprovado, preservar usos anteriores e tornar repetição da mesma escolha idempotente.
O serviço usa os adapters recebidos; só a composição consulta registro e configuração.

**Aceite:** banco indisponível não elimina os demais; nenhum banco disponível gera diagnóstico claro;
repetir download para outra cena preserva a primeira associação e nunca substitui mídia aprovada.

### G12 — As guardas atuais não comprovam as novas fronteiras

**Evidência atual:** [`test_architecture.py`](../tests/test_architecture.py) usa igualdade em
`module not in COMPOSITION` para permitir imports concretos fora do pipeline. O documento de tamanho diz que
o teste já aceita o prefixo `app.bootstrap`, mas `app.bootstrap.factories` cairia nessa checagem de igualdade.
O teste também não estabelece a fronteira de dependência de G09. Os contratos de TTS hoje verificam sobretudo
o WAV no caminho pedido; não comprovam fingerprint, lote e recuperação.

Há divergências documentais adicionais: o texto do gate ainda descreve 50 linhas/49 arquivos em partes,
mas a decisão final e [`test_tamanho_modulos.py`](../tests/test_tamanho_modulos.py) usam 200 por arquivo e
50 por função; a migração 5a usa objetos cujo contrato TTS só entraria em 5b. O desenho detalhado chama
`run()` de parada no primeiro erro, enquanto o `Narrator` deve continuar cenas independentes.

**Menor correção:** consolidar o contrato decidido antes da extração; adaptar guardas para fronteiras
exatas de pacote (`nome == raiz` ou `nome.startswith(raiz + '.')`). Usar um registro explícito de comandos,
sem descoberta dinâmica. Reexportar nomes antigos ao repartir módulos e preservar opções e códigos de saída.
Adicionar testes de comportamento por risco, não apenas asserts que repetem a estrutura das classes.

## 4. Ordem sugerida para avançar com calma

1. **Fechar proteção e retomada:** G01–G03, incluindo como reabrir, tratar falha parcial e reconstruir saída
   reutilizada. Um teste de aprovação pelo caminho real do CLI deve anteceder a promessa de imutabilidade.
2. **Fixar a porta de voz:** G04–G05. Definir fingerprint e compatibilidade antes de extrair `Narrator`;
   migrar os dois scripts para o componente comum com testes dos nomes antigos e das falhas.
3. **Fechar as operações públicas:** G06–G09. Esclarecer o que cada comando faz, limitar dependências e
   separar os valores compartilhados dos orquestradores. Ajustar o registro do CLI em uma mudança própria.
4. **Migrar uma operação por vez:** G10–G11, junto com chamadores, fakes, fixtures, skills e documentação.
   Fontes e ativos só entram após a proteção comum estar demonstrada.
5. **Apertar estrutura e tamanho:** G12 e os módulos grandes à medida que forem tocados, mantendo os limites
   decididos de 200/50. Partir por assunto; não usar mixins nem métodos de simples repasse para caber no gate.

Não é necessário bloquear a migração de uma casca fina offline, como métricas, até todos os gaps fecharem.
O bloqueio é para prometer segurança e retomada da produção sem antes provar esses contratos.

## 5. Critério para considerar o desenho pronto

O desenho pode virar implementação quando houver respostas verificáveis a estas perguntas:

- Qual componente impede a escrita de cada saída aprovada, inclusive binários, e como se reabre?
- Que resultado fica persistido após falha parcial, e o que a próxima execução realmente tenta de novo?
- Quais entradas efetivas mudam o cache, e quais nomes antigos continuam válidos?
- Qual é a garantia de um lote e quem fecha o recurso quando ele falha?
- Cada comando consegue operar com seus próprios pré-requisitos em um processo novo?
- Os valores compartilhados e as dependências mantêm a direção proposta sem ciclos?

## 6. Método e limites

Foram consultados `list_projects`, `index_status`, busca estrutural, rastreamento de `run_step` e cobertura
dos caminhos relevantes no projeto `home-viniciusk-projetos-auto-play`. A geração disponível é de
2026-10-15 e vários caminhos têm metadados alterados ou não rastreados; as conclusões materiais foram
conferidas por leitura e busca no código atual, não por alegação de completude do grafo.

Nenhum script de produção, chamada de provedor, download de ativo ou render foi executado para esta análise.
Os testes existentes não demonstram as classes futuras: os critérios acima são trabalho de implementação.

Verificação desta análise:

- `uv run pytest`: **880 passaram; 6 testes lentos ficaram fora**, conforme a configuração do projeto.
- `uv run ruff check .`: falhou com dois `B006` preexistentes em
  `renders/short-argumento-padrao/demo/lista.py` e `renders/short-revisar-comando/demo/lista.py`;
  não foram corrigidos por estarem fora do escopo.
- G01 reproduzido com `JsonFileStore` e `JsonReviewGate` em diretório temporário: registrar aprovação pelo
  mesmo `record_decision` chamado pelo CLI não preenche `protected_outputs`; `write_output` permite alterar
  `sources.json`. Foi uma reprodução mínima do mecanismo de hash/proteção, com `facts.json` sintético,
  não uma validação editorial de episódio completo.
- G12 reproduzido chamando a guarda com `app.bootstrap.factories`: ela aponta violação ao importar um
  adapter concreto. Nenhum arquivo de aplicação foi criado para essa checagem.
