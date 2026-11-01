# Linha de base da tipagem — 2026-11-01

Primeira medição com Mypy **2.4.1**, em modo estrito, Python alvo 3.11 e plugin `pydantic.mypy` com
`init_typed=true`. Escopo: `app/`. O verificador é uma dependência de desenvolvimento; configuração em
`pyproject.toml`, versões e hashes no `uv.lock`.

Comando: `uv run --no-sync mypy`.

**Medição inicial: 107 erros em 29 arquivos; 81 arquivos analisados.** Essa fotografia é preservada abaixo
como histórico, sem autorizar exceções. A correção subsequente zerou os diagnósticos nos **86 arquivos**
de `app/` de então, mantendo o modo estrito e `init_typed=true`. A organização posterior em
`app/<área>/models/` expandiu a análise para **302 arquivos**, ainda sem diagnósticos (ADR 037).

## Correção concluída

- Registro de provedores tipado por porta, com `Registration[T]` e `Registry` em
  `app/bootstrap/models/`, reexportados por `app/bootstrap_registry.py`.
  Fábricas devolvem a interface correspondente, sem conversões forçadas.
- Respostas HTTP preservam objeto ou lista; os adapters validam o formato esperado. JSON inválido vira
  falha de provedor, sem ecoar conteúdo sensível. Payloads variáveis usam dicionários com tipos explícitos.
- Opcionais e variantes são refinados antes do uso; nomes de variáveis deixam de misturar tipos distintos;
  coleções somente lidas aceitam `Sequence`; as janelas de métricas usam o `Literal` compartilhado `Window`.
- SQLite verifica o tipo das linhas retornadas e aceita seu tipo real nos métodos internos, sem migrar dados.
- Integrações opcionais têm [stubs locais parciais](../stubs/README.md), incluindo áudio e tensores. Não foram
  adicionados ignores globais, casts para silenciar diagnósticos ou dependências de modelos pesados.
- `BenchClaim` e `BenchScript` estão em `app/pipeline/models/bench_claim.py` e
  `app/pipeline/models/bench_script.py`; `bench_data.py` e `app/models/` preservam os imports antigos.
  A [ADR 037](decisions/037-modelos-por-fluxo.md) aplica essa organização a todos os fluxos.
  Conferência de links do Postiz foi separada em módulo próprio.
- Bootstrap e cadeia Postiz ficaram abaixo de 200 linhas; a baseline de tamanho diminuiu de 13 para 11
  arquivos, sem aumentar permissões de crescimento. As 10 funções legadas continuam na catraca.

Verificação da primeira correção: Mypy sem erros nos 86 arquivos, **921 testes passaram** e 6 lentos ficaram fora;
arquitetura e tamanho passaram. O lint dos arquivos alterados passou; o lint global continua bloqueado
pelos dois `B006` preexistentes das demonstrações em `renders/`, registrados no [gate de qualidade](gate-qualidade.md).
Os stubs descrevem a superfície consumida pelo projeto e têm precedência sobre tipos instalados: a execução
de serviços reais e a escuta de voz permanecem verificações separadas, não realizadas nessa refatoração.

## O que foi encontrado inicialmente

| Código | Quantidade | O que verificar |
|---|---:|---|
| `type-arg` | 30 | `dict`, `list` e `tuple` sem tipos dos elementos |
| `no-any-return` | 22 | Retorno dinâmico não comprova o tipo prometido pelo método |
| `union-attr` | 16 | Acesso a atributo ausente em parte das variantes de um tipo |
| `attr-defined` | 13 | Atributo não declarado no tipo inferido |
| `arg-type` | 7 | Valor passado não corresponde ao contrato do parâmetro |
| `assignment` | 4 | Tipos incompatíveis em atribuição ou valor padrão |
| `import-not-found` | 3 | Dependência de ambiente próprio ausente na análise local |
| `index` | 3 | Índice ou alvo da indexação não tem o tipo esperado |
| `call-overload` | 2 | Chamada não atende às assinaturas conhecidas |
| `misc` | 2 | Inferência ou construção de tipos precisa de revisão |
| `import-untyped` | 2 | Biblioteca instalada sem stubs ou marcador de tipagem |
| `var-annotated` | 1 | Coleção necessita de anotação explícita |
| `unused-ignore` | 1 | Comentário de supressão já não é necessário |
| `operator` | 1 | Operação inclui valor opcional sem refinamento suficiente |

Cada diagnóstico não corresponde necessariamente a um defeito independente: um único acesso a uma união
de 17 tipos gera vários avisos. Tampouco todos provam bug em runtime; podem indicar anotação imprecisa,
reuso de variável com tipos distintos ou contrato dinâmico que precisa ser descrito.

## Ordem usada para a correção

1. **Portas e composição:** `app/bootstrap.py` retorna `Any` onde promete `ManifestStore`, `ReviewGate`,
   TTS e outras portas. Tipar a composição deve permitir verificar a implementação que realmente chega ao
   chamador; substituir `Any` por `cast` sem prova não resolve essa garantia.
2. **Opcionais e variantes:** revisar `pipeline/shots.py`, `pipeline/molde.py`, `pipeline/numbers.py` e
   `pipeline/check.py`. Refinar o tipo antes do acesso e manter as validações de entrada.
3. **Contratos de coleções e retornos:** completar genéricos em Postiz e outros módulos; validar resultados
   de transporte antes de devolvê-los como tipos mais específicos.
4. **Inferência e anotações:** separar variáveis com papéis distintos em schemas/bench, corrigir assinaturas
   de coleções somente de leitura e documentar o tipo de resultados do SQLite sem mudar seus dados.
5. **Dependências opcionais:** Modal, Chatterbox e torchaudio não estão disponíveis nesse ambiente de
   análise; Kokoro e soundfile não oferecem os tipos esperados. Definir stubs ou uma fronteira tipada para
   esses adapters antes de aceitar supressões específicas. Não instalar modelos pesados só para satisfazer o gate.

Uma correção deve preservar o comportamento e passar pelos testes apropriados, pela catraca de tamanho e
pela arquitetura. O arquivo bruto da medição local está em `data/cache/qualidade-tipagem-2026-11-01.txt`,
ignorado pelo Git; para outra máquina ou revisão, gerar uma nova medição e comparar as causas.

## Alcance da garantia

O [teste do gate](../tests/test_quality_gate.py) comprova que Mypy aceita um adapter conforme a porta
`TTSProvider` existente e rejeita outro com retorno incompatível. São exemplos de verificação estática;
os adapters reais precisam continuar passando pelos testes de contrato de comportamento.

Não se conclui que o projeto segue SOLID só porque a tipagem passa. Responsabilidade única, limites das
interfaces e direção das dependências também exigem a guarda de arquitetura e revisão do desenho.
