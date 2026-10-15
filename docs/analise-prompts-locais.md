# Análise e revisão dos prompts para modelos locais

Data: 2026-10-12. Escopo: chamadas de texto local, seus contratos e testes offline. A pesquisa e a
criação de episódios continuam com agentes e validação determinística, conforme a
[ADR 009](decisions/009-agentes-para-etapas-criativas.md).

## O que o código envia hoje

A busca por `TextRequest`, `generate_json`, `/api/chat` e `/api/generate` em `app/`, `scripts/` e
`prompts/` encontrou dois caminhos de geração de texto. A configuração de `config/providers.toml`
escolhe Ollama em `127.0.0.1:11434`, `qwen3.5:9b` e oito threads; variáveis de ambiente podem substituir
esses valores. A presente revisão não leu nem modificou segredos ou a configuração do dono.

| Caminho | Prompt e dados | Finalidade e limite |
|---|---|---|
| `scripts/provisorio/checagem_local.py` → `app/pipeline/checagem_local.py:run` | Sistema e template de `prompts/local/checagem.md`; uma claim, ids e texto dos trechos citados | Segunda leitura factual de uma amostra. O resultado é alerta; não aprova roteiro, direitos ou fontes. |
| `vp bench` → `app/pipeline/bench.py:bench_llm` | `SYSTEM` e `prompt(run)` de `app/pipeline/bench_data.py`; dezesseis trechos fictícios | Medir transporte JSON, velocidade e material para avaliação humana. Não é um autor de episódios. |
| Ambos → `app/providers/text/ollama.py:generate_json` | Mensagens separadas `system`/`user`, schema em `format`, temperatura zero, `think=false`, `stream=false` | O adapter transporta e valida JSON; não decide o que é fato. Foi mantido. |

Não existe um terceiro prompt de fichamento ou roteiro real enviado ao Ollama no pipeline atual.
Os agentes escrevem arquivos, e `vp check` verifica schema, existência dos trechos e citações literais
sem chamar modelo. A análise semântica completa continua com o verificador e os gates do dono.

Os modelos locais de voz recebem outros tipos de entrada: Kokoro recebe o texto narrado; Chatterbox
recebe o texto, idioma e áudio de referência local. Não são os prompts de julgamento factual acima.
As entradas, vozes, referência pessoal e configurações de TTS foram preservadas, inclusive a narração
fixa e fictícia usada no benchmark de voz. Gemini TTS é remoto e também não foi alterado.

## Antes e depois

| Problema observado | Alteração aplicada |
|---|---|
| Afirmação e trecho eram interpolados em texto livre, sem explicitar que instruções neles eram apenas conteúdo de fonte. | Entrada como objeto JSON e regra expressa para ignorar instruções embutidas nos dados. As mensagens de sistema e usuário continuam separadas no transporte. |
| `render` fazia três substituições sequenciais. Um `{{trecho}}` existente na própria claim podia ser trocado pelo texto da fonte. | Uma única substituição de `{{dados}}`, com `json.dumps`. Aspas, linhas e placeholders da fonte permanecem literais. |
| Comparação mencionava números, mas deixava unidade, período e negação pouco explícitos. | Critérios para valor, unidade, moeda, período, negação, atribuição e todas as partes de claims compostas. Exemplos de milhões × mil, compra negada e atribuição ausente. |
| O superlativo em segunda frase passara em dois casos da medição antiga. | Regra explícita para conferir também a segunda frase e distinguir aumento de força de uma informação inteiramente ausente. |
| Risco de tratar gancho fraco, estilo ou opinião identificada como erro factual. | O prompt separa avaliação editorial da conferência de fatos. Atributos de retenção e engajamento ficam nos agentes criativos e na avaliação editorial. |
| JSON podia ter `confronto` vazio ou somente espaços. | Schema `Veredito` rejeita essa saída; erro é registrado e os outros casos continuam. Mantidos os quatro rótulos e as duas chaves da resposta. |
| Benchmark pedia cerca de 120 palavras, mas apenas quatro a seis claims, sem cobertura expressa de toda a narração. | Pede quatro a seis frases factuais e claims cobrindo todos seus fatos; preserva datas, ressalvas e atribuições. Não usa conhecimento externo para completar lacunas. |
| Fontes do benchmark tinham formato livre e a validação ignorava chaves extras. | Trechos como JSON; saída continua `narration` + `claims`, agora com rejeição de campos extras. Material fictício, ids e limite de 600 tokens foram preservados. |
| Relatórios não identificavam qual texto de prompt produziu a medição. | `prompt_sha256` no relatório de checagem e em cada execução de texto do benchmark. O campo do benchmark é opcional ao ler relatórios antigos. |

O hash da checagem cobre sistema e template. Seus dados continuam registrados por caso no relatório.
O hash de cada execução do benchmark cobre sistema e prompt completo, incluindo o número da execução;
por isso execuções diferentes têm hashes diferentes. Esses hashes identificam texto de prompt, não
atestam suporte factual ou equivalência entre versões de modelos.

## Como interpretar os rótulos

| Rótulo | Critério principal | Exemplo |
|---|---|---|
| `SUSTENTA` | Todos os elementos verificáveis têm suporte nos trechos recebidos, com a mesma força e escala. | “150 milhões” e “cento e cinquenta milhões”, na mesma moeda e período. |
| `DIVERGE` | Há contradição explícita de valor, unidade, data, ator, verbo ou negação. | “comprou” diante de “não comprou; arrendou”; milhões diante de mil. |
| `SEM_SUPORTE` | O elemento não consta. | Número, causa, intenção ou “segundo a prefeita” ausentes no trecho. |
| `EXAGERO` | Existe suporte parcial, mas a claim amplia certeza, alcance ou força. | “a maior” sem comparação; acusação atribuída apresentada como fato comprovado. |

Paráfrases equivalentes não são erros. Quando problemas distintos coexistem, a precedência continua
`DIVERGE` → `SEM_SUPORTE` → `EXAGERO`. `SUSTENTA` não significa que uma fonte é verdadeira, independente,
atual ou adequada; significa somente que ela sustenta aquela formulação. Entrada de checagem deve ser
uma claim factual: ela não substitui um parecer sobre uma opinião puramente editorial.

## Custo e comparabilidade

A medição existente de [2026-10-05](../data/benchmarks/checagem-local.md) usou `qwen3:4b`, 36 casos:
36 JSON válidos, nenhum alarme falso em doze claims reais e 22 erros detectados em 24 mutações. Dois
superlativos passaram. A mediana foi 31 segundos por chamada, com 23,7 minutos no total. Esse resultado
pertence ao prompt anterior; não comprova a qualidade ou a latência desta revisão.

Contagem por espaços, sem dados de episódio, para dimensionar a mudança:

| Texto enviado | Antes | Depois |
|---|---:|---:|
| Sistema + template da checagem | 380 palavras | 666 palavras |
| Sistema do benchmark | 34 palavras | 98 palavras |
| Usuário do benchmark, execução 1 | 694 palavras | 712 palavras |

Palavras não são tokens. O prompt de checagem cresceu e pode aumentar a leitura de contexto na CPU.
O mesmo provedor, limite de saída e dados fictícios foram mantidos, mas os tempos anteriores e novos
devem ser comparados identificando prompt, modelo, CPU e número de tokens. Nenhum modelo foi trocado
e nenhuma melhoria quantitativa de engajamento, precisão ou velocidade é afirmada.

## Validação e próxima medição

Os testes offline cobrem preservação de aspas, linhas e placeholders nos dados, envelope real do
adapter com transporte simulado, schema de resposta, comparação vazia, rótulo inválido, campos extras,
continuação após erro e hash do prompt em execução bem-sucedida e falha. Os testes de arquitetura e
contrato verificam que os prompts continuam no pipeline e o adapter continua sendo transporte.

```bash
.venv/bin/pytest -q tests/test_checagem_local.py tests/test_bench.py tests/test_ollama.py tests/test_contracts.py tests/test_architecture.py
.venv/bin/ruff check app/pipeline/checagem_local.py app/pipeline/bench.py app/pipeline/bench_data.py scripts/provisorio/checagem_local.py tests/test_checagem_local.py tests/test_bench.py
```

Para uma futura medição local, com a máquina livre, use outra semente e outra amostra. Exemplo, a ser
executado deliberadamente pelo dono/agente responsável:

```bash
.venv/bin/python scripts/provisorio/checagem_local.py <episode-id> --modelo qwen3:4b --semente 3 --saida data/cache/checagem-local-v2-semente3.json
vp bench --models qwen3:4b --runs 1 --skip-tts
```

Antes de pontuar, uma pessoa deve conferir o gabarito e separar casos reservados de casos usados para
ajustar o prompt. `build_cases` presume que claims reais são sustentadas e usa mutações mecânicas;
a aprovação anterior não prova que cada trecho escolhido sustenta integralmente cada claim. Baixa
sobreposição de palavras tampouco garante que um trecho alheio seja semanticamente incompatível.
Não se deve marcar uma paráfrase ou uma unidade numericamente equivalente como erro apenas pela
diferença textual. Caso ambíguo deve ser corrigido ou excluído do conjunto antes da comparação.

A próxima avaliação deve incluir suporte equivalente, unidade errada, número ausente, negação,
atribuição trocada/perdida, causa inferida, superlativo interno e em segunda frase, além de instruções
injetadas dentro de uma fonte. Compare JSON válido, alarmes falsos, erros que passaram, rótulo certo,
latência e tokens. O `ok` de `vp bench` indica uma resposta estruturalmente válida; citações conhecidas
e fidelidade semântica ainda precisam ser avaliadas separadamente.

Não foram executados modelos pesados, TTS, render ou APIs reais nesta revisão. Serializar dados e
escrever uma regra de isolamento reduz ambiguidades, mas não garante imunidade do modelo a instruções
injetadas. Os testes simulados comprovam contratos e montagem de payload; a obediência e a acurácia
do Qwen precisam de medição real e revisão humana.
