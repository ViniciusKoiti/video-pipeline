# Gate de qualidade

Este é o primeiro ponto de controle da refatoração SOLID. Ele mostra a qualidade verificável da árvore
de trabalho e bloqueia o avanço quando lint, tipagem, testes, arquitetura ou tamanho falham. Não aprova fatos,
direitos de ativos nem publicação: os gates humanos dos episódios continuam com suas regras atuais.

## Comando único

```bash
bash scripts/check_qualidade.sh
```

O comando pode ser chamado de qualquer diretório pelo caminho do script. Usa o ambiente já instalado
(`uv sync --frozen` na preparação do CI); `--no-sync` evita instalar ou atualizar dependências durante o gate.

| Verificação | Execução | Condição de passagem |
|---|---|---|
| Lint | `uv run --no-sync ruff check .` | Nenhum erro nas regras já configuradas |
| Tipagem estática | `uv run --no-sync mypy` | Nenhum diagnóstico no modo estrito de `app/`, com plugin Pydantic |
| Testes e regressão | `uv run --no-sync pytest -q` | Todos os testes selecionados passam |
| Arquitetura, dentro do pytest | `tests/test_architecture.py` | Dependências obedecem às fronteiras abaixo |
| Modelos, dentro do pytest | `tests/test_model_layout.py` | Objetos de dados em `app/<área>/models/`, uma classe por arquivo (ADR 037) |
| Constantes, dentro do pytest | `tests/test_constants_layout.py` | Todos os fluxos de `app/` usam classes em `constants/`, atributos `Final` e coleções imutáveis em profundidade (ADR 038) |
| Tamanho, dentro do pytest | `tests/test_tamanho_modulos.py` | Arquivos de `app/` até 200 linhas de código, funções até 50; exceções existentes não crescem |

Os três comandos são executados mesmo quando um anterior falha. O processo retorna **0** apenas se todos
passarem; qualquer falha retorna **1**. Não corrige arquivos, regenera baseline, produz áudio, renderiza
episódios ou aprova gates de conteúdo. Os testes usam seus próprios temporários e fixtures.

Arquitetura e tamanho já pertencem à suíte: não é necessário executá-los novamente como uma etapa separada
do gate completo. Os testes marcados `slow` ficam fora pela configuração atual do pytest; sucesso aqui
não comprova modelos pesados nem serviços remotos reais.

## Tipagem e desenho em objetos

O Mypy verifica parâmetros, retornos, valores opcionais, genéricos e compatibilidade estrutural com os
`Protocol`s. O plugin do Pydantic verifica também as assinaturas dos modelos, com `init_typed=true`.
Configuração em `pyproject.toml`; versão instalada **2.4.1**, fixada no `uv.lock`. É dependência de
desenvolvimento, com licença MIT e partes sob PSF-2.0; não entra nas dependências de execução.

Para executar só essa etapa: `uv run --no-sync mypy`. Ela analisa todos os arquivos Python de `app/`, sem
executar provedores. Os testes do gate comprovam que um adapter compatível é aceito como `TTSProvider` e
um retorno incompatível é recusado. A análise de `tests/`, scripts provisórios, `deploy/` e TypeScript não
faz parte do escopo estático inicial; os testes continuam sendo executados normalmente.

As dependências opcionais usam [stubs locais](../stubs/README.md) para a superfície de API consumida pelos
adapters, sem carregar modelos nem ignorar módulos inteiros. Os stubs têm precedência sobre os tipos das
bibliotecas instaladas; não representam suas APIs completas.

Isso complementa arquitetura e contratos de comportamento. Classes anotadas ainda podem acumular
responsabilidades; `Any` explícito ainda permite trechos dinâmicos mesmo em modo estrito. O Mypy não prova
SOLID nem substitui validação de JSON em runtime. Não foram acrescentados ignores globais ou uma baseline
que aceite os erros de tipagem existentes.

Referências verificadas: [Protocol e compatibilidade estrutural](https://mypy.readthedocs.io/en/stable/protocols.html),
[plugin Pydantic](https://docs.pydantic.dev/latest/integrations/mypy/) e
[licença do Mypy](https://github.com/python/mypy/blob/master/LICENSE).

## Onde é aplicado

- **Local:** comando acima, documentado também no README.
- **Pré-commit:** `.githooks/pre-commit` chama o mesmo script, além do limite de tamanho dos arquivos no
  índice e do lint dos Python que entram no commit. Este clone já usa `core.hooksPath=.githooks`.
  Em outro clone, ativar com `git config core.hooksPath .githooks`.
- **CI:** o job Python de `.github/workflows/ci.yml` chama o mesmo script após preparar as dependências.
  A varredura de segredos continua no job próprio.

A configuração do CI faz o job falhar se o gate reprovar. Exigir o job para permitir merge depende da
proteção de branch do serviço Git, que não foi alterada nesta entrega. O hook local verifica a árvore de
trabalho; o CI verifica o conteúdo do checkout da revisão enviada.

## Fronteiras verificadas

- Pipeline usa portas e valores; não importa adapters concretos nem raiz de composição.
- Adapters não dependem da orquestração do pipeline nem leem `Settings` diretamente.
- Mídia e adapters podem consumir `app.pipeline.models`, `app.pipeline.constants` e o reexport `app.pipeline.schemas`;
  não dependem de serviços de produção, Short ou efeitos do pipeline.
- Modelos de todos os fluxos ficam em `app/<área>/models/`, uma classe por arquivo; serviços e portas
  ficam fora. A regra e os caminhos de compatibilidade estão na [ADR 037](decisions/037-modelos-por-fluxo.md).
- Constantes públicas, privadas e de validação ficam nas classes de `constants/` da área. O gate rejeita
  definições fora da pasta, atributos sem `Final` e valores mutáveis em coleções aninhadas. Tipos, campos de
  modelos, variáveis locais e os dois registros mutáveis de composição têm o tratamento da
  [ADR 038](decisions/038-constantes-por-area.md); não há baseline que aceite constantes pendentes.
- A raiz `app.bootstrap` pode virar pacote sem perder sua função de composição. Nomes semelhantes, como
  `app.bootstrap_extra`, não recebem a mesma permissão. A exceção existente de `app.cli` é preservada.
- Imports relativos são resolvidos antes da análise, inclusive em `__init__.py`.

A guarda analisa imports estáticos com AST. Não é uma prova de SOLID nem uma detecção completa de ciclos,
imports dinâmicos, efeitos colaterais ou contratos de comportamento.

## Ponto de partida em 2026-11-01

| Indicador | Medida local |
|---|---|
| Código em `app/` | 11.743 linhas de código em 362 arquivos Python após separar modelos e constantes em todo o sistema |
| Exceções legadas de tamanho | 10 arquivos e 9 funções, em `tests/baseline_tamanho_app.json`; nenhuma exceção cresceu |
| Violações atuais da catraca de tamanho | 0 |
| Arquitetura, tamanho, modelos e constantes | 57 testes passaram na verificação específica |
| Constantes identificadas | 311 atributos em 54 classes; [inventário por responsabilidade](inventario-constantes-2026-11-01.md) |
| Suíte completa | 958 testes passaram; 6 lentos ficaram fora pela configuração existente |
| Tipagem estrita | Sem erros nos 362 arquivos de `app/`; 107 diagnósticos iniciais resolvidos |
| Lint dos testes alterados | Aprovado |
| Lint global | Reprovado por dois `B006` preexistentes, listados abaixo |

O gate retorna **1** enquanto lint ou tipagem reprovarem, mesmo que todos os testes passem. A medição
de tipagem e a ordem de correção estão em [qualidade de tipagem](qualidade-tipagem-2026-11-01.md).
Os testes do mecanismo do gate usam um `uv` falso; o teste de compatibilidade TTS executa o Mypy instalado.
Após as correções, o comando completo retornou **1** somente pelos dois erros de lint abaixo; tipagem,
arquitetura, tamanho e testes passaram. Nenhum serviço de produção foi chamado.

A extração de `FfmpegConstants` (ADR 038) preservou as chaves de cache de áudio conferidas antes e depois,
com e sem trilha. A suíte também verifica que trocar a versão invalida o cache; a catraca de tamanho
de `app/render/ffmpeg.py` caiu de 368 para 364 linhas de código.

Na extensão para todo o sistema, 288 valores globais e 133 schemas Pydantic foram comparados antes/depois
sem diferenças. A suíte verifica também as coleções aninhadas e o import do cliente isolado do Modal sem
exigir instalação de `app` naquele ambiente. Esta validação não chama o Modal nem qualquer provedor real.

Os dois impedimentos de lint são defaults mutáveis em demonstrações:

- `renders/short-argumento-padrao/demo/lista.py:1`
- `renders/short-revisar-comando/demo/lista.py:1`

São arquivos locais não rastreados nesta verificação. Não foram alterados nem excluídos do lint para
produzir um passe artificial. O gate está implantado; sua aprovação global continua pendente enquanto
essas falhas fizerem parte da árvore verificada. O resultado do CI pode diferir porque inclui apenas
os arquivos presentes no checkout enviado.

## Como usar o gate para melhorar

1. Executar o gate e registrar as falhas com seus caminhos; essa é a linha de base verificável.
2. Corrigir uma causa por vez e incluir regressão quando houver mudança de comportamento.
3. Executar novamente os checks afetados e o gate completo antes de fechar a fatia.
4. Reduzir a baseline de tamanho apenas quando código encolher ou for dividido por responsabilidade.
   Não aumentar limites nem regenerar exceções para esconder crescimento.
5. Seguir para o [fluxo RF1–RF7](fluxo-refatoracao-solid-2026-11-01.md) após o gate inicial: proteção de
   aprovações, retomada e contratos TTS são os próximos ganhos. Os 12 gaps ainda não estão resolvidos.

Não foram adicionados limiares de cobertura ou complexidade. Métricas desse tipo precisam
de uma medição e de um critério próprio antes de virarem bloqueio. A ferramenta adicionada nesta extensão é
o Mypy. Os testes do script demonstram as oito combinações de passe/falha de lint, tipagem e testes, sem
executar recursivamente o gate real.
