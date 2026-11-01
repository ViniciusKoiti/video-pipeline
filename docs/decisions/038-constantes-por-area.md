# ADR 038 — Constantes operacionais por área

Data: 2026-11-01. Status: aceita, por pedido do dono nesta sessão.

## Contexto

O motor FFmpeg misturava funções de render com constantes, como os argumentos do demuxer concat
e a versão do cache de áudio. Após a primeira extração, o dono pediu que o padrão valesse para todo
`app/`, inclusive com bloqueio no gate de qualidade.

## Decisão

- Constantes de **todos os fluxos de `app/`**, inclusive valores fixos usados na validação, ficam em
  `app/<área>/constants/<responsabilidade>_constants.py`, uma classe por arquivo.
- A classe serve como namespace, com atributos tipados como `Final` (o Mypy pode inferir o tipo pelo
  inicializador), acessados diretamente,
  por exemplo `FfmpegConstants.AUDIO_VERSION`. Não precisa ser instanciada.
- Coleções constantes usam `tuple`, `frozenset` ou `MappingProxyType`. Os mapas aninhados também
  precisam ser somente para leitura; `Final[dict[...]]` sozinho não atende à regra.
  `Final` verifica reatribuições na análise estática; a tupla de `CONCAT` também impede mutação dos itens.
- Modelos, membros de enums, campos/defaults e aliases de tipos continuam em `models/` (ADR 037).
  Esta decisão substitui a permissão anterior de definir constantes de validação nessa pasta.
  Parâmetros configuráveis continuam nos settings, modelos ou argumentos correspondentes; variáveis
  locais calculadas durante a execução permanecem nas funções.
- Classes de serviço podem referenciar a constante ao expor um atributo exigido pela interface,
  como `JsonReviewGate.NAME` e o código `reason` dos erros; a definição do valor fica em `constants/`.
- `__all__`, TypeVar e aliases de tipos não são constantes de negócio. `app.cli.HANDLERS` e
  `app.bootstrap.DEFAULT_REGISTRY` são os dois registros mutáveis de composição reconhecidos pela guarda.
  A exceção é pelo papel e caminho exatos, não pelo nome da variável em qualquer módulo.

## Primeira aplicação

`app/render/constants/ffmpeg_constants.py` agrupa os sete valores fixos do motor:
`ENGINE_VERSION`, `FIT_MIN_ASPECT`, `SRT_TIME`, `CONCAT`, `AUDIO_VERSION`, `DUCKING` e `LIMITER`.
Os consumidores passam a usar a classe. `integrated_lufs` aceita `Sequence[str]`, pois apenas lê
os argumentos de entrada; listas existentes e a nova tupla são compatíveis.

Valores e versões permanecem iguais. A comparação das chaves do cache de áudio, com e sem trilha,
confirmou que a reorganização não invalida o cache existente. Um teste cobre a invalidação quando
`AUDIO_VERSION` muda; os testes de montagem continuam cobrindo concatenação e reaproveitamento do áudio.

## Aplicação no sistema e gate

O [inventário completo](../inventario-constantes-2026-11-01.md) registra 311 constantes em 54 classes,
abrangendo comandos, mídia, pipeline, provedores, configuração, render e armazenamento. Os consumidores
em testes e scripts usam os caminhos novos; imports de constantes pelos módulos antigos foram atualizados.
Os imports de modelos preservados pela ADR 037 continuam disponíveis.

`tests/test_constants_layout.py` roda automaticamente no `scripts/check_qualidade.sh`, no pré-commit
e no CI, dentro do pytest. Verifica localização, uma classe por arquivo, atributos `Final` e
imutabilidade das coleções em profundidade. Há casos negativos para constantes públicas, privadas,
nomes minúsculos, aliases de Final, atributos de classes e coleções mutáveis aninhadas.

A identificação estática usa nomes convencionais de constantes, Final, literais e construtores conhecidos;
não infere a mutabilidade de qualquer retorno dinâmico. A checagem estrutural é complementada pelo Mypy e
pela inspeção dos valores efetivos das classes de constantes. `Final` não impede monkeypatch em runtime.

Antes/depois: 288 valores globais e 133 schemas Pydantic comparados sem diferenças. O cliente isolado do
Chatterbox mantém seu import local, sem exigir instalação de `app` no ambiente do Modal. Para respeitar
a catraca de tamanho, os argumentos da CLI foram separados dos handlers, o hash de revisão ganhou módulo
próprio e verificações de relatórios/fecho foram extraídas preservando as regras e os testes existentes.
