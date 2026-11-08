# 053 — Referência de voz por idioma e entrega da cena

Data: 2026-11-01. Status: aceita pelo pedido do dono de integrar o fluxo completo,
após gravar cinco intenções em português e inglês. A qualidade da entonação gerada
continua sujeita à escuta; a decisão não aprova vídeos novos ou sua publicação.

## Decisão

- `[chatterbox.references.<idioma>]` em `config/providers.toml` mapeia os nomes de
  `delivery` já existentes para WAVs locais. Caminhos relativos usam a raiz do projeto,
  independentemente do diretório de execução. Modelos validam idioma, entrega e extensão.
- O adapter resolve uma única referência por pedido, usada tanto pela síntese quanto
  pelo cache. Sem mapeamento usa `CHATTERBOX_REFERENCE`; arquivo mapeado ausente/inválido
  é `ModelUnavailable`, nunca substituição silenciosa. O narrador registra a cena
  pendente e continua as falas independentes. Reexecução pede só o que falta.
- `ReferencedTTS` é uma porta opcional de consulta da referência. Outros provedores
  mantêm seu contrato. Shorts e longos com banco ativo usam o fingerprint efetivo,
  incluindo hash da referência, parâmetros da entrega, pausas e divisão de fala longa.
  Sem banco de referências, os nomes legados da ADR 049 permanecem iguais.
- `manifest.json`, em `steps.voice.scenes.<id>.detail`, registra a identidade efetiva
  do cache de cada fala concluída, inclusive no reuso. O registro do Short acrescenta
  arquivo local, SHA-256 completo e nome remoto em `reference` de cada linha.
- No Modal, a gravação selecionada tem nome `references/<idioma>/<delivery>.wav` no
  volume privado `voz-dono-referencia`. O cliente envia nome/hash e texto, nunca os
  bytes da gravação; nomes absolutos ou com traversal são recusados antes da chamada.
  A função remota existente já verifica o hash contra o WAV do volume por pedido.
- O dono mantém controle do envio das referências ao volume (ADR 024). Uma rotina
  diária não cadastra nem sincroniza gravações novas. Esta integração e seu teste
  inicial são o pedido explícito do dono nesta sessão; não autorizam uploads futuros.

## Fluxo

Gravar e guardar os originais fora do Git → converter preservando os M4A → configurar
idioma/entrega → disponibilizar os WAVs no volume privado para a voz Modal → marcar
`delivery` no roteiro → gerar/reutilizar voz → conferir referência e identidade no
registro → escutar a prévia → ajustar animação aos tempos reais → gates existentes.

Os comandos `vp short voz` e `vp voice` permanecem os mesmos. Não há música nova,
mudança de modelo, publicação automática ou alteração dos vídeos já aprovados.

## Validação

Testes cobrem dez seleções, configuração relativa à raiz, ausência/WAV inválido,
fallback somente sem mapeamento, retomada, invalidação apenas das cenas afetadas,
registro de referência e nomes legados. O subprocesso real do cliente é exercitado
com Modal simulado, verificando troca por pedido e ausência de dados da referência.
O teste real de síntese fica em episódios novos de comparação, sem tocar os aprovados.
