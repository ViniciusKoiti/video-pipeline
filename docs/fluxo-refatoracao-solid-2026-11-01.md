# Fluxo de refatoração SOLID e gates de aceite

Data: 2026-11-01. Sequência de execução da
[análise de gaps](analise-gaps-solid-2026-10-31.md), complementando o
[inventário dos scripts](analise-scripts-provisorios-2026-10-31.md), o
[desenho em objetos](desenho-orientado-a-objetos-2026-10-31.md) e o
[gate de tamanho](analise-tamanho-modulos-2026-10-31.md).

Cada etapa entrega uma mudança pequena e verificável; a próxima começa quando os critérios anteriores
estiverem demonstrados. A ordem abaixo corrige a dependência do plano antigo, que extraía o narrador antes
de definir sua porta TTS. Os identificadores `RF` são gates de engenharia; os gates 1–4 dos episódios
continuam sendo decisões humanas, registradas em `review.json`.

**Foco desta entrega:** primeiro o [gate de qualidade](gate-qualidade.md), executado por
`bash scripts/check_qualidade.sh`. As demais etapas são plano de execução e permanecem pendentes.

**Estado atual:** modelos e constantes foram separados por área (ADRs 037–038), com guardas no gate:
311 constantes em 54 classes, tipagem estrita sem erros em 362 arquivos e 958 testes passando (6 lentos
fora pela configuração existente). A baseline de tamanho caiu para 10 arquivos e 9 funções. RF0 ainda
foi fechado em 2026-11-01: os dois `B006` eram demos de Shorts que mostram o bug de propósito e ganharam
exceção pontual no ruff. RF1 foi implementado no mesmo dia (ADR 039); o próximo gate funcional é RF2.

## 1. Sequência e situação

```mermaid
flowchart TD
    RF0["RF0 · Guardas e linha de base"] --> RF1["RF1 · Aprovação e proteção de escrita"]
    RF1 --> RF2["RF2 · Estado, falha parcial e retomada"]
    RF2 --> RF3["RF3 · Porta TTS e identidade do cache"]
    RF3 --> RF4["RF4 · Operações e contratos compartilhados"]
    RF4 --> RF5["RF5 · Entrada de fontes, ativos e briefs"]
    RF5 --> RF6["RF6 · Produção longa e Short"]
    RF6 --> RF7["RF7 · Migração de chamadores e consolidação"]
```

| Gate | Gaps cobertos | Situação atual |
|---|---|---|
| RF0 | G12; prevenção da dependência de G09 | Fechado em 2026-11-01: arquitetura, modelos, constantes, tamanho, tipagem e lint verdes |
| RF1 | G01; fronteira de proteção de G02 | Implementado em 2026-11-01 (ADR 039); ligar os escritores concretos fica para RF5/RF6 |
| RF2 | G03; recuperação de G02 | Implementado em 2026-11-01 (ADR 040); nenhum chamador real usa `run_scenes` ainda (RF3/RF6) |
| RF3 | G04–G05 | Porta implementada em 2026-11-01 (ADR 041); `VoiceKey`, biblioteca, narrador e a migração dos dois scripts seguem pendentes |
| RF4 | G06–G09 | Parcial em 2026-11-01 (ADR 042): `Context`, `Settings`, orquestração e registro de comandos provados; operações `voice`/`subs`/`render` e `EpisodeFolder` só com contrato escrito |
| RF5 | G02, G10–G11 | Fatia 1 (fontes) feita em 2026-11-01 (ADR 043); ativos, entradas do kit e briefs pendentes |
| RF6 | Integração G01–G11 no longo e Short | Pendente |
| RF7 | G12 e encerramento da migração | Pendente |

“Implantado” significa que há código de verificação, não que todos os gaps foram resolvidos. Teste antigo
passando não comprova serviço que ainda não existe. A migração de uma casca fina offline, como métricas,
pode ocorrer antes, se não depender dos contratos pendentes nem escrever artefatos protegidos.

## 2. Regra comum de passagem

Para cada fatia, registrar no PR ou na revisão local: gate, arquivos alterados, comportamento comprovado,
comandos e resultados, pendências e forma de desfazer a mudança sem apagar dados de episódio.

- O teste de regressão deve falhar com o defeito e passar com a correção. Não usar `skip` ou `xfail` para
  declarar um critério cumprido.
- Executar os testes específicos da mudança e `bash scripts/check_qualidade.sh` (suíte completa, tipagem e lint).
  Uma falha preexistente deve aparecer como pendência identificada, sem ser escondida ou contada como passe.
- Arquitetura e tamanho rodam no pytest, no CI e no pré-commit: 200 linhas por arquivo de `app/`, 50 por
  função; a baseline só encolhe. Não regenerá-la para aceitar crescimento.
- Alteração de contrato atualiza porta, adapters aplicáveis, fakes, chamadores e fixtures na mesma fatia.
  Preservar imports públicos ao repartir módulos.
- Chamadas externas, renders e episódios reais continuam sujeitos às autorizações existentes. O teste do
  gate usa pastas temporárias e provedores falsos. Aprovação de engenharia não aprova conteúdo nem publicação.

Se um critério falhar, corrigir a mesma fatia e repetir os checks afetados. Não começar a migração que depende
dele. Descobrir uma regressão em gate já verificado reabre sua pendência e exige nova evidência; não se edita
o histórico para fingir que a execução anterior nunca ocorreu.

## 3. Critérios por gate

### RF0 — Guardas e linha de base

**Entrega:** guarda de arquitetura compatível com pacotes, fronteiras explícitas e execução local/CI.

- [x] `app.bootstrap` e seus submódulos podem compor adapters; nomes parecidos não ganham essa permissão.
- [x] Pipeline continua impedido de importar adapters concretos e raiz de composição.
- [x] Mídia pode usar schemas, mas não importar orquestração de produção; imports relativos também são analisados.
- [x] Gate de tamanho preservado em 200/50, sem ampliar baseline.
- [x] Pré-commit executa arquitetura e tamanho; o CI executa ambos pela suíte existente.
- [x] Mypy estrito integrado ao comando único; linha de base dos erros de tipos registrada.
- [x] Modelos por área, uma classe por arquivo, com compatibilidade dos imports existentes (ADR 037).
- [x] Constantes por área, atributos Final e coleções imutáveis em profundidade, verificados no gate (ADR 038).
- [x] Checks globais inteiramente verdes, incluindo lint e tipagem (2026-11-01).

Comando rápido: `uv run pytest tests/test_architecture.py tests/test_tamanho_modulos.py -q`.
O hook depende de `git config core.hooksPath .githooks` no clone; a presença do arquivo não ativa essa configuração.

### RF1 — Aprovação e proteção antes de escrever

**Entrega:** uma regra de proteção consultada pelos escritores, com `review.json` como autoridade e
reabertura explícita; nenhuma migração de episódio real para provar o mecanismo.

- [x] Aprovar pelo CLI e tentar alterar fontes/fichas, roteiro e saídas do gate 4 recusa antes da escrita.
- [x] A fronteira de proteção também pode ser consultada antes de substituir binários (`check` sem candidato);
  integração dos escritores concretos será demonstrada em RF5/RF6.
- [x] Status de topo aprovado dos ativos continua protegido, incluindo ativos reaproveitados.
- [x] Reabertura tem motivo e autor registrados, libera apenas o alvo solicitado e não apaga decisões antigas.
- [x] Alteração de `asset_id` no gate 3 e bloco numérico derivado mantêm as exceções já definidas para o gate 2.
- [x] Decisões existentes e hashes legados continuam reconhecidos; nenhuma segunda autoridade de aprovação.

**Evidência:** `tests/test_protection.py` (aprovação pelo `main` do `vp` seguida da tentativa de escrita, hash
legado, reabertura, ativo, relógio recuado) e `tests/test_state.py`. Ressalvas: a recusa vale para quem consulta
o `WriteGuard`, e hoje só `write_output` o faz (ligar os escritores concretos é RF5/RF6); o gate 4 foi
provado pelo `check` direto, e só o gate 1 também pelo `write_output` de ponta a ponta.

### RF2 — Estado e retomada

**Entrega:** contrato de resultado incompleto e reutilização, provado com ações falsas e saídas persistidas.
Não depende de o futuro `Narrator` já existir.

- [x] Três cenas independentes: a segunda falha; primeira e terceira deixam saídas válidas.
- [x] Reexecutar a mesma entrada tenta só a cena pendente; `needs_review` parcial não impede a tentativa.
- [x] Revisão humana pendente é distinguida de produção incompleta: não refazer um resultado íntegro que
  esteja apenas aguardando revisão.
- [x] Saída reutilizada é reconstruída após reiniciar o processo, sem depender de estado em memória.
- [x] Arquivo ausente ou inválido gera recuperação ou erro explícito; aprovado não é recriado automaticamente.
- [x] Lock continua exclusivo, inclusive no erro; não aninhar `store.lock` com o lock de `run_step`.
- [x] Entrada mutável é conferida sob a trava; mudança entre etapas não produz resultado misto silencioso.
- [x] Erro inesperado sobe e é registrado; falha recuperável fica ligada à cena e bloqueia só dependências dela.

**Evidência:** `tests/test_scene_step.py` (15 casos, com mutações conferidas: sem a checagem de arquivo ou sem a
retomada de `RUNNING`, os testes falham), `tests/test_state.py` e `tests/test_failures.py`, com disco temporário
e ações falsas. Interromper uma gravação não vira saída concluída: a cena só é registrada depois que a ação
terminou e as saídas existem. Ressalva: o contrato vale para `run_scenes` e `run_step`; `for_each_scene` segue
sem estado e será substituído quando o narrador for migrado (RF3/RF6).

### RF3 — TTS, lotes, ciclo de vida e cache

**Entrega:** porta definida antes de extrair o código compartilhado de voz.

- [x] Fingerprint representa os mesmos parâmetros efetivos usados na síntese: idioma, voz, modelo,
  referência, pausa, entrega neutra/fallback e corte/junção; overrides têm regra explícita.
- [x] Identidade de cache e nome de exibição são distintos; alias legado `gemini` é tratado explicitamente.
- [x] Compatibilidade dos nomes de WAV de longo e Short é testada; invalidar cache incorreto é mudança
  declarada e limitada às falas afetadas, não promessa de zero regenerações.
- [x] Lote respeita voz/idioma, limite e pausas; mantém ordem, quantidade e correspondência entre pedidos e saídas.
- [x] Só recusa de corte prevista aciona fallback por cena; cota esgotada não gera nova rajada de chamadas.
- [x] Falha não publica WAV inválido; fechamento acontece também na exceção; propriedade e reuso do TTS
  após `close` estão definidos.
- [x] Fakes e adapters aplicáveis passam pelos mesmos contratos, com transporte falso para remotos.

**Evidência:** `tests/test_tts_fingerprint.py` (nomes antigos de longo e Short contra as funções reais dos
scripts, alias Gemini, dois idiomas, pausas, fala longa, entrega neutra e fallback, referência, versão),
`tests/test_tts_batching.py` (agrupamento, fallback, cota, WAV inválido, fechamento), `tests/test_contracts.py`,
`tests/test_chatterbox_tts.py` e `tests/test_gemini_tts.py`; mutações conferidas nos três pontos centrais.
Ressalvas: a escrita atômica do Kokoro só roda no teste lento (`extra tts`); a mudança de chave da entrega não
neutra do Chatterbox é declarada (ADR 041); a decisão de manter o nome dos Shorts já aprovados (identidade sem
texto) fica para o `VoiceKey`. Os scripts ainda não usam a porta nova: a migração dos dois chamadores é a etapa
seguinte, depois da extração de `VoiceKey`, biblioteca e narrador.

### RF4 — Operações públicas e direção das dependências

**Entrega:** contratos e limites dos objetos que vão receber os scripts.

- [ ] `voice` apenas produz voz; `subs` usa WAVs existentes; `render` não sintetiza nem alinha remotamente.
  *(contrato no ADR 042; a prova depende de as operações existirem, RF6)*
- [ ] Cada operação funciona em um processo novo com pré-requisitos próprios; voz de rascunho não exige
  ativos finais. Resolver as condições da voz final e do render final antes de habilitá-los.
  *(condições propostas no ADR 042, a confirmar pelo dono ao implementar)*
- [x] Composição resolve configuração e entrega aos serviços só as portas e valores necessários.
  *(guarda: núcleo não importa `app.settings`; os serviços novos já recebem portas e valores)*
- [x] `Context` e `FakeContext` declaram as capacidades realmente usadas pelo CLI.
- [ ] `EpisodeFolder` cuida do acesso/layout; política de proteção e preparação de post não se duplicam nele.
  *(a classe ainda não existe; fronteiras no ADR 042)*
- [ ] Narração compartilhada não depende de `ShortProduction`; plano de revisão de áudio chega pronto à mídia.
  *(a dependência já é barrada por teste; falta o `AudioReviewPlan` pronto, que nasce com o fluxo do Short)*
- [x] Registro de comandos preserva argumentos e códigos de saída; nenhuma descoberta dinâmica de módulos.

**Evidência:** `tests/test_context_contract.py`, `tests/test_command_registry.py` e os guardas novos de
`tests/test_architecture.py` (mutações conferidas: serviço lendo `Settings`, `FakeContext` sem `word_aligner`);
acrescentar testes de operações separadas quando forem implementadas. Os exemplos antigos de `run_voice -> Production.run()` não são critério de implementação.

### RF5 — Fontes, ativos e dados externos

**Entrega:** migrar uma entrada por fatia, usando os contratos de proteção e retomada já verificados.

- [x] Fontes baixadas, locais e declaradas compartilham registro; ID é alocado sob lock; repetição não duplica
  nem substitui fonte aprovada.
- [x] Falha no registro de bruto/texto/trechos/manifesto deixa uma recuperação definida; o manifesto de
  conclusão é publicado por último. `replace` individual não é chamado de transação de vários arquivos.
- [ ] Busca distingue banco indisponível, busca sem resultado e erro de programação; motivos ficam registrados.
- [ ] Download escolhido preserva associação de cenas anteriores, é idempotente e protege mídia aprovada.
- [ ] Entradas validam IDs, caminhos contidos, fps e durações positivos/finitos, intervalos de fala e referências.
- [ ] Leitura/escrita do conteúdo do kit preserva campos que o auto-play não interpreta.
- [ ] Cópias de briefs e catálogo de música mantêm seus contratos de substituição e licença.

**Evidência (fatia 1, fontes):** `tests/test_sources.py` (13 casos: as três entradas, id sob lock com dois
"processos", repetição, gate 1 aprovado, falha em texto, trechos e manifesto, órfão, manifesto por último;
mutações conferidas) e `tests/test_sources_scripts.py` (os dois scripts, sem rede). **Pendente:** ativos
(`AssetIntake`, busca tolerante a banco indisponível), validação das entradas do kit, preservação de campos
desconhecidos e briefs/catálogo de música. Criar testes específicos de ativos e briefs e ampliar os de
música/Short conforme a fatia. Nenhum critério passa só porque um arquivo foi movido para `app/`.

### RF6 — Integração da produção longa e Short

**Entrega:** comandos sobre os componentes verificados, uma operação por mudança revisável.

- [ ] Longo e Short compartilham voz sem herdar de uma classe genérica de produção.
- [ ] WAV novo é validado e promovido antes de remover versões obsoletas; erro conserva o anterior utilizável.
- [ ] Estado, relatório por cena e cache permitem retomar depois de encerrar o processo.
- [ ] Motor vem da porta configurada por formato; substituição é demonstrada com renderer falso.
- [ ] Montagem incompleta não avança para render final; precondições são verificadas na operação.
- [ ] Prévia e final não se confundem no estado/cache nem no conteúdo protegido pelo gate 4.
- [ ] Pacote de vídeo e texto é preparado e validado antes de publicar; falha injetada não produz pacote
  considerado completo. Recusar substituição de pacote aprovado antes da primeira cópia.
- [ ] Timestamps, legendas, áudio e efeitos preservam os contratos existentes; teste visual real, quando
  aplicável, segue o vídeo-régua e as autorizações atuais.

**Evidência:** testes de integração da produção a criar, mais os testes existentes de narração, captions,
shots, efeitos e Shorts. O vídeo-régua complementa esses testes; não substitui provas de proteção e retomada.

### RF7 — Chamadores, documentação e encerramento

**Entrega:** remover as dependências dos scripts migrados e consolidar os módulos tocados.

- [ ] Tests passam a importar de `app/`; nenhum consumidor ativo ainda importa script removido por caminho.
- [ ] Skills, referências do CLI e documentação apontam para os comandos implementados.
- [ ] Configurações locais e rotina diária são conferidas pelo dono quando precisarem de alteração fora
  do escopo editável; não remover o script enquanto houver um consumidor pendente.
- [ ] Ferramentas de uma vez e benchmarks são classificados e preservam referências históricas.
- [ ] Módulos grandes são divididos por responsabilidade ao serem tocados; imports públicos e schemas persistidos
  mantêm compatibilidade. Baseline encolhe apenas com redução comprovada.
- [ ] Testes globais e lint passam; não restam critérios obrigatórios sem evidência.

**Evidência:** busca dos caminhos antigos em app, testes e instruções; help do CLI; checks globais e
conferência dos consumidores operacionais. Não acrescentar publicação ou agendamento ao teste de migração.

## 4. Registro desta entrega

Foi implantado `scripts/check_qualidade.sh`, compartilhado pelo pré-commit e CI, com lint, tipagem estrita
via Mypy e suíte completa.
A guarda de arquitetura foi ampliada em `tests/test_architecture.py`; o gate de tamanho existente foi
preservado. RF1–RF7 continuam pendentes; escrever seus critérios não os implementa. A linha de base e os
resultados locais estão no [registro do gate de qualidade](gate-qualidade.md).

RF1 foi entregue em seguida (ADR 039): `ReviewWriteGuard` sobre o `review.json`, `reopen_gate` e `vp reopen`,
`ReviewLog.latest` pela posição no log e `default_reviewer` em `app/commands/reviewer.py` (o `cli.py` encolheu de
318 para 301 linhas de código e a baseline foi regenerada). 
RF2 veio depois (ADR 040): `run_scenes` com registro por cena no `manifest.json`, retomada só das cenas pendentes,
`plan` que só reaproveita resultado íntegro e `run_step` com a entrada conferida sob o lock. O próximo trabalho da
sequência é RF3: porta TTS, lotes e identidade do cache.

RF3 foi entregue em seguida (ADR 041): `identity` e `fingerprint(request)` na porta, `BatchTTS`, `Closeable` e
`closing_tts`, `atomic_wav` nos adapters, `app/media/speech_batches.py` (lote, fallback só no corte recusado, cota
que para as chamadas) e `app/media/wav.py`. O `chatterbox.py` foi dividido (`chatterbox_text.py`). O próximo
trabalho da sequência é RF4: operações públicas e direção das dependências.

RF4 foi feito só no que existe (ADR 042): `Context` com `tts_final`, `tts_named` e `word_aligner` (e o `FakeContext`
igual), guarda contra `Settings` no núcleo e contra a orquestração de produção em código compartilhado, e testes do
registro de comandos. O que falta no RF4 depende de objetos que só nascem no RF6 (`voice`, `subs`, `render`,
`EpisodeFolder`); o contrato deles está no ADR 042. O próximo trabalho da sequência é RF5: fontes, ativos e briefs.

RF5 começou pelas fontes (ADR 043): `app/pipeline/sources.py` (`SourceRegistry` e as três entradas) e
`app/pipeline/atomic_files.py`; `baixar_fonte.py` e `fonte_declarada.py` agora só chamam o registro. As próximas
fatias são a entrada de ativos (G11) e a validação das entradas do kit (G10).

## 5. Pendências abertas ao fim do RF3 (2026-11-01)

Nenhuma bloqueia o RF4. O dono confirmou em 2026-11-01 que se segue sem decidir agora.

| Pendência | Quem decide | Quando |
|---|---|---|
| Nome dos WAVs dos Shorts já aprovados na escuta: manter o nome de hoje (`fingerprint` de um pedido sem texto) ou adotar a identidade completa. Recomendação: manter, porque a voz clonada sorteia a pronúncia e regenerar pode trocar um áudio aprovado. Custo: o nome do Short não acompanha uma mudança de `pause_ms`. | Dono | Ao migrar o `shorts_tec` para a porta (`VoiceKey`) |
| A entrega não neutra do Chatterbox muda de chave (ADR 041): essas falas são regeradas na próxima vez que a voz de um episódio rodar. Nada dispara isso sozinho; não rodar a voz de episódio aprovado sem necessidade. | Aviso | Contínuo |
| Escrita atômica do Kokoro só é exercida no teste lento (`uv run pytest -m slow -k kokoro`, extra `tts`). Rodar com a máquina livre, depois da sonda de CPU (`cpu_probe`). | Dono pede | Quando quiser |
| `data/publicacoes/registro.jsonl` já vinha modificado antes da refatoração e ficou fora dos commits. | Dono | Quando revisar os agendamentos |
| Scripts `montar_episodio.py` e `shorts_tec.py` ainda usam a lógica própria de chave, lote e fechamento da voz. | Código | Depois da extração de `VoiceKey`, biblioteca e narrador |
