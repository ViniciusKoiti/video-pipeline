# Tipos das integrações opcionais

Estes arquivos `.pyi` descrevem somente a superfície usada pelo auto-play. O Mypy os encontra por
`mypy_path = "stubs"` em `pyproject.toml`; Python não os importa em execução e nenhum modelo é instalado.

- `kokoro`: construção de `KPipeline`, geração de resultados e áudio opcional. Conferido com
  `kokoro/pipeline.py` 0.9.4 instalado: `KPipeline.Result.audio` é uma propriedade que retorna Tensor ou None.
- `numpy`, `torch`, `soundfile`, `torchaudio`: arrays/tensores, junção, silêncio e gravação usados nos adapters
  e no worker. As assinaturas são parciais; não pretendem tipar o restante dessas bibliotecas.
- `chatterbox.mtl_tts`: contrato consumido pelo worker no ambiente próprio, incluindo `sr`,
  `from_pretrained` e `generate`. `modal`: proxy de classe e chamada remota consumidos pelo cliente.
  As chamadas e argumentos estão em `app/providers/tts/chatterbox_worker.py` e
  `app/providers/tts/chatterbox_modal_client.py`; execução real continua nos ambientes próprios.

Os stubs locais têm precedência sobre os tipos instalados, inclusive quando o extra `tts` está presente.
Uma chamada nova nessas bibliotecas precisa ampliar o stub com o contrato correspondente, conferido na
versão usada pelo projeto. Não usar `Any` para áudio ou inventar retorno só para obter passe do Mypy.
O payload do proxy Modal permanece um dicionário flexível: os campos são conferidos na fronteira do worker.

O gate comprova compatibilidade estática com esses contratos. Não comprova a presença das bibliotecas, o
carregamento de modelos, a qualidade do áudio nem o serviço remoto; esses continuam exigindo os testes
de integração/escuta apropriados e as autorizações de produção.
